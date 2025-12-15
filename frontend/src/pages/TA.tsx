import { useState, useEffect } from 'react';
import Timetable from '../components/table';
import Loader from '../components/loader';
import Menu from '../components/menu';
import type { LabInstructorsResponse, LabInstructorData } from '../types/labInstructors';

interface TAProps {
  onBackToHome: () => void;
}

const TA = ({ onBackToHome }: TAProps) => {
  const [instructors, setInstructors] = useState<LabInstructorsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInstructor, setSelectedInstructor] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/lab-instructors')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch lab instructors');
        return res.json();
      })
      .then((data: LabInstructorsResponse) => {
        setInstructors(data);
        setLoading(false);

        // Auto-select first instructor
        const firstInstructor = Object.keys(data.instructors)[0];
        if (firstInstructor) {
          setSelectedInstructor(firstInstructor);
        }
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const buildSchedule = (instructorData: LabInstructorData) => {
    const schedule: Record<string, Record<number, any>> = {};
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];

    days.forEach(day => {
      schedule[day] = { 1: null, 2: null, 3: null, 4: null };
    });

    instructorData.labs.forEach(lab => {
      schedule[lab.day][lab.slot] = lab;
    });

    return schedule;
  };

  if (loading) return <Loader />;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  if (!instructors) return <div style={{ padding: '20px' }}>No data available</div>;

  const instructorList = Object.keys(instructors.instructors).sort();
  const selectedInstrData = selectedInstructor ? instructors.instructors[selectedInstructor] : null;

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Back Button */}
      <button
        onClick={onBackToHome}
        style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          zIndex: 1000,
          padding: '10px 20px',
          backgroundColor: '#8B0000',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          fontWeight: 'bold',
          fontSize: '0.9rem',
          boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
        }}
      >
        ← Back to Home
      </button>

      {/* Sidebar Menu */}
      <Menu
        items={instructorList}
        selectedItem={selectedInstructor}
        onSelectItem={setSelectedInstructor}
        title="Lab Instructors"
        color="#8B0000"
      />

      {/* Main Content */}
      <div style={{ marginLeft: '280px', flex: 1, padding: '20px', backgroundColor: '#0A0A0A' }}>
        {selectedInstrData ? (
          <Timetable
            type="lab-instructor"
            title={`${selectedInstructor}`}
            subtitle={`${selectedInstrData.labs.length} labs`}
            schedule={buildSchedule(selectedInstrData)}
            headerColor="#FF5722"
          />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
            <h2>Select a lab instructor from the menu</h2>
          </div>
        )}
      </div>
    </div>
  );
};

export default TA;
