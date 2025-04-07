import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils import setup_logging

logger = setup_logging()

def upload_videos(config):
    """Upload de vídeos para as plataformas"""
    final_dir = Path(config['final_dir'])
    
    # Upload para YouTube
    youtube_service = get_youtube_service(config)
    if youtube_service:
        for video_path in final_dir.glob('*_shorts.mp4'):
            try:
                logger.info(f"Iniciando upload para YouTube: {video_path.name}")
                upload_to_youtube(video_path, youtube_service, config)
                logger.info(f"Upload para YouTube concluído: {video_path.name}")
            except Exception as e:
                logger.error(f"Erro ao fazer upload para YouTube {video_path.name}: {str(e)}")
                continue
    
    # Upload para TikTok (requer automação via navegador)
    for video_path in final_dir.glob('*_tiktok.mp4'):
        try:
            logger.info(f"Iniciando upload para TikTok: {video_path.name}")
            upload_to_tiktok(video_path, config)
            logger.info(f"Upload para TikTok concluído: {video_path.name}")
        except Exception as e:
            logger.error(f"Erro ao fazer upload para TikTok {video_path.name}: {str(e)}")
            continue

def get_youtube_service(config):
    """Autentica e retorna o serviço do YouTube"""
    creds = None
    token_path = Path('token.json')
    
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), ['https://www.googleapis.com/auth/youtube.upload'])
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                ['https://www.googleapis.com/auth/youtube.upload']
            )
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('youtube', 'v3', credentials=creds)

def upload_to_youtube(video_path, youtube_service, config):
    """Upload de vídeo para o YouTube"""
    video_title = f"{Path(video_path).stem} - Shorts"
    
    request_body = {
        'snippet': {
            'title': video_title,
            'description': config['default_description'],
            'tags': config['default_tags'],
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(
        str(video_path),
        mimetype='video/mp4',
        resumable=True
    )
    
    response = youtube_service.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    ).execute()
    
    return response

def upload_to_tiktok(video_path, config):
    """Upload de vídeo para o TikTok usando automação de navegador"""
    # Nota: Esta é uma implementação básica. O TikTok não possui API oficial,
    # então é necessário usar automação de navegador.
    # Implementação real requer Selenium ou Playwright
    
    logger.warning("Upload para TikTok não implementado. Requer automação de navegador.")
    logger.info("Por favor, faça o upload manualmente em: https://www.tiktok.com/upload")
    
    # TODO: Implementar automação com Selenium/Playwright
    # 1. Abrir navegador
    # 2. Fazer login
    # 3. Navegar para página de upload
    # 4. Selecionar arquivo
    # 5. Preencher descrição
    # 6. Publicar 