# Quickstart: Todo Full-Stack Web Application

**Feature**: 004-fullstack-todo-app
**Date**: 2026-01-15

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Neon PostgreSQL account (or compatible PostgreSQL)
- Git

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd todo_Application
git checkout 004-fullstack-todo-app
```

### 2. Database Setup

Create a Neon PostgreSQL database and note the connection string.

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create `.env.local`:
```env
# Better Auth Configuration
BETTER_AUTH_SECRET=<your-32-character-secret>
BETTER_AUTH_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Database URL (PostgreSQL format for Better Auth)
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
```

Initialize Better Auth tables (first time only):
```bash
node create-auth-tables.mjs
```

### 4. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env`:
```env
# Better Auth Configuration (same secret as frontend)
BETTER_AUTH_SECRET=<your-32-character-secret>

# Database URL (asyncpg format for FastAPI)
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>/<database>?ssl=require

# Debug mode
DEBUG=true
ENVIRONMENT=development
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd todo_Application
python -m uvicorn backend.main:app --port 8000 --reload
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:3000

## Verification

1. Open http://localhost:3000
2. Click "Sign Up" and create an account
3. After signup, you should be redirected to the dashboard
4. Try creating, editing, completing, and deleting tasks

## API Testing

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Test with authentication (replace tokens):
```bash
# List tasks
curl -H "Authorization: Bearer <session-token>" \
  http://localhost:8000/api/v1/users/<user-id>/tasks

# Create task
curl -X POST -H "Authorization: Bearer <session-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task"}' \
  http://localhost:8000/api/v1/users/<user-id>/tasks
```

## Troubleshooting

### "Failed to fetch" on frontend
- Check backend is running on port 8000
- Verify CORS allows http://localhost:3000
- Check browser console for detailed errors

### "Invalid credentials" / 401 errors
- Ensure BETTER_AUTH_SECRET matches in frontend and backend
- Verify session exists in database
- Check session hasn't expired

### Database connection errors
- Verify DATABASE_URL format (different for frontend vs backend)
- Frontend: `postgresql://...?sslmode=require`
- Backend: `postgresql+asyncpg://...?ssl=require`
- Check Neon database is active (auto-suspend after inactivity)

### Port already in use
- Kill existing processes: `taskkill /F /IM python.exe` (Windows)
- Or use different ports: `--port 8001`

## Project Structure

```
todo_Application/
├── frontend/               # Next.js application
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utilities and auth config
│   └── types/             # TypeScript definitions
├── backend/               # FastAPI application
│   ├── auth/              # Authentication middleware
│   ├── models/            # SQLModel entities
│   ├── routes/            # API endpoints
│   └── tests/             # Backend tests
└── specs/                 # Feature specifications
    └── 004-fullstack-todo-app/
        ├── spec.md        # Feature specification
        ├── plan.md        # Implementation plan
        ├── research.md    # Design research
        ├── data-model.md  # Entity definitions
        └── contracts/     # API contracts
```
