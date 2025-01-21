"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Youtube, Plus, Users } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/use-toast"

interface Channel {
  id: number
  channel_name: string
  channel_url: string
  banner_image?: string
  avatar_image?: string
  subscriber_count?: number
}

const API_BASE_URL = "http://localhost:8000"

export default function YoutubeChannelsPage() {
  const router = useRouter()
  const [channels, setChannels] = React.useState<Channel[]>([])
  const [isOpen, setIsOpen] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(false)
  const { toast } = useToast()

  const getAuthToken = () => {
    const token = localStorage.getItem('token')
    return token ? `Bearer ${token}` : ''
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    const formData = new FormData(e.currentTarget as HTMLFormElement)
    const channelData = {
      channel_url: formData.get("channel_url")?.toString() || "",
      api_key: formData.get("api_key")?.toString() || ""
    }

    try {
      const token = localStorage.getItem('token')
      if (!token) {
        toast({
          title: "Erro",
          description: "Você precisa estar logado para adicionar um canal",
          variant: "destructive",
        })
        return
      }

      const response = await fetch("http://localhost:8000/api/v1/youtube/channels", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(channelData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        console.error("Erro completo:", errorData)
        let errorMessage = "Erro ao adicionar canal"
        
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((err: any) => err.msg).join(", ")
          } else {
            errorMessage = errorData.detail
          }
        }
        
        toast({
          title: "Erro",
          description: errorMessage,
          variant: "destructive",
        })
        return
      }

      const data = await response.json()
      toast({
        title: "Sucesso",
        description: "Canal adicionado com sucesso!",
      })
      setIsOpen(false)
      router.refresh()
    } catch (error) {
      console.error("Erro completo:", error)
      toast({
        title: "Erro",
        description: "Erro ao adicionar canal. Tente novamente.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  React.useEffect(() => {
    const fetchChannels = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/youtube/channels`, {
          headers: {
            "Authorization": getAuthToken(),
          }
        })
        
        let data
        try {
          data = await response.json()
        } catch (error) {
          console.error("Erro ao parsear resposta:", error)
          toast({
            title: "Erro",
            description: "Erro de comunicação com o servidor. Verifique se o backend está rodando.",
            variant: "destructive",
          })
          return
        }

        if (!response.ok) throw new Error(data.detail || "Erro ao carregar canais")
        setChannels(data)
      } catch (error) {
        console.error("Erro ao carregar canais:", error)
        toast({
          title: "Erro ao carregar canais",
          description: "Não foi possível carregar a lista de canais. Verifique se o backend está rodando.",
          variant: "destructive",
        })
      }
    }

    fetchChannels()
  }, [toast])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Canais do YouTube</h1>
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Adicionar Canal
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Adicionar Canal do YouTube</DialogTitle>
              <DialogDescription>
                Informe a URL do canal e a chave da API do YouTube.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="channel_url">URL do Canal</Label>
                <Input
                  id="channel_url"
                  name="channel_url"
                  placeholder="https://youtube.com/c/canal"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="api_key">Chave da API</Label>
                <Input
                  id="api_key"
                  name="api_key"
                  type="password"
                  placeholder="Sua chave da API do YouTube"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsOpen(false)}
                >
                  Cancelar
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Adicionando..." : "Adicionar Canal"}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {channels.length === 0 ? (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xl font-semibold">
              Nenhum canal cadastrado
            </CardTitle>
            <Youtube className="h-5 w-5 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Clique no botão "Adicionar Canal" para começar a cadastrar canais do YouTube.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {channels.map((channel) => (
            <Card 
              key={channel.id} 
              className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => router.push(`/dashboard/youtube/channels/${channel.id}`)}
            >
              {channel.banner_image && (
                <div 
                  className="h-32 w-full bg-cover bg-center" 
                  style={{ backgroundImage: `url(${channel.banner_image})` }}
                />
              )}
              <CardHeader className="flex flex-row items-start space-y-0 pb-2">
                {channel.avatar_image && (
                  <div 
                    className="h-12 w-12 rounded-full bg-cover bg-center mr-4 border-2 border-background -mt-6"
                    style={{ backgroundImage: `url(${channel.avatar_image})` }}
                  />
                )}
                <div className="flex-1">
                  <CardTitle className="text-xl">{channel.channel_name}</CardTitle>
                  {channel.subscriber_count !== undefined && (
                    <CardDescription>
                      <span className="flex items-center">
                        <Users className="mr-1 h-4 w-4" />
                        {channel.subscriber_count.toLocaleString()} inscritos
                      </span>
                    </CardDescription>
                  )}
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
} 