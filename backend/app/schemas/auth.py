from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EmployeeRole


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Bootstrap-only — creates the very first user account. Rejected once
    any user already exists (see `POST /api/auth/register`)."""

    name: str
    email: str
    password: str = Field(min_length=8)


class CreateStaffUserRequest(BaseModel):
    """Admin-only — adds an additional staff login after initial setup."""

    name: str
    email: str
    password: str = Field(min_length=8)
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
