import { useState, useEffect } from 'react';
import Timetable from '../table';

const AllLevelsTimetable = () => {
    const [activeLevel, setActiveLevel] = useState<number>(1);
    const [levelsData, setLevelsData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchLevels();
    }, []);

    const fetchLevels = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:5000/api/levels');
            if (!res.ok) throw new Error('Failed to fetch levels data');
            const data = await res.json();
            setLevelsData(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const buildSchedule = (groupData: any) => {
        const schedule: Record<string, Record<number, any>> = {};
        const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];
        days.forEach(day => { schedule[day] = { 1: null, 2: null, 3: null, 4: null }; });

        // Add lectures
        groupData.lectures.forEach((lec: any) => {
            schedule[lec.day][lec.slot] = lec;
        });

        // Add labs (taking the first section's labs for simplicity in group view, 
        // or we could show a merged view. For now, let's show section 1's labs)
        const firstSectionId = groupData.sections[0];
        if (groupData.labs_by_section && groupData.labs_by_section[firstSectionId]) {
            groupData.labs_by_section[firstSectionId].forEach((lab: any) => {
                schedule[lab.day][lab.slot] = lab;
            });
        }

        return schedule;
    };

    if (loading) return <div>Loading timetables...</div>;
    if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;
    if (!levelsData) return <div>No data available</div>;

    const currentLevelKey = `Level${activeLevel}`;
    const currentLevelGroups = levelsData.levels[currentLevelKey] || {};

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{
                display: 'flex',
                marginBottom: '20px',
                borderBottom: '1px solid #333',
                paddingBottom: '10px'
            }}>
                {[1, 2, 3, 4].map(level => (
                    <button
                        key={level}
                        onClick={() => setActiveLevel(level)}
                        style={{
                            padding: '10px 20px',
                            backgroundColor: activeLevel === level ? '#1976d2' : 'transparent',
                            color: activeLevel === level ? 'white' : '#888',
                            border: 'none',
                            borderRadius: '4px',
                            marginRight: '10px',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            fontSize: '1rem'
                        }}
                    >
                        Level {level}
                    </button>
                ))}
            </div>

            <div style={{ flex: 1, overflowY: 'auto' }}>
                {Object.keys(currentLevelGroups).length === 0 ? (
                    <div style={{ color: '#888', textAlign: 'center', marginTop: '50px' }}>
                        No groups found for Level {activeLevel}
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
                        {Object.values(currentLevelGroups).map((group: any) => (
                            <div key={group.group_id}>
                                <Timetable
                                    type="group"
                                    title={`Group ${group.group_id}`}
                                    subtitle={`Level ${activeLevel}`}
                                    schedule={buildSchedule(group)}
                                    headerColor="#1976d2"
                                />
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AllLevelsTimetable;
