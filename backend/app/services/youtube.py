from datetime import datetime
from typing import Dict, Any, Optional, List
import aiohttp
import re
from app.core.cache import YouTubeCache


class YouTubeService:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz uma requisição para a API do YouTube.
        """
        params["key"] = self.api_key
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/{endpoint}", params=params) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Erro na API do YouTube: {error_data.get('error', {}).get('message', 'Erro desconhecido')}")
                return await response.json()

    async def extract_channel_id(self, channel_url: str) -> Optional[str]:
        """
        Extrai o ID do canal a partir da URL.
        Suporta vários formatos de URL do YouTube.
        """
        # Padrões de URL do YouTube
        patterns = [
            r"youtube\.com/channel/([^/?&]+)",  # URLs de canal padrão
            r"youtube\.com/c/([^/?&]+)",        # URLs personalizadas
            r"youtube\.com/@([^/?&]+)",         # URLs de handle
            r"youtube\.com/user/([^/?&]+)"      # URLs de usuário antigas
        ]
        
        for pattern in patterns:
            match = re.search(pattern, channel_url)
            if match:
                identifier = match.group(1)
                
                # Se for uma URL personalizada ou handle, precisamos fazer uma busca
                if "c/" in channel_url or "@" in channel_url or "user/" in channel_url:
                    try:
                        # Busca o canal usando o identificador
                        params = {
                            "part": "id",
                            "forUsername" if "user/" in channel_url else "q": identifier,
                            "type": "channel",
                            "maxResults": 1
                        }
                        result = await self._make_request("search", params)
                        items = result.get("items", [])
                        if items:
                            return items[0]["id"]["channelId"]
                    except Exception:
                        continue
                else:
                    return identifier
        
        return None

    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações detalhadas de um canal.
        """
        try:
            # Primeira requisição para informações básicas
            params = {
                "part": "snippet,statistics,brandingSettings",
                "id": channel_id
            }
            result = await self._make_request("channels", params)
            
            if not result.get("items"):
                return None
            
            channel = result["items"][0]
            snippet = channel["snippet"]
            statistics = channel["statistics"]
            branding = channel.get("brandingSettings", {})
            
            return {
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "avatar_image": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "banner_image": branding.get("image", {}).get("bannerExternalUrl"),
                "subscriber_count": int(statistics.get("subscriberCount", 0)),
                "video_count": int(statistics.get("videoCount", 0)),
                "view_count": int(statistics.get("viewCount", 0))
            }
        except Exception as e:
            print(f"Erro ao obter informações do canal: {str(e)}")
            return None

    async def get_recent_videos(self, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém os vídeos mais recentes de um canal.
        """
        try:
            # Primeiro, obtém os IDs dos vídeos mais recentes
            params = {
                "part": "id",
                "channelId": channel_id,
                "order": "date",
                "maxResults": max_results,
                "type": "video"
            }
            search_result = await self._make_request("search", params)
            
            if not search_result.get("items"):
                return []
            
            # Extrai os IDs dos vídeos
            video_ids = [item["id"]["videoId"] for item in search_result["items"]]
            
            # Obtém informações detalhadas dos vídeos
            params = {
                "part": "snippet,statistics,liveStreamingDetails",
                "id": ",".join(video_ids)
            }
            videos_result = await self._make_request("videos", params)
            
            videos = []
            for item in videos_result.get("items", []):
                snippet = item["snippet"]
                statistics = item.get("statistics", {})
                
                video = {
                    "id": item["id"],
                    "title": snippet["title"],
                    "description": snippet.get("description", ""),
                    "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    "published_at": snippet["publishedAt"],
                    "view_count": int(statistics.get("viewCount", 0)),
                    "like_count": int(statistics.get("likeCount", 0)),
                    "is_live": bool(item.get("liveStreamingDetails"))
                }
                videos.append(video)
            
            return videos
        except Exception as e:
            print(f"Erro ao obter vídeos recentes: {str(e)}")
            return []

    async def validate_channel(self, channel_url: str) -> Dict[str, Any]:
        """
        Valida se o canal existe e retorna suas informações básicas.
        """
        channel_id = self.extract_channel_id(channel_url)
        if not channel_id:
            raise ValueError("URL do canal inválida")

        # Se for um canal personalizado ou handle, precisamos primeiro obter o ID real
        if not channel_id.startswith('UC'):
            params = {
                "part": "id",
                "forUsername" if '@' not in channel_url else "forHandle": channel_id
            }
            data = await self._make_request("channels", params)
            if not data.get("items"):
                raise ValueError("Canal não encontrado")
            channel_id = data["items"][0]["id"]

        return await self.get_channel_info_by_id(channel_id)

    async def get_channel_info_by_id(self, channel_id: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas do canal pelo ID.
        """
        # Tenta obter do cache primeiro
        cached_data = await YouTubeCache.get_channel_info(channel_id)
        if cached_data:
            return cached_data

        params = {
            "part": "snippet,statistics,brandingSettings",
            "id": channel_id
        }
        
        data = await self._make_request("channels", params)
        if not data.get("items"):
            raise ValueError("Canal não encontrado")

        channel = data["items"][0]
        channel_info = {
            "channel_name": channel["snippet"]["title"],
            "banner_image": channel["brandingSettings"].get("image", {}).get("bannerExternalUrl"),
            "avatar_image": channel["snippet"]["thumbnails"].get("high", {}).get("url"),
            "subscriber_count": int(channel["statistics"].get("subscriberCount", 0)),
            "channel_email": channel["snippet"].get("email")
        }

        # Salva no cache
        await YouTubeCache.set_channel_info(channel_id, channel_info)
        return channel_info

    async def get_playlists(self, channel_id: str) -> List[Dict[str, Any]]:
        """
        Obtém todas as playlists do canal.
        """
        # Tenta obter do cache primeiro
        cached_data = await YouTubeCache.get_channel_playlists(channel_id)
        if cached_data:
            return cached_data

        params = {
            "part": "snippet,contentDetails",
            "channelId": channel_id,
            "maxResults": 50
        }
        
        data = await self._make_request("playlists", params)
        playlists = [
            {
                "playlist_id": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "video_count": item["contentDetails"]["itemCount"]
            }
            for item in data.get("items", [])
        ]

        # Salva no cache
        await YouTubeCache.set_channel_playlists(channel_id, playlists)
        return playlists

    async def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Obtém os vídeos de uma playlist específica.
        """
        # Tenta obter do cache primeiro
        cached_data = await YouTubeCache.get_playlist_videos(playlist_id)
        if cached_data:
            return cached_data

        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": max_results
        }
        
        data = await self._make_request("playlistItems", params)
        videos = []
        
        for item in data.get("items", []):
            video_data = {
                "video_id": item["contentDetails"]["videoId"],
                "title": item["snippet"]["title"],
                "thumbnail_url": item["snippet"]["thumbnails"].get("high", {}).get("url"),
                "published_at": datetime.fromisoformat(item["snippet"]["publishedAt"].replace('Z', '+00:00')),
                "position": item["snippet"]["position"]
            }
            videos.append(video_data)

        # Salva no cache
        await YouTubeCache.set_playlist_videos(playlist_id, videos)
        return videos 