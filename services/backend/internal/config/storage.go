package config

// FirestoreStorageConfig is the Firestore configuration.
type FirestoreStorageConfig struct {
	ProjectID string
	// Database empty means "let the Firestore client resolve its own default" (the literal
	// "(default)" database), which only exists for projects that provision one under
	// that name. Deployed environments always set this explicitly to
	// "<project-id>-database" (see infrastructure/env/gcp_firestore.tf).
	Database string
}

// StorageConfig is the storage configuration.
type StorageConfig struct {
	Firestore FirestoreStorageConfig
}

func defaultStorageConfig() StorageConfig {
	return StorageConfig{
		Firestore: FirestoreStorageConfig{
			ProjectID: "",
			Database:  "",
		},
	}
}

func (c *StorageConfig) load() {
	c.Firestore.ProjectID = envString("SERVICE__STORAGE__FIRESTORE__PROJECT_ID", c.Firestore.ProjectID)
	c.Firestore.Database = envString("SERVICE__STORAGE__FIRESTORE__DATABASE", c.Firestore.Database)
}
