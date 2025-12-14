import { useState } from 'react';
import Admin from './Admin';
import Student from './Student';
import Prof from './Prof';
import TA from './TA';

export const Home = () => {
  const [currentView, setCurrentView] = useState('home');

  const goToHome = () => setCurrentView('home');

  const renderView = () => {
    switch (currentView) {
      case 'admin':
        return <Admin onBackToHome={goToHome} />;
      case 'student':
        return <Student onBackToHome={goToHome} />;
      case 'prof':
        return <Prof onBackToHome={goToHome} />;
      case 'ta':
        return <TA onBackToHome={goToHome} />;
      default:
        return (
          <div className="home-container">
            <h1>Welcome to Timetable Generator</h1>
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
      {renderView()}
    </>
  );
};

