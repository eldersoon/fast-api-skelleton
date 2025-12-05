# Guia Docker

Este documento fornece informações detalhadas sobre como usar Docker neste projeto.

## Estrutura Docker

O projeto inclui:

- **Dockerfile**: Imagem da API FastAPI
- **docker-compose-dev.yml**: Configuração para desenvolvimento
- **docker-compose.yml**: Configuração para produção

## Credenciais Padrão

### PostgreSQL

- **Usuário:** `postgres`
- **Senha:** `postgres`
- **Banco de dados (dev):** `fastapi_dev`
- **Banco de dados (prod):** `fastapi`
- **Porta:** `5432`

> ⚠️ **Atenção:** Estas credenciais são apenas para desenvolvimento. Em produção, altere todas as senhas!

## Desenvolvimento

### Opções de Execução

#### 1. Apenas PostgreSQL

Se você quiser rodar apenas o PostgreSQL no Docker e a API localmente:

```bash
docker-compose -f docker-compose-dev.yml up postgres -d
```

Depois, configure seu `.env.development`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/fastapi_dev
```

#### 2. PostgreSQL + API no Docker

Para rodar tudo no Docker:

```bash
docker-compose -f docker-compose-dev.yml up
```

A API estará disponível em `http://localhost:8000` com hot reload ativado.

### Comandos Úteis

```bash
# Iniciar em background
docker-compose -f docker-compose-dev.yml up -d

# Ver logs
docker-compose -f docker-compose-dev.yml logs -f

# Ver logs apenas da API
docker-compose -f docker-compose-dev.yml logs -f api

# Parar serviços
docker-compose -f docker-compose-dev.yml down

# Parar e remover volumes (⚠️ apaga dados do banco)
docker-compose -f docker-compose-dev.yml down -v

# Reconstruir a imagem da API
docker-compose -f docker-compose-dev.yml build --no-cache api

# Executar comando dentro do container da API
docker-compose -f docker-compose-dev.yml exec api bash

# Executar migrações
docker-compose -f docker-compose-dev.yml exec api alembic upgrade head
```

## Produção

### Iniciar Serviços

```bash
docker-compose up -d
```

### Comandos Úteis

```bash
# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Reconstruir após mudanças
docker-compose up -d --build

# Executar migrações
docker-compose exec api alembic upgrade head
```

### Variáveis de Ambiente em Produção

Para produção, é recomendado usar variáveis de ambiente do sistema ou um arquivo `.env.production`:

```bash
export JWT_SECRET_KEY="sua-chave-secreta-muito-forte"
export CORS_ORIGINS='["https://seudominio.com"]'
docker-compose up -d
```

Ou edite o arquivo `docker-compose.yml` diretamente para adicionar variáveis específicas.

## Volumes

Os dados do PostgreSQL são persistidos em volumes Docker:

- **Desenvolvimento:** `postgres_data_dev`
- **Produção:** `postgres_data`

Para remover os volumes e começar do zero:

```bash
# Desenvolvimento
docker-compose -f docker-compose-dev.yml down -v

# Produção
docker-compose down -v
```

## Network

Todos os serviços estão na mesma rede Docker (`fastapi_network`), permitindo comunicação interna usando os nomes dos serviços como hostnames:

- `postgres:5432` - Acesso ao PostgreSQL de dentro dos containers
- `api:8000` - Acesso à API de dentro dos containers

## Troubleshooting

### Porta 5432 já está em uso

Se você já tem PostgreSQL rodando localmente, você pode:

1. Parar o PostgreSQL local
2. Ou alterar a porta no `docker-compose-dev.yml`:
   ```yaml
   ports:
     - "5433:5432"  # Mude para outra porta
   ```

### Porta 8000 já está em uso

Altere a porta no `docker-compose-dev.yml`:

```yaml
ports:
  - "8001:8000"  # A API estará em http://localhost:8001
```

### Erro de conexão com o banco

1. Verifique se o PostgreSQL está saudável:
   ```bash
   docker-compose -f docker-compose-dev.yml ps
   ```

2. Verifique os logs:
   ```bash
   docker-compose -f docker-compose-dev.yml logs postgres
   ```

3. Teste a conexão manualmente:
   ```bash
   docker-compose -f docker-compose-dev.yml exec postgres psql -U postgres -d fastapi_dev
   ```

### A API não está carregando mudanças (hot reload)

Certifique-se de que:

1. O volume está montado corretamente no `docker-compose-dev.yml`
2. Você está usando o comando `--reload` (já está configurado)
3. Os arquivos não estão sendo ignorados pelo `.dockerignore`

### Limpar tudo e começar do zero

```bash
# Parar e remover containers, networks e volumes
docker-compose -f docker-compose-dev.yml down -v

# Remover imagens
docker rmi fast-api-api  # ou o nome da sua imagem

# Limpar sistema Docker (cuidado!)
docker system prune -a --volumes
```

## Dicas

1. **Desenvolvimento Local + PostgreSQL Docker**: A maneira mais comum é rodar apenas o PostgreSQL no Docker e a API localmente para ter hot reload mais rápido.

2. **Logs em Tempo Real**: Use `docker-compose logs -f` para acompanhar os logs em tempo real.

3. **Inspecionar Container**: Use `docker-compose exec api bash` para entrar no container e debugar.

4. **Backup do Banco**: Para fazer backup dos dados:
   ```bash
   docker-compose -f docker-compose-dev.yml exec postgres pg_dump -U postgres fastapi_dev > backup.sql
   ```

5. **Restaurar Backup**:
   ```bash
   cat backup.sql | docker-compose -f docker-compose-dev.yml exec -T postgres psql -U postgres fastapi_dev
   ```

