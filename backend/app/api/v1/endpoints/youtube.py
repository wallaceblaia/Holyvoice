from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from app.crud.crud_youtube import crud_youtube
from app import models, schemas
from app.api import deps
from app.core.security import encrypt_api_key, decrypt_api_key, get_current_active_user
from app.services.youtube import YouTubeService

router = APIRouter()


@router.post("/channels", response_model=schemas.YoutubeChannel)
async def create_channel(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    channel_in: schemas.YoutubeChannelCreate
) -> models.YoutubeChannel:
    """
    Cria um novo canal do YouTube.
    """
    try:
        print("Iniciando criação do canal...")
        print(f"Dados recebidos: {channel_in.dict()}")
        
        print("Inicializando serviço do YouTube...")
        # Inicializa o serviço do YouTube
        youtube_service = YouTubeService(api_key=channel_in.api_key)
        
        print("Extraindo ID do canal...")
        # Extrai o ID do canal da URL
        channel_id = await youtube_service.extract_channel_id(channel_in.channel_url)
        print(f"ID do canal extraído: {channel_id}")
        
        if not channel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL do canal inválida"
            )
            
        # Verifica se o canal já existe
        existing_channel = crud_youtube.get_channel_by_youtube_id(db, youtube_id=channel_id)
        if existing_channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Canal já cadastrado"
            )
        
        print("Obtendo informações do canal...")
        # Obtém informações do canal
        channel_info = await youtube_service.get_channel_info(channel_id)
        print(f"Informações obtidas: {channel_info}")
        
        if not channel_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível obter informações do canal"
            )
        
        print("Criptografando API key...")
        # Cria o objeto do canal com as informações obtidas
        encrypted_api_key = encrypt_api_key(channel_in.api_key)
        print("API key criptografada com sucesso")
        
        channel_data = schemas.YoutubeChannelCreateDB(
            channel_url=channel_in.channel_url,
            youtube_id=channel_id,
            channel_name=channel_info["title"],
            api_key=encrypted_api_key,
            description=channel_info["description"],
            avatar_image=channel_info["avatar_image"],
            banner_image=channel_info["banner_image"],
            subscriber_count=channel_info["subscriber_count"],
            video_count=channel_info["video_count"],
            view_count=channel_info["view_count"],
            created_by=current_user.id
        )
        
        print("Criando canal no banco de dados...")
        # Cria o canal no banco de dados
        channel = crud_youtube.create(db, obj_in=channel_data)
        
        print("Criando registro de acesso...")
        # Cria o registro de acesso para o usuário atual
        access_data = schemas.YoutubeChannelAccessCreate(
            channel_id=channel.id,
            user_id=current_user.id,
            can_view=True,
            can_edit=True,
            can_delete=True,
            created_by=current_user.id
        )
        crud_youtube.create_access(db, obj_in=access_data)
        
        print("Canal criado com sucesso!")
        return channel
        
    except HTTPException as e:
        print(f"Erro HTTP: {e.detail}")
        raise e
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar canal: {str(e)}"
        )


@router.get("/channels", response_model=List[schemas.YoutubeChannel])
async def list_channels(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100
) -> List[models.YoutubeChannel]:
    """
    Lista os canais do YouTube.
    """
    try:
        # Se o usuário for superusuário, retorna todos os canais
        if current_user.is_superuser:
            return crud_youtube.get_multi(db, skip=skip, limit=limit)
        
        # Caso contrário, retorna apenas os canais que o usuário tem acesso
        return crud_youtube.get_channels_by_user(
            db, 
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar canais: {str(e)}"
        )


@router.get("/channels/{channel_id}", response_model=schemas.YoutubeChannelWithVideos)
async def get_channel(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    channel_id: int
) -> Any:
    """
    Obtém detalhes de um canal específico.
    """
    try:
        # Verifica se o usuário tem acesso ao canal
        if not current_user.is_superuser:
            if not crud_youtube.user_can_access_channel(
                db,
                user_id=current_user.id,
                channel_id=channel_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sem permissão para acessar este canal"
                )
        
        # Obtém o canal do banco de dados
        channel = crud_youtube.get_channel(db, id=channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canal não encontrado"
            )
        
        # Inicializa o serviço do YouTube com a chave descriptografada
        decrypted_api_key = decrypt_api_key(channel.api_key)
        youtube_service = YouTubeService(api_key=decrypted_api_key)
        
        # Obtém os vídeos recentes
        videos = await youtube_service.get_recent_videos(channel.youtube_id)
        
        # Mapeia os vídeos para o formato correto
        recent_videos = []
        for video in videos:
            print(f"\nCriando objeto YoutubeVideo com dados: {video}")
            video_data = schemas.YoutubeVideo(
                id=0,  # ID será definido quando salvo no banco
                video_id=str(video["id"]),  # Garante que seja string
                channel_id=channel.id,
                title=video["title"],
                thumbnail_url=video["thumbnail_url"],
                published_at=video["published_at"],
                is_live=video.get("is_live", False),
                created_at=None,
                updated_at=None
            )
            recent_videos.append(video_data)
        
        # Retorna o canal com os vídeos
        channel_data = schemas.YoutubeChannelWithVideos(
            id=channel.id,
            youtube_id=channel.youtube_id,
            channel_url=channel.channel_url,
            channel_name=channel.channel_name,
            description=channel.description,
            avatar_image=channel.avatar_image,
            banner_image=channel.banner_image,
            subscriber_count=channel.subscriber_count,
            video_count=channel.video_count,
            view_count=channel.view_count,
            created_at=channel.created_at,
            updated_at=channel.updated_at,
            last_sync_at=channel.last_sync_at,
            recent_videos=recent_videos
        )
        return channel_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro ao obter canal: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter canal: {str(e)}"
        )


