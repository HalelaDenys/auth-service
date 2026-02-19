FROM python:3.11-slim

ENV PYTHONPATH=src

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y gcc curl \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Копируем только конфиги зависимостей для кеша
COPY pyproject.toml uv.lock* ./


# 3. Ставим uv и зависимости в системный Python
RUN pip install --no-cache-dir uv \
    && UV_SYSTEM=true uv sync
#    && uv sync --system


COPY src/ /app/src/
COPY tests/ /app/tests/
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh