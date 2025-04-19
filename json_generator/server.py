from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно указать список доменов
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST и др.
    allow_headers=["*"],  # Заголовки, например Content-Type
)


@app.get("/")
async def root():
    return {"message": "Json generator API is working"}


@app.post("/chat")
async def llm_chat(json_data: Dict) -> Dict:
    try:
        return json_data

    except Exception as e:
        return {"error": f"Ошибка чтения файла: {str(e)}"}
