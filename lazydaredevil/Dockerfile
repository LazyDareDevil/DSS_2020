FROM python:3.7

COPY requirements.txt .
RUN apt update -y && apt upgrade -y && apt install gcc libc-dev -y && apt install python3 python3-pip -y
RUN python3 -m pip install -r requirements.txt
RUN python3 -m dostoevsky download fasttext-social-network-model

WORKDIR /app
COPY /app .

ENTRYPOINT ["sh", "-c"]
CMD ["python3 app.py"]
