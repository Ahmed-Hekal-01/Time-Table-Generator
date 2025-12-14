# Quick Reference: Dynamic Timetable System

## Component Usage

### Timetable Component Props

```typescript
interface TimetableProps {
  type: 'professor' | 'student' | 'room' | 'lab-instructor' | 'section';
  title: string;                    // Main header title
  subtitle?: string;                 // Optional subtitle (e.g., "8 lectures")
  schedule: Record<string, Record<number, Assignment | null>>;
  days?: string[];                   // Optional, defaults to Sun-Thu
  timeSlots?: TimeSlot[];           // Optional, defaults to 4 slots
  headerColor?: string;              // Optional, defaults to #673AB7
}
```

### Schedule Data Structure

```typescript
const schedule = {
  "Sunday": {
    1: { /* assignment data */ },
    2: null,  // empty slot
    3: { /* assignment data */ },
    4: null
  },
  "Monday": { /* ... */ },
  // ... more days
};
```

## View Types & Their Data

### Professor View
```typescript
type="professor"
// Shows: course_code, course_name, room, groups
// Color: Custom (recommend purple #9C27B0)
```

### Student/Section View
```typescript
type="student"
// Shows: course_code, course_name, instructor, room, type (LEC/LAB)
// Color: Custom (recommend green #4CAF50)
// Labs are red-tinted, lectures blue-tinted
```

### Lab Instructor View
```typescript
type="lab-instructor"
// Shows: course_code, course_name, room, sections
// Color: Custom (recommend orange-red #FF5722)
```

### Room View
```typescript
type="room"
// Shows: course_code, course_name, instructor, assigned_to
// Color: Custom (blue for lecture rooms, red for labs)
```

## Type Imports

```typescript
// Import all from index
import type {
  LevelsResponse,
  ProfessorsResponse,
  RoomsResponse
} from '../types';

// Or import from specific files
import type { ProfessorData } from '../types/professors';
```

## API Endpoints

| Endpoint | Response Type | View |
|----------|--------------|------|
| `/api/levels` | `LevelsResponse` | Student |
| `/api/professors` | `ProfessorsResponse` | Prof |
| `/api/lab-instructors` | `LabInstructorsResponse` | TA |
| `/api/rooms` | `RoomsResponse` | Admin |

## Color Scheme

- **Lectures**: `#e3f2fd` (light blue)
- **Labs**: `#ffebee` (light red)
- **Lecture Rooms**: `#1976d2` (blue)
- **Lab Rooms**: `#d32f2f` (red)
- **Students**: `#4CAF50` (green)
- **Professors**: `#9C27B0` (purple)
- **Lab Instructors**: `#FF5722` (orange-red)
- **Admin/Rooms**: `#FF9800` (orange)

## Common Patterns

### Fetch Data
```typescript
const [data, setData] = useState<ResponseType | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  fetch('http://localhost:5000/api/endpoint')
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    })
    .then((data: ResponseType) => {
      setData(data);
      setLoading(false);
    })
    .catch(err => {
      setError(err.message);
      setLoading(false);
    });
}, []);
```

### Build Schedule
```typescript
const buildSchedule = (data: DataType) => {
  const schedule: Record<string, Record<number, any>> = {};
  const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];

  days.forEach(day => {
    schedule[day] = { 1: null, 2: null, 3: null, 4: null };
  });

  data.items.forEach(item => {
    schedule[item.day][item.slot] = item;
  });

  return schedule;
};
```

### Render Pattern
```typescript
if (loading) return <Loader />;
if (error) return <div>Error: {error}</div>;
if (!data) return <div>No data</div>;

return (
  <div>
    {Object.entries(data.items).map(([key, value]) => (
      <Timetable
        key={key}
        type="view-type"
        title={key}
        schedule={buildSchedule(value)}
        headerColor="#color"
      />
    ))}
  </div>
);
```
