FROM python:3.12-slim

WORKDIR /app

RUN pip install uv --no-cache-dir

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app/ ./app/
COPY data/ ./data/

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "app"]
