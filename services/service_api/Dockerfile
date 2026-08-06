FROM python:3.12-slim AS builder

ENV PATH="/root/.local/bin:${PATH}"

RUN pip install --no-cache-dir pipx && pipx install poetry==2.4.1 && pipx inject poetry poetry-plugin-export

COPY pyproject.toml poetry.lock ./

RUN poetry export --only main --without-hashes -o requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

RUN useradd --shell /bin/bash appuser

WORKDIR /app

COPY --from=libs . /libs

COPY --from=builder requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --disable-pip-version-check \
    -r requirements.txt

COPY --chown=appuser:appuser . .

WORKDIR src/service_api

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

