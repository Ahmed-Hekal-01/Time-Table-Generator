"""
Tracker classes for managing schedules and constraints
"""

from typing import Dict, Optional, Set, List
from collections import defaultdict
from models import LabInstructor


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


class InstructorTracker:
    """Track lab instructor schedules and workload"""

    def __init__(self):
        # Schedule: instructor_id -> day -> slot_number -> assignment_id
        self.instructor_schedule: Dict[str, Dict[str, Dict[int, str]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: None))
        )

        # Workload: instructor_id -> hours assigned
        self.instructor_hours: Dict[str, float] = defaultdict(float)

        # Instructor pool: instructor_id -> LabInstructor object
        self.instructors: Dict[str, LabInstructor] = {}

    def is_available(self, instructor_id: str, day: str, slot_number: int) -> bool:
        """Check if instructor is free at given time"""
        return self.instructor_schedule[instructor_id][day][slot_number] is None

    def has_capacity(self, instructor_id: str, hours_needed: float) -> bool:
        """Check if instructor has capacity for more hours"""
        instructor = self.instructors.get(instructor_id)
        if not instructor or not instructor.max_hours_per_week:
            return True  # No limit set

        current = self.instructor_hours[instructor_id]
        return (current + hours_needed) <= instructor.max_hours_per_week

    def is_qualified(self, instructor_id: str, course_code: str) -> bool:
        """Check if instructor is qualified to teach this course"""
        instructor = self.instructors.get(instructor_id)
        if not instructor:
            return False
        return course_code in instructor.qualified_labs

    def assign(self, instructor_id: str, day: str, slot_number: int,
               assignment_id: str, hours: float):
        """Assign instructor to a time slot"""
        self.instructor_schedule[instructor_id][day][slot_number] = assignment_id
        self.instructor_hours[instructor_id] += hours

    def unassign(self, instructor_id: str, day: str, slot_number: int, hours: float):
        """Remove instructor assignment (for backtracking)"""
        self.instructor_schedule[instructor_id][day][slot_number] = None
        self.instructor_hours[instructor_id] -= hours
