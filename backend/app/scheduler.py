"""
Timetable scheduling algorithm
"""

import random
from typing import List
from collections import defaultdict
from .models import Room, Group, Section, TimeSlot, Lecture, Lab, Assignment
from .trackers import ScheduleTracker


class TimetableScheduler:
    """Main scheduler class for generating timetables"""

    def __init__(self, rooms: List[Room], groups: List[Group], sections: List[Section],
                 time_slots: List[TimeSlot], level_1_data: dict, level_2_data: dict, 
                 level_3_data: dict, level_4_data: dict, lab_instructors: List = None):
        self.rooms = rooms
        self.groups = groups
        self.sections = sections
        self.time_slots = time_slots
        self.level_1_data = level_1_data
        self.level_2_data = level_2_data
        self.level_3_data = level_3_data
        self.level_4_data = level_4_data
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

    def schedule_department_lectures(self, level: int, department: str, lectures_data: List[dict]) -> bool:
        """Schedule lectures for a specific department (L3/L4)"""
        # Get the department "group" (treated as a group for consistency)
        dept_groups = [g for g in self.groups if g.level == level and department in g.group_id]
        
        if not dept_groups:
            print(f"  Warning: No groups found for Level {level} {department}")
            return True  # Not an error, just no groups
        
        dept_group = dept_groups[0]
        
        for lecture_data in lectures_data:
            lecture = Lecture(**lecture_data)
            
            # Check if this department already has this lecture
            if self.tracker.has_group_taken_lecture(dept_group.group_id, lecture.course_code):
                continue
            
            # Try to find a valid time slot
            success = False
            for time_slot in self.time_slots:
                # Check instructor availability
                if not self.tracker.is_instructor_available(lecture.instructor_id, time_slot.day, time_slot.slot_number):
                    continue
                
                # Check if department (group) is available
                if not self.tracker.is_group_available(dept_group.group_id, time_slot.day, time_slot.slot_number):
                    continue
                
                # Find available lecture room
                available_room = None
                for room in self.lec_rooms:
                    if self.tracker.is_room_available(room.room_code, time_slot.day, time_slot.slot_number):
                        available_room = room.room_code
                        break
                
                if not available_room:
                    continue
                
                # Create assignment
                assignment_id = self.generate_assignment_id()
                assignment = Assignment(
                    assignment_id=assignment_id,
                    type="lecture",
                    course_code=lecture.course_code,
                    course_name=lecture.course_name,
                    time_slot=time_slot,
                    room=available_room,
                    instructor=lecture.instructor_name,
                    instructor_id=lecture.instructor_id,
                    assigned_to=[dept_group.group_id]
                )
                self.assignments.append(assignment)
                
                # Track assignments - correct parameter order
                self.tracker.assign_lecture(
                    assignment_id, lecture.instructor_id, available_room,
                    dept_group.group_id, [s.section_id for s in dept_group.sections], 
                    lecture.course_code, time_slot.day, time_slot.slot_number
                )
                
                success = True
                break
            
            if not success:
                print(f"  Failed to schedule lecture {lecture.course_code} for {department}")
                return False
        
        return True

    def schedule_department_labs(self, level: int, department: str, labs_data: List[dict]) -> bool:
        """Schedule labs for a specific department (L3/L4) - each section gets its own lab
        Instructor-aware scheduling: checks instructor availability to avoid conflicts"""
        # Get sections for this department
        dept_sections = [s for s in self.sections if s.level == level and s.department == department]
        
        if not dept_sections:
            print(f"  Warning: No sections found for Level {level} {department}")
            return True
        
        from collections import defaultdict
        import random
        
        # Track which time slots are used for each course (to spread them out)
        course_time_slot_count = defaultdict(lambda: defaultdict(int))
        
        # Track instructor time slot usage (instructor_id -> set of (day, slot) tuples)
        instructor_schedule = defaultdict(set)
        
        for lab_data in labs_data:
            lab = Lab(**lab_data)
            
            # Get qualified instructors for this lab
            qualified_instructors = [
                inst for inst in self.lab_instructors
                if lab.course_code in inst.qualified_labs
            ]
            
            # Each section needs its own lab session
            for section in dept_sections:
                # Check if section already has this lab
                if self.tracker.has_section_taken_lab(section.section_id, lab.course_code):
                    continue
                
                # Collect all valid time slots first
                valid_slots = []
                for time_slot in self.time_slots:
                    # Skip Saturday for regular labs (reserved for GP)
                    if time_slot.day == "Saturday":
                        continue
                        
                    # Check section availability
                    if not self.tracker.is_section_available(section.section_id, time_slot.day, time_slot.slot_number):
                        continue
                    
                    # Find available lab room
                    available_room = None
                    for room in self.lab_rooms:
                        if self.tracker.is_room_available(room.room_code, time_slot.day, time_slot.slot_number):
                            available_room = room.room_code
                            break
                    
                    if not available_room:
                        continue
                    
                    # INSTRUCTOR-AWARE: Check if at least one qualified instructor is available
                    instructor_available = False
                    for instructor in qualified_instructors:
                        time_key = (time_slot.day, time_slot.slot_number)
                        if time_key not in instructor_schedule[instructor.instructor_id]:
                            instructor_available = True
                            break
                    
                    if instructor_available:
                        # Calculate a score: prefer time slots that are less used for this course
                        usage_count = course_time_slot_count[lab.course_code][(time_slot.day, time_slot.slot_number)]
                        valid_slots.append((time_slot, available_room, usage_count))
                
                if not valid_slots:
                    print(f"  Warning: Could not schedule lab {lab.course_code} for {section.section_id} - no instructor-compatible slots")
                    continue
                
                # Sort by usage count (prefer less-used time slots) with added randomization
                valid_slots.sort(key=lambda x: (x[2], random.random()))
                
                # If there are multiple sections, prefer slots with zero usage
                if len(dept_sections) > 1 and valid_slots[0][2] == 0:
                    unused_slots = [s for s in valid_slots if s[2] == 0]
                    if len(unused_slots) > 1:
                        selected = unused_slots[random.randint(0, len(unused_slots) - 1)]
                        time_slot, available_room, _ = selected
                    else:
                        time_slot, available_room, _ = valid_slots[0]
                else:
                    time_slot, available_room, _ = valid_slots[0]
                
                # Find an available instructor for this time slot
                assigned_instructor = None
                time_key = (time_slot.day, time_slot.slot_number)
                for instructor in qualified_instructors:
                    if time_key not in instructor_schedule[instructor.instructor_id]:
                        assigned_instructor = instructor
                        break
                
                if not assigned_instructor:
                    print(f"  Warning: No instructor available for {lab.course_code} at {time_slot.day} slot {time_slot.slot_number}")
                    continue
                
                # Create assignment with instructor already assigned
                assignment_id = self.generate_assignment_id()
                assignment = Assignment(
                    assignment_id=assignment_id,
                    type="lab",
                    course_code=lab.course_code,
                    course_name=lab.course_name,
                    time_slot=time_slot,
                    room=available_room,
                    assigned_to=[section.section_id],
                    lab_instructor_id=assigned_instructor.instructor_id,
                    lab_instructor_name=assigned_instructor.instructor_name
                )
                self.assignments.append(assignment)
                
                # Track assignment
                self.tracker.assign_lab(
                    assignment_id, available_room, section.section_id,
                    lab.course_code, time_slot.day, time_slot.slot_number
                )
                
                # Mark instructor as busy at this time
                instructor_schedule[assigned_instructor.instructor_id].add(time_key)
                
                # Update usage count
                course_time_slot_count[lab.course_code][(time_slot.day, time_slot.slot_number)] += 1
        
        return True

    def schedule_graduation_project(self, level: int, department: str, gp_lecture: dict) -> bool:
        """Schedule graduation project - takes 4 consecutive slots on one day (full day)"""
        # Get department sections
        dept_sections = [s for s in self.sections if s.level == level and s.department == department]
        
        if not dept_sections:
            return True
        
        dept_group = [g for g in self.groups if g.level == level and department in g.group_id][0]
        lecture = Lecture(**gp_lecture)
        
        # Find a day where all 4 slots are available for this group
        days_to_try = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        
        for day in days_to_try:
            # Get all 4 time slots for this day
            day_slots = [ts for ts in self.time_slots if ts.day == day]
            
            if len(day_slots) != 4:
                continue
            
            # Check if group is available for all 4 slots
            group_available = all(
                self.tracker.is_group_available(dept_group.group_id, ts.day, ts.slot_number)
                for ts in day_slots
            )
            
            if not group_available:
                continue
            
            # Check if instructor is available for all 4 slots
            instructor_available = all(
                self.tracker.is_instructor_available(lecture.instructor_id, ts.day, ts.slot_number)
                for ts in day_slots
            )
            
            if not instructor_available:
                continue
            
            # Find a lecture room available for all 4 slots
            available_room = None
            for room in self.lec_rooms:
                room_available = all(
                    self.tracker.is_room_available(room.room_code, ts.day, ts.slot_number)
                    for ts in day_slots
                )
                if room_available:
                    available_room = room.room_code
                    break
            
            if not available_room:
                continue
            
            # Schedule the graduation project for all 4 slots
            for time_slot in day_slots:
                assignment_id = self.generate_assignment_id()
                assignment = Assignment(
                    assignment_id=assignment_id,
                    type="lecture",
                    course_code=lecture.course_code,
                    course_name=lecture.course_name,
                    time_slot=time_slot,
                    room=available_room,
                    instructor=lecture.instructor_name,
                    instructor_id=lecture.instructor_id,
                    assigned_to=[dept_group.group_id]
                )
                self.assignments.append(assignment)
                
                # Track assignment
                self.tracker.assign_lecture(
                    assignment_id, lecture.instructor_id, available_room,
                    dept_group.group_id, [section.section_id for section in dept_group.sections],
                    lecture.course_code, time_slot.day, time_slot.slot_number
                )
            
            print(f"  ✓ Graduation Project scheduled for {day} (all 4 slots) in room {available_room}")
            return True
        
        print(f"  Error: Could not find a full day available for {department} GP")
        return False

    def generate_schedule(self) -> bool:
        """Main scheduling function - Phased approach: L1/L2 first, then L3/L4 departments"""
        print("Starting timetable generation...")
        print(f"Total time slots available: {len(self.time_slots)}")
        print(f"Lecture rooms: {len(self.lec_rooms)}")
        print(f"Lab rooms: {len(self.lab_rooms)}")
        print()

        # ===== PHASE 1: Foundation Levels (L1 & L2) =====
        print("=" * 60)
        print("PHASE 1: FOUNDATION LEVELS (L1 & L2)")
        print("=" * 60)
        
        # Schedule Level 1 lectures
        print("\nScheduling Level 1 lectures...")
        if not self.schedule_lectures(1, self.level_1_data['lectures']):
            print("Failed to schedule Level 1 lectures")
            return False
        print(f"Level 1 lectures scheduled: {len([a for a in self.assignments if a.type == 'lecture' and any('L1' in x for x in a.assigned_to)])}")

        # Schedule Level 2 lectures
        print("Scheduling Level 2 lectures...")
        if not self.schedule_lectures(2, self.level_2_data['lectures']):
            print("Failed to schedule Level 2 lectures")
            return False
        print(f"Total foundation lectures scheduled: {len([a for a in self.assignments if a.type == 'lecture'])}")

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
        labs_count = len([a for a in self.assignments if a.type == 'lab'])
        print(f"Total foundation labs scheduled: {labs_count}")

        print(f"\n✓ Phase 1 complete: {len(self.assignments)} total assignments")
        
        # ===== PHASE 2: Major Departments (L3 & L4) =====
        print("\n" + "=" * 60)
        print("PHASE 2: MAJOR DEPARTMENTS (L3 & L4)")
        print("=" * 60)
        
        departments = ["CSC", "CNC", "BIF", "AID"]
        
        # Schedule Level 3 departments
        print("\n--- Level 3 Departments ---")
        for dept in departments:
            print(f"\nScheduling Level 3 - {dept} department...")
            
            # Schedule department lectures
            if not self.schedule_department_lectures(3, dept, self.level_3_data[dept]['lectures']):
                print(f"Failed to schedule Level 3 {dept} lectures")
                return False
            
            # Schedule department labs
            if not self.schedule_department_labs(3, dept, self.level_3_data[dept]['labs']):
                print(f"Failed to schedule Level 3 {dept} labs")
                return False
            
            print(f"✓ Level 3 {dept} complete")
        
        # Schedule Level 4 departments (with graduation projects)
        print("\n--- Level 4 Departments (with Graduation Projects) ---")
        for dept in departments:
            print(f"\nScheduling Level 4 - {dept} department...")
            
            # Separate regular lectures from graduation project
            regular_lectures = [l for l in self.level_4_data[dept]['lectures'] if not l.get('is_graduation_project', False)]
            gp_lecture = [l for l in self.level_4_data[dept]['lectures'] if l.get('is_graduation_project', False)]
            
            # Schedule regular lectures first
            if not self.schedule_department_lectures(4, dept, regular_lectures):
                print(f"Failed to schedule Level 4 {dept} lectures")
                return False
            
            # Schedule graduation project (takes whole day - Saturday)
            if gp_lecture:
                if not self.schedule_graduation_project(4, dept, gp_lecture[0]):
                    print(f"Failed to schedule Level 4 {dept} graduation project")
                    return False
            
            # Schedule department labs
            if not self.schedule_department_labs(4, dept, self.level_4_data[dept]['labs']):
                print(f"Failed to schedule Level 4 {dept} labs")
                return False
            
            print(f"✓ Level 4 {dept} complete")
        
        print(f"\n✓ Phase 2 complete!")
        print(f"\n{'='*60}")
        print(f"\nTotal assignments: {len(self.assignments)}")
        return True


