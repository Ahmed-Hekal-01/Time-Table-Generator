import { useState, useEffect } from 'react';
import SearchableDropdown from '../SearchableDropdown';

interface Course {
  course_code: string;
  course_name: string;
  instructor_name: string;
  instructor_id: number;
  level: number;
  department?: string;
  has_lab?: boolean;
}

interface Professor {
  instructor_id: number;
  instructor_name: string;
}

const ManageCourses = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [professors, setProfessors] = useState<Professor[]>([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [level, setLevel] = useState(1);
  const [department, setDepartment] = useState('CSC');
  const [courseCode, setCourseCode] = useState('');
  const [courseName, setCourseName] = useState('');
  const [selectedProfId, setSelectedProfId] = useState<string>('');
  const [hasLab, setHasLab] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [coursesRes, profsRes] = await Promise.all([
        fetch('http://localhost:5000/api/courses'),
        fetch('http://localhost:5000/api/manage/professors')
      ]);

      const coursesData = await coursesRes.json();
      const profsData = await profsRes.json();

      setCourses(coursesData);
      setProfessors(profsData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!courseCode || !courseName || !selectedProfId) {
      alert('Please fill in all required fields');
      return;
    }

    const professor = professors.find(p => p.instructor_id === parseInt(selectedProfId));
    if (!professor) return;

    const courseData = {
      course_code: courseCode,
      course_name: courseName,
      instructor_name: professor.instructor_name,
      instructor_id: professor.instructor_id,
      level: level
    };

    const payload: any = {
      level,
      has_lab: hasLab,
      data: courseData
    };

    if (level >= 3) {
      payload.department = department;
    }

    try {
      const res = await fetch('http://localhost:5000/api/manage/courses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      alert('Course added successfully');
      // Reset form
      setCourseCode('');
      setCourseName('');
      setSelectedProfId('');
      setHasLab(false);
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (course: Course) => {
    if (!window.confirm(`Delete course ${course.course_code}?`)) return;

    try {
      const res = await fetch('http://localhost:5000/api/manage/courses', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          level: course.level,
          course_code: course.course_code
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message);

      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCourseSelect = (code: string) => {
    const course = courses.find(c => c.course_code === code);
    if (course) {
      setCourseCode(course.course_code);
      setCourseName(course.course_name);
      setLevel(course.level);
      if (course.department) setDepartment(course.department);
      setHasLab(!!course.has_lab);

      // Find prof
      const prof = professors.find(p => p.instructor_id === course.instructor_id);
      if (prof) setSelectedProfId(prof.instructor_id.toString());
    }
  };

  const clearForm = () => {
    setCourseCode('');
    setCourseName('');
    setSelectedProfId('');
    setHasLab(false);
    setLevel(1);
    setDepartment('CSC');
  };

  const courseOptions = courses.map(c => ({
    value: c.course_code,
    label: `${c.course_code} - ${c.course_name}`
  }));

  const profOptions = professors.map(p => ({
    value: p.instructor_id.toString(),
    label: p.instructor_name
  }));

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h2>Manage Courses</h2>

      {/* Add Form */}
      <div style={{
        backgroundColor: '#1a1a1a',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '30px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '15px',
        alignItems: 'end'
      }}>
        <div style={{ gridColumn: '1 / -1', marginBottom: '10px', display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Select Existing Course to Edit</label>
            <SearchableDropdown
              options={courseOptions}
              value={courseOptions.find(o => o.value === courseCode)?.value || ''}
              onChange={(val) => handleCourseSelect(val as string)}
              placeholder="Search Course..."
            />
          </div>
          <button
            onClick={clearForm}
            style={{
              padding: '8px 15px',
              backgroundColor: '#555',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              height: '38px',
              marginTop: '22px'
            }}
          >
            New Course
          </button>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Level</label>
          <select
            value={level}
            onChange={e => setLevel(parseInt(e.target.value))}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
          >
            {[1, 2, 3, 4].map(l => <option key={l} value={l}>Level {l}</option>)}
          </select>
        </div>

        {level >= 3 && (
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Department</label>
            <select
              value={department}
              onChange={e => setDepartment(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
            >
              {['CSC', 'CNC', 'BIF', 'AID'].map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        )}

        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Course Code</label>
          <input
            type="text"
            value={courseCode}
            onChange={e => setCourseCode(e.target.value)}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Course Name</label>
          <input
            type="text"
            value={courseName}
            onChange={e => setCourseName(e.target.value)}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#333', color: 'white' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9rem', color: '#aaa' }}>Instructor</label>
          <SearchableDropdown
            options={profOptions}
            value={selectedProfId}
            onChange={(val) => setSelectedProfId(val as string)}
            placeholder="Select Prof..."
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', height: '40px' }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', color: '#fff' }}>
            <input
              type="checkbox"
              checked={hasLab}
              onChange={e => setHasLab(e.target.checked)}
              style={{ marginRight: '8px', width: '18px', height: '18px' }}
            />
            Has Lab?
          </label>
        </div>

        <button
          onClick={handleAdd}
          style={{
            padding: '10px',
            backgroundColor: '#4caf50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {courses.find(c => c.course_code === courseCode) ? 'Update Course' : 'Add Course'}
        </button>
      </div>

      {/* List */}
      <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: '#1a1a1a', borderRadius: '8px', overflow: 'hidden' }}>
        <thead>
          <tr style={{ backgroundColor: '#333', textAlign: 'left' }}>
            <th style={{ padding: '12px' }}>Code</th>
            <th style={{ padding: '12px' }}>Name</th>
            <th style={{ padding: '12px' }}>Level</th>
            <th style={{ padding: '12px' }}>Dept</th>
            <th style={{ padding: '12px' }}>Instructor</th>
            <th style={{ padding: '12px' }}>Lab?</th>
            <th style={{ padding: '12px' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {courses.map((course, idx) => (
            <tr key={`${course.course_code}-${idx}`} style={{ borderTop: '1px solid #333' }}>
              <td style={{ padding: '12px' }}>{course.course_code}</td>
              <td style={{ padding: '12px' }}>{course.course_name}</td>
              <td style={{ padding: '12px' }}>{course.level}</td>
              <td style={{ padding: '12px' }}>{course.department || '-'}</td>
              <td style={{ padding: '12px' }}>{course.instructor_name}</td>
              <td style={{ padding: '12px' }}>{course.has_lab ? '✅' : '❌'}</td>
              <td style={{ padding: '12px' }}>
                <button
                  onClick={() => handleDelete(course)}
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

export default ManageCourses;
