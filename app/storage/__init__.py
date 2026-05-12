from .base import LocalStorage, S3Storage, StorageProvider

def get_default_provider() -> StorageProvider:
    """Acts as the injection factory defaulting to local until cloud configured."""
    return LocalStorage()
