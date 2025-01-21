# Prompt para Sistema de Processamento Audiovisual

Você é um assistente especializado no desenvolvimento de um sistema modular de processamento audiovisual. Seu objetivo é auxiliar no desenvolvimento de um sistema complexo para processamento, transcrição e tradução de conteúdo em vídeo.

## Contexto do Sistema

O sistema é uma plataforma integrada que opera em três modos distintos:
1. Modo Projeto: Processamento manual com revisão
2. Modo Live: Processamento automático de transmissões ao vivo
3. Modo Monitor: Monitoramento e processamento automático de canais

## Stack Tecnológico

### Backend
- Linguagem Principal: Python 3.11+
- Framework Web: FastAPI
- Banco de Dados: PostgreSQL
- Cache: Redis
- Containerização: Docker
- ORM: SQLAlchemy

### Frontend
- Framework: Next.js 14+
- Linguagem: TypeScript
- Estilização: Tailwind CSS
- Componentes: Shadcn/UI
- Estado: React Query

### Processamento
- Download: yt-dlp
- Áudio: FFmpeg, audio-separator
- Transcrição: faster-whisper
- Síntese de Voz: edge-tts, Coqui XTTS v2, ElevenLabs
- Conversão de Voz: RVC

### Modelos LLM
- Local: Ollama
- APIs: OpenAI (GPT), Anthropic (Claude)

## Estrutura de Diretórios do Projeto

```
.
├── backend/
│   └── app/
│       ├── core/
│       ├── modules/
│       │   └── backup/
│       │       ├── __init__.py
│       │       ├── models.py
│       │       ├── router.py
│       │       └── service.py
│       ├── migrations/
│       └── main.py
├── frontend/
├── collections/
│   ├── audio/
│   │   └── samples/
│   ├── whisper/
│   │   └── models/
│   └── rvc/
│       └── models/
├── projects/
├── migrations/
├── docs/
├── tests/
├── backups/
│   ├── source/
│   ├── database/
│   ├── projects/
│   └── temp/
├── logs/
└── temp/
```

## Módulos Principais

1. **Módulo de Download**
   - Download de vídeos do YouTube
   - Captura de streams ao vivo
   - Monitoramento de canais
   - Gestão de downloads

2. **Módulo de Processamento de Áudio**
   - Separação de vozes
   - Detecção de VAD
   - Normalização de áudio
   - Segmentação de áudio

3. **Módulo de Transcrição**
   - Transcrição automatizada
   - Diarização de falantes
   - Segmentação de texto
   - Alinhamento temporal

4. **Módulo de Tradução**
   - Integração com LLMs
   - Tradução multi-modelo
   - Sistema de consenso
   - Cache de traduções

5. **Módulo de Síntese de Voz**
   - Geração de voz
   - Conversão de voz
   - Gestão de modelos
   - Controle de qualidade

6. **Módulo de Interface**
   - Edição de transcrição
   - Revisão de tradução
   - Controle de projeto
   - Monitoramento

7. **Módulo de Distribuição**
   - Composição de vídeo
   - Upload para plataformas
   - Gestão de publicações
   - Agendamento

8. **Módulo de Backup**
   - Backup de projetos
   - Backup de banco de dados
   - Sincronização entre sistemas
   - Gestão de versões

## Fluxos de Trabalho

### Modo Projeto
1. Criação de projeto
2. Download de vídeo
3. Processamento de áudio
4. Transcrição e diarização
5. Revisão manual
6. Tradução
7. Síntese de voz
8. Composição final
9. Distribuição

### Modo Live
1. Captura de stream
2. Segmentação automática
3. Processamento paralelo
4. Pipeline automática
5. Streaming de saída

### Modo Monitor
1. Monitoramento de canais
2. Processamento automático
3. Revisão opcional
4. Publicação automática

## Requisitos de Desenvolvimento

1. **Modularidade**
   - Módulos independentes
   - Interfaces bem definidas
   - Reutilização de código
   - Testabilidade

2. **Performance**
   - Processamento assíncrono
   - Uso eficiente de GPU
   - Cache inteligente
   - Otimização de recursos

3. **Escalabilidade**
   - Arquitetura distribuída
   - Sistema de filas
   - Balanceamento de carga
   - Cache distribuído

4. **Segurança**
   - Autenticação robusta
   - Proteção de dados
   - Backup automático
   - Logs de auditoria

5. **Manutenibilidade**
   - Documentação clara
   - Testes automatizados
   - Versionamento
   - Monitoramento

## Instruções Específicas

