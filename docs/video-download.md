# Módulo de Download de Vídeos

## Visão Geral
O módulo de download de vídeos é responsável por gerenciar todo o processo de obtenção de vídeos, seja do YouTube ou de fontes locais, criando a estrutura de diretórios necessária e mantendo registro detalhado de todas as informações relacionadas ao vídeo.

## Funcionalidades

### 1. Gerenciamento de Downloads
- **Download de Vídeos**
  - Suporte a URLs do YouTube
  - Suporte a arquivos locais
  - Monitoramento em tempo real do progresso
  - Padronização do arquivo final (mainvideo.mp4)

- **Estrutura de Diretórios**
  - Criação automática de diretórios do projeto
  - Organização padronizada de arquivos
  - Gestão de permissões de acesso

### 2. Estrutura de Diretórios do Projeto
- **source/**
  - mainvideo.mp4 (vídeo original)
  - metadados e informações do vídeo
- **audios/**
  - arquivos de áudio extraídos
  - faixas de áudio processadas
- **videos/**
  - versões processadas do vídeo
  - renders intermediários
- **docs/**
  - documentação do projeto
  - logs de processamento
- **legendas/**
  - arquivos de legenda
  - transcrições
- **assets/**
  - recursos adicionais
  - elementos gráficos
- **imagens/**
  - thumbnails
  - frames extraídos
- **voices/**
  - arquivos de voz processados
  - dublagens
- **lives/**
  - streams ao vivo
  - transmissões

### 3. Informações Armazenadas
- **Metadados do Vídeo**
  - Título
  - Descrição
  - Data de publicação
  - Número de visualizações
  - Duração
  - Qualidade do vídeo
  - Canal de origem
  - Tags
  - Categoria
  - Idioma original

- **Informações de Processamento**
  - ID do monitoramento
  - Status atual (step)
  - Timestamps de processamento
  - Caminhos dos arquivos
  - Logs de execução

### 4. Steps de Processamento
1. **Download** (atual módulo)
   - Download do vídeo
   - Extração de metadados
   - Criação da estrutura
2. Separação de áudio
3. Transcrição
4. Ajuste de transcrição
5. Tradução
6. Ajuste de tradução
7. Conversão de voz
8. Geração de áudio
9. Renderização de vídeo
10. Distribuição

## Interface Técnica

### API Endpoints

#### Download
- POST /api/v1/videos/download
  - **Requisição:**
    ```json
    {
      "url": "string",          // URL do vídeo no YouTube
      "monitoring_id": integer  // ID do monitoramento
    }
    ```
  - **Resposta:**
    ```json
    {
      "project_path": "string",      // Caminho completo do projeto criado
      "video_path": "string",        // Caminho do arquivo mainvideo.mp4
      "metadata": {
        "title": "string",
        "description": "string",
        "view_count": integer,
        "published_at": "datetime",
        "duration": integer,
        "video_quality": "string",
        "channel_title": "string",
        "tags": ["string"],
        "category": "string",
        "original_language": "string"
      },
      "directories": {              // Estrutura de diretórios criada
        "source": "string",
        "audios": "string",
        "videos": "string",
        "docs": "string",
        "legendas": "string",
        "assets": "string",
        "imagens": "string",
        "voices": "string",
        "lives": "string"
      },
      "download_status": {
        "step": "Downloading",      // Downloading -> Downloaded
        "progress": float,          // 0 a 100
        "started_at": "datetime",
        "completed_at": "datetime"  // null até completar
      }
    }
    ```

#### Websocket
- ws://api/v1/videos/{monitoring_id}/progress
  - **Eventos de Progresso:**
    ```json
    {
      "monitoring_id": integer,
      "step": "Downloading",
      "progress": float,          // 0 a 100
      "speed": "string",         // Velocidade do download
      "eta": "string",          // Tempo estimado
      "downloaded_bytes": integer,
      "total_bytes": integer
    }
    ```
  - **Evento de Conclusão:**
    ```json
    {
      "monitoring_id": integer,
      "step": "Downloaded",
      "completed_at": "datetime",
      "video_path": "string",
      "total_size": "string"
    }
    ```

### Integração yt-dlp
- Configuração personalizada
- Captura de eventos de progresso
- Gestão de qualidade do vídeo
- Tratamento de erros

## Banco de Dados

### Tabela: monitoring_videos
```sql
ALTER TABLE monitoring_videos ADD COLUMN (
    title TEXT,
    description TEXT,
    view_count INTEGER,
    published_at TIMESTAMP,
    duration INTEGER,
    video_quality TEXT,
    channel_title TEXT,
    tags TEXT[],
    category TEXT,
    original_language TEXT,
    source_path TEXT,
    step VARCHAR(20),           -- Alterado para VARCHAR com valores específicos
    download_progress FLOAT,    -- Progresso do download (0-100)
    download_started_at TIMESTAMP,
    download_completed_at TIMESTAMP,
    project_path TEXT,          -- Caminho base do projeto
    error_message TEXT
);

-- Remover enum anterior e definir valores válidos para step
ALTER TABLE monitoring_videos
    ADD CONSTRAINT valid_step CHECK (
        step IN ('Downloading', 'Downloaded', 'Processing', 'Completed', 'Error')
    );
```

### Variáveis de Ambiente
```env
# Diretório base para projetos
PROJECTS_ROOT_DIR=/path/to/projects

# Configurações yt-dlp
YTDLP_FORMAT="bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
YTDLP_MAX_FILESIZE="10G"
YTDLP_RATE_LIMIT="10M"
YTDLP_OUTPUT_TEMPLATE="source/mainvideo.mp4"  # Template fixo para saída

# Websocket
WS_MAX_CONNECTIONS=100
WS_HEARTBEAT_INTERVAL=30
```

### Dependências
- yt-dlp
- FFmpeg
- Python 3.8+
- PostgreSQL 12+
- Redis (para filas e cache) 