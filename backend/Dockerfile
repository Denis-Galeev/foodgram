FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
CMD ["gunicorn", "--bind", "0.0.0.0:7000", "foodgram_backend.wsgi"] 
