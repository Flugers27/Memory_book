from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class TokenBase(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPair(TokenBase):
    refresh_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    sub: UUID
    email: str
    exp: datetime
    iat: datetime
    type: str

class TokenResponse(BaseModel):
    id_user_token: UUID
    user_id: UUID
    device_info: Optional[str] = None
    expires_at: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)