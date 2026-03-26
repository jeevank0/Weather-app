from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, object]:
    return {"success": True, "data": {"status": "ok"}}
