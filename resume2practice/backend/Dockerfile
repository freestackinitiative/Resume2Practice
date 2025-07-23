# Production
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS prod

WORKDIR /src

COPY src .
COPY requirements.txt .

RUN uv pip install --no-cache-dir -r requirements.txt --system

EXPOSE 5000

WORKDIR /src/resume2practice

ENTRYPOINT ["fastapi"]
CMD ["run", "app.py", "--port", "5000"]

# Dev/Debug
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS dev

WORKDIR /src

COPY src .
COPY requirements.txt .

RUN uv pip install --no-cache-dir -r requirements.txt --system && \
    uv pip install --no-cache-dir jupyterlab --system

ENV JUPYTER_TOKEN=ai

EXPOSE 5000

WORKDIR /src/resume2practice

CMD ["jupyter", "lab", "--ip","0.0.0.0", "--port", "5000", "--notebook-dir", "/src", "--no-browser", "--allow-root"]