# Calls Helper

MVP booking service for calls (mini-Calendly). Allows creating free time slots and sharing a public link for booking.

## Features

- ✅ Create booking sessions with unique links
- ✅ Create time slots for each session
- ✅ Public page for slot booking
- ✅ Automatic booking management
- ✅ Protection against double booking

## Tech Stack

- **Backend**: Django 4.2.27
- **Database**: PostgreSQL
- **Python**: 3.9+

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd "Calls helper"
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Create PostgreSQL database:

```sql
CREATE DATABASE calls_helper_db;
CREATE USER calls_helper_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE calls_helper_db TO calls_helper_user;
```

### 5. Environment Variables

Create `.env` file in project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=calls_helper_db
DB_USER=calls_helper_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Run Migrations

```bash
cd callhelper
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Run Server

```bash
python manage.py runserver
```

Application will be available at: http://127.0.0.1:8000/


## Data Models

### BookingSession
Group of time slots with a single public link.

### TimeSlot
Time slot for booking, linked to a session.

## API Endpoints

- `/` - Dashboard (requires authentication)
- `/slots/` - User's slots list
- `/slots/create/` - Create new slot
- `/public/<public_link>/` - Public booking page

## Development

### Create Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run Tests

```bash
python manage.py test
```

## License

MIT
