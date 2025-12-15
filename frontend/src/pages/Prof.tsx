import { useState, useEffect } from 'react';
import Timetable from '../components/table';
import Loader from '../components/loader';
import Menu from '../components/menu';
import type { ProfessorsResponse, ProfessorData } from '../types/professors';

interface ProfProps {
  onBackToHome: () => void;
}

const Prof = ({ onBackToHome }: ProfProps) => {
  const [professors, setProfessors] = useState<ProfessorsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProfessor, setSelectedProfessor] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/professors')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch professors');
        return res.json();
      })
      .then((data: ProfessorsResponse) => {
        setProfessors(data);
        setLoading(false);

        // Auto-select first professor
        const firstProfessor = Object.keys(data.professors)[0];
        if (firstProfessor) {
          setSelectedProfessor(firstProfessor);
        }
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const buildSchedule = (profData: ProfessorData) => {
    const schedule: Record<string, Record<number, any>> = {};
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];

    days.forEach(day => {
      schedule[day] = { 1: null, 2: null, 3: null, 4: null };
    });

    profData.lectures.forEach(lec => {
      schedule[lec.day][lec.slot] = lec;
    });

    return schedule;
  };

  if (loading) return <Loader />;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  if (!professors) return <div style={{ padding: '20px' }}>No data available</div>;

  const professorList = Object.keys(professors.professors).sort();
  const selectedProfData = selectedProfessor ? professors.professors[selectedProfessor] : null;

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
        items={professorList}
        selectedItem={selectedProfessor}
        onSelectItem={setSelectedProfessor}
        title="Professors"
        color="#8B0000"
      />

      {/* Main Content */}
      <div style={{ marginLeft: '280px', flex: 1, padding: '20px', backgroundColor: '#0A0A0A' }}>
        {selectedProfData ? (
          <Timetable
            type="professor"
            title={`Prof. ${selectedProfessor}`}
            subtitle={`${selectedProfData.lectures.length} lectures`}
            schedule={buildSchedule(selectedProfData)}
            headerColor="#9C27B0"
          />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
            <h2>Select a professor from the menu</h2>
          </div>
        )}
      </div>
    </div>
  );
};

export default Prof;
