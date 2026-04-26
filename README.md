# Gerador de Vídeos (YouTube Workflow)

Aplicação self-hosted para:

- monitorar vídeos virais por nicho;
- rankear oportunidades por engajamento;
- analisar título, descrição, hashtags e comentários;
- gerar roteiro multilíngue com OpenAI;
- sintetizar narração com seleção de voz;
- montar vídeo vertical com legenda estilo shorts/tiktok;
- gerar variações de capa;
- aprovar manualmente, agendar e postar automaticamente no YouTube;
- armazenar ativos no Google Drive e registrar planilha no Google Sheets;
- operar múltiplos canais/chaves de API.

## Stack

- **Backend:** FastAPI + APScheduler + SQLite
- **Frontend:** HTML + JS (servido pelo FastAPI)
- **Integrações:** YouTube Data API, YouTube Upload API, Google Drive API, Google Sheets API, OpenAI API
- **Renderização:** ffmpeg (via subprocess)

## Setup rápido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000

## Variáveis de ambiente

Veja `.env.example`.

## Observações importantes

1. A parte de publicação é **somente após aprovação** (estado `approved`).
2. O sistema aceita múltiplos canais (`/api/channels`) para rodar em paralelo por nicho.
3. A montagem final de vídeo usa comando ffmpeg configurável em `app/services/video_renderer.py`.
4. Sem credenciais reais, o sistema roda em modo de desenvolvimento com erros claros de configuração.
