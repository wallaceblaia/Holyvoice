import json
from typing import Any, Optional
from datetime import timedelta
from redis import asyncio as aioredis
from app.core.config import settings

# Configuração do Redis
redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_options = {
    "db": settings.REDIS_DB,
    "encoding": "utf-8",
    "decode_responses": True
}

if settings.REDIS_PASSWORD:
    redis_options["password"] = settings.REDIS_PASSWORD

redis = aioredis.from_url(redis_url, **redis_options)

class YouTubeCache:
    """
    Gerenciador de cache para dados do YouTube usando Redis.
    """
    
    @staticmethod
    def _generate_key(key_type: str, id: str, subresource: str = "") -> str:
        """Gera uma chave hierárquica para o cache."""
        return f"youtube:{key_type}:{id}:{subresource}".rstrip(":")

    @staticmethod
    async def set_cache(key: str, data: Any, expire: int = 3600) -> None:
        """Define um valor no cache com tempo de expiração."""
        await redis.set(key, json.dumps(data), ex=expire)

    @staticmethod
    async def get_cache(key: str) -> Optional[Any]:
        """Recupera um valor do cache."""
        data = await redis.get(key)
        return json.loads(data) if data else None

    @staticmethod
    async def delete_cache(key: str) -> None:
        """Remove um valor do cache."""
        await redis.delete(key)

    @classmethod
    async def clear_channel_cache(cls, channel_id: str) -> None:
        """Limpa todo o cache relacionado a um canal."""
        pattern = cls._generate_key("channel", channel_id, "*")
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)

    # Métodos específicos para cada tipo de dado
    @classmethod
    async def get_channel_info(cls, channel_id: str) -> Optional[dict]:
        """Obtém informações do canal do cache."""
        key = cls._generate_key("channel", channel_id)
        return await cls.get_cache(key)

    @classmethod
    async def set_channel_info(cls, channel_id: str, data: dict) -> None:
        """Armazena informações do canal no cache por 1 hora."""
        key = cls._generate_key("channel", channel_id)
        await cls.set_cache(key, data, expire=3600)  # 1 hora

    @classmethod
    async def get_playlists(cls, channel_id: str) -> Optional[list]:
        """Obtém playlists do canal do cache."""
        key = cls._generate_key("channel", channel_id, "playlists")
        return await cls.get_cache(key)

    @classmethod
    async def set_playlists(cls, channel_id: str, data: list) -> None:
        """Armazena playlists do canal no cache por 6 horas."""
        key = cls._generate_key("channel", channel_id, "playlists")
        await cls.set_cache(key, data, expire=21600)  # 6 horas

    @classmethod
    async def get_recent_videos(cls, channel_id: str) -> Optional[list]:
        """Obtém vídeos recentes do canal do cache."""
        key = cls._generate_key("channel", channel_id, "recent_videos")
        return await cls.get_cache(key)

    @classmethod
    async def set_recent_videos(cls, channel_id: str, data: list) -> None:
        """Armazena vídeos recentes do canal no cache por 15 minutos."""
        key = cls._generate_key("channel", channel_id, "recent_videos")
        await cls.set_cache(key, data, expire=900)  # 15 minutos

    @classmethod
    async def get_playlist_videos(cls, playlist_id: str) -> Optional[list]:
        """Obtém vídeos de uma playlist do cache."""
        key = cls._generate_key("playlist", playlist_id, "videos")
        return await cls.get_cache(key)

    @classmethod
    async def set_playlist_videos(cls, playlist_id: str, data: list) -> None:
        """Armazena vídeos de uma playlist no cache por 2 horas."""
        key = cls._generate_key("playlist", playlist_id, "videos")
        await cls.set_cache(key, data, expire=7200)  # 2 horas 