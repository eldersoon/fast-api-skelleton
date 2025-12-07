"""
Registry central de módulos do sistema.

Este registry define todos os módulos disponíveis no sistema.
Os módulos são sincronizados com o banco de dados via migrations/seeds.

IMPORTANTE:
- Módulos devem ser adicionados aqui quando novas funcionalidades são criadas.
- Nunca remover módulos deste registry em produção (pode quebrar histórico/permissões).
- A sincronização com o banco é idempotente (INSERT ... ON CONFLICT DO UPDATE).
"""

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
]

