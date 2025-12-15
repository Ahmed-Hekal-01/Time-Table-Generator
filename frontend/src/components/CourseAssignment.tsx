import { useState, useEffect } from 'react';
import SearchableDropdown from './SearchableDropdown';

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

interface CourseAssignmentProps {
  onAssignmentComplete?: () => void;
}

const CourseAssignment = ({ onAssignmentComplete }: CourseAssignmentProps) => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [professors, setProfessors] = useState<Professor[]>([]);
  const [selectedCourseCode, setSelectedCourseCode] = useState<string>('');
  const [selectedProfId, setSelectedProfId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [coursesRes, profsRes] = await Promise.all([
        fetch('http://localhost:5000/api/manage/courses'),
        fetch('http://localhost:5000/api/manage/professors')
      ]);

      if (!coursesRes.ok || !profsRes.ok) throw new Error('Failed to fetch data');

      const coursesData = await coursesRes.json();
      const profsData = await profsRes.json();

      setProfessors(profsData);
      setCourses(processCourses(coursesData));
    } catch (err) {
      console.error(err);
      setMessage({ text: 'Failed to load data', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const processCourses = (data: any): Course[] => {
    const allCourses: Course[] = [];

    // Helper to check for lab existence
    const hasLab = (code: string, labs: any[]) => labs.some((l: any) => l.course_code === code);

    // Level 1 & 2
    [1, 2].forEach(level => {
      const levelKey = `level_${level}`;
      if (data[levelKey]) {
        const lectures = data[levelKey].lectures || [];
        const labs = data[levelKey].labs || [];

        lectures.forEach((lec: any) => {
          allCourses.push({
            ...lec,
            level,
            has_lab: hasLab(lec.course_code, labs)
          });
        });
      }
    });

    // Level 3 & 4
    [3, 4].forEach(level => {
      const levelKey = `level_${level}`;
      if (data[levelKey]) {
        Object.entries(data[levelKey]).forEach(([dept, content]: [string, any]) => {
          const lectures = content.lectures || [];
          const labs = content.labs || [];

          lectures.forEach((lec: any) => {
            allCourses.push({
              ...lec,
              level,
              department: dept,
              has_lab: hasLab(lec.course_code, labs)
            });
          });
        });
      }
    });

    return allCourses.sort((a, b) => a.course_code.localeCompare(b.course_code));
  };

  const handleAssign = async () => {
    if (!selectedCourseCode || !selectedProfId) {
      setMessage({ text: 'Please select both a course and a professor', type: 'error' });
      return;
    }

    const course = courses.find(c => c.course_code === selectedCourseCode);
    const professor = professors.find(p => p.instructor_id === parseInt(selectedProfId));

    if (!course || !professor) return;

    setAssigning(true);
    setMessage(null);

    try {
      // 1. Delete the existing course
      const deleteRes = await fetch('http://localhost:5000/api/manage/courses', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          level: course.level,
          course_code: course.course_code
        })
      });

      if (!deleteRes.ok) throw new Error('Failed to delete existing course record');

      // 2. Add the course back with new instructor
      const newCourseData = {
        course_code: course.course_code,
        course_name: course.course_name,
        instructor_name: professor.instructor_name,
        instructor_id: professor.instructor_id,
        level: course.level,
        is_graduation_project: (course as any).is_graduation_project // Preserve this flag if it exists
      };

      const postBody: any = {
        level: course.level,
        has_lab: course.has_lab,
        data: newCourseData
      };

      if (course.department) {
        postBody.department = course.department;
      }

      const postRes = await fetch('http://localhost:5000/api/manage/courses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postBody)
      });

      if (!postRes.ok) throw new Error('Failed to update course assignment');

      setMessage({ text: `Successfully assigned ${professor.instructor_name} to ${course.course_name}`, type: 'success' });

      // Refresh data
      await fetchData();
      if (onAssignmentComplete) onAssignmentComplete();

    } catch (err: any) {
      console.error(err);
      setMessage({ text: err.message || 'Assignment failed', type: 'error' });
    } finally {
      setAssigning(false);
    }
  };

  if (loading) return <div style={{ color: 'white' }}>Loading data...</div>;

  const courseOptions = courses.map(course => ({
    value: course.course_code,
    label: `${course.course_code} - ${course.course_name} (Current: ${course.instructor_name})`
  }));

  const professorOptions = professors.map(prof => ({
    value: prof.instructor_id.toString(),
    label: prof.instructor_name
  }));

  return (
    <div style={{
      backgroundColor: '#1a1a1a',
      padding: '20px',
      borderRadius: '8px',
      maxWidth: '600px',
      margin: '0 auto',
      color: 'white'
    }}>
      <h2 style={{ borderBottom: '1px solid #333', paddingBottom: '10px', marginBottom: '20px' }}>
        Assign Instructor to Course
      </h2>

      {message && (
        <div style={{
          padding: '10px',
          marginBottom: '20px',
          borderRadius: '4px',
          backgroundColor: message.type === 'success' ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)',
          color: message.type === 'success' ? '#4caf50' : '#f44336',
          border: `1px solid ${message.type === 'success' ? '#4caf50' : '#f44336'}`
        }}>
          {message.text}
        </div>
      )}

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', color: '#aaa' }}>Select Course</label>
        <SearchableDropdown
          options={courseOptions}
          value={selectedCourseCode}
          onChange={(val) => setSelectedCourseCode(val as string)}
          placeholder="Search for a course..."
        />
      </div>

      <div style={{ marginBottom: '30px' }}>
        <label style={{ display: 'block', marginBottom: '8px', color: '#aaa' }}>Select Professor</label>
        <SearchableDropdown
          options={professorOptions}
          value={selectedProfId}
          onChange={(val) => setSelectedProfId(val as string)}
          placeholder="Search for a professor..."
        />
      </div>

      <button
        onClick={handleAssign}
        disabled={assigning || !selectedCourseCode || !selectedProfId}
        style={{
          width: '100%',
          padding: '12px',
          backgroundColor: assigning ? '#555' : '#1976d2',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: assigning ? 'not-allowed' : 'pointer',
          fontWeight: 'bold',
          fontSize: '1rem'
        }}
      >
        {assigning ? 'Assigning...' : 'Assign Instructor'}
      </button>
    </div>
  );
};

export default CourseAssignment;
