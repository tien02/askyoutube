from pathlib import Path
from urllib.parse import quote

from config.settings import settings
from llama_index.core import Document, StorageContext
from llama_index.core.indices import MultiModalVectorStoreIndex
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.core.schema import ImageDocument
from llama_index.embeddings.clip import ClipEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from utils.helpers import download_video, extract_frames, get_transcript

from .storage import StorageManager


class IngestService:
    text_embed = HuggingFaceEmbedding(model_name=settings.TEXT_EMBED_MODEL)
    image_embed = ClipEmbedding(
        model_name=settings.IMAGE_EMBED_MODEL, device=settings.EMBED_DEVICE
    )
    frame_fps = settings.FRAME_FPS

    @classmethod
    def ingest(cls, video_url: str) -> dict:
        video_id = video_url.split("/watch?v=")[-1]

        # 1. Download + upload video
        local_vid, yt_id = download_video(video_url)
        StorageManager.upload(local_vid, f"videos/{video_id}.mp4")

        # 2. Extract + upload frames
        duration, frames_dir = extract_frames(
            local_vid, out_dir=f"/tmp/frames/{video_id}", fps=cls.frame_fps
        )
        frame_paths = sorted(Path(frames_dir).glob("frame*.png"))

        frame_urls = []
        for i, p in enumerate(frame_paths):
            object_name = f"frames/{video_id}/frame_{i:04d}.png"
            StorageManager.upload(str(p), object_name)
            url = cls._get_minio_url(object_name)
            frame_urls.append(url)

        # 3. Transcript
        segments = get_transcript(yt_id, local_video_path=local_vid)

        # 4. Documents
        text_docs = [
            Document(
                text=s["text"],
                metadata={"start": s["start"], "end": s["end"], "type": "text"},
            )
            for s in segments
        ]
        step = duration / len(frame_urls) if frame_urls else 0
        image_docs = [
            ImageDocument(
                image_url=url,
                metadata={
                    "timestamp": i * step,
                    "type": "image",
                    "minio_key": f"frames/{video_id}/frame_{i:04d}.png",
                },
            )
            for i, url in enumerate(frame_urls)
        ]
        all_docs = text_docs + image_docs

        # 5. Nodes
        parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[128, 512, 2048])
        nodes = parser.get_nodes_from_documents(all_docs)

        # 6. Vector stores
        text_vec = StorageManager.get_qdrant_vector_store(f"text_{video_id}", 384)
        img_vec = StorageManager.get_qdrant_vector_store(f"img_{video_id}", 512)

        # 7. Index store
        index_store = StorageManager.get_redis_index_store(f"index_{video_id}")

        # 8. Storage context
        storage_ctx = StorageContext.from_defaults(
            vector_store=text_vec,
            image_store=img_vec,
            index_store=index_store,
        )

        # 9. Build index
        index = MultiModalVectorStoreIndex(
            nodes,
            storage_context=storage_ctx,
            embed_model=cls.text_embed,
            image_embed_model=cls.image_embed,
        )

        index.set_index_id(video_id)

        return {
            "video_id": video_id,
        }

    @classmethod
    def _get_minio_url(cls, object_name: str) -> str:
        # Direct public URL (no auth needed)
        encoded = quote(object_name, safe="")
        return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{encoded}"
