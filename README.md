# 📚 bookstore-docker2

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-REST_Framework-ff1709?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-dependency_management-60A5FA?logo=poetry&logoColor=white)
![Deploy](https://img.shields.io/badge/Deploy-PythonAnywhere-1D9FD7)

API REST de uma livraria (**produtos, categorias e pedidos**) feita com **Django** e **Django REST Framework**, com autenticação por token, dependências gerenciadas pelo **Poetry**, banco **PostgreSQL** orquestrado com **Docker Compose** e **deploy automático no PythonAnywhere** via webhook do GitHub.

**Projeto no ar:** <https://rogeriodev81.pythonanywhere.com>

Desenvolvido como exercício do curso Python Back-End (EBAC), cobrindo containerização, API com autenticação e deploy.

---

## Sumário

- [Funcionalidades](#funcionalidades)
- [Arquitetura do projeto](#arquitetura-do-projeto)
  - [Containers e comunicação](#containers-e-comunicação)
- [API REST](#api-rest)
  - [Rotas](#rotas)
  - [Autenticação](#autenticação)
  - [Exemplos de uso](#exemplos-de-uso)
  - [Modelos e formato dos dados](#modelos-e-formato-dos-dados)
- [Pré-requisitos](#pré-requisitos)
- [Como rodar o projeto](#como-rodar-o-projeto)
- [Rodando sem Docker](#rodando-sem-docker)
- [Variáveis de ambiente](#variáveis-de-ambiente-envdev)
- [Testes](#testes)
- [Deploy no PythonAnywhere](#deploy-no-pythonanywhere)
  - [Passo a passo](#passo-a-passo)
  - [Deploy automático (webhook)](#deploy-automático-webhook)
- [Comandos úteis](#comandos-úteis)
- [CI/CD com GitHub Actions](#cicd-com-github-actions)
- [Solução de problemas](#solução-de-problemas)

---

## Funcionalidades

- **API REST** com Django REST Framework: CRUD de **produtos**, **categorias** e **pedidos**, com a versão da API na URL (`/bookstore/v1/` e `/bookstore/v2/`) e **paginação** de 5 itens por página.
- **Autenticação**: todas as rotas da API exigem credencial. São aceitos **Token**, **Basic** e **Session**, e o token é obtido em `/api-token-auth/`. Sem credencial a API responde `401`.
- **Pedidos com regras de negócio**: o `total` é calculado automaticamente, o usuário do pedido vem do token e cada usuário só enxerga os próprios pedidos (staff enxerga todos).
- **Banco de dados PostgreSQL 16** rodando em container próprio, com volume persistente e healthcheck (o container `web` só sobe depois que o banco está pronto para aceitar conexões).
- **Gerenciamento de dependências com Poetry**, isolado em virtualenv dentro do próprio container (`POETRY_VIRTUALENVS_IN_PROJECT`).
- **Build multi-stage no Dockerfile**: um estágio (`builder-base`) instala o Poetry e resolve as dependências; o estágio final (`production`) apenas copia o virtualenv já pronto, gerando uma imagem final mais enxuta.
- **Configuração via variáveis de ambiente** (`env.dev`): o Django lê `SQL_ENGINE`, `SQL_DATABASE`, `SQL_USER`, `SQL_PASSWORD`, `SQL_HOST` e `SQL_PORT` para conectar ao Postgres, com fallback para SQLite caso essas variáveis não existam.
- **Hot reload em desenvolvimento**: o código-fonte é montado como volume no container `web`, então alterações no código refletem sem precisar rebuildar a imagem.
- **Painel administrativo do Django** (`/admin/`) disponível após criação de superusuário.
- **Testes automatizados** dos apps `product` e `order` (autenticação, criação, cálculo do total, isolamento entre usuários e versões da API).
- **Integração contínua com GitHub Actions**: a cada push, os testes rodam automaticamente; a cada push/PR para `main`, o fluxo completo com Docker também é executado.
- **Deploy automático no PythonAnywhere**: um webhook do GitHub aciona a rota `/update_server/`, que atualiza o código no servidor a cada push.

---

## Arquitetura do projeto

```text
bookstore-docker2/
├── api/                        # app reservado (esqueleto vazio, sem rotas)
├── bookstore/                  # configurações principais do projeto Django
│   ├── __init__.py
│   ├── settings.py             # apps, DRF, autenticação e variáveis de ambiente
│   ├── urls.py                 # admin, API v1/v2, token, webhook e /hello/
│   ├── views.py                # update_server (webhook de deploy) e hello_world
│   ├── templates/
│   │   └── hello_world.html    # página de teste do deploy
│   ├── wsgi.py
│   └── asgi.py
├── product/                    # app de produtos e categorias
│   ├── migrations/
│   ├── models.py               # Category e Product
│   ├── serializers.py
│   ├── viewsets.py
│   ├── urls.py                 # rotas product/ e category/
│   ├── admin.py
│   └── tests.py
├── order/                      # app de pedidos
│   ├── migrations/
│   ├── models.py               # Order
│   ├── serializers.py          # total calculado e produtos aninhados
│   ├── viewsets.py             # filtro por usuário
│   ├── urls.py                 # rota order/
│   ├── admin.py
│   └── tests.py
├── .github/
│   └── workflows/
│       ├── build.yml           # roda os testes com Poetry a cada push
│       └── ci.yml              # build com Docker, migrate e testes (main/develop)
├── .dockerignore               # exclui .venv, __pycache__, db.sqlite3, .git do build
├── .env.dev.example            # modelo para criar o env.dev (que não é versionado)
├── .gitignore
├── docker-compose.yml          # orquestra os serviços web + db
├── dockerfile                  # build multi-stage da imagem da aplicação
├── Makefile
├── manage.py
├── poetry.lock
├── pyproject.toml              # dependências gerenciadas pelo Poetry
└── README.md
```

### Containers e comunicação

```text
                        rede: bookstore_network (bridge)
┌───────────────────────────┐              ┌───────────────────────────┐
│       web (Django)        │              │       db (PostgreSQL)     │
│ imagem: bookstore-docker2 │──────SQL────▶│  imagem: postgres:16-alpine │
│ porta: 8000 → 8000         │              │  porta: 5432 → 5432         │
│ lê variáveis de env.dev    │              │  volume: postgres_data      │
└───────────────────────────┘              └───────────────────────────┘
        depende_de: db (aguarda healthcheck do banco)
```

Os dois serviços são conectados explicitamente a uma rede *bridge* própria, declarada em `docker-compose.yml` e chamada `bookstore_network`, em vez de depender da rede *default* implícita que o Compose criaria automaticamente. Isso deixa a topologia de rede documentada no próprio arquivo e facilita adicionar novos serviços (cache, worker, etc.) no futuro.

O `web` se conecta ao `db` usando o nome do serviço (`SQL_HOST=db`) em vez de `localhost` — a resolução de nomes funciona porque ambos os containers estão na mesma rede, via DNS interno do Docker.

```yaml
networks:
  bookstore_network:
    driver: bridge
    name: bookstore_network
```

---

## API REST

Nos exemplos abaixo, `BASE` é o endereço do servidor: `https://rogeriodev81.pythonanywhere.com` no deploy ou `http://127.0.0.1:8000` localmente.

### Rotas

| Método | Rota | Descrição |
|---|---|---|
| `GET`, `POST` | `/bookstore/v1/product/` | Lista (paginada) e cria produtos |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/bookstore/v1/product/{id}/` | Consulta, altera e remove um produto |
| `GET`, `POST` | `/bookstore/v1/category/` | Lista (paginada) e cria categorias |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/bookstore/v1/category/{id}/` | Consulta, altera e remove uma categoria |
| `GET`, `POST` | `/bookstore/v1/order/` | Lista (paginada) e cria pedidos do usuário autenticado |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/bookstore/v1/order/{id}/` | Consulta, altera e remove um pedido |
| `POST` | `/api-token-auth/` | Recebe `username` e `password` e devolve o token |
| `POST` | `/update_server/` | Webhook de deploy (atualiza o código no servidor) |
| `GET` | `/hello/` | Página de teste do deploy |
| — | `/admin/` | Painel administrativo do Django |

A versão `v2` expõe as mesmas rotas em `/bookstore/v2/...`. As duas versões usam os mesmos viewsets, então hoje o comportamento é idêntico; a separação existe para permitir evoluir a API sem quebrar clientes antigos.

### Autenticação

Todas as rotas de `/bookstore/...` exigem usuário autenticado. Os métodos aceitos são:

| Método | Como enviar |
|---|---|
| **Token** (recomendado) | Cabeçalho `Authorization: Token SEU_TOKEN` |
| **Basic** | Usuário e senha no cabeçalho `Authorization: Basic ...` |
| **Session** | Login pelo navegador (`/admin/` ou a interface navegável do DRF) |

Sem credencial, a resposta é `401 Unauthorized`. Com usuário e senha inválidos em `/api-token-auth/`, a resposta é `400` com a mensagem `Unable to log in with provided credentials.`

### Exemplos de uso

**1. Sem token (esperado: 401):**

```bash
curl -i $BASE/bookstore/v1/product/
```

**2. Obter o token** (o usuário é criado antes com `createsuperuser` ou pelo `/admin/`):

```bash
curl -X POST $BASE/api-token-auth/ -d "username=SEU_USUARIO&password=SUA_SENHA"
```

```json
{"token": "0123456789abcdef0123456789abcdef01234567"}
```

> Dica: para não deixar a senha no histórico do terminal, use `read -s -p "senha: " P` e referencie `$P` no comando.

**3. Usar o token nas rotas:**

```bash
export TOKEN=0123456789abcdef0123456789abcdef01234567

# cria uma categoria
curl -X POST -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"Tecnologia","slug":"tecnologia"}' $BASE/bookstore/v1/category/

# cria um produto ligado à categoria 1
curl -X POST -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"Django na pratica","description":"Livro","price":100,"categories_id":[1]}' \
  $BASE/bookstore/v1/product/

# cria um pedido com o produto 1
curl -X POST -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" \
  -d '{"products_id":[1]}' $BASE/bookstore/v1/order/

# lista produtos e pedidos
curl -H "Authorization: Token $TOKEN" $BASE/bookstore/v1/product/
curl -H "Authorization: Token $TOKEN" $BASE/bookstore/v1/order/
```

**Resposta ao criar o pedido** (o `user` vem do token e o `total` é calculado):

```json
{
  "id": 1,
  "user": "demo",
  "product": [
    {
      "id": 1,
      "title": "Django na pratica",
      "description": "Livro",
      "price": 100,
      "active": true,
      "category": [
        {"id": 1, "title": "Tecnologia", "slug": "tecnologia", "description": null, "active": true}
      ]
    }
  ],
  "total": 100,
  "created_at": "2026-10-15T19:55:37.911251Z"
}
```

**Resposta paginada da listagem** (5 itens por página):

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [ ... ]
}
```

**No PowerShell:**

```powershell
$BASE = "https://rogeriodev81.pythonanywhere.com"
$r = Invoke-RestMethod -Method Post -Uri "$BASE/api-token-auth/" -Body @{username="SEU_USUARIO"; password="SUA_SENHA"}
$h = @{ Authorization = "Token $($r.token)" }
Invoke-RestMethod -Uri "$BASE/bookstore/v1/product/" -Headers $h
```

### Modelos e formato dos dados

| Modelo | Campos |
|---|---|
| `Category` | `title`, `slug` (único), `description`, `active` |
| `Product` | `title`, `description`, `price`, `active`, `categories` (vários) |
| `Order` | `user` (preenchido pelo token), `products` (vários), `created_at` e `total` (calculado, somente leitura) |

Ao **criar ou alterar**, as relações são enviadas como listas de ids: `categories_id` no produto e `products_id` no pedido. Ao **ler**, a API devolve os objetos completos em `category` (produto) e `product` (pedido). Um pedido exige pelo menos um produto.

---

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando (com WSL2 habilitado, no Windows)
- Git

Para rodar com Docker não é necessário ter Python, Poetry ou Postgres instalados localmente — tudo roda dentro dos containers. Para [rodar sem Docker](#rodando-sem-docker), é preciso ter Python 3.11+ e o [Poetry](https://python-poetry.org/docs/#installation).

---

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/RogerioFernandesSilva/bookstore-docker2.git
cd bookstore-docker2
```

### 2. Criar o arquivo de variáveis de ambiente

O `env.dev` **não é versionado** (ele guarda credenciais). Crie-o a partir do modelo:

```bash
cp .env.dev.example env.dev
```

No PowerShell: `Copy-Item .env.dev.example env.dev`

### 3. Build e subida dos containers

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

### 4. Aplicar as migrações

Em outro terminal, com os containers em execução:

```bash
docker compose exec web python manage.py migrate
```

### 5. Criar um superusuário

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Acessar

- Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Página de teste: [http://localhost:8000/hello/](http://localhost:8000/hello/)
- API: [http://localhost:8000/bookstore/v1/product/](http://localhost:8000/bookstore/v1/product/) (peça usuário e senha no navegador, ou use o token como em [Exemplos de uso](#exemplos-de-uso))

A raiz (`/`) não tem página; use as rotas acima.

### 7. Verificar a rede (opcional)

Para confirmar que os containers estão conectados à rede `bookstore_network`:

```bash
docker compose ps
docker network inspect bookstore_network
docker compose exec web ping -c 3 db
```

O `network inspect` deve listar os containers `web` e `db` em `"Containers"`, e o `ping` deve responder pelo nome `db`, confirmando a comunicação entre eles.

---

## Rodando sem Docker

Sem as variáveis `SQL_*`, o projeto usa **SQLite** (`db.sqlite3`, que não é versionado). Com o Poetry instalado:

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
DEBUG=1 poetry run python manage.py runserver
```

No PowerShell, defina a variável antes do `runserver`:

```powershell
$env:DEBUG = "1"
poetry run python manage.py runserver
```

O `DEBUG=1` faz o CSS do admin carregar localmente; sem a variável, o `DEBUG` fica desligado, que é o padrão seguro. A aplicação fica em `http://127.0.0.1:8000`.

---

## Variáveis de ambiente (`env.dev`)

| Variável | Descrição |
|---|---|
| `DEBUG` | `1` ativa o modo debug do Django; sem a variável, fica desligado |
| `SECRET_KEY` | Chave secreta do Django |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por espaço |
| `SQL_ENGINE` | Engine do banco (`django.db.backends.postgresql`) |
| `SQL_DATABASE` | Nome do banco |
| `SQL_USER` | Usuário do Postgres |
| `SQL_PASSWORD` | Senha do Postgres |
| `SQL_HOST` | Host do banco (`db`, nome do serviço no Compose) |
| `SQL_PORT` | Porta do Postgres (`5432`) |
| `REPO_PATH` | *(deploy)* pasta do repositório no servidor, usada pelo webhook |
| `WSGI_FILE` | *(deploy)* arquivo WSGI do PythonAnywhere, tocado após o `git pull` para recarregar o app |

> **Importante:** o `env.dev` não vai para o Git e o repositório traz apenas o `.env.dev.example`, com valores de desenvolvimento local. Nunca coloque a `SECRET_KEY` real de produção em nenhum arquivo versionado — em produção, ela deve vir de uma variável de ambiente do ambiente de deploy (veja [Deploy no PythonAnywhere](#deploy-no-pythonanywhere)).

---

## Testes

O projeto tem **11 testes automatizados** (`product/tests.py` e `order/tests.py`) que cobrem:

- rotas protegidas respondendo `401` sem credencial;
- listagem paginada e criação de produtos e categorias com token;
- criação de pedido com cálculo do `total` e usuário vindo do token;
- rejeição de pedido sem produtos;
- cada usuário vendo apenas os próprios pedidos;
- obtenção do token em `/api-token-auth/` e rejeição de senha errada;
- a rota da versão `v2`.

Para executar:

```bash
poetry run python manage.py test
```

Com Docker:

```bash
docker compose exec web python manage.py test
```

Os testes usam um banco temporário e não alteram os dados do `db.sqlite3` nem do Postgres.

---

## Deploy no PythonAnywhere

O projeto roda no plano gratuito do [PythonAnywhere](https://www.pythonanywhere.com), com Python 3.11 e um virtualenv próprio dentro da pasta do projeto (`env/`, não versionado). O banco em produção é o SQLite.

### Passo a passo

**1. No console Bash do PythonAnywhere**, clone o repositório e crie o ambiente:

```bash
git clone https://github.com/RogerioFernandesSilva/bookstore-docker2.git
cd bookstore-docker2
echo "env/" >> .git/info/exclude

python3.11 -m venv env
source env/bin/activate
pip install "django>=5.1,<6.0" "djangorestframework>=3.18,<4.0" psycopg2-binary gitpython "django-debug-toolbar>=8.0,<9.0"
```

**2. Prepare o banco e os arquivos estáticos:**

```bash
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

**3. Na aba Web**, crie um app com *Manual configuration* (Python 3.11) e configure:

| Campo | Valor |
|---|---|
| Source code | `/home/SEU_USUARIO/bookstore-docker2` |
| Working directory | `/home/SEU_USUARIO/bookstore-docker2` |
| Virtualenv | `/home/SEU_USUARIO/bookstore-docker2/env` |
| Static files | `/static/` → `/home/SEU_USUARIO/bookstore-docker2/staticfiles` |

**4. Edite o arquivo WSGI** (link na aba Web) e deixe apenas isto:

```python
import os
import sys

path = "/home/SEU_USUARIO/bookstore-docker2"
if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "bookstore.settings"
os.environ["DJANGO_ALLOWED_HOSTS"] = "localhost 127.0.0.1 SEU_USUARIO.pythonanywhere.com"
os.environ["SECRET_KEY"] = "DEFINA-UMA-CHAVE-PROPRIA-AQUI"  # nunca versionar esta chave

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**5. Clique em Reload** e teste `https://SEU_USUARIO.pythonanywhere.com/hello/` e a API conforme [Exemplos de uso](#exemplos-de-uso).

> O plano gratuito tem **512 MB de disco**. Não instale o Poetry no servidor (o `pip` basta) e, depois de qualquer `pip install`, rode `rm -rf ~/.cache/pip` para liberar espaço.

### Deploy automático (webhook)

A cada `push`, o GitHub avisa o servidor e o código é atualizado sem nenhum comando manual:

```text
git push ──▶ GitHub ──POST──▶ /update_server/ ──▶ git pull ──▶ app recarregado
                              (bookstore/views.py)   (REPO_PATH)  (toca o arquivo WSGI)
```

Para configurar, no repositório vá em **Settings → Webhooks → Add webhook**:

| Campo | Valor |
|---|---|
| Payload URL | `https://SEU_USUARIO.pythonanywhere.com/update_server/` |
| Content type | `application/json` |
| Evento | *Just the push event* |

Depois de salvar, a aba **Recent Deliveries** mostra cada entrega; o status esperado é `200`, e é possível reenviar uma entrega com **Redeliver**.

Para o deploy funcionar:

- o repositório no servidor deve ficar na branch `main` e **sem alterações locais** (senão o `git pull` é abortado). Por isso `__pycache__/`, `db.sqlite3`, `env/` e `staticfiles/` ficam no `.gitignore`;
- se um push alterar `pyproject.toml` com dependências novas, instale-as no servidor com `pip install` e dê Reload;
- se o push incluir novas migrações, rode `python manage.py migrate` no console do servidor.

> **Segurança:** o endpoint `/update_server/` aceita qualquer `POST` e não valida a assinatura do GitHub (`X-Hub-Signature-256`). É suficiente para este exercício; em produção, configure um *secret* no webhook e valide o cabeçalho antes de executar o `git pull`.

---

## Comandos úteis

| Comando | O que faz |
|---|---|
| `docker compose up --build` | Builda a imagem e sobe os containers, com logs no terminal |
| `docker compose up -d` | Sobe os containers em segundo plano |
| `docker compose down` | Para e remove os containers |
| `docker compose down -v` | Para e remove containers **e volumes** (reseta o banco do zero) |
| `docker compose ps` | Lista o status dos containers |
| `docker compose logs web` | Mostra os logs do container Django |
| `docker compose logs db` | Mostra os logs do container Postgres |
| `docker network ls` | Lista todas as redes Docker disponíveis |
| `docker network inspect bookstore_network` | Mostra detalhes da rede e quais containers estão conectados a ela |
| `docker compose exec web python manage.py migrate` | Aplica as migrações |
| `docker compose exec web python manage.py makemigrations` | Gera migrações a partir dos models |
| `docker compose exec web python manage.py createsuperuser` | Cria um superusuário |
| `docker compose exec web python manage.py test` | Roda a suíte de testes dentro do container |
| `docker compose exec web python manage.py shell` | Abre o shell interativo do Django dentro do container |
| `poetry run python manage.py test` | Roda os testes sem Docker |
| `poetry add <pacote>` | Adiciona uma dependência de produção ao projeto |
| `poetry add --group dev <pacote>` | Adiciona uma dependência de desenvolvimento |

---

## CI/CD com GitHub Actions

Há dois workflows em `.github/workflows/`:

**`build.yml`** — roda a cada `push`, em qualquer branch:

1. Checkout do código
2. Instala o Python 3.11 e o Poetry
3. `poetry install`
4. `poetry run python manage.py test`

**`ci.yml`** — roda a cada `push` ou `pull request` para as branches `main`/`develop`. Repete, dentro do runner do GitHub, o mesmo fluxo usado localmente com Docker:

1. Checkout do código
2. Geração do `env.dev` (com a `SECRET_KEY` vinda do secret `DJANGO_SECRET_KEY` configurado no repositório)
3. `docker compose up -d --build`
4. `docker compose exec web python manage.py migrate`
5. `docker compose exec web python manage.py test`
6. `docker compose down -v`

O status dos últimos runs aparece na aba **Actions** do repositório e nos checks de cada Pull Request.

---

## Solução de problemas

**Docker e ambiente local**

- **`env file ./env.dev not found`**: o `env.dev` não é versionado. Crie-o com `cp .env.dev.example env.dev` (no PowerShell, `Copy-Item .env.dev.example env.dev`).
- **`service "web" is not running`**: verifique se o container caiu com `docker compose logs web` — geralmente é erro de sintaxe no `settings.py` ou dependência faltando.
- **`could not translate host name "db" to address`**: o `web` tentou conectar antes do Postgres terminar de inicializar. O `healthcheck` + `depends_on: condition: service_healthy` no `docker-compose.yml` já cobre isso; se ainda ocorrer, rode `docker compose down -v` e suba de novo do zero.
- **`NotSupportedError: PostgreSQL 14 or later is required`**: a imagem do Postgres está desatualizada em relação à versão mínima exigida pelo Django. Use `postgres:16-alpine` (ou qualquer versão ≥ 14).
- **`NameError: name 'os' is not defined`**: falta `import os` no topo do `bookstore/settings.py`, necessário para ler as variáveis de ambiente do banco.
- **`make` não reconhecido no PowerShell**: `make` não vem nativo no Windows; use os comandos `docker compose` equivalentes ou instale via Chocolatey/WSL.
- **`failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`**: o Docker Desktop não está aberto/rodando no Windows. Abra o aplicativo Docker Desktop, aguarde o status mudar para "Engine running" e rode `docker info` para confirmar antes de repetir o comando. Se persistir, tente `wsl --update` (PowerShell como administrador) e reinicie o Docker Desktop.
- **`docker network inspect bookstore_network` retorna `[]` ou erro "not found"**: a rede só é criada quando os containers sobem pela primeira vez com `docker compose up`. Rode `docker compose up -d --build` antes de inspecionar a rede.

**API**

- **`401 Unauthorized`**: é o comportamento esperado quando a requisição não traz credencial. Envie o cabeçalho `Authorization: Token SEU_TOKEN`.
- **`Unable to log in with provided credentials.`** em `/api-token-auth/`: usuário ou senha incorretos, ou o usuário ainda não foi criado (`createsuperuser`).
- **`no such table` (erro 500)**: as migrações não foram aplicadas; rode `python manage.py migrate`.

**Deploy no PythonAnywhere**

- **`404` em `/bookstore/v1/...`** ou **`ModuleNotFoundError: No module named 'order'`**: o servidor está com uma versão antiga do código ou na branch errada. Confirme com `git log --oneline -3` e `ls` (devem existir `product/` e `order/`), faça `git pull origin main` e dê Reload.
- **`Disk quota exceeded` ou erro `502`**: o disco de 512 MB encheu. Veja o uso com `du -sh ~`, apague `~/.cache/pip` e `~/.cache/pypoetry`, remova ambientes virtuais e clones antigos e recarregue o app.
- **`git pull` abortado com "Your local changes would be overwritten"**: há arquivos alterados no servidor. Confira com `git status`; arquivos gerados (`__pycache__/`, `db.sqlite3`, `staticfiles/`, `env/`) precisam estar no `.gitignore` e fora do Git.
- **`ModuleNotFoundError: No module named 'debug_toolbar'`**: pacote não instalado no virtualenv do site (`pip install django-debug-toolbar` com o `env` ativado). Se o erro for `doesn't declare an explicit app_label`, falta `"debug_toolbar"` no `INSTALLED_APPS`.
- **Comandos `python manage.py ...` usando o Python errado**: ative o ambiente antes (`source env/bin/activate`); o prompt deve mostrar `(env)`.
- **Webhook com entrega `500`**: abra `/var/log/SEU_USUARIO.pythonanywhere.com.error.log` e veja o final do arquivo; as causas mais comuns são alterações locais no servidor (acima) ou caminho `REPO_PATH` incorreto.