import type { TimeSlot } from '../types/common';

interface Assignment {
  day: string;
  slot: number;
  time: string;
  course_code: string;
  course_name: string;
  room: string;
  instructor?: string;
  lab_instructor_name?: string;
  type?: string;
  sections?: string[];
  groups?: string[];
  assigned_to?: string[];
}

interface TimetableProps {
  type: 'professor' | 'student' | 'room' | 'lab-instructor' | 'section' | 'group';
  title: string;
  subtitle?: string;
  schedule: Record<string, Record<number, Assignment | null>>;
  days?: string[];
  timeSlots?: TimeSlot[];
  headerColor?: string;
}

const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];
const TIME_SLOTS: TimeSlot[] = [
  { slot: 1, time: "9:00-10:30" },
  { slot: 2, time: "10:45-12:15" },
  { slot: 3, time: "12:30-14:00" },
  { slot: 4, time: "14:15-15:45" }
];

const Timetable = ({
  type,
  title,
  subtitle,
  schedule,
  days = DAYS,
  timeSlots = TIME_SLOTS
}: TimetableProps) => {

  const renderCellContent = (assignment: Assignment) => {
    switch (type) {
      case 'professor':
        return (
          <div style={{ fontSize: '0.8rem', lineHeight: '1.4' }}>
            <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '4px' }}>
              {assignment.course_name}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {assignment.course_code}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {assignment.room}
            </div>
          </div>
        );

      case 'student':
      case 'section':
        const isLab = assignment.type === 'lab';
        const instructorName = assignment.instructor;
        return (
          <div style={{ fontSize: '0.8rem', lineHeight: '1.4' }}>
            <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '4px' }}>
              {assignment.course_name}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {instructorName}, {isLab ? 'Lab' : assignment.room}
            </div>
          </div>
        );

      case 'room':
        return (
          <div style={{ fontSize: '0.8rem', lineHeight: '1.4' }}>
            <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '4px' }}>
              {assignment.course_name}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {assignment.instructor}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {assignment.assigned_to?.join(', ')}
            </div>
          </div>
        );

      case 'lab-instructor':
        return (
          <div style={{ fontSize: '0.8rem', lineHeight: '1.4' }}>
            <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '4px' }}>
              {assignment.course_name}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {assignment.room}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {assignment.sections?.join(', ')}
            </div>
          </div>
        );

      case 'group':
        return (
          <div style={{ fontSize: '0.8rem', lineHeight: '1.4' }}>
            <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '4px' }}>
              {assignment.course_name}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {assignment.room}
            </div>
            <div style={{ color: '#666', fontSize: '0.75rem' }}>
              {assignment.instructor}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const getCellClassName = (assignment: Assignment | null) => {
    if (!assignment) return '';
    if (type === 'lab-instructor') return 'lab';
    return assignment.type === 'lecture' ? 'lecture' : 'lab';
  };

  const getCellStyle = (assignment: Assignment | null) => {
    if (!assignment) {
      return {
        border: '1px solid #ddd',
        backgroundColor: '#fff',
        padding: '12px'
      };
    }

    const baseStyle = {
      border: '1px solid #ddd',
      padding: '12px',
      verticalAlign: 'top' as const,
      backgroundColor: '#fff'
    };

    // Different background colors for lectures vs labs
    if (type === 'lab-instructor') {
      return { ...baseStyle, backgroundColor: '#fff3e0' };
    }

    if (assignment.type === 'lab') {
      return { ...baseStyle, backgroundColor: '#fff3e0' }; // Light orange for labs
    }

    return { ...baseStyle, backgroundColor: '#e8f5e9' }; // Light green for lectures
  };

  return (
    <div style={{ marginBottom: '30px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Title Header with Red Background */}
      <div style={{
        backgroundColor: '#8B0000',
        color: 'white',
        padding: '15px 20px',
        fontSize: '1.1rem',
        fontWeight: 'bold',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderTopLeftRadius: '8px',
        borderTopRightRadius: '8px'
      }}>
        <div>
          <span style={{ fontSize: '0.85rem', opacity: 0.9, marginRight: '15px' }}>School Level</span>
          <span>{title}</span>
        </div>
        {subtitle && <span style={{ fontSize: '0.9rem', opacity: 0.85 }}>({subtitle})</span>}
      </div>

      {/* Table */}
      <table style={{
        borderCollapse: 'collapse',
        width: '100%',
        fontSize: '0.85rem',
        backgroundColor: '#fff',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <thead>
          <tr>
            <th rowSpan={2} style={{
              background: '#8B0000',
              color: 'white',
              padding: '15px 10px',
              width: '120px',
              border: '1px solid #6B0000',
              fontWeight: 'bold'
            }}>
              Time/Day
            </th>
            {/* Group Headers (G1, G2, G3) - Only for student view */}
            {type === 'student' ? (
              days.slice(0, 3).map((_, idx) => (
                <th key={`G${idx + 1}`} colSpan={3} style={{
                  background: '#8B0000',
                  color: 'white',
                  padding: '12px',
                  border: '1px solid #6B0000',
                  fontWeight: 'bold',
                  fontSize: '1rem'
                }}>
                  G{idx + 1}
                </th>
              ))
            ) : (
              days.map((day) => (
                <th key={day} style={{
                  background: '#8B0000',
                  color: 'white',
                  padding: '12px',
                  border: '1px solid #6B0000',
                  minWidth: '150px'
                }}>
                  {day}
                </th>
              ))
            )}
          </tr>
          {/* Section Headers (Sec A, Sec B, Sec C) - Only for student view */}
          {type === 'student' && (
            <tr>
              {days.slice(0, 3).map((_, groupIdx) =>
                ['A', 'B', 'C'].map((sec) => (
                  <th key={`${groupIdx}-${sec}`} style={{
                    background: '#8B0000',
                    color: 'white',
                    padding: '10px',
                    border: '1px solid #6B0000',
                    fontWeight: 'normal',
                    fontSize: '0.9rem'
                  }}>
                    Sec {sec}
                  </th>
                ))
              )}
            </tr>
          )}
        </thead>
        <tbody>
          {timeSlots.map(slot => (
            <tr key={slot.slot}>
              <td style={{
                fontSize: '0.85rem',
                textAlign: 'center',
                fontWeight: 'bold',
                backgroundColor: '#f8f8f8',
                border: '1px solid #ddd',
                padding: '15px 10px',
                color: '#333'
              }}>
                {slot.time}
              </td>
              {days.map(day => {
                const assignment = schedule[day]?.[slot.slot];
                return (
                  <td
                    key={day}
                    className={getCellClassName(assignment)}
                    style={{
                      ...getCellStyle(assignment),
                      minHeight: '80px',
                      verticalAlign: 'middle'
                    }}
                  >
                    {assignment && renderCellContent(assignment)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Timetable;
