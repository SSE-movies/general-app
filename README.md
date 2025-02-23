# Movie App

A Flask-based web application that allows users to browse, search, and manage their Netflix movies and TV shows watchlist. The application integrates with an Azure-hosted Netflix content database and uses Supabase for user management and watchlist features.

## Features (Coming Soon)
- User Authentication (Login/Register)
- Browse Netflix Content Catalog
- Search Movies and Shows by Title, Type, and Categories
- Personal Watchlist Management
- Admin Dashboard for User Management
- Responsive Design with Tailwind CSS and coherence of repeated components through js

## Components
- **`app.py`**: Main application entry point
- **`templates/`**: HTML templates
- **`requirements.txt`**: Python dependencies

## Prerequisites
- Python 3.12
- Node.js (for Tailwind CSS)
- Supabase Account
- Access to Azure Netflix Content API

## Installation

1. Clone the repository:
```bash
git clone git@github.com:SSE-movies/general-app.git
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Node.js dependencies:
```bash
npm install
```

5. Build Tailwind CSS:
```bash
npm run build:css
```

## Running the Application

1. Run the application:
```bash
flask run
```

## Testing
To run the test suite:
```bash
pytest
```

The test suite includes:
- Authentication Tests
- Netflix Content Search Tests
- Watchlist Management Tests
- Admin Functionality Tests

## CI/CD
The project uses GitHub Actions for continuous integration and deployment, including:
- Automated code formatting checks and improvements (black)
- Automated testing
- Dependency security scanning
- Deployment to ImPaaS

## API Integration
MovieApp integrates with:
- Azure Netflix Content API for movie and TV show catalog
- Supabase for user management and watchlist storage

## Security Features
- Password hashing with bcrypt
- Session-based authentication
- Protected routes with custom decorators
- Admin access control