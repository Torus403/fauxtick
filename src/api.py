from fastapi import APIRouter

from src.auth.router import main_router as auth_router
from src.auth.router import admin_router as admin_auth_router
from src.user.router import main_router as user_router
from src.user.router import admin_router as admin_user_router
from src.ticker.router import router as ticker_router

ADMIN_PREFIX = "/admin"

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin_auth_router, prefix=f"{ADMIN_PREFIX}/auth", tags=["Admin: Authentication"])
api_router.include_router(user_router, prefix="/user", tags=["User"])
api_router.include_router(admin_user_router, prefix=f"{ADMIN_PREFIX}/user", tags=["Admin: User"])
api_router.include_router(ticker_router, prefix="/ticker", tags=["Tickers"])
