import secrets
from datetime import date


def generate_receipt_number(prefix: str, issue_date: date) -> str:
    # 6 random bytes = 48 bits (~281 trillion) via a cryptographically secure
    # RNG. Collision odds are negligible even at thousands of passes/day, and
    # the DB unique constraint on receipt_number is the hard backstop.
    return f"{prefix}-{issue_date.strftime('%Y%m%d')}-{secrets.token_hex(6).upper()}"
