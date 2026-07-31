"""Test storage configuration module."""
from src.config.storage import FirestoreStorageConfig, StorageConfig


def test_storage_config_defaults():
    """Test default storage configuration values."""
    config = StorageConfig()
    assert config.firestore.project_id == ""
    assert config.firestore.database == ""


def test_storage_config_custom_values():
    """Test storage configuration with custom values."""
    config = StorageConfig(firestore=FirestoreStorageConfig(project_id="my-project", database="my-database"))
    assert config.firestore.project_id == "my-project"
    assert config.firestore.database == "my-database"
