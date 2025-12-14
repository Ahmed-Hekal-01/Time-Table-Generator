import { useState, useEffect } from 'react';
import Timetable from '../components/table';
import Loader from '../components/loader';
import Menu from '../components/menu';
import type { LevelsResponse, GroupData } from '../types/levels';

interface StudentProps {
  onBackToHome: () => void;
}

const Student = ({ onBackToHome }: StudentProps) => {
  const [levels, setLevels] = useState<LevelsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/levels')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch levels');
        return res.json();
      })
      .then((data: LevelsResponse) => {
        setLevels(data);
        setLoading(false);

        // Auto-select first section
        const firstLevel = Object.values(data.levels)[0];
        if (firstLevel) {
          const firstGroup = Object.values(firstLevel)[0];
          if (firstGroup && firstGroup.sections.length > 0) {
            setSelectedSection(`${firstGroup.group_id}-${firstGroup.sections[0]}`);
          }
        }
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const buildSectionSchedule = (group: GroupData, sectionId: string) => {
    const schedule: Record<string, Record<number, any>> = {};
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];

    days.forEach(day => {
      schedule[day] = { 1: null, 2: null, 3: null, 4: null };
    });

    // Add lectures (shared by all sections)
    group.lectures?.forEach(lec => {
      schedule[lec.day][lec.slot] = { ...lec, type: 'lecture' };
    });

    // Add labs for this specific section
    group.labs_by_section?.[sectionId]?.forEach(lab => {
      schedule[lab.day][lab.slot] = { ...lab, type: 'lab' };
    });

    return schedule;
  };

  // Build section list for menu
  const getSectionList = (): string[] => {
    if (!levels) return [];
    const sections: string[] = [];

    Object.values(levels.levels).forEach(levelData => {
      Object.values(levelData).forEach(group => {
        group.sections.forEach(sectionId => {
          sections.push(`${group.group_id}-${sectionId}`);
        });
      });
    });

    return sections;
  };

  // Get selected group and section data
  const getSelectedData = () => {
    if (!levels || !selectedSection) return null;

    for (const levelData of Object.values(levels.levels)) {
      for (const [gId, group] of Object.entries(levelData)) {
        if (selectedSection.startsWith(gId)) {
          const secId = selectedSection.replace(`${gId}-`, '');
          if (group.sections.includes(secId)) {
            return { group, sectionId: secId, groupId: gId };
          }
        }
      }
    }

    return null;
  };

  if (loading) return <Loader />;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  if (!levels) return <div style={{ padding: '20px' }}>No data available</div>;

  const sectionList = getSectionList();
  const selectedData = getSelectedData();

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
        items={sectionList}
        selectedItem={selectedSection}
        onSelectItem={setSelectedSection}
        title="School Level - Sections"
        color="#4CAF50"
      />

      {/* Main Content */}
      <div style={{ marginLeft: '280px', flex: 1, padding: '20px', backgroundColor: '#0A0A0A' }}>
        {selectedData ? (
          <Timetable
            type="student"
            title={`${selectedData.groupId} - Section ${selectedData.sectionId}`}
            schedule={buildSectionSchedule(selectedData.group, selectedData.sectionId)}
            headerColor="#4CAF50"
          />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
            <h2>Select a section from the menu</h2>
          </div>
        )}
      </div>
    </div>
  );
};

export default Student;
