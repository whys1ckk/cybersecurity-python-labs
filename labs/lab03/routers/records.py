import sqlite3
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from labs.lab03 import repository
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])

@router.get("", response_model=List[RecordRead])
def get_records(
    category_id: Optional[int] = Query(None, gt=0),
    status_val: Optional[str] = Query(None, alias="status"),
    min_value: Optional[float] = Query(None, ge=0, le=10),
    q: Optional[str] = Query(None, min_length=1, max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Отримати список записів із можливістю фільтрації та пагінації."""
    return repository.get_records(
        category_id=category_id,
        status=status_val,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset
    )

@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int):
    """Отримати конкретний запис за його ідентифікатором."""
    record = repository.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Запис не знайдено.")
    return record

@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(payload: RecordCreate):
    """Створити новий запис."""
    try:
        return repository.create_record(payload.model_dump())
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "foreign key" in err_msg:
            raise HTTPException(status_code=404, detail="Вказана категорія не існує.")
        raise HTTPException(status_code=409, detail="Запис із таким кодом вже існує.")

@router.put("/{record_id}", response_model=RecordRead)
def replace_record(record_id: int, payload: RecordReplace):
    """Повністю замінити змінювані поля наявного запису."""
    try:
        updated = repository.update_record(record_id, payload.model_dump())
        if not updated:
            raise HTTPException(status_code=404, detail="Запис не знайдено.")
        return updated
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "foreign key" in err_msg:
            raise HTTPException(status_code=404, detail="Вказана категорія не існує.")
        raise HTTPException(status_code=409, detail="Запис із таким кодом вже існує.")

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int):
    """Видалити запис за ідентифікатором."""
    success = repository.delete_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запис не знайдено.")

@router.post("/bulk", response_model=List[RecordRead], status_code=status.HTTP_201_CREATED)
def create_records_bulk(payload: List[RecordCreate]):
    """Пакетне створення записів в одній атомарній транзакції."""
    if not (1 <= len(payload) <= 100):
        raise HTTPException(status_code=422, detail="Кількість елементів пакета має бути від 1 до 100.")
    
    dicts = [item.model_dump() for item in payload]
    try:
        return repository.create_records_bulk(dicts)
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "foreign key" in err_msg:
            raise HTTPException(status_code=404, detail="Один із записів посилається на неіснуючу категорію.")
        raise HTTPException(status_code=409, detail="Конфлікт унікальності коду в пакеті або базі даних.")