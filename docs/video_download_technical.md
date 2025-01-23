# Documentação Técnica - Módulo de Download de Vídeos

## Estrutura do Código

### 1. Schemas (`app/schemas/video.py`)
```python
class VideoCreate(BaseModel):
    url: HttpUrl
    title: str

class VideoDownloadRequest(BaseModel):
    url: HttpUrl
    monitoring_id: int

class VideoDownloadResponse(BaseModel):
    id: int
    url: str
    title: str
    download_progress: float
    project_path: str
    video_path: str
    source_path: Optional[str]
    metadata: VideoMetadata
    directories: ProjectDirectories
    download_status: DownloadStatus
```

### 2. Serviço (`app/services/video_download/service.py`)
```python
class VideoDownloadService:
    def __init__(self, db: Session):
        self.db = db
        self._progress_subscribers: Dict[int, WebSocket] = {}
        self._loop = asyncio.get_event_loop()

    async def download(self, url: str, monitoring_id: int) -> VideoDownloadResponse:
        # Inicia o download do vídeo
        pass

    def _progress_hook(self, monitoring_id: int, d: dict):
        # Atualiza o progresso do download
        pass

    async def _download_video(self, url: str, video: MonitoringVideo, opts: dict):
        # Realiza o download em background
        pass

    async def subscribe_to_progress(self, websocket: WebSocket, monitoring_id: int):
        # Gerencia inscrições WebSocket
        pass
```

### 3. Endpoints (`app/api/v1/endpoints/video_download.py`)
```python
@router.post("/videos", response_model=VideoDownloadResponse)
async def create_video(...)

@router.post("/download", response_model=VideoDownloadResponse)
async def download_video(...)

@router.websocket("/ws/{monitoring_id}")
async def websocket_endpoint(...)
```

## Fluxo de Dados

1. **Criação do Vídeo:**
   ```mermaid
   sequenceDiagram
       Client->>API: POST /videos
       API->>Database: Cria YoutubeVideo
       API->>Database: Cria MonitoringVideo
       API->>Client: Retorna VideoDownloadResponse
   ```

2. **Download do Vídeo:**
   ```mermaid
   sequenceDiagram
       Client->>API: POST /download
       API->>FileSystem: Cria estrutura de diretórios
       API->>Background: Inicia download com yt-dlp
       API->>Client: Retorna status inicial
       Background->>Database: Atualiza progresso
       Background->>WebSocket: Notifica progresso
       Background->>FileSystem: Salva vídeo
   ```

3. **Monitoramento do Progresso:**
   ```mermaid
   sequenceDiagram
       Client->>WebSocket: Conecta ws://.../ws/{id}
       WebSocket->>Client: Aceita conexão
       Background->>WebSocket: Envia progresso
       WebSocket->>Client: Notifica progresso
   ```

## Modelos de Banco de Dados

### MonitoringVideo
- `id`: Integer (PK)
- `monitoring_id`: Integer (FK)
- `video_id`: Integer (FK)
- `status`: VideoProcessingStatus
- `created_by`: Integer (FK)
- `download_progress`: Float
- `download_started_at`: DateTime
- `download_completed_at`: DateTime
- `source_path`: String

### YoutubeVideo
- `id`: Integer (PK)
- `channel_id`: Integer (FK)
- `video_id`: String
- `title`: String
- `published_at`: DateTime

## Dependências

- **FastAPI**: Framework web
- **SQLAlchemy**: ORM
- **yt-dlp**: Download de vídeos
- **WebSockets**: Comunicação em tempo real
- **Pydantic**: Validação de dados

## Configuração

1. **Ambiente Virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

2. **Variáveis de Ambiente:**
   ```env
   DATABASE_URL=postgresql://user:pass@localhost/db
   SECRET_KEY=your-secret-key
   ```

3. **Banco de Dados:**
   ```bash
   alembic upgrade head
   ```

## Testes

```bash
# Testes unitários
pytest tests/unit/test_video_download.py

# Testes de integração
pytest tests/integration/test_video_download.py
```

## Considerações de Segurança

1. **Autenticação:**
   - Requer token JWT válido
   - Verifica permissões do usuário

2. **Validação:**
   - Valida URLs do YouTube
   - Limita tamanho dos arquivos
   - Verifica extensões permitidas

3. **Recursos:**
   - Limita downloads simultâneos
   - Gerencia espaço em disco
   - Timeout para downloads longos

## Manutenção

1. **Logs:**
   - Erros de download
   - Progresso de downloads
   - Conexões WebSocket

2. **Limpeza:**
   - Downloads incompletos
   - Arquivos temporários
   - Conexões inativas

3. **Monitoramento:**
   - Uso de disco
   - Performance do banco
   - Conexões ativas 