"""
Validation functions for checking schedule constraints
"""

from typing import List, Tuple
from collections import defaultdict
from models import LabInstructor
from scheduler import TimetableScheduler
from trackers import InstructorTracker


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
