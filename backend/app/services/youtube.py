import yt_dlp
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.core.cache import YouTubeCache


class YouTubeService:
    def __init__(self, api_key: str = None):
        # api_key não será mais necessária, mas mantemos o parâmetro para compatibilidade
        self.ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_json': True,
            'no_warnings': True
        }

    async def extract_channel_id(self, channel_url: str) -> Optional[str]:
        try:
            print(f"Extraindo ID do canal da URL: {channel_url}")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                channel_id = info.get('channel_id')
                print(f"ID do canal extraído: {channel_id}")
                return channel_id
        except Exception as e:
            print(f"Erro ao extrair ID do canal: {str(e)}")
            return None

    async def get_channel_info(self, channel_url: str) -> Optional[Dict[str, Any]]:
        try:
            print(f"Obtendo informações do canal: {channel_url}")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"{channel_url}/videos", download=False)
                
                # Obtém a thumbnail de melhor qualidade
                thumbnails = info.get('thumbnails', [])
                avatar_url = thumbnails[-1].get('url') if thumbnails else ''
                
                channel_info = {
                    "title": info.get('channel', ''),
                    "description": info.get('description', ''),
                    "avatar_image": avatar_url,
                    "banner_image": avatar_url,  # Usando mesmo avatar como banner por enquanto
                    "subscriber_count": 0,  # Valor fixo por enquanto
                    "video_count": info.get('playlist_count', 0),
                    "view_count": 0  # Será calculado pela soma dos vídeos
                }
                print(f"Informações obtidas: {channel_info}")
                return channel_info
        except Exception as e:
            print(f"Erro ao obter informações do canal: {str(e)}")
            return None

    async def get_recent_videos(self, channel_id: str, max_results: int = 12) -> List[Dict[str, Any]]:
        try:
            print(f"Buscando {max_results} vídeos recentes do canal {channel_id}")
            ydl_opts = {
                **self.ydl_opts,
                'playlist_items': f'1-{max_results}'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/channel/{channel_id}/videos", download=False)
                print("Dados brutos retornados pelo yt-dlp:")
                print(info)
                
                videos = []
                print("\nProcessando entradas de vídeos:")
                for entry in info.get('entries', []):
                    if entry:
                        print(f"\nDados do vídeo:")
                        print(f"ID: {entry.get('id')}")
                        print(f"Título: {entry.get('title')}")
                        print(f"Data de upload: {entry.get('upload_date')}")
                        print(f"Thumbnails: {entry.get('thumbnails')}")
                        
                        upload_date = entry.get('upload_date', '')
                        try:
                            published_at = datetime.strptime(upload_date, '%Y%m%d') if upload_date else datetime.now()
                        except:
                            published_at = datetime.now()
                        
                        # Garante que o ID seja string
                        video_id = str(entry.get('id', ''))
                        # Usa o formato padrão de thumbnail do YouTube em alta qualidade
                        thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
                        
                        video = {
                            "id": video_id,
                            "title": entry.get('title', ''),
                            "description": entry.get('description', ''),
                            "thumbnail_url": thumbnail_url,
                            "published_at": published_at,
                            "view_count": entry.get('view_count', 0),
                            "like_count": entry.get('like_count', 0),
                            "is_live": entry.get('is_live', False)
                        }
                        print(f"Vídeo processado: {video}")
                        videos.append(video)
                
                print(f"Total de vídeos processados: {len(videos)}")
                return videos
                
        except Exception as e:
            print(f"Erro ao obter vídeos recentes: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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

    async def extract_video_id(self, video_url: str) -> Optional[str]:
        try:
            print(f"Extraindo ID do vídeo da URL: {video_url}")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False, process=False)
                # Verifica se é um vídeo individual
                if info.get('_type') == 'url' and 'watch?v=' in video_url:
                    # Extrai o ID do vídeo da URL
                    import re
                    video_id_match = re.search(r'v=([^&]+)', video_url)
                    if video_id_match:
                        video_id = video_id_match.group(1)
                        print(f"ID do vídeo extraído: {video_id}")
                        return video_id
                # Se não for um vídeo individual, tenta pegar o ID diretamente
                video_id = info.get('id')
                print(f"ID do vídeo extraído: {video_id}")
                return video_id
        except Exception as e:
            print(f"Erro ao extrair ID do vídeo: {str(e)}")
            return None

    async def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        try:
            print(f"Obtendo informações do vídeo: {video_id}")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                upload_date = info.get('upload_date', '')
                try:
                    published_at = datetime.strptime(upload_date, '%Y%m%d') if upload_date else datetime.now()
                except:
                    published_at = datetime.now()
                
                video_info = {
                    "id": info.get('id', ''),
                    "channel_id": info.get('channel_id', ''),
                    "title": info.get('title', ''),
                    "description": info.get('description', ''),
                    "thumbnail_url": info.get('thumbnail', ''),
                    "published_at": published_at,
                    "view_count": info.get('view_count', 0),
                    "like_count": info.get('like_count', 0),
                    "is_live": info.get('is_live', False)
                }
                print(f"Informações obtidas: {video_info}")
                return video_info
        except Exception as e:
            print(f"Erro ao obter informações do vídeo: {str(e)}")
            return None 