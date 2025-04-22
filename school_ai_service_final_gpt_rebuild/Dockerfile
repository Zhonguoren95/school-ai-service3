
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils && \
    apt-get clean

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_interface.py"]
