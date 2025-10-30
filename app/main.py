from typing import Optional

import uvicorn
from config.settings import settings
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from schema import ChatResponse, IngestRequest, IngestResponse
from src import ChatService, IngestService

app = FastAPI(title=settings.APP_NAME)

# Global services
ingest_service = IngestService()
chat_service = ChatService()


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME}", "debug": settings.DEBUG}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest_video(request: IngestRequest):
    try:
        result = ingest_service.ingest(request.video_url)
        video_id = result["video_id"]
        return IngestResponse(
            video_id=video_id, status="ingested", frames=len(result.get("frames", []))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(
    video_id: str = Form(...),
    query: str = Form(...),
    image: Optional[UploadFile] = File(None),
):

    image_bytes = await image.read() if image else None
    response = chat_service.chat(
        video_id=video_id, query=query, image_bytes=image_bytes
    )

    return ChatResponse(**response)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.CHAT_APP_PORT,
    )