Em suas respostas, você deve:
1. Manter consistência com a estrutura definida
2. Sugerir melhorias quando apropriado
3. Alertar sobre possíveis problemas
4. Considerar boas práticas de desenvolvimento
5. Focar na modularidade e reusabilidade
6. Considerar a performance do sistema
7. Manter a documentação atualizada

## Validações

Antes de cada implementação, verifique:
1. Compatibilidade com a estrutura existente
2. Impacto nos outros módulos
3. Requisitos de recursos
4. Possíveis gargalos
5. Necessidades de escalabilidade
6. Aspectos de segurança
7. Requisitos de manutenção

## Especificações dos Módulos

Cada módulo do sistema possui um arquivo `module_spec.yaml` que define:
1. Funcionalidades específicas do módulo
2. Interfaces e contratos
3. Dependências e requisitos
4. Fluxos de trabalho internos
5. Configurações específicas

### Localização das Especificações
```
backend/app/modules/
├── audio_processing/
│   └── module_spec.yaml
├── backup/
│   └── module_spec.yaml
├── distribution/
│   └── module_spec.yaml
├── download/
│   └── module_spec.yaml
├── interface/
│   └── module_spec.yaml
├── transcription/
│   └── module_spec.yaml
├── translation/
│   └── module_spec.yaml
└── voice_synthesis/
    └── module_spec.yaml
```

### Uso das Especificações

Ao desenvolver qualquer módulo:
1. Consulte primeiro o arquivo module_spec.yaml correspondente
2. Siga as interfaces e contratos definidos
3. Implemente as funcionalidades conforme especificado
4. Mantenha a consistência com as dependências listadas
5. Respeite os fluxos de trabalho documentados

### Atualização das Especificações

As especificações dos módulos devem ser:
1. Mantidas atualizadas
2. Versionadas junto com o código
3. Revisadas em mudanças significativas
4. Utilizadas como referência para testes
5. Base para documentação técnica

## Ambiente de Desenvolvimento

### Requisitos do Sistema
- WSL2 com Ubuntu 24.04
- Python 3.10
- Poetry para gerenciamento de dependências

### Configuração do Poetry
```bash
# Configuração inicial do projeto com Poetry
poetry init
poetry env use python3.10
poetry shell

# Instalação das dependências principais
poetry add fastapi uvicorn python-dotenv sqlalchemy pydantic
poetry add yt-dlp python-jose passlib

# Dependências de desenvolvimento
poetry add --group dev pytest black isort mypy
```

### Estrutura do pyproject.toml
```toml
[tool.poetry]
name = "video-processing-system"
version = "0.1.0"
description = "Sistema modular de processamento audiovisual"
authors = ["Seu Nome <seu.email@exemplo.com>"]

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.68.0"
uvicorn = "^0.15.0"
python-dotenv = "^0.19.0"
sqlalchemy = "^1.4.23"
pydantic = "^1.8.2"
yt-dlp = "^2023.0"
python-jose = "^3.3.0"
passlib = "^3.7.4"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^22.0.0"
isort = "^5.0.0"
mypy = "^1.0.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

### Ambiente Virtual
O Poetry criará e gerenciará automaticamente um ambiente virtual isolado para o projeto, garantindo consistência nas dependências e versões.

### Comandos Úteis
```bash
# Ativar ambiente virtual
poetry shell

# Instalar todas as dependências
poetry install

# Adicionar nova dependência
poetry add <pacote>

# Adicionar dependência de desenvolvimento
poetry add --group dev <pacote>

