# Timetable API

Flask REST API for the College Timetable System with 4 endpoints.

## Installation

```bash
pip install -r requirements.txt
```

## Running the API

```bash
python api.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Levels Table - `/api/levels`
Get timetable organized by levels and groups.

**Request:**
```bash
GET http://localhost:5000/api/levels
GET http://localhost:5000/api/levels/1
```

**Parameters:**
- `level_id` (optional): Specific level to retrieve (1, 2, 3, or 4)
```

**Response:**
```json
{
  "metadata": {
    "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
    "time_slots": [
      {"slot": 1, "time": "9:00-10:30"},
      {"slot": 2, "time": "10:45-12:15"},
      {"slot": 3, "time": "12:30-14:00"},
      {"slot": 4, "time": "14:15-15:45"}
    ]
  },
  "levels": {
    "Level1": {
      "L1-G1": {
        "group_id": "L1-G1",
        "sections": ["L1-G1-S1", "L1-G1-S2", "L1-G1-S3"],
        "schedule": [...]
      }
    }
  }
}
```

### 2. Lab Instructors Table - `/api/lab-instructors`
Get timetable organized by lab instructors.

**Request:**
```bash
GET http://localhost:5000/api/lab-instructors
GET http://localhost:5000/api/lab-instructors/John%20Doe
```

**Parameters:**
- `instructor_name` (optional): Specific lab instructor name to retrieve
```

**Response:**
```json
{
  "metadata": {...},
  "instructors": {
    "John Doe": {
      "instructor_id": "INS001",
      "instructor_name": "John Doe",
      "labs": [
        {
          "day": "Sunday",
          "slot": 1,
          "time": "9:00-10:30",
          "course_code": "MTH111",
          "course_name": "Calculus I",
          "room": "Lab1",
          "sections": ["L1-G1-S1"]
        }
      ]
    }
  }
}
```

### 3. Professors Table - `/api/professors`
Get timetable organized by professors (lecture instructors).

**Request:**
```bash
GET http://localhost:5000/api/professors
GET http://localhost:5000/api/professors/Dr.%20Smith
```

**Parameters:**
- `professor_name` (optional): Specific professor name to retrieve
```

**Response:**
```json
{
  "metadata": {...},
  "professors": {
    "Dr. Smith": {
      "professor_name": "Dr. Smith",
      "lectures": [
        {
          "day": "Sunday",
          "slot": 1,
          "time": "9:00-10:30",
          "course_code": "MTH111",
          "course_name": "Calculus I",
          "room": "A101",
          "groups": ["L1-G1", "L1-G2"]
        }
      ]
    }
  }
}
```

### 4. Rooms Table - `/api/rooms`
Get timetable organized by rooms.

**Request:**
```bash
GET http://localhost:5000/api/rooms
GET http://localhost:5000/api/rooms/A101
```

**Parameters:**
- `room_id` (optional): Specific room code/ID to retrieve
```

**Response:**
```json
{
  "metadata": {...},
  "rooms": {
    "A101": {
      "room_name": "A101",
      "room_type": "lec",
      "schedule": [
        {
          "day": "Sunday",
          "slot": 1,
          "time": "9:00-10:30",
          "type": "lecture",
          "course_code": "MTH111",
          "course_name": "Calculus I",
          "instructor": "Dr. Smith",
          "assigned_to": ["L1-G1", "L1-G2"]
        }
      ]
    }
  }
}
```

### 5. List Professors - `/api/list/professors`
Get a list of all professors.

**Request:**
```bash
GET http://localhost:5000/api/list/professors
```

**Response:**
```json
{
  "professors": ["Dr. Smith", "Dr. Jones", ...]
}
```

### 6. List Lab Instructors - `/api/list/lab-instructors`
Get a list of all lab instructors.

**Request:**
```bash
GET http://localhost:5000/api/list/lab-instructors
```

**Response:**
```json
{
  "lab_instructors": ["John Doe", "Jane Doe", ...]
}
```

### 7. List Rooms - `/api/list/rooms`
Get a list of all rooms with their types.

**Request:**
```bash
GET http://localhost:5000/api/list/rooms
```

**Response:**
```json
{
  "rooms": [
    {"room_code": "A101", "room_type": "lec"},
    {"room_code": "Lab1", "room_type": "lab"}
  ],
  "total_count": 20,
  "lecture_rooms": 10,
  "lab_rooms": 10
}
```

### 8. Health Check - `/api/health`
Check API status.

**Request:**
```bash
GET http://localhost:5000/api/health
```

**Response:**
```json
{
  "status": "ok",
  "scheduler_initialized": true,
  "assignments": 270
}
```

### 9. Regenerate Schedule - `/api/regenerate`
Regenerate the timetable.

**Request:**
```bash
POST http://localhost:5000/api/regenerate
```

**Response:**
```json
{
  "status": "success",
  "message": "Timetable regenerated successfully",
  "assignments": 270
}
```

## CORS

CORS is enabled for all origins, allowing frontend applications to access the API.

## Frontend Integration Example

```javascript
// Fetch levels table
fetch('http://localhost:5000/api/levels')
  .then(response => response.json())
  .then(data => {
    console.log('Levels:', data);
  });

// Fetch lab instructors table
fetch('http://localhost:5000/api/lab-instructors')
  .then(response => response.json())
  .then(data => {
    console.log('Lab Instructors:', data);
  });

// Fetch professors table
fetch('http://localhost:5000/api/professors')
  .then(response => response.json())
  .then(data => {
    console.log('Professors:', data);
  });

// Fetch rooms table
fetch('http://localhost:5000/api/rooms')
  .then(response => response.json())
  .then(data => {
    console.log('Rooms:', data);
  });
```

## Notes

- The HTML export function has been removed from `app.py`
- All timetable data is now accessible via JSON endpoints
- The API initializes the scheduler on startup
- Use `/api/regenerate` to generate a new schedule without restarting the server
