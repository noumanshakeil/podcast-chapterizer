# Dev server for podcast-chapterizer
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
