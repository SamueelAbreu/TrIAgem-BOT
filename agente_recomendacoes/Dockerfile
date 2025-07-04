# Dockerfile para o Agente de Triagem
FROM python:3.11-slim-buster

WORKDIR /app

ENV PATH="/usr/local/bin:$PATH"
COPY requirements.txt .
RUN pip install --upgrade pip  
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn


COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
