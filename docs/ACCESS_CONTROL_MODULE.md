# Módulo de Controle de Acesso (RBAC) – Especificação (v2)

Este documento descreve a arquitetura do módulo de **controle de acesso baseado em papéis (RBAC)** para a API em FastAPI já existente, incluindo:

- Uso de um **`MODULES_REGISTRY`** em código para sincronizar módulos com o banco.
- **CRUD de Roles** (papéis) via sistema, com proteção para roles de sistema (`is_system`).

A ideia central:

- **Super Admin**: acesso global ao sistema.
- **Admin / Admin Clínica / outros**: acesso amplo, configurável.
- **Usuário comum**: acesso restrito.
- Controle **dinâmico** de quais papéis (roles) podem acessar **quais módulos** e **quais ações** podem executar (read, create, update, delete).
- Tudo gerenciado por uma **página de administração** acessível apenas ao Super Admin (e, opcionalmente, a alguns admins autorizados).

---

## 1. Objetivos

1. Permitir que o Super Admin:
   - Crie/edite/exclua papéis (roles) **não-sistêmicos**.
   - Defina, para cada papel, quais ações são permitidas em cada módulo.
   - Atribua papéis aos usuários.
   - Controle se um usuário pode ou não acessar o sistema (`can_access_system`).

2. Tornar o controle de acesso **centralizado e consistente**:
   - As permissões são validadas no backend.
   - O frontend apenas consome as permissões e adapta a UI (esconder botões, desabilitar ações, etc.).

3. Manter a lista de módulos **controlada pelo sistema, via código**, e sincronizada com o banco de forma **idempotente**:
   - Módulos definidos em um **registry em Python** (`MODULES_REGISTRY`).
   - Sincronização com a tabela `modules` feita via migração/seed segura.

---

## 2. Conceitos e Entidades

### 2.1. User

Usuário do sistema, autenticado via JWT.

- Cada usuário possui exatamente **um papel (role)**.
- Possui flags de controle de acesso.

Campos principais:

```text
User
- id: int
- name: str
- username: str
- hashed_password: str
- is_active: bool              # se o usuário está ativo no sistema
- can_access_system: bool      # se pode efetivamente fazer login
- role_id: int (FK -> Role.id)
```

Regra:

- No login, além de validar as credenciais, o backend deve checar:
  - `is_active == True`
  - `can_access_system == True`
  - Caso contrário, negar autenticação.

---

### 2.2. Role

Tipo de usuário / perfil de acesso.

Exemplos:
- `SUPER_ADMIN` – Acesso total ao sistema (bypass nas checagens granulares).
- `ADMIN` – Acesso amplo, obedecendo às permissões definidas.
- `CLINIC_ADMIN` – admin de clínica (exemplo de papel adicional).
- `USER` – Usuário comum.

```text
Role
- id: int
- key: str        # ex: "SUPER_ADMIN", "ADMIN", "CLINIC_ADMIN", "USER"
- name: str       # ex: "Super Administrador", "Admin Clínica"
- description: str | null
- is_system: bool # true para papéis críticos, não podem ser excluídos pelo painel
```

Regras para `Role`:

- Roles com `is_system = true`:
  - Não podem ser excluídas via API.
  - Não pode alterar `key`.
  - Podem ter `name`/`description` ajustados com cuidado, se desejado.

- Roles com `is_system = false`:
  - Podem ser criadas, atualizadas e excluídas via CRUD no sistema.

---

### 2.3. Module

Representa uma área funcional do sistema (um "módulo") sobre a qual se tem permissões.

**Não há CRUD de módulos via sistema**.  
Toda a gestão de módulos é feita via código, usando `MODULES_REGISTRY` e migrações.

```text
Module
- id: int
- key: str          # identificador estável, ex: "users", "access_control", "appointments", "billing"
- name: str         # label amigável, ex: "Usuários", "Controle de Acesso", "Agendamentos"
- description: str | null
```

---

### 2.4. RoleModulePermission

Define as ações permitidas de um determinado **Role** em um determinado **Module**.

```text
RoleModulePermission
- id: int
- role_id: int     (FK -> Role.id)
- module_id: int   (FK -> Module.id)
- can_read: bool
- can_create: bool
- can_update: bool
- can_delete: bool

Unique: (role_id, module_id)
```

