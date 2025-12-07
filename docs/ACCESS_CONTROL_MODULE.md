# Módulo de Controle de Acesso (RBAC) – Especificação

Este documento descreve a arquitetura do módulo de **controle de acesso baseado em papéis (RBAC)** para a API em FastAPI já existente.

A ideia central:

- **Super Admin**: acesso global ao sistema.
- **Admin**: acesso amplo, mas não total.
- **Usuário comum**: acesso restrito.
- Controle **dinâmico** de quais papéis (roles) podem acessar **quais módulos** e **quais ações** podem executar (read, create, update, delete).
- Tudo gerenciado por uma **página de administração** acessível apenas ao Super Admin (e, opcionalmente, a alguns admins autorizados).

---

## 1. Objetivos

1. Permitir que o Super Admin:
   - Crie/edite papéis (roles) de acesso.
   - Defina, para cada papel, quais ações são permitidas em cada módulo.
   - Atribua papéis aos usuários.

2. Tornar o controle de acesso **centralizado e consistente**:
   - As permissões são validadas no backend.
   - O frontend apenas consome as permissões e adapta a UI (esconder botões, desabilitar ações, etc.).

3. Manter a lista de módulos **controlada pelo sistema**, não por CRUD:
   - Módulos são definidos via **seed/migração**, de acordo com as entidades/recursos da aplicação.
   - O Super Admin **não cria módulos**, apenas gerencia as permissões sobre eles.

---

## 2. Conceitos e Entidades

### 2.1. User

Usuário do sistema, autenticado via JWT.

- Cada usuário possui exatamente **um papel (role)**.
- Campos principais (já existentes + adição de `role_id`):

```
User
- id: int
- name: str
- username: str
- hashed_password: str
- is_active: bool
- role_id: int (FK -> Role.id)
```

### 2.2. Role

Tipo de usuário / perfil de acesso.

Exemplos:
- `SUPER_ADMIN` – Acesso total ao sistema (bypass nas checagens granulares).
- `ADMIN` – Acesso amplo, mas obedecendo às permissões definidas.
- `USER` – Usuário comum.

```
Role
- id: int
- key: str        # ex: "SUPER_ADMIN", "ADMIN", "USER"
- name: str       # ex: "Super Administrador"
- description: str | null
- is_system: bool # true para papéis críticos, não podem ser excluídos pelo painel
```

### 2.3. Module

Representa uma área funcional do sistema (um "módulo") sobre a qual se tem permissões.

> **Importante:**  
> Não haverá CRUD de módulos para o usuário final.
> - A lista de módulos é **controlada pelo sistema** via seeds/migrações.
> - O painel apenas **lista** os módulos já cadastrados.
> - Quando novas funcionalidades/recursos forem criados, o time de desenvolvimento adiciona novos módulos via seed.

Campos:

```
Module
- id: int
- key: str          # identificador estável, ex: "users", "access_control", "reports"
- name: str         # label amigável, ex: "Usuários", "Controle de Acesso", "Relatórios"
- description: str | null
```

### 2.4. RoleModulePermission

Define as ações permitidas de um determinado **Role** em um determinado **Module**.

```
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
- **SUPER_ADMIN** tem acesso total (sem olhar RoleModulePermission).
- Para outros roles, as ações são permitidas conforme esses flags.

---

## 3. Seeding Inicial

### 3.1. Roles seed

Criar via migration/seed:

```
Roles iniciais:
- SUPER_ADMIN
  - key: "SUPER_ADMIN"
  - name: "Super Administrador"
  - is_system: true

- ADMIN
  - key: "ADMIN"
  - name: "Administrador"
  - is_system: false

- USER
  - key: "USER"
  - name: "Usuário"
  - is_system: false
```

### 3.2. Modules seed

Exemplo inicial (pode ajustar conforme o sistema):

```
Modules iniciais:
- key: "users"
  name: "Usuários"
  description: "Gerenciamento de usuários"

- key: "access_control"
  name: "Controle de Acesso"
  description: "Gerenciar papéis e permissões"

- key: "reports"
  name: "Relatórios"
  description: "Visualização de relatórios"

- key: "inventory"
  name: "Inventário"
  description: "Gestão de itens/estoque"
```

Essa lista é mantida **pelo código** (migrations/seeds).  
O Super Admin apenas ajusta permissões por papel/módulo.

---

## 4. Regras de Autorização

### 4.1. Identificação do usuário atual

Já existe a dependência `get_current_user` (via JWT), que retorna um `User` com `role` carregado.

### 4.2. Super Admin

Convenção:

```
Role.key == "SUPER_ADMIN" => bypass em todas as checagens.
```

### 4.3. Funções principais de autorização (backend)

Camada de serviço, por exemplo em `app/services/authz_service.py`:

- `is_super_admin(user: User) -> bool`
- `has_permission(db, user, module_key, action) -> bool`
  - `module_key`: string (ex: `"users"`, `"access_control"`)
  - `action`: `"read" | "create" | "update" | "delete"`
- `enforce_permission(db, user, module_key, action) -> None`
  - Lança `HTTPException 403` se não tiver permissão.

### 4.4. Dependency `require_permission`

Será criada uma factory de dependência em algo como `app/api/deps.py`:

```python
def require_permission(module_key: str, action: str):
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        enforce_permission(db, current_user, module_key, action)
        return current_user  # opcionalmente retorna o usuário
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

## 5. API – Endpoints de Controle de Acesso

### 5.1. Listar módulos

`GET /api/v1/access/modules`

Permissão: `"access_control"`, `"read"` ou Super Admin.

### 5.2. Listar roles

`GET /api/v1/access/roles`

### 5.3. Obter matriz de permissões

`GET /api/v1/access/roles/{role_id}/permissions`

Retorno:

```
{
  "role": {...},
  "modules": [
    {
      "module_key": "users",
      "module_name": "Usuários",
      "can_read": true,
      "can_create": true,
      "can_update": false,
      "can_delete": false
    },
    ...
  ]
}
```

### 5.4. Atualizar permissões

`PUT /api/v1/access/roles/{role_id}/permissions`

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
    }
  ]
}
```

### 5.5. Atribuir papel a usuário

`PATCH /api/v1/users/{user_id}/role`

---

## 6. Uso no frontend

Um painel permitirá:

- Escolher um role
- Ver a matriz de permissões (módulos × ações)
- Atualizar permissões
- Alterar papéis de usuários

---

## 7. Integração com o backend existente

1. Criar models (`Role`, `Module`, `RoleModulePermission`) e ajustar `User`.
2. Criar seeds para roles e módulos.
3. Implementar autorização com `require_permission`.
4. Proteger as rotas de cada módulo usando o padrão:
   - `"read" | "create" | "update" | "delete"`

---

## 8. Próximos Passos

- Gerar migrações Alembic
- Implementar serviços
- Criar rotas de controle de acesso
- Integrar com o frontend

---

