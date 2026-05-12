import abc
import json
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, Union
import pyarrow as pa
import pyarrow.parquet as pq

class StorageProvider(abc.ABC):
    """Contract specifying explicit decoupled access to persisted data blobs."""
    
    @abc.abstractmethod
    def read_json(self, path: str) -> Any:
        pass

    @abc.abstractmethod
    def write_json(self, path: str, payload: Any) -> str:
        pass

    @abc.abstractmethod
    def write_parquet(self, path: str, table: pa.Table) -> str:
        pass

class LocalStorage(StorageProvider):
    def read_json(self, path: str) -> Any:
        target = Path(path)
        if not target.exists():
            return None
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_json(self, path: str, payload: Any) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return str(target.absolute())

    def write_parquet(self, path: str, table: pa.Table) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, str(target))
        return str(target.absolute())

class S3Storage(StorageProvider):
    """Rigid robust industry-grade S3 interaction plane empowering cloud scaling."""
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        import boto3
        self.s3 = boto3.client("s3", region_name=region)
        self.bucket = bucket_name

    def read_json(self, path: str) -> Any:
        try:
            resp = self.s3.get_object(Bucket=self.bucket, Key=path)
            return json.loads(resp['Body'].read().decode('utf-8'))
        except Exception as e:
            print(f"S3 Read Failure: {e}")
            return None

    def write_json(self, path: str, payload: Any) -> str:
        content = json.dumps(payload, indent=2, ensure_ascii=False)
        self.s3.put_object(Bucket=self.bucket, Key=path, Body=content, ContentType='application/json')
        return f"s3://{self.bucket}/{path}"

    def write_parquet(self, path: str, table: pa.Table) -> str:
        import io
        buffer = io.BytesIO()
        pq.write_table(table, buffer)
        self.s3.put_object(Bucket=self.bucket, Key=path, Body=buffer.getvalue())
        return f"s3://{self.bucket}/{path}"

    def list_objects(self, prefix: str) -> list[str]:
        resp = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj['Key'] for obj in resp.get('Contents', [])]
