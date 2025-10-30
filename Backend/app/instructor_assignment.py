"""
Lab instructor assignment logic
"""

from typing import List
from collections import defaultdict
from .models import LabInstructor
from .scheduler import TimetableScheduler
from .trackers import InstructorTracker
from .constraints import can_assign_instructor_to_lab


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
    all_lab_assignments = [a for a in scheduler.assignments if a.type == "lab"]
    
    # Separate already assigned labs from unassigned ones
    already_assigned = [a for a in all_lab_assignments if a.lab_instructor_id]
    lab_assignments = [a for a in all_lab_assignments if not a.lab_instructor_id]

    print(f"\nDebug: Total lab assignments: {len(all_lab_assignments)}")
    print(f"Debug: Already assigned during scheduling: {len(already_assigned)}")
    print(f"Debug: Remaining to assign: {len(lab_assignments)}")
    
    # Register already assigned instructors in the tracker
    for lab in already_assigned:
        instructor_tracker.assign(
            lab.lab_instructor_id,
            lab.time_slot.day,
            lab.time_slot.slot_number,
            lab.assignment_id,
            session_hours
        )

    # Sort remaining labs by constraint difficulty (fewer qualified instructors = harder to assign)
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
            print(f"WARNING: Cannot assign instructor to {lab_assignment.course_code} "
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

            # Leave lab unassigned but continue with others
            print(f"  → Leaving {lab_assignment.course_code} unassigned and continuing...")

    # Return True even if some labs couldn't be assigned
    # This allows the timetable to be generated with most labs assigned
    unassigned_count = sum(1 for lab in lab_assignments if not lab.lab_instructor_name)
    print(f"\n✓ Lab instructor assignment complete: {len(lab_assignments) - unassigned_count}/{len(lab_assignments)} labs assigned")
    if unassigned_count > 0:
        print(f"  Warning: {unassigned_count} labs remain unassigned due to scheduling conflicts")
    
    return True
