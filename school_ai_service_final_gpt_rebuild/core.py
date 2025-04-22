
import pandas as pd
import fitz
import re
import io
from openpyxl import load_workbook
import pdfplumber
from pdf2image import convert_from_bytes

def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except:
        images = convert_from_bytes(file.read())
        import pytesseract
        text = "\n".join([pytesseract.image_to_string(img) for img in images])
    return text

def parse_requirements(text):
    lines = text.split("\n")
    rows = []
    for line in lines:
        if any(char.isdigit() for char in line):
            parts = re.split(r"\s{2,}|\t", line.strip())
            if len(parts) >= 2:
                name = parts[0]
                quantity = re.search(r"\d+", parts[1])
                quantity = quantity.group() if quantity else ""
                rows.append({"Наименование из ТЗ": name, "Кол-во": quantity})
    return pd.DataFrame(rows)

def load_price_list(files):
    all_items = []
    for file in files:
        df = pd.read_excel(file, header=None)
        for _, row in df.iterrows():
            for col in row:
                if isinstance(col, str) and any(kw in col.lower() for kw in ["стол", "кресло", "шкаф", "банкетка"]):
                    item = {
                        "Артикул": row[0] if len(row) > 1 else "",
                        "Наименование": col,
                        "Цена": next((v for v in row if isinstance(v, (int, float))), "")
                    }
                    all_items.append(item)
                    break
    return pd.DataFrame(all_items)

def load_discounts(file):
    if not file:
        return {}
    df = pd.read_excel(file)
    return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

def process_documents(spec_file, prices_files, discounts_file=None):
    text = extract_text_from_pdf(spec_file)
    spec_df = parse_requirements(text)
    prices_df = load_price_list(prices_files)
    discounts = load_discounts(discounts_file)

    results = []
    for _, row in spec_df.iterrows():
        name = row["Наименование из ТЗ"]
        qty = row["Кол-во"]
        matches = prices_df[prices_df["Наименование"].str.contains(name.split()[0], case=False, na=False)].head(3)
        item = {"Наименование из ТЗ": name, "Кол-во": qty}
        for i, (_, match_row) in enumerate(matches.iterrows()):
            supplier = f"Поставщик {i+1}"
            price = match_row.get("Цена", "")
            discount = discounts.get(supplier, 0)
            final_price = round(price * (1 - discount/100), 2) if price else ""
            item.update({
                f"Поставщик {i+1}": supplier,
                f"Цена {i+1}": price,
                f"Скидка {i+1}": f"{discount}%",
                f"Итого {i+1}": final_price
            })
        results.append(item)

    result_df = pd.DataFrame(results)
    wb = load_workbook("Форма для результата.xlsx")
    ws = wb.active
    for i, row in result_df.iterrows():
        ws.append(list(row.values()))
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return text, result_df, output.read()
