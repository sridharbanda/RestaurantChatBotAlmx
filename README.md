# TableTalk Restaurant Chatbot

## Run backend
1. Install Python 3.10+.
2. `cd backend`
3. Create and activate a virtual environment.
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`, then set `GOOGLE_API_KEY`.
6. Run `uvicorn app.main:app --reload --port 8000`.

API docs: http://localhost:8000/docs

## Run frontend
1. In another terminal: `cd frontend`
2. `npm install`
3. Copy `.env.example` to `.env`.
4. Run `npm run dev`; open http://localhost:5173.

## Deploy
**Render backend:** Root directory `backend`; build `pip install -r requirements.txt`; start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set `GOOGLE_API_KEY`, `LLM_MODEL`, and `ALLOWED_ORIGINS` (your Vercel URL).

**Vercel frontend:** Root directory `frontend`; build `npm run build`; output `dist`; set `VITE_API_BASE_URL` to the Render backend URL.

All 15 restaurants, addresses, phone numbers, and menus are fictional sample data. Session history is in memory and resets on server restart; use Redis/database for production.
