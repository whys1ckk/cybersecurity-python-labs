import sqlite3
from typing import List
from fastapi import APIRouter, HTTPException, status
from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryRead])
def get_categories():
    """Отримати список усіх категорій."""
    return repository.get_categories()

@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate):
    """Створити нову категорію."""
    try:
        return repository.create_category(payload.name)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Категорія з такою назвою вже існує."
        )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int):
    """Видалити порожню категорію за її ідентифікатором."""
    try:
        success = repository.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Категорію не знайдено.")
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Неможливо видалити категорію, яка містить записи."
        )