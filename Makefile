# Defina isso para usar em todo o setup do projeto
PYTHON_VERSION ?= 3.11.7

# Diretórios que contêm os módulos/apps Django deste repositório
LIBRARY_DIRS = bookstore api

# Onde os artefatos de build/relatórios são colocados
BUILD_DIR ?= build

# ---- Opções do PyTest ----
PYTEST_HTML_OPTIONS = --html=$(BUILD_DIR)/report.html --self-contained-html
PYTEST_COVERAGE_OPTIONS = --cov=$(LIBRARY_DIRS)
PYTEST_OPTIONS ?= $(PYTEST_HTML_OPTIONS) $(PYTEST_COVERAGE_OPTIONS)

# ---- Opções de verificação de tipos do MyPy ----
MYPY_OPTS ?= --python-version $(basename $(PYTHON_VERSION)) --show-column-numbers --pretty

# ---- Artefatos de instalação do Python via pyenv ----
PYTHON_VERSION_FILE = .python-version

ifeq ($(shell which pyenv),)
  # pyenv não está instalado, tenta adivinhar o caminho final
  PYENV_VERSION_DIR ?= $(HOME)/.pyenv/versions/$(PYTHON_VERSION)
else
  # pyenv está instalado
  PYENV_VERSION_DIR ?= $(shell pyenv root)/versions/$(PYTHON_VERSION)
endif

PIP ?= pip3
POETRY_OPTS ?=
POETRY ?= poetry $(POETRY_OPTS)
RUN_PYPKG_BIN = $(POETRY) run

COLOR_ORANGE = \033[33m
COLOR_RESET = \033[0m

##@ Utilitário

.PHONY: help
help: ## Exibe esta ajuda
	@awk 'BEGIN {FS = ":.*##"; printf "\nUso:\n  make \033[36m<alvo>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

.PHONY: python-version
python-version: ## Exibe a versão do Python em uso
	@echo $(PYTHON_VERSION)

##@ Django

.PHONY: migrate
migrate: ## Aplica as migrações no banco de dados
	$(RUN_PYPKG_BIN) python manage.py migrate

.PHONY: makemigrations
makemigrations: ## Gera novas migrações a partir dos models
	$(RUN_PYPKG_BIN) python manage.py makemigrations

.PHONY: runserver
runserver: ## Sobe o servidor de desenvolvimento
	$(RUN_PYPKG_BIN) python manage.py runserver 0.0.0.0:8000

.PHONY: superuser
superuser: ## Cria um superusuário Django
	$(RUN_PYPKG_BIN) python manage.py createsuperuser

.PHONY: shell
shell: ## Abre o shell interativo do Django
	$(RUN_PYPKG_BIN) python manage.py shell

##@ Testando

.PHONY: test
test: ## Executa os testes
	$(RUN_PYPKG_BIN) pytest $(PYTEST_OPTIONS)

##@ Docker

.PHONY: docker-build
docker-build: ## Builda as imagens do docker-compose
	docker compose build

.PHONY: docker-up
docker-up: ## Sobe os containers em background
	docker compose up -d

.PHONY: docker-down
docker-down: ## Derruba os containers
	docker compose down

.PHONY: docker-logs
docker-logs: ## Acompanha os logs do container web
	docker compose logs -f web

.PHONY: docker-migrate
docker-migrate: ## Aplica migrações dentro do container web
	docker compose exec web python manage.py migrate

.PHONY: docker-superuser
docker-superuser: ## Cria superusuário dentro do container web
	docker compose exec web python manage.py createsuperuser

##@ Configurar

# Detecção quase dinâmica do diretório de instalação do Python com pyenv
$(PYENV_VERSION_DIR):
	pyenv install --skip-existing $(PYTHON_VERSION)

$(PYTHON_VERSION_FILE): $(PYENV_VERSION_DIR)
	pyenv local $(PYTHON_VERSION)

.PHONY: deps
deps: deps-py ## Instala todas as dependências

.PHONY: deps-py
deps-py: $(PYTHON_VERSION_FILE) ## Instala as dependências de desenvolvimento e runtime via Poetry
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade poetry
	$(POETRY) install

.PHONY: deps-py-update
deps-py-update: pyproject.toml ## Atualiza dependências do Poetry
	$(POETRY) update

##@ Qualidade do Código

.PHONY: check
check: check-py ## Executa linters e outras ferramentas de qualidade

.PHONY: check-py
check-py: check-py-flake8 check-py-black check-py-mypy ## Verifica apenas arquivos Python

.PHONY: check-py-flake8
check-py-flake8: ## Executa o linter flake8
	$(RUN_PYPKG_BIN) flake8 .

.PHONY: check-py-black
check-py-black: ## Executa o black em modo de verificação (sem alterar arquivos)
	$(RUN_PYPKG_BIN) black --check --line-length 118 --fast .

.PHONY: check-py-mypy
check-py-mypy: ## Executa mypy
	$(RUN_PYPKG_BIN) mypy $(MYPY_OPTS) $(LIBRARY_DIRS)

.PHONY: format-py
format-py: ## Formata o código, fazendo alterações onde necessário
	$(RUN_PYPKG_BIN) black --line-length 118 .

.PHONY: format-isort
format-isort: ## Organiza os imports
	$(RUN_PYPKG_BIN) isort .
