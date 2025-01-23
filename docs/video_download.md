# Módulo de Download de Vídeos

## Visão Geral
O módulo de download de vídeos é responsável por gerenciar o download de vídeos do YouTube, fornecendo atualizações em tempo real do progresso através de WebSocket e organizando os arquivos em uma estrutura de diretórios padronizada.

## Endpoints da API

### 1. Criar Novo Vídeo
```http
POST /api/v1/videos/videos
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "title": "Título do Vídeo"
}
```

**Response:**
```json
{
    "id": 1,
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "title": "Título do Vídeo",
    "download_progress": 0.0,
    "project_path": "downloads/1",
    "video_path": "downloads/1/source/video.mp4",
    "source_path": null,
    "metadata": {
        "title": "Título do Vídeo",
        "duration": null,
        "view_count": null,
        "like_count": null,
        "comment_count": null,
        "description": null
    },
    "directories": {
        "source": "downloads/1/source",
        "audios": "downloads/1/audios",
        "videos": "downloads/1/videos",
        "docs": "downloads/1/docs",
        "legendas": "downloads/1/legendas",
        "assets": "downloads/1/assets",
        "imagens": "downloads/1/imagens",
        "voices": "downloads/1/voices",
        "lives": "downloads/1/lives"
    },
    "download_status": "pending"
}
```

### 2. Iniciar Download
```http
POST /api/v1/videos/download
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {token}
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "monitoring_id": 1
}
```

**Response:** Similar ao endpoint anterior, mas com `download_status: "downloading"`.

### 3. WebSocket para Progresso
```
ws://localhost:8000/api/v1/videos/ws/{monitoring_id}
```

**Mensagens WebSocket:**
```json
{
    "progress": 45.5,
    "error": null
}
```

## Estrutura de Diretórios
Cada vídeo é organizado na seguinte estrutura:
```
downloads/
└── {monitoring_id}/
    ├── source/      # Vídeo original
    ├── audios/      # Arquivos de áudio extraídos
    ├── videos/      # Vídeos processados
    ├── docs/        # Documentação
    ├── legendas/    # Arquivos de legenda
    ├── assets/      # Recursos diversos
    ├── imagens/     # Imagens extraídas
    ├── voices/      # Vozes isoladas
    └── lives/       # Streams ao vivo
```

## Interface de Monitoramento
Para monitorar o progresso do download, use o arquivo `progress.html`:

1. Abra o arquivo no navegador
2. Conecta automaticamente ao WebSocket
3. Mostra:
   - Título do vídeo
   - Barra de progresso
   - Status atual
   - Porcentagem de conclusão

## Exemplo de Uso

1. Criar um novo vídeo:
```bash
curl -X POST "http://localhost:8000/api/v1/videos/videos" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer {token}" \
-d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "title": "Meu Vídeo"
}'
```

2. Iniciar o download:
```bash
curl -X POST "http://localhost:8000/api/v1/videos/download" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer {token}" \
-d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "monitoring_id": ID_RETORNADO
}'
```

3. Monitorar o progresso:
- Abra `progress.html` no navegador
- Ou conecte ao WebSocket usando uma ferramenta como `wscat`:
```bash
wscat -c "ws://localhost:8000/api/v1/videos/ws/ID_RETORNADO"
```

## Notas Técnicas

- Utiliza `yt-dlp` para download dos vídeos
- Suporta downloads em background
- Atualiza o banco de dados em tempo real
- Notifica progresso via WebSocket
- Cria estrutura de diretórios automaticamente
- Gerencia metadados do vídeo
- Suporta múltiplos downloads simultâneos 