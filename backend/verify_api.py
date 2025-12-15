import requests
import json

BASE_URL = "http://localhost:5000"

def test_get_all_courses():
    print("Testing GET /api/courses...")
    try:
        response = requests.get(f"{BASE_URL}/api/courses")
        if response.status_code == 200:
            courses = response.json()
            print(f"SUCCESS: Retrieved {len(courses)} courses.")
            if len(courses) > 0:
                print("Sample course:", courses[0])
            return True
        else:
            print(f"FAILED: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"FAILED: Connection error: {e}")
        return False

def test_add_course_with_lab():
    print("\nTesting POST /api/manage/courses (Add Course with Lab)...")

    # Test data
    course_code = "TEST999"
    payload = {
        "level": 1,
        "has_lab": True,
        "data": {
            "course_code": course_code,
            "course_name": "Test Course With Lab",
            "instructor_name": "Test Instructor",
            "instructor_id": 999,
            "level": 1
        }
    }

    try:
        # 1. Add Course
        response = requests.post(f"{BASE_URL}/api/manage/courses", json=payload)
        if response.status_code != 200:
            print(f"FAILED: Add course failed. {response.text}")
            return False

        print("Course added successfully.")

        # 2. Verify it exists in GET /api/courses
        response = requests.get(f"{BASE_URL}/api/courses")
        courses = response.json()

        added_course = next((c for c in courses if c["course_code"] == course_code), None)
        if not added_course:
            print("FAILED: Added course not found in /api/courses")
            return False

        if not added_course.get("has_lab"):
            print("FAILED: Added course does not have 'has_lab=True' in response")
            return False

        print("SUCCESS: Course verified with has_lab=True")

        # 3. Clean up (Delete)
        print("Cleaning up...")
        requests.delete(f"{BASE_URL}/api/manage/courses", json={
            "level": 1,
            "course_code": course_code
        })

        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    success_get = test_get_all_courses()
    success_post = test_add_course_with_lab()

    if success_get and success_post:
        print("\nALL TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")
