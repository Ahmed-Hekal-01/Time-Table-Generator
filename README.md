# 🎓 College Timetable Generator

An intelligent timetable scheduling system for Computer Science & IT (CSIT) colleges. This application automatically generates conflict-free timetables for multiple levels, groups, and sections while optimally assigning lab instructors and managing room allocations.

## ✨ Features

- **Automated Scheduling**: Generates complete timetables with zero conflicts
- **Multi-Level Support**: Handles Level 1 and Level 2 with multiple groups
- **Lab Instructor Assignment**: Intelligently assigns lab instructors based on qualifications and availability
- **Room Management**: Efficiently allocates lecture halls and lab rooms
- **Constraint Satisfaction**: Ensures no time, room, or instructor conflicts
- **Multiple Views**:
  - Combined Level Overview (Level 1 & 2 side-by-side)
  - Individual Section Schedules
  - Professor Timetables
  - Room Utilization Schedules
  - Lab Instructor Schedules
- **REST API**: Full-featured Flask API for integration
- **Modern Web UI**: React + TypeScript frontend with responsive design

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)

## 🏗 Architecture

The system consists of two main components:

### Backend (Python + Flask)
- **Scheduler Engine**: Core algorithm for timetable generation
- **Constraint Solver**: Ensures all scheduling rules are satisfied
- **Instructor Assignment**: Matches lab instructors to courses
- **REST API**: Provides JSON endpoints for data access

### Frontend (React + TypeScript + Vite)
- **Interactive Dashboard**: Displays all timetable views
- **Dynamic Updates**: Real-time data fetching from API
- **Responsive Design**: Works on desktop and mobile devices
- **Print-Friendly**: Optimized for PDF export

## 🚀 Installation

### Prerequisites

- Python 3.8+ (tested with Python 3.13)
- Node.js 18+ and npm
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ahmed-Hekal-01/Time-Table-Generator.git
   cd Time-Table-Generator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   cd Backend
   pip install -r req.txt
   ```

4. **Configure data files**

   Edit the CSV files in `Backend/CSV/`:
   - `rooms.csv` - Define available rooms (lecture halls and labs)
   - `inslab.csv` - Define lab instructors and their qualifications

5. **Run the backend server**
   ```bash
   python api.py
   ```

   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install Node dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## 📖 Usage

### Starting the Application

1. **Start the Backend API** (Terminal 1)
   ```bash
   cd Backend
   python api.py
   ```

2. **Start the Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**

   Open your browser and navigate to `http://localhost:5173`

### Viewing Timetables

The application provides multiple views accessible through the navigation menu:

- **Level Overview**: Combined view of Level 1 and Level 2 schedules side-by-side
- **Section Timetables**: Individual schedules for each section showing lectures and labs
- **Professor Timetables**: Weekly schedule for each professor
- **Room Timetables**: Utilization schedule for all lecture halls and lab rooms
- **Lab Instructor Timetables**: Weekly schedule for each lab instructor

### Regenerating Schedules

Click the "♻️ Regenerate Timetable" button to generate a new schedule with different room and time allocations.

## 📡 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Get Levels Table
```http
GET /api/levels
```
Returns timetable organized by levels and groups.

**Response:**
```json
{
  "metadata": {
    "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
    "time_slots": [
      {"slot": 1, "time": "9:00-10:30"},
      {"slot": 2, "time": "10:45-12:15"},
      {"slot": 3, "time": "12:30-14:00"},
      {"slot": 4, "time": "14:15-15:45"}
    ]
  },
  "levels": {
    "Level1": {
      "L1-G1": {
        "group_id": "L1-G1",
        "sections": ["L1-G1-S1", "L1-G1-S2", "L1-G1-S3"],
        "lectures": [...],
        "labs_by_section": {...}
      }
    }
  }
}
```

#### 2. Get Lab Instructors Table
```http
GET /api/lab-instructors
```
Returns schedule for each lab instructor.

#### 3. Get Professors Table
```http
GET /api/professors
```
Returns schedule for each professor.

#### 4. Get Rooms Table
```http
GET /api/rooms
```
Returns utilization schedule for all rooms.

#### 5. Health Check
```http
GET /api/health
```
Returns API status and scheduler information.

