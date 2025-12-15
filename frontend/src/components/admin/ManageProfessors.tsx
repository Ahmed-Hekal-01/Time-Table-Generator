import { useState, useEffect } from 'react';

interface Professor {
  instructor_id: number;
  instructor_name: string;
}

const ManageProfessors = () => {
  const [professors, setProfessors] = useState<Professor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [newProf, setNewProf] = useState<Professor>({
    instructor_id: 0,
    instructor_name: ''
  });

  useEffect(() => {
    fetchProfessors();
  }, []);

  const fetchProfessors = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5000/api/manage/professors');
      if (!res.ok) throw new Error('Failed to fetch professors');
      const data = await res.json();
      setProfessors(data);

      // Auto-increment ID suggestion
      const maxId = data.reduce((max: number, p: Professor) => Math.max(max, p.instructor_id), 0);
      setNewProf(prev => ({ ...prev, instructor_id: maxId + 1 }));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!newProf.instructor_name) return alert('Name is required');

    try {
      const res = await fetch('http://localhost:5000/api/manage/professors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProf)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      alert('Professor added successfully');
      setNewProf({ instructor_id: 0, instructor_name: '' });
      fetchProfessors();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm(`Are you sure you want to delete professor ID ${id}?`)) return;

    try {
      const res = await fetch('http://localhost:5000/api/manage/professors', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instructor_id: id })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      fetchProfessors();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h2>Manage Professors</h2>

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
        <div style={{ flex: 1 }}>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Name</label>
          <input
            type="text"
            value={newProf.instructor_name}
            onChange={e => setNewProf({ ...newProf, instructor_name: e.target.value })}
            placeholder="e.g. Dr. Ahmed"
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
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
          Add Professor
        </button>
      </div>

      {/* List */}
      <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#1a1a1a', borderRadius: '8px', overflow: 'hidden' }}>
        <thead>
          <tr style={{ backgroundColor: '#333', textAlign: 'left' }}>
            <th style={{ padding: '12px' }}>ID</th>
            <th style={{ padding: '12px' }}>Name</th>
            <th style={{ padding: '12px' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {professors.map(prof => (
            <tr key={prof.instructor_id} style={{ borderTop: '1px solid #333' }}>
              <td style={{ padding: '12px' }}>{prof.instructor_id}</td>
              <td style={{ padding: '12px' }}>{prof.instructor_name}</td>
              <td style={{ padding: '12px' }}>
                <button
                  onClick={() => handleDelete(prof.instructor_id)}
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

export default ManageProfessors;
