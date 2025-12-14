import { useState } from 'react';
import Admin from './Admin';
import Student from './Student';
import Prof from './Prof';
import TA from './TA';

export const Home = () => {
  const [currentView, setCurrentView] = useState('home');

  const renderView = () => {
    switch (currentView) {
      case 'admin':
        return <Admin />;
      case 'student':
        return <Student />;
      case 'prof':
        return <Prof />;
      case 'ta':
        return <TA />;
      default:
        return (
          <div className="home-container">
            <h1>Welcome to TimeTabe generator </h1>
            <div className="button-group">
              <button className="nav-button" onClick={() => setCurrentView('admin')}>Admin</button>
              <button className="nav-button" onClick={() => setCurrentView('student')}>Student</button>
              <button className="nav-button" onClick={() => setCurrentView('prof')}>Professor</button>
              <button className="nav-button" onClick={() => setCurrentView('ta')}>TA</button>
            </div>
          </div>
        );
    }
  };

  return (
    <>
      {currentView !== 'home' && (
        <button className="back-button" onClick={() => setCurrentView('home')}>Back to Home</button>
      )}
      {renderView()}
    </>
  );
};

