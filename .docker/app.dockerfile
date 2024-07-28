FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY src/ src/
COPY packages/ packages/
COPY settings.py settings.py
COPY function_app.py function_app.py

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "80", "function_app:app"]
