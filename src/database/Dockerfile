#DOCKERFILE training service with train.py (app = FastAPI() inside)
FROM python:3.11.0rc1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN pip install pytest

COPY . .

CMD ["uvicorn", "init_database:app", "--host", "0.0.0.0", "--port", "8001"]