import streamlit as st
import pandas as pd
import openai
from core import process_documents

st.set_page_config(page_title="AI-сервис подбора оборудования", layout="wide")

st.title("🛠️ AI-сервис подбора оборудования")
st.markdown("Загрузите техническое задание, прайсы и (опционально) файл со скидками — система всё сделает сама.")

uploaded_spec = st.file_uploader("📄 Техническое задание (PDF)", type=["pdf"])
uploaded_prices = st.file_uploader("📊 Прайсы поставщиков (XLSX)", type=["xlsx"], accept_multiple_files=True)
uploaded_discounts = st.file_uploader("💸 Скидки от поставщиков (XLSX, по желанию)", type=["xlsx"])

# GPT KEY
openai.api_key = st.secrets.get("OPENAI_API_KEY")

st.markdown("---")
st.subheader("📥 Загрузка и подбор")

if st.button("🚀 Запустить подбор"):
    if uploaded_spec and uploaded_prices:
        with st.spinner("⏳ Обработка данных..."):
            try:
                ts_text, result_df, result_file = process_documents(uploaded_spec, uploaded_prices, uploaded_discounts)

                if result_df.empty:
                    st.warning("⚠️ Обработка завершена, но подходящих товаров не найдено.")
                else:
                    st.success("✅ Подбор завершён!")
                    st.subheader("📜 Распознанный текст из ТЗ")
                    st.text_area("Текст ТЗ", ts_text[:1000], height=200)
                    st.subheader("📋 Результаты подбора")
                    st.dataframe(result_df, use_container_width=True)
                    st.download_button("💾 Скачать Excel", data=result_file, file_name="Результат_подбора.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            except Exception as e:
                st.error(f"❌ Ошибка при обработке: {e}")
    else:
        st.error("⚠️ Загрузите как минимум ТЗ и хотя бы один прайс.")
