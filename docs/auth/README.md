# Módulo de Autenticação e Controle de Acesso

## Visão Geral
O módulo de autenticação e controle de acesso do Holyvoice fornece um sistema robusto de gerenciamento de usuários, permissões e políticas de acesso.

## Funcionalidades

### Níveis de Acesso
1. **Administrador**
   - Acesso total ao sistema
   - Gerenciamento de usuários
   - Configuração de políticas de acesso
   - Visualização de logs do sistema

2. **Usuário Normal**
   - Acesso baseado em permissões configuradas
   - Gerenciamento de projetos próprios
   - Visualização limitada do sistema

3. **Visualizador**
   - Apenas visualização de conteúdo permitido
   - Sem permissões de modificação

### Permissões
- **Leitura**: Visualização de recursos
- **Escrita**: Criação e edição de recursos
- **Execução**: Execução de processos e tarefas
- **Administração**: Gerenciamento de configurações

### Políticas de Acesso
- Políticas padrão pré-configuradas
- Políticas personalizadas por grupo
- Herança de permissões
- Restrições por recurso

### Registro de Atividades
- Log detalhado de todas as ações
- Trilha de auditoria
- Histórico de modificações
- Alertas de segurança

## Interface do Usuário

### Telas Principais
1. **Login**
   - Formulário de login
   - Recuperação de senha
   - 2FA (quando habilitado)

2. **Cadastro de Usuários**
   - Informações básicas
   - Configuração de permissões
   - Atribuição de grupos

3. **Painel de Administração**
   - Gerenciamento de usuários
   - Configuração de políticas
   - Visualização de logs

4. **Perfil do Usuário**
   - Informações pessoais
   - Alteração de senha
   - Configurações de 2FA

## Banco de Dados

### Tabelas Principais
```sql
-- Usuários
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Grupos
CREATE TABLE groups (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Permissões
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Usuários-Grupos
CREATE TABLE user_groups (
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES groups(id),
    PRIMARY KEY (user_id, group_id)
);

-- Grupos-Permissões
CREATE TABLE group_permissions (
    group_id UUID REFERENCES groups(id),
    permission_id UUID REFERENCES permissions(id),
    PRIMARY KEY (group_id, permission_id)
);

-- Logs de Atividade
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Segurança

### Medidas Implementadas
- Senhas hasheadas com Argon2
- Proteção contra força bruta
- Rate limiting
- CSRF Protection
- XSS Prevention
- Sessões seguras
- Tokens JWT com rotação

### Boas Práticas
- Validação de entrada
- Sanitização de saída
- Princípio do menor privilégio
- Logs de segurança
- Monitoramento de atividades suspeitas

## API Endpoints

### Autenticação
```
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh-token
POST /api/auth/forgot-password
POST /api/auth/reset-password
```

### Usuários
```
GET /api/users
POST /api/users
GET /api/users/{id}
PUT /api/users/{id}
DELETE /api/users/{id}
```

### Grupos e Permissões
```
GET /api/groups
POST /api/groups
GET /api/permissions
POST /api/permissions
```

## Configuração

### Variáveis de Ambiente
```env
# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRATION=24h
JWT_REFRESH_EXPIRATION=7d

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=holyvoice
DB_USER=postgres
DB_PASSWORD=your-password

# Security
RATE_LIMIT_WINDOW=15m
RATE_LIMIT_MAX_REQUESTS=100
SESSION_SECRET=your-session-secret
```