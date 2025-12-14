/**
 * Types for utility API endpoints
 */

export interface HealthResponse {
  status: 'ok' | 'error';
  scheduler_initialized: boolean;
  assignments: number;
}

export interface RegenerateResponse {
  status: 'success' | 'error';
  message: string;
  assignments?: number;
}

export interface ProfessorListResponse {
  professors: string[];
}

export interface LabInstructorListResponse {
  lab_instructors: string[];
}

export interface ApiError {
  error: string;
}
