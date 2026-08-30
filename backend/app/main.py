from fastapi import FastAPI
from sqlalchemy import text
from app.core.config import settings
from app.database.connection import engine
from app.routers.users import router as users_router
from app.auth.router import router as auth_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(users_router)
app.include_router(auth_router)


@app.get("/")
def root():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        database_connection = result.scalar()

    return {
        "message": "FinTrack API is running",
        "database_connection": database_connection,
    }