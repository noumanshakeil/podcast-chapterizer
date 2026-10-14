import pytest

@pytest.mark.asyncio
async def test_chapterize(client):
    body = {
        "title": "Ep 1",
        "duration_sec": 600,
        "transcript": (
            "Welcome to the show we discuss shipping AI products.\n\n"
            "Next we cover evaluation harnesses and regression suites.\n\n"
            "Finally we talk about on-call for LLM systems and guardrails."
        ),
    }
    ep = await client.post("/api/episodes", json=body)
    eid = ep.json()["id"]
    r = await client.post(f"/api/episodes/{eid}/chapterize")
    assert r.status_code == 200
    assert r.json()["chapters"] >= 1
    toc = await client.get(f"/api/episodes/{eid}/toc")
    assert "markdown" in toc.json()
