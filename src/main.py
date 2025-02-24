from fastapi import FastAPI

from src.api import api_router
from src.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


@app.get("/")
async def root():
    return "Hello, World!"


app.include_router(api_router, prefix=settings.API_V1_STR)
