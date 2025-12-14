/**
 * Types for /api/rooms and /api/rooms/<room_id> endpoints
 */

import type { Metadata, AssignmentType } from './common';

export interface RoomAssignment {
  day: string;
  slot: number;
  time: string;
  type: AssignmentType;
  course_code: string;
  course_name: string;
  instructor: string;
  assigned_to: string[];
}

export interface RoomData {
  room_name: string;
  room_type: 'lec' | 'lab';
  schedule: RoomAssignment[];
}

export interface RoomsResponse {
  metadata: Metadata;
  rooms: {
    [roomName: string]: RoomData;
  };
}

export interface RoomInfo {
  room_code: string;
  room_type: 'lec' | 'lab';
}

export interface RoomListResponse {
  rooms: RoomInfo[];
  total_count: number;
  lecture_rooms: number;
  lab_rooms: number;
}
