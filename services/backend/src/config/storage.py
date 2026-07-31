"""Storage configuration module."""
from pydantic import BaseModel


class FirestoreStorageConfig(BaseModel):
    """Firestore configuration."""

    project_id: str = ""
    # Empty means "let the Firestore client resolve its own default" (the literal
    # "(default)" database), which only exists for projects that provision one under
    # that name. Deployed environments always set this explicitly to
    # "<project-id>-database" (see infrastructure/env/gcp_firestore.tf).
    database: str = ""


class StorageConfig(BaseModel):
    """Storage configuration."""

    firestore: FirestoreStorageConfig = FirestoreStorageConfig()
