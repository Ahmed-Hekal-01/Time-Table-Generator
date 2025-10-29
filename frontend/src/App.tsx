import React, { useState, useEffect } from 'react'
import './CSS/index.css'

// Type definitions
interface TimeSlot {
  slot: number;
  time: string;
}

interface Assignment {
  day: string;
  slot: number;
  time: string;
  course_code: string;
  course_name: string;
  room: string;
  instructor?: string;
  type?: string;
  sections?: string[];
  groups?: string[];
  assigned_to?: string[];
  section?: string;
}

interface AllData {
  levels: any;
  professors: any;
  rooms: any;
  labInstructors: any;
}

const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];
const TIME_SLOTS = [
  {slot: 1, time: "9:00-10:30"},
  {slot: 2, time: "10:45-12:15"},
  {slot: 3, time: "12:30-14:00"},
  {slot: 4, time: "14:15-15:45"}
];

function App() {
  const [allData, setAllData] = useState<AllData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [regenerating, setRegenerating] = useState<boolean>(false);
  const [activeView, setActiveView] = useState<string>('levels');

  const API_BASE_URL = 'http://127.0.0.1:5000/api';

  const loadAllData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [levelsRes, profsRes, roomsRes, labInsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/levels`),
        fetch(`${API_BASE_URL}/professors`),
        fetch(`${API_BASE_URL}/rooms`),
        fetch(`${API_BASE_URL}/lab-instructors`)
      ]);

      const levels = await levelsRes.json();
      const professors = await profsRes.json();
      const rooms = await roomsRes.json();
      const labInstructors = await labInsRes.json();

      setAllData({ levels, professors, rooms, labInstructors });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/regenerate`, {
        method: 'POST',
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || `HTTP error! status: ${response.status}`);
      }

      alert(`Success! ${result.message}. Generated ${result.assignments} assignments.`);
      loadAllData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to regenerate timetable');
    } finally {
      setRegenerating(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // Combined Level 1 & 2 Table (like HTML template)
  const renderCombinedLevelTable = () => {
    if (!allData?.levels?.levels) return null;

    const levelsData = allData.levels.levels;
    const level1Groups: any[] = [];
    const level2Groups: any[] = [];

    // Organize Level 1 groups
    Object.keys(levelsData.Level1 || {}).sort().forEach(groupId => {
      const group = levelsData.Level1[groupId];
      level1Groups.push({
        groupId: group.group_id,
        sections: group.sections.sort(),
        lectures: group.lectures || [],
        labs_by_section: group.labs_by_section || {}
      });
    });

    // Organize Level 2 groups
    Object.keys(levelsData.Level2 || {}).sort().forEach(groupId => {
      const group = levelsData.Level2[groupId];
      level2Groups.push({
        groupId: group.group_id,
        sections: group.sections.sort(),
        lectures: group.lectures || [],
        labs_by_section: group.labs_by_section || {}
      });
    });

    const renderGroupCells = (group: any, day: string, slotNumber: number) => {
      const cells: React.JSX.Element[] = [];
      const sectionAssignments: any[] = [];

      // Get assignments for each section
      group.sections.forEach((sectionId: string) => {
        let assignment = null;

        // Check lectures
        const lecture = group.lectures.find((lec: Assignment) => lec.day === day && lec.slot === slotNumber);
        if (lecture) {
          assignment = { type: 'lecture', ...lecture };
        }

        // Check labs
        const labs = group.labs_by_section[sectionId] || [];
        const lab = labs.find((l: Assignment) => l.day === day && l.slot === slotNumber);
        if (lab) {
          assignment = { type: 'lab', ...lab };
        }

        sectionAssignments.push(assignment);
      });

      // Check if all sections have the same lecture
      const firstAssignment = sectionAssignments[0];
      const isSharedLecture = firstAssignment &&
                             firstAssignment.type === 'lecture' &&
                             sectionAssignments.every(a =>
                               a && a.type === 'lecture' &&
                               a.course_code === firstAssignment.course_code
                             );

      if (isSharedLecture) {
        // Merge cells for lecture
        const assignment = firstAssignment;
        cells.push(
          <td key={`${group.groupId}-merged`} className="lecture" colSpan={3} style={{fontSize: '0.7rem', padding: '3px', minWidth: '100px'}}>
            <div style={{fontWeight: 'bold', fontSize: '0.8rem', marginBottom: '2px'}}>{assignment.course_code}</div>
            <div style={{fontSize: '0.7rem', marginBottom: '2px'}}>{assignment.course_name}</div>
            <div style={{color: '#1976d2', fontSize: '0.7rem', marginBottom: '2px'}}>{assignment.instructor}</div>
            <div style={{color: '#666', fontSize: '0.6rem'}}>LEC {assignment.room}</div>
          </td>
        );
      } else {
        // Separate cells for each section
        sectionAssignments.forEach((assignment, idx) => {
          if (assignment) {
            const cssClass = assignment.type === 'lecture' ? 'lecture' : 'lab';
            const roomType = assignment.type === 'lecture' ? 'LEC' : 'LAB';

            cells.push(
              <td key={`${group.groupId}-${idx}`} className={cssClass} style={{fontSize: '0.7rem', padding: '3px', minWidth: '100px'}}>
                <div style={{fontWeight: 'bold', fontSize: '0.8rem', marginBottom: '2px'}}>{assignment.course_code}</div>
                <div style={{fontSize: '0.7rem', marginBottom: '2px'}}>{assignment.course_name}</div>
                <div style={{color: assignment.type === 'lecture' ? '#1976d2' : '#d32f2f', fontSize: '0.7rem', marginBottom: '2px'}}>
                  {assignment.instructor}
                </div>
                <div style={{color: '#666', fontSize: '0.6rem'}}>{roomType} {assignment.room}</div>
              </td>
            );
          } else {
            cells.push(<td key={`${group.groupId}-${idx}`} style={{minWidth: '100px'}}></td>);
          }
        });
      }

      return cells;
    };

    return (
      <div id="combined" className="combined-table">
        <h2 style={{backgroundColor: '#673AB7', color: 'white', padding: '15px', textAlign: 'center', margin: '0'}}>
          📚 LEVEL 1 & LEVEL 2 - COMBINED SCHEDULE
        </h2>
        <table>
          <thead>
            {/* Header Row 1: Day, Time, LEVEL 1, LEVEL 2 */}
            <tr>
              <th className="time-col" rowSpan={3}>Day</th>
              <th className="time-col" rowSpan={3}>Time</th>
              <th colSpan={level1Groups.length * 3} style={{backgroundColor: '#4CAF50', color: 'white', fontSize: '1rem'}}>LEVEL 1</th>
              <th colSpan={level2Groups.length * 3} style={{backgroundColor: '#FF9800', color: 'white', fontSize: '1rem'}}>LEVEL 2</th>
            </tr>

            {/* Header Row 2: Group names */}
            <tr>
              {level1Groups.map(group => (
                <th key={group.groupId} colSpan={3} style={{backgroundColor: '#2196F3', color: 'white'}}>{group.groupId}</th>
              ))}
              {level2Groups.map(group => (
                <th key={group.groupId} colSpan={3} style={{backgroundColor: '#FF5722', color: 'white'}}>{group.groupId}</th>
              ))}
            </tr>

            {/* Header Row 3: Section numbers */}
            <tr>
              {level1Groups.map(group =>
                group.sections.map((sectionId: string) => {
                  const sectionNum = sectionId.split('-S')[1];
                  return <th key={sectionId} style={{fontSize: '0.8rem'}}>S{sectionNum}</th>;
                })
              )}
              {level2Groups.map(group =>
                group.sections.map((sectionId: string) => {
                  const sectionNum = sectionId.split('-S')[1];
                  return <th key={sectionId} style={{fontSize: '0.8rem'}}>S{sectionNum}</th>;
                })
              )}
            </tr>
          </thead>

          <tbody>
            {DAYS.map((day, dayIdx) => {
              let firstSlotOfDay = true;
              return TIME_SLOTS.map((slot, slotIdx) => {
                const borderStyle = (slotIdx === 0 && dayIdx > 0) ? {borderTop: '3px solid #000'} : {};

                return (
                  <tr key={`${day}-${slot.slot}`}>
                    {firstSlotOfDay && (
                      <td
                        className="time-col"
                        rowSpan={TIME_SLOTS.length}
                        style={{fontSize: '0.9rem', fontWeight: 'bold', backgroundColor: '#d0d0d0', ...borderStyle}}
                      >
                        {day}
                        {(firstSlotOfDay = false, null)}
                      </td>
                    )}

                    <td className="time-col" style={{fontSize: '0.8rem', textAlign: 'center', ...borderStyle}}>
                      {slot.time}
                    </td>

                    {level1Groups.map(group => renderGroupCells(group, day, slot.slot))}
                    {level2Groups.map(group => renderGroupCells(group, day, slot.slot))}
                  </tr>
                );
              });
            })}
          </tbody>
        </table>
      </div>
    );
  };

  // Section Timetables (Grid view)
  const renderSectionSchedules = () => {
    if (!allData?.levels?.levels) return null;

    const levelsData = allData.levels.levels;

    return (
      <div id="sections" className="section-schedules">
        <h2 style={{backgroundColor: '#FF9800', color: 'white', padding: '15px', textAlign: 'center', margin: '20px 0 10px 0'}}>
          📋 SECTION TIMETABLES
        </h2>

        {['Level1', 'Level2'].map((levelKey, idx) => {
          const levelNum = idx + 1;
          const groups = levelsData[levelKey];

          return (
            <div key={levelKey}>
              <h3 style={{backgroundColor: '#f0f0f0', padding: '8px'}}>Level {levelNum} - Sections</h3>

              {Object.keys(groups).sort().map(groupId => {
                const group = groups[groupId];

                return group.sections.map((sectionId: string) => (
                  <div key={sectionId} style={{marginBottom: '30px'}}>
                    <div style={{backgroundColor: '#FF9800', color: 'white', padding: '8px', fontSize: '1rem', fontWeight: 'bold'}}>
                      Section: {sectionId}
                    </div>
                    {renderSectionGrid(group, sectionId)}
                  </div>
                ));
              })}
            </div>
          );
        })}
      </div>
    );
  };

  const renderSectionGrid = (group: any, sectionId: string) => {
    // Create schedule grid
    const schedule: any = {};
    DAYS.forEach(day => {
      schedule[day] = {};
      TIME_SLOTS.forEach(slot => {
        schedule[day][slot.slot] = null;
      });
    });

    // Add lectures
    if (group.lectures) {
      group.lectures.forEach((lec: Assignment) => {
        schedule[lec.day][lec.slot] = { type: 'lecture', ...lec };
      });
    }

    // Add labs
    if (group.labs_by_section && group.labs_by_section[sectionId]) {
      group.labs_by_section[sectionId].forEach((lab: Assignment) => {
        schedule[lab.day][lab.slot] = { type: 'lab', ...lab };
      });
    }

    return (
      <table>
        <thead>
          <tr>
            <th className="time-col">Time</th>
            {DAYS.map(day => <th key={day} className="day-col">{day}</th>)}
          </tr>
        </thead>
        <tbody>
          {TIME_SLOTS.map(slot => (
            <tr key={slot.slot}>
              <td className="time-col">{slot.time}</td>
              {DAYS.map(day => {
                const item = schedule[day][slot.slot];
                if (item) {
                  const cssClass = item.type === 'lecture' ? 'lecture' : 'lab';
                  return (
                    <td key={day} className={cssClass}>
                      <span className="course-code">{item.course_code}</span>
                      <span className="course-name">{item.course_name}</span>
                      {item.type === 'lecture' ? (
                        <>
                          <span className="instructor">{item.instructor}</span>
                          <span className="room">LEC {item.room}</span>
                        </>
                      ) : (
                        <>
                          <span className="lab-instructor">{item.instructor || 'N/A'}</span>
                          <span className="room">LAB {item.room}</span>
                        </>
                      )}
                    </td>
                  );
                } else {
                  return <td key={day}></td>;
                }
              })}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  // Professor Schedules
  const renderProfessors = () => {
    if (!allData?.professors?.professors) return null;

    const professors = allData.professors.professors;

    return (
      <div id="professors" className="professor-schedules">
        <h2 style={{backgroundColor: '#9C27B0', color: 'white', padding: '15px', textAlign: 'center', margin: '0 0 10px 0'}}>
          👨‍🏫 PROFESSOR TIMETABLES
        </h2>

        {Object.keys(professors).sort().map(profName => {
          const prof = professors[profName];

          // Create schedule grid
          const schedule: any = {};
          DAYS.forEach(day => {
            schedule[day] = {};
            TIME_SLOTS.forEach(slot => {
              schedule[day][slot.slot] = null;
            });
          });

          prof.lectures.forEach((lec: Assignment) => {
            schedule[lec.day][lec.slot] = lec;
          });

          return (
            <div key={profName} style={{marginBottom: '30px'}}>
              <div style={{backgroundColor: '#9C27B0', color: 'white', padding: '8px', fontSize: '1rem', fontWeight: 'bold'}}>
                Prof. {profName}
              </div>
              <table>
                <thead>
                  <tr>
                    <th className="time-col">Time</th>
                    {DAYS.map(day => <th key={day} className="day-col">{day}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {TIME_SLOTS.map(slot => (
                    <tr key={slot.slot}>
                      <td className="time-col" style={{fontSize: '0.8rem', textAlign: 'center'}}>{slot.time}</td>
                      {DAYS.map(day => {
                        const item = schedule[day][slot.slot];
                        if (item) {
                          return (
                            <td key={day} className="lecture" style={{fontSize: '0.7rem', padding: '3px'}}>
                              <div style={{fontWeight: 'bold', fontSize: '0.8rem', marginBottom: '2px'}}>{item.course_code}</div>
                              <div style={{fontSize: '0.7rem', marginBottom: '2px'}}>{item.course_name}</div>
                              <div style={{color: '#666', fontSize: '0.6rem'}}>LEC {item.room}</div>
                              <div style={{fontSize: '0.6rem', color: '#666'}}>Groups: {item.groups.join(', ')}</div>
                            </td>
                          );
                        } else {
                          return <td key={day}></td>;
                        }
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })}
      </div>
    );
  };

  // Room Schedules
  const renderRooms = () => {
    if (!allData?.rooms?.rooms) return null;

    const rooms = allData.rooms.rooms;
    const lecRooms: any[] = [];
    const labRooms: any[] = [];

    Object.keys(rooms).sort().forEach(roomName => {
      const room = rooms[roomName];
      if (room.room_type === 'lec') {
        lecRooms.push({name: roomName, ...room});
      } else {
        labRooms.push({name: roomName, ...room});
      }
    });

    const renderRoomGrid = (room: any) => {
      const schedule: any = {};
      DAYS.forEach(day => {
        schedule[day] = {};
        TIME_SLOTS.forEach(slot => {
          schedule[day][slot.slot] = null;
        });
      });

      room.schedule.forEach((item: Assignment) => {
        schedule[item.day][item.slot] = item;
      });

      return (
        <div key={room.name} style={{marginBottom: '30px'}}>
          <div style={{backgroundColor: '#FF5722', color: 'white', padding: '8px', fontSize: '1rem', fontWeight: 'bold'}}>
            Room: {room.name} ({room.room_type.toUpperCase()})
          </div>
          <table>
            <thead>
              <tr>
                <th className="time-col">Time</th>
                {DAYS.map(day => <th key={day} className="day-col">{day}</th>)}
              </tr>
            </thead>
            <tbody>
              {TIME_SLOTS.map(slot => (
                <tr key={slot.slot}>
                  <td className="time-col" style={{fontSize: '0.8rem', textAlign: 'center'}}>{slot.time}</td>
                  {DAYS.map(day => {
                    const item = schedule[day][slot.slot];
                    if (item) {
                      const cssClass = item.type === 'lecture' ? 'lecture' : 'lab';
                      return (
                        <td key={day} className={cssClass} style={{fontSize: '0.7rem', padding: '3px'}}>
                          <div style={{fontWeight: 'bold', fontSize: '0.8rem', marginBottom: '2px'}}>{item.course_code}</div>
                          <div style={{fontSize: '0.7rem', marginBottom: '2px'}}>{item.course_name}</div>
                          <div style={{color: item.type === 'lecture' ? '#1976d2' : '#d32f2f', fontSize: '0.7rem', marginBottom: '2px'}}>
                            {item.instructor}
                          </div>
                          <div style={{fontSize: '0.6rem', color: '#666'}}>{item.assigned_to.join(', ')}</div>
                        </td>
                      );
                    } else {
                      return <td key={day}></td>;
                    }
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    };

    return (
      <div id="rooms" className="room-schedules">
        <h2 style={{backgroundColor: '#FF5722', color: 'white', padding: '15px', textAlign: 'center', margin: '0 0 10px 0'}}>
          🚪 ROOM TIMETABLES
        </h2>

        <h3 style={{backgroundColor: '#f0f0f0', padding: '8px', margin: '10px 0'}}>Lecture Rooms</h3>
        {lecRooms.map(room => renderRoomGrid(room))}

        <h3 style={{backgroundColor: '#f0f0f0', padding: '8px'}}>Lab Rooms</h3>
        {labRooms.map(room => renderRoomGrid(room))}
      </div>
    );
  };

  // Lab Instructor Schedules
  const renderLabInstructors = () => {
    if (!allData?.labInstructors?.instructors) return null;

    const instructors = allData.labInstructors.instructors;

    return (
      <div id="lab-instructors" className="lab-instructor-schedules">
        <h2 style={{backgroundColor: '#00BCD4', color: 'white', padding: '15px', textAlign: 'center', margin: '0 0 10px 0'}}>
          🔬 LAB INSTRUCTOR TIMETABLES
        </h2>

        {Object.keys(instructors).sort().map(instName => {
          const inst = instructors[instName];

          const schedule: any = {};
          DAYS.forEach(day => {
            schedule[day] = {};
            TIME_SLOTS.forEach(slot => {
              schedule[day][slot.slot] = null;
            });
          });

          inst.labs.forEach((lab: Assignment) => {
            schedule[lab.day][lab.slot] = lab;
          });

          return (
            <div key={instName} style={{marginBottom: '30px'}}>
              <div style={{backgroundColor: '#00BCD4', color: 'white', padding: '8px', fontSize: '1rem', fontWeight: 'bold'}}>
                {instName} ({inst.labs.length} lab sessions)
              </div>
              <table>
                <thead>
                  <tr>
                    <th className="time-col">Time</th>
                    {DAYS.map(day => <th key={day} className="day-col">{day}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {TIME_SLOTS.map(slot => (
                    <tr key={slot.slot}>
                      <td className="time-col" style={{fontSize: '0.8rem', textAlign: 'center'}}>{slot.time}</td>
                      {DAYS.map(day => {
                        const item = schedule[day][slot.slot];
                        if (item) {
                          return (
                            <td key={day} className="lab" style={{fontSize: '0.7rem', padding: '3px'}}>
                              <div style={{fontWeight: 'bold', fontSize: '0.8rem', marginBottom: '2px'}}>{item.course_code}</div>
                              <div style={{fontSize: '0.7rem', marginBottom: '2px'}}>{item.course_name}</div>
                              <div style={{color: '#666', fontSize: '0.6rem'}}>LAB {item.room}</div>
                              <div style={{fontSize: '0.6rem', color: '#666'}}>{item.sections.join(', ')}</div>
                            </td>
                          );
                        } else {
                          return <td key={day}></td>;
                        }
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })}
      </div>
    );
  };

  const renderContent = () => {
    if (loading) {
      return <div className="loading">⏳ Loading timetable data...</div>;
    }

    if (error) {
      return (
        <div className="error">
          <h3>❌ Error</h3>
          <p>{error}</p>
          <p>Make sure the API server is running: <code>python api.py</code></p>
          <button onClick={loadAllData}>🔄 Retry</button>
        </div>
      );
    }

    if (!allData) {
      return <div className="no-data">No data available</div>;
    }

    // Show only the active view
    switch (activeView) {
      case 'levels':
        return (
          <>
            {renderCombinedLevelTable()}
            {renderSectionSchedules()}
          </>
        );
      case 'professors':
        return renderProfessors();
      case 'rooms':
        return renderRooms();
      case 'lab-instructors':
        return renderLabInstructors();
      default:
        return renderCombinedLevelTable();
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1 className="app-header">
          🎓 CSIT College Timetable
        </h1>

        <div style={{backgroundColor: '#e8f5e9', padding: '10px', margin: '10px 0', borderLeft: '4px solid #4CAF50', fontSize: '0.9rem'}}>
          <p><strong>Generated:</strong> {new Date().toLocaleString()}</p>
          <p><strong>Days:</strong> {DAYS.join(', ')}</p>
          <p><strong>Time Slots:</strong> {TIME_SLOTS.map(t => `Slot ${t.slot}: ${t.time}`).join(' | ')}</p>
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            style={{marginTop: '10px', padding: '8px 16px', backgroundColor: '#4CAF50', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px'}}
          >
            {regenerating ? '♻️ Regenerating...' : '♻️ Regenerate Timetable'}
          </button>
        </div>

        <nav className="nav-tabs">
          <button 
            onClick={() => setActiveView('levels')}
            className={activeView === 'levels' ? 'active' : ''}
          >
            📚 Levels
          </button>
          <button 
            onClick={() => setActiveView('professors')}
            className={activeView === 'professors' ? 'active' : ''}
          >
            👨‍🏫 Professors
          </button>
          <button 
            onClick={() => setActiveView('rooms')}
            className={activeView === 'rooms' ? 'active' : ''}
          >
            🏛️ Rooms
          </button>
          <button 
            onClick={() => setActiveView('lab-instructors')}
            className={activeView === 'lab-instructors' ? 'active' : ''}
          >
            🔬 Lab Instructors
          </button>
        </nav>

        <main className="main-content">
          {renderContent()}
        </main>

        <footer style={{marginTop: '40px', padding: '20px', textAlign: 'center', borderTop: '1px solid #ddd', fontSize: '0.8rem', color: '#666'}}>
          <p>College Timetable Scheduling System © 2025</p>
          <p>API: <code>{API_BASE_URL}</code></p>
        </footer>
      </div>
    </div>
  )
}

export default App
