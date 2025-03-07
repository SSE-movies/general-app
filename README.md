# Movie App

A Flask-based web application that allows users to browse, search, and manage their Netflix movies and TV shows watchlist. The application integrates with an Azure-hosted Netflix content database and uses Supabase for user management and watchlist features.

## Features
- User Authentication (Login/Register)
- Browse Netflix Content Catalog
- Search Movies and Shows by:
  - Title
  - Type (Movie or TV Show)
  - Categories
  - Release Year
- Personal Watchlist Management
- Responsive Design with Tailwind CSS

## Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Database**: Supabase
- **Content API**: Azure-hosted Netflix Content API
- **Authentication**: Flask-Session with Supabase JWT tokens (users remain logged in across page refreshes using secure HTTP-only cookies)

## Project Structure
- **`src/app.py`**: Main application entry point
- **`src/auth.py`**: Authentication routes and logic
- **`src/database.py`**: Database and API interaction
- **`src/search.py`**: Search functionality
- **`src/watchlist.py`**: Watchlist management
- **`src/templates/`**: HTML templates
- **`src/static/`**: Static assets (CSS, JS)
- **`unit_tests/`**: Test suite
- **`requirements.txt`**: Python dependencies

## Prerequisites
- Python 3.12
- Node.js (for Tailwind CSS)
- Supabase Account
- Access to Azure Netflix Movie Backend API
- Access to Azure Watchlist Backend API

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

4. Set up environment variables:

5. Install Node.js dependencies (if using Tailwind):
```bash
npm install
```

6. Build Tailwind CSS:
```bash
npm run build:css
```

## Running the Application

1. Run the application:
```bash
flask run
```

2. Access the application at http://127.0.0.1:5000

## Key Features Implementation

### Search Functionality
- Search by title
- Filter by movie type (Movie or TV Show)
- Filter by categories with multi-select
- Filter by release year
- Pagination for search results

### Special Character Handling
The application properly handles special characters in search queries, including:
- Ampersands (&) in category names
- Spaces in titles and categories
- Special characters in movie titles

## Testing
To run the test suite:
```bash
pytest
```

The test suite includes:
- Authentication Tests
- Netflix Content Search Tests
- Watchlist Management Tests

## CI/CD
The project uses GitHub Actions for continuous integration and deployment, including:
- Automated code formatting checks (black, flake8)
- Automated testing
- Pylint
- Dependency security scanning
- Deployment to Azure

## API Integration
MovieApp integrates with:
- Azure Movies Content API for movie and TV show catalog
- Azure Watchlist API
- Supabase for user management and watchlist storage

## Security Features
- Password hashing with bcrypt
- Session-based authentication
- Protected routes with custom decorators