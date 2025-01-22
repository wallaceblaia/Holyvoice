"use client"

import * as React from "react"
import { useEffect, useState } from "react"
import { useToast } from "@/components/ui/use-toast"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Play, Pause, Trash2, Plus, Youtube } from "lucide-react"
import { api } from "@/lib/axios"
import { formatDistanceToNow } from "date-fns"
import { ptBR } from "date-fns/locale"
import { AxiosError } from "axios"
import { useRouter } from "next/navigation"

interface Video {
  id: number
  video_id: string
  title: string
  thumbnail_url: string
  published_at: string
}

interface MonitoringDetails {
  id: number
  name: string
  channel_id: number
  channel_name: string
  channel_avatar: string | null
  status: "active" | "paused" | "completed" | "error"
  is_continuous: boolean
  interval_time: string | null
  created_at: string
  last_check_at: string | null
  total_videos: number
  processed_videos: number
  playlist_ids: string[]
  videos: Array<{
    id: number
    video_id: number
    status: "pending" | "processing" | "completed" | "error"
    error_message: string | null
    processed_at: string | null
  }>
}

interface Playlist {
  playlist_id: string
  title: string
  description: string | null
  thumbnail_url: string | null
  video_count: number
}

interface MonitoringDetailsProps {
  monitoringId: number
}

const intervalOptions = [
  { value: 10, label: "10 minutos" },
  { value: 20, label: "20 minutos" },
  { value: 30, label: "30 minutos" },
  { value: 45, label: "45 minutos" },
  { value: 60, label: "1 hora" },
  { value: 120, label: "2 horas" },
  { value: 300, label: "5 horas" },
  { value: 720, label: "12 horas" },
  { value: 1440, label: "1 dia" },
  { value: 2880, label: "2 dias" },
  { value: 10080, label: "1 semana" },
  { value: 43200, label: "1 mês" },
]

