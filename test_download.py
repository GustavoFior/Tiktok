from pytube import YouTube

def download_video(url, output_path):
    try:
        yt = YouTube(url)
        print(f"Baixando: {yt.title}")
        
        # Obtém a melhor resolução disponível
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not video:
            print("Não foi possível encontrar um stream adequado")
            return
        
        # Faz o download
        video.download(output_path=output_path)
        print(f"Download concluído: {yt.title}")
        
    except Exception as e:
        print(f"Erro: {str(e)}")

# URLs de teste
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0"
]

# Faz o download de cada vídeo
for url in urls:
    download_video(url, "videos/originals") 