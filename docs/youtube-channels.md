# Módulo de Canais do YouTube

## Visão Geral
O módulo de Canais do YouTube permite gerenciar canais do YouTube, visualizar informações detalhadas, vídeos recentes e controlar permissões de acesso. O módulo utiliza a API oficial do YouTube para obter dados em tempo real.

## Estrutura do Banco de Dados

### Tabela: youtube_channel
| Campo           | Tipo                     | Descrição                                    |
|----------------|--------------------------|----------------------------------------------|
| id             | SERIAL PRIMARY KEY       | Identificador único do canal                 |
| channel_url    | VARCHAR NOT NULL         | URL do canal no YouTube                      |
| youtube_id     | VARCHAR NOT NULL UNIQUE  | ID único do canal no YouTube                 |
| channel_name   | VARCHAR NOT NULL         | Nome do canal                                |
| description    | TEXT                     | Descrição do canal                           |
| banner_image   | VARCHAR                  | URL da imagem do banner                      |
| avatar_image   | VARCHAR                  | URL da imagem do avatar                      |
| subscriber_count| INTEGER                 | Número de inscritos                          |
| video_count    | INTEGER                  | Número total de vídeos                       |
| view_count     | INTEGER                  | Número total de visualizações                |
| api_key        | VARCHAR NOT NULL         | Chave de API do YouTube (criptografada)      |
| created_by     | INTEGER NOT NULL         | ID do usuário que criou o registro           |
| updated_by     | INTEGER                  | ID do usuário que atualizou o registro       |
| created_at     | TIMESTAMP WITH TIMEZONE  | Data de criação                              |
| updated_at     | TIMESTAMP WITH TIMEZONE  | Data da última atualização                   |
| last_sync_at   | TIMESTAMP WITH TIMEZONE  | Data da última sincronização com o YouTube   |

### Tabela: youtube_channel_access
| Campo       | Tipo                    | Descrição                                    |
|------------|-------------------------|----------------------------------------------|
| id         | SERIAL PRIMARY KEY      | Identificador único do acesso                |
| channel_id | INTEGER NOT NULL        | ID do canal (referência)                     |
| user_id    | INTEGER NOT NULL        | ID do usuário (referência)                   |
| can_view   | BOOLEAN DEFAULT true    | Permissão para visualizar                    |
| can_edit   | BOOLEAN DEFAULT false   | Permissão para editar                        |
| can_delete | BOOLEAN DEFAULT false   | Permissão para deletar                       |
| created_by | INTEGER NOT NULL        | ID do usuário que concedeu o acesso          |
| created_at | TIMESTAMP WITH TIMEZONE | Data de criação do acesso                    |

## Endpoints da API

### POST /api/v1/youtube/channels
Cria um novo canal do YouTube.
- **Corpo da requisição**: `YoutubeChannelCreate`
  ```typescript
  {
    channel_url: string;  // URL do canal
    api_key: string;     // Chave de API do YouTube
  }
  ```
- **Resposta**: `YoutubeChannel`

### GET /api/v1/youtube/channels
Lista os canais do YouTube.
- **Parâmetros**: 
  - skip (opcional): número de registros para pular
  - limit (opcional): número máximo de registros
- **Resposta**: Array de `YoutubeChannel`

### GET /api/v1/youtube/channels/{channel_id}
Obtém detalhes de um canal específico.
- **Parâmetros**: channel_id (path)
- **Resposta**: `YoutubeChannelWithVideos`

### PUT /api/v1/youtube/channels/{channel_id}
Atualiza um canal existente.
- **Parâmetros**: channel_id (path)
- **Corpo**: `YoutubeChannelUpdate`
- **Resposta**: `YoutubeChannel`

### DELETE /api/v1/youtube/channels/{channel_id}
Remove um canal.
- **Parâmetros**: channel_id (path)
- **Resposta**: Mensagem de sucesso

## Interface do Usuário

### Cores e Estilos
- **Cores Principais**:
  - Texto Principal: `text-foreground`
  - Texto Secundário: `text-muted-foreground`
  - Fundo: `bg-background`
  - Borda: `border-border`
  - Destaque: `bg-primary`

- **Componentes UI**:
  - Cards: `@/components/ui/card`
  - Diálogos: `@/components/ui/dialog`
  - Botões: `@/components/ui/button`
  - Toast: `@/components/ui/use-toast`

### Páginas

#### Lista de Canais (/dashboard/youtube/channels)
- Grid responsivo de cards
- Informações exibidas:
  - Nome do canal
  - Thumbnail
  - Data de criação
  - Status (ao vivo)

#### Detalhes do Canal (/dashboard/youtube/channels/[id])
- Banner do canal (altura: 48 - `h-48`)
- Avatar (dimensões: 24x24 - `h-24 w-24`)
- Informações do canal:
  - Nome
  - Número de inscritos
  - Total de vídeos
  - Total de visualizações
  - Descrição
- Grid de vídeos recentes:
  - 3 colunas em desktop (`lg:grid-cols-3`)
  - 2 colunas em tablet (`md:grid-cols-2`)
  - 1 coluna em mobile
  - Altura das thumbnails: 48 (`h-48`)

### Componentes

#### Card de Vídeo
```typescript
interface Video {
  id: string;
  title: string;
  thumbnail_url: string;
  published_at: string;
  is_live: boolean;
}
```
- Efeitos:
  - Hover: sombra (`hover:shadow-lg`)
  - Transição suave (`transition-shadow`)
  - Overlay escuro no hover (`bg-opacity-0 group-hover:bg-opacity-50`)
  - Ícone do YouTube aparece no hover

#### Modal de Vídeo
- Largura máxima: 800px (`sm:max-w-[800px]`)
- Proporção de aspecto 16:9 (`aspect-video`)
- Player do YouTube incorporado
- Título com limite de 2 linhas (`line-clamp-2`)

## Segurança
- Autenticação via token JWT
- Criptografia da API key usando Fernet
- Controle granular de permissões por usuário
- Validação de URLs do YouTube
- Validação de formato da API key

## Cache
- Cache de informações do canal: 1 hora
- Cache de vídeos recentes: 15 minutos
- Cache de playlists: 6 horas
- Implementado com Redis

## Dependências
```json
{
  "date-fns": "^2.30.0",
  "lucide-react": "^0.294.0",
  "next": "14.0.3",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "tailwindcss": "^3.3.0",
  "shadcn/ui": "latest"
}
```

## Considerações de Performance
- Lazy loading de imagens
- Paginação de resultados
- Cache de respostas da API
- Otimização de consultas ao banco
- Índices nas colunas mais consultadas 