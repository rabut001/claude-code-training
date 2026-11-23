# 開発用コンテナ（Python・PDF の読み取り・ブラウザでのテスト）
# 使い方は ./dev を参照。git / gh / Claude Code / Codex はホスト（Linux）側のものを使う。
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright \
    HOME=/tmp

# PDF の読み取り（pdftotext / pdftoppm）
RUN apt-get update \
 && apt-get install -y --no-install-recommends poppler-utils \
 && rm -rf /var/lib/apt/lists/*

# ブラウザでのテスト（Playwright + Chromium）
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install -r /tmp/requirements-dev.txt \
 && playwright install --with-deps chromium \
 && chmod -R a+rX /opt/ms-playwright \
 && rm -rf /var/lib/apt/lists/* /tmp/requirements-dev.txt

WORKDIR /work
