import streamlit as st
import pandas as pd
from core import process_documents
import openai

st.set_page_config(page_title="AI-сервис подбора оборудования", layout="wide")
st.title("🛠️ AI-сервис подбора оборудования")
st.markdown("Загрузите техническое задание, прайсы и (опционально) файл со скидками — система всё сделает сама.")

uploaded_spec = st.file_uploader("📄 Техническое задание (PDF)", type=["pdf"])
uploaded_prices = st.file_uploader("📊 Прайсы поставщиков (XLSX)", type=["xlsx"], accept_multiple_files=True)
uploaded_discounts = st.file_uploader("💸 Скидки от поставщиков (XLSX, по желанию)", type=["xlsx"])

# GPT API KEY (через Render Environment Variables)
openai.api_key = st.secrets.get("OPENAI_API_KEY")

def ask_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты помощник по интерпретации ТЗ для оборудования в школы и детские сады."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Ошибка GPT: {e}"

st.markdown("---")
st.subheader("🤖 Помощь от GPT")
gpt_input = st.text_area("Задай вопрос по ТЗ или товару (например: 'что такое рельефная модель моллюска?')")
if st.button("🧠 Получить ответ от ИИ") and gpt_input:
    with st.spinner("Запрос к GPT..."):
        st.markdown(f"> {ask_gpt(gpt_input)}")

st.markdown("---")
st.subheader("📥 Загрузка и подбор")
if st.button("🚀 Запустить подбор"):
    if uploaded_spec and uploaded_prices:
        with st.spinner("⏳ Обработка данных..."):
            ts_text, result_df, result_file = process_documents(uploaded_spec, uploaded_prices, uploaded_discounts)
        st.success("✅ Подбор завершён!")
        st.subheader("📜 Распознанный текст из ТЗ")
        st.text_area("Текст ТЗ (первые 1000 символов)", ts_text[:1000], height=200)
        st.subheader("📋 Результаты подбора")
        st.dataframe(result_df, use_container_width=True)
        st.download_button("💾 Скачать Excel", data=result_file, file_name="Результат_подбора.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.error("⚠️ Загрузите как минимум ТЗ и один прайс.")

