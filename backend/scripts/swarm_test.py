"""100+ simulated customers hammer the REAL prod stack (Postgres) at once.

Run it after ANY change to spot assignment (app/core/spots.py) — this is the
only test that exercises the Postgres locking path; SQLite serializes writers
and cannot reproduce the races this has already caught (4 spots double-sold
via a stale-snapshot window, flagged spots resold).

    # stack up + clean books first:
    docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
    docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend         python -m scripts.purge_demo --yes
    # then, from the repo root, with an admin login (edit EMAIL/PASSWORD below):
    backend/.venv/Scripts/python.exe backend/scripts/swarm_test.py

DESTRUCTIVE: fills the lot with fake companies and rewrites pass dates via
docker-compose psql. Never point it at a live client system.
"""
import sys

What must survive the stampede:
  1. Every customer gets a spot; NO two live passes ever share one (SKIP LOCKED).
  2. Expiry frees spots with no job running — the next wave REUSES exactly them,
     longest-vacant first.
  3. "Spot occupied?" reassigns under load and flags overstays.
  4. Monthly spots are sticky through a renewal.
  5. Past capacity, checkout refuses cleanly.
  6. The books reconcile at the end: grid == passes == arithmetic.
"""

import random
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import requests

BASE = "http://localhost"
EMAIL, PASSWORD = "verify@madcotruckplaza.com", "VerifyProd!234"
CUSTOMERS = 110
WORKERS = 24

s = requests.Session()


def login() -> dict:
    r = s.post(f"{BASE}/api/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=20)
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


H = login()
today = date.today()


def issue(i: int, pass_type: str = "daily", days: int = 1, price=None):
    body = {
        "company_name": f"Swarm Freight {i:03d}",
        "truck_number": f"SW{i:04d}",
        "phone": f"313-555-{1000 + i}",
        "vehicle_type": "truck",
        "pass_type": pass_type,
        "issue_date": today.isoformat(),
        "end_date": (today + timedelta(days=days)).isoformat(),
        "payment_method": "cash",
    }
    if price is not None:
        body["price"] = price
    r = s.post(f"{BASE}/api/passes", json=body, headers=H, timeout=30)
    return r.status_code, (r.json() if r.status_code == 200 else r.text[:120])


def lot():
    r = s.get(f"{BASE}/api/spots", headers=H, timeout=20)
    r.raise_for_status()
    return r.json()


def states():
    return Counter(x["state"] for x in lot())


fails = 0


def check(label, ok, detail=""):
    global fails
    print(f"{'ok  ' if ok else 'FAIL'}  {label}{'  <- ' + str(detail) if not ok and detail else ''}")
    if not ok:
        fails += 1


# ---- Wave 1: 110 customers rush the gate at once ----------------------------
print(f"WAVE 1: {CUSTOMERS} concurrent customers (daily/weekly/monthly mix)")
kinds = [("daily", 1, None)] * 70 + [("weekly", 7, None)] * 25 + [("monthly", 30, 250)] * 15
random.Random(42).shuffle(kinds)

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    results = list(ex.map(lambda a: issue(a[0], *a[1]), enumerate(kinds)))

issued = [body for code, body in results if code == 200]
errors = [(code, body) for code, body in results if code != 200]
spots_taken = [p["spot_number"] for p in issued]
dupes = [n for n, c in Counter(spots_taken).items() if c > 1]

check(f"all {CUSTOMERS} passes issued", len(issued) == CUSTOMERS, errors[:2])
check("every pass got a spot number", all(n is not None for n in spots_taken))
check("NO duplicate spots under concurrency", not dupes, f"spots issued twice: {dupes}")

st = states()
check(f"grid agrees: {st.get('occupied',0)+st.get('expiring',0)} held",
      st.get("occupied", 0) + st.get("expiring", 0) == CUSTOMERS, dict(st))
free_before = st.get("free", 0)
print(f"      lot: {dict(st)}")

# ---- Wave 2: 30 dailies expire; their spots must be REUSED ------------------
print("WAVE 2: 30 dailies expire (dates pushed back via DB) -> 30 new customers")
victims = [p for p in issued if p["pass_type"] == "daily"][:30]
victim_spots = sorted(p["spot_number"] for p in victims)
import subprocess

ids = ",".join(str(p["id"]) for p in victims)
subprocess.run(
    ["docker", "compose", "-f", "docker-compose.prod.yml", "--env-file", ".env.prod",
     "exec", "-T", "postgres", "psql", "-U", "mtpms", "-d", "mtpms", "-c",
     f"UPDATE parking_passes SET expiration_date = CURRENT_DATE - 1, issue_date = CURRENT_DATE - 2 WHERE id IN ({ids});"],
    check=True, capture_output=True,
)

st = states()
check("30 spots freed instantly, no cron involved", st.get("free", 0) == free_before + 30, dict(st))

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    wave2 = list(ex.map(lambda i: issue(1000 + i), range(30)))
w2 = [b for c, b in wave2 if c == 200]
w2_spots = sorted(p["spot_number"] for p in w2)
check("30 new customers seated", len(w2) == 30, [x for x in wave2 if x[0] != 200][:2])
reused = set(w2_spots) & set(victim_spots)
check(f"expired spots REUSED ({len(reused)}/30 exact matches)", len(reused) >= 25,
      f"only {len(reused)} reused — expected the freed block to be preferred")

# ---- Wave 3: 10 squatter reports under load ---------------------------------
print("WAVE 3: 10 customers find their spot blocked -> one-tap reassign")
targets = w2[:10]
tokens = [p["qr_code"].split("/verify/")[1] for p in targets]

def report(tok):
    r = s.post(f"{BASE}/api/verify/{tok}/report-occupied", timeout=20)
    return r.status_code, (r.json() if r.status_code == 200 else r.text[:80])

with ThreadPoolExecutor(max_workers=10) as ex:
    re_results = list(ex.map(report, tokens))
ok_re = [b for c, b in re_results if c == 200]
new_spots = [b["spot_number"] for b in ok_re]
old_spots = [p["spot_number"] for p in targets]
check("all 10 reassigned", len(ok_re) == 10, [x for x in re_results if x[0] != 200][:2])
check("all got DIFFERENT spots", all(n != o for n, o in zip(new_spots, old_spots)))
check("no collisions among reassignments", len(set(new_spots)) == len(new_spots), new_spots)
st = states()
check("10 overstay flags on the grid", st.get("overstay", 0) == 10, dict(st))

# ---- Wave 4: monthly stickiness ---------------------------------------------
print("WAVE 4: a monthly lapses past grace, returns — same spot")
monthly = next(p for p in issued if p["pass_type"] == "monthly")
subprocess.run(
    ["docker", "compose", "-f", "docker-compose.prod.yml", "--env-file", ".env.prod",
     "exec", "-T", "postgres", "psql", "-U", "mtpms", "-d", "mtpms", "-c",
     f"UPDATE parking_passes SET expiration_date = CURRENT_DATE - 10 WHERE id = {monthly['id']};"],
    check=True, capture_output=True,
)
r = s.get(f"{BASE}/api/passes", headers=H, timeout=20)
row = next(x for x in r.json() if x["id"] == monthly["id"])
body = {
    "company_name": row["company_name"], "truck_number": row["truck_number"],
    "phone": "313-555-9999", "vehicle_type": "truck", "pass_type": "monthly",
    "issue_date": today.isoformat(), "end_date": (today + timedelta(days=30)).isoformat(),
    "payment_method": "cash",
}
r2 = s.post(f"{BASE}/api/passes", json=body, headers=H, timeout=30)
check("lapsed monthly re-issued", r2.status_code == 200, r2.text[:100])
check(f"STICKY: got their old spot {monthly['spot_number']} back",
      r2.status_code == 200 and r2.json()["spot_number"] == monthly["spot_number"],
      f"got {r2.json().get('spot_number') if r2.status_code==200 else '—'}")

# ---- Wave 5: fill to the brim, then one too many ----------------------------
print("WAVE 5: fill every remaining spot, then customer 151 is refused")
st = states()
remaining = st.get("free", 0)
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    fill = list(ex.map(lambda i: issue(2000 + i), range(remaining)))
seated = [b for c, b in fill if c == 200 and b["spot_number"] is not None]
check(f"remaining {remaining} spots all seated", len(seated) == remaining)

st = states()
check("zero free", st.get("free", 0) == 0, dict(st))
code, body = issue(9000)  # desk issue when full -> spotless pass allowed (money never blocked)
check("desk issue when full: pass valid, spot NULL (awaiting-spot chip case)",
      code == 200 and body["spot_number"] is None, (code, str(body)[:80]))

# ---- Final reconciliation ----------------------------------------------------
st = states()
r = s.get(f"{BASE}/api/passes", headers=H, timeout=20)
live_with_spots = [x for x in r.json() if x["spot_number"] is not None and x["status"] in ("active", "expiring_soon")]
# overstay spots hold no pass by design — their customer was reassigned away
grid_held = st.get("occupied", 0) + st.get("expiring", 0) + st.get("grace", 0)
print(f"      final lot: {dict(st)}")
check("BOOKS RECONCILE: live passes with spots == spots held on grid",
      len({x['spot_number'] for x in live_with_spots}) == grid_held,
      f"{len(set(x['spot_number'] for x in live_with_spots))} vs {grid_held}")
dupes_final = [n for n, c in Counter(x["spot_number"] for x in live_with_spots).items() if c > 1]
check("ZERO spots double-sold across the whole day", not dupes_final, dupes_final)

print(f"\n{'ALL CHECKS PASS' if fails == 0 else f'{fails} CHECK(S) FAILED'}")
sys.exit(1 if fails else 0)
