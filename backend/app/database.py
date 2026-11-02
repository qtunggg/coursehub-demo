from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

# Tự động lấy giá trị từ .env, nếu thiếu sẽ dùng giá trị mặc định của project
db_user = os.getenv("DB_USER", "coursehub_user")
db_password = os.getenv("DB_PASSWORD", "coursehub_password")
db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", "5432"))
db_name = os.getenv("DB_NAME", "coursehub")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name,
)

engine = create_engine(database_url, pool_pre_ping=True)