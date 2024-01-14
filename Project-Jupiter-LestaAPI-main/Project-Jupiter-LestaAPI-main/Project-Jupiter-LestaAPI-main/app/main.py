from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import sqlite3
from pathlib import Path

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

# Инициализация базы данных SQLite
conn = sqlite3.connect("request_history.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history
             (id INTEGER PRIMARY KEY AUTOINCREMENT, nickname TEXT, request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# Модель для хранения данных запроса
class RequestHistory(BaseModel):
    id: int
    nickname: str

# Функция для сохранения данных запроса в базе данных
def save_request_history(nickname: str):
    c.execute("INSERT INTO history (nickname) VALUES (?)", (nickname,))
    conn.commit()

# Функция для получения данных
def get_data(nickname):
    key = "a1b084fb734c833b6394496ded650f97"
    selects = "tanks"
    search = "account_id"
    response = requests.get(f'https://api.tanki.su/wot/account/{selects}/?application_id={key}&{search}={nickname}')
    save_request_history(nickname)  # Сохранение истории запросов
    return response.json()

@app.get("/")
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/")
async def read_form(request: Request, nickname: str = Form(...)):
    result = get_data(nickname)
    return templates.TemplateResponse("result.html", {"request": request, "result": result})

@app.get("/history")
async def history(request: Request):
    c.execute("SELECT * FROM history")
    history_records = c.fetchall()
    return templates.TemplateResponse("history.html", {"request": request, "history_records": history_records})