# Bookstore

Projeto Django desenvolvido durante o curso **Python Back-End** da EBAC (módulo 13).

## 🛠️ Tecnologias

- **Python** 3.11
- **Django** ^5.1
- **Poetry** — gerenciador de dependências e ambientes virtuais

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

- [Python 3.11+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)

Para verificar se o Poetry está instalado e acessível no terminal:

```powershell
poetry --version
```

> **Nota (Windows):** se o comando não for reconhecido, adicione a pasta `C:\Users\<seu_usuario>\AppData\Roaming\Python\Scripts` à variável de ambiente `PATH` do usuário e reinicie o terminal (ou o VS Code inteiro, se estiver usando o terminal integrado).

## 🚀 Passo a passo do projeto

### 1. Clonar o repositório

```powershell
git clone <url-do-repositorio>
cd bookstore
```

### 2. Instalar as dependências

O Poetry lê o arquivo `pyproject.toml` e instala tudo automaticamente, criando um ambiente virtual isolado para o projeto:

```powershell
poetry install
```

### 3. Adicionar o Django (caso ainda não esteja no projeto)

```powershell
poetry add django@^5.1
```

> Foi usada a versão 5.1 do Django porque a versão 6.x exige Python 3.12+, e este projeto está configurado para Python 3.11.

### 4. Criar o projeto Django

Dentro da pasta do repositório:

```powershell
poetry run django-admin startproject bookstore .
```

O `.` no final faz o Django criar os arquivos na pasta atual, em vez de criar uma subpasta extra.

### 5. Rodar as migrações iniciais

```powershell
poetry run python manage.py migrate
```

### 6. Subir o servidor de desenvolvimento

```powershell
poetry run python manage.py runserver
```

Depois disso, o projeto estará disponível em [http://127.0.0.1:8000](http://127.0.0.1:8000).

## 📁 Estrutura do projeto

```
bookstore/
├── bookstore/          # Configurações principais do projeto Django
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── manage.py            # Utilitário de linha de comando do Django
├── pyproject.toml       # Dependências e configuração do Poetry
└── README.md
```

## 💡 Comandos úteis do Poetry

| Comando | O que faz |
|---|---|
| `poetry install` | Instala todas as dependências do projeto |
| `poetry add <pacote>` | Adiciona uma nova dependência |
| `poetry run <comando>` | Executa um comando dentro do ambiente virtual do projeto |
| `poetry shell` | Ativa o ambiente virtual no terminal atual |
| `poetry show` | Lista as dependências instaladas |

---

*Projeto em desenvolvimento como parte do curso EBAC - Python Back-End.*
