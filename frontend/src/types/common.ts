/**
 * Common types used across all API endpoints
 */

export interface TimeSlot {
  slot: number;
  time: string;
}

export interface Metadata {
  days: string[];
  time_slots: TimeSlot[];
}

export type AssignmentType = 'lecture' | 'lab';

export const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"] as const;
export const TIME_SLOTS: TimeSlot[] = [
  { slot: 1, time: "9:00-10:30" },
  { slot: 2, time: "10:45-12:15" },
  { slot: 3, time: "12:30-14:00" },
  { slot: 4, time: "14:15-15:45" }
] as const;
