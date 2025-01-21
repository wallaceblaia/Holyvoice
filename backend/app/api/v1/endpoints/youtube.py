from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.security import encrypt_api_key, decrypt_api_key
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
        
        # Verifica se o canal já existe
        existing_channel = crud.youtube.get_by_url(db, channel_url=channel_in.channel_url)
        if existing_channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Canal já cadastrado"
            )
        
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
        channel = crud.youtube.create(db, obj_in=channel_data)
        
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
        crud.youtube_access.create(db, obj_in=access_data)
        
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
            return crud.youtube.get_multi(db, skip=skip, limit=limit)
        
        # Caso contrário, retorna apenas os canais que o usuário tem acesso
        return crud.youtube.get_multi_by_user(
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
            access = crud.youtube_access.get_by_user_and_channel(
                db,
                user_id=current_user.id,
                channel_id=channel_id
            )
            if not access or not access.can_view:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sem permissão para acessar este canal"
                )
        
        # Obtém o canal do banco de dados
        channel = crud.youtube.get(db, id=channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canal não encontrado"
            )
        
        # Inicializa o serviço do YouTube com a chave descriptografada
        decrypted_api_key = decrypt_api_key(channel.api_key)
        youtube_service = YouTubeService(api_key=decrypted_api_key)
        
        # Obtém os vídeos recentes
        recent_videos = await youtube_service.get_recent_videos(channel.youtube_id)
        
        # Retorna o canal com os vídeos
        return {
            **channel.__dict__,
            "recent_videos": recent_videos
        }
        
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
    limit: int = 10
):
    """
    Retorna os vídeos mais recentes de um canal.
    """
    channel = crud.youtube.get(db, id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verifica se o usuário tem acesso ao canal
    if not crud.youtube_access.has_access(db, channel_id=channel.id, user_id=current_user.id):
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    try:
        # Cria uma instância do serviço com a chave da API do canal
        youtube_service = YouTubeService(channel.api_key)
        
        # Obtém os vídeos recentes
        videos = await youtube_service.get_recent_videos(channel.youtube_id, limit)
        
        # Atualiza ou cria os vídeos no banco de dados
        db_videos = []
        for video in videos:
            video_data = schemas.YoutubeVideoCreate(
                channel_id=channel.id,
                video_id=video["id"],
                title=video["title"],
                description=video.get("description", ""),
                thumbnail_url=video["thumbnail_url"],
                published_at=video["published_at"],
                view_count=video.get("view_count"),
                like_count=video.get("like_count"),
                is_live=video.get("is_live", False)
            )
            db_video = crud.youtube_video.get_by_video_id(db, video_id=video["id"])
            if db_video:
                db_video = crud.youtube_video.update(db, db_obj=db_video, obj_in=video_data)
            else:
                db_video = crud.youtube_video.create(db, obj_in=video_data)
            db_videos.append(db_video)
        
        return db_videos
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter vídeos: {str(e)}"
        )


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
    channel = crud.youtube.get(db=db, id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    if not crud.youtube.user_can_edit(db, user_id=current_user.id, channel_id=channel_id):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")

    # Se a API key foi atualizada, criptografa a nova chave
    channel_data = channel_in.dict(exclude_unset=True)
    if "api_key" in channel_data:
        channel_data["api_key"] = encrypt_api_key(channel_data["api_key"])
    
    channel_data["updated_by"] = current_user.id
    channel = crud.youtube.update(db=db, db_obj=channel, obj_in=channel_data)
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
    channel = crud.youtube.get(db=db, id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    if not crud.youtube.user_can_delete(db, user_id=current_user.id, channel_id=channel_id):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    channel = crud.youtube.remove(db=db, id=channel_id)
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
    channel = crud.youtube.get(db=db, id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    if not crud.youtube.user_can_edit(db, user_id=current_user.id, channel_id=channel_id):
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
        
        channel = crud.youtube.update(db=db, db_obj=channel, obj_in=channel_data)
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
    if not crud.youtube.user_can_edit(db, user_id=current_user.id, channel_id=channel_id):
        raise HTTPException(status_code=403, detail="Permissão insuficiente")
    
    access_data = access_in.dict()
    access_data["created_by"] = current_user.id
    
    access = crud.youtube.create_access(db=db, obj_in=access_data)
    return access 