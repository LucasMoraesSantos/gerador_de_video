from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlmodel import Session, select

from app.db import get_session, init_db, engine
from app.models import ChannelConfig, PublishJob, ScriptJob, ViralCandidate
from app.schemas import AnalyzeRequest, ApproveRequest, ChannelCreate, ScheduleRequest, ScriptRequest
from app.services.openai_service import OpenAIService
from app.services.scheduler_service import scheduler
from app.services.youtube_service import compute_engagement, fetch_viral_candidates

app = FastAPI(title='Gerador de Vídeo - Workflow')
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')


@app.on_event('startup')
def on_startup() -> None:
    init_db()
    if not scheduler.running:
        scheduler.start()


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post('/api/channels')
def create_channel(payload: ChannelCreate, session: Session = Depends(get_session)):
    channel = ChannelConfig.model_validate(payload)
    session.add(channel)
    session.commit()
    session.refresh(channel)
    return channel


@app.get('/api/channels')
def list_channels(session: Session = Depends(get_session)):
    return session.exec(select(ChannelConfig).order_by(ChannelConfig.created_at.desc())).all()


@app.post('/api/analyze')
def analyze(payload: AnalyzeRequest, session: Session = Depends(get_session)):
    channel = session.get(ChannelConfig, payload.channel_config_id)
    if not channel:
        raise HTTPException(status_code=404, detail='Canal não encontrado')

    raw = fetch_viral_candidates(channel.youtube_api_key, channel.youtube_channel_id, payload.max_results)
    created = []
    for item in raw:
        candidate = ViralCandidate(
            channel_config_id=channel.id,
            video_id=item['video_id'],
            title=item['title'],
            description=item['description'],
            hashtags=item['hashtags'],
            views=item['views'],
            likes=item['likes'],
            comments=item['comments'],
            engagement_score=compute_engagement(item),
            niche=channel.niche,
        )
        session.add(candidate)
        created.append(candidate)

    session.commit()
    return {'created': len(created)}


@app.get('/api/ranking/{niche}')
def ranking_by_niche(niche: str, session: Session = Depends(get_session)):
    stmt = (
        select(ViralCandidate)
        .where(ViralCandidate.niche == niche)
        .order_by(ViralCandidate.engagement_score.desc(), ViralCandidate.views.desc())
        .limit(30)
    )
    return session.exec(stmt).all()


@app.post('/api/script')
def generate_script(payload: ScriptRequest, session: Session = Depends(get_session)):
    candidate = session.get(ViralCandidate, payload.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail='Candidato não encontrado')

    service = OpenAIService()
    result = service.generate_script(
        title=candidate.title,
        description=candidate.description,
        hashtags=candidate.hashtags,
        language=payload.language,
    )

    job = ScriptJob(
        candidate_id=candidate.id,
        language=payload.language,
        voice=payload.voice,
        script_text=result['script'] or result['raw'],
        seo_title=result['seo_title'],
        seo_description=result['seo_description'],
        status='draft',
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@app.get('/api/scripts')
def list_scripts(session: Session = Depends(get_session)):
    return session.exec(select(ScriptJob).order_by(ScriptJob.created_at.desc())).all()


@app.post('/api/approve')
def approve_script(payload: ApproveRequest, session: Session = Depends(get_session)):
    job = session.get(ScriptJob, payload.script_job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Roteiro não encontrado')
    job.status = 'approved'
    session.add(job)
    session.commit()
    return {'ok': True}


def _publish(script_job_id: int):
    with Session(engine) as session:
        pub = session.exec(select(PublishJob).where(PublishJob.script_job_id == script_job_id)).first()
        if not pub:
            return
        pub.status = 'done'
        pub.youtube_video_id = f'mock-{script_job_id}-{int(datetime.utcnow().timestamp())}'
        session.add(pub)
        session.commit()


@app.post('/api/schedule')
def schedule(payload: ScheduleRequest, session: Session = Depends(get_session)):
    job = session.get(ScriptJob, payload.script_job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Roteiro não encontrado')
    if job.status != 'approved':
        raise HTTPException(status_code=400, detail='Aprovação necessária antes de agendar')

    pub = PublishJob(script_job_id=job.id, scheduled_at=payload.scheduled_at, status='scheduled')
    session.add(pub)
    session.commit()
    session.refresh(pub)

    scheduler.add_job(_publish, 'date', run_date=payload.scheduled_at, args=[job.id], id=f'publish-{pub.id}', replace_existing=True)
    return pub


@app.get('/api/publish-jobs')
def list_publish_jobs(session: Session = Depends(get_session)):
    return session.exec(select(PublishJob).order_by(PublishJob.created_at.desc())).all()


@app.get('/api/health')
def health():
    return {'status': 'ok', 'time': datetime.utcnow().isoformat()}
