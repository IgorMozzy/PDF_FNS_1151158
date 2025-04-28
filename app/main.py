import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.handlers import fetch_and_prepare_data, fill_pdf_document
from app.settings import get_settings

app = FastAPI(
    docs_url=None,  # Отключает Swagger UI (/docs)
    redoc_url=None,  # Отключает ReDoc (/redoc)
    openapi_url=None,  # Отключает OpenAPI JSON (/openapi.json)
)

settings = get_settings()

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


@app.get("/", response_class=FileResponse)
async def get_index():
    """Отдаёт главную страницу HTML."""
    return FileResponse(f"{settings.static_dir}/index.html")


@app.post("/fetch_data")
async def fetch_data(
    year: int = Form(...),
    id: int = Form(...),
    subdomain: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
):
    """
    Получение данных ученика из внешнего API.

    Аргументы:
        year (int): Год для запроса данных.
        id (int): Идентификатор ученика.
        subdomain (str): Субдомен для подключения к API.
        login (str): Логин пользователя.
        password (str): Пароль пользователя.

    Возвращает:
        JSON-ответ с данными ученика.
    """

    data = await fetch_and_prepare_data(year, id, subdomain, login, password)
    return JSONResponse(content=data)


@app.post("/fill_pdf/")
async def fill_pdf(request: Request):
    """
    Генерирует PDF справку.

    Аргументы:
        request: HTTP-запрос с данными формы.

    Возвращает:
        HTTP-ответ с PDF-файлом.
    """
    response = await fill_pdf_document(request)
    return response

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host,
                port=settings.port, reload=settings.reload)
