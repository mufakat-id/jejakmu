from sqlmodel import SQLModel


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# JSON payload containing access and refresh tokens
class TokenWithRefresh(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


# OAuth access denied error
class OAuthAccessDenied(SQLModel):
    message: str
    email: str


# Google authorization code request from frontend
class GoogleAuthCodeRequest(SQLModel):
    code: str
    scope: str | None = None
    authuser: str | None = None
    hd: str | None = None  # hosted domain
    prompt: str | None = None
