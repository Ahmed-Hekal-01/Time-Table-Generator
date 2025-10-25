"""
College Timetable Scheduling System with Lab Instructor Assignment
Generates timetables for 2 levels, 3 groups per level, 3 sections per group
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple
from collections import defaultdict
import csv
import random
from datetime import datetime


# ==================== DATA MODELS ====================

@dataclass
class TimeSlot:
    id: str
    day: str
    slot_number: int
    start_time: str
    end_time: str

    def __hash__(self):
        return hash(self.id)


@dataclass
class Lecture:
    course_code: str
    course_name: str
    instructor_name: str
    instructor_id: int
    level: int


@dataclass
class Lab:
    course_code: str
    course_name: str
    room_code: str
    level: int


@dataclass
class Room:
    room_code: str
    room_type: str
    capacity: Optional[int] = None
    building: Optional[str] = None


@dataclass
class Section:
    section_id: str
    level: int
    group_number: int
    section_number: int
    group_id: str


@dataclass
class Group:
    group_id: str
    level: int
    group_number: int
    sections: List[Section] = field(default_factory=list)


@dataclass
class LabInstructor:
    instructor_id: str
    instructor_name: str
    qualified_labs: List[str]  # ["CSC111", "ECE111", "MTH111"]
    max_hours_per_week: float  # e.g., 12.0 hours
    instructor_type: str = "TA"  # TA, Lab Assistant, etc.
    current_hours: float = 0.0  # Track assigned hours (runtime)


@dataclass
class Assignment:
    assignment_id: str
    type: str  # "lecture" or "lab"
    course_code: str
    course_name: str
    time_slot: TimeSlot
    room: str
    instructor: Optional[str] = None
    instructor_id: Optional[int] = None
    lab_instructor_id: Optional[int] = None
    lab_instructor_name: Optional[str] = None
    assigned_to: List[str] = field(default_factory=list)


# ==================== SCHEDULE TRACKER ====================

class ScheduleTracker:
    """Track all scheduling constraints and assignments"""

    def __init__(self):
        self.instructor_schedule: Dict[int, Dict[str, Dict[int, Optional[str]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: None))
        )
        self.room_schedule: Dict[str, Dict[str, Dict[int, Optional[str]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: None))
        )
        self.group_schedule: Dict[str, Dict[str, Dict[int, Optional[str]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: None))
        )
        self.section_schedule: Dict[str, Dict[str, Dict[int, Optional[str]]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: None))
        )
        self.group_lectures_assigned: Dict[str, Set[str]] = defaultdict(set)
        self.section_labs_assigned: Dict[str, Set[str]] = defaultdict(set)

    def is_instructor_available(self, instructor_id: int, day: str, slot_number: int) -> bool:
        return self.instructor_schedule[instructor_id][day][slot_number] is None

    def is_room_available(self, room_code: str, day: str, slot_number: int) -> bool:
        return self.room_schedule[room_code][day][slot_number] is None

    def is_group_available(self, group_id: str, day: str, slot_number: int) -> bool:
        return self.group_schedule[group_id][day][slot_number] is None

    def is_section_available(self, section_id: str, day: str, slot_number: int) -> bool:
        return self.section_schedule[section_id][day][slot_number] is None

    def has_group_taken_lecture(self, group_id: str, course_code: str) -> bool:
        return course_code in self.group_lectures_assigned[group_id]

    def has_section_taken_lab(self, section_id: str, course_code: str) -> bool:
        return course_code in self.section_labs_assigned[section_id]

    def assign_lecture(self, assignment_id: str, instructor_id: int, room_code: str,
                       group_id: str, section_ids: List[str], course_code: str,
                       day: str, slot_number: int):
        self.instructor_schedule[instructor_id][day][slot_number] = assignment_id
        self.room_schedule[room_code][day][slot_number] = assignment_id
        self.group_schedule[group_id][day][slot_number] = assignment_id

        for section_id in section_ids:
            self.section_schedule[section_id][day][slot_number] = assignment_id

        self.group_lectures_assigned[group_id].add(course_code)

    def assign_lab(self, assignment_id: str, room_code: str, section_id: str,
                   course_code: str, day: str, slot_number: int):
        self.room_schedule[room_code][day][slot_number] = assignment_id
        self.section_schedule[section_id][day][slot_number] = assignment_id
        self.section_labs_assigned[section_id].add(course_code)


# ==================== INSTRUCTOR TRACKER ====================

class InstructorTracker:
    """Track lab instructor schedules and workload"""

    def __init__(self):
        # Schedule: instructor_id -> day -> slot_number -> assignment_id
        self.instructor_schedule: Dict[str, Dict[str, Dict[int, str]]] = defaultdict(  # Changed to str
            lambda: defaultdict(lambda: defaultdict(lambda: None))
        )

        # Workload: instructor_id -> hours assigned
        self.instructor_hours: Dict[str, float] = defaultdict(float)  # Changed to str

        # Instructor pool: instructor_id -> LabInstructor object
        self.instructors: Dict[str, LabInstructor] = {}  # Changed to str

    def is_available(self, instructor_id: str, day: str, slot_number: int) -> bool:  # Changed to str
        """Check if instructor is free at given time"""
        return self.instructor_schedule[instructor_id][day][slot_number] is None

    def has_capacity(self, instructor_id: str, hours_needed: float) -> bool:  # Changed to str
        """Check if instructor has capacity for more hours"""
        instructor = self.instructors.get(instructor_id)
        if not instructor or not instructor.max_hours_per_week:
            return True  # No limit set

        current = self.instructor_hours[instructor_id]
        return (current + hours_needed) <= instructor.max_hours_per_week

    def is_qualified(self, instructor_id: str, course_code: str) -> bool:  # Changed to str
        """Check if instructor is qualified to teach this course"""
        instructor = self.instructors.get(instructor_id)
        if not instructor:
            return False
        return course_code in instructor.qualified_labs

    def assign(self, instructor_id: str, day: str, slot_number: int,  # Changed to str
               assignment_id: str, hours: float):
        """Assign instructor to a time slot"""
        self.instructor_schedule[instructor_id][day][slot_number] = assignment_id
        self.instructor_hours[instructor_id] += hours

    def unassign(self, instructor_id: str, day: str, slot_number: int, hours: float):  # Changed to str
        """Remove instructor assignment (for backtracking)"""
        self.instructor_schedule[instructor_id][day][slot_number] = None
        self.instructor_hours[instructor_id] -= hours


# ==================== DATA INITIALIZATION ====================

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
    try:
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
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Using default rooms.")
        rooms = get_default_rooms()
    return rooms


def get_default_rooms() -> List[Room]:
    """Provide default rooms if CSV is not available"""
    return [
        Room("CEO.PHYLAB", "lab", 25, "CEO"),
        Room("B7.f1.04", "lab", 30, "B7"),
        Room("LAB.COMP.01", "lab", 30, "B7"),
        Room("LAB.COMP.02", "lab", 30, "B7"),
        Room("LAB.COMP.03", "lab", 30, "B7"),
        Room("LAB.COMP.04", "lab", 30, "B8"),
        Room("LAB.COMP.05", "lab", 30, "B8"),
        Room("LAB.COMP.06", "lab", 30, "B8"),
        Room("LEC.HALL.01", "lec", 100, "Main"),
        Room("LEC.HALL.02", "lec", 100, "Main"),
        Room("LEC.HALL.03", "lec", 80, "B7"),
        Room("LEC.HALL.04", "lec", 80, "B7"),
        Room("LEC.HALL.05", "lec", 90, "B8"),
    ]


def load_lab_instructors_from_csv(filename: str) -> List[LabInstructor]:
    """Load lab instructors from CSV file"""
    instructors = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Parse qualified labs (pipe-separated)
                qualified_labs = []
                if row.get('qualified_labs'):
                    qualified_labs = [lab.strip() for lab in row['qualified_labs'].split('|') if lab.strip()]

                instructor = LabInstructor(
                    instructor_id=row['instructor_id'].strip(),  # Keep as string
                    instructor_name=row['instructor_name'],
                    qualified_labs=qualified_labs,
                    max_hours_per_week=float(row['max_hours_per_week']) if row.get('max_hours_per_week') else 20.0,
                    instructor_type=row.get('instructor_type', 'TA')
                )
                instructors.append(instructor)
        print(f"Loaded {len(instructors)} lab instructors from {filename}")

        # Print loaded instructors for verification
        for inst in instructors[:5]:  # Show first 5
            print(f"  - {inst.instructor_name} (ID: {inst.instructor_id}): {inst.qualified_labs}")
        if len(instructors) > 5:
            print(f"  - ... and {len(instructors) - 5} more")

    except FileNotFoundError:
        print(f"Warning: {filename} not found. Using default lab instructors.")
        instructors = get_default_lab_instructors()
    except Exception as e:
        print(f"Error loading lab instructors from {filename}: {e}")
        print("Using default lab instructors instead.")
        instructors = get_default_lab_instructors()

    return instructors


def get_default_lab_instructors() -> List[LabInstructor]:
    """Provide default lab instructors if CSV is not available"""
    return [
        # Programming & CS courses
        LabInstructor("101", "Eng. Omnya", ["CSC111", "ECE111", "MTH111"], 12.0, "TA"),
        LabInstructor("102", "Eng. Nouran Moussa", ["CSC111", "CSC211"], 10.0, "TA"),
        LabInstructor("103", "Eng. Zeina Ahmed", ["CSC111", "AID321", "AID428"], 15.0, "TA"),
        LabInstructor("105", "Eng. Mariem Nagy", ["CSC111", "CSC211", "AID413"], 12.0, "TA"),
        LabInstructor("106", "Eng. Nour Akram", ["CSC111"], 10.0, "TA"),
        LabInstructor("108", "Eng. Nada Essam", ["CSC111", "AID411"], 10.0, "TA"),
        LabInstructor("109", "Eng. Nada Ahmed", ["CSC211", "CSE214", "CSC317"], 14.0, "TA"),
        LabInstructor("110", "Eng. Menna Magdy", ["CSC211", "CSC317"], 12.0, "TA"),

        # Hardware & Electronics
        LabInstructor("104", "Eng. ECE", ["ECE111", "PHY113"], 8.0, "Lab Assistant"),
        LabInstructor("111", "Eng. Heba Abdelkader", ["CSE214"], 10.0, "TA"),
        LabInstructor("112", "Eng. Omnya Ramadan", ["CSE214"], 10.0, "TA"),

        # Networking
        LabInstructor("113", "Eng. Sama Osama", ["CNC111", "CNC324"], 12.0, "TA"),
        LabInstructor("114", "Eng. Nada Hamdy", ["CNC111", "CNC311"], 14.0, "TA"),
        LabInstructor("115", "Eng. Menna Hamdi", ["CNC111", "CNC312"], 12.0, "TA"),
        LabInstructor("120", "Eng. Nourhan Waleed", ["CNC314"], 10.0, "TA"),

        # AI & Data
        LabInstructor("121", "Eng. Salma Waleed", ["AID311", "AID312"], 12.0, "TA"),
        LabInstructor("107", "Eng. Salma Alashry", ["MTH111", "AID321", "CSC114"], 12.0, "TA"),

        # Math & Statistics (NEW - to fix the error)
        LabInstructor("122", "Eng. Math Assistant", ["MTH111", "MTH121", "MTH212", "ACM215"], 15.0, "TA"),
        LabInstructor("123", "Eng. Math Specialist", ["MTH111", "MTH212", "ACM215"], 12.0, "TA"),
        LabInstructor("124", "Eng. Statistics TA", ["MTH212", "ACM215"], 10.0, "TA"),

        # Languages (NEW)
        LabInstructor("125", "Eng. Language TA", ["LRA401", "LRA403"], 12.0, "TA"),
        LabInstructor("126", "Eng. JA Specialist", ["LRA401", "LRA403"], 10.0, "TA"),

    ]


def load_course_data():
    """Load course data for both levels"""
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


# ==================== CONSTRAINT CHECKING ====================
def can_assign_instructor_to_lab(
        instructor: LabInstructor,
        lab_assignment: Assignment,
        instructor_tracker: InstructorTracker,
        schedule_tracker: ScheduleTracker,
        session_hours: float = 1.5
) -> Tuple[bool, str]:
    """
    Check all hard constraints for assigning instructor to lab
    Returns: (can_assign: bool, reason: str)
    """

    # Constraint 1: Qualification
    if not instructor_tracker.is_qualified(instructor.instructor_id, lab_assignment.course_code):
        return False, f"Instructor {instructor.instructor_name} not qualified for {lab_assignment.course_code}"

    # Constraint 2: Time availability
    if not instructor_tracker.is_available(
            instructor.instructor_id,
            lab_assignment.time_slot.day,
            lab_assignment.time_slot.slot_number
    ):
        return False, f"Instructor {instructor.instructor_name} already teaching at {lab_assignment.time_slot.day} slot {lab_assignment.time_slot.slot_number}"

    # Constraint 3: Check if instructor is also a lecture instructor
    # If instructor_id is numeric and exists in lecture instructor schedule, check conflicts
    try:
        # Try to convert to int to check if it's a lecture instructor ID
        lecture_instructor_id = int(instructor.instructor_id)
        if lecture_instructor_id < 100:  # Lecture instructors have ID < 100
            if not schedule_tracker.is_instructor_available(
                    lecture_instructor_id,
                    lab_assignment.time_slot.day,
                    lab_assignment.time_slot.slot_number
            ):
                return False, f"Instructor {instructor.instructor_name} has lecture conflict"
    except ValueError:
        # instructor_id is not numeric, so it's not a lecture instructor
        pass

    # Constraint 4: Workload capacity
    if not instructor_tracker.has_capacity(instructor.instructor_id, session_hours):
        current = instructor_tracker.instructor_hours[instructor.instructor_id]
        max_hours = instructor.max_hours_per_week or "unlimited"
        return False, f"Instructor {instructor.instructor_name} exceeds max hours ({current}+{session_hours} > {max_hours})"

    # All constraints satisfied
    return True, "OK"


# ==================== SCHEDULING ALGORITHM ====================

class TimetableScheduler:
    def __init__(self, rooms: List[Room], groups: List[Group], sections: List[Section],
                 time_slots: List[TimeSlot], level_1_data: dict, level_2_data: dict):
        self.rooms = rooms
        self.groups = groups
        self.sections = sections
        self.time_slots = time_slots
        self.level_1_data = level_1_data
        self.level_2_data = level_2_data

        self.tracker = ScheduleTracker()
        self.assignments: List[Assignment] = []
        self.assignment_counter = 0

        # Separate rooms by type
        self.lec_rooms = [r for r in rooms if r.room_type == "lec"]
        self.lab_rooms = [r for r in rooms if r.room_type == "lab"]

    def generate_assignment_id(self) -> str:
        self.assignment_counter += 1
        return f"A{self.assignment_counter:04d}"

    def schedule_lectures(self, level: int, lectures_data: List[dict]) -> bool:
        """Schedule all lectures for a given level"""
        # Get groups for this level
        level_groups = [g for g in self.groups if g.level == level]

        # Sort lectures: prioritize shared instructors first
        lectures_data_sorted = sorted(lectures_data,
                                      key=lambda x: (x['instructor_id'], x['course_code']))

        for lecture_data in lectures_data_sorted:
            lecture = Lecture(**lecture_data)

            for group in level_groups:
                # Check if this group already has this lecture
                if self.tracker.has_group_taken_lecture(group.group_id, lecture.course_code):
                    continue

                # Try to find a valid time slot
                success = False
                for time_slot in self.time_slots:
                    # Check all constraints
                    if not self.tracker.is_instructor_available(lecture.instructor_id,
                                                                time_slot.day,
                                                                time_slot.slot_number):
                        continue

                    if not self.tracker.is_group_available(group.group_id,
                                                           time_slot.day,
                                                           time_slot.slot_number):
                        continue

                    # Check if all sections in the group are available
                    all_sections_free = all(
                        self.tracker.is_section_available(s.section_id,
                                                          time_slot.day,
                                                          time_slot.slot_number)
                        for s in group.sections
                    )
                    if not all_sections_free:
                        continue

                    # Find an available lecture room
                    available_room = None
                    for room in self.lec_rooms:
                        if self.tracker.is_room_available(room.room_code,
                                                          time_slot.day,
                                                          time_slot.slot_number):
                            available_room = room
                            break

                    if not available_room:
                        continue

                    # All constraints satisfied - assign the lecture
                    assignment_id = self.generate_assignment_id()
                    section_ids = [s.section_id for s in group.sections]

                    assignment = Assignment(
                        assignment_id=assignment_id,
                        type="lecture",
                        course_code=lecture.course_code,
                        course_name=lecture.course_name,
                        time_slot=time_slot,
                        room=available_room.room_code,
                        instructor=lecture.instructor_name,
                        instructor_id=lecture.instructor_id,
                        assigned_to=[group.group_id] + section_ids
                    )

                    self.assignments.append(assignment)
                    self.tracker.assign_lecture(
                        assignment_id, lecture.instructor_id, available_room.room_code,
                        group.group_id, section_ids, lecture.course_code,
                        time_slot.day, time_slot.slot_number
                    )

                    success = True
                    break

                if not success:
                    print(f"Warning: Could not schedule lecture {lecture.course_code} for {group.group_id}")
                    return False

        return True


    def schedule_labs(self, level: int, labs_data: List[dict]) -> bool:
        """Schedule all labs for a given level with instructor awareness"""
        # Get sections for this level
        level_sections = [s for s in self.sections if s.level == level]

        # Sort labs: prioritize those with specific room requirements
        labs_data_sorted = sorted(labs_data,
                                key=lambda x: (x['room_code'] == "", x['course_code']))

        # Track course scheduling to avoid instructor conflicts
        course_time_slot_count = defaultdict(lambda: defaultdict(int))  # course_code -> day -> slot -> count

        # Get available lab instructors (we'll estimate this since we don't have them in scheduler yet)
        # For now, we'll assume a conservative limit
        course_instructor_limits = {
            'CSE214': 2, 'LRA401': 5, 'LRA403': 5, 'ECE111': 3, 'PHY113': 3,
            'CNC111': 3, 'MTH212': 4, 'MTH111': 5, 'CSC211': 5, 'ACM215': 7, 'CSC111': 10
        }

        for lab_data in labs_data_sorted:
            lab = Lab(**lab_data)

            for section in level_sections:
                # Check if this section already has this lab
                if self.tracker.has_section_taken_lab(section.section_id, lab.course_code):
                    continue

                # Try to find a valid time slot
                success = False
                # Try time slots in random order to distribute load
                shuffled_slots = self.time_slots.copy()
                random.shuffle(shuffled_slots)

                for time_slot in shuffled_slots:
                    # Check if section is available
                    if not self.tracker.is_section_available(section.section_id,
                                                            time_slot.day,
                                                            time_slot.slot_number):
                        continue

                    # Check instructor availability constraint
                    current_count = course_time_slot_count[lab.course_code][(time_slot.day, time_slot.slot_number)]
                    max_instructors = course_instructor_limits.get(lab.course_code, 3)

                    # Don't schedule more labs than available instructors
                    if current_count >= max_instructors:
                        continue

                    # Determine which room to use
                    available_room = None

                    # IMPORTANT: If lab has a specific room, use ONLY that room
                    if lab.room_code and lab.room_code.strip():
                        # Lab has a specific room requirement - must use that room
                        if self.tracker.is_room_available(lab.room_code,
                                                        time_slot.day,
                                                        time_slot.slot_number):
                            available_room = lab.room_code
                    else:
                        # Lab doesn't have specific room - find any available lab room
                        # Try rooms in random order to distribute usage
                        shuffled_rooms = self.lab_rooms.copy()
                        random.shuffle(shuffled_rooms)
                        for room in shuffled_rooms:
                            if self.tracker.is_room_available(room.room_code,
                                                            time_slot.day,
                                                            time_slot.slot_number):
                                available_room = room.room_code
                                break

                    if not available_room:
                        continue

                    # All constraints satisfied - assign the lab
                    assignment_id = self.generate_assignment_id()

                    assignment = Assignment(
                        assignment_id=assignment_id,
                        type="lab",
                        course_code=lab.course_code,
                        course_name=lab.course_name,
                        time_slot=time_slot,
                        room=available_room,
                        assigned_to=[section.section_id]
                    )

                    self.assignments.append(assignment)
                    self.tracker.assign_lab(
                        assignment_id, available_room, section.section_id,
                        lab.course_code, time_slot.day, time_slot.slot_number
                    )

                    # Track this course scheduling
                    course_time_slot_count[lab.course_code][(time_slot.day, time_slot.slot_number)] += 1

                    success = True
                    break

                if not success:
                    print(f"Warning: Could not schedule lab {lab.course_code} for {section.section_id}")
                    # Show debug info about the scheduling issue
                    print(f"  Course {lab.course_code} distribution:")
                    time_slots_used = [(day, slot, count) for (day, slot), count in
                                    course_time_slot_count[lab.course_code].items() if count > 0]
                    for day, slot, count in sorted(time_slots_used)[:5]:  # Show first 5
                        print(f"    {day} slot {slot}: {count} labs")
                    return False

        return True

    def generate_schedule(self) -> bool:
        """Main scheduling function"""
        print("Starting timetable generation...")
        print(f"Total time slots available: {len(self.time_slots)}")
        print(f"Lecture rooms: {len(self.lec_rooms)}")
        print(f"Lab rooms: {len(self.lab_rooms)}")
        print()

        # Schedule Level 1 lectures
        print("Scheduling Level 1 lectures...")
        if not self.schedule_lectures(1, self.level_1_data['lectures']):
            print("Failed to schedule Level 1 lectures")
            return False
        print(f"Level 1 lectures scheduled: {len([a for a in self.assignments if a.type == 'lecture'])}")

        # Schedule Level 2 lectures
        print("Scheduling Level 2 lectures...")
        if not self.schedule_lectures(2, self.level_2_data['lectures']):
            print("Failed to schedule Level 2 lectures")
            return False
        print(f"Total lectures scheduled: {len([a for a in self.assignments if a.type == 'lecture'])}")

        # Schedule Level 1 labs
        print("\nScheduling Level 1 labs...")
        if not self.schedule_labs(1, self.level_1_data['labs']):
            print("Failed to schedule Level 1 labs")
            return False
        print(
            f"Level 1 labs scheduled: {len([a for a in self.assignments if a.type == 'lab' and any('L1' in x for x in a.assigned_to)])}")

        # Schedule Level 2 labs
        print("Scheduling Level 2 labs...")
        if not self.schedule_labs(2, self.level_2_data['labs']):
            print("Failed to schedule Level 2 labs")
            return False
        print(f"Total labs scheduled: {len([a for a in self.assignments if a.type == 'lab'])}")

        print(f"\nTotal assignments: {len(self.assignments)}")
        return True


# ==================== LAB INSTRUCTOR ASSIGNMENT ====================
def assign_instructors_to_labs(
        scheduler: TimetableScheduler,
        lab_instructors: List[LabInstructor],
        session_hours: float = 1.5
) -> bool:
    """
    Assign instructors to all scheduled labs
    """

    instructor_tracker = InstructorTracker()

    # Initialize instructor pool
    for instructor in lab_instructors:
        instructor_tracker.instructors[instructor.instructor_id] = instructor

    # Get all lab assignments (already scheduled with time slots)
    lab_assignments = [a for a in scheduler.assignments if a.type == "lab"]

    print(f"\nDebug: Total lab assignments to process: {len(lab_assignments)}")

    # Sort by constraint difficulty
    def count_qualified_instructors(lab_assignment):
        count = sum(1 for inst in lab_instructors
                    if lab_assignment.course_code in inst.qualified_labs)
        return count

    lab_assignments_sorted = sorted(lab_assignments, key=count_qualified_instructors)

    # Print debug info about course coverage
    print("\nDebug: Course coverage by instructors:")
    course_coverage = defaultdict(list)
    for lab in lab_assignments_sorted:
        qualified = [inst.instructor_name for inst in lab_instructors
                     if lab.course_code in inst.qualified_labs]
        course_coverage[lab.course_code] = qualified
        print(f"  {lab.course_code}: {len(qualified)} qualified instructors - {qualified}")

    # Try to assign instructor to each lab
    for lab_assignment in lab_assignments_sorted:
        assigned = False

        # Get qualified instructors for this lab
        qualified = [inst for inst in lab_instructors
                     if lab_assignment.course_code in inst.qualified_labs]

        print(f"\nDebug: Processing {lab_assignment.course_code} for {lab_assignment.assigned_to[0]} "
              f"at {lab_assignment.time_slot.day} slot {lab_assignment.time_slot.slot_number}")
        print(f"Debug: Found {len(qualified)} qualified instructors: {[q.instructor_name for q in qualified]}")

        # Sort by current workload (prefer instructors with less load)
        qualified_sorted = sorted(
            qualified,
            key=lambda inst: instructor_tracker.instructor_hours[inst.instructor_id]
        )

        # Try each qualified instructor
        for instructor in qualified_sorted:
            can_assign, reason = can_assign_instructor_to_lab(
                instructor,
                lab_assignment,
                instructor_tracker,
                scheduler.tracker,
                session_hours
            )

            print(f"Debug: Trying {instructor.instructor_name} - {reason}")

            if can_assign:
                # Assign instructor
                lab_assignment.lab_instructor_id = instructor.instructor_id
                lab_assignment.lab_instructor_name = instructor.instructor_name

                instructor_tracker.assign(
                    instructor.instructor_id,
                    lab_assignment.time_slot.day,
                    lab_assignment.time_slot.slot_number,
                    lab_assignment.assignment_id,
                    session_hours
                )

                print(f"Debug: ✓ Assigned {instructor.instructor_name} to {lab_assignment.course_code}")
                assigned = True
                break

        if not assigned:
            print(f"ERROR: Cannot assign instructor to {lab_assignment.course_code} "
                  f"for {lab_assignment.assigned_to[0]} at "
                  f"{lab_assignment.time_slot.day} slot {lab_assignment.time_slot.slot_number}")

            # Show why each qualified instructor failed
            for instructor in qualified:
                can_assign, reason = can_assign_instructor_to_lab(
                    instructor,
                    lab_assignment,
                    instructor_tracker,
                    scheduler.tracker,
                    session_hours
                )
                print(f"  - {instructor.instructor_name}: {reason}")

            return False

    return True


# ==================== VALIDATION ====================

def validate_schedule(scheduler: TimetableScheduler) -> Tuple[bool, List[str]]:
    """Validate the generated schedule"""
    errors = []

    # Check no instructor conflicts
    instructor_slots = defaultdict(list)
    for assignment in scheduler.assignments:
        if assignment.instructor_id:
            key = (assignment.instructor_id, assignment.time_slot.day, assignment.time_slot.slot_number)
            instructor_slots[key].append(assignment.assignment_id)

    for key, assignments in instructor_slots.items():
        if len(assignments) > 1:
            errors.append(f"Instructor {key[0]} double-booked on {key[1]} slot {key[2]}: {assignments}")

    # Check no room conflicts
    room_slots = defaultdict(list)
    for assignment in scheduler.assignments:
        key = (assignment.room, assignment.time_slot.day, assignment.time_slot.slot_number)
        room_slots[key].append(assignment.assignment_id)

    for key, assignments in room_slots.items():
        if len(assignments) > 1:
            errors.append(f"Room {key[0]} double-booked on {key[1]} slot {key[2]}: {assignments}")

    # Check each group has all lectures
    for group in scheduler.groups:
        level = group.level
        expected_courses = set()
        if level == 1:
            expected_courses = {lec['course_code'] for lec in scheduler.level_1_data['lectures']}
        else:
            expected_courses = {lec['course_code'] for lec in scheduler.level_2_data['lectures']}

        assigned_courses = scheduler.tracker.group_lectures_assigned[group.group_id]
        if assigned_courses != expected_courses:
            errors.append(f"Group {group.group_id} missing lectures: {expected_courses - assigned_courses}")

    # Check each section has all labs
    for section in scheduler.sections:
        level = section.level
        expected_labs = set()
        if level == 1:
            expected_labs = {lab['course_code'] for lab in scheduler.level_1_data['labs']}
        else:
            expected_labs = {lab['course_code'] for lab in scheduler.level_2_data['labs']}

        assigned_labs = scheduler.tracker.section_labs_assigned[section.section_id]
        if assigned_labs != expected_labs:
            errors.append(f"Section {section.section_id} missing labs: {expected_labs - assigned_labs}")

    return len(errors) == 0, errors


def validate_instructor_assignments(
        scheduler: TimetableScheduler,
        lab_instructors: List[LabInstructor]
) -> Tuple[bool, List[str]]:
    """Validate all instructor assignment constraints"""
    errors = []

    # Create instructor tracker for validation
    instructor_tracker = InstructorTracker()
    for instructor in lab_instructors:
        instructor_tracker.instructors[instructor.instructor_id] = instructor

    # Track assignments manually for validation
    instructor_assignments = defaultdict(list)
    instructor_hours = defaultdict(float)

    for assignment in scheduler.assignments:
        if assignment.type == "lab" and assignment.lab_instructor_id:
            instructor_id = assignment.lab_instructor_id
            instructor_assignments[instructor_id].append(assignment)
            instructor_hours[instructor_id] += 1.5  # Each lab is 1.5 hours

    # Check 1: All labs have instructors
    labs_without_instructors = [a for a in scheduler.assignments
                                if a.type == "lab" and not a.lab_instructor_id]
    for assignment in labs_without_instructors:
        errors.append(f"Lab {assignment.course_code} for {assignment.assigned_to[0]} has no instructor")

    # Check 2: No instructor double-booking
    instructor_time_slots = defaultdict(set)
    for assignment in scheduler.assignments:
        if assignment.type == "lab" and assignment.lab_instructor_id:
            key = (assignment.lab_instructor_id, assignment.time_slot.day, assignment.time_slot.slot_number)
            if key in instructor_time_slots:
                errors.append(
                    f"Instructor {assignment.lab_instructor_name} double-booked on {assignment.time_slot.day} slot {assignment.time_slot.slot_number}")
            instructor_time_slots[key].add(assignment.assignment_id)

    # Check 3: No workload violations
    for instructor_id, hours in instructor_hours.items():
        instructor = next((inst for inst in lab_instructors if inst.instructor_id == instructor_id), None)
        if instructor and instructor.max_hours_per_week and hours > instructor.max_hours_per_week:
            errors.append(
                f"Instructor {instructor.instructor_name} exceeds max hours: {hours} > {instructor.max_hours_per_week}")

    # Check 4: All assignments are qualified
    for assignment in scheduler.assignments:
        if assignment.type == "lab" and assignment.lab_instructor_id:
            instructor = next((inst for inst in lab_instructors
                               if inst.instructor_id == assignment.lab_instructor_id), None)
            if instructor and assignment.course_code not in instructor.qualified_labs:
                errors.append(f"Instructor {instructor.instructor_name} not qualified for {assignment.course_code}")

    return len(errors) == 0, errors


# ==================== OUTPUT GENERATION ====================

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
    """Export individual section timetables"""
    import os

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


def export_html_timetable(scheduler: TimetableScheduler, filename: str = "timetable.html"):
    """Export timetable as HTML with lab instructor display"""
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]

    # Define time slots with exact times from the reference
    time_slots_display = [
        ("9:00- 9:45", "9:00", "9:45"),
        ("9:45 - 10:30", "9:45", "10:30"),
        ("10:45 - 11:30", "10:45", "11:30"),
        ("11:30 - 12:15", "11:30", "12:15"),
        ("12:30 - 1:15", "12:30", "1:15"),
        ("1:15 - 2:00", "1:15", "2:00"),
        ("2:15 - 3:00", "2:15", "3:00"),
        ("3:00 - 3:45", "3:00", "3:45")
    ]

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>College Timetable - CSIT</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 10px;
                font-size: 10px;
            }
            h1 { 
                text-align: center; 
                color: #333; 
                font-size: 18px;
                margin: 10px 0;
            }
            h2 { 
                color: #333; 
                font-size: 14px;
                margin: 15px 0 5px 0;
                background-color: #f0f0f0;
                padding: 5px;
            }
            h3 {
                color: #555;
                font-size: 12px;
                margin: 10px 0 5px 0;
            }
            table { 
                border-collapse: collapse; 
                width: 100%; 
                margin: 10px 0;
                page-break-inside: avoid;
            }
            th, td { 
                border: 1px solid #000; 
                padding: 3px;
                text-align: center;
                vertical-align: top;
                font-size: 9px;
                min-width: 80px;
            }
            th { 
                background-color: #d0d0d0; 
                font-weight: bold;
                font-size: 10px;
            }
            .time-col {
                background-color: #e8e8e8;
                font-weight: bold;
                font-size: 9px;
                min-width: 60px;
            }
            .lecture { 
                background-color: #e3f2fd;
                font-size: 8px;
            }
            .lab { 
                background-color: #fff3e0;
                font-size: 8px;
            }
            .course-code {
                font-weight: bold;
                font-size: 9px;
                display: block;
                margin-bottom: 2px;
            }
            .course-name {
                font-size: 8px;
                display: block;
                margin-bottom: 2px;
            }
            .instructor {
                font-size: 7px;
                color: #1976d2;
                font-weight: bold;
                display: block;
                margin-bottom: 1px;
            }
            .lab-instructor {
                font-size: 7px;
                color: #d32f2f;
                font-weight: bold;
                display: block;
                margin-bottom: 1px;
            }
            .room {
                font-size: 7px;
                color: #666;
                display: block;
            }
            .section-label {
                font-size: 7px;
                color: #d32f2f;
                font-weight: bold;
                display: block;
                margin-top: 2px;
            }
            .section-table { 
                margin-bottom: 30px;
                page-break-after: always;
            }
            .group-table {
                margin-bottom: 20px;
            }
            .nav-menu {
                background-color: #f5f5f5;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
            }
            .nav-menu a {
                margin: 0 10px;
                text-decoration: none;
                color: #1976d2;
                font-weight: bold;
            }
            .nav-menu a:hover {
                text-decoration: underline;
            }
            .instructor-summary {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 10px 0;
                font-size: 9px;
            }
            .instructor-summary h3 {
                margin-top: 0;
                color: #333;
            }
            .instructor-list {
                columns: 3;
                font-size: 8px;
            }
            .instructor-item {
                margin-bottom: 3px;
                break-inside: avoid;
            }
            @media print {
                .section-table, .group-table {
                    page-break-after: always;
                }
                .nav-menu {
                    display: none;
                }
                .instructor-summary {
                    page-break-inside: avoid;
                }
                body {
                    font-size: 9px;
                }
            }
        </style>
    </head>
    <body>
        <h1>CSIT College Timetable</h1>
        <p style="text-align: center; font-size: 10px;">Generated on: """ + datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + """</p>
        
        <div class="nav-menu">
            <strong>Quick Navigation:</strong>
            <a href="#levels">Level Overview</a> |
            <a href="#instructors">Lab Instructors Summary</a> |
            <a href="#groups">Group Timetables</a> |
            <a href="#sections">Section Timetables</a> |
            <a href="#professors">Professor Timetables</a> |
            <a href="#rooms">Room Timetables</a> |
            <a href="#lab-instructors">Lab Instructor Timetables</a>
        </div>
    """

    # ========== PART 1: LEVEL OVERVIEW ==========
    html += '<h1 id="levels" style="background-color: #673AB7; color: white; padding: 10px;">LEVEL OVERVIEW</h1>'
    html += '<p style="text-align: center; font-style: italic;">Complete schedule for both levels organized by groups and sections</p>'

    # Get groups for both levels
    level_1_groups = sorted([g for g in scheduler.groups if g.level == 1], key=lambda g: g.group_id)
    level_2_groups = sorted([g for g in scheduler.groups if g.level == 2], key=lambda g: g.group_id)
    
    html += '<div class="section-table" style="overflow-x: auto;">'
    html += '<h2 style="background-color: #4CAF50; color: white; padding: 8px;">Level 1 & Level 2 - Combined Schedule</h2>'
    html += '<table style="width: auto;">'
    
    # Header row 1: Level names
    html += '<tr><th class="time-col" rowspan="3">Day</th><th class="time-col" rowspan="3">Time</th>'
    html += f'<th colspan="{len(level_1_groups) * 3}" style="background-color: #4CAF50; color: white; font-size: 12px;">LEVEL 1</th>'
    html += f'<th colspan="{len(level_2_groups) * 3}" style="background-color: #FF9800; color: white; font-size: 12px;">LEVEL 2</th>'
    html += '</tr>'
    
    # Header row 2: Group names
    html += '<tr>'
    for group in level_1_groups:
        html += f'<th colspan="3" style="background-color: #2196F3; color: white;">{group.group_id}</th>'
    for group in level_2_groups:
        html += f'<th colspan="3" style="background-color: #FF5722; color: white;">{group.group_id}</th>'
    html += '</tr>'
    
    # Header row 3: Section numbers
    html += '<tr>'
    for group in level_1_groups:
        for section in sorted(group.sections, key=lambda s: s.section_number):
            html += f'<th style="font-size: 8px;">S{section.section_number}</th>'
    for group in level_2_groups:
        for section in sorted(group.sections, key=lambda s: s.section_number):
            html += f'<th style="font-size: 8px;">S{section.section_number}</th>'
    html += '</tr>'
    
    # Data rows: Each day and time slot (shared between both levels)
    for day_idx, day in enumerate(days):
        day_time_slots = [ts for ts in time_slots_display]
        first_slot_of_day = True
        
        for time_idx, (time_label, start, end) in enumerate(day_time_slots):
            our_slot = (time_idx // 2) + 1
            is_first_half = (time_idx % 2 == 0)
            
            if not is_first_half:
                continue  # Skip second half, we use rowspan
            
            html += '<tr>'
            
            # Day column (merged for all time slots of this day)
            if first_slot_of_day:
                num_slots = len([ts for ts in day_time_slots if day_time_slots.index(ts) % 2 == 0])
                border_style = "border-top: 5px solid #000;" if day_idx > 0 else ""
                html += f'<td class="time-col" rowspan="{num_slots}" style="font-size: 9px; font-weight: bold; background-color: #d0d0d0; {border_style}">{day}</td>'
                first_slot_of_day = False
            
            # Time column (start-end) - centered and shared
            border_style = "border-top: 5px solid #000;" if time_idx == 0 and day_idx > 0 else ""
            html += f'<td class="time-col" style="font-size: 8px; text-align: center; vertical-align: middle; {border_style}">{start}-{end}</td>'
            
            # Process Level 1 groups
            for group in level_1_groups:
                # Check if this is a lecture (all sections have the same assignment)
                group_assignments = []
                for section in sorted(group.sections, key=lambda s: s.section_number):
                    assignment = None
                    for a in scheduler.assignments:
                        if (section.section_id in a.assigned_to and 
                            a.time_slot.day == day and 
                            a.time_slot.slot_number == our_slot):
                            assignment = a
                            break
                    group_assignments.append(assignment)
                
                # Check if all sections have the same lecture
                is_lecture = (group_assignments[0] is not None and 
                             group_assignments[0].type == "lecture" and
                             all(a == group_assignments[0] for a in group_assignments))
                
                border_style = "border-top: 5px solid #000;" if day_idx > 0 and time_idx == 0 else ""
                
                if is_lecture:
                    # Merge cells for lecture (all 3 sections attend together)
                    assignment = group_assignments[0]
                    html += f'<td class="lecture" colspan="3" style="font-size: 7px; padding: 3px; min-width: 100px; {border_style}">'
                    html += f'<div style="font-weight: bold; font-size: 8px; margin-bottom: 2px;">{assignment.course_code}</div>'
                    html += f'<div style="font-size: 7px; margin-bottom: 2px;">{assignment.course_name}</div>'
                    html += f'<div style="color: #1976d2; font-size: 7px; margin-bottom: 2px;">{assignment.instructor}</div>'
                    html += f'<div style="color: #666; font-size: 6px;">LEC {assignment.room}</div>'
                    html += '</td>'
                else:
                    # Different assignments for each section (labs or different lectures)
                    for section_idx, section in enumerate(sorted(group.sections, key=lambda s: s.section_number)):
                        assignment = group_assignments[section_idx]
                        
                        if assignment:
                            css_class = "lecture" if assignment.type == "lecture" else "lab"
                            html += f'<td class="{css_class}" style="font-size: 7px; padding: 3px; min-width: 100px; {border_style}">'
                            html += f'<div style="font-weight: bold; font-size: 8px; margin-bottom: 2px;">{assignment.course_code}</div>'
                            html += f'<div style="font-size: 7px; margin-bottom: 2px;">{assignment.course_name}</div>'
                            
                            if assignment.type == "lecture" and assignment.instructor:
                                html += f'<div style="color: #1976d2; font-size: 7px; margin-bottom: 2px;">{assignment.instructor}</div>'
                            elif assignment.type == "lab" and assignment.lab_instructor_name:
                                html += f'<div style="color: #d32f2f; font-size: 7px; margin-bottom: 2px;">{assignment.lab_instructor_name}</div>'
                            
                            room_type = "LEC" if assignment.type == "lecture" else "LAB"
                            html += f'<div style="color: #666; font-size: 6px;">{room_type} {assignment.room}</div>'
                            html += '</td>'
                        else:
                            html += f'<td style="min-width: 100px; {border_style}"></td>'
            
            # Process Level 2 groups (same logic)
            for group in level_2_groups:
                group_assignments = []
                for section in sorted(group.sections, key=lambda s: s.section_number):
                    assignment = None
                    for a in scheduler.assignments:
                        if (section.section_id in a.assigned_to and 
                            a.time_slot.day == day and 
                            a.time_slot.slot_number == our_slot):
                            assignment = a
                            break
                    group_assignments.append(assignment)
                
                is_lecture = (group_assignments[0] is not None and 
                             group_assignments[0].type == "lecture" and
                             all(a == group_assignments[0] for a in group_assignments))
                
                border_style = "border-top: 5px solid #000;" if day_idx > 0 and time_idx == 0 else ""
                
                if is_lecture:
                    assignment = group_assignments[0]
                    html += f'<td class="lecture" colspan="3" style="font-size: 7px; padding: 3px; min-width: 100px; {border_style}">'
                    html += f'<div style="font-weight: bold; font-size: 8px; margin-bottom: 2px;">{assignment.course_code}</div>'
                    html += f'<div style="font-size: 7px; margin-bottom: 2px;">{assignment.course_name}</div>'
                    html += f'<div style="color: #1976d2; font-size: 7px; margin-bottom: 2px;">{assignment.instructor}</div>'
                    html += f'<div style="color: #666; font-size: 6px;">LEC {assignment.room}</div>'
                    html += '</td>'
                else:
                    for section_idx, section in enumerate(sorted(group.sections, key=lambda s: s.section_number)):
                        assignment = group_assignments[section_idx]
                        
                        if assignment:
                            css_class = "lecture" if assignment.type == "lecture" else "lab"
                            html += f'<td class="{css_class}" style="font-size: 7px; padding: 3px; min-width: 100px; {border_style}">'
                            html += f'<div style="font-weight: bold; font-size: 8px; margin-bottom: 2px;">{assignment.course_code}</div>'
                            html += f'<div style="font-size: 7px; margin-bottom: 2px;">{assignment.course_name}</div>'
                            
                            if assignment.type == "lecture" and assignment.instructor:
                                html += f'<div style="color: #1976d2; font-size: 7px; margin-bottom: 2px;">{assignment.instructor}</div>'
                            elif assignment.type == "lab" and assignment.lab_instructor_name:
                                html += f'<div style="color: #d32f2f; font-size: 7px; margin-bottom: 2px;">{assignment.lab_instructor_name}</div>'
                            
                            room_type = "LEC" if assignment.type == "lecture" else "LAB"
                            html += f'<div style="color: #666; font-size: 6px;">{room_type} {assignment.room}</div>'
                            html += '</td>'
                        else:
                            html += f'<td style="min-width: 100px; {border_style}"></td>'
            
            html += '</tr>'
    
    html += '</table></div>'

    # ========== PART 2: LAB INSTRUCTORS SUMMARY ==========
    html += '<h1 id="instructors" style="background-color: #9C27B0; color: white; padding: 10px;">LAB INSTRUCTORS SUMMARY</h1>'

    # Collect lab instructor assignments
    lab_assignments = [a for a in scheduler.assignments if a.type == "lab" and a.lab_instructor_name]
    instructor_workload = defaultdict(list)

    for assignment in lab_assignments:
        instructor_workload[assignment.lab_instructor_name].append(assignment)

    html += f'<p style="text-align: center; font-style: italic;">Total lab sessions with assigned instructors: {len(lab_assignments)}</p>'

    html += '<div class="instructor-summary">'
    html += '<h3>Lab Instructor Assignments:</h3>'
    html += '<div class="instructor-list">'

    for instructor_name, assignments in sorted(instructor_workload.items()):
        courses = set(a.course_code for a in assignments)
        total_hours = len(assignments) * 1.5  # Each lab is 1.5 hours
        html += f'''
        <div class="instructor-item">
            <strong>{instructor_name}</strong>: {len(assignments)} labs ({total_hours}h) - Courses: {", ".join(sorted(courses))}
        </div>
        '''

    html += '</div></div>'

    # ========== PART 3: GROUP TIMETABLES ==========
    html += '<h1 id="groups" style="background-color: #2196F3; color: white; padding: 10px; margin-top: 30px;">GROUP TIMETABLES</h1>'
    html += '<p style="text-align: center; font-style: italic;">Shows lectures for each group (all 3 sections attend together)</p>'

    groups_by_level = {}
    for group in scheduler.groups:
        level_key = f"Level {group.level}"
        if level_key not in groups_by_level:
            groups_by_level[level_key] = []
        groups_by_level[level_key].append(group)

    for level_name in sorted(groups_by_level.keys()):
        html += f'<h2 style="background-color: #4CAF50; color: white; padding: 8px;">{level_name} - Groups</h2>'

        for group in sorted(groups_by_level[level_name], key=lambda g: g.group_id):
            # Get lecture assignments for this group
            lecture_assignments = [a for a in scheduler.assignments
                                   if a.type == "lecture" and group.group_id in a.assigned_to]

            html += f"""
        <div class="group-table">
            <h2>Group: {group.group_id} (Sections: {', '.join([s.section_id for s in group.sections])})</h2>
            <p style="font-size: 9px; color: #666; margin: 5px 0;">Lectures only - all sections attend together</p>
            <table>
                <tr>
                    <th class="time-col">Time</th>
            """

            for day in days:
                html += f"<th>{day}</th>"
            html += "</tr>"

            for time_idx, (time_label, start, end) in enumerate(time_slots_display):
                our_slot = (time_idx // 2) + 1
                is_first_half = (time_idx % 2 == 0)

                html += f"""
                <tr>
                    <td class="time-col">{time_label}</td>
                """

                for day in days:
                    assignment = None
                    for a in lecture_assignments:
                        if a.time_slot.day == day and a.time_slot.slot_number == our_slot:
                            assignment = a
                            break

                    if assignment and is_first_half:
                        html += f'<td class="lecture" rowspan="2">'
                        html += f'<span class="course-code">{assignment.course_code}</span>'
                        html += f'<span class="course-name">{assignment.course_name}</span>'
                        html += f'<span class="instructor">{assignment.instructor}</span>'
                        html += f'<span class="room">LEC {assignment.room}</span>'
                        html += '</td>'
                    elif not assignment and is_first_half:
                        html += '<td rowspan="2"></td>'

                html += "</tr>"

            html += "</table>"

            # Add lab information for this group
            group_labs = []
            for section in group.sections:
                section_labs = [a for a in scheduler.assignments
                                if a.type == "lab" and section.section_id in a.assigned_to and a.lab_instructor_name]
                group_labs.extend(section_labs)

            if group_labs:
                html += '<h3>Lab Sessions for this Group (by section):</h3>'
                html += '<table>'
                html += '<tr><th>Section</th><th>Course</th><th>Day</th><th>Time</th><th>Room</th><th>Lab Instructor</th></tr>'

                for lab in sorted(group_labs,
                                  key=lambda x: (x.assigned_to[0], x.time_slot.day, x.time_slot.slot_number)):
                    html += f"""
                    <tr>
                        <td>{lab.assigned_to[0]}</td>
                        <td>{lab.course_code} - {lab.course_name}</td>
                        <td>{lab.time_slot.day}</td>
                        <td>{lab.time_slot.start_time}-{lab.time_slot.end_time}</td>
                        <td>{lab.room}</td>
                        <td><strong>{lab.lab_instructor_name}</strong></td>
                    </tr>
                    """

                html += '</table>'

            html += "</div>"

    # ========== PART 4: SECTION TIMETABLES ==========
    html += '<h1 id="sections" style="background-color: #FF9800; color: white; padding: 10px; margin-top: 40px;">SECTION TIMETABLES</h1>'
    html += '<p style="text-align: center; font-style: italic;">Complete schedule for each section (lectures + labs)</p>'

    sections_by_level = {}
    for section in scheduler.sections:
        level_key = f"Level {section.level}"
        if level_key not in sections_by_level:
            sections_by_level[level_key] = []
        sections_by_level[level_key].append(section)

    for level_name in sorted(sections_by_level.keys()):
        html += f'<h2 style="background-color: #4CAF50; color: white; padding: 8px;">{level_name} - Sections</h2>'

        for section in sorted(sections_by_level[level_name], key=lambda s: s.section_id):
            assignments = [a for a in scheduler.assignments if section.section_id in a.assigned_to]

            html += f"""
        <div class="section-table">
            <h2>Section: {section.section_id} (Group: {section.group_id})</h2>
            <table>
                <tr>
                    <th class="time-col">Time</th>
            """

            for day in days:
                html += f"<th>{day}</th>"
            html += "</tr>"

            for time_idx, (time_label, start, end) in enumerate(time_slots_display):
                our_slot = (time_idx // 2) + 1
                is_first_half = (time_idx % 2 == 0)

                html += f"""
                <tr>
                    <td class="time-col">{time_label}</td>
                """

                for day in days:
                    assignment = None
                    for a in assignments:
                        if a.time_slot.day == day and a.time_slot.slot_number == our_slot:
                            assignment = a
                            break

                    if assignment and is_first_half:
                        css_class = "lecture" if assignment.type == "lecture" else "lab"

                        html += f'<td class="{css_class}" rowspan="2">'
                        html += f'<span class="course-code">{assignment.course_code}</span>'
                        html += f'<span class="course-name">{assignment.course_name}</span>'

                        if assignment.type == "lecture" and assignment.instructor:
                            html += f'<span class="instructor">{assignment.instructor}</span>'
                        elif assignment.type == "lab" and assignment.lab_instructor_name:
                            html += f'<span class="lab-instructor">{assignment.lab_instructor_name}</span>'

                        html += f'<span class="room">{assignment.type.upper()} {assignment.room}</span>'
                        html += '</td>'
                    elif not assignment and is_first_half:
                        html += '<td rowspan="2"></td>'

                html += "</tr>"

            html += "</table>"

            # Add lab instructor summary for this section
            section_labs = [a for a in assignments if a.type == "lab" and a.lab_instructor_name]
            if section_labs:
                html += '<h3>Lab Instructors for this Section:</h3>'
                html += '<table>'
                html += '<tr><th>Course</th><th>Lab Instructor</th><th>Day & Time</th><th>Room</th></tr>'

                for lab in sorted(section_labs, key=lambda x: x.course_code):
                    html += f"""
                    <tr>
                        <td><strong>{lab.course_code}</strong> - {lab.course_name}</td>
                        <td><strong>{lab.lab_instructor_name}</strong></td>
                        <td>{lab.time_slot.day} {lab.time_slot.start_time}-{lab.time_slot.end_time}</td>
                        <td>{lab.room}</td>
                    </tr>
                    """

                html += '</table>'

            html += "</div>"

    # ========== PART 5: PROFESSOR TIMETABLES ==========
    html += '<h1 id="professors" style="background-color: #9C27B0; color: white; padding: 10px; margin-top: 30px;">PROFESSOR TIMETABLES</h1>'
    html += '<p style="text-align: center; font-style: italic;">Complete schedule for each professor showing all their lectures</p>'

    # Group assignments by professor
    professors = {}
    for assignment in scheduler.assignments:
        if assignment.type == "lecture" and assignment.instructor:
            if assignment.instructor not in professors:
                professors[assignment.instructor] = []
            professors[assignment.instructor].append(assignment)

    for professor in sorted(professors.keys()):
        prof_assignments = professors[professor]
        html += f'<div class="section-table">'
        html += f'<h2 style="background-color: #9C27B0; color: white; padding: 8px;">Prof. {professor}</h2>'
        html += f'<p style="font-size: 9px; color: #666; margin: 5px 0;">Teaching {len(prof_assignments)} lectures</p>'
        html += '<table>'
        html += '<tr><th class="time-col">Time</th>'
        
        for day in days:
            html += f"<th>{day}</th>"
        html += "</tr>"

        for time_idx, (time_label, start, end) in enumerate(time_slots_display):
            our_slot = (time_idx // 2) + 1
            is_first_half = (time_idx % 2 == 0)

            html += f'<tr><td class="time-col">{time_label}</td>'

            for day in days:
                assignment = None
                for a in prof_assignments:
                    if a.time_slot.day == day and a.time_slot.slot_number == our_slot:
                        assignment = a
                        break

                if assignment and is_first_half:
                    html += '<td class="lecture" rowspan="2">'
                    html += f'<strong>{assignment.course_code}</strong> - {assignment.course_name}<br>'
                    html += f'<span class="room">LEC {assignment.room}</span><br>'
                    html += f'<span style="font-size: 8px; color: #666;">Groups: {", ".join(sorted(set([g[:5] for g in assignment.assigned_to])))}</span>'
                    html += '</td>'
                elif not assignment and is_first_half:
                    html += '<td rowspan="2"></td>'

            html += "</tr>"

        html += "</table></div>"

    # ========== PART 6: ROOM TIMETABLES ==========
    html += '<h1 id="rooms" style="background-color: #FF5722; color: white; padding: 10px; margin-top: 30px;">ROOM TIMETABLES</h1>'
    html += '<p style="text-align: center; font-style: italic;">Occupancy schedule for each room</p>'

    # Group assignments by room
    room_usage = {}
    for assignment in scheduler.assignments:
        if assignment.room not in room_usage:
            room_usage[assignment.room] = []
        room_usage[assignment.room].append(assignment)

    # Separate lecture and lab rooms
    lecture_rooms = sorted([r for r in room_usage.keys() if any(a.type == "lecture" for a in room_usage[r])])
    lab_rooms = sorted([r for r in room_usage.keys() if r not in lecture_rooms])

    html += '<h2 style="background-color: #2196F3; color: white; padding: 8px;">Lecture Rooms</h2>'
    for room in lecture_rooms:
        room_assignments = room_usage[room]
        html += f'<div class="section-table">'
        html += f'<h3 style="background-color: #64B5F6; padding: 6px;">Room {room}</h3>'
        html += f'<p style="font-size: 9px; color: #666; margin: 5px 0;">{len(room_assignments)} sessions scheduled</p>'
        html += '<table>'
        html += '<tr><th class="time-col">Time</th>'
        
        for day in days:
            html += f"<th>{day}</th>"
        html += "</tr>"

        for time_idx, (time_label, start, end) in enumerate(time_slots_display):
            our_slot = (time_idx // 2) + 1
            is_first_half = (time_idx % 2 == 0)

            html += f'<tr><td class="time-col">{time_label}</td>'

            for day in days:
                assignment = None
                for a in room_assignments:
                    if a.time_slot.day == day and a.time_slot.slot_number == our_slot:
                        assignment = a
                        break

                if assignment and is_first_half:
                    css_class = "lecture" if assignment.type == "lecture" else "lab"
                    html += f'<td class="{css_class}" rowspan="2">'
                    html += f'<strong>{assignment.course_code}</strong> - {assignment.course_name}<br>'
                    if assignment.instructor:
                        html += f'<span class="instructor">{assignment.instructor}</span><br>'
                    html += f'<span style="font-size: 8px; color: #666;">Groups: {", ".join(sorted(set([g[:5] for g in assignment.assigned_to])))}</span>'
                    html += '</td>'
                elif not assignment and is_first_half:
                    html += '<td rowspan="2"></td>'

            html += "</tr>"

        html += "</table></div>"

    html += '<h2 style="background-color: #E91E63; color: white; padding: 8px; margin-top: 20px;">Lab Rooms</h2>'
    for room in lab_rooms:
        room_assignments = room_usage[room]
        html += f'<div class="section-table">'
        html += f'<h3 style="background-color: #F06292; padding: 6px;">Room {room}</h3>'
        html += f'<p style="font-size: 9px; color: #666; margin: 5px 0;">{len(room_assignments)} sessions scheduled</p>'
        html += '<table>'
        html += '<tr><th class="time-col">Time</th>'
        
        for day in days:
            html += f"<th>{day}</th>"
        html += "</tr>"

        for time_idx, (time_label, start, end) in enumerate(time_slots_display):
            our_slot = (time_idx // 2) + 1
            is_first_half = (time_idx % 2 == 0)

            html += f'<tr><td class="time-col">{time_label}</td>'

            for day in days:
                assignment = None
                for a in room_assignments:
                    if a.time_slot.day == day and a.time_slot.slot_number == our_slot:
                        assignment = a
                        break

                if assignment and is_first_half:
                    html += '<td class="lab" rowspan="2">'
                    html += f'<strong>{assignment.course_code}</strong> - {assignment.course_name}<br>'
                    if assignment.lab_instructor_name:
                        html += f'<span class="lab-instructor">{assignment.lab_instructor_name}</span><br>'
                    html += f'<span style="font-size: 8px; color: #666;">{assignment.assigned_to[0]}</span>'
                    html += '</td>'
                elif not assignment and is_first_half:
                    html += '<td rowspan="2"></td>'

            html += "</tr>"

        html += "</table></div>"

    # ========== PART 7: LAB INSTRUCTOR TIMETABLES ==========
    html += '<h1 id="lab-instructors" style="background-color: #00BCD4; color: white; padding: 10px; margin-top: 30px;">LAB INSTRUCTOR TIMETABLES</h1>'
    html += '<p style="text-align: center; font-style: italic;">Complete schedule for each lab instructor</p>'

    # Group lab assignments by instructor
    lab_instructors_map = {}
    for assignment in scheduler.assignments:
        if assignment.type == "lab" and assignment.lab_instructor_name:
            if assignment.lab_instructor_name not in lab_instructors_map:
                lab_instructors_map[assignment.lab_instructor_name] = []
            lab_instructors_map[assignment.lab_instructor_name].append(assignment)

    for lab_instructor in sorted(lab_instructors_map.keys()):
        instructor_assignments = lab_instructors_map[lab_instructor]
        html += f'<div class="section-table">'
        html += f'<h2 style="background-color: #00BCD4; color: white; padding: 8px;">{lab_instructor}</h2>'
        html += f'<p style="font-size: 9px; color: #666; margin: 5px 0;">Teaching {len(instructor_assignments)} lab sessions</p>'
        html += '<table>'
        html += '<tr><th class="time-col">Time</th>'
        
        for day in days:
            html += f"<th>{day}</th>"
        html += "</tr>"

        for time_idx, (time_label, start, end) in enumerate(time_slots_display):
            our_slot = (time_idx // 2) + 1
            is_first_half = (time_idx % 2 == 0)

            html += f'<tr><td class="time-col">{time_label}</td>'

            for day in days:
                assignment = None
                for a in instructor_assignments:
                    if a.time_slot.day == day and a.time_slot.slot_number == our_slot:
                        assignment = a
                        break

                if assignment and is_first_half:
                    html += '<td class="lab" rowspan="2">'
                    html += f'<strong>{assignment.course_code}</strong> - {assignment.course_name}<br>'
                    html += f'<span class="room">LAB {assignment.room}</span><br>'
                    html += f'<span style="font-size: 8px; color: #666;">{assignment.assigned_to[0]}</span>'
                    html += '</td>'
                elif not assignment and is_first_half:
                    html += '<td rowspan="2"></td>'

            html += "</tr>"

        html += "</table></div>"

    html += """
    </body>
    </html>
    """

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)

    print(f"HTML timetable exported to {filename}")


# ==================== MAIN EXECUTION ====================

def main():
    """Main execution function"""
    print("=" * 60)
    print("COLLEGE TIMETABLE SCHEDULING SYSTEM WITH LAB INSTRUCTORS")
    print("=" * 60)
    print()

    # Step 1: Load all data
    print("Step 1: Loading data...")
    time_slots = generate_time_slots()
    groups, sections = generate_groups_and_sections()
    rooms = load_rooms_from_csv("rooms.csv")
    lab_instructors = load_lab_instructors_from_csv("inslab.csv")
    level_1_data, level_2_data = load_course_data()

    print(f"  - Time slots: {len(time_slots)}")
    print(f"  - Groups: {len(groups)}")
    print(f"  - Sections: {len(sections)}")
    print(
        f"  - Rooms: {len(rooms)} ({len([r for r in rooms if r.room_type == 'lec'])} lecture, {len([r for r in rooms if r.room_type == 'lab'])} lab)")
    print(f"  - Lab Instructors: {len(lab_instructors)}")
    print(f"  - Level 1 courses: {len(level_1_data['lectures'])} lectures, {len(level_1_data['labs'])} labs")
    print(f"  - Level 2 courses: {len(level_2_data['lectures'])} lectures, {len(level_2_data['labs'])} labs")
    print()

    # Step 2: Initialize scheduler
    print("Step 2: Initializing scheduler...")
    scheduler = TimetableScheduler(rooms, groups, sections, time_slots, level_1_data, level_2_data)
    print()

    # Step 3: Generate schedule
    print("Step 3: Generating timetable...")
    success = scheduler.generate_schedule()
    print()

    if not success:
        print("ERROR: Failed to generate complete timetable!")
        return

    # Step 4: Assign lab instructors
    print("Step 4: Assigning lab instructors...")
    instructor_success = assign_instructors_to_labs(scheduler, lab_instructors)

    if not instructor_success:
        print("ERROR: Failed to assign instructors to all labs!")
        return

    labs_with_instructors = len([a for a in scheduler.assignments if a.type == "lab" and a.lab_instructor_id])
    print(
        f"✓ Lab instructors assigned: {labs_with_instructors}/{len([a for a in scheduler.assignments if a.type == 'lab'])} labs")
    print()

    # Step 5: Validate schedule
    print("Step 5: Validating timetable...")
    is_valid, errors = validate_schedule(scheduler)

    if is_valid:
        print("✓ Timetable is VALID - all constraints satisfied!")
    else:
        print("✗ Timetable has ERRORS:")
        for error in errors:
            print(f"  - {error}")
    print()

    # Step 6: Validate instructor assignments
    print("Step 6: Validating instructor assignments...")
    instructor_valid, instructor_errors = validate_instructor_assignments(scheduler, lab_instructors)

    if instructor_valid:
        print("✓ Instructor assignments are VALID!")
    else:
        print("✗ Instructor assignments have ERRORS:")
        for error in instructor_errors:
            print(f"  - {error}")
    print()

    # Step 7: Generate outputs
    print("Step 7: Generating output files...")
    export_to_csv(scheduler, "timetable_complete.csv")
    export_section_timetables(scheduler, ".")
    export_html_timetable(scheduler, "timetable.html")
    print()

    # # Step 8: Print summary
    # print_summary(scheduler, lab_instructors)

    print("Timetable generation completed successfully!")
    print("\nGenerated files:")
    print("  - timetable_complete.csv (complete timetable with instructors)")
    print("  - timetable_L*-G*-S*.csv (individual section timetables)")
    print("  - timetable.html (visual HTML timetable with lab instructors)")


if __name__ == "__main__":
    main()
