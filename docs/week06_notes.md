# Buổi 6 - Docker, Testing, CI

## Môi trường
- OS: Windows 10 Pro
- Docker version: Docker Desktop (WSL2)
- Python / Node version: Python 3.15, Node 22

## Kết quả local
- pytest backend/tests -q: 3 passed
- npm test: 8/8 pass
- npm run build: build thành công
- docker compose up --build:

## Một luồng tích hợp đã kiểm tra
- Request:
- HTTP status:
- SQL xác nhận:

## Debug / AI
- Lỗi gặp phải: lúc chạy pytest thì nó lấy luôn file week04_concurrency_test.py (vì tên có đuôi _test.py), file này gọi server thật nên lên CI sẽ bị đỏ.
- Bằng chứng đã xem: thêm pytest.ini chỉ lấy file test_*.py, chạy lại pytest thì còn 3 test và đều pass.
- Nếu dùng AI: có dùng Claude để tham khảo cách viết Dockerfile, compose và workflow CI. Mình đã đọc lại từng file, chạy test, build ở máy và xem CI trên GitHub chạy xanh rồi mới commit.

## Pull Request / CI
- PR: week_6 -> main
- Reviewer:
- CI run: pass, cả 3 job backend, frontend, docker đều xanh
