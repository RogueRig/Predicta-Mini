FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy frontend for serving static files
COPY ../frontend/public /app/frontend/public

EXPOSE 8080

ENV PORT=8080
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:create_app()"]
