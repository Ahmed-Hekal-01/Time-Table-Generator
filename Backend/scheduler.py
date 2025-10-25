"""
Timetable scheduling algorithm
"""

import random
from typing import List
from collections import defaultdict
from models import Room, Group, Section, TimeSlot, Lecture, Lab, Assignment
from trackers import ScheduleTracker


class TimetableScheduler:
    """Main scheduler class for generating timetables"""

    def __init__(self, rooms: List[Room], groups: List[Group], sections: List[Section],
                 time_slots: List[TimeSlot], level_1_data: dict, level_2_data: dict, lab_instructors: List = None):
        self.rooms = rooms
        self.groups = groups
        self.sections = sections
        self.time_slots = time_slots
        self.level_1_data = level_1_data
        self.level_2_data = level_2_data
        self.lab_instructors = lab_instructors or []

        self.tracker = ScheduleTracker()
        self.assignments: List[Assignment] = []
        self.assignment_counter = 0

        # Separate rooms by type
        self.lec_rooms = [r for r in rooms if r.room_type == "lec"]
        self.lab_rooms = [r for r in rooms if r.room_type == "lab"]

        # Calculate instructor limits dynamically from lab_instructors
        self.course_instructor_limits = self._calculate_instructor_limits()

    def _calculate_instructor_limits(self) -> dict:
        """Calculate the number of qualified instructors for each course"""
        from collections import defaultdict
        course_counts = defaultdict(int)

        for instructor in self.lab_instructors:
            for course_code in instructor.qualified_labs:
                course_counts[course_code] += 1

        return dict(course_counts)

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
        course_time_slot_count = defaultdict(lambda: defaultdict(int))

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
                    # Use calculated limit, or default to 2 (conservative) if course not found
                    max_instructors = self.course_instructor_limits.get(lab.course_code, 2)

                    # Don't schedule more labs than available instructors
                    if current_count >= max_instructors:
                        # Debug: uncomment to see when limits are hit
                        # print(f"  Skipping {time_slot.day} slot {time_slot.slot_number} for {lab.course_code}: {current_count}/{max_instructors} instructors used")
                        continue

                    # Determine which room to use
                    available_room = None

                    # If lab has a specific room, use ONLY that room
                    if lab.room_code and lab.room_code.strip():
                        if self.tracker.is_room_available(lab.room_code,
                                                        time_slot.day,
                                                        time_slot.slot_number):
                            available_room = lab.room_code
                    else:
                        # Find any available lab room
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
                    print(f"  Course {lab.course_code} distribution:")
                    time_slots_used = [(day, slot, count) for (day, slot), count in
                                    course_time_slot_count[lab.course_code].items() if count > 0]
                    for day, slot, count in sorted(time_slots_used)[:5]:
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
        print(f"Level 1 labs scheduled: {len([a for a in self.assignments if a.type == 'lab' and any('L1' in x for x in a.assigned_to)])}")

        # Schedule Level 2 labs
        print("Scheduling Level 2 labs...")
        if not self.schedule_labs(2, self.level_2_data['labs']):
            print("Failed to schedule Level 2 labs")
            return False
        print(f"Total labs scheduled: {len([a for a in self.assignments if a.type == 'lab'])}")

        print(f"\nTotal assignments: {len(self.assignments)}")
        return True
