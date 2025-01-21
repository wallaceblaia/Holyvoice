# Documentação do Módulo de Autenticação

## Visão Geral
O módulo de autenticação do HolyVoice fornece funcionalidades completas de registro e login de usuários, utilizando JWT (JSON Web Tokens) para autenticação e controle de acesso.

## Backend

### Tecnologias Utilizadas
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Banco de Dados**: PostgreSQL
- **Autenticação**: JWT (JSON Web Tokens)
- **Criptografia**: Bcrypt

### Dependências Principais
```txt
fastapi>=0.110.0
uvicorn>=0.27.1
sqlalchemy>=2.0.27
pydantic>=2.6.1
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
email-validator>=2.1.0.post1
psycopg2-binary>=2.9.9
python-dotenv>=1.0.1
```

### Estrutura do Banco de Dados

#### Tabela: user
| Campo           | Tipo      | Descrição                                |
|----------------|-----------|------------------------------------------|
| id             | Integer   | ID único do usuário (Primary Key)        |
| name           | String    | Nome completo do usuário                 |
| email          | String    | Email do usuário (Único)                 |
| hashed_password| String    | Senha criptografada                      |
| is_active      | Boolean   | Status de ativação da conta              |
| is_superuser   | Boolean   | Indica se é um administrador             |
| created_at     | DateTime  | Data de criação da conta                 |
| updated_at     | DateTime  | Data da última atualização               |
| last_login     | DateTime  | Data do último login                     |
| avatar         | String    | URL do avatar do usuário (opcional)      |

### Endpoints da API

#### Registro de Usuário
- **URL**: `/api/v1/auth/register`
- **Método**: POST
- **Campos**:
  - email (string, obrigatório)
  - password (string, obrigatório)
  - confirm_password (string, obrigatório)
  - name (string, obrigatório)
  - is_superuser (boolean, opcional)

#### Login
- **URL**: `/api/v1/auth/login`
- **Método**: POST
- **Campos**:
  - username (string, email do usuário)
  - password (string)
- **Retorno**: Token JWT e dados do usuário

#### Obter Dados do Usuário
- **URL**: `/api/v1/users/me`
- **Método**: GET
- **Headers**: Authorization: Bearer {token}
- **Retorno**: Dados completos do usuário

#### Atualizar Avatar
- **URL**: `/api/v1/users/me`
- **Método**: PATCH
- **Headers**: 
  - Authorization: Bearer {token}
  - Content-Type: text/plain
- **Body**: URL do avatar (string)
- **Retorno**: Dados atualizados do usuário

### Validações
- Email único no sistema
- Senha e confirmação de senha devem coincidir
- Email deve ser válido
- Senha deve ser segura (mínimo 8 caracteres)
- URL do avatar deve ser válida (se fornecida)

### Segurança
- Senhas são hasheadas usando bcrypt
- Tokens JWT com expiração configurável
- Proteção contra força bruta
- CORS configurado para permitir apenas origens específicas
- Registro automático de último login

## Frontend

### Tecnologias Utilizadas
- **Framework**: Next.js 14
- **UI Components**: Shadcn/ui
- **Formulários**: React Hook Form
- **Validação**: Zod
- **Estilização**: Tailwind CSS
- **Gerenciamento de Estado**: Zustand
- **Diálogos**: HeadlessUI

### Temas e Estilos
- Tema escuro por padrão
- Cores principais:
  - Background: bg-background
  - Texto: text-foreground
  - Primária: primary
  - Secundária: secondary
  - Destaque: accent
  - Bordas: border

### Componentes Principais
- UserAuthForm: Formulário de autenticação reutilizável
- Button: Botão estilizado com variantes
- Input: Campo de entrada com validação
- Form: Componente de formulário com validação integrada
- Avatar: Componente de exibição de avatar
- AvatarSelector: Seletor de avatar com cores profissionais
- UserNav: Navegação do usuário com menu dropdown

### Sistema de Avatares
- Geração dinâmica via UI Avatars API
- 12 esquemas de cores profissionais
- Avatares baseados nas iniciais do usuário
- Cores disponíveis:
  - Azul profundo
  - Azul corporativo
  - Azul marinho
  - Azul acinzentado
  - Cinza elegante
  - Marrom executivo
  - Roxo sofisticado
  - Roxo acinzentado
  - Verde musgo
  - Azul noturno
  - Vermelho vinho
  - Preto elegante

### Validações no Frontend
- Email válido
- Senha com mínimo de 8 caracteres
- Confirmação de senha
- Nome obrigatório
- URL do avatar válida

## Configuração

### Variáveis de Ambiente (.env)
```env
PROJECT_NAME=HolyVoice
VERSION=0.1.0
API_V1_STR=/api/v1
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=holyvoice
```

### Inicialização do Banco de Dados
```bash
python init_db.py
```

### Execução do Backend
```bash
uvicorn app.main:app --reload
```

### Execução do Frontend
```bash
npm run dev
```

## Fluxo de Autenticação

1. **Registro**:
   - Usuário preenche formulário de registro
   - Frontend valida dados
   - Backend verifica email único
   - Senha é hasheada
   - Usuário é criado no banco
   - Avatar padrão é gerado com iniciais

2. **Login**:
   - Usuário fornece credenciais
   - Backend verifica credenciais
   - Data do último login é atualizada
   - Token JWT é gerado
   - Frontend armazena token
   - Usuário é redirecionado

3. **Atualização de Avatar**:
   - Usuário clica em "Alterar Avatar"
   - Modal exibe opções de avatares com iniciais
   - Usuário seleciona novo avatar
   - Frontend envia URL via PATCH
   - Backend atualiza avatar
   - Interface atualiza automaticamente

4. **Proteção de Rotas**:
   - Frontend verifica token
   - Backend valida token em requisições
   - Rotas protegidas verificam permissões
   - Tipo de usuário (admin/normal) é verificado

## Considerações de Segurança

- Todas as senhas são hasheadas antes de armazenamento
- Tokens JWT têm tempo de expiração
- CORS configurado para segurança
- Validações tanto no frontend quanto no backend
- Proteção contra injeção SQL via ORM
- Logs de tentativas de login
- Sanitização de URLs de avatar 