"""
Data loading and initialization functions
"""

import csv
from typing import List, Tuple
from .models import TimeSlot, Group, Section, Room, LabInstructor


def generate_time_slots() -> List[TimeSlot]:
    """Generate all 20 time slots (5 days × 4 slots) - Sunday to Thursday only"""
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
    """Generate all groups and sections for levels 1-4"""
    groups = []
    sections = []

    # Level 1 & 2: Traditional group structure (3 groups, 3 sections each)
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
                    group_id=group_id,
                    department=None
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

    # Level 3 & 4: Department structure (CSC, CNC, BIF, AID)
    departments = {
        "CSC": 1,  # 1 section
        "CNC": 3,  # 3 sections
        "BIF": 1,  # 1 section
        "AID": 3   # 3 sections
    }

    for level in [3, 4]:
        for dept_code, num_sections in departments.items():
            # Create a "group" for the department (to keep consistent with L1/L2 structure)
            group_id = f"L{level}-{dept_code}"
            group_sections = []

            for section_num in range(1, num_sections + 1):
                section = Section(
                    section_id=f"L{level}-{dept_code}-S{section_num}",
                    level=level,
                    group_number=0,  # No group number for departments
                    section_number=section_num,
                    group_id=group_id,
                    department=dept_code
                )
                sections.append(section)
                group_sections.append(section)

            # Create a group object for the department
            group = Group(
                group_id=group_id,
                level=level,
                group_number=0,  # Departments don't have group numbers
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


import json
import os

def load_professors_from_csv(filename: str) -> List[dict]:
    """Load professors from CSV file"""
    professors = []
    if not os.path.exists(filename):
        return []
        
    with open(filename, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            professors.append({
                "instructor_id": int(row['instructor_id']),
                "instructor_name": row['instructor_name'],
                "qualified_courses": row.get("qualified_courses", "").split("|") if row.get("qualified_courses") else []
            })
    return professors

def save_professors_to_csv(filename: str, professors: List[dict]):
    """Save professors to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
        fieldnames = ["instructor_id", "instructor_name", "qualified_courses"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for prof in professors:
            writer.writerow({
                "instructor_id": prof["instructor_id"],
                "instructor_name": prof["instructor_name"],
                "qualified_courses": "|".join(prof.get("qualified_courses", []))
            })

def load_course_data(filename: str = None):
    """Load course data from JSON file"""
    if not filename or not os.path.exists(filename):
        print(f"Warning: Course data file not found: {filename}")
        return {}, {}, {}, {}
        
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    return data.get("level_1", {}), data.get("level_2", {}), data.get("level_3", {}), data.get("level_4", {})

def save_course_data(filename: str, level_1: dict, level_2: dict, level_3: dict, level_4: dict):
    """Save course data to JSON file"""
    data = {
        "level_1": level_1,
        "level_2": level_2,
        "level_3": level_3,
        "level_4": level_4
    }
    
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def save_rooms_to_csv(filename: str, rooms: List[Room]):
    """Save rooms to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["room_code", "room_type", "capacity", "building"])
        writer.writeheader()
        for room in rooms:
            writer.writerow({
                "room_code": room.room_code,
                "room_type": room.room_type,
                "capacity": room.capacity,
                "building": room.building
            })

def save_lab_instructors_to_csv(filename: str, instructors: List[LabInstructor]):
    """Save lab instructors to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["instructor_id", "instructor_name", "qualified_labs", "max_hours_per_week", "instructor_type"])
        writer.writeheader()
        for inst in instructors:
            writer.writerow({
                "instructor_id": inst.instructor_id,
                "instructor_name": inst.instructor_name,
                "qualified_labs": "|".join(inst.qualified_labs),
                "max_hours_per_week": inst.max_hours_per_week,
                "instructor_type": inst.instructor_type
            })




