import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app import config

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/")
async def get_dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})

@router.get("/api/public-settings")
async def get_public_settings():
    return {
        "allow_public_registration": config.ALLOW_PUBLIC_REGISTRATION,
        "require_invite_code": config.REQUIRE_INVITE_CODE
    }
