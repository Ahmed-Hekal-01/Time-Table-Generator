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


def load_course_data():
    """Load course data for all levels (1-4)"""
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

    # Level 3 - Department-specific courses
    level_3_data = {
        "CSC": {
            "lectures": [
                {"course_code": "CSC317", "course_name": "Computer Graphics and Visualization", 
                 "instructor_name": "Dr. Hataba", "instructor_id": 12, "level": 3},
                {"course_code": "AID312", "course_name": "Intelligent Systems", 
                 "instructor_name": "Dr. Ahmed Bayumi", "instructor_id": 13, "level": 3},
                {"course_code": "CNC314", "course_name": "Database Systems", 
                 "instructor_name": "Dr. Mohamed Issa", "instructor_id": 14, "level": 3},
                {"course_code": "CNC311", "course_name": "Computer Networks", 
                 "instructor_name": "Prof. Samir Ahmed", "instructor_id": 15, "level": 3},
                {"course_code": "CSC314", "course_name": "Software Modeling and Analysis", 
                 "instructor_name": "Dr. Mustafa AlSayed", "instructor_id": 16, "level": 3}
            ],
            "labs": [
                {"course_code": "CSC317", "course_name": "Computer Graphics and Visualization", "room_code": "", "level": 3},
                {"course_code": "AID312", "course_name": "Intelligent Systems", "room_code": "", "level": 3},
                {"course_code": "CNC314", "course_name": "Database Systems", "room_code": "", "level": 3},
                {"course_code": "CNC311", "course_name": "Computer Networks", "room_code": "", "level": 3},
                {"course_code": "CSC314", "course_name": "Software Modeling and Analysis", "room_code": "", "level": 3}
            ]
        },
        "AID": {
            "lectures": [
                {"course_code": "CSC317", "course_name": "Computer Graphics and Visualization", 
                 "instructor_name": "Dr. Hataba", "instructor_id": 12, "level": 3},
                {"course_code": "AID312", "course_name": "Intelligent Systems", 
                 "instructor_name": "Dr. Ahmed Bayumi", "instructor_id": 13, "level": 3},
                {"course_code": "CNC314", "course_name": "Database Systems", 
                 "instructor_name": "Dr. Mohamed Issa", "instructor_id": 14, "level": 3},
                {"course_code": "CNC311", "course_name": "Computer Networks", 
                 "instructor_name": "Prof. Samir Ahmed", "instructor_id": 15, "level": 3},
                {"course_code": "AID311", "course_name": "Mathematics of Data Science", 
                 "instructor_name": "Dr. Ahmed Anter", "instructor_id": 17, "level": 3}
            ],
            "labs": [
                {"course_code": "CSC317", "course_name": "Computer Graphics and Visualization", "room_code": "", "level": 3},
                {"course_code": "AID312", "course_name": "Intelligent Systems", "room_code": "", "level": 3},
                {"course_code": "CNC314", "course_name": "Database Systems", "room_code": "", "level": 3},
                {"course_code": "CNC311", "course_name": "Computer Networks", "room_code": "", "level": 3},
                {"course_code": "AID311", "course_name": "Mathematics of Data Science", "room_code": "", "level": 3}
            ]
        },
        "BIF": {
            "lectures": [
                {"course_code": "CSC317", "course_name": "Computer Graphics and Visualization", 
                 "instructor_name": "Dr. Hataba", "instructor_id": 12, "level": 3},
                {"course_code": "AID312", "course_name": "Intelligent Systems", 
                 "instructor_name": "Dr. Ahmed Bayumi", "instructor_id": 13, "level": 3},
                {"course_code": "CNC314", "course_name": "Database Systems", 
                 "instructor_name": "Dr. Mohamed Issa", "instructor_id": 14, "level": 3},
                {"course_code": "CNC311", "course_name": "Computer Networks", 
                 "instructor_name": "Prof. Samir Ahmed", "instructor_id": 15, "level": 3},
                {"course_code": "BIF311", "course_name": "Human Biology", 
                 "instructor_name": "Prof. Eman Allam", "instructor_id": 18, "level": 3}
            ],
            "labs": [
                {"course_code": "CSC317", "course_name": "Computer Graphics and Visualization", "room_code": "", "level": 3},
                {"course_code": "AID312", "course_name": "Intelligent Systems", "room_code": "", "level": 3},
                {"course_code": "CNC314", "course_name": "Database Systems", "room_code": "", "level": 3},
                {"course_code": "CNC311", "course_name": "Computer Networks", "room_code": "", "level": 3},
                {"course_code": "BIF311", "course_name": "Human Biology", "room_code": "", "level": 3}
            ]
        },
        "CNC": {
            "lectures": [
                {"course_code": "CSC317", "course_name": "Computer Graphics and Visualization", 
                 "instructor_name": "Dr. Hataba", "instructor_id": 12, "level": 3},
                {"course_code": "AID312", "course_name": "Intelligent Systems", 
                 "instructor_name": "Dr. Ahmed Bayumi", "instructor_id": 13, "level": 3},
                {"course_code": "CNC314", "course_name": "Database Systems", 
                 "instructor_name": "Dr. Mohamed Issa", "instructor_id": 14, "level": 3},
                {"course_code": "CNC311", "course_name": "Computer Networks", 
                 "instructor_name": "Prof. Samir Ahmed", "instructor_id": 15, "level": 3},
                {"course_code": "CNC312", "course_name": "Foundations of Information Systems", 
                 "instructor_name": "Dr. Reda", "instructor_id": 19, "level": 3}
            ],
            "labs": [
                {"course_code": "CSC317", "course_name": "Computer Graphics and Visualization", "room_code": "", "level": 3},
                {"course_code": "AID312", "course_name": "Intelligent Systems", "room_code": "", "level": 3},
                {"course_code": "CNC314", "course_name": "Database Systems", "room_code": "", "level": 3},
                {"course_code": "CNC311", "course_name": "Computer Networks", "room_code": "", "level": 3},
                {"course_code": "CNC312", "course_name": "Foundations of Information Systems", "room_code": "", "level": 3}
            ]
        }
    }

    # Level 4 - Department-specific courses with Graduation Projects
    level_4_data = {
        "CSC": {
            "lectures": [
                {"course_code": "CSC410", "course_name": "Software Quality", 
                 "instructor_name": "Dr. Mohamed Khames", "instructor_id": 20, "level": 4},
                {"course_code": "CSC411", "course_name": "Software Verification and Validation", 
                 "instructor_name": "Dr. Mohamed Akhames", "instructor_id": 21, "level": 4},
                {"course_code": "CSC412", "course_name": "Software Security", 
                 "instructor_name": "Dr. Mustafa AlSayed", "instructor_id": 16, "level": 4},
                {"course_code": "CSC426", "course_name": "Distributed Systems", 
                 "instructor_name": "Dr. Mustafa AlSayed", "instructor_id": 16, "level": 4},
                {"course_code": "CSC413", "course_name": "Graduation Project I", 
                 "instructor_name": "Various", "instructor_id": 999, "level": 4, "is_graduation_project": True}
            ],
            "labs": [
                {"course_code": "CSC410", "course_name": "Software Quality", "room_code": "", "level": 4},
                {"course_code": "CSC411", "course_name": "Software Verification and Validation", "room_code": "", "level": 4},
                {"course_code": "CSC412", "course_name": "Software Security", "room_code": "", "level": 4},
                {"course_code": "CSC426", "course_name": "Distributed Systems", "room_code": "", "level": 4}
            ]
        },
        "AID": {
            "lectures": [
                {"course_code": "AID321", "course_name": "Machine Learning", 
                 "instructor_name": "Prof. Marghany Hassan", "instructor_id": 22, "level": 4},
                {"course_code": "AID411", "course_name": "Big Data Analytics & Visualization", 
                 "instructor_name": "Prof. Marghany Hassan", "instructor_id": 22, "level": 4},
                {"course_code": "AID413", "course_name": "Data Security", 
                 "instructor_name": "Dr. Ahmed Arafa", "instructor_id": 7, "level": 4},
                {"course_code": "AID417", "course_name": "Advanced Data Mining", 
                 "instructor_name": "Dr. Mohamed Issa", "instructor_id": 14, "level": 4},
                {"course_code": "AID427", "course_name": "New Trends in Data Science", 
                 "instructor_name": "Dr. Ahmed Arafa", "instructor_id": 7, "level": 4},
                {"course_code": "AID428", "course_name": "New Trends in AI", 
                 "instructor_name": "Dr. Ahmed Bayumi", "instructor_id": 13, "level": 4},
                {"course_code": "AID414", "course_name": "Graduation Project I", 
                 "instructor_name": "Various", "instructor_id": 999, "level": 4, "is_graduation_project": True}
            ],
            "labs": [
                {"course_code": "AID321", "course_name": "Machine Learning", "room_code": "", "level": 4},
                {"course_code": "AID411", "course_name": "Big Data Analytics & Visualization", "room_code": "", "level": 4},
                {"course_code": "AID413", "course_name": "Data Security", "room_code": "", "level": 4},
                {"course_code": "AID417", "course_name": "Advanced Data Mining", "room_code": "", "level": 4},
                {"course_code": "AID427", "course_name": "New Trends in Data Science", "room_code": "", "level": 4},
                {"course_code": "AID428", "course_name": "New Trends in AI", "room_code": "", "level": 4}
            ]
        },
        "BIF": {
            "lectures": [
                {"course_code": "BIF411", "course_name": "Structural Bioinformatics", 
                 "instructor_name": "Dr. Sameh Shreif", "instructor_id": 23, "level": 4},
                {"course_code": "BIF412", "course_name": "Management and Design of Health Care Systems", 
                 "instructor_name": "Dr. Sameh Shreif", "instructor_id": 23, "level": 4},
                {"course_code": "BIF413", "course_name": "Algorithms in Bioinformatics", 
                 "instructor_name": "Prof. Marghany", "instructor_id": 24, "level": 4},
                {"course_code": "BIF424", "course_name": "IT Infrastructure", 
                 "instructor_name": "Dr. Mohamed Akhames", "instructor_id": 21, "level": 4},
                {"course_code": "BIF425", "course_name": "New Trends in Bioinformatics", 
                 "instructor_name": "Dr. Mohamed Issa", "instructor_id": 14, "level": 4},
                {"course_code": "BIF410", "course_name": "Graduation Project I", 
                 "instructor_name": "Various", "instructor_id": 999, "level": 4, "is_graduation_project": True}
            ],
            "labs": [
                {"course_code": "BIF411", "course_name": "Structural Bioinformatics", "room_code": "", "level": 4},
                {"course_code": "BIF412", "course_name": "Management and Design of Health Care Systems", "room_code": "", "level": 4},
                {"course_code": "BIF413", "course_name": "Algorithms in Bioinformatics", "room_code": "", "level": 4},
                {"course_code": "BIF424", "course_name": "IT Infrastructure", "room_code": "", "level": 4},
                {"course_code": "BIF425", "course_name": "New Trends in Bioinformatics", "room_code": "", "level": 4}
            ]
        },
        "CNC": {
            "lectures": [
                {"course_code": "CNC411", "course_name": "Fundamentals of Cybersecurity", 
                 "instructor_name": "Dr. Ahmed Arafa", "instructor_id": 7, "level": 4},
                {"course_code": "CNC413", "course_name": "Digital Forensics", 
                 "instructor_name": "Prof. Samir Ahmed", "instructor_id": 15, "level": 4},
                {"course_code": "CNC415", "course_name": "Network Design and Management", 
                 "instructor_name": "Dr. Mustafa AlSayed", "instructor_id": 16, "level": 4},
                {"course_code": "CNC418", "course_name": "Software Security", 
                 "instructor_name": "Dr. Hataba", "instructor_id": 12, "level": 4},
                {"course_code": "CNC419", "course_name": "IT Security and Risk Management", 
                 "instructor_name": "Dr. Hataba", "instructor_id": 12, "level": 4},
                {"course_code": "CNC414", "course_name": "Graduation Project I", 
                 "instructor_name": "Various", "instructor_id": 999, "level": 4, "is_graduation_project": True}
            ],
            "labs": [
                {"course_code": "CNC411", "course_name": "Fundamentals of Cybersecurity", "room_code": "", "level": 4},
                {"course_code": "CNC413", "course_name": "Digital Forensics", "room_code": "", "level": 4},
                {"course_code": "CNC415", "course_name": "Network Design and Management", "room_code": "", "level": 4},
                {"course_code": "CNC418", "course_name": "Software Security", "room_code": "", "level": 4},
                {"course_code": "CNC419", "course_name": "IT Security and Risk Management", "room_code": "", "level": 4}
            ]
        }
    }

    return level_1_data, level_2_data, level_3_data, level_4_data




