import { useState, useEffect } from 'react';
import Loader from '../components/loader';
import Timetable from '../components/table';
import ManageRooms from '../components/admin/ManageRooms';
import ManageProfessors from '../components/admin/ManageProfessors';
import ManageLabInstructors from '../components/admin/ManageLabInstructors';
import ManageCourses from '../components/admin/ManageCourses';
import type { RoomsResponse, RoomData } from '../types/rooms';

interface AdminProps {
  onBackToHome: () => void;
}

type ViewMode = 'dashboard' | 'courses' | 'professors' | 'instructors' | 'rooms' | 'assign';

const Admin = ({ onBackToHome }: AdminProps) => {
  const [viewMode, setViewMode] = useState<ViewMode>('dashboard');
  const [rooms, setRooms] = useState<RoomsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    if (viewMode === 'dashboard') {
      fetchRooms();
    }
  }, [viewMode]);

  const fetchRooms = () => {
    setLoading(true);
    fetch('http://localhost:5000/api/rooms')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch rooms');
        return res.json();
      })
      .then((data: RoomsResponse) => {
        setRooms(data);
        setLoading(false);

        if (!selectedRoom) {
          const firstRoom = Object.keys(data.rooms)[0];
          if (firstRoom) setSelectedRoom(firstRoom);
        }
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  const handleRegenerate = async () => {
    if (!window.confirm('Are you sure you want to regenerate the timetable? This will overwrite the current schedule.')) {
      return;
    }

    setRegenerating(true);
    try {
      const res = await fetch('http://localhost:5000/api/regenerate', { method: 'POST' });
      if (!res.ok) throw new Error('Failed to regenerate timetable');
      const data = await res.json();
      alert(data.message || 'Timetable regenerated successfully!');
      if (viewMode === 'dashboard') fetchRooms();
    } catch (err: any) {
      alert('Error: ' + err.message);
    } finally {
      setRegenerating(false);
    }
  };

  const buildSchedule = (roomData: RoomData) => {
    const schedule: Record<string, Record<number, any>> = {};
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];
    days.forEach(day => { schedule[day] = { 1: null, 2: null, 3: null, 4: null }; });
    roomData.schedule.forEach(assignment => { schedule[assignment.day][assignment.slot] = assignment; });
    return schedule;
  };

  // Sidebar Menu Items
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', color: '#1976d2' },
    { id: 'courses', label: 'Manage Courses', color: '#4caf50' },
    { id: 'professors', label: 'Manage Professors', color: '#ff9800' },
    { id: 'instructors', label: 'Manage Lab Instructors', color: '#9c27b0' },
    { id: 'rooms', label: 'Manage Rooms', color: '#795548' },
  ];

  const renderContent = () => {
    switch (viewMode) {
      case 'courses': return <ManageCourses />;
      case 'professors': return <ManageProfessors />;
      case 'instructors': return <ManageLabInstructors />;
      case 'rooms': return <ManageRooms />;
      case 'dashboard':
      default:
        if (loading) return <Loader />;
        if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;
        if (!rooms) return <div>No data</div>;

        const roomList = Object.entries(rooms.rooms)
          .sort(([, a], [, b]) => {
            if (a.room_type === 'lec' && b.room_type === 'lab') return -1;
            if (a.room_type === 'lab' && b.room_type === 'lec') return 1;
            return 0;
          })
          .map(([name]) => name);

        const selectedRoomData = selectedRoom ? rooms.rooms[selectedRoom] : null;

        return (
          <div style={{ display: 'flex', gap: '20px', height: '100%' }}>
            {/* Room List */}
            <div style={{ width: '200px', overflowY: 'auto', borderRight: '1px solid #333', paddingRight: '10px' }}>
              <h3 style={{ color: '#aaa', marginBottom: '10px' }}>Rooms</h3>
              {roomList.map(room => (
                <div
                  key={room}
                  onClick={() => setSelectedRoom(room)}
                  style={{
                    padding: '10px',
                    cursor: 'pointer',
                    backgroundColor: selectedRoom === room ? '#333' : 'transparent',
                    color: selectedRoom === room ? 'white' : '#888',
                    borderRadius: '4px',
                    marginBottom: '5px'
                  }}
                >
                  {room}
                </div>
              ))}
            </div>

            {/* Timetable */}
            <div style={{ flex: 1 }}>
              {selectedRoomData ? (
                <Timetable
                  type="room"
                  title={`Room ${selectedRoomData.room_name}`}
                  subtitle={`${selectedRoomData.room_type.toUpperCase()} - Capacity: ${selectedRoomData.capacity}`}
                  schedule={buildSchedule(selectedRoomData)}
                  headerColor={selectedRoomData.room_type === 'lec' ? '#1976d2' : '#d32f2f'}
                />
              ) : (
                <div>Select a room</div>
              )}
            </div>
          </div>
        );
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0A0A0A' }}>
      {/* Sidebar */}
      <div style={{
        width: '260px',
        backgroundColor: '#111',
        borderRight: '1px solid #333',
        display: 'flex',
        flexDirection: 'column',
        padding: '20px'
      }}>
        <h2 style={{ color: 'white', marginBottom: '30px', paddingBottom: '10px', borderBottom: '1px solid #333' }}>
          Admin Panel
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', flex: 1 }}>
          {menuItems.map(item => (
            <button
              key={item.id}
              onClick={() => setViewMode(item.id as ViewMode)}
              style={{
                padding: '12px 15px',
                textAlign: 'left',
                backgroundColor: viewMode === item.id ? item.color : 'transparent',
                color: viewMode === item.id ? 'white' : '#888',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.95rem',
                fontWeight: viewMode === item.id ? 'bold' : 'normal',
                transition: 'all 0.2s'
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        <button
          onClick={onBackToHome}
          style={{
            marginTop: '20px',
            padding: '12px',
            backgroundColor: '#333',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          ← Back to Home
        </button>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #333',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#111'
        }}>
          <h2 style={{ color: 'white', margin: 0 }}>
            {menuItems.find(i => i.id === viewMode)?.label}
          </h2>

          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            style={{
              padding: '10px 20px',
              backgroundColor: regenerating ? '#555' : '#ff9800',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: regenerating ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
            }}
          >
            {regenerating ? 'Regenerating...' : '♻️ Regenerate Timetable'}
          </button>
        </div>

        {/* Content Area */}
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default Admin;
