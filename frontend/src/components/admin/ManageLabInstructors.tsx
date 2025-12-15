import { useState, useEffect } from 'react';

interface LabInstructor {
  instructor_id: string;
  instructor_name: string;
  instructor_type: string;
  max_hours_per_week: number;
  qualified_labs: string[];
}

interface Course {
  course_code: string;
  course_name: string;
}

const ManageLabInstructors = () => {
  const [instructors, setInstructors] = useState<LabInstructor[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [newInst, setNewInst] = useState<LabInstructor>({
    instructor_id: '',
    instructor_name: '',
    instructor_type: 'TA',
    max_hours_per_week: 20,
    qualified_labs: []
  });
  const [selectedCourse, setSelectedCourse] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [instRes, coursesRes] = await Promise.all([
        fetch('http://localhost:5000/api/manage/lab-instructors'),
        fetch('http://localhost:5000/api/courses')
      ]);

      if (!instRes.ok) throw new Error('Failed to fetch instructors');
      const instData = await instRes.json();
      setInstructors(instData);

      if (coursesRes.ok) {
        const coursesData = await coursesRes.json();
        setCourses(coursesData);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!newInst.instructor_name) return alert('Name is required');

    // Auto-generate ID (simple random for now, or could be incremental)
    const generatedId = Math.floor(Math.random() * 10000).toString();

    const payload = {
      ...newInst,
      instructor_id: generatedId,
      qualified_labs: selectedCourse ? [selectedCourse] : []
    };

    try {
      const res = await fetch('http://localhost:5000/api/manage/lab-instructors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      alert('Instructor added successfully');
      setNewInst({
        instructor_id: '',
        instructor_name: '',
        instructor_type: 'TA',
        max_hours_per_week: 20,
        qualified_labs: []
      });
      setSelectedCourse('');
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm(`Are you sure you want to delete instructor ${id}?`)) return;

    try {
      const res = await fetch('http://localhost:5000/api/manage/lab-instructors', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instructor_id: id })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h2>Manage Lab Instructors</h2>

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
            value={newInst.instructor_name}
            onChange={e => setNewInst({ ...newInst, instructor_name: e.target.value })}
            placeholder="e.g. TA Sarah"
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
          />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Type</label>
          <select
            value={newInst.instructor_type}
            onChange={e => setNewInst({ ...newInst, instructor_type: e.target.value })}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
          >
            <option value="TA">TA</option>
            <option value="Lab Instructor">Lab Instructor</option>
          </select>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Max Hours</label>
          <input
            type="number"
            value={newInst.max_hours_per_week}
            onChange={e => setNewInst({ ...newInst, max_hours_per_week: parseFloat(e.target.value) })}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white', width: '80px' }}
          />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Qualified Course</label>
          <select
            value={selectedCourse}
            onChange={e => setSelectedCourse(e.target.value)}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white', maxWidth: '200px' }}
          >
            <option value="">Select Course...</option>
            {courses.map(c => (
              <option key={c.course_code} value={c.course_code}>
                {c.course_code} - {c.course_name}
              </option>
            ))}
          </select>
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
          Add Instructor
        </button>
      </div>

      {/* List */}
      <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#1a1a1a', borderRadius: '8px', overflow: 'hidden' }}>
        <thead>
          <tr style={{ backgroundColor: '#333', textAlign: 'left' }}>
            <th style={{ padding: '12px' }}>ID</th>
            <th style={{ padding: '12px' }}>Name</th>
            <th style={{ padding: '12px' }}>Type</th>
            <th style={{ padding: '12px' }}>Max Hours</th>
            <th style={{ padding: '12px' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {instructors.map(inst => (
            <tr key={inst.instructor_id} style={{ borderTop: '1px solid #333' }}>
              <td style={{ padding: '12px' }}>{inst.instructor_id}</td>
              <td style={{ padding: '12px' }}>{inst.instructor_name}</td>
              <td style={{ padding: '12px' }}>
                <span style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  backgroundColor: inst.instructor_type === 'TA' ? 'rgba(76, 175, 80, 0.2)' : 'rgba(33, 150, 243, 0.2)',
                  color: inst.instructor_type === 'TA' ? '#81c784' : '#64b5f6',
                  fontSize: '0.85rem'
                }}>
                  {inst.instructor_type}
                </span>
              </td>
              <td style={{ padding: '12px' }}>{inst.max_hours_per_week}</td>
              <td style={{ padding: '12px' }}>
                <button
                  onClick={() => handleDelete(inst.instructor_id)}
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

export default ManageLabInstructors;
