from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import EmployeeRole

# bcrypt only ever looks at the first 72 bytes, so anything past that is dead
# weight — and an unbounded password field means an attacker can post megabytes
# straight into the hasher on an endpoint that needs no login.
PASSWORD_MAX = 128
_Password = Field(min_length=8, max_length=PASSWORD_MAX)


class LoginRequest(BaseModel):
    # Bounded but deliberately NOT EmailStr. Format-validating an email at LOGIN
    # can lock out an account that already exists — any address the validator now
    # dislikes (a reserved TLD, an unusual-but-real domain) becomes un-loggable-in
    # even though it authenticated fine yesterday. Validation belongs at REGISTER,
    # where the account is minted. Here we only bound the size; a wrong address
    # simply fails to authenticate.
    email: str = Field(min_length=1, max_length=254)  # RFC 5321 practical ceiling
    password: str = Field(min_length=1, max_length=PASSWORD_MAX)


class RegisterRequest(BaseModel):
    """Bootstrap-only — creates the very first user account. Rejected once
    any user already exists (see `POST /api/auth/register`)."""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(max_length=254)
    password: str = _Password


class CreateStaffUserRequest(BaseModel):
    """Admin-only — adds an additional staff login after initial setup."""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(max_length=254)
    password: str = _Password
    role: EmployeeRole = EmployeeRole.attendant


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: EmployeeRole


class AuthStatus(BaseModel):
    needs_setup: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
