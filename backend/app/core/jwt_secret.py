import os
import secrets
from pathlib import Path

# If JWT_SECRET is set (env var or .env), that always wins — see config.py.
# Otherwise, rather than fall back to a hardcoded literal (which would be
# checked into source and forgeable by anyone who's seen this codebase), we
# generate a random secret once per install and persist it locally so it
# survives restarts but is never shared/guessable. Gitignored — never commit
# this file.
_SECRET_FILE = Path(__file__).resolve().parent.parent.parent / ".jwt_secret"


def load_or_create_jwt_secret() -> str:
    env_secret = os.environ.get("JWT_SECRET")
    if env_secret:
        return env_secret

    if _SECRET_FILE.exists():
        existing = _SECRET_FILE.read_text().strip()
        if existing:
            return existing

    generated = secrets.token_hex(32)
    _SECRET_FILE.write_text(generated)
    return generated