@router.get("/channels/{channel_id}/videos", response_model=List[schemas.YoutubeVideo])
async def get_channel_videos(
    channel_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    limit: int = 12,
    sort: str = "-published_at"
):
    """
    Retorna os vídeos mais recentes de um canal.
    """
    channel = crud_youtube.get_channel(db, id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verifica se o usuário tem acesso ao canal
    if not crud_youtube.user_can_access_channel(db, channel_id=channel.id, user_id=current_user.id):
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    try:
        # Primeiro tenta buscar do YouTube
        decrypted_api_key = decrypt_api_key(channel.api_key)
        youtube_service = YouTubeService(api_key=decrypted_api_key)
        videos = await youtube_service.get_recent_videos(channel.youtube_id, limit)
        
        # Atualiza ou cria os vídeos no banco de dados
        db_videos = []
        for video in videos:
            # Garante que o video_id seja string
            video_id = str(video["id"])
            
            # Usa o formato padrão de thumbnail do YouTube em alta qualidade
            thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
            
            video_data = schemas.YoutubeVideoCreate(
                channel_id=channel.id,
                video_id=video_id,
                title=video["title"],
                thumbnail_url=thumbnail_url,
                published_at=video["published_at"],
                is_live=video.get("is_live", False)
            )
            
            # Verifica se o vídeo já existe
            db_video = crud_youtube.get_video_by_youtube_id(db, youtube_id=video_id, channel_id=channel.id)
            if db_video:
                db_video = crud_youtube.update_video(db, db_obj=db_video, obj_in=video_data)
            else:
                db_video = crud_youtube.create_video(db, obj_in=video_data, channel_id=channel.id)
            
            db_videos.append(db_video)
            
    except Exception as e:
        # Se falhar, retorna os vídeos do banco de dados
        db_videos = (
            db.query(models.YoutubeVideo)
            .filter(models.YoutubeVideo.channel_id == channel_id)
            .order_by(desc(models.YoutubeVideo.published_at))
            .limit(limit)
            .all()
        )
    
    return db_videos


@router.put("/channels/{channel_id}", response_model=schemas.YoutubeChannel)
async def update_channel(
    *,
    db: Session = Depends(deps.get_db),
    channel_id: int,
    channel_in: schemas.YoutubeChannelUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Atualizar canal do YouTube.
    """
    channel = crud_youtube.get_channel(db=db, id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    if not crud_youtube.user_can_edit(db, user_id=current_user.id, channel_id=channel_id):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")

    # Se a API key foi atualizada, criptografa a nova chave
    channel_data = channel_in.dict(exclude_unset=True)
    if "api_key" in channel_data:
        channel_data["api_key"] = encrypt_api_key(channel_data["api_key"])
    
    channel_data["updated_by"] = current_user.id
    channel = crud_youtube.update_channel(db=db, db_obj=channel, obj_in=channel_data)
    return channel


@router.delete("/channels/{channel_id}")
async def delete_channel(
    *,
    db: Session = Depends(deps.get_db),
    channel_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Deletar canal do YouTube.
    """
    channel = crud_youtube.get_channel(db=db, id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    if not crud_youtube.user_can_delete(db, user_id=current_user.id, channel_id=channel_id):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    channel = crud_youtube.remove_channel(db=db, id=channel_id)
    return {"message": "Canal removido com sucesso"}


@router.post("/channels/{channel_id}/sync", response_model=schemas.YoutubeChannel)
async def sync_channel(
    *,
    db: Session = Depends(deps.get_db),
    channel_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Sincronizar dados do canal com o YouTube.
    """
    channel = crud_youtube.get_channel(db=db, id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    if not crud_youtube.user_can_edit(db, user_id=current_user.id, channel_id=channel_id):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")

    try:
        # Descriptografa a API key para uso
        api_key = decrypt_api_key(channel.api_key)
        youtube = YouTubeService(api_key)
        
        # Sincroniza dados do canal
        channel_info = await youtube.get_channel_info(channel.channel_url)
        channel_data = {
            "updated_by": current_user.id,
            "last_sync_at": datetime.utcnow(),
            **channel_info
        }
        
        channel = crud_youtube.update_channel(db=db, db_obj=channel, obj_in=channel_data)
        return channel
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao sincronizar com YouTube: {str(e)}"
        )


@router.post("/channels/{channel_id}/access", response_model=schemas.YoutubeChannelAccess)
def create_channel_access(
    *,
    db: Session = Depends(deps.get_db),
    channel_id: int,
    access_in: schemas.YoutubeChannelAccessCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Conceder acesso ao canal para um usuário.
    """
    if not crud_youtube.user_can_edit(db, user_id=current_user.id, channel_id=channel_id):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    access_data = access_in.dict()
    access_data["created_by"] = current_user.id
    
    access = crud_youtube.create_access(db=db, obj_in=access_data)
    return access


@router.post("/channels/{channel_id}/validate-video", response_model=schemas.YoutubeVideo)
async def validate_video(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    channel_id: int,
    video_url: str = Body(..., embed=True)
) -> Any:
    """
    Valida se um vídeo pertence ao canal e retorna suas informações.
    """
    # Verifica se o usuário tem acesso ao canal
    if not crud_youtube.user_can_access_channel(db, user_id=current_user.id, channel_id=channel_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este canal"
        )
    
    # Obtém o canal
    channel = crud_youtube.get_channel(db, id=channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canal não encontrado"
        )
    
    try:
        # Inicializa o serviço do YouTube
        decrypted_api_key = decrypt_api_key(channel.api_key)
        youtube_service = YouTubeService(api_key=decrypted_api_key)
        
        # Extrai o ID do vídeo da URL
        video_id = await youtube_service.extract_video_id(video_url)
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="URL do vídeo inválida. Por favor, verifique se a URL está correta."
            )
        
        # Obtém informações do vídeo
        video_info = await youtube_service.get_video_info(video_id)
        if not video_info:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Não foi possível obter informações do vídeo. Verifique se o vídeo está disponível."
            )
        
        # Verifica se o vídeo pertence ao canal
        if video_info["channel_id"] != channel.youtube_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Este vídeo não pertence ao canal selecionado"
            )
        
        # Cria ou atualiza o vídeo no banco
        video_data = schemas.YoutubeVideoCreate(
            channel_id=channel.id,
            video_id=video_id,
            title=video_info["title"],
            thumbnail_url=video_info["thumbnail_url"],
            published_at=video_info["published_at"],
            is_live=video_info.get("is_live", False)
        )
        
        db_video = crud_youtube.get_video_by_youtube_id(db, youtube_id=video_id, channel_id=channel.id)
        if db_video:
            db_video = crud_youtube.update_video(db, db_obj=db_video, obj_in=video_data)
        else:
            db_video = crud_youtube.create_video(db, obj_in=video_data, channel_id=channel.id)
        
        return db_video
        
    except HTTPException as e:
        # Repassa os erros HTTP já tratados
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Erro ao validar vídeo. Verifique se a URL está correta e tente novamente."
        )


