"""Storage configuration module."""
from pydantic import BaseModel


class FirestoreStorageConfig(BaseModel):
    """Firestore configuration."""

    project_id: str = ""
    database: str = "(default)"


class StorageConfig(BaseModel):
    """Storage configuration."""

    firestore: FirestoreStorageConfig = FirestoreStorageConfig()
