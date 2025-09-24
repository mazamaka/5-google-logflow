from __future__ import annotations

import io
import json
from functools import lru_cache
from typing import Any

from minio import Minio
from starlette.concurrency import run_in_threadpool

from app.core.config import settings


class MinioService:
    def __init__(self) -> None:
        endpoint = settings.minio_endpoint_effective
        self._bucket = settings.minio_bucket
        self._client = Minio(
            endpoint=endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=bool(settings.minio_secure),
        )

    @property
    def bucket(self) -> str:
        return self._bucket

    def ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    async def ensure_bucket_async(self) -> None:
        await run_in_threadpool(self.ensure_bucket)

    def upload_json(self, object_name: str, data: dict[str, Any]) -> str:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        stream = io.BytesIO(raw)
        self._client.put_object(
            bucket_name=self._bucket,
            object_name=object_name,
            data=stream,
            length=len(raw),
            content_type="application/json",
        )
        return object_name

    async def upload_json_async(self, object_name: str, data: dict[str, Any]) -> str:
        return await run_in_threadpool(self.upload_json, object_name, data)


@lru_cache(maxsize=1)
def get_minio_service() -> MinioService:
    return MinioService()
