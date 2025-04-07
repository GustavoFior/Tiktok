import os
import yt_dlp
from pathlib import Path
from utils import setup_logging, generate_safe_filename

logger = setup_logging()

def download_videos(urls_file, config):
    """Download de vídeos a partir de um arquivo de URLs"""
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        try:
            logger.info(f"Iniciando download do vídeo: {url}")
            video_info = download_single_video(url, config)
            logger.info(f"Download concluído: {video_info['title']}")
        except Exception as e:
            logger.error(f"Erro ao baixar vídeo {url}: {str(e)}")
            continue

def download_single_video(url, config):
    """Download de um único vídeo"""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(config['originals_dir'], '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        # Adiciona headers para evitar bloqueio
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            # Garante que o arquivo final seja .mp4
            if not video_path.endswith('.mp4'):
                base_path = os.path.splitext(video_path)[0]
                new_path = base_path + '.mp4'
                if os.path.exists(video_path) and not os.path.exists(new_path):
                    os.rename(video_path, new_path)
                video_path = new_path
            
            return {
                'title': info.get('title', 'video_sem_titulo'),
                'path': video_path,
                'duration': info.get('duration', 0),
                'url': url
            }
        except Exception as e:
            logger.error(f"Erro durante o download: {str(e)}")
            raise

def get_video_info(url):
    """Obtém informações do vídeo sem fazer download"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'video_sem_titulo'),
                'duration': info.get('duration', 0),
                'url': url
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações do vídeo: {str(e)}")
            raise 