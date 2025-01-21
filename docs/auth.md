# Módulo de Autenticação e Controle de Acesso

## Visão Geral
O módulo de autenticação e controle de acesso do HolyVoice fornece um sistema robusto e seguro para gerenciamento de usuários, permissões e auditoria de ações.

## Funcionalidades

### 1. Gestão de Usuários
- Cadastro de novos usuários
- Atualização de perfil
- Recuperação de senha
- Autenticação 2FA (opcional)
- Status de usuário (ativo/inativo/bloqueado)

### 2. Níveis de Acesso
- **Administrador**
  - Acesso total ao sistema
  - Gerenciamento de usuários
  - Configuração de políticas de acesso
  - Visualização de logs de auditoria

- **Supervisor**
  - Gerenciamento de projetos
  - Aprovação de conteúdo
  - Visualização de relatórios
  - Gestão de equipe

- **Usuário**
  - Acesso aos projetos designados
  - Execução de tarefas atribuídas
  - Edição de conteúdo próprio

- **Visualizador**
  - Apenas visualização
  - Sem permissão de edição

### 3. Permissões Granulares
- Leitura
- Escrita
- Execução
- Aprovação
- Publicação
- Administração

### 4. Políticas de Acesso
- Criação de políticas personalizadas
- Templates de permissões
- Herança de permissões
- Restrições por módulo

### 5. Auditoria
- Log de todas as ações
- Registro de tentativas de acesso
- Histórico de alterações
- Relatórios de atividade

## Interface do Usuário

### Telas Principais
1. **Login**
   - Formulário de login
   - Recuperação de senha
   - 2FA (quando ativado)

2. **Cadastro**
   - Informações básicas
   - Validação de email
   - Termos de uso

3. **Painel de Administração**
   - Lista de usuários
   - Gerenciamento de permissões
   - Logs de auditoria
   - Configurações do sistema

4. **Perfil do Usuário**
   - Dados pessoais
   - Alteração de senha
   - Configurações de 2FA
   - Preferências

## Segurança

### Medidas Implementadas
- Senhas hasheadas (Argon2)
- Tokens JWT com rotação
- Rate limiting
- Proteção contra força bruta
- Sessões com timeout
- CSRF Protection
- XSS Prevention

### Políticas de Senha
- Mínimo 8 caracteres
- Combinação de letras, números e símbolos
- Histórico de senhas
- Expiração periódica
- Bloqueio após tentativas falhas

## Banco de Dados

### Tabelas Principais
1. **users**
   - Dados básicos dos usuários
   - Credenciais
   - Status

2. **roles**
   - Níveis de acesso
   - Descrições
   - Hierarquia

3. **permissions**
   - Permissões granulares
   - Escopo de acesso
   - Restrições

4. **user_roles**
   - Relacionamento usuário-papel
   - Datas de atribuição
   - Status

5. **audit_logs**
   - Registro de ações
   - Timestamps
   - Detalhes da operação

## API Endpoints

### Autenticação
- POST /api/auth/login
- POST /api/auth/logout
- POST /api/auth/refresh
- POST /api/auth/password/reset

### Usuários
- GET /api/users
- POST /api/users
- PUT /api/users/{id}
- DELETE /api/users/{id}

### Permissões
- GET /api/roles
- POST /api/roles
- PUT /api/roles/{id}
- GET /api/permissions
- POST /api/permissions

### Auditoria
- GET /api/audit/logs
- GET /api/audit/users/{id}
- GET /api/audit/reports 