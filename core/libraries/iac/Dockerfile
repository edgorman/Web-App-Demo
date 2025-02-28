FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ADD . /app
WORKDIR /app
RUN uv sync --frozen

ENTRYPOINT [ "iac" ]
