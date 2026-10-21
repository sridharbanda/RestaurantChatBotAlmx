# TableTalk Restaurant Chatbot

## Run backend
1. Install Python 3.10+.
2. `cd backend`
3. Create and activate a virtual environment.
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`, then set `GOOGLE_API_KEY`.
6. Run `uvicorn app.main:app --reload --port 8000`.

API docs: http://localhost:8000/docs

## Architecture
The application consists of 3 distinct components:
- `backend/`: FastAPI application, LangChain chat agent, session management, and MCP client bridge.
- `frontend/`: React + Vite interactive UI for chatting and discovering restaurants.
- `mcp_server/`: Standalone Model Context Protocol (MCP) server providing restaurant tools, resources, and prompts.

## MCP Server (Model Context Protocol)
The restaurant tools and catalog are available via the standalone `mcp_server` folder:
- **Stdio transport (Claude Desktop / Cursor / Antigravity):**
  ```bash
  cd mcp_server
  python server.py
  # or
  python -m mcp_server
  ```
- **SSE transport (Web / Remote):**
  Accessible under `/mcp/sse` when the FastAPI backend is running (`http://localhost:8000/mcp/sse`).

Available MCP tools:
- `search_restaurants`
- `get_restaurant_details`
- `get_restaurant_menu`
- `find_vegetarian_restaurants`
- `filter_restaurants_by_rating`
- `recommend_restaurants`
- `compare_restaurants`
- `get_restaurant_contact`

Available MCP resources:
- `restaurants://catalog`
- `restaurants://{restaurant_id}`

## Run frontend
1. In another terminal: `cd frontend`
2. `npm install`
3. Copy `.env.example` to `.env`.
4. Run `npm run dev`; open http://localhost:5173.

## Deploy
**Render backend:** Root directory `backend`; build `pip install -r requirements.txt`; start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set `GOOGLE_API_KEY`, `LLM_MODEL`, and `ALLOWED_ORIGINS` (your Vercel URL).

**Vercel frontend:** Root directory `frontend`; build `npm run build`; output `dist`; set `VITE_API_BASE_URL` to the Render backend URL.

All 15 restaurants, addresses, phone numbers, and menus are fictional sample data. Session history is in memory and resets on server restart; use Redis/database for production.
