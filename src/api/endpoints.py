from fastapi import APIRouter
from src.api.routes.graph_text_input import router as graph_input_router
from src.api.routes.graph_audio_input import router as graph_audio_router

router = APIRouter()
routers = [graph_audio_router, graph_input_router]

for route in routers:
    router.include_router(router=route)
