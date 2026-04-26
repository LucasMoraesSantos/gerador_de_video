from datetime import datetime
from pydantic import BaseModel


class ChannelCreate(BaseModel):
    name: str
    niche: str
    youtube_api_key: str
    youtube_channel_id: str
    upload_enabled: bool = False


class AnalyzeRequest(BaseModel):
    channel_config_id: int
    max_results: int = 15


class ScriptRequest(BaseModel):
    candidate_id: int
    language: str = 'pt-BR'
    voice: str = 'alloy'


class ApproveRequest(BaseModel):
    script_job_id: int


class ScheduleRequest(BaseModel):
    script_job_id: int
    scheduled_at: datetime