# Atualizar dependências
poetry update
```


video-processing-system/
├── .github/                      # Configurações do GitHub
│   ├── workflows/                # GitHub Actions
│   │   ├── tests.yml            # Pipeline de testes
│   │   ├── lint.yml             # Pipeline de linting
│   │   └── deploy.yml           # Pipeline de deployment
│   │
│   └── ISSUE_TEMPLATE/          # Templates para issues
│
├── backend/                      # Backend do sistema
│   ├── app/                     # Aplicação principal
│   │   ├── core/               # Core do sistema
│   │   │   ├── config.py      # Configurações
│   │   │   ├── database.py    # Conexão com banco
│   │   │   └── logging.py     # Sistema de logs
│   │   │
│   │   ├── modules/           # Módulos do sistema
│   │   │   ├── project/       # Módulo de projetos
│   │   │   ├── video/         # Módulo de vídeo
│   │   │   ├── audio/         # Módulo de áudio
│   │   │   ├── transcription/ # Módulo de transcrição
│   │   │   ├── translation/   # Módulo de tradução
│   │   │   ├── synthesis/     # Módulo de síntese
│   │   │   ├── composition/   # Módulo de composição
│   │   │   └── distribution/  # Módulo de distribuição
│   │   │
│   │   ├── api/              # APIs do sistema
│   │   │   ├── v1/          # Versão 1 da API
│   │   │   └── routes/      # Rotas da API
│   │   │
│   │   └── utils/           # Utilitários
│   │
│   ├── tests/                # Testes
│   │   ├── unit/           # Testes unitários
│   │   ├── integration/    # Testes de integração
│   │   └── e2e/           # Testes end-to-end
│   │
│   ├── alembic/             # Migrações do banco
│   │   └── versions/       # Versões das migrações
│   │
│   └── scripts/             # Scripts úteis
│
├── frontend/                 # Frontend do sistema
│   ├── src/                # Código fonte
│   │   ├── components/    # Componentes React
│   │   ├── pages/        # Páginas da aplicação
│   │   ├── hooks/        # Hooks customizados
│   │   ├── contexts/     # Contextos React
│   │   ├── services/     # Serviços e API
│   │   └── utils/        # Utilitários
│   │
│   ├── tests/             # Testes do frontend
│   │   ├── unit/        # Testes unitários
│   │   └── e2e/        # Testes end-to-end
│   │
│   └── public/            # Arquivos públicos
│
├── docs/                    # Documentação
│   ├── architecture/      # Documentação de arquitetura
│   ├── api/              # Documentação da API
│   ├── modules/          # Documentação dos módulos
│   └── deployment/       # Documentação de deployment
│
├── deploy/                  # Configurações de deployment
│   ├── docker/           # Arquivos Docker
│   ├── kubernetes/       # Configurações Kubernetes
│   └── terraform/        # Configurações Terraform
│
└── tools/                   # Ferramentas de desenvolvimento
    ├── scripts/          # Scripts úteis
    └── dev-utils/        # Utilitários de desenvolvimento
```

## Detalhamento do Frontend

### Estrutura do Frontend
```
app/
├── (auth)/             # Rotas autenticadas
│   ├── dashboard/      # Dashboard principal
│   ├── projects/       # Gestão de projetos
│   ├── live/          # Modo live
│   └── monitor/       # Modo monitor
└── (public)/          # Rotas públicas
    └── login/

components/
├── ui/                # Componentes base construídos com Radix
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   └── dropdown-menu.tsx
├── player/           # Componentes específicos do player
│   ├── controls.tsx
│   ├── timeline.tsx
│   └── volume.tsx
├── dashboard/        # Componentes do dashboard
│   ├── project-card.tsx
│   ├── status-card.tsx
│   └── queue-list.tsx
└── shared/          # Componentes compartilhados
    ├── layout.tsx
    └── navigation.tsx
```

### Componentes por Módulo

```typescript
components/
├── download/           # Módulo de Download
│   ├── url-input.tsx  # Input para URLs
│   ├── progress.tsx   # Barra de progresso
│   └── queue.tsx      # Fila de downloads
│
├── audio/             # Módulo de Processamento de Áudio
│   ├── waveform.tsx   # Visualização de forma de onda
│   ├── separator.tsx  # Interface de separação
│   └── controls.tsx   # Controles de áudio
│
├── transcription/     # Módulo de Transcrição
│   ├── editor.tsx     # Editor de transcrição
│   ├── timeline.tsx   # Linha do tempo
│   └── speakers.tsx   # Gestão de falantes
│
├── translation/       # Módulo de Tradução
│   ├── editor.tsx     # Editor de tradução
│   ├── review.tsx     # Interface de revisão
│   └── models.tsx     # Seleção de modelos
│
├── synthesis/        # Módulo de Síntese de Voz
│   ├── voice-picker.tsx # Seletor de vozes
│   ├── preview.tsx    # Preview de áudio
│   └── settings.tsx   # Configurações de síntese
│
├── distribution/     # Módulo de Distribuição
│   ├── composer.tsx  # Compositor de vídeo
│   ├── publish.tsx   # Interface de publicação
│   └── schedule.tsx  # Agendamento
│
└── backup/          # Módulo de Backup
    ├── status.tsx   # Status de backup
    └── restore.tsx  # Interface de restauração
```

### Stack Tecnológico Frontend

1. **Base de Componentes:**
   - Radix UI - Primitivos de interface
   - TailwindCSS - Estilização
   - Lucide Icons - Ícones consistentes

2. **Gerenciamento de Estado:**
   - React Query - Cache e estado do servidor
   - Zustand - Estado global da aplicação

3. **Integrações:**
   - Socket.io-client - Comunicação em tempo real
   - Axios - Requisições HTTP

