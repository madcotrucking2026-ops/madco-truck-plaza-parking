"""Break-glass password reset — run ON THE SERVER, no login required.

For the one person the in-app reset can't help: the admin who forgot their own
password. Anyone who can run this already owns the box (and the database), so it
grants nothing an attacker didn't have.

    .venv/Scripts/python.exe -m scripts.reset_password owner@example.com
    # docker:
    docker compose exec backend python -m scripts.reset_password owner@example.com

Prompts for the new password (never takes it as an argv — argv leaks into shell
history and process lists). Also clears any login lockout.
"""

import getpass
import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m scripts.reset_password <email>")
        return 2

    email = sys.argv[1].strip().lower()
    db = SessionLocal()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        emails = [u.email for u in db.scalars(select(User))]
        print(f"No user {email!r}. Accounts on this system: {', '.join(emails) or '(none)'}")
        return 1

    pw = getpass.getpass(f"New password for {user.name} <{user.email}>: ")
    if len(pw) < 8:
        print("Password must be at least 8 characters.")
        return 1
    if getpass.getpass("Repeat it: ") != pw:
        print("Passwords don't match — nothing changed.")
        return 1

    user.hashed_password = hash_password(pw)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    print(f"Password reset for {user.email}; lockout cleared. They can sign in now.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
