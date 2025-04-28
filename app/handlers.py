import html
import json
from datetime import datetime
from io import BytesIO

import aiohttp
import fitz
from bs4 import BeautifulSoup
from fastapi import HTTPException, Request, Response

from app.field_map import FIELD_NAMES, human_to_pdf
from app.tools import split_date_fields


# TODO: разделить на функции получения авторизации и парсинга
async def fetch_and_prepare_data(year, id, subdomain, login, password):
    """
    Получение данных ученика и организации из внешнего API ХХ.

    Аргументы:
        year (int): Год для запроса платежей.
        id (int): Идентификатор ученика-клиента в системе.
        subdomain (str): Субдомен для подключения к API.
        login (str): Логин пользователя для авторизации.
        password (str): Пароль пользователя для авторизации.

    Возвращает:
        dict: Словарь с подготовленными данными для заполнения PDF-формы.
    """

    url = f"https://{subdomain}.t8s.ru"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            data={"LogLogin": login, "LogPassword": password},
            allow_redirects=False,
        ) as r:
            if r.status != 302:
                raise Exception("Неверные данные для входа")
            cookie = r.cookies.get(".ASPXAUTH")
            if not cookie:
                raise Exception("Кука авторизации не найдена")
            token = cookie.value

    headers = {"Cookie": f".ASPXAUTH={token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f"{url}/Api/V2/GetStudents?Id={id}") as r:
            student = (await r.json())["Students"][0]

        st_data = {
            "student_first_name": student.get("FirstName"),
            "student_last_name": student.get("LastName"),
            "student_middle_name": student.get("MiddleName"),
            "student_birthday": student.get("Birthday"),
            "client_id": student.get("ClientId"),
            "doc_number": student.get("Id"),
        }

        agent = next((a for a in student.get("Agents", []) if a.get("IsCustomer")), {})
        customer = (
            {
                "payer_first_name": agent.get("FirstName"),
                "payer_last_name": agent.get("LastName"),
                "payer_middle_name": agent.get("MiddleName"),
            }
            if agent
            else {}
        )

        async with session.get(
            f"{url}/Api/V2/GetPayments?&clientId="
            f"{st_data['client_id']}&paidDateFrom={year}-01-01"
            f"&paidDateTo={year}-12-31&state=4"
        ) as r:
            payments = (await r.json()).get("Payments", [])
            total = sum(p.get("ValueQuantity", 0) for p in payments)

        async with session.get(f"{url}/School/EditBankingDetails") as r:
            soup = BeautifulSoup(await r.text(), "html.parser")
            company_data = {}
            for div in soup.find_all("div", class_="col-8"):
                inp = div.find("input")
                if inp and (val := inp.get("value")):
                    key = inp.get("id").split("_")[1]
                    company_data[key] = html.unescape(val)

    now = datetime.now()
    money = f"{total:.2f}".split(".")
    title = company_data.get("CompanyName", "")
    parts = title.split()
    title_parts = []
    line = ""
    for word in parts:
        if len(line + " " + word) > 30 and len(title_parts) < 3:
            title_parts.append(line.strip())
            line = word
        else:
            line += " " + word
    title_parts.append(line.strip())
    while len(title_parts) < 4:
        title_parts.append("")

    chief = company_data.get("Chief", "").split()
    while len(chief) < 3:
        chief.append("")

    data = {
        "org_inn": company_data.get("INN"),
        "org_kpp": company_data.get("KPP"),
        "correction_number": "---",
        "year": year,
        "org_name_1": title_parts[0],
        "org_name_2": title_parts[1],
        "org_name_3": title_parts[2],
        "org_name_4": title_parts[3],
        "org_head_last_name": chief[0],
        "org_head_first_name": chief[1],
        "org_head_middle_name": chief[2],
        "doc_day": now.strftime("%d"),
        "doc_month": now.strftime("%m"),
        "doc_year": now.strftime("%Y"),
        "amount_rub": money[0],
        "amount_kop": money[1],
        "doc_number": st_data["doc_number"],
    }

    if customer:
        data.update(customer)
        data["same_person"] = "0"
        data.update(
            {
                "student_last_name": st_data["student_last_name"],
                "student_first_name": st_data["student_first_name"],
                "student_middle_name": st_data["student_middle_name"],
            }
        )
        if bd := st_data["student_birthday"]:
            y, m, d = bd.split("-")
            data.update(
                {
                    "student_birth_day": d,
                    "student_birth_month": m,
                    "student_birth_year": y,
                }
            )
    else:
        data.update(
            {
                "payer_first_name": st_data["student_first_name"],
                "payer_last_name": st_data["student_last_name"],
                "payer_middle_name": st_data["student_middle_name"],
                "same_person": "1",
            }
        )
        if bd := st_data["student_birthday"]:
            y, m, d = bd.split("-")
            data.update(
                {"payer_birth_day": d, "payer_birth_month": m, "payer_birth_year": y}
            )

    return data


async def fill_pdf_document(request: Request) -> Response:
    """
    Генерация заполненного PDF-документа на основе данных из запроса.

    Аргументы:
        request (Request): HTTP-запрос с данными формы в формате JSON или формы.

    Возвращает:
        Response: Ответ с готовым PDF-файлом в бинарном формате.
    """
    try:
        form = await request.json()
    except json.JSONDecodeError:
        try:
            form = await request.form()
            form = dict(form)
        except Exception:
            raise HTTPException(
                status_code=400, detail="Некорректный формат передаваемых данных"
            )

    if not form:
        raise HTTPException(
            status_code=400, detail="В запросе отсутствуют данные для обработки"
        )

    split_date_fields(
        form,
        [
            "payer_doc_issue_full",
            "doc_date_full",
            "payer_birth_date_full",
            "student_birth_date_full",
            "student_doc_issue_date_full",
        ],
    )

    fields = human_to_pdf({k: v for k, v in form.items()})
    restricted_for_padding = (
        FIELD_NAMES.get("same_person"),
        FIELD_NAMES.get("education_form"),
    )
    padded = {
        k: (v.upper().ljust(40, "-") if k not in restricted_for_padding else v)
        for k, v in fields.items()
    }

    doc = fitz.open("static/template.pdf")
    for page in doc:
        for field in page.widgets():
            if field.field_name in padded:
                field.text_font = "Cour"
                field.text_fontsize = 16
                field.field_value = padded[field.field_name]
                field.update()

    doc.bake()
    pages = 1 if fields.get("Text14.0") == "1" else 2
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=0, to_page=pages - 1)
    pdf_stream = BytesIO()
    new_doc.save(pdf_stream)
    doc.close()
    new_doc.close()
    pdf_stream.seek(0)

    return Response(
        pdf_stream.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=form_filled.pdf"},
    )