Regra geral:
- **SUPER_ADMIN** tem acesso total (sem olhar `RoleModulePermission`).
- Para outros roles, as ações são permitidas conforme esses flags.

---

## 3. `MODULES_REGISTRY` e sincronização de módulos

### 3.1. Registry em código

Definir um registro central de módulos, por exemplo em `app/core/modules_registry.py`:

```python
MODULES_REGISTRY = [
    {
        "key": "users",
        "name": "Usuários",
        "description": "Gerenciamento de usuários",
    },
    {
        "key": "access_control",
        "name": "Controle de Acesso",
        "description": "Papéis e permissões",
    },
    {
        "key": "appointments",
        "name": "Agendamentos",
        "description": "Gestão de consultas e horários",
    },
    {
        "key": "billing",
        "name": "Faturamento",
        "description": "Cobranças e pagamentos",
    },
    # novos módulos devem ser adicionados aqui
]
```

### 3.2. Estratégia de sincronização com o banco

Em uma **migration Alembic** (ou script de seed de sistema), realizar um **sync idempotente**:

- Para cada item do `MODULES_REGISTRY`:
  - Se `key` ainda não existe na tabela `modules` → **`INSERT`**.
  - Se `key` já existe → **`UPDATE`** de `name`/`description` (se desejar).
- Não remover módulos existentes no banco automaticamente (para não quebrar histórico, logs etc.).

Exemplo de lógica em SQL (Postgres):

```sql
INSERT INTO modules (key, name, description)
VALUES ('users', 'Usuários', 'Gerenciamento de usuários')
ON CONFLICT (key) DO UPDATE
SET name = EXCLUDED.name,
    description = EXCLUDED.description;
```

Essa lógica deve ser aplicada para cada módulo do `MODULES_REGISTRY`.

### 3.3. Boas práticas

- Nunca fazer migrations que:
  - `TRUNCATE TABLE modules` em produção.
  - Sobrescrevam permissões ou relacionamentos com base em uma lista fixa.
- Sempre garantir que a sincronização seja **aditiva** e **não destrutiva**.

---

## 4. Regras de Autorização

### 4.1. Identificação do usuário atual

Já existe a dependência `get_current_user` (via JWT), que retorna um `User` com `role` carregado.

No fluxo de login, além de senha/usuário, deve ser checado:

- `user.is_active`
- `user.can_access_system`

Caso algum desses seja falso, retornar erro de autenticação (401/403).

---

### 4.2. Super Admin

Convenção:

```text
Role.key == "SUPER_ADMIN" => bypass em todas as checagens de RoleModulePermission.
```

Ou seja:

- `SUPER_ADMIN` pode acessar qualquer rota protegida, independentemente de permissões cadastradas.
- Essa decisão pode ser centralizada na função `is_super_admin(user)`.

---

### 4.3. Funções principais de autorização (backend)

Camada de serviço, por exemplo em `app/services/authz_service.py`:

- `is_super_admin(user: User) -> bool`
- `has_permission(db, user, module_key, action) -> bool`
  - `module_key`: string (ex: `"users"`, `"access_control"`, `"appointments"`)
  - `action`: `"read" | "create" | "update" | "delete"`
- `enforce_permission(db, user, module_key, action) -> None`
  - Lança `HTTPException 403` se não tiver permissão.

---

### 4.4. Dependency `require_permission`

Será criada uma factory de dependência em algo como `app/api/deps.py`:

```python
def require_permission(module_key: str, action: str):
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        enforce_permission(db, current_user, module_key, action)
        return current_user  # opcional
    return dependency
```

Uso nas rotas:

```python
@router.get(
    "",
    response_model=list[UserRead],
    dependencies=[Depends(require_permission("users", "read"))],
)
def list_users(...):
    ...
```

---

## 5. API – Módulo de Controle de Acesso

Todas essas rotas devem ser expostas sob um prefixo, por exemplo:

- `/api/v1/access/*`

E protegidas por permissões adequadas, tipicamente:

- Apenas `SUPER_ADMIN`, ou
- Roles com permissão no módulo `"access_control"`.

---

### 5.1. Módulos – leitura

> Não há CRUD de módulos via sistema. Apenas leitura.

**Endpoint:**

- `GET /api/v1/access/modules`

**Permissão:**

- `"access_control"`, `"read"` (ou `SUPER_ADMIN`).

**Retorno:**

