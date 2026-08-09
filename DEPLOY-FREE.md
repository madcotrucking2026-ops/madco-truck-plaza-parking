# Put MTPMS online for free (Vercel + Render + Neon)

A click-by-click guide to get the app on the internet so your client can use it,
with **no domain and $0/month**. Takes about **30–40 minutes**, all in a browser.

## What you're setting up (and what each does)

| Service | Free? | Its job | The link you get |
|---|---|---|---|
| **GitHub** | yes | Holds your code (Render + Vercel read from it) | (private repo) |
| **Neon** | yes | The **database** — where all your data safely lives | (connection string) |
| **Render** | yes | Runs the **engine** (the Python backend) | `…​.onrender.com` |
| **Vercel** | yes | Runs the **website** (what people see) | `…​.vercel.app` |

**You give the client the Vercel link.** That's the whole app.

### Two honest caveats (tell your client)
1. **The engine sleeps when idle.** After ~15 minutes with nobody using it, Render
   puts the backend to sleep. The **first** visit after a nap takes ~30–60 seconds
   to wake up, then it's fast all day. Your **data is never lost** (it lives in Neon).
2. **Free tiers are for trying it out.** Great for the client to test and decide.
   For the real business long-term, move to the ~$5/month server (see the end).

---

## Before you start
Open these 4 sites in tabs and **sign up for each with your GitHub account** (one click):
- https://github.com
- https://neon.tech
- https://render.com
- https://vercel.com

Signing in everywhere with GitHub keeps it simple.

---

## Step 1 — Put the code on GitHub (~5 min)

1. On https://github.com click **New repository**.
2. Name it `madco-truck-plaza` · set it **Private** · **don't** add a README · click **Create repository**.
3. GitHub shows commands. On your computer, in the project folder, run **only these**
   (replace `YOUR-USERNAME`):
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/madco-truck-plaza.git
   git branch -M main
   git push -u origin main
   ```
   (If it asks you to sign in, use your GitHub login or a personal access token.)
4. Refresh the GitHub page — your code is now there.

> Tell me if you'd like me to run these push commands for you — I just need the repo URL.

---

## Step 2 — Create the database on Neon (~5 min)

1. On https://neon.tech click **Create project** (or **New Project**).
2. Name: `madco` · Region: pick **US East** (closest to Michigan) · **Create**.
3. Neon shows a **connection string** that looks like:
   `postgresql://madco_owner:XXXX@ep-xxxx.us-east-1.aws.neon.tech/madco?sslmode=require`
4. Click **Copy** and paste it into a note — you'll need it in Step 3.

That's it. The app builds its own tables automatically the first time it starts.

---

## Step 3 — Deploy the engine on Render (~10 min)

1. On https://render.com click **New +** → **Blueprint**.
2. Connect your GitHub and pick the `madco-truck-plaza` repo. Render finds the
   `render.yaml` in it and shows a service called **mtpms-backend**. Click **Apply**.
3. It starts deploying, then needs one value. Open the **mtpms-backend** service →
   **Environment** tab → find **DATABASE_URL** → **Edit** → paste the **Neon
   connection string** from Step 2 → **Save Changes**. (You can paste it exactly as
   Neon gave it — the app adjusts the format itself.)
4. Render redeploys. When it shows **Live** (green), copy the service URL at the top,
   e.g. `https://mtpms-backend.onrender.com` — you'll need it in Step 4.

> `JWT_SECRET` is generated automatically — leave it alone.
> Leave `PUBLIC_BASE_URL` and `CORS_ORIGINS` for now; you set them in Step 5.

---

## Step 4 — Deploy the website on Vercel (~10 min)

1. On https://vercel.com click **Add New…** → **Project** and import the
   `madco-truck-plaza` repo.
2. On the setup screen, set **Root Directory** to `frontend` (click **Edit** next to
   Root Directory and choose the `frontend` folder). Framework should auto-detect as
   **Next.js**.
3. Open **Environment Variables** and add one:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** your Render URL from Step 3, e.g. `https://mtpms-backend.onrender.com`
4. Click **Deploy**. When it finishes, copy your site URL, e.g.
   `https://madco-truck-plaza.vercel.app` — this is the link you give the client.

---

## Step 5 — Connect the two (so they can talk) (~3 min)

The engine only accepts the website once you tell it the website's address.

1. Back on Render → **mtpms-backend** → **Environment** tab. Set these two (Edit → paste → Save):
   - **PUBLIC_BASE_URL** = your Vercel URL, e.g. `https://madco-truck-plaza.vercel.app`
   - **CORS_ORIGINS** = the same URL as a list: `["https://madco-truck-plaza.vercel.app"]`
   (No trailing slash. The `CORS_ORIGINS` one **must** have the square brackets and quotes.)
2. **Save Changes** — Render redeploys once more. Wait for **Live**.

Done. The website and engine are now connected.

---

## Step 6 — First login (~2 min)

1. Open your **Vercel URL**. The very first visit shows **"Create your admin account."**
2. Enter your name, email, and a password — **this is the owner login. Write it down.**
3. You're in. To add the cashier: go to **Settings → add a staff member**, choose role
   **Attendant**, give them an email + password.
4. Give the client the **Vercel URL** and the login you want them to use.

---

## If something looks wrong

- **First load is slow / "loading…" for a minute** → normal. The engine was asleep and
  is waking up. Wait ~60 seconds and refresh once.
- **Login says "can't reach the system" / network error** → the connect step (Step 5)
  isn't done or the URL has a typo. Recheck `CORS_ORIGINS` on Render is exactly
  `["https://your-vercel-url"]` and `NEXT_PUBLIC_API_URL` on Vercel is exactly your
  Render URL. After changing either, redeploy that service.
- **Changed an env var but nothing changed** → you must redeploy the service after
  changing its environment (Render redeploys on Save; on Vercel, go to Deployments →
  redeploy).

## Costs & limits (free tier)
- **$0/month.** Neon free = 0.5 GB (you'll use a tiny fraction). Render free = one
  service that sleeps when idle. Vercel free = plenty for this site.
- No credit card required for the basic free tiers.

## When the client says yes (the real setup)
Move to a single **~$5/month server** (DigitalOcean/Hetzner) running everything with
**SQLite** + a **nightly backup** — no sleeping, no free-tier limits, fully yours, and
a real domain whenever you want one. Ask me and I'll walk you through it.
