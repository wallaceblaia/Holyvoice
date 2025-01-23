# Módulo de Monitoramento de Vídeos

## Visão Geral
O módulo de monitoramento do HolyVoice é responsável por gerenciar e acompanhar o processamento de vídeos do YouTube, permitindo tanto monitoramento contínuo de canais quanto processamento manual de vídeos específicos.

## Funcionalidades

### 1. Tipos de Monitoramento
- **Monitoramento Contínuo**
  - Verificação automática de novos vídeos
  - Intervalos configuráveis
  - Monitoramento de playlists específicas
  - Processamento automático

- **Monitoramento Manual**
  - Seleção individual de vídeos
  - Processamento sob demanda
  - Controle granular do conteúdo

### 2. Configurações de Intervalo
- 10 minutos
- 20 minutos
- 30 minutos
- 45 minutos
- 1 hora
- 2 horas
- 5 horas
- 12 horas
- 1 dia
- 2 dias
- 1 semana
- 1 mês

### 3. Status de Monitoramento
- **Não Configurado**
  - Monitoramento criado mas sem configurações
  - Aguardando setup inicial

- **Ativo**
  - Verificação periódica em execução
  - Processamento automático de novos vídeos

- **Pausado**
  - Verificações temporariamente suspensas
  - Mantém configurações salvas

- **Concluído**
  - Todos os vídeos processados
  - Apenas para monitoramento manual

- **Erro**
  - Falha na execução
  - Requer intervenção manual

### 4. Processamento de Vídeos
- Download do vídeo
- Extração do áudio
- Tradução do conteúdo
- Dublagem
- Upload do resultado
- Registro de progresso
- Tratamento de erros

## Interface do Usuário

### Telas Principais
1. **Lista de Monitoramentos**
   - Visão geral de todos os monitoramentos
   - Status atual
   - Progresso de processamento
   - Última verificação
   - Ações rápidas

2. **Detalhes do Monitoramento**
   - Configurações detalhadas
   - Lista de vídeos
   - Histórico de processamento
   - Controles de status

3. **Criação de Monitoramento**
   - Seleção de canal
   - Configuração de tipo
   - Definição de intervalos
   - Seleção de playlists

4. **Seleção de Vídeos**
   - Lista de vídeos recentes
   - Busca por URL
   - Visualização em grid
   - Seleção múltipla

## Sistema de Processamento

### Componentes
1. **Worker de Verificação**
   - Execução periódica
   - Verificação de novos vídeos
   - Atualização de status
   - Gerenciamento de fila

2. **Worker de Processamento**
   - Processamento assíncrono
   - Gestão de recursos
   - Tratamento de erros
   - Notificações de conclusão

### Estados de Processamento
- PENDING (Aguardando)
- PROCESSING (Em Processamento)
- COMPLETED (Concluído)
- ERROR (Erro)

## API Endpoints

### Monitoramento
- GET /api/v1/monitoring
- POST /api/v1/monitoring
- GET /api/v1/monitoring/{id}
- PUT /api/v1/monitoring/{id}
- DELETE /api/v1/monitoring/{id}

### Vídeos
- GET /api/v1/monitoring/{id}/videos
- POST /api/v1/monitoring/{id}/videos
- DELETE /api/v1/monitoring/{id}/videos/{video_id}

### Playlists
- GET /api/v1/youtube/channels/{id}/playlists
- POST /api/v1/monitoring/{id}/playlists
- DELETE /api/v1/monitoring/{id}/playlists/{playlist_id}

## Banco de Dados

### Tabelas Principais
1. **youtube_monitoring**
   - Configurações do monitoramento
   - Status
   - Intervalos
   - Métricas

2. **monitoring_videos**
   - Vídeos monitorados
   - Estado de processamento
   - Timestamps
   - Resultados

3. **monitoring_playlists**
   - Playlists monitoradas
   - Configurações específicas
   - Status de sincronização 