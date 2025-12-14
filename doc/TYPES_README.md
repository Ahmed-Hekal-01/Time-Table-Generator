# TypeScript Type Definitions for Timetable Generator API

This directory contains all TypeScript type definitions for the Timetable Generator API endpoints.

## File Structure

```
types/
├── index.ts              # Main export file - import all types from here
├── common.ts             # Shared types used across endpoints
├── levels.ts             # Types for /api/levels endpoints
├── professors.ts         # Types for /api/professors endpoints
├── labInstructors.ts     # Types for /api/lab-instructors endpoints
├── rooms.ts              # Types for /api/rooms endpoints
└── api.ts                # Types for utility endpoints (health, regenerate, lists)
```

## Usage Examples

### Import all types
```typescript
import {
  LevelsResponse,
  ProfessorsResponse,
  RoomsResponse,
  HealthResponse
} from '@/types';
```

### Import specific types
```typescript
import type { LevelsResponse, GroupData, LectureAssignment } from '@/types/levels';
import type { ProfessorData, ProfessorLecture } from '@/types/professors';
import type { LabInstructorData } from '@/types/labInstructors';
import type { RoomData, RoomListResponse } from '@/types/rooms';
import type { HealthResponse, ApiError } from '@/types/api';
```

### Using types with fetch
```typescript
import type { LevelsResponse } from '@/types/levels';

async function fetchLevels(): Promise<LevelsResponse> {
  const response = await fetch('http://localhost:5000/api/levels');
  const data: LevelsResponse = await response.json();
  return data;
}
```

## API Endpoints Coverage

### Student/Level Views
- **GET** `/api/levels` → `LevelsResponse`
- **GET** `/api/levels/<level_id>` → `LevelsResponse`

### Professor Views
- **GET** `/api/professors` → `ProfessorsResponse`
- **GET** `/api/professors/<name>` → `ProfessorsResponse`

### Lab Instructor Views
- **GET** `/api/lab-instructors` → `LabInstructorsResponse`
- **GET** `/api/lab-instructors/<name>` → `LabInstructorsResponse`

### Room Views
- **GET** `/api/rooms` → `RoomsResponse`
- **GET** `/api/rooms/<room_id>` → `RoomsResponse`

### Utility Endpoints
- **GET** `/api/health` → `HealthResponse`
- **POST** `/api/regenerate` → `RegenerateResponse`
- **GET** `/api/list/professors` → `ProfessorListResponse`
- **GET** `/api/list/lab-instructors` → `LabInstructorListResponse`
- **GET** `/api/list/rooms` → `RoomListResponse`

### Error Responses
All endpoints may return → `ApiError`

## Type Descriptions

### Common Types (`common.ts`)
- `TimeSlot`: Represents a time slot with slot number and time range
- `Metadata`: Contains days and time slots arrays used in responses
- `AssignmentType`: Union type for 'lecture' or 'lab'
- `DAYS`: Constant array of weekday names
- `TIME_SLOTS`: Constant array of time slot objects

### Level Types (`levels.ts`)
- `LectureAssignment`: Lecture assignment details for a group
- `LabAssignment`: Lab assignment details for a section
- `GroupData`: Complete group information including lectures and labs
- `LevelData`: Collection of groups in a level
- `LevelsResponse`: Full response from levels API
- `LevelId`: Type-safe level IDs (1-4)
- `LevelKey`: Type-safe level keys ('Level1'-'Level4')

### Professor Types (`professors.ts`)
- `ProfessorLecture`: Lecture details for a professor
- `ProfessorData`: Complete professor schedule
- `ProfessorsResponse`: Full response from professors API

### Lab Instructor Types (`labInstructors.ts`)
- `LabInstructorLab`: Lab details for an instructor
- `LabInstructorData`: Complete lab instructor schedule
- `LabInstructorsResponse`: Full response from lab instructors API

### Room Types (`rooms.ts`)
- `RoomAssignment`: Assignment details for a room
- `RoomData`: Complete room schedule
- `RoomsResponse`: Full response from rooms API
- `RoomInfo`: Basic room information
- `RoomListResponse`: Response from room list endpoint

### API Utility Types (`api.ts`)
- `HealthResponse`: Health check endpoint response
- `RegenerateResponse`: Regenerate schedule endpoint response
- `ProfessorListResponse`: Professor list endpoint response
- `LabInstructorListResponse`: Lab instructor list endpoint response
- `ApiError`: Standard error response format

## Best Practices

1. **Always use type imports** when importing only types:
   ```typescript
   import type { LevelsResponse } from '@/types/levels';
   ```

2. **Use const assertions** when working with constants:
   ```typescript
   const day: (typeof DAYS)[number] = "Sunday";
   ```

3. **Handle API errors** properly:
   ```typescript
   try {
     const data = await fetch('/api/levels').then(r => r.json());
     if ('error' in data) {
       // Handle ApiError
       console.error(data.error);
     } else {
       // Handle LevelsResponse
       processLevels(data);
     }
   } catch (error) {
     console.error('Network error:', error);
   }
   ```

4. **Type guard functions** for runtime type checking:
   ```typescript
   function isApiError(data: any): data is ApiError {
     return 'error' in data;
   }
   ```
