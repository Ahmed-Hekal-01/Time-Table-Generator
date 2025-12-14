/**
 * Types for /api/levels and /api/levels/<level_id> endpoints
 */

import type { Metadata } from './common';

export interface LectureAssignment {
  day: string;
  slot: number;
  time: string;
  course_code: string;
  course_name: string;
  room: string;
  instructor: string;
  type: 'lecture';
  sections: string[];
}

export interface LabAssignment {
  day: string;
  slot: number;
  time: string;
  course_code: string;
  course_name: string;
  room: string;
  instructor: string;
  type: 'lab';
  section: string;
}

export interface GroupData {
  group_id: string;
  sections: string[];
  lectures: LectureAssignment[];
  labs_by_section: {
    [sectionId: string]: LabAssignment[];
  };
}

export interface LevelData {
  [groupId: string]: GroupData;
}

export interface LevelsResponse {
  metadata: Metadata;
  levels: {
    Level1?: LevelData;
    Level2?: LevelData;
    Level3?: LevelData;
    Level4?: LevelData;
  };
}

export type LevelId = 1 | 2 | 3 | 4;
export type LevelKey = 'Level1' | 'Level2' | 'Level3' | 'Level4';
