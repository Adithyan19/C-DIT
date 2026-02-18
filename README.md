# KrishiRakshak — Crop Disease Advisor

AI-Powered Agricultural Advisory System using FastAPI, SvelteKit, and Supabase.

## Project Structure

- `backend/`: Python FastAPI application
  - `app/`: Core application logic
    - `routers/`: API endpoints (`analyze`, `chat`, `feedback`)
    - `services/`: RAG pipeline, Supabase client, and AI model placeholders
    - `models/`: Pydantic data models
    - `data/`: Disease knowledge base
  - `requirements.txt`: Python dependencies
  - `supabase_schema.sql`: Database schema for Supabase
- `src/`: SvelteKit frontend
  - `routes/`: Page routes (`/`, `/analyze`, `/history`, `/about`)
  - `lib/`: Shared components, stores, and API client

## Setup & Development

### Backend (Python/FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env`:
   ```env
   PORT=3001
   CORS_ORIGIN=http://localhost:5173
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```
4. Start the server:
   ```bash
   python -m app.main
   ```

### Frontend (SvelteKit)

1. Install dependencies:
   ```bash
   pnpm install
   ```
2. Start the development server:
   ```bash
   pnpm dev
   ```
3. Open `http://localhost:5173`.

## Database Setup

Run the SQL provided in `backend/supabase_schema.sql` in your Supabase SQL Editor to create the required tables for sessions, messages, and results.
