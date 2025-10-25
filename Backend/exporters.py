"""
Export functions for timetable data (CSV and JSON formats)
"""

import csv
import json
import os
from datetime import datetime
from scheduler import TimetableScheduler


def export_to_csv(scheduler: TimetableScheduler, filename: str = "timetable.csv"):
    """Export complete timetable to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Assignment ID', 'Type', 'Course Code', 'Course Name', 'Day',
                         'Slot', 'Time', 'Room', 'Instructor', 'Lab Instructor', 'Assigned To'])

        for assignment in sorted(scheduler.assignments,
                                 key=lambda x: (x.time_slot.day, x.time_slot.slot_number)):
            instructor_display = assignment.instructor or "N/A"
            if assignment.type == "lab" and assignment.lab_instructor_name:
                instructor_display = f"{assignment.lab_instructor_name} (Lab)"

            writer.writerow([
                assignment.assignment_id,
                assignment.type,
                assignment.course_code,
                assignment.course_name,
                assignment.time_slot.day,
                assignment.time_slot.slot_number,
                f"{assignment.time_slot.start_time}-{assignment.time_slot.end_time}",
                assignment.room,
                instructor_display,
                assignment.lab_instructor_name or "N/A",
                ", ".join(assignment.assigned_to)
            ])
    print(f"Complete timetable exported to {filename}")


def export_section_timetables(scheduler: TimetableScheduler, output_dir: str = "."):
    """Export individual section timetables to CSV files"""
    for section in scheduler.sections:
        assignments = [a for a in scheduler.assignments if section.section_id in a.assigned_to]
        assignments_sorted = sorted(assignments, key=lambda x: (x.time_slot.day, x.time_slot.slot_number))

        filename = os.path.join(output_dir, f"timetable_{section.section_id}.csv")
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([f"Timetable for {section.section_id}"])
            writer.writerow(
                ['Day', 'Slot', 'Time', 'Type', 'Course Code', 'Course Name', 'Room', 'Instructor', 'Lab Instructor'])

            for assignment in assignments_sorted:
                instructor_display = assignment.instructor or "N/A"
                if assignment.type == "lab" and assignment.lab_instructor_name:
                    instructor_display = f"{assignment.lab_instructor_name} (Lab)"

                writer.writerow([
                    assignment.time_slot.day,
                    assignment.time_slot.slot_number,
                    f"{assignment.time_slot.start_time}-{assignment.time_slot.end_time}",
                    assignment.type.capitalize(),
                    assignment.course_code,
                    assignment.course_name,
                    assignment.room,
                    instructor_display,
                    assignment.lab_instructor_name or "N/A"
                ])

    print(f"Section timetables exported to {output_dir}/")


def export_json_timetable(scheduler: TimetableScheduler, filename: str = "timetable.json"):
    """Export timetable as JSON with comprehensive data structure"""
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

    # Prepare the main timetable data structure
    timetable_data = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": "CSIT College Timetable",
            "total_assignments": len(scheduler.assignments),
            "total_lecture_assignments": len([a for a in scheduler.assignments if a.type == "lecture"]),
            "total_lab_assignments": len([a for a in scheduler.assignments if a.type == "lab"])
        },
        "time_slots": [],
        "assignments": [],
        "sections": {},
        "groups": {},
        "instructors": {
            "lecture_instructors": {},
            "lab_instructors": {}
        },
        "rooms": {},
        "statistics": {}
    }

    # Add time slot definitions
    for ts in scheduler.time_slots:
        timetable_data["time_slots"].append({
            "id": ts.id,
            "day": ts.day,
            "slot_number": ts.slot_number,
            "start_time": ts.start_time,
            "end_time": ts.end_time
        })

    # Add all assignments
    for assignment in scheduler.assignments:
        assignment_data = {
            "assignment_id": assignment.assignment_id,
            "type": assignment.type,
            "course_code": assignment.course_code,
            "course_name": assignment.course_name,
            "day": assignment.time_slot.day,
            "slot_number": assignment.time_slot.slot_number,
            "start_time": assignment.time_slot.start_time,
            "end_time": assignment.time_slot.end_time,
            "room": assignment.room,
            "assigned_to": assignment.assigned_to
        }

        # Add instructor information
        if assignment.type == "lecture" and assignment.instructor:
            assignment_data["instructor"] = assignment.instructor
            assignment_data["instructor_id"] = assignment.instructor_id
        elif assignment.type == "lab" and assignment.lab_instructor_name:
            assignment_data["lab_instructor"] = assignment.lab_instructor_name
            assignment_data["lab_instructor_id"] = assignment.lab_instructor_id

        timetable_data["assignments"].append(assignment_data)

    # Generate section timetables
    for section in scheduler.sections:
        section_assignments = [a for a in scheduler.assignments if section.section_id in a.assigned_to]

        section_schedule = {}
        for day in days:
            section_schedule[day] = {}
            for slot in [1, 2, 3, 4]:
                assignment = next((a for a in section_assignments
                                 if a.time_slot.day == day and a.time_slot.slot_number == slot), None)
                if assignment:
                    slot_data = {
                        "course_code": assignment.course_code,
                        "course_name": assignment.course_name,
                        "type": assignment.type,
                        "room": assignment.room,
                        "start_time": assignment.time_slot.start_time,
                        "end_time": assignment.time_slot.end_time
                    }

                    if assignment.type == "lecture" and assignment.instructor:
                        slot_data["instructor"] = assignment.instructor
                    elif assignment.type == "lab" and assignment.lab_instructor_name:
                        slot_data["lab_instructor"] = assignment.lab_instructor_name

                    section_schedule[day][f"slot_{slot}"] = slot_data
                else:
                    section_schedule[day][f"slot_{slot}"] = None

        timetable_data["sections"][section.section_id] = {
            "section_info": {
                "section_id": section.section_id,
                "level": section.level,
                "group_number": section.group_number,
                "section_number": section.section_number,
                "group_id": section.group_id
            },
            "schedule": section_schedule
        }

    # Generate group timetables (lectures only)
    for group in scheduler.groups:
        lecture_assignments = [a for a in scheduler.assignments
                              if a.type == "lecture" and group.group_id in a.assigned_to]

        group_schedule = {}
        for day in days:
            group_schedule[day] = {}
            for slot in [1, 2, 3, 4]:
                assignment = next((a for a in lecture_assignments
                                 if a.time_slot.day == day and a.time_slot.slot_number == slot), None)
                if assignment:
                    group_schedule[day][f"slot_{slot}"] = {
                        "course_code": assignment.course_code,
                        "course_name": assignment.course_name,
                        "instructor": assignment.instructor,
                        "room": assignment.room,
                        "start_time": assignment.time_slot.start_time,
                        "end_time": assignment.time_slot.end_time
                    }
                else:
                    group_schedule[day][f"slot_{slot}"] = None

        timetable_data["groups"][group.group_id] = {
            "group_info": {
                "group_id": group.group_id,
                "level": group.level,
                "group_number": group.group_number,
                "sections": [s.section_id for s in group.sections]
            },
            "schedule": group_schedule
        }

    # Generate instructor schedules
    # Lecture instructors
    lecture_instructors = {}
    for assignment in scheduler.assignments:
        if assignment.type == "lecture" and assignment.instructor:
            if assignment.instructor not in lecture_instructors:
                lecture_instructors[assignment.instructor] = []
            lecture_instructors[assignment.instructor].append({
                "course_code": assignment.course_code,
                "course_name": assignment.course_name,
                "day": assignment.time_slot.day,
                "slot_number": assignment.time_slot.slot_number,
                "start_time": assignment.time_slot.start_time,
                "end_time": assignment.time_slot.end_time,
                "room": assignment.room,
                "groups": [g for g in assignment.assigned_to if g.startswith("L")]
            })

    timetable_data["instructors"]["lecture_instructors"] = lecture_instructors

    # Lab instructors
    lab_instructors = {}
    for assignment in scheduler.assignments:
        if assignment.type == "lab" and assignment.lab_instructor_name:
            if assignment.lab_instructor_name not in lab_instructors:
                lab_instructors[assignment.lab_instructor_name] = []
            lab_instructors[assignment.lab_instructor_name].append({
                "course_code": assignment.course_code,
                "course_name": assignment.course_name,
                "day": assignment.time_slot.day,
                "slot_number": assignment.time_slot.slot_number,
                "start_time": assignment.time_slot.start_time,
                "end_time": assignment.time_slot.end_time,
                "room": assignment.room,
                "section": assignment.assigned_to[0]
            })

    timetable_data["instructors"]["lab_instructors"] = lab_instructors

    # Generate room schedules
    room_schedules = {}
    for assignment in scheduler.assignments:
        if assignment.room not in room_schedules:
            room_schedules[assignment.room] = []

        room_data = {
            "course_code": assignment.course_code,
            "course_name": assignment.course_name,
            "type": assignment.type,
            "day": assignment.time_slot.day,
            "slot_number": assignment.time_slot.slot_number,
            "start_time": assignment.time_slot.start_time,
            "end_time": assignment.time_slot.end_time,
            "assigned_to": assignment.assigned_to
        }

        if assignment.type == "lecture" and assignment.instructor:
            room_data["instructor"] = assignment.instructor
        elif assignment.type == "lab" and assignment.lab_instructor_name:
            room_data["lab_instructor"] = assignment.lab_instructor_name

        room_schedules[assignment.room].append(room_data)

    timetable_data["rooms"] = room_schedules

    # Generate statistics
    lab_instructor_stats = {}
    for instructor_name, assignments in lab_instructors.items():
        courses = set(a["course_code"] for a in assignments)
        lab_instructor_stats[instructor_name] = {
            "total_sessions": len(assignments),
            "total_hours": len(assignments) * 1.5,
            "courses": list(courses)
        }

    lecture_instructor_stats = {}
    for instructor_name, assignments in lecture_instructors.items():
        courses = set(a["course_code"] for a in assignments)
        lecture_instructor_stats[instructor_name] = {
            "total_sessions": len(assignments),
            "total_hours": len(assignments) * 1.5,
            "courses": list(courses)
        }

    timetable_data["statistics"] = {
        "lab_instructor_workload": lab_instructor_stats,
        "lecture_instructor_workload": lecture_instructor_stats,
        "room_utilization": {room: len(assignments) for room, assignments in room_schedules.items()},
        "courses_by_level": {
            "level_1": {
                "lectures": len([a for a in scheduler.assignments if a.type == "lecture" and any("L1" in x for x in a.assigned_to)]),
                "labs": len([a for a in scheduler.assignments if a.type == "lab" and any("L1" in x for x in a.assigned_to)])
            },
            "level_2": {
                "lectures": len([a for a in scheduler.assignments if a.type == "lecture" and any("L2" in x for x in a.assigned_to)]),
                "labs": len([a for a in scheduler.assignments if a.type == "lab" and any("L2" in x for x in a.assigned_to)])
            }
        }
    }

    # Write to JSON file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(timetable_data, file, indent=2, ensure_ascii=False)

    print(f"JSON timetable exported to {filename}")
