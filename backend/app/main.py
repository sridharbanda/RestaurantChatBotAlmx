import json, os, uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from .mcp_client import get_mcp_tool_schemas, execute_mcp_tool, get_mcp_tools_metadata

load_dotenv()
app = FastAPI(title="TableTalk Restaurant Chatbot")
origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS","http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

sessions = {}

SYSTEM_PROMPT = (
    "You are TableTalk, a specialized restaurant assistant. "
    "You are strictly limited to restaurants and restaurant-related topics (such as dining, cuisines, menus, food, dishes, pricing, locations, ratings, and restaurant recommendations). "
    "CRITICAL RULE: If a user queries or asks about anything other than restaurants (for example: general knowledge, coding, math, science, sports, politics, weather, movies, history, health, personal advice, or any non-restaurant topic), you must NOT answer the question and you must NOT invoke any tools. "
    "Instead, you must respond strictly with: 'I am limited to restaurants only.' "
    "For restaurant-related questions, use tools for factual restaurant questions. Never invent facts; all data is fictional demo data. "
    "Price level 1=budget, 2=moderate, 3=premium. Be concise."
)

def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict) and "text" in p:
                parts.append(p["text"])
            elif isinstance(p, str):
                parts.append(p)
            else:
                parts.append(str(p))
        return "".join(parts).strip()
    return str(content)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/tools")
async def list_tools():
    return await get_mcp_tools_metadata()

@app.post("/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(503, "Set GOOGLE_API_KEY in backend/.env")
    sid = req.session_id or str(uuid.uuid4())
    history = sessions.setdefault(sid, [])
    tool_schemas = await get_mcp_tool_schemas()
    model = ChatGoogleGenerativeAI(
        model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
        google_api_key=api_key,
        temperature=0.2
    ).bind_tools(tool_schemas)

    msgs = [SystemMessage(content=SYSTEM_PROMPT), *history, HumanMessage(content=req.message)]
    calls_used, result_restaurants = [], []
    try:
        for _ in range(6):
            ai = await model.ainvoke(msgs)
            msgs.append(ai)
            calls = getattr(ai, "tool_calls", []) or []
            if not calls:
                answer = extract_text(ai.content)
                sessions[sid] = (history + [HumanMessage(content=req.message), AIMessage(content=answer)])[-20:]
                return {"response": answer, "session_id": sid, "restaurants": result_restaurants, "tool_calls": calls_used}
            for call in calls:
                name, args = call["name"], call.get("args", {})
                content_str, is_error, found_restaurants = await execute_mcp_tool(name, args)
                status = "error" if is_error else "success"
                calls_used.append({"tool_name": name, "status": status})
                result_restaurants.extend(found_restaurants)
                msgs.append(ToolMessage(content=content_str, tool_call_id=call["id"]))
        raise HTTPException(500, "Tool-call limit reached. Try a shorter question.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, f"Chat provider error: {str(exc)}")
