const Loader = () => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '400px',
      flexDirection: 'column',
      gap: '20px'
    }}>
      <div style={{
        border: '4px solid #f3f3f3',
        borderTop: '4px solid #673AB7',
        borderRadius: '50%',
        width: '50px',
        height: '50px',
        animation: 'spin 1s linear infinite'
      }} />
      <p style={{ color: '#673AB7', fontSize: '1.1rem' }}>Loading timetable...</p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Loader;
