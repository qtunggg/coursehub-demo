from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .database import engine
from .schemas import EnrollmentCreate

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CourseHub API",
    version="0.4.0",
    description="API thuc hanh Buoi 4 - transaction, locking va hieu nang",
)


class CapacityUpdate(BaseModel):
    capacity: int = Field(..., gt=0, description="Capacity phai lon hon 0")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "CourseHub API dang hoat dong"}


@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.exception("Khong ket noi duoc co so du lieu")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong ket noi duoc co so du lieu",
        ) from exc
    return {"status": "ok", "database": "connected"}


@app.get("/courses", status_code=status.HTTP_200_OK)
def list_courses(
    q: str | None = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> list[dict[str, Any]]:
    sql = "SELECT code, name, credits FROM courses"
    parameters: dict[str, Any] = {}

    if q is not None:
        keyword = q.strip().lower()
        if keyword:
            sql += " WHERE LOWER(code) LIKE :keyword OR LOWER(name) LIKE :keyword"
            parameters["keyword"] = f"%{keyword}%"

    sql += " ORDER BY code ASC"

    with engine.connect() as connection:
        rows = connection.execute(text(sql), parameters).mappings().all()

    courses = [dict(row) for row in rows]
    start = int(skip)
    end = start + int(limit)
    return courses[start:end]


@app.get("/courses/{course_code}")
def get_course(course_code: str) -> dict[str, Any]:
    sql = """
        SELECT code, name, credits
        FROM courses
        WHERE code = :course_code
    """

    with engine.connect() as connection:
        row = (
            connection.execute(
                text(sql),
                {"course_code": course_code.upper()},
            )
            .mappings()
            .first()
        )

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay hoc phan",
        )

    return dict(row)


@app.get("/sections")
def list_sections(
    available_only: bool = False,
) -> list[dict[str, Any]]:
    sql = """
        SELECT class_id, course_code, capacity, enrolled, remaining
        FROM v_section_summary
    """

    if available_only:
        sql += " WHERE remaining > 0"

    sql += " ORDER BY class_id"

    with engine.connect() as connection:
        rows = connection.execute(text(sql)).mappings().all()

    return [dict(row) for row in rows]


@app.get("/sections/{section_id}", status_code=status.HTTP_200_OK)
def get_section_detail(section_id: str) -> dict[str, Any]:
    try:
        with engine.connect() as conn:
            cols_query = text("SELECT * FROM v_section_summary LIMIT 0;")
            cols = conn.execute(cols_query).keys()

            target_col = None
            for col in cols:
                if any(k in col.lower() for k in ["section", "code", "class"]):
                    target_col = col
                    break
            if not target_col:
                target_col = list(cols)[0]

            sql = text(
                f"SELECT * FROM v_section_summary WHERE {target_col} = :sec_id;"
            )
            result = conn.execute(sql, {"sec_id": section_id}).mappings().fetchone()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Lớp học phần '{section_id}' không tồn tại.",
                )

            return dict(result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.patch("/sections/{section_id}/capacity", status_code=status.HTTP_200_OK)
def update_section_capacity(section_id: str, body: CapacityUpdate):
    new_capacity = body.capacity

    with engine.begin() as conn:
        sec = conn.execute(
            text("SELECT capacity FROM class_sections WHERE id = :id FOR UPDATE"),
            {"id": section_id},
        ).fetchone()

        if not sec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lớp học phần '{section_id}' không tồn tại.",
            )

        enrolled_count = (
            conn.execute(
                text("SELECT COUNT(*) FROM enrollments WHERE class_section_id = :id"),
                {"id": section_id},
            ).scalar()
            or 0
        )

        if new_capacity < enrolled_count:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Sức chứa mới ({new_capacity}) nhỏ hơn số sinh viên đã đăng ký ({enrolled_count}).",
            )

        conn.execute(
            text("UPDATE class_sections SET capacity = :cap WHERE id = :id"),
            {"cap": new_capacity, "id": section_id},
        )

    return {
        "message": "Cập nhật sức chứa thành công",
        "section_id": section_id,
        "capacity": new_capacity,
    }


