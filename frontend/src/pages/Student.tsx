import { useState, useEffect } from 'react';
import Loader from '../components/loader';
import Menu from '../components/menu';
import LevelTimetable from '../components/LevelTimetable';
import type { LevelsResponse } from '../types/levels';

interface StudentProps {
  onBackToHome: () => void;
}

const Student = ({ onBackToHome }: StudentProps) => {
  const [levels, setLevels] = useState<LevelsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string>('Level 1');

  useEffect(() => {
    fetch('http://localhost:5000/api/levels')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch levels');
        return res.json();
      })
      .then((data: LevelsResponse) => {
        setLevels(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <Loader />;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  if (!levels) return <div style={{ padding: '20px' }}>No data available</div>;

  // Get available levels (e.g., ["Level 1", "Level 2", ...])
  const levelList = Object.keys(levels.levels).map(key => key.replace('Level', 'Level '));

  // Get data for the selected level
  const levelKey = selectedLevel.replace(' ', '') as keyof typeof levels.levels;
  const levelData = levels.levels[levelKey];
  const groups = levelData ? Object.values(levelData) : [];

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
        items={levelList}
        selectedItem={selectedLevel}
        onSelectItem={setSelectedLevel}
        title="Select Level"
        color="#8B0000"
      />

      {/* Main Content */}
      <div style={{ marginLeft: '280px', flex: 1, padding: '20px', backgroundColor: '#0A0A0A' }}>
        {groups.length > 0 ? (
          <LevelTimetable
            levelName={selectedLevel}
            groups={groups}
          />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
            <h2>No data for this level</h2>
          </div>
        )}
      </div>
    </div>
  );
};

export default Student;
