# 📚 bookstore-docker2

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-REST_Framework-ff1709?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-dependency_management-60A5FA?logo=poetry&logoColor=white)

Projeto Django (bookstore) dockerizado, usando **Poetry** para gerenciamento de dependências, **Django REST Framework** para a API e **PostgreSQL** como banco de dados, orquestrado com **Docker Compose**.

Desenvolvido como exercício do curso Python Back-End (EBAC), módulo de containerização.

---

## Sumário

- [Funcionalidades](#funcionalidades)
- [Arquitetura do projeto](#arquitetura-do-projeto)
  - [Containers e comunicação](#containers-e-comunicação)
- [Pré-requisitos](#pré-requisitos)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Variáveis de ambiente](#variáveis-de-ambiente-envdev)
- [Comandos úteis](#comandos-úteis)
- [Solução de problemas](#solução-de-problemas)

---

## Funcionalidades

- **API REST** com Django REST Framework (`rest_framework` em `INSTALLED_APPS`).
- **Banco de dados PostgreSQL 16** rodando em container próprio, com volume persistente e healthcheck (o container `web` só sobe depois que o banco está pronto para aceitar conexões).
- **Gerenciamento de dependências com Poetry**, isolado em virtualenv dentro do próprio container (`POETRY_VIRTUALENVS_IN_PROJECT`).
- **Build multi-stage no Dockerfile**: um estágio (`builder-base`) instala o Poetry e resolve as dependências; o estágio final (`production`) apenas copia o virtualenv já pronto, gerando uma imagem final mais enxuta.
- **Configuração via variáveis de ambiente** (`.env.dev`): o Django lê `SQL_ENGINE`, `SQL_DATABASE`, `SQL_USER`, `SQL_PASSWORD`, `SQL_HOST` e `SQL_PORT` para conectar ao Postgres, com fallback para SQLite caso essas variáveis não existam.
- **Hot reload em desenvolvimento**: o código-fonte é montado como volume no container `web`, então alterações no código refletem sem precisar rebuildar a imagem.
- **Painel administrativo do Django** (`/admin`) disponível após criação de superusuário.

---

## Arquitetura do projeto

```text
bookstore-docker2/
├── api/                        # app Django (models, serializers, views, urls da API)
│   ├── migrations/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── bookstore/                  # configurações principais do projeto Django
│   ├── __init__.py
│   ├── settings.py             # lê variáveis de ambiente para o banco (SQL_*)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── .dockerignore                # exclui .venv, __pycache__, db.sqlite3, .git do build
├── .env.dev                     # variáveis de ambiente (não versionar com segredo real)
├── .gitignore
├── docker-compose.yml           # orquestra os serviços web + db
├── dockerfile                   # build multi-stage da imagem da aplicação
├── Makefile                     # atalhos de comandos (build, migrate, testes, lint)
├── manage.py
├── poetry.lock
├── pyproject.toml               # dependências gerenciadas pelo Poetry
└── README.md
```

### Containers e comunicação

```text
┌─────────────────────────────┐        ┌─────────────────────────────┐
│         web (Django)        │        │        db (PostgreSQL)      │
│  imagem: bookstore-docker2  │        │   imagem: postgres:16-alpine│
│  porta: 8000 → 8000          │───────▶│  porta: 5432 → 5432          │
│  lê variáveis de .env.dev    │  SQL   │  volume: postgres_data       │
└─────────────────────────────┘        └─────────────────────────────┘
        depende_de: db (aguarda healthcheck do banco)
```

Os dois serviços rodam na mesma rede interna criada pelo Docker Compose (`bookstore-docker2_default`), e o `web` se conecta ao `db` usando o nome do serviço (`SQL_HOST=db`) em vez de `localhost`.

---

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando (com WSL2 habilitado, no Windows)
- Git

Não é necessário ter Python, Poetry ou Postgres instalados localmente — tudo roda dentro dos containers.

---

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/RogerioFernandesSilva/bookstore-docker2.git
cd bookstore-docker2
```

### 2. Build e subida dos containers

```bash
docker compose up --build
```

Isso sobe dois serviços:
- `db`: PostgreSQL 16, com volume persistente `postgres_data`
- `web`: aplicação Django, servida em `http://localhost:8000`

Para rodar em segundo plano (sem travar o terminal):

```bash
docker compose up -d
```

### 3. Aplicar as migrações

Em outro terminal, com os containers em execução:

```bash
docker compose exec web python manage.py migrate
```

### 4. Criar um superusuário

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Acessar

- Aplicação: [http://localhost:8000](http://localhost:8000)
- Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## Variáveis de ambiente (`.env.dev`)

| Variável | Descrição |
|---|---|
| `DEBUG` | Ativa modo debug do Django |
| `SECRET_KEY` | Chave secreta do Django |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos |
| `SQL_ENGINE` | Engine do banco (`django.db.backends.postgresql`) |
| `SQL_DATABASE` | Nome do banco |
| `SQL_USER` | Usuário do Postgres |
| `SQL_PASSWORD` | Senha do Postgres |
| `SQL_HOST` | Host do banco (`db`, nome do serviço no Compose) |
| `SQL_PORT` | Porta do Postgres (`5432`) |

> **Importante:** `.env.dev` não deve ser commitado com segredos reais. Mantenha-o no `.gitignore` e disponibilize um `.env.dev.example` com valores fictícios como referência.

---

## Comandos úteis

| Comando | O que faz |
|---|---|
| `docker compose up --build` | Builda a imagem e sobe os containers, com logs no terminal |
| `docker compose up -d` | Sobe os containers em segundo plano |
| `docker compose down` | Para e remove os containers |
| `docker compose ps` | Lista o status dos containers |
| `docker compose logs web` | Mostra os logs do container Django |
| `docker compose logs db` | Mostra os logs do container Postgres |
| `docker compose exec web python manage.py migrate` | Aplica as migrações |
| `docker compose exec web python manage.py createsuperuser` | Cria um superusuário |
| `docker compose exec web python manage.py shell` | Abre o shell interativo do Django dentro do container |
| `poetry add <pacote>` | Adiciona uma dependência de produção ao projeto |
| `poetry add --group dev <pacote>` | Adiciona uma dependência de desenvolvimento |

Se tiver `make` instalado (Linux/macOS/WSL), os mesmos comandos estão disponíveis como atalhos no `Makefile` (`make docker-up`, `make docker-migrate`, etc.). No Windows com PowerShell puro, use os comandos `docker compose` diretamente.

---

## Solução de problemas

- **`service "web" is not running`**: verifique se o container caiu com `docker compose logs web` — geralmente é erro de sintaxe no `settings.py` ou dependência faltando.
- **`NameError: name 'os' is not defined`**: falta `import os` no topo do `bookstore/settings.py`, necessário para ler as variáveis de ambiente do banco.
- **`make` não reconhecido no PowerShell**: `make` não vem nativo no Windows; use os comandos `docker compose` equivalentes ou instale via Chocolatey/WSL.
