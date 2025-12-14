"""
Flask API for Timetable System
Provides endpoints for timetable views and data management
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from app.scheduler import TimetableScheduler
from app.data_loader import (
    generate_time_slots,
    generate_groups_and_sections,
    load_rooms_from_csv,
    load_lab_instructors_from_csv,
    load_course_data,
    load_professors_from_csv,
    save_course_data,
    save_rooms_to_csv,
    save_lab_instructors_to_csv,
    save_professors_to_csv
)
from app.instructor_assignment import assign_instructors_to_labs
from app.models import Room, LabInstructor
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Global scheduler instance and data
scheduler = None
global_data = {
    "rooms": [],
    "lab_instructors": [],
    "professors": [],
    "level_1": {},
    "level_2": {},
    "level_3": {},
    "level_4": {}
}
file_paths = {}

def initialize_scheduler():
    """Initialize and generate the timetable"""
    global scheduler, global_data, file_paths

    print("Initializing timetable scheduler...")

    # Determine CSV directory (env var CSV_DIR takes precedence; otherwise use Backend/CSV folder)
    csv_dir = os.environ.get("CSV_DIR")
    if not csv_dir:
        # Get the directory containing api.py (Backend folder)
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        # CSV folder is in the Backend directory
        csv_dir = os.path.join(backend_dir, "CSV")

    csv_dir = os.path.abspath(csv_dir)

    # Verify CSV directory exists
    if not os.path.exists(csv_dir):
        raise Exception(f"CSV directory not found: {csv_dir}")

    # Build file paths
    file_paths = {
        "rooms": os.path.join(csv_dir, "rooms.csv"),
        "lab_instructors": os.path.join(csv_dir, "inslab.csv"),
        "professors": os.path.join(csv_dir, "professors.csv"),
        "courses": os.path.join(csv_dir, "courses.json")
    }

    # Verify critical files exist
    if not os.path.exists(file_paths["rooms"]):
        raise Exception(f"rooms.csv not found: {file_paths['rooms']}")
    if not os.path.exists(file_paths["lab_instructors"]):
        raise Exception(f"inslab.csv not found: {file_paths['lab_instructors']}")

    # Load all data
    time_slots = generate_time_slots()
    groups, sections = generate_groups_and_sections()
    
    global_data["rooms"] = load_rooms_from_csv(file_paths["rooms"])
    global_data["lab_instructors"] = load_lab_instructors_from_csv(file_paths["lab_instructors"])
    global_data["professors"] = load_professors_from_csv(file_paths["professors"])
    
    l1, l2, l3, l4 = load_course_data(file_paths["courses"])
    global_data["level_1"] = l1
    global_data["level_2"] = l2
    global_data["level_3"] = l3
    global_data["level_4"] = l4

    # Create scheduler
    scheduler = TimetableScheduler(
        global_data["rooms"], groups, sections, time_slots,
        global_data["level_1"], global_data["level_2"], 
        global_data["level_3"], global_data["level_4"],
        global_data["lab_instructors"]
    )

    # Generate schedule
    success = scheduler.generate_schedule()
    if not success:
        raise Exception("Failed to generate timetable")

    # Assign lab instructors
    instructor_success = assign_instructors_to_labs(scheduler, global_data["lab_instructors"])
    if not instructor_success:
        print("Warning: Not all lab instructors could be assigned")

    print("Timetable initialized successfully!")
    return scheduler


# ==========================================
# Timetable View Endpoints
# ==========================================

@app.route('/api/levels', methods=['GET'])
@app.route('/api/levels/<int:level_id>', methods=['GET'])
def get_levels_table(level_id=None):
    if scheduler is None:
        return jsonify({"error": "Scheduler not initialized"}), 500

    if level_id is not None and level_id not in [1, 2, 3, 4]:
        return jsonify({"error": f"Invalid level_id: {level_id}. Must be 1, 2, 3, or 4"}), 400

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"]
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

    levels_to_process = [level_id] if level_id else [1, 2, 3, 4]

    for level in levels_to_process:
        levels_data["levels"][f"Level{level}"] = {}

        for group in scheduler.groups:
            if group.level != level:
                continue

            group_assignments = []
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


@app.route('/api/professors', methods=['GET'])
@app.route('/api/professors/<string:professor_name>', methods=['GET'])
def get_professors_table(professor_name=None):
    if scheduler is None:
        return jsonify({"error": "Scheduler not initialized"}), 500

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"]
    time_slots_info = [
        {"slot": 1, "time": "9:00-10:30"},
        {"slot": 2, "time": "10:45-12:15"},
        {"slot": 3, "time": "12:30-14:00"},
        {"slot": 4, "time": "14:15-15:45"}
    ]

    professors_data = {
        "metadata": {"days": days, "time_slots": time_slots_info},
        "professors": {}
    }

    for assignment in scheduler.assignments:
        if assignment.type == "lecture" and assignment.instructor:
            prof_name = assignment.instructor
            if professor_name and prof_name != professor_name:
                continue

            if prof_name not in professors_data["professors"]:
                professors_data["professors"][prof_name] = {
                    "professor_name": prof_name,
                    "lectures": []
                }

            professors_data["professors"][prof_name]["lectures"].append({
                "day": assignment.time_slot.day,
                "slot": assignment.time_slot.slot_number,
                "time": time_slots_info[assignment.time_slot.slot_number - 1]["time"],
                "course_code": assignment.course_code,
                "course_name": assignment.course_name,
                "room": assignment.room,
                "groups": assignment.assigned_to
            })

    if professor_name and not professors_data["professors"]:
        return jsonify({"error": f"Professor '{professor_name}' not found"}), 404

    for professor in professors_data["professors"].values():
        professor["lectures"].sort(key=lambda x: (days.index(x["day"]), x["slot"]))

    return jsonify(professors_data)


@app.route('/api/lab-instructors', methods=['GET'])
@app.route('/api/lab-instructors/<string:instructor_name>', methods=['GET'])
def get_lab_instructors_table(instructor_name=None):
    if scheduler is None:
        return jsonify({"error": "Scheduler not initialized"}), 500

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"]
    time_slots_info = [
        {"slot": 1, "time": "9:00-10:30"},
        {"slot": 2, "time": "10:45-12:15"},
        {"slot": 3, "time": "12:30-14:00"},
        {"slot": 4, "time": "14:15-15:45"}
    ]

    instructors_data = {
        "metadata": {"days": days, "time_slots": time_slots_info},
        "instructors": {}
    }

    for assignment in scheduler.assignments:
        if assignment.type == "lab" and assignment.lab_instructor_name:
            instr_name = assignment.lab_instructor_name
            if instructor_name and instr_name != instructor_name:
                continue

            if instr_name not in instructors_data["instructors"]:
                instructors_data["instructors"][instr_name] = {
                    "instructor_id": assignment.lab_instructor_id,
                    "instructor_name": instr_name,
                    "labs": []
                }

            instructors_data["instructors"][instr_name]["labs"].append({
                "day": assignment.time_slot.day,
                "slot": assignment.time_slot.slot_number,
                "time": time_slots_info[assignment.time_slot.slot_number - 1]["time"],
                "course_code": assignment.course_code,
                "course_name": assignment.course_name,
                "room": assignment.room,
                "sections": assignment.assigned_to
            })

    if instructor_name and not instructors_data["instructors"]:
        return jsonify({"error": f"Lab instructor '{instructor_name}' not found"}), 404

    for instructor in instructors_data["instructors"].values():
        instructor["labs"].sort(key=lambda x: (days.index(x["day"]), x["slot"]))

    return jsonify(instructors_data)


@app.route('/api/rooms', methods=['GET'])
@app.route('/api/rooms/<string:room_id>', methods=['GET'])
def get_rooms_table(room_id=None):
    if scheduler is None:
        return jsonify({"error": "Scheduler not initialized"}), 500

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"]
    time_slots_info = [
        {"slot": 1, "time": "9:00-10:30"},
        {"slot": 2, "time": "10:45-12:15"},
        {"slot": 3, "time": "12:30-14:00"},
        {"slot": 4, "time": "14:15-15:45"}
    ]

    rooms_data = {
        "metadata": {"days": days, "time_slots": time_slots_info},
        "rooms": {}
    }

    for assignment in scheduler.assignments:
        room_name = assignment.room
        if room_id and room_name != room_id:
            continue

        if room_name not in rooms_data["rooms"]:
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

    if room_id and not rooms_data["rooms"]:
        return jsonify({"error": f"Room '{room_id}' not found"}), 404

    for room in rooms_data["rooms"].values():
        room["schedule"].sort(key=lambda x: (days.index(x["day"]), x["slot"]))

    return jsonify(rooms_data)


# ==========================================
# Data Management Endpoints (CRUD)
# ==========================================

@app.route('/api/manage/courses', methods=['GET', 'POST', 'DELETE'])
def manage_courses():
    """Manage courses (lectures and labs)"""
    if request.method == 'GET':
        return jsonify({
            "level_1": global_data["level_1"],
            "level_2": global_data["level_2"],
            "level_3": global_data["level_3"],
            "level_4": global_data["level_4"]
        })

    if request.method == 'POST':
        data = request.json
        # Expected format: 
        # { "level": 1, "has_lab": true, "data": { ... } }
        # or for L3/L4: 
        # { "level": 3, "department": "CSC", "has_lab": true, "data": { ... } }
        
        try:
            level = int(data.get("level"))
            has_lab = data.get("has_lab", False)
            course_data = data.get("data")
            
            # Prepare Lab Data if needed
            lab_data = None
            if has_lab:
                lab_data = {
                    "course_code": course_data.get("course_code"),
                    "course_name": course_data.get("course_name"),
                    "room_code": "", # Default empty room
                    "level": level
                }

            if level in [1, 2]:
                # Add Lecture
                global_data[f"level_{level}"]["lectures"].append(course_data)
                # Add Lab if requested
                if has_lab and lab_data:
                    global_data[f"level_{level}"]["labs"].append(lab_data)
                    
            elif level in [3, 4]:
                dept = data.get("department")
                if not dept:
                    return jsonify({"status": "error", "message": "Department is required for levels 3 and 4"}), 400
                
                # Add Lecture
                global_data[f"level_{level}"][dept]["lectures"].append(course_data)
                # Add Lab if requested
                if has_lab and lab_data:
                    global_data[f"level_{level}"][dept]["labs"].append(lab_data)
            
            save_course_data(file_paths["courses"], global_data["level_1"], global_data["level_2"], global_data["level_3"], global_data["level_4"])
            
            msg = "Course added successfully"
            if has_lab:
                msg += " (with Lab)"
            return jsonify({"status": "success", "message": msg})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    if request.method == 'DELETE':
        # Expected format: { "level": 1, "course_code": "CSC111" }
        data = request.json
        try:
            level = int(data.get("level"))
            course_code = data.get("course_code")
            
            deleted = False
            if level in [1, 2]:
                for type_key in ["lectures", "labs"]:
                    original_len = len(global_data[f"level_{level}"][type_key])
                    global_data[f"level_{level}"][type_key] = [
                        c for c in global_data[f"level_{level}"][type_key] 
                        if c["course_code"] != course_code
                    ]
                    if len(global_data[f"level_{level}"][type_key]) < original_len:
                        deleted = True
            elif level in [3, 4]:
                for dept in global_data[f"level_{level}"]:
                    for type_key in ["lectures", "labs"]:
                        original_len = len(global_data[f"level_{level}"][dept][type_key])
                        global_data[f"level_{level}"][dept][type_key] = [
                            c for c in global_data[f"level_{level}"][dept][type_key]
                            if c["course_code"] != course_code
                        ]
                        if len(global_data[f"level_{level}"][dept][type_key]) < original_len:
                            deleted = True
            
            if deleted:
                save_course_data(file_paths["courses"], global_data["level_1"], global_data["level_2"], global_data["level_3"], global_data["level_4"])
                return jsonify({"status": "success", "message": "Course deleted successfully"})
            else:
                return jsonify({"status": "error", "message": "Course not found"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/manage/rooms', methods=['GET', 'POST', 'DELETE'])
def manage_rooms():
    """Manage rooms"""
    if request.method == 'GET':
        return jsonify([
            {"room_code": r.room_code, "room_type": r.room_type, "capacity": r.capacity, "building": r.building}
            for r in global_data["rooms"]
        ])

    if request.method == 'POST':
        data = request.json
        try:
            new_room = Room(
                room_code=data["room_code"],
                room_type=data["room_type"],
                capacity=int(data.get("capacity", 0)),
                building=data.get("building", "")
            )
            # Check if exists
            if any(r.room_code == new_room.room_code for r in global_data["rooms"]):
                return jsonify({"status": "error", "message": "Room already exists"}), 400
            
            global_data["rooms"].append(new_room)
            save_rooms_to_csv(file_paths["rooms"], global_data["rooms"])
            return jsonify({"status": "success", "message": "Room added successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    if request.method == 'DELETE':
        data = request.json
        room_code = data.get("room_code")
        
        original_len = len(global_data["rooms"])
        global_data["rooms"] = [r for r in global_data["rooms"] if r.room_code != room_code]
        
        if len(global_data["rooms"]) < original_len:
            save_rooms_to_csv(file_paths["rooms"], global_data["rooms"])
            return jsonify({"status": "success", "message": "Room deleted successfully"})
        else:
            return jsonify({"status": "error", "message": "Room not found"}), 404


@app.route('/api/manage/lab-instructors', methods=['GET', 'POST', 'DELETE'])
def manage_lab_instructors():
    """Manage lab instructors (TAs)"""
    if request.method == 'GET':
        return jsonify([
            {
                "instructor_id": i.instructor_id,
                "instructor_name": i.instructor_name,
                "qualified_labs": i.qualified_labs,
                "max_hours_per_week": i.max_hours_per_week,
                "instructor_type": i.instructor_type
            }
            for i in global_data["lab_instructors"]
        ])

    if request.method == 'POST':
        data = request.json
        try:
            new_inst = LabInstructor(
                instructor_id=str(data["instructor_id"]),
                instructor_name=data["instructor_name"],
                qualified_labs=data.get("qualified_labs", []),
                max_hours_per_week=float(data.get("max_hours_per_week", 20)),
                instructor_type=data.get("instructor_type", "TA")
            )
            
            # Check if exists
            if any(i.instructor_id == new_inst.instructor_id for i in global_data["lab_instructors"]):
                return jsonify({"status": "error", "message": "Instructor ID already exists"}), 400
                
            global_data["lab_instructors"].append(new_inst)
            save_lab_instructors_to_csv(file_paths["lab_instructors"], global_data["lab_instructors"])
            return jsonify({"status": "success", "message": "Lab Instructor added successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    if request.method == 'DELETE':
        data = request.json
        instructor_id = str(data.get("instructor_id"))
        
        original_len = len(global_data["lab_instructors"])
        global_data["lab_instructors"] = [i for i in global_data["lab_instructors"] if i.instructor_id != instructor_id]
        
        if len(global_data["lab_instructors"]) < original_len:
            save_lab_instructors_to_csv(file_paths["lab_instructors"], global_data["lab_instructors"])
            return jsonify({"status": "success", "message": "Lab Instructor deleted successfully"})
        else:
            return jsonify({"status": "error", "message": "Instructor not found"}), 404


@app.route('/api/manage/professors', methods=['GET', 'POST', 'DELETE'])
def manage_professors():
    """Manage professors"""
    if request.method == 'GET':
        return jsonify(global_data["professors"])

    if request.method == 'POST':
        data = request.json
        try:
            new_prof = {
                "instructor_id": int(data["instructor_id"]),
                "instructor_name": data["instructor_name"]
            }
            
            # Check if exists
            if any(p["instructor_id"] == new_prof["instructor_id"] for p in global_data["professors"]):
                return jsonify({"status": "error", "message": "Professor ID already exists"}), 400
                
            global_data["professors"].append(new_prof)
            save_professors_to_csv(file_paths["professors"], global_data["professors"])
            return jsonify({"status": "success", "message": "Professor added successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    if request.method == 'DELETE':
        data = request.json
        instructor_id = int(data.get("instructor_id"))
        
        original_len = len(global_data["professors"])
        global_data["professors"] = [p for p in global_data["professors"] if p["instructor_id"] != instructor_id]
        
        if len(global_data["professors"]) < original_len:
            save_professors_to_csv(file_paths["professors"], global_data["professors"])
            return jsonify({"status": "success", "message": "Professor deleted successfully"})
        else:
            return jsonify({"status": "error", "message": "Professor not found"}), 404


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


@app.route('/api/list/professors', methods=['GET'])
def list_professors():
    """Get list of all professors (from loaded data)"""
    return jsonify({
        "professors": [p["instructor_name"] for p in global_data["professors"]]
    })


@app.route('/api/list/lab-instructors', methods=['GET'])
def list_lab_instructors():
    """Get list of all lab instructors"""
    return jsonify({
        "lab_instructors": [i.instructor_name for i in global_data["lab_instructors"]]
    })


@app.route('/api/list/rooms', methods=['GET'])
def list_rooms():
    """Get list of all rooms"""
    rooms = []
    for room in global_data["rooms"]:
        rooms.append({
            "room_code": room.room_code,
            "room_type": room.room_type
        })
    rooms.sort(key=lambda x: (x["room_type"], x["room_code"]))
    
    return jsonify({
        "rooms": rooms,
        "total_count": len(rooms),
        "lecture_rooms": len([r for r in rooms if r["room_type"] == "lec"]),
        "lab_rooms": len([r for r in rooms if r["room_type"] == "lab"])
    })


if __name__ == '__main__':
    # Initialize scheduler on startup
    try:
        initialize_scheduler()
        print("\n" + "=" * 60)
        print("API Server Starting...")
        print("=" * 60)
        print("\nAvailable Endpoints:")
        print("  - GET  /api/levels                    - Timetable by levels")
        print("  - GET  /api/professors                - Timetable by professors")
        print("  - GET  /api/lab-instructors           - Timetable by lab instructors")
        print("  - GET  /api/rooms                     - Timetable by rooms")
        print("  - CRUD /api/manage/courses            - Manage courses")
        print("  - CRUD /api/manage/rooms              - Manage rooms")
        print("  - CRUD /api/manage/lab-instructors    - Manage lab instructors")
        print("  - CRUD /api/manage/professors         - Manage professors")
        print("  - POST /api/regenerate                - Regenerate timetable")
        print("\nServer running on http://localhost:5000")
        print("=" * 60 + "\n")

        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"ERROR: Failed to initialize scheduler: {e}")