@router.get("/channels/{channel_id}/playlists", response_model=List[schemas.YoutubePlaylist])
async def get_channel_playlists(
    channel_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retorna todas as playlists de um canal.
    """
    channel = crud_youtube.get_channel(db, id=channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canal não encontrado",
        )

    if not crud_youtube.user_can_access_channel(db, user_id=current_user.id, channel_id=channel.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este canal",
        )

    try:
        decrypted_api_key = decrypt_api_key(channel.api_key)
        youtube_service = YouTubeService(api_key=decrypted_api_key)
        playlists = await youtube_service.get_playlists(channel.channel_url)
        
        # Formata as playlists para incluir todos os campos obrigatórios
        formatted_playlists = []
        for playlist in playlists:
            formatted_playlist = schemas.YoutubePlaylist(
                id=0,  # ID será definido quando salvo no banco
                channel_id=channel.id,
                playlist_id=playlist["playlist_id"],
                title=playlist["title"],
                description=playlist.get("description", ""),
                thumbnail_url=playlist.get("thumbnail_url", ""),
                video_count=playlist.get("video_count", 0),
                created_at=datetime.utcnow()
            )
            formatted_playlists.append(formatted_playlist)
            
        return formatted_playlists
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não foi possível obter as playlists do canal. Tente novamente mais tarde.",
        ) 