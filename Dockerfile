FROM python:3.12

COPY api api
COPY pyproject.toml poetry.lock ./
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY jwt_auth jwt_auth
COPY certs certs

RUN pip install --upgrade pip  \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

CMD ["sh", "-c", "alembic upgrade head && \
                  cd certs && \
                  openssl genrsa -out jwt-private.pem 2048 && \
                  openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem && \
                  cd ../ && \
                  uvicorn api.main:app --reload --port 8000 --host 0.0.0.0"]
