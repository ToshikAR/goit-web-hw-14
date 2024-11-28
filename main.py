import logging
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
import uvicorn

from src.app_contacts import routes_contacts
from src.app_index import routes_index
from src.app_users import routes_auth, routes_user
from src.app_users.services_cache import get_redis_client
from src.app_users.services_middleware import (
    CORSMiddlewareConfig,
    BanIPsMiddleware,
    UserAgentBanMiddleware,
)


app = FastAPI(title="Contact Application")

redis_client = None

app.add_middleware(CORSMiddlewareConfig)
app.add_middleware(BanIPsMiddleware)
app.add_middleware(UserAgentBanMiddleware)


BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(routes_index.router)
app.include_router(routes_auth.router, prefix="/api")
app.include_router(routes_user.router, prefix="/api")
app.include_router(routes_contacts.router, prefix="/api")


@app.on_event("startup")
async def startup():
    global redis_client
    try:
        redis_client = await get_redis_client()
        await FastAPILimiter.init(redis_client)
        logging.info("FastAPILimiter initialized successfully.")
    except Exception as err:
        logging.error(f"Startup on_event failed: {err}")


@app.on_event("shutdown")
async def shutdown():
    global redis_client
    if redis_client:
        await redis_client.close()
        logging.info("Redis client closed successfully.")


@app.get("/")
def root():
    return {"message": "REST APP v1.0"}


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=int(os.environ.get("PORT", 8000)),
#         reload=True,
#         log_level="info",
#     )
