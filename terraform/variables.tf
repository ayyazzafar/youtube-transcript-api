variable "project_id" {
  description = "The GCP project id"
  type        = string
}
variable "region" {
  default     = "us-central1"
  description = "GCP region"
  type        = string
}

variable "g_keys_json" {
  type = string
}
