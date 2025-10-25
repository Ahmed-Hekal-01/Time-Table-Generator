"""
Constraint checking functions for scheduling
"""

from typing import Tuple
from models import LabInstructor, Assignment
from trackers import InstructorTracker, ScheduleTracker


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
