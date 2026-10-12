import sqlite3
from contextlib import closing
from typing import Any, Dict, List, Optional
from labs.lab03.database import get_connection

def get_categories() -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        cursor = conn.execute("SELECT id, name FROM categories ORDER BY id ASC")
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]

def create_category(name: str) -> Dict[str, Any]:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            cat_id = cursor.lastrowid
        return {"id": cat_id, "name": name}

def delete_category(category_id: int) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0

def get_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            """SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name
               FROM records r JOIN categories c ON r.category_id = c.id
               WHERE r.id = ?""",
            (record_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0], "code": row[1], "title": row[2],
            "category_id": row[3], "value": row[4], "status": row[5], "category_name": row[6]
        }

def get_records(
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    min_value: Optional[float] = None,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    query = """
        SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name
        FROM records r JOIN categories c ON r.category_id = c.id
        WHERE 1=1
    """
    params: List[Any] = []
    
    if category_id is not None:
        query += " AND r.category_id = ?"
        params.append(category_id)
    if status is not None:
        query += " AND r.status = ?"
        params.append(status)
    if min_value is not None:
        query += " AND r.value >= ?"
        params.append(min_value)
    if q is not None:
        query += " AND instr(r.title, ?) > 0"
        params.append(q)
        
    query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with closing(get_connection()) as conn:
        cursor = conn.execute(query, params)
        return [
            {
                "id": row[0], "code": row[1], "title": row[2],
                "category_id": row[3], "value": row[4], "status": row[5], "category_name": row[6]
            }
            for row in cursor.fetchall()
        ]

def create_record(data: Dict[str, Any]) -> Dict[str, Any]:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """INSERT INTO records (code, title, category_id, value, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (data["code"], data["title"], data["category_id"], data["value"], data["status"])
            )
            rec_id = cursor.lastrowid
    return get_record_by_id(rec_id) # type: ignore

def update_record(record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """UPDATE records SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                   WHERE id = ?""",
                (data["code"], data["title"], data["category_id"], data["value"], data["status"], record_id)
            )
            if cursor.rowcount == 0:
                return None
    return get_record_by_id(record_id)

def delete_record(record_id: int) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
            return cursor.rowcount > 0

def create_records_bulk(records_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        with conn:
            created_ids = []
            for data in records_data:
                cursor = conn.execute(
                    """INSERT INTO records (code, title, category_id, value, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    (data["code"], data["title"], data["category_id"], data["value"], data["status"])
                )
                created_ids.append(cursor.lastrowid)
        
        results = []
        for rid in created_ids:
            rec = get_record_by_id(rid)
            if rec:
                results.append(rec)
        return results