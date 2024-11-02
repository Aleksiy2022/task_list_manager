FROM python:3.12

COPY api api
COPY pyproject.toml poetry.lock ./
COPY alembic alembic
COPY alembic.ini alembic.ini

RUN pip install --upgrade pip  \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

CMD alembic upgrade head && uvicorn api.main:app --reload --port 8000 --host 0.0.0.0