"use client"

import * as React from "react"
import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Play, Pause, Trash2 } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import { ptBR } from "date-fns/locale"
import { api } from "@/lib/axios"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"

interface Monitoring {
  id: number
  name: string
  channel_name: string
  channel_avatar: string | null
  status: "active" | "paused" | "completed" | "error"
  is_continuous: boolean
  interval_time: string | null
  created_at: string
  last_check_at: string | null
  total_videos: number
  processed_videos: number
}

const statusMap = {
  not_configured: {
    label: "Não configurado",
    className: "bg-gray-100 text-gray-800"
  },
  active: {
    label: "Ativo",
    className: "bg-green-100 text-green-800"
  },
  paused: {
    label: "Pausado",
    className: "bg-yellow-100 text-yellow-800"
  },
  completed: {
    label: "Concluído",
    className: "bg-blue-100 text-blue-800"
  },
  error: {
    label: "Erro",
    className: "bg-red-100 text-red-800"
  }
}

export function MonitoringList() {
  const { toast } = useToast()
  const [monitorings, setMonitorings] = useState<Monitoring[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    loadMonitorings()
  }, [])

  async function loadMonitorings() {
    try {
      const response = await api.get<Monitoring[]>("/api/v1/monitoring")
      setMonitorings(response.data)
    } catch (error) {
      console.error("Erro ao carregar monitoramentos:", error)
      toast({
        title: "Erro",
        description: "Não foi possível carregar a lista de monitoramentos",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  async function handleToggleStatus(id: number, currentStatus: string) {
    try {
      const newStatus = currentStatus === "active" ? "paused" : "active"
      await api.put(`/api/v1/monitoring/${id}`, {
        status: newStatus,
      })
      
      toast({
        title: "Sucesso",
        description: `Monitoramento ${newStatus === "active" ? "ativado" : "pausado"} com sucesso`,
      })
      
      loadMonitorings()
    } catch (error) {
      console.error("Erro ao alterar status:", error)
      toast({
        title: "Erro",
        description: "Não foi possível alterar o status do monitoramento",
        variant: "destructive",
      })
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Tem certeza que deseja excluir este monitoramento?")) return

    try {
      await api.delete(`/api/v1/monitoring/${id}`)
      toast({
        title: "Sucesso",
        description: "Monitoramento excluído com sucesso",
      })
      loadMonitorings()
    } catch (error) {
      console.error("Erro ao excluir monitoramento:", error)
      toast({
        title: "Erro",
        description: "Não foi possível excluir o monitoramento",
        variant: "destructive",
      })
    }
  }

  if (isLoading) {
    return (
      <Card className="p-8">
        <div className="flex items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-current border-t-transparent text-muted-foreground" />
        </div>
      </Card>
    )
  }

  if (monitorings.length === 0) {
    return (
      <Card className="p-8 text-center text-muted-foreground">
        Nenhum monitoramento encontrado.
      </Card>
    )
  }

  return (
    <div className="grid gap-4">
      {monitorings.map((monitoring) => (
        <Card
          key={monitoring.id}
          className="cursor-pointer hover:bg-accent/50 transition-colors"
          onClick={() => router.push(`/dashboard/projects/monitoring/${monitoring.id}`)}
        >
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {monitoring.channel_avatar && (
                  <img
                    src={monitoring.channel_avatar}
                    alt={monitoring.channel_name}
                    className="h-12 w-12 rounded-full"
                  />
                )}
                <div>
                  <h3 className="font-semibold">{monitoring.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {monitoring.channel_name}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge
                  variant={monitoring.status === "active" ? "default" : "secondary"}
                >
                  {monitoring.status === "active" ? "Ativo" : "Pausado"}
                </Badge>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleToggleStatus(monitoring.id, monitoring.status)
                  }}
                >
                  {monitoring.status === "active" ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(monitoring.id)
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="mt-4">
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary"
                  style={{
                    width: `${(monitoring.processed_videos / monitoring.total_videos) * 100}%`,
                  }}
                />
              </div>
              <div className="mt-2 flex items-center justify-between text-sm text-muted-foreground">
                <p>
                  {monitoring.processed_videos} de {monitoring.total_videos} vídeos processados
                </p>
                <p>
                  {monitoring.last_check_at
                    ? `Última verificação ${formatDistanceToNow(
                        new Date(monitoring.last_check_at),
                        { locale: ptBR, addSuffix: true }
                      )}`
                    : "Nunca verificado"}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
} 