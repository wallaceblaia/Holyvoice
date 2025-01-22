import { api } from "@/lib/axios"

export interface Monitoring {
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

export interface CreateMonitoringData {
  name: string
  channel_id: number
  videos: number[]
  is_continuous: boolean
  interval_time?: string
}

export async function listMonitorings() {
  const response = await api.get<Monitoring[]>("/monitoring")
  return response.data
}

export async function createMonitoring(data: CreateMonitoringData) {
  const response = await api.post<Monitoring>("/monitoring", data)
  return response.data
}

export async function updateMonitoring(id: number, data: Partial<CreateMonitoringData>) {
  const response = await api.put<Monitoring>(`/monitoring/${id}`, data)
  return response.data
}

export async function deleteMonitoring(id: number) {
  await api.delete(`/monitoring/${id}`)
}

export async function getChannelVideos(channelId: number) {
  const response = await api.get<{
    id: number
    title: string
    thumbnail_url: string | null
    published_at: string
  }[]>(`/youtube/channels/${channelId}/videos`, {
    params: {
      limit: 10,
      sort: "-published_at"
    }
  })
  return response.data
}

export async function validateVideoUrl(channelId: number, url: string) {
  const response = await api.post<{
    id: number
    title: string
    thumbnail_url: string | null
    published_at: string
  }>(`/api/v1/youtube/channels/${channelId}/validate-video`, {
    video_url: url
  })
  return response.data
} 