```json
[
  {
    "id": 1,
    "key": "users",
    "name": "Usuários",
    "description": "Gerenciamento de usuários"
  },
  {
    "id": 2,
    "key": "access_control",
    "name": "Controle de Acesso",
    "description": "Papéis e permissões"
  }
]
```

---

### 5.2. Roles – CRUD

Esses endpoints permitem criar, listar, atualizar e excluir roles.  
Sempre respeitando `is_system` para proteger papéis críticos.

#### 5.2.1. Listar roles

`GET /api/v1/access/roles`

- Permissão: `"access_control"`, `"read"`.

Retorno:

```json
[
  { "id": 1, "key": "SUPER_ADMIN", "name": "Super Administrador", "description": null, "is_system": true },
  { "id": 2, "key": "ADMIN", "name": "Administrador", "description": null, "is_system": true },
  { "id": 3, "key": "CLINIC_ADMIN", "name": "Admin Clínica", "description": null, "is_system": false },
  { "id": 4, "key": "USER", "name": "Usuário", "description": null, "is_system": false }
]
```

#### 5.2.2. Obter detalhes de uma role

`GET /api/v1/access/roles/{role_id}`

- Permissão: `"access_control"`, `"read"`.

#### 5.2.3. Criar role

`POST /api/v1/access/roles`

- Permissão: `"access_control"`, `"create"`.
- Apenas roles com `is_system = false` podem ser criadas via API.
- Campos de entrada:

```json
{
  "key": "CLINIC_ADMIN",
  "name": "Admin Clínica",
  "description": "Administração da clínica"
}
```

No backend:

- `is_system` sempre `false` para roles criadas via API (roles de sistema são criadas via migration/seed).
- Validar unicidade de `key`.

#### 5.2.4. Atualizar role

`PUT /api/v1/access/roles/{role_id}`

- Permissão: `"access_control"`, `"update"`.

Regras:

- Se `role.is_system == true`:
  - Não permitir alterar `key`.
  - Opcional: permitir apenas alteração de `name`/`description`.

- Se `role.is_system == false`:
  - Permitir alterar `key`, `name`, `description`, desde que:
    - `key` permaneça única.

#### 5.2.5. Deletar role

`DELETE /api/v1/access/roles/{role_id}`

- Permissão: `"access_control"`, `"delete"`.

Regras:

- Se `role.is_system == true` → **bloquear** e retornar erro (ex: 400/403).
- Se `role.is_system == false`:
  - Verificar se existem usuários associados:
    - Pode exigir que os usuários sejam migrados para outra role antes.
    - Ou bloquear a exclusão enquanto houver vínculos.

---

### 5.3. Permissões por Role (Matriz de Permissões)

#### 5.3.1. Buscar matriz de permissões

`GET /api/v1/access/roles/{role_id}/permissions`

- Permissão: `"access_control"`, `"read"`.

Retorno esperado para montar a tabela:

```json
{
  "role": {
    "id": 3,
    "key": "CLINIC_ADMIN",
    "name": "Admin Clínica"
  },
  "modules": [
    {
      "module_id": 1,
      "module_key": "users",
      "module_name": "Usuários",
      "can_read": true,
      "can_create": true,
      "can_update": true,
      "can_delete": false
    },
    {
      "module_id": 2,
      "module_key": "access_control",
      "module_name": "Controle de Acesso",
      "can_read": true,
      "can_create": false,
      "can_update": false,
      "can_delete": false
    },
    {
      "module_id": 3,
      "module_key": "appointments",
      "module_name": "Agendamentos",
      "can_read": true,
      "can_create": true,
      "can_update": true,
      "can_delete": true
    },
    {
      "module_id": 4,
      "module_key": "billing",
      "module_name": "Faturamento",
      "can_read": true,
      "can_create": true,
      "can_update": true,
      "can_delete": false
    }
  ]
}
```

A lógica no backend:

- Carregar todos os módulos (tabela `modules`).
- Carregar permissões existentes em `role_module_permissions` para este `role_id`.
- Montar uma lista para cada módulo, com `can_* = false` por padrão, e sobrescrever com `true` onde houver permissão cadastrada.

#### 5.3.2. Atualizar matriz de permissões

`PUT /api/v1/access/roles/{role_id}/permissions`

- Permissão: `"access_control"`, `"update"`.

Payload recomendado:

