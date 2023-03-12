from fastapi import APIRouter

from api.routers.v1.seg import router as seg_api

router = APIRouter()

router.include_router(seg_api, prefix="/seg", tags=["v0.0.1"])