export function MonitoringDetails({ monitoringId }: MonitoringDetailsProps) {
  const { toast } = useToast()
  const [monitoring, setMonitoring] = useState<MonitoringDetails | null>(null)
  const [recentVideos, setRecentVideos] = useState<Video[]>([])
  const [selectedVideos, setSelectedVideos] = useState<Video[]>([])
  const [isContinuous, setIsContinuous] = useState(false)
  const [intervalTime, setIntervalTime] = useState<number | null>(null)
  const [videoUrl, setVideoUrl] = useState("")
  const [playlists, setPlaylists] = useState<Playlist[]>([])
  const [selectedPlaylists, setSelectedPlaylists] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  // Carrega os detalhes do monitoramento
  async function loadMonitoring() {
    try {
      const response = await api.get(`/api/v1/monitoring/${monitoringId}`)
      setMonitoring(response.data)
      setIsContinuous(response.data.is_continuous)
      setIntervalTime(response.data.interval_time ? parseInt(response.data.interval_time) : null)
    } catch (error) {
      console.error("Erro ao carregar monitoramento:", error)
      toast({
        title: "Erro",
        description: "Não foi possível carregar os detalhes do monitoramento",
        variant: "destructive"
      })
    }
  }

  // Carrega os vídeos recentes do canal
  async function loadRecentVideos() {
    if (!monitoring) return

    try {
      const response = await api.get(`/api/v1/youtube/channels/${monitoring.channel_id}/videos`, {
        params: {
          limit: 12,
          sort: "-published_at"
        }
      })
      
      // Garantir que cada vídeo tenha um ID único
      const videos = response.data.map((video: Video, index: number) => ({
        ...video,
        // Se não tiver id, usa o índice como fallback
        id: video.id || index + 1
      }))
      setRecentVideos(videos)
    } catch (error) {
      console.error("Erro ao carregar vídeos recentes:", error)
      toast({
        title: "Erro",
        description: "Não foi possível carregar os vídeos recentes",
        variant: "destructive"
      })
    }
  }

  // Carrega as playlists do canal
  async function loadPlaylists() {
    if (!monitoring) return

    try {
      const response = await api.get<Playlist[]>(`/api/v1/youtube/channels/${monitoring.channel_id}/playlists`)
      setPlaylists(response.data)
      setSelectedPlaylists(monitoring.playlist_ids || [])
    } catch (error) {
      console.error("Erro ao carregar playlists:", error)
      toast({
        title: "Erro",
        description: "Não foi possível carregar as playlists do canal",
        variant: "destructive"
      })
    }
  }

  // Valida e adiciona um vídeo por URL
  async function handleAddVideoByUrl() {
    if (!monitoring || !videoUrl) return

    try {
      const response = await api.post(`/api/v1/youtube/channels/${monitoring.channel_id}/validate-video`, {
        video_url: videoUrl
      })
      
      const newVideo = response.data
      if (!selectedVideos.some(v => v.video_id === newVideo.video_id)) {
        setSelectedVideos([...selectedVideos, newVideo])
      }
      setVideoUrl("")
    } catch (error) {
      console.error("Erro ao adicionar vídeo:", error)
      toast({
        title: "Erro",
        description: "URL do vídeo inválida ou vídeo não pertence ao canal",
        variant: "destructive"
      })
    }
  }

  // Alterna a seleção de um vídeo da lista
  function toggleVideoSelection(video: Video) {
    if (selectedVideos.some(v => v.video_id === video.video_id)) {
      setSelectedVideos(selectedVideos.filter(v => v.video_id !== video.video_id))
    } else {
      setSelectedVideos([...selectedVideos, video])
    }
  }

  // Atualiza a configuração do monitoramento
  const handleUpdateMonitoring = async () => {
    if (!monitoring) return

    try {
      setIsLoading(true)

      // Se for monitoramento contínuo, precisa ter um intervalo
      if (isContinuous && !intervalTime) {
        toast({
          title: "Erro ao atualizar monitoramento",
          description: "Para monitoramento contínuo é necessário especificar um intervalo",
          variant: "destructive",
        })
        return
      }

      const data = {
        is_continuous: isContinuous,
        interval_time: isContinuous ? intervalTime?.toString() : null,
        playlist_ids: isContinuous ? selectedPlaylists : []
      }

      await api.put(`/api/v1/monitoring/${monitoring.id}`, data)

      toast({
        title: "Monitoramento atualizado",
        description: "O monitoramento foi atualizado com sucesso",
      })

    } catch (error) {
      if (error instanceof AxiosError) {
        toast({
          title: "Erro ao atualizar monitoramento",
          description: error.response?.data?.detail || "Erro ao atualizar monitoramento",
          variant: "destructive",
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadMonitoring()
  }, [monitoringId])

  useEffect(() => {
    if (monitoring) {
      loadRecentVideos()
      loadPlaylists()
    }
  }, [monitoring])

  if (!monitoring) {
    return <div>Carregando...</div>
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Configuração do Monitoramento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <h3 className="text-base font-medium">Monitoramento Contínuo</h3>
              <p className="text-sm text-muted-foreground">
                Ative para monitorar todos os novos vídeos do canal
              </p>
            </div>
            <Switch
              checked={isContinuous}
              onCheckedChange={setIsContinuous}
            />
          </div>

          {isContinuous && (
            <>
              <div className="space-y-2">
                <label className="text-sm font-medium">Intervalo de Verificação</label>
                <Select value={intervalTime?.toString() || ""} onValueChange={(value) => setIntervalTime(parseInt(value))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um intervalo" />
                  </SelectTrigger>
                  <SelectContent>
                    {intervalOptions.map(option => (
                      <SelectItem key={option.value} value={option.value.toString()}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Playlists para Monitorar</label>
                <div className="grid grid-cols-2 gap-4">
                  {playlists.map(playlist => (
                    <Card 
                      key={playlist.playlist_id}
                      className={`cursor-pointer ${
                        selectedPlaylists.includes(playlist.playlist_id) ? "ring-2 ring-primary" : ""
                      }`}
                      onClick={() => {
                        if (selectedPlaylists.includes(playlist.playlist_id)) {
                          setSelectedPlaylists(selectedPlaylists.filter(id => id !== playlist.playlist_id))
                        } else {
                          setSelectedPlaylists([...selectedPlaylists, playlist.playlist_id])
                        }
                      }}
                    >
                      <CardContent className="p-4">
                        <h4 className="font-medium line-clamp-2">{playlist.title}</h4>
                        <p className="text-sm text-muted-foreground mt-1">
                          {playlist.video_count} vídeos
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </>
          )}

          {!isContinuous && (
            <>
              <div className="space-y-2">
                <h3 className="text-base font-medium">Vídeos Recentes</h3>
                <div className="grid grid-cols-3 gap-4">
                  {recentVideos.map(video => (
                    <Card 
                      key={video.video_id}
                      className={`cursor-pointer ${
                        selectedVideos.some(v => v.video_id === video.video_id) ? "ring-2 ring-primary" : ""
                      }`}
                      onClick={() => toggleVideoSelection(video)}
                    >
                      <CardContent className="p-4">
                        <div 
                          className="w-full h-32 bg-cover bg-center rounded-lg mb-2"
                          style={{ backgroundImage: `url(https://i.ytimg.com/vi/${video.video_id}/hqdefault.jpg)` }}
                        />
                        <p className="text-sm font-medium line-clamp-2">{video.title}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(video.published_at), { locale: ptBR, addSuffix: true })}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <h3 className="text-base font-medium">Adicionar Vídeo por URL</h3>
                <div className="flex gap-2">
                  <Input
                    value={videoUrl}
                    onChange={e => setVideoUrl(e.target.value)}
                    placeholder="Cole a URL do vídeo aqui"
                  />
                  <Button onClick={handleAddVideoByUrl}>
                    <Plus className="w-4 h-4 mr-2" />
                    Adicionar
                  </Button>
                </div>
              </div>

              {selectedVideos.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-base font-medium">Vídeos Selecionados</h3>
                  <div className="space-y-2">
                    {selectedVideos.map(video => (
                      <Card key={video.video_id}>
                        <CardContent className="p-4 flex justify-between items-center">
                          <div className="flex items-center gap-4">
                            <div 
                              className="w-24 h-16 bg-cover bg-center rounded"
                              style={{ backgroundImage: `url(https://i.ytimg.com/vi/${video.video_id}/hqdefault.jpg)` }}
                            />
                            <div>
                              <p className="font-medium">{video.title}</p>
                              <p className="text-sm text-muted-foreground">
                                {formatDistanceToNow(new Date(video.published_at), { locale: ptBR, addSuffix: true })}
                              </p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setSelectedVideos(selectedVideos.filter(v => v.video_id !== video.video_id))}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {isContinuous && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Playlists</h3>
                <p className="text-sm text-muted-foreground">
                  Selecione as playlists que deseja monitorar
                </p>
              </div>
              
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {playlists.map((playlist) => (
                  <Card
                    key={playlist.playlist_id}
                    className={`cursor-pointer transition-colors ${
                      selectedPlaylists.includes(playlist.playlist_id)
                        ? "border-primary"
                        : "hover:border-primary/50"
                    }`}
                    onClick={() => {
                      if (selectedPlaylists.includes(playlist.playlist_id)) {
                        setSelectedPlaylists(selectedPlaylists.filter(id => id !== playlist.playlist_id))
                      } else {
                        setSelectedPlaylists([...selectedPlaylists, playlist.playlist_id])
                      }
                    }}
                  >
                    <CardHeader>
                      <CardTitle className="line-clamp-2 text-base">
                        {playlist.title}
                      </CardTitle>
                      <div className="flex items-center text-sm text-muted-foreground">
                        <Youtube className="mr-1 h-4 w-4" />
                        {playlist.video_count} vídeos
                      </div>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </div>
          )}

          <Button onClick={handleUpdateMonitoring} className="w-full" disabled={isLoading}>
            Salvar Configuração
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Status do Monitoramento</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-medium">{monitoring.name}</h3>
                <p className="text-sm text-muted-foreground">
                  Canal: {monitoring.channel_name}
                </p>
              </div>
              <Badge variant={monitoring.status === "active" ? "default" : "secondary"}>
                {monitoring.status === "active" ? "Ativo" : "Pausado"}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progresso:</span>
                <span>{monitoring.processed_videos} de {monitoring.total_videos} vídeos</span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all"
                  style={{ 
                    width: `${monitoring.total_videos > 0 
                      ? (monitoring.processed_videos / monitoring.total_videos) * 100 
                      : 0}%` 
                  }}
                />
              </div>
            </div>

            <div className="flex gap-2">
              <Button 
                variant={monitoring.status === "active" ? "destructive" : "default"}
                onClick={async () => {
                  try {
                    const response = await api.put(`/api/v1/monitoring/${monitoringId}`, {
                      status: monitoring.status === "active" ? "paused" : "active"
                    })
                    setMonitoring(response.data)
                  } catch (error) {
                    console.error("Erro ao alterar status:", error)
                    toast({
                      title: "Erro",
                      description: "Não foi possível alterar o status do monitoramento",
                      variant: "destructive"
                    })
                  }
                }}
              >
                {monitoring.status === "active" ? (
                  <>
                    <Pause className="w-4 h-4 mr-2" />
                    Pausar
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Ativar
                  </>
                )}
              </Button>

              <Button 
                variant="destructive"
                onClick={async () => {
                  try {
                    await api.delete(`/api/v1/monitoring/${monitoringId}`)
                    toast({
                      title: "Sucesso",
                      description: "Monitoramento excluído com sucesso"
                    })
                    // TODO: Redirecionar para a lista de monitoramentos
                  } catch (error) {
                    console.error("Erro ao excluir:", error)
                    toast({
                      title: "Erro",
                      description: "Não foi possível excluir o monitoramento",
                      variant: "destructive"
                    })
                  }
                }}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Excluir
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 