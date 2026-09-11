from fastapi import FastAPI
from sqlalchemy import text
from app.core.config import settings
from app.database.connection import engine
#Router imports
from app.routers.users import router as users_router
from app.auth.router import router as auth_router
from app.routers.account import router as account_router
from app.routers.transaction import router as transaction_router
from app.routers.category import router as category_router
from app.routers.budget import router as budget_router
from app.routers.report import router as report_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(category_router)
app.include_router(budget_router)
app.include_router(report_router)

@app.get("/")
def root():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        database_connection = result.scalar()

    return {
        "message": "FinTrack API is running",
        "database_connection": database_connection,
    }