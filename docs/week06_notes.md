# Buổi 6 - Docker, Testing, CI

## Môi trường
- OS: Windows 10 Pro 22H2 (10.0.19045), RAM 7.9 GB, i5-6200U 4 luồng
- Docker: Docker Desktop (WSL2), giới hạn qua `%USERPROFILE%\.wslconfig`: memory=2GB, processors=2
- Python: 3.15 (local `.venv`, image `python:3.15-slim`, CI `setup-python` 3.15 — cùng phiên bản)
- Node: local v26 / image `node:22-alpine` / CI 22.12.0 (`engines: >=22.12.0`)

## Tệp mới
| Tệp | Vai trò |
|---|---|
| `backend/Dockerfile` | Image FastAPI, chỉ cài `requirements.txt`, Uvicorn `--host 0.0.0.0 --port 8000`, không `--reload` |
| `backend/requirements-dev.txt` | `-r requirements.txt` + `pytest` (chỉ dùng local/CI) |
| `backend/.env.docker.example` | Mẫu biến `DB_*`, `DB_HOST=host.docker.internal`, không có password thật |
| `backend/tests/test_openapi_contract.py` | Contract test: path + method mà Frontend gọi |
| `pytest.ini` | `pythonpath = .`, chỉ thu thập `test_*.py` (bỏ qua script `week04_concurrency_test.py` cần server thật) |
| `frontend/Dockerfile` | Multi-stage: `node:22-alpine` build → `nginx:alpine` phục vụ `dist` |
| `frontend/nginx.conf` | SPA fallback + `location /api/ { proxy_pass http://backend:8000/; }` |
| `compose.yaml` | `backend` (8000:8000, healthcheck `/health`) + `frontend` (8080:80, chờ backend healthy) |
| `.dockerignore` | Loại `.git`, `.venv`, `node_modules`, `dist`, `.env*` khỏi build context |
| `.github/workflows/ci.yml` | Job backend + frontend song song, job docker chạy sau khi cả hai đạt |

Database vẫn là PostgreSQL `coursehub` trên máy host; không reset schema/dữ liệu, không thay đổi API hay nghiệp vụ.

## Đường đi request (bản Docker)
```
Browser → http://127.0.0.1:8080/api/sections
  → (port mapping 8080:80) Nginx trong container frontend
  → proxy_pass http://backend:8000/sections   (tên service trong network Compose)
  → FastAPI → host.docker.internal:5432 → PostgreSQL trên máy host
```
- `127.0.0.1` bên trong container backend là chính container đó, không phải máy thật → phải dùng `host.docker.internal`.
- Browser không phân giải được tên `backend`; tên này chỉ tồn tại trong network Compose.
- Frontend và API cùng origin 8080 nên bản Docker không cần CORS; CORS Buổi 5 vẫn giữ cho chế độ dev Vite 5173 → 8000.

## Kết quả local
- `pytest backend/tests -q`: **3 passed**
- `npm test`: **8/8 pass**
- `npm run build`: **ok** (`dist/assets/index-*.js` 150 kB)
- `docker compose up --build`: _(điền sau khi chạy: backend healthy? trang 8080 tải được?)_

## Test chứng minh gì / không chứng minh gì
| Kiểm tra | Chứng minh | Không chứng minh |
|---|---|---|
| pytest contract | App import được; các path/method Frontend gọi còn đăng ký | DB thật, transaction, race condition |
| npm test | `api.js` xử lý đúng response giả lập (204, lỗi JSON, detail…) | Nginx, network Docker, DB |
| npm run build | JSX/CSS/import tạo được bundle production | Nghiệp vụ đăng ký |
| compose up + thao tác thật | Các service nối được nhau qua API thật | Mọi edge case/concurrency |

## Một luồng tích hợp đã kiểm tra
- Request: `POST http://127.0.0.1:8080/api/enrollments` (22000004, WEB-01) → `DELETE /api/enrollments/22000004/WEB-01`
- HTTP status: _(201 / 204)_
- SQL xác nhận: _(enrollments + enrollment_events CREATED/CANCELLED, `database/13_week05_verify.sql`)_

## Debug / AI
- Phát hiện: `backend/tests/week04_concurrency_test.py` khớp mẫu `*_test.py` mặc định của pytest → nếu không cấu hình, CI sẽ thu thập file gọi `127.0.0.1:8000`. Đã thêm `python_files = test_*.py` trong `pytest.ini`.
- `backend/app/database.py` gọi `load_dotenv(backend/.env)`; `.dockerignore` loại `.env` khỏi image nên container chỉ nhận biến từ `env_file: backend/.env.docker`.
- AI (Claude Code) đã dùng để: viết Dockerfile/Compose/CI theo giáo trình, phát hiện vấn đề pytest ở trên. Đã xác minh bằng cách chạy pytest/npm test/build local và kiểm tra `git check-ignore` cho các file `.env*`.

## Pull Request / CI
- Nhánh nộp: `week_6`
- PR: _(week_6 → main)_
- Reviewer: _(tên thành viên)_
- CI run: _(pass/fail và nguyên nhân nếu fail)_
