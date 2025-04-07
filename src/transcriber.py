import os
import whisper
from googletrans import Translator
from utils import setup_logging, load_config, generate_safe_filename
import logging
import json
import time

logger = logging.getLogger(__name__)

def transcribe_videos(config):
    """Transcreve os vídeos da pasta de origem para a pasta de transcrições."""
    input_dir = config["paths"]["input_dir"]
    transcript_dir = config["paths"]["transcript_dir"]
    os.makedirs(transcript_dir, exist_ok=True)
    
    # Carrega o modelo Whisper (usando o modelo medium para melhor qualidade)
    logger.info("Carregando modelo Whisper...")
    start_time = time.time()
    model = whisper.load_model("medium")
    logger.info(f"Modelo carregado em {time.time() - start_time:.2f} segundos")
    
    translator = Translator()
    
    for filename in os.listdir(input_dir):
        if filename.endswith((".mp4", ".avi", ".mov")):
            input_path = os.path.join(input_dir, filename)
            # Remove a extensão do arquivo para gerar o nome base
            base_filename = os.path.splitext(filename)[0]
            safe_filename = generate_safe_filename(base_filename)
            
            logger.info(f"Iniciando transcrição do vídeo: {filename}")
            
            try:
                # Primeiro, detecta a língua original
                logger.info("Carregando áudio...")
                audio = whisper.load_audio(input_path)
                audio = whisper.pad_or_trim(audio)
                mel = whisper.log_mel_spectrogram(audio).to(model.device)
                
                # Detecta a língua
                logger.info("Detectando língua...")
                _, probs = model.detect_language(mel)
                detected_lang = max(probs, key=probs.get)
                logger.info(f"Língua detectada: {detected_lang}")
                
                # Transcreve na língua original com segmentos
                logger.info("Iniciando transcrição...")
                options = whisper.DecodingOptions(
                    fp16=False,
                    language=detected_lang,
                    task="transcribe",
                    temperature=0.0,  # Menos criatividade, mais precisão
                    best_of=3,  # Tenta 3 vezes e pega o melhor resultado
                    beam_size=3  # Usa beam search para melhor qualidade
                )
                start_time = time.time()
                result = model.transcribe(input_path, **options.__dict__)
                logger.info(f"Transcrição concluída em {time.time() - start_time:.2f} segundos")
                
                # Salva a transcrição original com timing
                transcript_data = {
                    "language": detected_lang,
                    "segments": result["segments"],
                    "text": result["text"]
                }
                
                # Salva o arquivo JSON com a transcrição original
                json_path = os.path.join(transcript_dir, f"{safe_filename}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(transcript_data, f, ensure_ascii=False, indent=2)
                
                # Traduz cada segmento para português
                logger.info("Iniciando tradução...")
                translated_segments = []
                for i, segment in enumerate(result["segments"], 1):
                    text = segment["text"].strip()
                    if not text:  # Pula segmentos vazios
                        continue
                        
                    if detected_lang != 'pt':
                        try:
                            # Tenta traduzir o segmento
                            translated = translator.translate(
                                text, 
                                dest='pt',
                                src=detected_lang
                            )
                            translated_text = translated.text
                        except Exception as e:
                            logger.warning(f"Erro ao traduzir segmento: {str(e)}")
                            translated_text = text
                    else:
                        translated_text = text
                    
                    translated_segments.append({
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": translated_text
                    })
                    
                    if i % 10 == 0:  # Log a cada 10 segmentos
                        logger.info(f"Traduzidos {i} segmentos...")
                
                # Salva a transcrição traduzida em formato SRT
                logger.info("Salvando arquivo SRT...")
                srt_path = os.path.join(transcript_dir, f"{safe_filename}.srt")
                with open(srt_path, "w", encoding="utf-8") as f:
                    for i, segment in enumerate(translated_segments, 1):
                        start_time = format_time(segment["start"])
                        end_time = format_time(segment["end"])
                        f.write(f"{i}\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{segment['text']}\n\n")
                
                logger.info(f"Processo completo concluído para: {filename}")
                
            except Exception as e:
                logger.error(f"Erro ao transcrever vídeo {filename}: {str(e)}")
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