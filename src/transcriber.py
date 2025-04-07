import os
import whisper
from googletrans import Translator
from utils import setup_logging, load_config, generate_safe_filename
import logging
import json
import time
import srt
from datetime import timedelta
import re

logger = logging.getLogger(__name__)

def transcribe_videos(config):
    """Transcreve os vídeos baixados"""
    logger.info("Iniciando transcrição dos vídeos")
    
    # Carrega o modelo Whisper
    model = whisper.load_model(config["transcription"]["model"])
    
    # Diretório dos vídeos originais
    input_dir = config["paths"]["input_dir"]
    
    # Processa cada vídeo
    for filename in os.listdir(input_dir):
        if filename.endswith(".mp4"):
            video_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            
            logger.info(f"Transcrevendo vídeo: {filename}")
            
            try:
                # Primeiro, detecta a língua original
                logger.info("Detectando língua...")
                audio = whisper.load_audio(video_path)
                audio = whisper.pad_or_trim(audio)
                mel = whisper.log_mel_spectrogram(audio).to(model.device)
                _, probs = model.detect_language(mel)
                detected_lang = max(probs, key=probs.get)
                logger.info(f"Língua detectada: {detected_lang}")
                
                # Transcreve com word_timestamps para melhor precisão
                result = model.transcribe(
                    video_path,
                    task="transcribe",
                    language=detected_lang,
                    verbose=True,
                    initial_prompt="Este é um vídeo do YouTube. A transcrição deve começar quando o áudio começar. Não ignore o início do vídeo.",
                    word_timestamps=True,
                    condition_on_previous_text=False,
                    temperature=0.0,  # Menos criatividade, mais precisão
                    best_of=3,  # Tenta 3 vezes e pega o melhor resultado
                    beam_size=3,  # Usa beam search para melhor qualidade
                    no_speech_threshold=0.3  # Ajusta sensibilidade para detecção de fala
                )
                
                # Gera arquivo JSON com os segmentos
                json_path = os.path.join(input_dir, f"{base_name}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                # Gera arquivo SRT com legendas quebradas de forma inteligente
                srt_path = os.path.join(input_dir, f"{base_name}.srt")
                with open(srt_path, "w", encoding="utf-8") as f:
                    subtitle_index = 1
                    
                    for segment in result["segments"]:
                        text = segment["text"].strip()
                        words = text.split()
                        
                        # Lista de pontuações que indicam fim de frase
                        sentence_enders = ['.', '!', '?', '...', ';', ':']
                        
                        current_sentence = ""
                        current_start = segment["start"]
                        current_end = segment["end"]
                        
                        for i, word in enumerate(words):
                            current_sentence += word + " "
                            
                            # Verifica se a palavra atual termina com um marcador de fim de frase
                            # ou se é a última palavra do segmento
                            if (any(word.endswith(ender) for ender in sentence_enders) or 
                                i == len(words) - 1):
                                
                                # Formata o tempo no formato SRT
                                start = timedelta(seconds=current_start)
                                end = timedelta(seconds=current_end)
                                start_time = f"{start.seconds//3600:02d}:{(start.seconds//60)%60:02d}:{start.seconds%60:02d},{int(start.microseconds/1000):03d}"
                                end_time = f"{end.seconds//3600:02d}:{(end.seconds//60)%60:02d}:{end.seconds%60:02d},{int(end.microseconds/1000):03d}"
                                
                                f.write(f"{subtitle_index}\n{start_time} --> {end_time}\n{current_sentence.strip()}\n\n")
                                
                                # Reseta para próxima legenda
                                subtitle_index += 1
                                current_sentence = ""
                                current_start = current_end
                
                logger.info(f"Transcrição concluída para {filename}")
                
            except Exception as e:
                logger.error(f"Erro ao transcrever {filename}: {str(e)}")
                continue

def format_time(seconds):
    """Formata o tempo em segundos para o formato SRT (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def transcribe_single_video(video_path, model, config):
    """Transcreve um único vídeo"""
    result = model.transcribe(
        str(video_path),
        language=config['language'],
        verbose=False
    )
    
    # Formata a transcrição
    transcript = {
        'video_path': str(video_path),
        'segments': [],
        'text': result['text']
    }
    
    for segment in result['segments']:
        transcript['segments'].append({
            'start': format_timestamp(segment['start']),
            'end': format_timestamp(segment['end']),
            'text': segment['text'].strip()
        })
    
    return transcript

def format_timestamp(seconds):
    """Formata segundos em timestamp HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def find_keywords(transcript, keywords):
    """Encontra momentos importantes baseado em palavras-chave"""
    important_segments = []
    
    for segment in transcript['segments']:
        text = segment['text'].lower()
        for keyword in keywords:
            if keyword.lower() in text:
                important_segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'],
                    'keyword': keyword
                })
                break
    
    return important_segments 