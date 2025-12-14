/**
 * Types for /api/professors and /api/professors/<professor_name> endpoints
 */

import type { Metadata } from './common';

export interface ProfessorLecture {
  day: string;
  slot: number;
  time: string;
  course_code: string;
  course_name: string;
  room: string;
  groups: string[];
}

export interface ProfessorData {
  professor_name: string;
  lectures: ProfessorLecture[];
}

export interface ProfessorsResponse {
  metadata: Metadata;
  professors: {
    [professorName: string]: ProfessorData;
  };
}
