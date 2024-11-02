FROM python:3.12

COPY api api
COPY pyproject.toml poetry.lock ./
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY jwt_auth jwt_auth

RUN pip install --upgrade pip  \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

CMD alembic upgrade head && \
    mkdir certs && \
    cd certs && \
    openssl genrsa -out jwt-private.pem 2048 && \
    openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem && \
    uvicorn api.main:app --reload --port 8000 --host 0.0.0.0
