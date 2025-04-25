FIELD_NAMES = {
    "org_inn": "Text1",
    "org_kpp": "Text2",
    "doc_number": "Text4",
    "correction_number": "Text5.0",
    "year": "Text3",
    "org_name_1": "Text6.0",
    "org_name_2": "Text6.1",
    "org_name_3": "Text6.2",
    "org_name_4": "Text6.3",
    "education_form": "Text14.1",
    "payer_last_name": "Text7.0",
    "payer_first_name": "Text7.1",
    "payer_middle_name": "Text7.2",
    "payer_inn": "Text8",
    "payer_birth_day": "Text9.0",
    "payer_birth_month": "Text10.0",
    "payer_birth_year": "Text11.0",
    "payer_doc_type": "Text12",
    "payer_doc_series": "Text13",
    "payer_doc_issue_day": "Text9.1.0.0",
    "payer_doc_issue_month": "Text10.1.0.0",
    "payer_doc_issue_year": "Text11.1.0.0",
    "same_person": "Text14.0",
    "amount_rub": "Text15.0",
    "amount_kop": "Text16.0",
    "org_head_last_name": "Text17.0",
    "org_head_first_name": "Text17.1",
    "org_head_middle_name": "Text17.2",
    "doc_day": "Text9.1.1",
    "doc_month": "Text10.1.1",
    "doc_year": "Text11.1.1",
    "pages_count": "Text5.1",
    "student_last_name": "Text18.0",
    "student_first_name": "Text18.1",
    "student_middle_name": "Text18.2",
    "student_inn": "Text20",
    "student_birth_day": "Text21.0",
    "student_birth_month": "Text22.0",
    "student_birth_year": "Text23.0",
    "student_doc_type": "Text25",
    "student_doc_series": "Text260",
    "student_doc_issue_day": "Text21.1",
    "student_doc_issue_month": "Text22.1",
    "student_doc_issue_year": "Text23.1",
    "doc_date": "Text30",
}


def human_to_pdf(data: dict) -> dict:
    """
    Преобразует пользовательские данные в формат полей PDF.

    Аргументы:
        data (dict): Словарь с пользовательскими данными (человекочитаемые ключи).

    Возвращает:
        dict: Словарь, где ключи приведены к внутренним именам PDF-полей.
    """
    return {FIELD_NAMES[k]: v for k, v in data.items() if k in FIELD_NAMES}


def pdf_to_human(data: dict) -> dict:
    """
    Преобразует данные из PDF-формата в человекочитаемый формат.

    Аргументы:
        data (dict): Словарь с данными из полей PDF (внутренние ключи).

    Возвращает:
        dict: Словарь с человекочитаемыми именами полей.
    """
    reverse_map = {v: k for k, v in FIELD_NAMES.items()}
    return {reverse_map[k]: v for k, v in data.items() if k in reverse_map}
