import type { GroupData } from '../types/levels';

interface LevelTimetableProps {
  levelName: string;
  groups: GroupData[];
}

const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];
const TIME_SLOTS = [
  { slot: 1, time: "9:00-10:30" },
  { slot: 2, time: "10:45-12:15" },
  { slot: 3, time: "12:30-14:00" },
  { slot: 4, time: "14:15-15:45" }
];

const LevelTimetable = ({ levelName, groups }: LevelTimetableProps) => {
  // Helper to find assignment for a specific slot and section
  const getAssignment = (day: string, slot: number, group: GroupData, sectionId: string) => {
    // Check for Lecture (Group-wide)
    const lecture = group.lectures.find(l => l.day === day && l.slot === slot);
    if (lecture) return { ...lecture, type: 'lecture' };

    // Check for Lab (Section-specific)
    const labs = group.labs_by_section[sectionId] || [];
    const lab = labs.find(l => l.day === day && l.slot === slot);
    if (lab) return { ...lab, type: 'lab' };

    return null;
  };

  const getCellColor = (assignment: any) => {
    if (!assignment) return '#fff';
    return assignment.type === 'lecture' ? '#e8f5e9' : '#fff3e0';
  };

  return (
    <div style={{ padding: '20px', overflowX: 'auto' }}>
      <div style={{
        backgroundColor: '#8B0000',
        color: 'white',
        padding: '15px',
        fontSize: '1.5rem',
        fontWeight: 'bold',
        textAlign: 'center',
        marginBottom: '20px',
        borderRadius: '8px'
      }}>
        {levelName} Timetable
      </div>

      <table style={{
        borderCollapse: 'collapse',
        width: '100%',
        minWidth: '1200px',
        backgroundColor: 'white',
        color: '#333', // Override global white text
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <thead>
          {/* Row 1: Groups */}
          <tr>
            <th rowSpan={2} style={{ border: '1px solid #ddd', padding: '10px', backgroundColor: '#f5f5f5', width: '100px' }}>Day</th>
            <th rowSpan={2} style={{ border: '1px solid #ddd', padding: '10px', backgroundColor: '#f5f5f5', width: '120px' }}>Time</th>
            {groups.map(group => (
              <th
                key={group.group_id}
                colSpan={group.sections.length}
                style={{
                  border: '1px solid #ddd',
                  padding: '10px',
                  backgroundColor: '#333',
                  color: 'white'
                }}
              >
                {group.group_id}
              </th>
            ))}
          </tr>
          {/* Row 2: Sections */}
          <tr>
            {groups.map(group =>
              group.sections.map(sectionId => (
                <th
                  key={sectionId}
                  style={{
                    border: '1px solid #ddd',
                    padding: '8px',
                    backgroundColor: '#555',
                    color: 'white',
                    fontSize: '0.9rem'
                  }}
                >
                  {sectionId.split('-').pop()} {/* Show only S1, S2 etc */}
                </th>
              ))
            )}
          </tr>
        </thead>
        <tbody>
          {DAYS.map(day => (
            TIME_SLOTS.map((slot, slotIndex) => (
              <tr key={`${day}-${slot.slot}`}>
                {/* Day Column (Spans 4 rows) */}
                {slotIndex === 0 && (
                  <td
                    rowSpan={4}
                    style={{
                      border: '1px solid #ddd',
                      padding: '10px',
                      fontWeight: 'bold',
                      backgroundColor: '#f9f9f9',
                      textAlign: 'center',
                      verticalAlign: 'middle'
                    }}
                  >
                    {day}
                  </td>
                )}

                {/* Time Slot Column */}
                <td style={{
                  border: '1px solid #ddd',
                  padding: '10px',
                  textAlign: 'center',
                  fontSize: '0.9rem',
                  backgroundColor: '#fff'
                }}>
                  {slot.time}
                </td>

                {/* Data Columns */}
                {groups.map(group => {
                  // 1. Check for Graduation Project (Special Case: Spans whole day)
                  const gradProject = group.lectures.find(l =>
                    l.day === day &&
                    l.slot === 1 &&
                    l.course_name.toLowerCase().includes('graduation project')
                  );

                  if (gradProject) {
                    if (slot.slot === 1) {
                      // Render big cell spanning 4 rows (whole day) and all sections
                      return (
                        <td
                          key={`${group.group_id}-grad-project`}
                          colSpan={group.sections.length}
                          rowSpan={4}
                          style={{
                            border: '1px solid #ddd',
                            padding: '8px',
                            backgroundColor: '#e3f2fd', // Light blue for Grad Project
                            textAlign: 'center',
                            verticalAlign: 'middle',
                            fontSize: '0.9rem',
                            fontWeight: 'bold',
                            color: '#0d47a1'
                          }}
                        >
                          <div>
                            <div style={{ marginBottom: '4px', fontSize: '1rem' }}>
                              {gradProject.course_name}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#555' }}>
                              {gradProject.instructor}
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#555' }}>
                              {gradProject.room}
                            </div>
                          </div>
                        </td>
                      );
                    } else {
                      // Skip rendering for slots 2, 3, 4 as they are covered by the rowSpan
                      return null;
                    }
                  }

                  // 2. Normal Logic: Check for regular lecture
                  const groupLecture = group.lectures.find(l => l.day === day && l.slot === slot.slot);

                  if (groupLecture) {
                    // Render merged cell for lecture
                    return (
                      <td
                        key={`${group.group_id}-lecture`}
                        colSpan={group.sections.length}
                        style={{
                          border: '1px solid #ddd',
                          padding: '8px',
                          backgroundColor: '#e8f5e9', // Lecture color
                          textAlign: 'center',
                          verticalAlign: 'middle',
                          fontSize: '0.85rem',
                          height: '80px'
                        }}
                      >
                        <div>
                          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                            {groupLecture.course_name}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#666' }}>
                            {groupLecture.instructor}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#666' }}>
                            {groupLecture.room}
                          </div>
                        </div>
                      </td>
                    );
                  } else {
                    // 3. Render individual cells for sections (Labs or Empty)
                    return group.sections.map(sectionId => {
                      const assignment = getAssignment(day, slot.slot, group, sectionId);
                      // Note: getAssignment will only return Labs here because we already checked for lectures

                      return (
                        <td
                          key={`${group.group_id}-${sectionId}`}
                          style={{
                            border: '1px solid #ddd',
                            padding: '8px',
                            backgroundColor: getCellColor(assignment),
                            textAlign: 'center',
                            verticalAlign: 'middle',
                            fontSize: '0.85rem',
                            height: '80px'
                          }}
                        >
                          {assignment ? (
                            <div>
                              <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                                {assignment.course_name}
                              </div>
                              <div style={{ fontSize: '0.75rem', color: '#666' }}>
                                {(assignment as any).instructor}
                              </div>
                              <div style={{ fontSize: '0.75rem', color: '#666' }}>
                                {assignment.room}
                              </div>
                            </div>
                          ) : null}
                        </td>
                      );
                    });
                  }
                })}
              </tr>
            ))
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LevelTimetable;
