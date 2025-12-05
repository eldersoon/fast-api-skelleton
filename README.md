# FastAPI Project

Projeto FastAPI estruturado de forma profissional com autenticação JWT, SQLAlchemy e Alembic.

## Estrutura do Projeto

```
.
├── app
│   ├── api
│   │   └── v1
│   │       └── routes
│   │           ├── auth.py      # Rotas de autenticação
│   │           └── users.py     # Rotas de usuários
│   ├── core
│   │   ├── config.py            # Configurações da aplicação
│   │   └── security.py          # Funções de segurança (JWT, hash)
│   ├── db
│   │   ├── base.py              # Base do SQLAlchemy
│   │   └── session.py           # Configuração do banco de dados
│   ├── models
│   │   └── user.py              # Models do SQLAlchemy
│   ├── schemas
│   │   ├── auth.py              # Schemas Pydantic para autenticação
│   │   └── user.py              # Schemas Pydantic para usuários
│   ├── services
│   │   └── user_service.py      # Lógica de negócio dos usuários
│   └── main.py                  # Aplicação FastAPI principal
├── alembic
│   ├── versions/                # Migrações do Alembic
│   ├── env.py
│   └── script.py.mako
├── alembic.ini                  # Configuração do Alembic
├── requirements.txt             # Dependências do projeto
├── run.py                       # Entry point da aplicação
├── Dockerfile                   # Imagem Docker da API
├── docker-compose.yml           # Docker Compose para produção
├── docker-compose-dev.yml       # Docker Compose para desenvolvimento
├── .dockerignore                # Arquivos ignorados no build Docker
├── env.example                  # Exemplo de variáveis de ambiente
├── env.development.example      # Exemplo para desenvolvimento
└── env.production.example       # Exemplo para produção
```

## Instalação

1. **Criar ambiente virtual:**

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

2. **Instalar dependências:**

```bash
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente:**

O projeto suporta configuração por ambiente. Você pode criar arquivos específicos para cada ambiente:

**Desenvolvimento:**

```bash
cp env.development.example .env.development
# Edite o arquivo .env.development com suas configurações
```

**Produção:**

```bash
cp env.production.example .env.production
# Edite o arquivo .env.production com suas configurações
```

O arquivo será carregado automaticamente baseado na variável de ambiente `APP_ENV`. Por padrão, usa `development` se `APP_ENV` não estiver definida.

## Configuração

### Variáveis de Ambiente

Cada arquivo `.env.{ambiente}` deve conter as seguintes variáveis:

- `APP_ENV`: Ambiente atual (development, production, etc.)
- `DATABASE_URL`: URL de conexão com o banco de dados (formato: `postgresql+psycopg2://user:password@host:port/database`)
- `JWT_SECRET_KEY`: Chave secreta para JWT (gere uma chave forte: `openssl rand -hex 32`)
- `JWT_ALGORITHM`: Algoritmo JWT (padrão: HS256)
- `DEBUG`: Modo debug (True/False)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tempo de expiração do token em minutos
- `CORS_ORIGINS`: Lista de origens permitidas para CORS (formato JSON)

### Banco de Dados

1. **Criar banco de dados PostgreSQL:**

```sql
CREATE DATABASE fastapi_dev;
```

2. **Executar migrações:**

```bash
# Certifique-se de que o ambiente virtual está ativado
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Execute as migrações
alembic upgrade head
```

## Executando a Aplicação

### Opção 1: Localmente (sem Docker)

> ⚠️ **Importante:** Certifique-se de ativar o ambiente virtual antes de executar:
>
> ```bash
> source .venv/bin/activate  # No Windows: .venv\Scripts\activate
> ```

**Desenvolvimento:**

```bash
# Ativar ambiente virtual (se ainda não ativou)
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Define o ambiente (opcional, padrão é 'development')
export APP_ENV=development  # No Windows: set APP_ENV=development

uvicorn run:app --reload
```

**Produção:**

```bash
# Ativar ambiente virtual (se ainda não ativou)
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

export APP_ENV=production  # No Windows: set APP_ENV=production

uvicorn run:app --host 0.0.0.0 --port 8000
```

A aplicação estará disponível em: http://localhost:8000

Documentação interativa:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Opção 2: Com Docker

O projeto inclui configuração Docker com PostgreSQL e API opcional.

#### Desenvolvimento

**Iniciar apenas o PostgreSQL:**

```bash
docker-compose -f docker-compose-dev.yml up postgres -d
```

**Iniciar PostgreSQL + API:**

```bash
docker-compose -f docker-compose-dev.yml up
```

**Parar os serviços:**

```bash
docker-compose -f docker-compose-dev.yml down
```

**Ver logs:**

```bash
docker-compose -f docker-compose-dev.yml logs -f
```

#### Produção

**Iniciar serviços:**

```bash
docker-compose up -d
```

**Parar serviços:**

```bash
docker-compose down
```

**Ver logs:**

```bash
docker-compose logs -f
```

#### Credenciais Padrão do PostgreSQL

- **Usuário:** `postgres`
- **Senha:** `postgres`
- **Banco de dados (dev):** `fastapi_dev`
- **Banco de dados (prod):** `fastapi`
- **Porta:** `5432`

> ⚠️ **Importante:** As credenciais acima são apenas para desenvolvimento. Em produção, altere as senhas!

#### Executando Migrações no Docker

**Desenvolvimento:**

```bash
# Se a API estiver rodando no Docker
docker-compose -f docker-compose-dev.yml exec api alembic upgrade head

# Ou se estiver rodando localmente, apenas conecte ao PostgreSQL do Docker
export APP_ENV=development
alembic upgrade head
```

**Produção:**

```bash
docker-compose exec api alembic upgrade head
```

#### Reconstruir a imagem da API

```bash
# Desenvolvimento
docker-compose -f docker-compose-dev.yml build --no-cache api

# Produção
docker-compose build --no-cache api
```

## Migrações (Alembic)

> ⚠️ **Importante:** Certifique-se de ativar o ambiente virtual antes de executar comandos do Alembic:
>
> ```bash
> source .venv/bin/activate  # No Windows: .venv\Scripts\activate
> ```

- **Criar nova migração:**

```bash
alembic revision --autogenerate -m "descrição da migração"
```

- **Aplicar migrações:**

```bash
alembic upgrade head
```

- **Reverter última migração:**

```bash
alembic downgrade -1
```

- **Ver status das migrações:**

```bash
alembic current
alembic history
```

## Endpoints Principais

### Autenticação

- `POST /api/v1/auth/login` - Login (OAuth2 form)
- `POST /api/v1/auth/login/json` - Login (JSON)
- `GET /api/v1/auth/me` - Obter usuário atual

### Usuários

- `POST /api/v1/users/` - Criar usuário
- `GET /api/v1/users/` - Listar usuários (requer autenticação)
- `GET /api/v1/users/{user_id}` - Obter usuário por ID (requer autenticação)
- `PUT /api/v1/users/{user_id}` - Atualizar usuário (requer autenticação)

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy 2.0**: ORM para Python
- **Alembic**: Ferramenta de migração de banco de dados
- **Pydantic**: Validação de dados
- **JWT**: Autenticação via tokens
- **Passlib**: Hash de senhas com bcrypt
- **Uvicorn**: Servidor ASGI

## Próximos Passos

- [ ] Adicionar testes
- [ ] Configurar CI/CD
- [ ] Adicionar logging
- [ ] Implementar rate limiting
- [ ] Adicionar mais models e endpoints
