# CourseHub - Buoi 5 Notes: React Frontend

## 1. Bản phác giao diện (Figma / Wireframe)
- **Link thiết kế Figma:** [CourseHub Figma Design](https://www.figma.com/design/2JOSz9YHBPU8b7xDlV7oR2/CourseHub---Bu%E1%BB%95i-5?node-id=1-2&t=kxbopTMWJTpYYeIp-1)
- Frame Desktop ~1280 px: tiêu đề, chọn sinh viên, danh sách lớp, lớp đã đăng ký.
- Có trạng thái "Đăng ký thành công" và "Hết chỗ" (WEB-01, RACE-01).

## 2. Thành phần đã làm
- Backend: chỉ thêm `CORSMiddleware` trong `backend/app/main.py`
  (origin `http://localhost:5173`, `http://127.0.0.1:5173`; method GET/POST/DELETE). Giữ version 0.4.0, giữ `FOR UPDATE` và ghi `enrollment_events`.
- Frontend (`frontend/`, React 18.2.0 + Vite 7.1.7):
  - `src/api.js`: hàm `api()` dùng chung, xử lý 204, lỗi JSON, `detail` dạng chuỗi/danh sách.
  - `src/App.jsx`: state, `useEffect` + `AbortController`, đăng ký/hủy, lọc tại trình duyệt.
  - `src/components/`: `Notice.jsx`, `SectionTable.jsx`, `EnrollmentList.jsx`.
  - `src/styles.css`: Flex, Grid hai cột, media query 900 px / 560 px.
  - `tests/api.test.mjs`: 8 tình huống HTTP giả lập cho `api.js`.
- API sử dụng: `GET /courses`, `GET /sections`, `GET /students/{student_id}/enrollments`,
  `POST /enrollments`, `DELETE /enrollments/{student_id}/{class_section_id}`.

## 3. Cách chạy
| Thành phần | Thư mục | Lệnh |
|---|---|---|
| Backend | `coursehub-demo` | `python -m uvicorn backend.app.main:app --reload` |
| Frontend | `coursehub-demo/frontend` | `npm ci` (lần đầu) rồi `npm run dev` → http://127.0.0.1:5173 |
| Kiểm thử | `coursehub-demo/frontend` | `npm test`; `npm run build` |

Cấu hình: `backend/.env` (DB_*), `frontend/.env.local` (`VITE_API_BASE_URL=http://127.0.0.1:8000`). Cả hai không commit.

## 4. Kết quả kiểm tra thực tế
| Thao tác | Kết quả |
|---|---|
| `GET /health` | 200, `database: connected` |
| Preflight `OPTIONS /enrollments` từ origin 5173 | 200, `allow-origin: http://127.0.0.1:5173` |
| `GET /students/22000004/enrollments` (chưa đăng ký) | 200, `[]` → "Sinh viên chưa đăng ký lớp nào." |
| `POST /enrollments` 22000004 / WEB-01 | 201; SQL: WEB-01 enrolled = 3, remaining = 0 |
| POST lặp lại 22000004 / WEB-01 | 409 "Sinh vien da dang ky lop nay" |
| POST gửi `class_id` thay `class_section_id` | 422 "Field required" |
| `DELETE /enrollments/22000004/WEB-01` | 204, body trống; WEB-01 trở lại enrolled = 2, remaining = 1 |
| `GET /students/99999999/enrollments` | 404 "Khong tim thay sinh vien" |
| RACE-01: A = 22000002 POST | 201 |
| RACE-01: B = 22000004 POST (dữ liệu cũ) | 409 "Lop hoc phan da het cho" |
| Dọn dẹp: DELETE 22000002 / RACE-01 | 204; RACE-01 enrolled = 0, remaining = 1 |
| `npm test` | 8/8 pass |
| `npm run build` | thành công, tạo `dist/` |

Nhật ký `enrollment_events` (dataset = demo) có thêm CREATED rồi CANCELLED cho từng thao tác,
không xóa sự kiện cũ. SQL xác nhận: `database/13_week05_verify.sql`.

## 5. Ghi chú
- Lọc / "chỉ hiện lớp còn chỗ" chạy tại trình duyệt, không phải phân trang PostgreSQL.
- Thử hai cửa sổ chỉ kiểm tra giao diện xử lý dữ liệu cũ; test concurrency bắt buộc vẫn là script hai worker của Buổi 4.
- Ô mã sinh viên chỉ chọn dữ liệu demo, không phải đăng nhập.
