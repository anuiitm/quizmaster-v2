# QuizMaster - Data Export System

This application includes a comprehensive data export system using Celery background tasks for both user and admin exports.

## Features

### User Exports
- **Quiz History Export**: Users can export their complete quiz history to CSV format
- **Real-time Status**: Progress tracking with modal notifications
- **Automatic Download**: Files are automatically downloaded when ready

### Admin Exports  
- **User Performance Export**: Admins can export all user performance data to CSV
- **Comprehensive Data**: Includes total quizzes, average scores, highest/lowest scores, and last quiz dates
- **Background Processing**: Large exports are handled asynchronously

## Setup Instructions

### 1. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies  
cd ../frontend
npm install
```

### 2. Install and Start Redis

Redis is required for Celery message broker and result backend.

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Windows:**
Download from https://redis.io/download or use WSL.

### 3. Start the Application

**Terminal 1 - Flask Backend:**
```bash
cd backend
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

**Terminal 2 - Celery Worker:**
```bash
python celery_worker.py
```

**Terminal 3 - Vue Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Usage

#### User Export
1. Login as a regular user
2. Navigate to "Scores" page
3. Click "Export to CSV" button
4. Wait for processing (modal will show progress)
5. Click "Download CSV" when ready

#### Admin Export
1. Login as admin
2. Navigate to "Users" page  
3. Click "Export Performance Data" button
4. Wait for processing (modal will show progress)
5. Click "Download CSV" when ready

## File Structure

```
backend/
├── api/
│   ├── admin.py          # Admin export endpoints
│   └── user.py           # User export endpoints
├── tasks.py              # Celery background tasks
├── celery_app.py         # Celery configuration
├── requirements.txt      # Python dependencies
└── app.py               # Flask app with Celery init

frontend/
├── src/views/
│   ├── UserScores.vue   # User export UI
│   └── AdminUsers.vue   # Admin export UI
└── ...

celery_worker.py          # Celery worker script
exports/                  # Generated CSV files
```

## API Endpoints

### User Export
- `POST /api/user/export/quiz-history` - Start quiz history export
- `GET /api/user/export/status/<task_id>` - Check export status
- `GET /api/user/export/download/<filename>` - Download CSV file

### Admin Export
- `POST /api/admin/export/user-performance` - Start user performance export
- `GET /api/admin/export/status/<task_id>` - Check export status  
- `GET /api/admin/export/download/<filename>` - Download CSV file

## CSV Format

### User Quiz History
- Quiz ID, Subject, Chapter, Quiz Date, Score, Date Taken

### Admin User Performance
- User ID, User Name, Email, Total Quizzes Taken, Average Score, Highest Score, Lowest Score, Last Quiz Date

## Troubleshooting

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping
# Should return "PONG"
```

### Celery Worker Issues
```bash
# Check Celery worker status
celery -A backend.celery_app.celery status
```

### Export Directory Permissions
```bash
# Ensure exports directory is writable
chmod 755 exports/
```

## Configuration

Environment variables can be set in `.env`:
```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
FLASK_SECRET_KEY=your-secret-key
``` 