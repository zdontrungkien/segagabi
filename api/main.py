from fastapi import FastAPI

from api import config
from api.routers import router as seg
from api.services.repository import get_mongo_meta
from api.utils import get_logger, init_mongo

global_settings = config.get_settings()

if global_settings.environment == "local":
    get_logger("uvicorn")

app = FastAPI()

app.include_router(seg, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    app.state.logger = get_logger(__name__)
    app.state.logger.info("Starting api on your crawler...mmm")
    app.state.mongo_client, app.state.mongo_db, app.state.mongo_collection = await init_mongo(
        global_settings.db_name, global_settings.db_url, global_settings.collection
    )


@app.on_event("shutdown")
async def shutdown_event():
    app.state.logger.info("Parking tractors in garage...")


@app.get("/health-check")
async def health_check():
    # # TODO: check settings dependencies passing as args and kwargs
    # a = 5
    # try:
    #     assert 5 / 0
    # except Exception:
    #     app.state.logger.exception("My way or highway...")
    return await get_mongo_meta()
