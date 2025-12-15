import { useState, useEffect } from 'react';

interface Room {
  room_code: string;
  room_type: string;
  capacity: number;
  building: string;
}

const ManageRooms = () => {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [newRoom, setNewRoom] = useState<Room>({
    room_code: '',
    room_type: 'lec',
    capacity: 50,
    building: ''
  });

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5000/api/manage/rooms');
      if (!res.ok) throw new Error('Failed to fetch rooms');
      const data = await res.json();
      setRooms(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!newRoom.room_code) return alert('Room Code is required');

    try {
      const res = await fetch('http://localhost:5000/api/manage/rooms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newRoom)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      alert('Room added successfully');
      setNewRoom({ room_code: '', room_type: 'lec', capacity: 50, building: '' });
      fetchRooms();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (roomCode: string) => {
    if (!window.confirm(`Are you sure you want to delete room ${roomCode}?`)) return;

    try {
      const res = await fetch('http://localhost:5000/api/manage/rooms', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_code: roomCode })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      fetchRooms();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h2>Manage Rooms</h2>

      {/* Add Form */}
      <div style={{
        backgroundColor: '#1a1a1a',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '30px',
        display: 'flex',
        gap: '10px',
        flexWrap: 'wrap',
        alignItems: 'flex-end'
      }}>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Room Code</label>
          <input
            type="text"
            value={newRoom.room_code}
            onChange={e => setNewRoom({ ...newRoom, room_code: e.target.value })}
            placeholder="e.g. 101"
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
          />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Type</label>
          <select
            value={newRoom.room_type}
            onChange={e => setNewRoom({ ...newRoom, room_type: e.target.value })}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white', minWidth: '100px' }}
          >
            <option value="lec">Lecture</option>
            <option value="lab">Lab</option>
          </select>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Capacity</label>
          <input
            type="number"
            value={newRoom.capacity}
            onChange={e => setNewRoom({ ...newRoom, capacity: parseInt(e.target.value) })}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white', width: '80px' }}
          />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Building</label>
          <input
            type="text"
            value={newRoom.building}
            onChange={e => setNewRoom({ ...newRoom, building: e.target.value })}
            placeholder="e.g. Main"
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
          />
        </div>
        <button
          onClick={handleAdd}
          style={{
            padding: '8px 20px',
            backgroundColor: '#4caf50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
            height: '36px'
          }}
        >
          Add Room
        </button>
      </div>

      {/* List */}
      <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#1a1a1a', borderRadius: '8px', overflow: 'hidden' }}>
        <thead>
          <tr style={{ backgroundColor: '#333', textAlign: 'left' }}>
            <th style={{ padding: '12px' }}>Code</th>
            <th style={{ padding: '12px' }}>Type</th>
            <th style={{ padding: '12px' }}>Capacity</th>
            <th style={{ padding: '12px' }}>Building</th>
            <th style={{ padding: '12px' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rooms.map(room => (
            <tr key={room.room_code} style={{ borderTop: '1px solid #333' }}>
              <td style={{ padding: '12px' }}>{room.room_code}</td>
              <td style={{ padding: '12px' }}>
                <span style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  backgroundColor: room.room_type === 'lec' ? 'rgba(25, 118, 210, 0.2)' : 'rgba(255, 152, 0, 0.2)',
                  color: room.room_type === 'lec' ? '#90caf9' : '#ffcc80',
                  fontSize: '0.85rem'
                }}>
                  {room.room_type === 'lec' ? 'Lecture' : 'Lab'}
                </span>
              </td>
              <td style={{ padding: '12px' }}>{room.capacity}</td>
              <td style={{ padding: '12px' }}>{room.building}</td>
              <td style={{ padding: '12px' }}>
                <button
                  onClick={() => handleDelete(room.room_code)}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.85rem'
                  }}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ManageRooms;
