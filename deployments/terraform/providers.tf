provider "google" {
  credentials = var.g_keys_json
  project     = var.project_id
  region      = var.region
}
