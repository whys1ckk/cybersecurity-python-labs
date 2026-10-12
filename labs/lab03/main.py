from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared.student import STUDENT_NAME, GROUP_NAME, VARIANT_NUMBER
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title="Реєстр ризиків контейнерної конфігурації (Варіант 14)",
    description="Сервіс обліку результатів перевірки конфігурації контейнерного середовища. Одиниця вимірювання: score.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(categories.router)
app.include_router(records.router)

@app.get("/ping", tags=["System"])
def ping():
    """Перевірка доступності API."""
    return {"status": "ok"}

@app.get("/student", tags=["System"])
def student_info():
    """Інформація про студента та варіант."""
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER
    }