```json
{
  "permissions": [
    {
      "module_key": "users",
      "can_read": true,
      "can_create": true,
      "can_update": true,
      "can_delete": false
    },
    {
      "module_key": "access_control",
      "can_read": true,
      "can_create": false,
      "can_update": false,
      "can_delete": false
    },
    {
      "module_key": "appointments",
      "can_read": true,
      "can_create": true,
      "can_update": true,
      "can_delete": true
    },
    {
      "module_key": "billing",
      "can_read": true,
      "can_create": true,
      "can_update": true,
      "can_delete": false
    }
  ]
}
```

Comportamento esperado:

- Resolver `module_id` a partir de `module_key`.
- Para simplificar e ser previsível:
  - Excluir permissões antigas deste `role_id` em `role_module_permissions`.
  - Recriar os registros com base no payload.
- Não alterar outros roles.

Restrições:

- Opcionalmente, impedir alteração das permissões do `SUPER_ADMIN` (ele já tem bypass).  
  Ou simplesmente permitir edição, mas manter o bypass na lógica de autorização.

---

### 5.4. Atribuir Role a Usuário

`PATCH /api/v1/users/{user_id}/role`

- Permissão: `"access_control"`, `"update"` ou `"users"`, `"update"` (decisão de negócio).

Payload:

```json
{
  "role_id": 3
}
```

Regras:

- Não permitir que um usuário comum altere sua própria role.
- Apenas Super Admin (e quem tiver permissão apropriada) pode alterar a role de outros.

---

## 6. Tela de Atualização de Permissões (Vista do Frontend)

A tela de controle de acesso para um `role` deve:

1. Permitir escolher um role (`GET /access/roles`).
2. Buscar a matriz de permissões (`GET /access/roles/{role_id}/permissions`).
3. Renderizar uma tabela do tipo:

   | Módulo           | read | create | update | delete |
   | ---------------- | ---- | ------ | ------ | ------ |
   | Usuários         | [ ]  | [ ]    | [ ]    | [ ]    |
   | Controle Acesso  | [ ]  | [ ]    | [ ]    | [ ]    |
   | Agendamentos     | [ ]  | [ ]    | [ ]    | [ ]    |
   | Faturamento      | [ ]  | [ ]    | [ ]    | [ ]    |

4. A cada toggle de checkbox, atualizar o estado local.
5. Ao clicar em **Salvar**, enviar:

   - `PUT /access/roles/{role_id}/permissions` com o payload descrito acima.

---

## 7. Considerações de Segurança e Produção

- **Módulos (`modules`)**:
  - Mantidos pelo `MODULES_REGISTRY` em código.
  - Sincronizados via migrations/seed idempotente (INSERT com `ON CONFLICT DO UPDATE`).
  - Nunca truncar/zerar a tabela em produção.

- **Roles de sistema**:
  - Criadas via migration/seed inicial (ex.: `SUPER_ADMIN`, `ADMIN`, `USER`).
  - Marcadas com `is_system = true`.
  - Não podem ser excluídas ou ter `key` alterada via API.

- **Roles customizadas**:
  - Criadas via CRUD pelo Super Admin.
  - `is_system = false`.
  - Podem ser removidas, desde que regras de integridade (usuários vinculados) sejam respeitadas.

- **Permissões (`role_module_permissions`)**:
  - Sempre gerenciadas via sistema (tela).
  - Não resetar globalmente em produção via migrations.

- **Flags de usuário (`can_access_system`, `is_active`)**:
  - Controladas via sistema (telas de administração de usuário).
  - Usadas na autenticação para permitir/bloquear login.

---

## 8. Próximos Passos para Implementação

1. Implementar `MODULES_REGISTRY` e a migration de sync com `modules`.
2. Implementar models/schemas/rotas de **CRUD de Role**:
   - `GET /access/roles`
   - `GET /access/roles/{role_id}`
   - `POST /access/roles`
   - `PUT /access/roles/{role_id}`
   - `DELETE /access/roles/{role_id}`
3. Implementar os endpoints de permissões:
   - `GET /access/roles/{role_id}/permissions`
   - `PUT /access/roles/{role_id}/permissions`
4. Ajustar autenticação para respeitar `can_access_system`.
5. Aplicar `require_permission(module_key, action)` nas rotas de negócio.
6. Criar a tela de controle de acesso no frontend consumindo esses endpoints.

---
