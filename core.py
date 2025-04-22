import pandas as pd
import fitz  # PyMuPDF
import re
from openpyxl import load_workbook
from io import BytesIO
import pdfplumber

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def parse_requirements(text):
    rows = []
    for line in text.split("\n"):
        if any(char.isdigit() for char in line):
            parts = re.split(r"\s{2,}", line.strip())
            if len(parts) >= 2:
                name = parts[0]
                quantity_match = re.search(r"\d+", parts[1])
                quantity = quantity_match.group() if quantity_match else ""
                rows.append({"Наименование из ТЗ": name, "Кол-во": quantity})
    return pd.DataFrame(rows)

def load_price_list(files):
    all_items = []
    for file in files:
        df = pd.read_excel(file, header=None)
        for _, row in df.iterrows():
            for col in row:
                if isinstance(col, str) and any(k in col.lower() for k in ["стол", "кресло", "шкаф", "барьер", "лампа", "банкетка"]):
                    item = {
                        "Артикул": row[0] if len(row) > 1 else "",
                        "Наименование": col,
                        "Цена": next((v for v in row if isinstance(v, (int, float))), "")
                    }
                    all_items.append(item)
                    break
    return pd.DataFrame(all_items)

def load_discounts(file):
    if file is None:
        return {}
    df = pd.read_excel(file)
    return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

def process_documents(spec_file, prices_files, discounts_file=None):
    text = extract_text_from_pdf(spec_file)
    ts_df = parse_requirements(text)
    prices_df = load_price_list(prices_files)
    discounts = load_discounts(discounts_file)

    results = []
    for _, row in ts_df.iterrows():
        name = row["Наименование из ТЗ"]
        qty = row["Кол-во"]
        matches = prices_df[prices_df["Наименование"].str.contains(name[:5], case=False, na=False)]
        item = {"Наименование из ТЗ": name, "Кол-во": qty}

        for i, (_, match_row) in enumerate(matches.head(3).iterrows(), 1):
            supplier = f"Поставщик {i}"
            price = match_row["Цена"]
            discount = discounts.get(supplier, 0)
            final_price = round(price * (1 - discount / 100), 2) if price else ""
            item.update({
                f"Поставщик {i}": supplier,
                f"Цена {i}": price,
                f"Скидка {i}": f"{discount}%",
                f"Итог {i}": final_price
            })
        results.append(item)

    result_df = pd.DataFrame(results)

    # Формирование Excel-файла
    wb = load_workbook("Форма для результата.xlsx")
    ws = wb.active
    for i, row in result_df.iterrows():
        ws.append([
            i + 1,
            row["Наименование из ТЗ"],
            row["Кол-во"],
            row.get("Поставщик 1", ""),
            row.get("Цена 1", ""),
            row.get("Скидка 1", ""),
            row.get("Итог 1", "")
        ])
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return text, result_df, output.read()

