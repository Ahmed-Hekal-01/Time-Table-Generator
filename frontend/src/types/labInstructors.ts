/**
 * Types for /api/lab-instructors and /api/lab-instructors/<instructor_name> endpoints
 */

import type { Metadata } from './common';

export interface LabInstructorLab {
  day: string;
  slot: number;
  time: string;
  course_code: string;
  course_name: string;
  room: string;
  sections: string[];
}

export interface LabInstructorData {
  instructor_id: string;
  instructor_name: string;
  labs: LabInstructorLab[];
}

export interface LabInstructorsResponse {
  metadata: Metadata;
  instructors: {
    [instructorName: string]: LabInstructorData;
  };
}
