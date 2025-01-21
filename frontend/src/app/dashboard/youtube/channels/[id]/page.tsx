"use client"

import * as React from "react"
import { useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Youtube, Users, Calendar, Eye } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface Channel {
  id: number
  youtube_id: string
  channel_name: string
  description: string
  banner_image?: string
  avatar_image?: string
  subscriber_count?: number
  video_count?: number
  view_count?: number
  created_at: string
}

interface Video {
  id: string
  title: string
  thumbnail_url: string
  published_at: string
  is_live: boolean
}

export default function ChannelDetailsPage() {
  const params = useParams()
  const { toast } = useToast()
  const [channel, setChannel] = React.useState<Channel | null>(null)
  const [recentVideos, setRecentVideos] = React.useState<Video[]>([])
  const [isLoading, setIsLoading] = React.useState(true)
  const [selectedVideo, setSelectedVideo] = React.useState<Video | null>(null)

  React.useEffect(() => {
    const fetchChannelDetails = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          toast({
            title: "Erro",
            description: "Você precisa estar logado para visualizar os detalhes do canal",
            variant: "destructive",
          })
          return
        }

        const response = await fetch(`http://localhost:8000/api/v1/youtube/channels/${params.id}`, {
          headers: {
            "Authorization": `Bearer ${token}`,
          }
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || "Erro ao carregar dados do canal")
        }
        const data = await response.json()
        setChannel(data)
        setRecentVideos(data.recent_videos || [])
      } catch (error) {
        console.error("Erro ao carregar detalhes do canal:", error)
        toast({
          title: "Erro",
          description: error instanceof Error ? error.message : "Erro ao carregar detalhes do canal",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    if (params.id) {
      fetchChannelDetails()
    }
  }, [params.id, toast])

  if (isLoading) {
    return <div>Carregando...</div>
  }

  if (!channel) {
    return <div>Canal não encontrado</div>
  }

  return (
    <div className="space-y-6">
      {channel.banner_image && (
        <div 
          className="h-48 w-full bg-cover bg-center rounded-lg"
          style={{ backgroundImage: `url(${channel.banner_image})` }}
        />
      )}

      <div className="flex items-start space-x-4">
        {channel.avatar_image && (
          <div 
            className="h-24 w-24 rounded-full bg-cover bg-center border-4 border-background"
            style={{ backgroundImage: `url(${channel.avatar_image})` }}
          />
        )}
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{channel.channel_name}</h1>
          <div className="flex space-x-4 mt-2 text-muted-foreground">
            {channel.subscriber_count !== undefined && (
              <span className="flex items-center">
                <Users className="mr-1 h-4 w-4" />
                {channel.subscriber_count.toLocaleString()} inscritos
              </span>
            )}
            {channel.video_count !== undefined && (
              <span className="flex items-center">
                <Youtube className="mr-1 h-4 w-4" />
                {channel.video_count.toLocaleString()} vídeos
              </span>
            )}
            {channel.view_count !== undefined && (
              <span className="flex items-center">
                <Eye className="mr-1 h-4 w-4" />
                {channel.view_count.toLocaleString()} visualizações
              </span>
            )}
          </div>
          {channel.description && (
            <p className="mt-4 text-muted-foreground">{channel.description}</p>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Vídeos Recentes</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {recentVideos.map((video) => (
            <Card 
              key={video.id} 
              className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => setSelectedVideo(video)}
            >
              {video.thumbnail_url && (
                <div className="relative group">
                  <div 
                    className="h-48 w-full bg-cover bg-center"
                    style={{ backgroundImage: `url(${video.thumbnail_url})` }}
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center">
                    <Youtube className="text-white opacity-0 group-hover:opacity-100 transition-opacity h-12 w-12" />
                  </div>
                </div>
              )}
              <CardHeader>
                <CardTitle className="line-clamp-2 text-base">{video.title}</CardTitle>
                <CardDescription className="flex items-center">
                  <Calendar className="mr-1 h-4 w-4" />
                  {format(new Date(video.published_at), "d 'de' MMMM 'de' yyyy", { locale: ptBR })}
                  {video.is_live && (
                    <span className="ml-2 px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
                      AO VIVO
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>

      <Dialog open={!!selectedVideo} onOpenChange={() => setSelectedVideo(null)}>
        <DialogContent className="sm:max-w-[800px]">
          <DialogHeader>
            <DialogTitle className="line-clamp-2">{selectedVideo?.title}</DialogTitle>
          </DialogHeader>
          <div className="aspect-video">
            {selectedVideo && (
              <iframe
                className="w-full h-full rounded-lg"
                src={`https://www.youtube.com/embed/${selectedVideo.id}`}
                title={selectedVideo.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
} 