"""Contract test: kiểm tra các route Frontend đang gọi vẫn được đăng ký trong OpenAPI.

Không kết nối database, không chứng minh transaction/row lock hay nghiệp vụ đúng.
"""

from backend.app.main import app

REQUIRED_PATHS = {
    "/health",
    "/courses",
    "/sections",
    "/students/{student_id}/enrollments",
    "/enrollments",
    "/enrollments/{student_id}/{class_section_id}",
}


def test_required_paths_are_registered():
    paths = set(app.openapi()["paths"])
    missing = REQUIRED_PATHS - paths
    assert not missing, f"Missing API paths: {sorted(missing)}"


def test_enrollment_methods_are_registered():
    paths = app.openapi()["paths"]
    assert "post" in paths["/enrollments"]
    assert "delete" in paths["/enrollments/{student_id}/{class_section_id}"]


def test_read_endpoints_use_get():
    # Bài tự thực hành 1: các endpoint đọc mà Frontend dùng phải là GET.
    paths = app.openapi()["paths"]
    assert "get" in paths["/sections"]
    assert "get" in paths["/courses"]
    assert "get" in paths["/students/{student_id}/enrollments"]
