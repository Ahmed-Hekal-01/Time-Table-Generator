"""
Data models for the College Timetable Scheduling System
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TimeSlot:
    """Represents a time slot in the timetable"""
    id: str
    day: str
    slot_number: int
    start_time: str
    end_time: str

    def __hash__(self):
        return hash(self.id)


@dataclass
class Lecture:
    """Represents a lecture course"""
    course_code: str
    course_name: str
    instructor_name: str
    instructor_id: int
    level: int
    is_graduation_project: bool = False


@dataclass
class Lab:
    """Represents a lab course"""
    course_code: str
    course_name: str
    room_code: str
    level: int


@dataclass
class Room:
    """Represents a classroom or lab room"""
    room_code: str
    room_type: str
    capacity: Optional[int] = None
    building: Optional[str] = None


@dataclass
class Section:
    """Represents a section within a group (L1/L2) or department (L3/L4)"""
    section_id: str
    level: int
    group_number: int
    section_number: int
    group_id: str
    department: Optional[str] = None  # For L3/L4: CSC, CNC, BIF, AID


@dataclass
class Group:
    """Represents a group containing multiple sections"""
    group_id: str
    level: int
    group_number: int
    sections: List[Section] = field(default_factory=list)


@dataclass
class Department:
    """Represents a department in L3/L4 (CSC, CNC, BIF, AID)"""
    department_id: str
    department_name: str
    level: int
    sections: List[Section] = field(default_factory=list)


@dataclass
class LabInstructor:
    """Represents a lab instructor/TA"""
    instructor_id: str
    instructor_name: str
    qualified_labs: List[str]  # Course codes the instructor is qualified to teach
    max_hours_per_week: float  # Maximum teaching hours per week
    instructor_type: str = "TA"  # TA, Lab Assistant, etc.
    current_hours: float = 0.0  # Track assigned hours (runtime)


@dataclass
class Assignment:
    """Represents a scheduled assignment (lecture or lab)"""
    assignment_id: str
    type: str  # "lecture" or "lab"
    course_code: str
    course_name: str
    time_slot: TimeSlot
    room: str
    instructor: Optional[str] = None
    instructor_id: Optional[int] = None
    lab_instructor_id: Optional[str] = None
    lab_instructor_name: Optional[str] = None
    assigned_to: List[str] = field(default_factory=list)
