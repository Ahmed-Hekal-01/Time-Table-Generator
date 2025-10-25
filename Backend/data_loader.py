"""
Data loading and initialization functions
"""

import csv
from typing import List, Tuple
from models import TimeSlot, Group, Section, Room, LabInstructor


def generate_time_slots() -> List[TimeSlot]:
    """Generate all 20 time slots (5 days × 4 slots)"""
    TIME_SLOTS_CONFIG = [
        {"slot_number": 1, "start_time": "9:00", "end_time": "10:30"},
        {"slot_number": 2, "start_time": "10:45", "end_time": "12:15"},
        {"slot_number": 3, "start_time": "12:30", "end_time": "14:00"},
        {"slot_number": 4, "start_time": "14:15", "end_time": "15:45"}
    ]
    DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

    time_slots = []
    for day in DAYS:
        for slot_config in TIME_SLOTS_CONFIG:
            slot = TimeSlot(
                id=f"{day[:3].upper()}-{slot_config['slot_number']}",
                day=day,
                slot_number=slot_config['slot_number'],
                start_time=slot_config['start_time'],
                end_time=slot_config['end_time']
            )
            time_slots.append(slot)
    return time_slots


def generate_groups_and_sections() -> Tuple[List[Group], List[Section]]:
    """Generate all groups and sections for both levels"""
    groups = []
    sections = []

    for level in [1, 2]:
        for group_num in [1, 2, 3]:
            group_id = f"L{level}-G{group_num}"
            group_sections = []

            for section_num in [1, 2, 3]:
                section = Section(
                    section_id=f"L{level}-G{group_num}-S{section_num}",
                    level=level,
                    group_number=group_num,
                    section_number=section_num,
                    group_id=group_id
                )
                sections.append(section)
                group_sections.append(section)

            group = Group(
                group_id=group_id,
                level=level,
                group_number=group_num,
                sections=group_sections
            )
            groups.append(group)

    return groups, sections


def load_rooms_from_csv(filename: str) -> List[Room]:
    """Load rooms from CSV file"""
    rooms = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            room = Room(
                room_code=row['room_code'],
                room_type=row['room_type'],
                capacity=int(row['capacity']) if row.get('capacity') and row['capacity'] else None,
                building=row.get('building', None)
            )
            rooms.append(room)
    return rooms


def load_lab_instructors_from_csv(filename: str) -> List[LabInstructor]:
    """Load lab instructors from CSV file"""
    instructors = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse qualified labs (pipe-separated)
            qualified_labs = []
            if row.get('qualified_labs'):
                qualified_labs = [lab.strip() for lab in row['qualified_labs'].split('|') if lab.strip()]

            instructor = LabInstructor(
                instructor_id=row['instructor_id'].strip(),
                instructor_name=row['instructor_name'],
                qualified_labs=qualified_labs,
                max_hours_per_week=float(row['max_hours_per_week']),
                instructor_type=row['instructor_type']
            )
            instructors.append(instructor)
    print(f"Loaded {len(instructors)} lab instructors from {filename}")

    # Print loaded instructors for verification
    for inst in instructors[:5]:  # Show first 5
        print(f"  - {inst.instructor_name} (ID: {inst.instructor_id}): {inst.qualified_labs}")
    if len(instructors) > 5:
        print(f"  - ... and {len(instructors) - 5} more")

    return instructors


def load_course_data():
    level_1_data = {
        "lectures": [
            {"course_code": "MTH111", "course_name": "Math 1", "instructor_name": "Prof. Ayman Arafa",
             "instructor_id": 1, "level": 1},
            {"course_code": "LRA104", "course_name": "Music", "instructor_name": "Music Prof", "instructor_id": 2,
             "level": 1},
            {"course_code": "ECE111", "course_name": "Digital Logic Design", "instructor_name": "Prof. Ahmed Allam",
             "instructor_id": 3, "level": 1},
            {"course_code": "CSC111", "course_name": "Fundamentals of Programming",
             "instructor_name": "Prof. Reda Elbasyoine", "instructor_id": 4, "level": 1},
            {"course_code": "PHY113", "course_name": "Physics 1", "instructor_name": "Prof. Adel Fathy",
             "instructor_id": 5, "level": 1},
            {"course_code": "LRA101", "course_name": "JA Culture", "instructor_name": "Prof. Sherien",
             "instructor_id": 6, "level": 1}
        ],
        "labs": [
            {"course_code": "PHY113", "course_name": "Physics 1", "room_code": "CEO.PHYLAB", "level": 1},
            {"course_code": "ECE111", "course_name": "Digital Logic Design", "room_code": "B7.f1.04", "level": 1},
            {"course_code": "LRA401", "course_name": "JA Language 1", "room_code": "", "level": 1},
            {"course_code": "CSC111", "course_name": "Fundamentals of Programming", "room_code": "", "level": 1},
            {"course_code": "MTH111", "course_name": "Math 1", "room_code": "", "level": 1}
        ]
    }

    level_2_data = {
        "lectures": [
            {"course_code": "ACM215", "course_name": "ODE", "instructor_name": "Prof. Ayman Arafa", "instructor_id": 1,
             "level": 2},
            {"course_code": "CSC211", "course_name": "Software Engineering", "instructor_name": "Prof. Ahmed Arafa",
             "instructor_id": 7, "level": 2},
            {"course_code": "CNC111", "course_name": "Network and Web Programming",
             "instructor_name": "Prof. Ahmed Antar", "instructor_id": 8, "level": 2},
            {"course_code": "MTH212", "course_name": "Probability and Statistics",
             "instructor_name": "Prof. Ahmed Zakaria", "instructor_id": 9, "level": 2},
            {"course_code": "CSE214", "course_name": "Computer Organization",
             "instructor_name": "Prof. Mostafa Soliman", "instructor_id": 10, "level": 2},
            {"course_code": "LRA306", "course_name": "Natural Resources and Sustainability",
             "instructor_name": "Prof. LRA", "instructor_id": 11, "level": 2}
        ],
        "labs": [
            {"course_code": "ACM215", "course_name": "ODE", "room_code": "", "level": 2},
            {"course_code": "CSC211", "course_name": "Software Engineering", "room_code": "", "level": 2},
            {"course_code": "CNC111", "course_name": "Network and Web Programming", "room_code": "", "level": 2},
            {"course_code": "MTH212", "course_name": "Probability and Statistics", "room_code": "", "level": 2},
            {"course_code": "CSE214", "course_name": "Computer Organization", "room_code": "", "level": 2},
            {"course_code": "LRA403", "course_name": "JA Language 3", "room_code": "", "level": 2}
        ]
    }

    return level_1_data, level_2_data


