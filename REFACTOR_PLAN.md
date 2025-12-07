# Plano de Refatoração - Padronização de Respostas e Paginação

## 📋 Objetivo

Padronizar todas as respostas da API com formatos consistentes e adicionar paginação para endpoints que retornam múltiplos resultados.

---

## 🎯 Mapeamento de Endpoints Atuais

### Endpoints de Autenticação (`/api/v1/auth`)

1. **POST `/login`** - Login (OAuth2 form)
   - Retorna: `Token` (access_token, token_type)
   - Status: Mantém formato atual (padrão OAuth2)

2. **POST `/login/json`** - Login (JSON)
   - Retorna: `Token` (access_token, token_type)
   - Status: Mantém formato atual ou padronizar

3. **GET `/me`** - Usuário atual
   - Retorna: `User` diretamente
   - **Ação**: Padronizar para formato de resposta única

### Endpoints de Usuários (`/api/v1/users`)

1. **POST `/`** - Criar usuário
   - Retorna: `User` diretamente
   - **Ação**: Padronizar para formato de criação (message, status, result, errors)

2. **GET `/`** - Listar usuários
   - Retorna: `List[User]`
   - Parâmetros atuais: `skip`, `limit`
   - **Ação**: 
     - Converter para paginação (page, perPage)
     - Adicionar meta (total, page, perPage, totalPages)
     - Adicionar filtros opcionais

3. **GET `/{user_id}`** - Buscar usuário por ID
   - Retorna: `User` diretamente
   - **Ação**: Padronizar para formato de resposta única

4. **PUT `/{user_id}`** - Atualizar usuário
   - Retorna: `User` diretamente
   - **Ação**: Padronizar para formato de atualização

---

## 📐 Formatos de Resposta Padronizados

### 1. Resposta de Criação/Atualização

```json
{
  "message": "User created successfully",
  "status": 201,
  "result": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    ...
  },
  "errors": null
}
```

### 2. Resposta de Item Único (GET por ID)

```json
{
  "message": "User retrieved successfully",
  "status": 200,
  "result": {
    "id": 1,
    "email": "user@example.com",
    ...
  },
  "errors": null
}
```

### 3. Resposta de Lista Paginada (GET múltiplos)

```json
{
  "message": "Users retrieved successfully",
  "status": 200,
  "result": [
    {
      "id": 1,
      "email": "user1@example.com",
      ...
    },
    {
      "id": 2,
      "email": "user2@example.com",
      ...
    }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "perPage": 10,
    "totalPages": 10,
    "hasNext": true,
    "hasPrevious": false
  },
  "errors": null
}
```

### 4. Resposta de Erro

```json
{
  "message": "Error message",
  "status": 400,
  "result": null,
  "errors": [
    {
      "field": "email",
      "message": "Email already registered"
    }
  ]
}
```

---

## 📦 Estrutura de Arquivos a Criar

### Schemas de Resposta (`app/schemas/`)

1. **`app/schemas/response.py`** - Schemas base de resposta
   - `BaseResponse[T]` - Resposta genérica base
   - `CreateResponse[T]` - Resposta de criação
   - `GetResponse[T]` - Resposta de item único
   - `ListResponse[T]` - Resposta de lista paginada
   - `MetaPagination` - Metadados de paginação
   - `ErrorDetail` - Detalhes de erro

### Utilitários (`app/core/`)

2. **`app/core/pagination.py`** - Utilitários de paginação
   - `PaginationParams` - Parâmetros de paginação (page, perPage)
   - `get_pagination_meta()` - Calcular metadados
   - Funções auxiliares

3. **`app/core/responses.py`** - Funções helper para criar respostas
   - `create_response()` - Criar resposta de criação
   - `get_response()` - Criar resposta de item único
   - `list_response()` - Criar resposta de lista paginada
   - `error_response()` - Criar resposta de erro

### Atualizações em Services

4. **`app/services/user_service.py`**
   - Atualizar `get_users()` para:
     - Aceitar `page` e `per_page` ao invés de `skip` e `limit`
     - Retornar total de registros
     - Suportar filtros (email, username, is_active, etc.)

