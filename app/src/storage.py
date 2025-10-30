import redis
from config.settings import settings
from llama_index.storage.index_store.redis import RedisIndexStore
from minio import Minio
from qdrant_client import QdrantClient


class StorageManager:
    # MinIO
    minio = Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )
    if not minio.bucket_exists(settings.MINIO_BUCKET):
        minio.make_bucket(settings.MINIO_BUCKET)
    bucket = settings.MINIO_BUCKET

    # Qdrant
    qdrant = QdrantClient(settings.QDRANT_URL)

    # Redis
    redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )

    @classmethod
    def upload(cls, local_path: str, object_name: str):
        cls.minio.fput_object(cls.bucket, object_name, local_path)

    @classmethod
    def get_qdrant_vector_store(cls, collection: str, dim: int):
        from llama_index.vector_stores.qdrant import QdrantVectorStore

        return QdrantVectorStore(client=cls.qdrant, collection_name=collection, dim=dim)

    @classmethod
    def get_redis_index_store(cls, namespace: str):
        return RedisIndexStore.from_host_and_port(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, namespace=namespace
        )
