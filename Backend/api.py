"""
Flask API for Timetable System
Provides 4 endpoints for different timetable views
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from app.scheduler import TimetableScheduler
from app.data_loader import (
    generate_time_slots,
    generate_groups_and_sections,
    load_rooms_from_csv,
    load_lab_instructors_from_csv,
    load_course_data
)
from app.instructor_assignment import assign_instructors_to_labs

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Global scheduler instance
scheduler = None


def initialize_scheduler():
    """Initialize and generate the timetable"""
    global scheduler

    print("Initializing timetable scheduler...")

    # Load all data
    time_slots = generate_time_slots()
    groups, sections = generate_groups_and_sections()
    rooms = load_rooms_from_csv("./CSV/rooms.csv")
    lab_instructors = load_lab_instructors_from_csv("./CSV/inslab.csv")
    level_1_data, level_2_data = load_course_data()

    # Create scheduler
    scheduler = TimetableScheduler(
        rooms, groups, sections, time_slots,
        level_1_data, level_2_data
    )

    # Generate schedule
    success = scheduler.generate_schedule()
    if not success:
        raise Exception("Failed to generate timetable")

    # Assign lab instructors
    instructor_success = assign_instructors_to_labs(scheduler, lab_instructors)
    if not instructor_success:
        print("Warning: Not all lab instructors could be assigned")

    print("Timetable initialized successfully!")
    return scheduler


@app.route('/api/levels', methods=['GET'])
def get_levels_table():
    """
    Endpoint 1: Get timetable organized by levels and groups
    Returns: Timetable for Level 1 and Level 2 with all groups
    """
    if scheduler is None:
        return jsonify({"error": "Scheduler not initialized"}), 500

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    time_slots_info = [
        {"slot": 1, "time": "9:00-10:30"},
        {"slot": 2, "time": "10:45-12:15"},
        {"slot": 3, "time": "12:30-14:00"},
        {"slot": 4, "time": "14:15-15:45"}
    ]

    levels_data = {
        "metadata": {
            "days": days,
            "time_slots": time_slots_info
        },
        "levels": {}
    }

    # Organize by level and group
    for level in [1, 2]:
        levels_data["levels"][f"Level{level}"] = {}

        for group in scheduler.groups:
            if group.level != level:
                continue

            # Collect all assignments for this group (lectures + labs from all sections)
            group_assignments = []

            # Get lectures (shared by all sections in the group)
            for day in days:
                for slot_num in range(1, 5):
                    lectures = [
                        a for a in scheduler.assignments
                        if a.type == "lecture"
                        and group.group_id in a.assigned_to
                        and a.time_slot.day == day
                        and a.time_slot.slot_number == slot_num
                    ]

                    if lectures:
                        lecture = lectures[0]
                        group_assignments.append({
                            "day": day,
                            "slot": slot_num,
                            "time": time_slots_info[slot_num - 1]["time"],
                            "course_code": lecture.course_code,
                            "course_name": lecture.course_name,
                            "room": lecture.room,
                            "instructor": lecture.instructor,
                            "type": "lecture",
                            "sections": lecture.assigned_to
                        })

            # Get labs for each section in the group
            section_labs = {}
            for section in group.sections:
                section_labs[section.section_id] = []

                labs = [
                    a for a in scheduler.assignments
                    if a.type == "lab"
                    and section.section_id in a.assigned_to
                ]

                for lab in labs:
                    section_labs[section.section_id].append({
                        "day": lab.time_slot.day,
                        "slot": lab.time_slot.slot_number,
                        "time": time_slots_info[lab.time_slot.slot_number - 1]["time"],
                        "course_code": lab.course_code,
                        "course_name": lab.course_name,
                        "room": lab.room,
                        "instructor": lab.lab_instructor_name,
                        "type": "lab",
                        "section": section.section_id
                    })

            levels_data["levels"][f"Level{level}"][group.group_id] = {
                "group_id": group.group_id,
                "sections": [s.section_id for s in group.sections],
                "lectures": group_assignments,
                "labs_by_section": section_labs
            }

    return jsonify(levels_data)


@app.route('/api/lab-instructors', methods=['GET'])
def get_lab_instructors_table():
    """
    Endpoint 2: Get timetable organized by lab instructors
    Returns: Schedule for each lab instructor showing their assigned labs
    """
    if scheduler is None:
        return jsonify({"error": "Scheduler not initialized"}), 500

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    time_slots_info = [
        {"slot": 1, "time": "9:00-10:30"},
        {"slot": 2, "time": "10:45-12:15"},
        {"slot": 3, "time": "12:30-14:00"},
        {"slot": 4, "time": "14:15-15:45"}
    ]

    instructors_data = {
        "metadata": {
            "days": days,
            "time_slots": time_slots_info
        },
        "instructors": {}
    }

    # Group by lab instructor
    for assignment in scheduler.assignments:
        if assignment.type == "lab" and assignment.lab_instructor_name:
            instructor_name = assignment.lab_instructor_name

            if instructor_name not in instructors_data["instructors"]:
                instructors_data["instructors"][instructor_name] = {
                    "instructor_id": assignment.lab_instructor_id,
                    "instructor_name": instructor_name,
                    "labs": []
                }

            instructors_data["instructors"][instructor_name]["labs"].append({
                "day": assignment.time_slot.day,
                "slot": assignment.time_slot.slot_number,
                "time": time_slots_info[assignment.time_slot.slot_number - 1]["time"],
                "course_code": assignment.course_code,
                "course_name": assignment.course_name,
                "room": assignment.room,
                "sections": assignment.assigned_to
            })

    # Sort each instructor's labs by day and time
    for instructor in instructors_data["instructors"].values():
        instructor["labs"].sort(
            key=lambda x: (days.index(x["day"]), x["slot"])
        )

    return jsonify(instructors_data)


@app.route('/api/professors', methods=['GET'])
def get_professors_table():
    """
    Endpoint 3: Get timetable organized by professors (lecture instructors)
    Returns: Schedule for each professor showing their lectures
    """
    if scheduler is None:
        return jsonify({"error": "Scheduler not initialized"}), 500

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    time_slots_info = [
        {"slot": 1, "time": "9:00-10:30"},
        {"slot": 2, "time": "10:45-12:15"},
        {"slot": 3, "time": "12:30-14:00"},
        {"slot": 4, "time": "14:15-15:45"}
    ]

    professors_data = {
        "metadata": {
            "days": days,
            "time_slots": time_slots_info
        },
        "professors": {}
    }

    # Group by professor
    for assignment in scheduler.assignments:
        if assignment.type == "lecture" and assignment.instructor:
            professor_name = assignment.instructor

            if professor_name not in professors_data["professors"]:
                professors_data["professors"][professor_name] = {
                    "professor_name": professor_name,
                    "lectures": []
                }

            professors_data["professors"][professor_name]["lectures"].append({
                "day": assignment.time_slot.day,
                "slot": assignment.time_slot.slot_number,
                "time": time_slots_info[assignment.time_slot.slot_number - 1]["time"],
                "course_code": assignment.course_code,
                "course_name": assignment.course_name,
                "room": assignment.room,
                "groups": assignment.assigned_to
            })

    # Sort each professor's lectures by day and time
    for professor in professors_data["professors"].values():
        professor["lectures"].sort(
            key=lambda x: (days.index(x["day"]), x["slot"])
        )

    return jsonify(professors_data)


@app.route('/api/rooms', methods=['GET'])
def get_rooms_table():
    """
    Endpoint 4: Get timetable organized by rooms
    Returns: Schedule for each room showing what's happening when
    """
    if scheduler is None:
        return jsonify({"error": "Scheduler not initialized"}), 500

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    time_slots_info = [
        {"slot": 1, "time": "9:00-10:30"},
        {"slot": 2, "time": "10:45-12:15"},
        {"slot": 3, "time": "12:30-14:00"},
        {"slot": 4, "time": "14:15-15:45"}
    ]

    rooms_data = {
        "metadata": {
            "days": days,
            "time_slots": time_slots_info
        },
        "rooms": {}
    }

    # Group by room
    for assignment in scheduler.assignments:
        room_name = assignment.room

        if room_name not in rooms_data["rooms"]:
            # Find room type
            room_obj = next((r for r in scheduler.rooms if r.room_code == room_name), None)
            room_type = room_obj.room_type if room_obj else "unknown"

            rooms_data["rooms"][room_name] = {
                "room_name": room_name,
                "room_type": room_type,
                "schedule": []
            }

        rooms_data["rooms"][room_name]["schedule"].append({
            "day": assignment.time_slot.day,
            "slot": assignment.time_slot.slot_number,
            "time": time_slots_info[assignment.time_slot.slot_number - 1]["time"],
            "type": assignment.type,
            "course_code": assignment.course_code,
            "course_name": assignment.course_name,
            "instructor": assignment.instructor if assignment.type == "lecture" else assignment.lab_instructor_name,
            "assigned_to": assignment.assigned_to
        })

    # Sort each room's schedule by day and time
    for room in rooms_data["rooms"].values():
        room["schedule"].sort(
            key=lambda x: (days.index(x["day"]), x["slot"])
        )

    return jsonify(rooms_data)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "scheduler_initialized": scheduler is not None,
        "assignments": len(scheduler.assignments) if scheduler else 0
    })


@app.route('/api/regenerate', methods=['POST'])
def regenerate_schedule():
    """Regenerate the timetable"""
    try:
        initialize_scheduler()
        return jsonify({
            "status": "success",
            "message": "Timetable regenerated successfully",
            "assignments": len(scheduler.assignments)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    # Initialize scheduler on startup
    try:
        initialize_scheduler()
        print("\n" + "=" * 60)
        print("API Server Starting...")
        print("=" * 60)
        print("\nAvailable Endpoints:")
        print("  - GET  /api/levels           - Timetable by levels and groups")
        print("  - GET  /api/lab-instructors  - Timetable by lab instructors")
        print("  - GET  /api/professors       - Timetable by professors")
        print("  - GET  /api/rooms            - Timetable by rooms")
        print("  - GET  /api/health           - Health check")
        print("  - POST /api/regenerate       - Regenerate timetable")
        print("\nServer running on http://localhost:5000")
        print("=" * 60 + "\n")

        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"ERROR: Failed to initialize scheduler: {e}")

