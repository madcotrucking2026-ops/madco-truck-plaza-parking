"""The external reminder trigger: a shared-secret header, not a user account.

Its caller is cron. The failure modes that matter: running unauthenticated when
no token is configured (must 503, never sweep), accepting a wrong token, and a
JWT-less call sweeping successfully with the right one.
"""

from app.core.config import settings


def test_refuses_when_no_token_is_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "scheduler_token", "")
    r = client.post("/api/reminders/cron")
    assert r.status_code == 503


def test_rejects_a_wrong_token(client, monkeypatch):
    monkeypatch.setattr(settings, "scheduler_token", "cron-secret")
    r = client.post("/api/reminders/cron", headers={"X-Scheduler-Token": "guess"})
    assert r.status_code == 403


def test_sweeps_with_the_right_token_and_no_login(client, monkeypatch):
    monkeypatch.setattr(settings, "scheduler_token", "cron-secret")
    r = client.post("/api/reminders/cron", headers={"X-Scheduler-Token": "cron-secret"})
    assert r.status_code == 200
    body = r.json()
    assert body["enabled"] is True
    assert body["checked"] == 0  # empty database — the point is it RAN, sans JWT
