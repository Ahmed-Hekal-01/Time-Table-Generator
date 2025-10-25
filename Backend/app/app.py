"""
Main execution script for College Timetable Scheduling System
"""

from .data_loader import (
    generate_time_slots,
    generate_groups_and_sections,
    load_rooms_from_csv,
    load_lab_instructors_from_csv,
    load_course_data
)
from .scheduler import TimetableScheduler
from .instructor_assignment import assign_instructors_to_labs
from .validators import validate_schedule, validate_instructor_assignments
from .exporters import export_to_csv, export_section_timetables, export_json_timetable


def main():
    """Main execution function"""
    print("=" * 60)
    print("COLLEGE TIMETABLE SCHEDULING SYSTEM WITH LAB INSTRUCTORS")
    print("=" * 60)
    print()

        # Step 1: Load all data
    print("Step 1: Loading data...")
    try:
        time_slots = generate_time_slots()
        groups, sections = generate_groups_and_sections()
        rooms = load_rooms_from_csv("/home/taqsiim/dev/Time-Table-Generator/Backend/CSV/rooms.csv")
        lab_instructors = load_lab_instructors_from_csv("/home/taqsiim/dev/Time-Table-Generator/Backend/CSV/inslab.csv")
        level_1_data, level_2_data = load_course_data()
    except FileNotFoundError as e:
        print(f"ERROR: Could not load required CSV file: {e}")
        return
    except Exception as e:
        print(f"ERROR: Failed to load data: {e}")
        return


    print(f"  - Time slots: {len(time_slots)}")
    print(f"  - Groups: {len(groups)}")
    print(f"  - Sections: {len(sections)}")
    print(f"  - Rooms: {len(rooms)} ({len([r for r in rooms if r.room_type == 'lec'])} lecture, {len([r for r in rooms if r.room_type == 'lab'])} lab)")
    print(f"  - Lab Instructors: {len(lab_instructors)}")
    print(f"  - Level 1 courses: {len(level_1_data['lectures'])} lectures, {len(level_1_data['labs'])} labs")
    print(f"  - Level 2 courses: {len(level_2_data['lectures'])} lectures, {len(level_2_data['labs'])} labs")
    print()

    # Try up to 5 times to generate a valid schedule with instructors assigned
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            print(f"\n{'=' * 60}")
            print(f"Retry attempt {attempt}/{max_attempts}...")
            print(f"{'=' * 60}\n")

        # Step 2: Initialize scheduler
        print("Step 2: Initializing scheduler...")
        scheduler = TimetableScheduler(rooms, groups, sections, time_slots, level_1_data, level_2_data, lab_instructors)
        print()

        # Step 3: Generate schedule
        print("Step 3: Generating timetable...")
        success = scheduler.generate_schedule()
        print()

        if not success:
            print("ERROR: Failed to generate complete timetable!")
            if attempt < max_attempts:
                continue
            else:
                return

        # Step 4: Assign lab instructors
        print("Step 4: Assigning lab instructors...")
        instructor_success = assign_instructors_to_labs(scheduler, lab_instructors)

        if not instructor_success:
            print("ERROR: Failed to assign instructors to all labs!")
            if attempt < max_attempts:
                continue
            else:
                return

        # Success! Break out of retry loop
        break

    labs_with_instructors = len([a for a in scheduler.assignments if a.type == "lab" and a.lab_instructor_id])
    print(f"✓ Lab instructors assigned: {labs_with_instructors}/{len([a for a in scheduler.assignments if a.type == 'lab'])} labs")
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
    export_to_csv(scheduler, "./Backend/generated/timetable_complete.csv")
    export_section_timetables(scheduler, "./Backend/generated")
    export_json_timetable(scheduler, "./Backend/generated/timetable.json")
    print()

    print("Timetable generation completed successfully!")
    print("\nGenerated files:")
    print("  - timetable_complete.csv (complete timetable with instructors)")
    print("  - timetable_L*-G*-S*.csv (individual section timetables)")
    print("  - timetable.json (structured JSON timetable with all data)")


if __name__ == "__main__":
    main()
