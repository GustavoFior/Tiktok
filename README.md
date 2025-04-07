# Automatizador de Vídeos para Redes Sociais

Este projeto automatiza o processo de download, transcrição, edição e upload de vídeos para plataformas como TikTok e YouTube Shorts.

## 🚀 Funcionalidades

- Download automático de vídeos de múltiplas fontes
- Transcrição de áudio para texto
- Identificação de cortes inteligentes
- Edição automática para formatos de redes sociais
- Upload automatizado com legendas

## 📋 Pré-requisitos

- Python 3.8 ou superior
- FFmpeg instalado no sistema
- Contas nas plataformas de destino (YouTube, TikTok)

## 🔧 Instalação

1. Clone o repositório:

```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DO_REPOSITORIO]
```

2. Crie um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Instale o modelo do spaCy:

```bash
python -m spacy download pt_core_news_sm
```

5. Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais.

## 📁 Estrutura do Projeto

```
.
├── src/
│   ├── downloader.py      # Download de vídeos
│   ├── transcriber.py     # Transcrição de áudio
│   ├── editor.py          # Edição de vídeos
│   ├── uploader.py        # Upload para plataformas
│   └── utils.py           # Funções auxiliares
├── videos/
│   ├── originals/         # Vídeos baixados
│   ├── transcripts/       # Transcrições
│   └── final/            # Vídeos editados
├── .env                   # Configurações
├── requirements.txt       # Dependências
└── README.md             # Documentação
```

## 🎯 Como Usar

1. Prepare um arquivo `urls.txt` com as URLs dos vídeos:

```
https://youtube.com/watch?v=...
https://vimeo.com/...
```

2. Execute o pipeline completo:

```bash
python src/main.py --input urls.txt
```

3. Ou execute etapas específicas:

```bash
python src/downloader.py --input urls.txt
python src/transcriber.py
python src/editor.py
python src/uploader.py
```

## ⚙️ Configuração

Edite o arquivo `.env` com suas configurações:

```env
YOUTUBE_API_KEY=seu_api_key
YOUTUBE_CLIENT_ID=seu_client_id
YOUTUBE_CLIENT_SECRET=seu_client_secret
TIKTOK_USERNAME=seu_usuario
TIKTOK_PASSWORD=sua_senha
```

## 📝 Licença

Este projeto está sob a licença MIT.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição antes de enviar um pull request.
