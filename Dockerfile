FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN huggingface-cli login --token ${HUGGINGFACE_TOKEN} 2>/dev/null || true

COPY . .

EXPOSE 4002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
