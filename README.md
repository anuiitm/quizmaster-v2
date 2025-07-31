# QuizMaster - Complete Quiz Management System

A comprehensive quiz application built with Vue.js frontend and Flask backend, featuring user authentication, quiz creation, taking, and performance tracking.

## Features

### Admin Features
- **Subject Management**: Create, edit, and delete subjects
- **Chapter Management**: Organize content by chapters within subjects
- **Quiz Creation**: Create quizzes with multiple choice questions
- **User Management**: View all users and their performance
- **Performance Analytics**: View summary statistics and charts
- **User Search**: Search for users and their quiz results

### User Features
- **Quiz Taking**: Take quizzes with timer functionality
- **Score Tracking**: View detailed score history
- **Search Functionality**: Search for quizzes and subjects
- **Performance Summary**: View overall performance statistics

## Technologies Used

### Frontend
- **Vue.js 3** (Composition API)
- **Vue Router** for navigation
- **Axios** for HTTP requests
- **Bootstrap 5** for styling
- **Vite** for build tooling

### Backend
- **Flask** web framework
- **SQLAlchemy** ORM
- **SQLite** database
- **Flask-Login** for authentication
- **Flask-WTF** for CSRF protection
- **Celery** for background tasks
- **Redis** for message broker

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

Redis is required for Celery message broker.

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
flask run --port=5001
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

### 4. Database Setup

The application uses SQLite database which will be created automatically on first run.

## API Design

### Authentication
- **POST** `/api/auth/login` - User login
- **POST** `/api/auth/register` - User registration
- **POST** `/api/auth/logout` - User logout

### Admin Endpoints
- **GET** `/api/admin/subjects` - Get all subjects
- **POST** `/api/admin/subject` - Create subject
- **PUT** `/api/admin/subject/<id>` - Update subject
- **DELETE** `/api/admin/subject/<id>` - Delete subject
- **GET** `/api/admin/users` - Get all users
- **GET** `/api/admin/summary` - Get admin summary data
- **GET** `/api/admin/search/quizzes` - Search quizzes

### User Endpoints
- **GET** `/api/user/dashboard` - Get user dashboard data
- **GET** `/api/user/quizzes` - Get available quizzes
- **POST** `/api/user/quiz/<id>/submit` - Submit quiz answers
- **GET** `/api/user/scores` - Get user scores
- **GET** `/api/user/search` - Search quizzes and subjects

## File Structure

```
backend/
├── api/
│   ├── admin.py          # Admin API endpoints
│   ├── auth.py           # Authentication endpoints
│   ├── user.py           # User API endpoints
│   └── cache.py          # Cache management
├── models/
│   └── model.py          # Database models
├── utils/
│   ├── cache.py          # Caching utilities
│   ├── decorators.py     # Custom decorators
│   └── performance.py    # Performance utilities
├── tasks.py              # Celery background tasks
├── celery_app.py         # Celery configuration
├── requirements.txt      # Python dependencies
└── app.py               # Flask application

frontend/
├── src/
│   ├── components/       # Vue components
│   ├── views/           # Page components
│   ├── router/          # Vue Router configuration
│   ├── stores/          # Pinia stores
│   └── api/             # API client configuration
├── public/              # Static assets
└── package.json         # Node.js dependencies
```

## Security Features

- **CSRF Protection**: All forms protected with CSRF tokens
- **Session-based Authentication**: Secure user sessions
- **Input Validation**: Server-side validation for all inputs
- **Rate Limiting**: API rate limiting for abuse prevention

## Performance Features

- **Background Processing**: Celery tasks for heavy operations
- **Caching**: Redis-based caching for improved performance
- **Optimized Queries**: Efficient database queries with SQLAlchemy

## Development

The application is built with modern development practices:
- **Hot Reload**: Frontend development with Vite
- **Type Safety**: JavaScript with proper typing
- **Code Formatting**: Prettier and ESLint for code quality
- **Modular Architecture**: Clean separation of concerns
