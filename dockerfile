# ---------- Stage 1: base com Poetry instalado ----------
FROM python:3.11-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Dependências de sistema necessárias para compilar pacotes Python
# (build-essential/gcc para pacotes com extensões C, libpq-dev para psycopg2)
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

# ---------- Stage 2: instala as dependências do projeto ----------
FROM python-base AS builder-base

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# --no-root: não instala o próprio pacote ainda, só as dependências
# Se você usa uma versão de Poetry >= 1.2, "--only main" substitui "--no-dev"
RUN poetry install --no-root --only main

# ---------- Stage 3: imagem final, enxuta ----------
FROM python-base AS production

ENV PATH="$VENV_PATH/bin:$PATH"

# Copia apenas o venv já resolvido do estágio anterior, sem as ferramentas de build
COPY --from=builder-base $VENV_PATH $VENV_PATH

WORKDIR /app
COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
