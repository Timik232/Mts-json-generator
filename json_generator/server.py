import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .agents import ChatManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно указать список доменов
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST и др.
    allow_headers=["*"],  # Заголовки, например Content-Type
)
chat_manager = ChatManager()


@app.get("/")
async def root():
    return {"message": "Json generator API is working"}


class ChatRequest(BaseModel):
    session_id: str
    message: str


class SessionID(BaseModel):
    session_id: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    json_schema: dict | str = ""


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        res = await chat_manager.handle_message(req.session_id, req.message)
        return ChatResponse(
            session_id=req.session_id,
            response=res["message"],
            json_schema=res["json_schema"],
        )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/clear")
async def clear(session_id: SessionID):
    try:
        res = chat_manager.clear_messages(session_id.session_id)
        if res:
            return JSONResponse(
                content={"detail": "Messages cleared successfully"}, status_code=200
            )
        else:
            return JSONResponse(
                content={"detail": "Failed to clear messages"}, status_code=500
            )
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e)) from e
