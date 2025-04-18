from fastapi import APIRouter
from src.api.routes.graph_text_input import router as graph_router

router = APIRouter()

router.include_router(router=graph_router)
