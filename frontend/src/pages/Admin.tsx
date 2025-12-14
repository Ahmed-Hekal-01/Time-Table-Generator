import { useState, useEffect } from 'react';
import Timetable from '../components/table';
import Loader from '../components/loader';
import Menu from '../components/menu';
import type { RoomsResponse, RoomData } from '../types/rooms';

interface AdminProps {
  onBackToHome: () => void;
}

const Admin = ({ onBackToHome }: AdminProps) => {
  const [rooms, setRooms] = useState<RoomsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/rooms')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch rooms');
        return res.json();
      })
      .then((data: RoomsResponse) => {
        setRooms(data);
        setLoading(false);

        // Auto-select first room
        const firstRoom = Object.keys(data.rooms)[0];
        if (firstRoom) {
          setSelectedRoom(firstRoom);
        }
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const buildSchedule = (roomData: RoomData) => {
    const schedule: Record<string, Record<number, any>> = {};
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"];

    days.forEach(day => {
      schedule[day] = { 1: null, 2: null, 3: null, 4: null };
    });

    roomData.schedule.forEach(assignment => {
      schedule[assignment.day][assignment.slot] = assignment;
    });

    return schedule;
  };

  if (loading) return <Loader />;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  if (!rooms) return <div style={{ padding: '20px' }}>No data available</div>;

  // Sort rooms: lecture rooms first, then labs
  const roomList = Object.entries(rooms.rooms)
    .sort(([, a], [, b]) => {
      if (a.room_type === 'lec' && b.room_type === 'lab') return -1;
      if (a.room_type === 'lab' && b.room_type === 'lec') return 1;
      return 0;
    })
    .map(([roomName]) => roomName);

  const selectedRoomData = selectedRoom ? rooms.rooms[selectedRoom] : null;
  const roomColor = selectedRoomData?.room_type === 'lec' ? '#1976d2' : '#d32f2f';

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
        items={roomList}
        selectedItem={selectedRoom}
        onSelectItem={setSelectedRoom}
        title="Rooms"
        color="#FF9800"
      />

      {/* Main Content */}
      <div style={{ marginLeft: '280px', flex: 1, padding: '20px', backgroundColor: '#0A0A0A' }}>
        {selectedRoomData ? (
          <Timetable
            type="room"
            title={`${selectedRoomData.room_type === 'lec' ? 'Room' : 'Lab'} ${selectedRoom}`}
            subtitle={`${selectedRoomData.schedule.length} assignments`}
            schedule={buildSchedule(selectedRoomData)}
            headerColor={roomColor}
          />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
            <h2>Select a room from the menu</h2>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
