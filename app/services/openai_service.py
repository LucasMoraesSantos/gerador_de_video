from openai import OpenAI

from app.config import settings


class OpenAIService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError('OPENAI_API_KEY não configurada.')
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_script(self, title: str, description: str, hashtags: str, language: str) -> dict[str, str]:
        prompt = f'''Você é um roteirista de vídeos curtos.
Gere roteiro completo em {language} baseado no vídeo referência.

Título referência: {title}
Descrição referência: {description}
Hashtags: {hashtags}

Retorne no formato:
SEO_TITLE:\n...
SEO_DESCRIPTION:\n...
SCRIPT:\n...'''

        response = self.client.responses.create(
            model=settings.openai_model,
            input=prompt,
            temperature=0.7,
        )
        text = response.output_text

        return {
            'raw': text,
            'seo_title': _extract_block(text, 'SEO_TITLE:'),
            'seo_description': _extract_block(text, 'SEO_DESCRIPTION:'),
            'script': _extract_block(text, 'SCRIPT:'),
        }

    def generate_tts(self, text: str, voice: str, output_path: str) -> str:
        with self.client.audio.speech.with_streaming_response.create(
            model=settings.openai_tts_model,
            voice=voice,
            input=text,
        ) as resp:
            resp.stream_to_file(output_path)
        return output_path


def _extract_block(text: str, marker: str) -> str:
    idx = text.find(marker)
    if idx < 0:
        return ''
    return text[idx + len(marker):].strip().split('\n\n')[0].strip()
