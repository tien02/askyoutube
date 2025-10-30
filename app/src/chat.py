from pathlib import Path

from config.settings import settings
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from utils.helpers import ts

from .storage import StorageManager

Settings.llm = Ollama(
    model=settings.OLLAMA_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    request_timeout=120,
    max_new_tokens=256,
    context_window=2048,
)
Settings.embed_model = HuggingFaceEmbedding(model_name=settings.TEXT_EMBED_MODEL)


class ChatService:
    @staticmethod
    def chat(video_id: str, query: str, image_bytes: bytes | None = None) -> dict:

        index_store = StorageManager.get_redis_index_store(f"index_{video_id}")
        text_vec = StorageManager.get_qdrant_vector_store(f"text_{video_id}", 384)
        img_vec = StorageManager.get_qdrant_vector_store(f"img_{video_id}", 512)

        storage_ctx = StorageContext.from_defaults(
            vector_store=text_vec,
            image_store=img_vec,
            index_store=index_store,
        )

        index = load_index_from_storage(
            storage_ctx, embed_model=Settings.embed_model, index_id=video_id
        )

        query_engine = index.as_query_engine(response_mode="compact")

        if image_bytes:
            tmp_path = f"/tmp/uploaded_{video_id}.jpg"
            with open(tmp_path, "wb") as f:
                f.write(image_bytes)

            response = query_engine.image_query(tmp_path, query)

            # clean up
            Path(tmp_path).unlink(missing_ok=True)
        else:
            response = query_engine.query(query)

        sources = []
        for node in response.source_nodes:
            m = node.node.metadata
            if m.get("type") == "text":
                sources.append(
                    {
                        "type": "text",
                        "time": f"{ts(m['start'])}–{ts(m['end'])}",
                        "text": node.node.text[:200],
                    }
                )
            else:
                sources.append(
                    {
                        "type": "image",
                        "time": ts(m["timestamp"]),
                        "path": node.node.image_url,
                    }
                )

        return {"answer": response.response, "sources": sources}
