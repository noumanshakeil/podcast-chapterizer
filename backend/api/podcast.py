from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import chapters as svc

class EpisodeIn(BaseModel):
    title: str = Field(min_length=2)
    transcript: str = Field(min_length=40)
    duration_sec: int = 0

router = APIRouter()

@router.get("/episodes")
async def episodes(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_episodes(db)
    return {"episodes": [{"id": e.id, "title": e.title, "duration_sec": e.duration_sec} for e in rows]}

@router.post("/episodes")
async def create(payload: EpisodeIn, db: AsyncSession = Depends(get_db)):
    e = await svc.add_episode(db, payload.title, payload.transcript, payload.duration_sec)
    return {"id": e.id}

@router.post("/episodes/{episode_id}/chapterize")
async def chapterize(episode_id: str, db: AsyncSession = Depends(get_db)):
    try:
        rows = await svc.chapterize(db, episode_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"chapters": len(rows)}

@router.get("/episodes/{episode_id}/chapters")
async def chapters(episode_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_chapters(db, episode_id)
    return {"chapters": [{"id": c.id, "title": c.title, "start_sec": c.start_sec, "summary": c.summary[:200]} for c in rows]}

@router.get("/episodes/{episode_id}/toc")
async def toc(episode_id: str, db: AsyncSession = Depends(get_db)):
    return {"markdown": await svc.export_toc(db, episode_id)}
