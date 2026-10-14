from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import Chapter, Episode

async def add_episode(session: AsyncSession, title: str, transcript: str, duration_sec: int = 0) -> Episode:
    ep = Episode(
        id=uuid.uuid4().hex[:10],
        title=title.strip()[:200],
        transcript=transcript.strip(),
        duration_sec=max(0, int(duration_sec)),
    )
    session.add(ep)
    await session.commit()
    await session.refresh(ep)
    return ep

async def list_episodes(session: AsyncSession) -> list[Episode]:
    return list((await session.execute(select(Episode).order_by(Episode.created_at.desc()))).scalars())

async def list_chapters(session: AsyncSession, episode_id: str) -> list[Chapter]:
    return list(
        (
            await session.execute(
                select(Chapter).where(Chapter.episode_id == episode_id).order_by(Chapter.start_sec.asc())
            )
        ).scalars()
    )

async def chapterize(session: AsyncSession, episode_id: str) -> list[Chapter]:
    ep = await session.get(Episode, episode_id)
    if not ep:
        raise ValueError("not found")
    # Clear old chapters
    for old in await list_chapters(session, episode_id):
        await session.delete(old)
    await session.flush()
    paras = [p.strip() for p in ep.transcript.split("\n\n") if len(p.strip()) > 40]
    if not paras:
        paras = [ep.transcript[i : i + 280] for i in range(0, max(len(ep.transcript), 1), 280)][:8]
    llm = get_llm()
    created: list[Chapter] = []
    step = max(30, (ep.duration_sec or max(60, len(paras) * 45)) // max(len(paras), 1))
    for i, para in enumerate(paras[:10]):
        title = (await llm.complete(f"Chapter title for: {para[:180]}", system="Return a short title only.")).strip()
        title = title.split("\n")[0][:120] or f"Chapter {i + 1}"
        ch = Chapter(
            id=uuid.uuid4().hex[:12],
            episode_id=episode_id,
            title=title,
            start_sec=i * step,
            summary=para[:400],
        )
        session.add(ch)
        created.append(ch)
    await session.commit()
    return created

async def export_toc(session: AsyncSession, episode_id: str) -> str:
    ep = await session.get(Episode, episode_id)
    chapters = await list_chapters(session, episode_id)
    lines = [f"# {ep.title if ep else episode_id}", ""]
    for ch in chapters:
        m, s = divmod(ch.start_sec, 60)
        lines.append(f"- {m:02d}:{s:02d} {ch.title}")
    return "\n".join(lines)
