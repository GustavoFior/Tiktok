import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from slugify import slugify

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_config():
    """Carrega as configurações do arquivo .env"""
    load_dotenv()
    
    config = {
        "youtube": {
            "api_key": os.getenv("YOUTUBE_API_KEY"),
            "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET")
        },
        "tiktok": {
            "username": os.getenv("TIKTOK_USERNAME"),
            "password": os.getenv("TIKTOK_PASSWORD")
        },
        "paths": {
            "input_dir": os.getenv("PATHS_INPUT_DIR", "./videos/originals"),
            "transcript_dir": os.getenv("PATHS_TRANSCRIPT_DIR", "./videos/transcripts"),
            "final_dir": os.getenv("PATHS_FINAL_DIR", "./videos/final")
        },
        "transcription": {
            "model": os.getenv("WHISPER_MODEL", "base"),
            "language": os.getenv("LANGUAGE", "pt")
        },
        "upload": {
            "default_title": os.getenv("DEFAULT_TITLE", "Vídeo Automático"),
            "default_description": os.getenv("DEFAULT_DESCRIPTION", "Vídeo processado automaticamente"),
            "default_tags": os.getenv("DEFAULT_TAGS", "automacao,video,shorts").split(",")
        }
    }
    
    return config

def save_transcript(video_path, transcript_data):
    """Salva a transcrição em formato JSON"""
    video_name = Path(video_path).stem
    transcript_path = Path(os.getenv('TRANSCRIPTS_DIR', './videos/transcripts')) / f"{video_name}.json"
    
    with open(transcript_path, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=2)
    
    return transcript_path

def load_transcript(video_path):
    """Carrega a transcrição de um vídeo"""
    video_name = Path(video_path).stem
    transcript_path = Path(os.getenv('TRANSCRIPTS_DIR', './videos/transcripts')) / f"{video_name}.json"
    
    if not transcript_path.exists():
        return None
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_safe_filename(title):
    """Gera um nome de arquivo seguro a partir do título"""
    # Remove caracteres inválidos e espaços extras
    safe_name = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
    # Substitui espaços por underscores
    safe_name = safe_name.replace(' ', '_')
    # Adiciona extensão .mp4
    return safe_name + '.mp4'

def get_video_duration(video_path):
    """Obtém a duração do vídeo em segundos"""
    import cv2
    video = cv2.VideoCapture(str(video_path))
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    video.release()
    return duration 