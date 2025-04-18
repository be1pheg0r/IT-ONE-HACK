from fastapi import APIRouter
from src.api.routes.graph import router as graph_audio_router

router = APIRouter()

router.include_router(router=graph_audio_router)
