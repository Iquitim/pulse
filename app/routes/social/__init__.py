from fastapi import APIRouter
from app.routes.social.status import router as status_router
from app.routes.social.accounts import router as accounts_router
from app.routes.social.oauth_twitter import router as twitter_router, get_twitter_redirect_uri
from app.routes.social.oauth_threads import router as threads_router, get_threads_redirect_uri

router = APIRouter()

router.include_router(status_router)
router.include_router(accounts_router)
router.include_router(twitter_router)
router.include_router(threads_router)

__all__ = [
    "router",
    "get_twitter_redirect_uri",
    "get_threads_redirect_uri"
]
