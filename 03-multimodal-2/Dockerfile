FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_EDITABLE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN uv sync --frozen --no-dev --no-editable

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "tg_llm_bot"]
