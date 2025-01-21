# Documentação do HolyVoice

## Visão Geral
O HolyVoice é uma plataforma de gerenciamento de músicas para igrejas, oferecendo funcionalidades de autenticação, gerenciamento de usuários, e processamento de áudio.

## Estrutura da Documentação

### Módulos
- [Autenticação](auth/authentication.md)
  - Sistema completo de login e registro
  - Controle de acesso baseado em papéis
  - Segurança e validações

### Tecnologias Principais

#### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT
- Bcrypt

#### Frontend
- Next.js
- Tailwind CSS
- Shadcn/ui
- React Hook Form
- Zod

## Configuração do Ambiente

### Requisitos
- Python 3.12+
- Node.js 18+
- PostgreSQL 16+

### Instalação
1. Clone o repositório
2. Configure o ambiente virtual Python
3. Instale as dependências do backend
4. Instale as dependências do frontend
5. Configure as variáveis de ambiente
6. Inicialize o banco de dados
7. Inicie os servidores

### Estrutura de Diretórios
```
holyvoice/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── crud/
│   │   ├── db/
│   │   ├── models/
│   │   └── schemas/
│   └── tests/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
└── docs/
    ├── auth/
    └── README.md
```

## Contribuição
- Siga as diretrizes de código
- Documente novas funcionalidades
- Mantenha os testes atualizados
- Use commits semânticos