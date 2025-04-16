import fastapi

router = fastapi.APIRouter(prefix="/graph_generate", tags=["accounts"])


@router.get("/", summary="Получить всех студентов")
async def get_all_students():
    return "penis"
