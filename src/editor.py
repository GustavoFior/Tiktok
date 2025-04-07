import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings
from utils import setup_logging, load_config
import logging

# Configura o caminho do ImageMagick
imagemagick_paths = [
    r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe",
    r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe",
    r"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe",
    r"C:\Program Files\ImageMagick-7.1.0-Q16\magick.exe",
    r"C:\Program Files\ImageMagick-7.0.11-Q16-HDRI\magick.exe",
    r"C:\Program Files\ImageMagick-7.0.11-Q16\magick.exe"
]

for path in imagemagick_paths:
    if os.path.exists(path):
        change_settings({"IMAGEMAGICK_BINARY": path})
        break

logger = setup_logging()

def add_subtitles(video_clip, srt_path, config):
    """Adiciona legendas ao vídeo"""
    try:
        # Carrega as legendas
        subs = SubtitlesClip(srt_path, 
                           make_textclip=lambda txt: TextClip(
                               txt,
                               font='Arial-Bold',
                               fontsize=16,
                               color='white',
                               stroke_color='black',
                               stroke_width=1.5,
                               method='caption',
                               size=(video_clip.w * 0.7, None),
                               align='center',
                               bg_color='rgba(0,0,0,0.7)'
                           ))
        
        # Posiciona as legendas na parte inferior do vídeo
        subs = subs.set_position(('center', 'bottom'))
        
        # Combina o vídeo com as legendas
        final = CompositeVideoClip([video_clip, subs])
        
        return final
    except Exception as e:
        logger.error(f"Erro ao adicionar legendas: {str(e)}")
        return video_clip

def edit_videos(config):
    """Edita os vídeos baixados"""
    logger.info("Iniciando edição dos vídeos")
    
    # Diretório dos vídeos originais
    input_dir = config["paths"]["input_dir"]
    final_dir = config["paths"]["final_dir"]
    os.makedirs(final_dir, exist_ok=True)
    
    # Processa cada vídeo
    for filename in os.listdir(input_dir):
        if filename.endswith(".mp4"):
            video_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            srt_path = os.path.join(input_dir, f"{base_name}.srt")
            
            if not os.path.exists(srt_path):
                logger.warning(f"Arquivo de legendas não encontrado para {filename}")
                continue
                
            try:
                # Carrega o vídeo
                video = VideoFileClip(video_path)
                
                # Adiciona as legendas
                video = add_subtitles(video, srt_path, config)
                
                # Salva o vídeo editado
                output_path = os.path.join(final_dir, f"{base_name}_editado.mp4")
                video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                
                logger.info(f"Vídeo editado salvo em: {output_path}")
                
            except Exception as e:
                logger.error(f"Erro ao editar {filename}: {str(e)}")
                continue 