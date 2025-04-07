import argparse
import os
from dotenv import load_dotenv
from downloader import download_videos
from transcriber import transcribe_videos
from editor import edit_videos
from uploader import upload_videos
from utils import setup_logging, load_config

def main():
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(description='Automatizador de Vídeos para Redes Sociais')
    parser.add_argument('--input', required=True, help='Arquivo com URLs dos vídeos')
    parser.add_argument('--skip-download', action='store_true', help='Pular etapa de download')
    parser.add_argument('--skip-transcribe', action='store_true', help='Pular etapa de transcrição')
    parser.add_argument('--skip-edit', action='store_true', help='Pular etapa de edição')
    parser.add_argument('--skip-upload', action='store_true', help='Pular etapa de upload')
    args = parser.parse_args()

    # Configura logging
    logger = setup_logging()
    logger.info("Iniciando processo de automação de vídeos")

    # Carrega configurações
    config = load_config()

    try:
        # Download dos vídeos
        if not args.skip_download:
            logger.info("Iniciando download dos vídeos")
            download_videos(args.input, config)
        
        # Transcrição dos vídeos
        if not args.skip_transcribe:
            logger.info("Iniciando transcrição dos vídeos")
            transcribe_videos(config)
        
        # Edição dos vídeos
        if not args.skip_edit:
            logger.info("Iniciando edição dos vídeos")
            edit_videos(config)
        
        # Upload dos vídeos
        if not args.skip_upload:
            logger.info("Iniciando upload dos vídeos")
            upload_videos(config)
        
        logger.info("Processo concluído com sucesso!")
    
    except Exception as e:
        logger.error(f"Erro durante o processo: {str(e)}")
        raise

if __name__ == "__main__":
    main() 