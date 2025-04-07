import os
import re
import subprocess
from pathlib import Path
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings
from utils import load_config, generate_safe_filename, setup_logging, load_transcript, get_video_duration
import logging

# Configuração do FFmpeg
change_settings({"FFMPEG_BINARY": os.getenv("FFMPEG_PATH", "ffmpeg")})

# Configuração do logging
logger = logging.getLogger(__name__)

def check_imagemagick():
    """Verifica se o ImageMagick está instalado e acessível"""
    try:
        # Tenta executar o comando convert do ImageMagick
        result = subprocess.run(['convert', '--version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            logger.info("ImageMagick encontrado:")
            logger.info(result.stdout.split('\n')[0])
            return True
    except FileNotFoundError:
        logger.error("ImageMagick não encontrado no PATH")
        logger.info("Por favor, verifique se o ImageMagick está instalado e adicionado ao PATH do sistema")
        return False

def find_keywords(text, keywords):
    """Encontra palavras-chave no texto e retorna suas posições."""
    matches = []
    for keyword in keywords:
        for match in re.finditer(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            matches.append((match.start(), match.end()))
    return matches

def edit_videos(config):
    """Edita os vídeos transcritos adicionando legendas e efeitos."""
    # Verifica o ImageMagick antes de começar
    if not check_imagemagick():
        logger.error("ImageMagick não encontrado. O processo não pode continuar.")
        return
    
    input_dir = config["paths"]["input_dir"]
    transcript_dir = config["paths"]["transcript_dir"]
    final_dir = config["paths"]["final_dir"]
    os.makedirs(final_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith((".mp4", ".avi", ".mov")):
            input_path = os.path.join(input_dir, filename)
            # Remove a extensão do arquivo para gerar o nome base
            base_filename = os.path.splitext(filename)[0]
            safe_filename = generate_safe_filename(base_filename)
            output_path = os.path.join(final_dir, f"{safe_filename}.mp4")
            
            # Verifica se existe o arquivo SRT correspondente
            srt_path = os.path.join(transcript_dir, f"{safe_filename}.srt")
            
            if not os.path.exists(srt_path):
                logger.warning(f"Nenhuma transcrição SRT encontrada para {filename}")
                continue
            
            logger.info(f"Iniciando edição do vídeo: {filename}")
            
            try:
                # Carrega o vídeo
                logger.info("Carregando vídeo...")
                video = VideoFileClip(input_path)
                logger.info(f"Vídeo carregado. Duração: {video.duration:.2f} segundos")
                
                # Cria o gerador de legendas a partir do arquivo SRT
                def make_text(txt):
                    return TextClip(txt, fontsize=24, color='white', 
                                  font='Arial', stroke_color='black', 
                                  stroke_width=1)
                
                # Carrega as legendas do arquivo SRT
                logger.info("Carregando legendas...")
                subtitles = SubtitlesClip(srt_path, make_text)
                subtitles = subtitles.set_position(('center', 'bottom'))
                logger.info("Legendas carregadas com sucesso")
                
                # Combina o vídeo com as legendas
                logger.info("Combinando vídeo com legendas...")
                final_video = CompositeVideoClip([video, subtitles])
                
                # Salva o vídeo final
                logger.info("Salvando vídeo final...")
                final_video.write_videofile(output_path, codec='libx264', 
                                          audio_codec='aac')
                
                logger.info(f"Edição concluída: {filename}")
                
            except Exception as e:
                logger.error(f"Erro ao editar vídeo {filename}: {str(e)}")
                continue

def edit_single_video(video_path, config):
    """Edita um único vídeo"""
    # Carrega o vídeo
    video = VideoFileClip(str(video_path))
    
    # Carrega a transcrição
    transcript = load_transcript(video_path)
    if not transcript:
        logger.warning(f"Transcrição não encontrada para {video_path.name}")
        return
    
    # Identifica segmentos importantes
    keywords = ['importante', 'dica', 'tutorial', 'como', 'passo a passo']
    important_segments = find_keywords(transcript, keywords)
    
    # Cria versões para diferentes plataformas
    create_tiktok_version(video, important_segments, config)
    create_youtube_shorts_version(video, important_segments, config)

def create_tiktok_version(video, segments, config):
    """Cria versão para TikTok"""
    # Configurações do TikTok
    target_duration = 60  # segundos
    target_ratio = 9/16  # proporção vertical
    
    # Corta o vídeo se necessário
    if video.duration > target_duration:
        video = video.subclip(0, target_duration)
    
    # Redimensiona para o formato vertical
    new_width = int(video.h * target_ratio)
    x_center = (video.w - new_width) // 2
    video = video.crop(x1=x_center, width=new_width)
    
    # Adiciona legendas
    if segments:
        clips = [video]
        for segment in segments:
            text_clip = TextClip(
                segment['text'],
                fontsize=24,
                color='white',
                bg_color='black',
                font='Arial',
                size=(video.w, None)
            ).set_position(('center', 'bottom')).set_duration(5)
            clips.append(text_clip)
        
        final = CompositeVideoClip(clips)
    else:
        final = video
    
    # Salva o vídeo
    output_path = Path(config['final_dir']) / f"{Path(video.filename).stem}_tiktok.mp4"
    final.write_videofile(
        str(output_path),
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )

def create_youtube_shorts_version(video, segments, config):
    """Cria versão para YouTube Shorts"""
    # Configurações do YouTube Shorts
    target_duration = 60  # segundos
    target_ratio = 9/16  # proporção vertical
    
    # Corta o vídeo se necessário
    if video.duration > target_duration:
        video = video.subclip(0, target_duration)
    
    # Redimensiona para o formato vertical
    new_width = int(video.h * target_ratio)
    x_center = (video.w - new_width) // 2
    video = video.crop(x1=x_center, width=new_width)
    
    # Adiciona legendas
    if segments:
        clips = [video]
        for segment in segments:
            text_clip = TextClip(
                segment['text'],
                fontsize=24,
                color='white',
                bg_color='black',
                font='Arial',
                size=(video.w, None)
            ).set_position(('center', 'bottom')).set_duration(5)
            clips.append(text_clip)
        
        final = CompositeVideoClip(clips)
    else:
        final = video
    
    # Salva o vídeo
    output_path = Path(config['final_dir']) / f"{Path(video.filename).stem}_shorts.mp4"
    final.write_videofile(
        str(output_path),
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    ) 