#### 6. Regenerate Schedule
```http
POST /api/regenerate
```
Generates a new timetable schedule.

See [API_README.md](./API_README.md) for detailed API documentation.

## 📁 Project Structure

```
Time-Table-Generator/
├── Backend/
│   ├── api.py                      # Flask REST API
│   ├── req.txt                     # Python dependencies
│   ├── CSV/
│   │   ├── rooms.csv               # Room definitions
│   │   └── inslab.csv              # Lab instructor definitions
│   ├── app/
│   │   ├── __init__.py             # Package initialization
│   │   ├── models.py               # Data models
│   │   ├── scheduler.py            # Core scheduling algorithm
│   │   ├── data_loader.py          # CSV data loading
│   │   ├── instructor_assignment.py # Lab instructor assignment
│   │   ├── constraints.py          # Constraint checking
│   │   ├── trackers.py             # State tracking
│   │   ├── validators.py           # Schedule validation
│   │   └── exporters.py            # CSV/JSON export
│   └── generated/                  # Generated timetable files
├── frontend/
│   ├── package.json                # Node dependencies
│   ├── tsconfig.json               # TypeScript configuration
│   ├── vite.config.ts              # Vite configuration
│   ├── index.html                  # HTML entry point
│   └── src/
│       ├── App.tsx                 # Main React component
│       ├── main.tsx                # React entry point
│       └── CSS/
│           └── index.css           # Styles
├── API_README.md                   # API documentation
└── README.md                       # This file
```

## ⚙️ Configuration

### Course Configuration

Edit `Backend/app/data_loader.py` to configure:
- Courses for Level 1 and Level 2
- Lecture instructors
- Lab courses and requirements

### Room Configuration

Edit `Backend/CSV/rooms.csv`:
```csv
room_code,room_type,capacity,building
A101,lec,60,Building A
Lab1,lab,30,Building B
```

### Lab Instructor Configuration

Edit `Backend/CSV/inslab.csv`:
```csv
instructor_id,instructor_name,qualified_labs,max_hours_per_week,instructor_type
INS001,John Doe,PHY111|CHM111|BIO111,12,full-time
INS002,Jane Smith,CSC211|MTH211,10,part-time
```

### Time Slots

Modify in `Backend/app/data_loader.py`:
```python
time_slots = [
    TimeSlot(1, "Sunday", "9:00-10:30", 1),
    TimeSlot(2, "Sunday", "10:45-12:15", 2),
    # ... add more slots
]
```

## 🛠 Technology Stack

### Backend
- **Python 3.13** - Core programming language
- **Flask 2.3+** - Web framework
- **Flask-CORS 4.0+** - Cross-origin resource sharing

### Frontend
- **React 19** - UI library
- **TypeScript 5.9** - Type-safe JavaScript
- **Vite 7** - Build tool and dev server
- **CSS3** - Styling

## 📝 Key Features Explained

### Scheduling Algorithm
The scheduler uses a constraint satisfaction approach:
1. Assigns lectures to time slots ensuring no group conflicts
2. Distributes labs across sections avoiding instructor conflicts
3. Allocates rooms based on type (lecture vs lab)
4. Validates all assignments before finalizing

### Lab Instructor Assignment
- Matches instructors to labs based on qualifications
- Respects maximum hours per week limits
- Balances workload across instructors
- Prioritizes full-time instructors

### Conflict Prevention
- No student group in two places at once
- No instructor teaching two classes simultaneously
- No room double-booked for same time slot
- All courses assigned required number of hours

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available for educational purposes.

## 👥 Authors

- **Ahmed Hekal** - [@Ahmed-Hekal-01](https://github.com/Ahmed-Hekal-01)

## 🙏 Acknowledgments

- CSIT Department for requirements specification
- Open source community for tools and libraries

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team

## 🔮 Future Enhancements

- [ ] Database integration for persistent storage
- [ ] User authentication and role management
- [ ] Advanced constraint customization UI
- [ ] Multi-semester planning
- [ ] Conflict resolution suggestions
- [ ] PDF export functionality
- [ ] Email notifications for schedule changes
- [ ] Mobile app version

---

**Built with ❤️ for efficient academic scheduling**
