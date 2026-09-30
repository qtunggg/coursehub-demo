# Chạy chương trình Python đầu tiên trong project
print("CourseHub - Buoi 1")

# Mô phỏng dữ liệu bằng list và dictionary
students = [
    {"id": "22000001", "name": "Nguyen Minh Anh", "major": "KHDL"},
    {"id": "22000002", "name": "Tran Duc Long", "major": "KHDL"},
]

courses = [
    {
        "code": "INT2204",
        "name": "Co so du lieu Web va he thong thong tin",
        "capacity": 3,
        "enrolled": 2,
    },
    {
        "code": "INT2205",
        "name": "Khai pha du lieu",
        "capacity": 2,
        "enrolled": 2,
    },
]

enrollments = [
    {"student_id": "22000001", "course_code": "INT2204"}
]

def find_student(student_id):
    """Tìm sinh viên theo mã"""
    for student in students:
        if student["id"] == student_id:
            return student
    return None

def find_course(course_code):
    """Tìm học phần theo mã"""
    for course in courses:
        if course["code"] == course_code:
            return course
    return None

# Duyệt dữ liệu và tính giá trị
for course in courses:
    remaining = course["capacity"] - course["enrolled"]
    print(course["code"], "- con", remaining, "cho")

# Tách xử lý thành hàm
def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    return None
print(find_course("INT2204"))

# Mô phỏng quy tắc đăng ký
def can_enroll(student_id, course_code):
    course = find_course(course_code)

    if course is None:
        return False, "Học phần không tồn tại"
    
    if course["enrolled"] >= course["capacity"]:
        return False, "Lớp đã đủ số lượng"
    
    duplicated = any(
        item["student_id"] == student_id and item["course_code"] == course_code
        for item in enrollments
    )
    if duplicated:
        return False, "Sinh viên đã đăng kí học phần này"
    
    return True, "Có thể đăng kí"

print(can_enroll("22000002", "INT2204"))

# Xử lý dữ liệu nhập sai
try:
    limit = int(input("Nhập số lượng học phần muốn hiển thị: "))
    print(courses[:limit])
except ValueError:
    print("Số lượng phải là số nguyên")

# Hàm tìm kiếm học phần
def search_courses(keyword):
    normalized = keyword.strip().lower()
    results = []

    for course in courses:
        code = course["code"].lower()
        name = course["name"].lower()
        if normalized in code or normalized in name:
            results.append(course)

    return results

print(search_courses("web"))

# BÀI TẬP TỰ LUYỆN

# 1. Hoàn thiện hàm đăng ký học phần
def enroll_student(student_id, course_code):
    student = find_student(student_id)
    if student is None:
        return False, "Sinh viên không tồn tại"

    valid, message = can_enroll(student_id, course_code)
    if not valid:
        return False, message

    course = find_course(course_code)
    enrollments.append({"student_id": student_id, "course_code": course_code})
    course["enrolled"] += 1

    return True, "Đăng kí thành công!"

# 2. Kiểm tra chương trình
if __name__ == "__main__":
    print("\nKẾT QUẢ HIỂN THỊ CHỖ TRỐNG")
    for course in courses:
        remaining = course["capacity"] - course["enrolled"]
        print(course["code"], "con", remaining, "cho")

    print("\n5 TÌNH HUỐNG")

    # Tình huống 1: Đăng ký thành công
    status, msg = enroll_student("22000002", "INT2204")
    print(f"TH1 (Đăng ký thành công): {status} - {msg}")

    # Tình huống 2: Đăng ký trùng
    status, msg = enroll_student("22000001", "INT2204")
    print(f"TH2 (Đăng ký trùng): {status} - {msg}")

    # Tình huống 3: Lớp đã đầy
    status, msg = enroll_student("22000001", "INT2205")
    print(f"TH3 (Lớp đã đầy): {status} - {msg}")

    # Tình huống 4: Mã học phần không tồn tại
    status, msg = enroll_student("22000001", "INT9999")
    print(f"TH4 (Mã HP không tồn tại): {status} - {msg}")

    # Tình huống 5: Mã sinh viên không tồn tại
    status, msg = enroll_student("99999999", "INT2204")
    print(f"TH5 (Mã SV không tồn tại): {status} - {msg}")