from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ChannelConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    niche: str
    youtube_api_key: str
    youtube_channel_id: str
    upload_enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ViralCandidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_config_id: int
    video_id: str
    title: str
    description: str
    hashtags: str
    views: int
    likes: int
    comments: int
    engagement_score: float
    niche: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class ScriptJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: int
    language: str = 'pt-BR'
    voice: str = 'alloy'
    script_text: str
    seo_title: str
    seo_description: str
    status: str = 'draft'
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PublishJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    script_job_id: int
    scheduled_at: datetime
    status: str = 'scheduled'
    youtube_video_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
