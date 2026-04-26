from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    app_env: str = 'dev'
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    database_url: str = 'sqlite:///./gerador.db'

    openai_api_key: str = ''
    openai_model: str = 'gpt-4.1-mini'
    openai_tts_model: str = 'gpt-4o-mini-tts'

    youtube_client_secrets_file: str = './secrets/youtube_client_secrets.json'
    google_service_account_file: str = './secrets/google_service_account.json'
    google_drive_folder_id: str = ''
    google_sheets_id: str = ''

    ffmpeg_bin: str = 'ffmpeg'


settings = Settings()
