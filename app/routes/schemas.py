from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    invite_code: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ConnectAccountRequest(BaseModel):
    platform: str
    account_handle: str
    credentials: dict  # e.g., {"handle": "...", "password": "..."}

class ConfigModel(BaseModel):
    themes: List[str]
    tone: str
    interval_hours: int
    is_active: bool
    system_prompt: str
    persona_description: Optional[str] = None
    requires_approval: bool
    scheduling_mode: Optional[str] = "recorrente"
    channel: Optional[str] = "bluesky"

class LLMServerCreate(BaseModel):
    name: str
    provider: str
    model: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None

class LLMServerResponse(BaseModel):
    id: int
    name: str
    provider: str
    model: str
    base_url: Optional[str] = None
    is_active: bool
    api_key: Optional[str] = None

    class Config:
        from_attributes = True

class TestLLMServerRequest(BaseModel):
    provider: str
    model: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    id: Optional[int] = None




class DraftRequest(BaseModel):
    theme: Optional[str] = None
    tone: Optional[str] = None
    system_prompt: Optional[str] = None
    idea_text: Optional[str] = None

class IdeaCreate(BaseModel):
    title: str
    description: str
    channel: str = "bluesky"

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    channel: Optional[str] = None

class IdeaResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    channel: str = "bluesky"
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyzeQualityRequest(BaseModel):
    content: str
    tone: str

class PostDraftRequest(BaseModel):
    content: str
    theme: str
    calendar_item_id: Optional[int] = None
    draft_id: Optional[int] = None
    channel: Optional[str] = None

class PostNowRequest(BaseModel):
    theme: Optional[str] = None
    calendar_item_id: Optional[int] = None
    channel: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class EditorialItemCreate(BaseModel):
    theme: Optional[str] = "Uso Manual"
    scheduled_date: datetime
    objective: Optional[str] = None
    cta: Optional[str] = None
    channel: str = "bluesky"
    is_manual: bool = False
    manual_content: Optional[str] = None

class EditorialItemResponse(BaseModel):
    id: int
    theme: str
    scheduled_date: datetime
    status: str
    objective: Optional[str] = None
    cta: Optional[str] = None
    channel: str = "bluesky"
    is_manual: bool = False
    manual_content: Optional[str] = None
    post_history_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InviteCodeCreate(BaseModel):
    code: str
    plan_tier: str = "free"
    max_uses: int = 1

class UpdatePlanRequest(BaseModel):
    plan_tier: str

class TierConfigUpdate(BaseModel):
    max_themes: int
    max_accounts: int
    max_calendar_items: int
    daily_post_limit: int
