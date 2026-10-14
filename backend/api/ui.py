from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import chapters as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, episode_id: str | None = None, db: AsyncSession = Depends(get_db)):
    eps = await svc.list_episodes(db)
    eid = episode_id or (eps[0].id if eps else None)
    chapters = await svc.list_chapters(db, eid) if eid else []
    toc = await svc.export_toc(db, eid) if eid else ""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Podcast Chapterizer", "episodes": eps, "episode_id": eid, "chapters": chapters, "toc": toc},
    )

@router.post("/ui/episodes")
async def ui_ep(title: str = Form(...), transcript: str = Form(...), duration_sec: int = Form(600), db: AsyncSession = Depends(get_db)):
    e = await svc.add_episode(db, title, transcript, duration_sec)
    return RedirectResponse(f"/?episode_id={e.id}", status_code=303)

@router.post("/ui/chapterize")
async def ui_ch(episode_id: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.chapterize(db, episode_id)
    return RedirectResponse(f"/?episode_id={episode_id}", status_code=303)
