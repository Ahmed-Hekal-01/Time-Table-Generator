# Project Report: Timetable Generation System

## 1. Project Overview
The **Timetable Generation System** is a full-stack application designed to automate the scheduling of academic courses, labs, and lectures. It manages complex constraints such as room availability, instructor qualifications, and student group schedules to produce conflict-free timetables for multiple academic levels (1-4).

### Key Features
- **Automated Scheduling**: Uses a heuristic-based algorithm to assign times and rooms.
- **Constraint Management**: Handles hard constraints (conflicts) and soft constraints (load balancing).
- **Resource Management**: Manages Professors, Lab Instructors, Rooms, and Courses.
- **Multi-Level Support**: Generates schedules for Levels 1, 2, 3, and 4.
- **Interactive Admin Dashboard**: Allows manual management of all resources and viewing of generated timetables.

---

## 2. System Architecture & Data Flow

### 2.1 Technology Stack
- **Backend**: Python (Flask)
- **Frontend**: React (TypeScript)
- **Data Storage**: CSV and JSON files (for portability and simplicity)

### 2.2 Data Flow
The system follows a clear flow from data input to schedule generation:

1.  **Data Input (Frontend -> API -> CSV/JSON)**
    - Administrators use the React dashboard to add/edit Professors, Courses, Rooms, etc.
    - The Flask API receives these requests and updates the underlying CSV/JSON files in the `backend/CSV` directory.
    - *Note*: These changes are persisted but do not immediately affect the active schedule.

2.  **Schedule Generation (API -> Scheduler)**
    - When "Regenerate Timetable" is clicked, the API initializes the `TimetableScheduler`.
    - The scheduler reads the latest data from the files.
    - It executes the scheduling algorithm (detailed below).
    - The resulting schedule is stored in memory.

3.  **Data Retrieval (Frontend <- API)**
    - The Frontend requests timetable data (e.g., `GET /api/levels`).
    - The API serves the generated schedule from memory.

---

## 3. Timetable Generation Algorithm
The core of the system is the `TimetableScheduler` class in `backend/app/scheduler.py`. It uses a **greedy heuristic algorithm** with backtracking capabilities to find a valid schedule.

### 3.1 Initialization
- **Inputs**: Rooms, Groups, Sections, Time Slots, Course Data (Lectures/Labs), and Instructors.
- **Tracker**: A `ScheduleTracker` object is created to maintain the state of every resource (Room, Instructor, Student Group) for every time slot (Day + Slot Number).

### 3.2 The Algorithm Flow

The generation process happens in a specific order to maximize success:

#### Step 1: Schedule Lectures (Level by Level)
Lectures are harder to schedule because they involve entire groups (multiple sections) and specific professors.
1.  **Sort**: Lectures are sorted to prioritize those with shared instructors or specific constraints.
2.  **Iterate**: For each lecture:
    - **Check Constraints**:
        - Is the **Instructor** free?
        - Is the **Student Group** free?
        - Are all **Sections** in the group free?
    - **Find Room**: Look for an available lecture hall (`lec` type).
    - **Assign**: If a valid slot and room are found, the assignment is made and recorded in the `ScheduleTracker`.

#### Step 2: Schedule Labs (Level by Level)
Labs are more flexible but more numerous. They are assigned to individual sections.
1.  **Sort**: Labs are sorted, prioritizing those with specific room requirements (e.g., "Physics Lab").
2.  **Iterate**: For each lab:
    - **Shuffle Slots**: Time slots are tried in a random order to distribute the workload evenly across the week.
    - **Check Constraints**:
        - Is the **Section** free?
        - **Instructor Limit**: Checks if the number of concurrent labs for this course exceeds the number of available qualified instructors.
    - **Find Room**:
        - If a specific room is required, check only that room.
        - Otherwise, find any available lab room (`lab` type).
    - **Assign**: If valid, the assignment is made.

#### Step 3: Department Scheduling (Levels 3 & 4)
For higher levels, courses are often department-specific (e.g., CS, IS).
- The algorithm treats departments as "Groups" and follows a similar logic to Step 1, ensuring that students in the "CS" department don't have conflicting lectures.

### 3.3 Conflict Resolution
The system uses a "Hard Constraint" model. If a valid slot cannot be found for a critical resource (like a Lecture), the scheduler will:
1.  Log a warning.
2.  Skip the assignment (to prevent an invalid schedule).
3.  Report the conflict in the final output.

### 3.4 Optimization
- **Load Balancing**: Labs are distributed randomly to prevent stacking all labs on one day.
- **Instructor Limits**: The system dynamically calculates how many labs of "Physics" can run at once based on the number of instructors qualified to teach "Physics".

---

## 4. Conclusion
The system provides a robust way to generate timetables by strictly enforcing hard constraints (no double booking) while attempting to optimize for soft constraints (even distribution). The modular design allows for easy updates to data without breaking the core logic.
