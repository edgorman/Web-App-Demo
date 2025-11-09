terraform {
  required_version = "1.13.5"

  backend "gcs" {
    bucket = ""
  }
}
