from pydantic import BaseModel


class IngestRequest(BaseModel):
    video_url: str


class IngestResponse(BaseModel):
    video_id: str
    status: str
    frames: int


class SourceItem(BaseModel):
    type: str
    time: str
    text: str | None = None
    path: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