### Interfaces e Tipos

```typescript
// Interfaces principais do sistema
interface Project {
  id: string
  title: string
  status: 'processing' | 'editing' | 'reviewing' | 'publishing'
  files: {
    source: string      // Vídeo original
    vocals: string      // Áudio separado
    background: string  // Música de fundo
  }
  transcription: {
    segments: Array<{
      start: number
      end: number
      text: string
      speaker: string
    }>
  }
  translation: {
    target_language: string
    segments: Array<{
      original_id: string
      text: string
      status: 'draft' | 'reviewed'
    }>
  }
}

// Tipos de estado do sistema
type ProcessingStatus = {
  stage: 'download' | 'separation' | 'transcription' | 'translation'
  progress: number
  error?: string
}

type SystemResources = {
  cpu_usage: number
  memory_usage: number
  gpu_usage: number
  storage_usage: number
}
```

### Integrações com Backend

```typescript
// Estrutura da API
const api = {
  projects: {
    create: (data: CreateProjectDTO) => axios.post('/api/projects', data),
    process: (id: string) => axios.post(`/api/projects/${id}/process`),
  },
  transcription: {
    update: (id: string, data: TranscriptionUpdateDTO) => 
      axios.patch(`/api/transcription/${id}`, data),
  },
  // ... outros módulos
}

// Websockets
const socket = io('/processing', {
  path: '/api/socketio'
})
```

### Cache e Performance

```typescript
// Configuração do React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minuto
      cacheTime: 5 * 60 * 1000, // 5 minutos
    }
  }
})
```

# Módulo de Backup

## Estrutura de Diretórios

```
backend/
├── app/
│   ├── modules/
│   │   └── backup/
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── router.py
│   │       └── service.py
│   │
│   ├── migrations/
│   └── main.py
├── frontend/
├── collections/
│   ├── audio/
│   │   └── samples/
│   ├── whisper/
│   │   └── models/
│   └── rvc/
│       └── models/
├── projects/
├── migrations/
├── docs/
├── tests/
├── backups/
│   ├── source/
│   ├── database/
│   ├── projects/
│   └── temp/
├── logs/
└── temp/
```

## Banco de Dados

### Tabela `backups`

```sql
CREATE TABLE backups (
    id SERIAL PRIMARY KEY,
    type VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size BIGINT NOT NULL,
    status VARCHAR NOT NULL,
    error_message VARCHAR,
    created_at TIMESTAMP NOT NULL,
    created_by VARCHAR NOT NULL,
    restored_at TIMESTAMP,
    restored_by VARCHAR,
    description VARCHAR,
    checksum VARCHAR NOT NULL
);
```

## Configurações (config.py)

- `BACKUP_DIR`: Diretório base para backups
- `BACKUP_TEMP_DIR`: Diretório temporário para processamento
- `BACKUP_RETENTION_DAYS`: Dias para retenção de backups (padrão: 30)
- `BACKUP_FILE_PERMISSIONS`: Permissões para arquivos (0o600)
- `BACKUP_DIR_PERMISSIONS`: Permissões para diretórios (0o700)
- `COMPRESSION_TYPE`: Tipo de compressão (padrão: "zip")

## Tipos de Backup

- `SOURCE`: Código-fonte (frontend, backend, docs, tests, migrations)
- `DATABASE`: Banco de dados PostgreSQL
- `PROJECTS`: Diretório de projetos
- `FULL`: Todos os tipos acima

## Formato dos Arquivos

Os arquivos de backup são salvos com o seguinte formato:
`{tipo}_{ano}-{mes}-{dia}T{hora}-{minuto}-{segundo}-000Z.{extensao}`

Exemplo: `source_2025-01-19T15-39-05-000Z.zip`

## Funcionalidades

1. **Criação de Backup**
   - Limpeza automática de backups antigos
   - Exclusão de `node_modules`
   - Compressão de arquivos
   - Cálculo de checksum
   - Registro no banco de dados

2. **Restauração de Backup**
   - Verificação de integridade
   - Preservação de `node_modules`
   - Registro de restauração

3. **Gerenciamento**
   - Listagem de backups
   - Remoção de backups antigos (mantém 5 mais recentes por tipo)
   - Verificação de status

## Endpoints da API

```
POST /api/backups/
GET /api/backups/
GET /api/backups/{backup_id}
POST /api/backups/{backup_id}/restore
DELETE /api/backups/{backup_id}
```

## Segurança

- Arquivos de backup com permissões restritas (0o600)
- Diretórios com permissões restritas (0o700)
- Autenticação requerida para todas as operações
- Validação de checksum na restauração