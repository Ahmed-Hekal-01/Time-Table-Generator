# Backend API Documentation

**Base URL**: `http://localhost:5000/api`

## Overview
This API provides access to the Timetable Generator system. It supports:
1.  **Viewing Timetables**: By Level, Professor, Lab Instructor, or Room.
2.  **Managing Data**: CRUD operations for Courses, Rooms, Lab Instructors, and Professors.
3.  **Regeneration**: Triggering the scheduling algorithm to rebuild the timetable.

---

## 1. Timetable Views

### Get Timetable by Level
Returns the schedule organized by student levels (1-4).

*   **Endpoint**: `GET /levels` or `GET /levels/<level_id>`
*   **Parameters**: `level_id` (optional, integer 1-4)
*   **Response Example**:
    ```json
    {
      "metadata": { "days": [...], "time_slots": [...] },
      "levels": {
        "Level1": {
          "L1-G1": {
            "lectures": [ ... ],
            "labs_by_section": { ... }
          }
        }
      }
    }
    ```

### Get Timetable by Professor
Returns the schedule for a specific professor or all professors.

*   **Endpoint**: `GET /professors` or `GET /professors/<professor_name>`
*   **Parameters**: `professor_name` (optional, string)

### Get Timetable by Lab Instructor
Returns the schedule for a specific TA or all TAs.

*   **Endpoint**: `GET /lab-instructors` or `GET /lab-instructors/<instructor_name>`
*   **Parameters**: `instructor_name` (optional, string)

### Get Timetable by Room
Returns the schedule for a specific room or all rooms.

*   **Endpoint**: `GET /rooms` or `GET /rooms/<room_code>`
*   **Parameters**: `room_code` (optional, string)

---

## 2. Data Management (CRUD)

**Note**: All POST and DELETE requests expect `Content-Type: application/json`.

### Courses
Manage courses for all levels.

*   **List Courses**: `GET /manage/courses`
*   **Add Course**: `POST /manage/courses`
    *   **Payload (Level 1 & 2)**:
        ```json
        {
          "level": 1,
          "has_lab": true, // true to create both lecture and lab, false for lecture only
          "data": {
            "course_code": "CSE101",
            "course_name": "Intro to CS",
            "instructor_name": "Prof. Smith",
            "instructor_id": 101,
            "level": 1
          }
        }
        ```
    *   **Payload (Level 3 & 4)**:
        ```json
        {
          "level": 3,
          "department": "CSC", // CSC, AID, BIF, or CNC
          "has_lab": false,
          "data": { ... }
        }
        ```
*   **Delete Course**: `DELETE /manage/courses`
    *   **Payload**: `{"level": 1, "course_code": "CSE101"}`

### Rooms
Manage physical rooms (Labs and Lecture Halls).

*   **List Rooms**: `GET /manage/rooms`
*   **Add Room**: `POST /manage/rooms`
    *   **Payload**:
        ```json
        {
          "room_code": "C2.201",
          "room_type": "lec", // "lec" or "lab"
          "capacity": 60,
          "building": "C2"
        }
        ```
*   **Delete Room**: `DELETE /manage/rooms`
    *   **Payload**: `{"room_code": "C2.201"}`

### Lab Instructors (TAs)
Manage Teaching Assistants.

*   **List TAs**: `GET /manage/lab-instructors`
*   **Add TA**: `POST /manage/lab-instructors`
    *   **Payload**:
        ```json
        {
          "instructor_id": "TA_001",
          "instructor_name": "Jane Doe",
          "qualified_labs": ["CSE101", "PHY101"],
          "max_hours_per_week": 18,
          "instructor_type": "TA"
        }
        ```
*   **Delete TA**: `DELETE /manage/lab-instructors`
    *   **Payload**: `{"instructor_id": "TA_001"}`

### Professors
Manage Professors.

*   **List Professors**: `GET /manage/professors`
*   **Add Professor**: `POST /manage/professors`
    *   **Payload**:
        ```json
        {
          "instructor_id": 505,
          "instructor_name": "Dr. Alan Turing"
        }
        ```
*   **Delete Professor**: `DELETE /manage/professors`
    *   **Payload**: `{"instructor_id": 505}`

---

## 3. System Operations

### Regenerate Schedule
Triggers the scheduling algorithm to re-assign times and rooms based on the current data. Call this after making changes to courses, rooms, or instructors to update the views.

*   **Endpoint**: `POST /regenerate`
*   **Response**:
    ```json
    {
      "status": "success",
      "message": "Timetable regenerated successfully",
      "assignments": 250
    }
    ```
