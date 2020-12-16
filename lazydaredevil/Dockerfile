FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN pythom -m dostoevsky download fasttext-social-network-model

WORKDIR /app
COPY /app .

EXPOSE 9200
ENTRYPOINT ["sh", "-c"]
CMD ["python app.py"]