---

## 🔧 Tarefas Detalhadas

### Fase 1: Criar Schemas Base

- [ ] Criar `app/schemas/response.py`
  - [ ] `ErrorDetail` schema
  - [ ] `MetaPagination` schema
  - [ ] `BaseResponse[T]` schema genérico
  - [ ] `CreateResponse[T]` schema
  - [ ] `GetResponse[T]` schema
  - [ ] `ListResponse[T]` schema

### Fase 2: Criar Utilitários

- [ ] Criar `app/core/pagination.py`
  - [ ] `PaginationParams` (pydantic model)
  - [ ] `get_pagination_meta()` função
  - [ ] Validação de parâmetros

- [ ] Criar `app/core/responses.py`
  - [ ] `create_response()` função helper
  - [ ] `get_response()` função helper
  - [ ] `list_response()` função helper
  - [ ] `error_response()` função helper

### Fase 3: Atualizar Services

- [ ] Atualizar `app/services/user_service.py`
  - [ ] Modificar `get_users()` para usar paginação (page/perPage)
  - [ ] Adicionar função `count_users()` para contar total
  - [ ] Adicionar suporte a filtros (email, username, is_active)
  - [ ] Retornar tupla (items, total) ou objeto paginado

### Fase 4: Atualizar Rotas - Auth

- [ ] Atualizar `app/api/v1/routes/auth.py`
  - [ ] `GET /me` - Usar `GetResponse[User]`
  - [ ] Opcional: Padronizar login (manter OAuth2 ou criar formato custom)

### Fase 5: Atualizar Rotas - Users

- [ ] Atualizar `app/api/v1/routes/users.py`
  - [ ] `POST /` - Usar `CreateResponse[User]`
  - [ ] `GET /` - Usar `ListResponse[User]` com paginação
  - [ ] `GET /{user_id}` - Usar `GetResponse[User]`
  - [ ] `PUT /{user_id}` - Usar `CreateResponse[User]` ou criar `UpdateResponse`

### Fase 6: Tratamento de Erros

- [ ] Criar exception handler global
  - [ ] Converter HTTPException para formato padronizado
  - [ ] Tratar erros de validação do Pydantic
  - [ ] Tratar erros genéricos

---

## 📝 Parâmetros de Paginação

### Query Parameters Padrão

```
?page=1          # Página atual (default: 1, min: 1)
?perPage=10      # Itens por página (default: 10, min: 1, max: 100)
```

### Filtros para Users

```
?email=...       # Filtrar por email (opcional, busca parcial)
?username=...    # Filtrar por username (opcional, busca parcial)
?is_active=true  # Filtrar por status ativo (opcional, boolean)
```

---

## 🔄 Exemplo de Mudança

### Antes:
```python
@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users
```

### Depois:
```python
@router.get("/", response_model=ListResponse[User])
def read_users(
    pagination: PaginationParams = Depends(),
    email: Optional[str] = None,
    username: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    users, total = get_users(
        db,
        page=pagination.page,
        per_page=pagination.per_page,
        email=email,
        username=username,
        is_active=is_active
    )
    return list_response(
        items=users,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        message="Users retrieved successfully"
    )
```

---

## ✅ Checklist Final

- [ ] Schemas de resposta criados
- [ ] Utilitários de paginação criados
- [ ] Helpers de resposta criados
- [ ] Services atualizados com paginação
- [ ] Rotas de auth atualizadas
- [ ] Rotas de users atualizadas
- [ ] Tratamento de erros padronizado
- [ ] Testes manuais realizados
- [ ] Documentação atualizada (se houver)

---

## 🎨 Considerações

1. **Backward Compatibility**: Manter compatibilidade ou criar versão nova?
   - Decisão: Criar formato novo, manter documentação clara

2. **Filtros**: Quais filtros são realmente necessários?
   - Email (busca parcial)
   - Username (busca parcial)
   - is_active (exato)

3. **Ordenação**: Adicionar ordenação (sort, orderBy)?
   - Para fase futura, não incluído agora

4. **Performance**: Considerar cache para contagem total?
   - Para fase futura, não incluído agora


