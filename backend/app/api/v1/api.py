from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, youtube, monitoring

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"]) 