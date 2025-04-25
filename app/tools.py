from typing import Dict, List

from fastapi import HTTPException


def split_date_fields(form: Dict[str, str], date_fields: List[str]) -> None:
    """
    Разбивает даты в формате YYYY-MM-DD на отдельные поля года, месяца и дня.

    Аргументы:
        form (dict): Словарь с данными формы, где содержатся даты.
        date_fields (list): Список полей с полными датами (..._date_full).

    Возвращает:
        None
    """
    for field_name in date_fields:
        date_str = form.get(field_name)
        if date_str:
            try:
                year, month, day = date_str.split("-")
                base = field_name.replace("_date_full", "")
                form[f"{base}_year"] = year
                form[f"{base}_month"] = month
                form[f"{base}_day"] = day
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Некорректный формат даты в поле '{field_name}'"
                    f": ожидается YYYY-MM-DD",
                )
