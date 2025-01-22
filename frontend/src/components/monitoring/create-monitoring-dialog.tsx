"use client"

import React, { useEffect, useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { useToast } from "@/components/ui/use-toast"
import { api } from "@/lib/axios"

interface Channel {
  id: number
  channel_name: string
  avatar_image: string | null
}

interface CreateMonitoringDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function CreateMonitoringDialog({ open, onOpenChange, onSuccess }: CreateMonitoringDialogProps) {
  const { toast } = useToast()
  const [name, setName] = useState("")
  const [selectedChannel, setSelectedChannel] = useState<string>("")
  const [channels, setChannels] = useState<Channel[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (open) {
      loadChannels()
    }
  }, [open])

  async function loadChannels() {
    try {
      const response = await api.get("/api/v1/youtube/channels")
      setChannels(response.data)
    } catch (error) {
      console.error("Erro ao carregar canais:", error)
      toast({
        title: "Erro",
        description: "Não foi possível carregar a lista de canais",
        variant: "destructive",
      })
    }
  }

  async function handleSubmit() {
    if (!name || !selectedChannel) {
      toast({
        title: "Erro",
        description: "Por favor, preencha todos os campos obrigatórios",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      await api.post("/api/v1/monitoring", {
        name,
        channel_id: parseInt(selectedChannel),
        is_continuous: false,
      })

      toast({
        title: "Sucesso",
        description: "Monitoramento criado com sucesso",
      })
      
      onOpenChange(false)
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      console.error("Erro ao criar monitoramento:", error)
      toast({
        title: "Erro",
        description: "Não foi possível criar o monitoramento",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Criar Novo Monitoramento</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="name">Nome do Monitoramento</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Digite um nome para identificar este monitoramento"
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="channel">Canal</Label>
            <Select value={selectedChannel} onValueChange={setSelectedChannel}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione um canal" />
              </SelectTrigger>
              <SelectContent className="min-w-[300px] max-h-[300px]">
                {channels.map((channel) => (
                  <SelectItem key={channel.id} value={channel.id.toString()}>
                    <div className="flex items-center gap-2">
                      <Avatar className="h-6 w-6">
                        <AvatarImage src={channel.avatar_image || undefined} alt={channel.channel_name} />
                        <AvatarFallback>{channel.channel_name.slice(0, 2).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <span>{channel.channel_name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? "Criando..." : "Criar Monitoramento"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
} 