@app.get("/students/{student_id}/enrollments")
def list_student_enrollments(student_id: str) -> list[dict[str, Any]]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    enrollment_sql = """
        SELECT e.student_id,
            s.name AS student_name,
            cs.id AS class_section_id,
            c.code AS course_code,
            c.name AS course_name,
            e.registered_at
        FROM enrollments AS e
        JOIN students AS s ON s.id = e.student_id
        JOIN class_sections AS cs ON cs.id = e.class_section_id
        JOIN courses AS c ON c.code = cs.course_code
        WHERE e.student_id = :student_id
        ORDER BY cs.id
    """

    with engine.connect() as connection:
        student = connection.execute(
            text(student_sql),
            {"student_id": student_id},
        ).first()
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay sinh vien",
            )

        rows = (
            connection.execute(
                text(enrollment_sql),
                {"student_id": student_id},
            )
            .mappings()
            .all()
        )

    return [dict(row) for row in rows]


@app.get("/lecturers", status_code=status.HTTP_200_OK)
def get_lecturers() -> list[dict[str, Any]]:
    query = text("SELECT id, name FROM lecturers ORDER BY id ASC;")
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        lecturers = [{"id": row.id, "name": row.name} for row in result]
    return lecturers


# ==========================================
# CÁC ENDPOINT ĐĂNG KÝ VÀ HỦY ĐĂNG KÝ (PHẦN 5)
# ==========================================


@app.post(
    "/enrollments",
    status_code=status.HTTP_201_CREATED,
)
def create_enrollment(payload: EnrollmentCreate) -> dict[str, str]:
    student_sql = "SELECT id FROM students WHERE id = :student_id"
    lock_section_sql = """
        SELECT id, capacity
        FROM class_sections
        WHERE id = :class_section_id
        FOR UPDATE
    """
    duplicate_sql = """
        SELECT 1
        FROM enrollments
        WHERE student_id = :student_id
          AND class_section_id = :class_section_id
    """
    count_sql = """
        SELECT COUNT(*)
        FROM enrollments
        WHERE class_section_id = :class_section_id
    """
    insert_sql = """
        INSERT INTO enrollments (student_id, class_section_id)
        VALUES (:student_id, :class_section_id)
    """
    event_sql = """
        INSERT INTO enrollment_events
            (student_id, class_section_id, event_type, source, dataset)
        VALUES
            (:student_id, :class_section_id, 'CREATED', 'api', 'demo')
    """
    parameters = {
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }

    try:
        with engine.begin() as connection:
            student = connection.execute(
                text(student_sql),
                {"student_id": payload.student_id},
            ).first()
            if student is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay sinh vien",
                )

            section = (
                connection.execute(
                    text(lock_section_sql),
                    {"class_section_id": payload.class_section_id},
                )
                .mappings()
                .first()
            )
            if section is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Khong tim thay lop hoc phan",
                )

            duplicated = connection.execute(
                text(duplicate_sql), parameters
            ).first()
            if duplicated is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sinh vien da dang ky lop nay",
                )

            enrolled = connection.execute(
                text(count_sql),
                {"class_section_id": payload.class_section_id},
            ).scalar_one()

            if int(enrolled) >= int(section["capacity"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Lop hoc phan da het cho",
                )

            connection.execute(text(insert_sql), parameters)
            connection.execute(text(event_sql), parameters)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dang ky xung dot voi du lieu hien tai",
        ) from exc

    return {
        "message": "Dang ky thanh cong",
        "student_id": payload.student_id,
        "class_section_id": payload.class_section_id,
    }


@app.delete(
    "/enrollments/{student_id}/{class_section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enrollment(student_id: str, class_section_id: str) -> Response:
    lock_section_sql = """
        SELECT id
        FROM class_sections
        WHERE id = :class_section_id
        FOR UPDATE
    """
    delete_sql = """
        DELETE FROM enrollments
        WHERE student_id = :student_id
          AND class_section_id = :class_section_id
        RETURNING student_id
    """
    event_sql = """
        INSERT INTO enrollment_events
            (student_id, class_section_id, event_type, source, dataset)
        VALUES
            (:student_id, :class_section_id, 'CANCELLED', 'api', 'demo')
    """
    parameters = {
        "student_id": student_id,
        "class_section_id": class_section_id,
    }

    with engine.begin() as connection:
        section = connection.execute(
            text(lock_section_sql),
            {"class_section_id": class_section_id},
        ).first()
        if section is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay lop hoc phan",
            )

        deleted = connection.execute(text(delete_sql), parameters).first()
        if deleted is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Khong tim thay dang ky can huy",
            )

        connection.execute(text(event_sql), parameters)

    return Response(status_code=status.HTTP_204_NO_CONTENT)