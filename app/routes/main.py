from fastapi import APIRouter
from app.routes.views import router as views_router
from app.routes.auth import router as auth_router
from app.routes.social import router as social_router
from app.routes.config import router as config_router
from app.routes.posts import router as posts_router
from app.routes.calendar import router as calendar_router
from app.routes.ideas import router as ideas_router
from app.routes.admin import router as admin_router
from app.routes.ollama import router as ollama_router

router = APIRouter()

# Include sub-routers
router.include_router(views_router)
router.include_router(auth_router)
router.include_router(social_router)
router.include_router(config_router)
router.include_router(posts_router)
router.include_router(calendar_router)
router.include_router(ideas_router)
router.include_router(admin_router)
router.include_router(ollama_router)
