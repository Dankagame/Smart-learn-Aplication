variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "repositories" {
  description = "Short names of the image repositories to create"
  type        = list(string)
  default     = ["backend", "frontend"]
}

variable "keep_image_count" {
  description = "Number of images kept per repository, older ones are deleted"
  type        = number
  default     = 20

  validation {
    condition     = var.keep_image_count >= 5
    error_message = "keep_image_count must be at least 5 so there are always images to roll back to."
  }
}

variable "untagged_expiry_days" {
  description = "Days before untagged images are deleted"
  type        = number
  default     = 7
}

variable "force_delete" {
  description = "Allow terraform destroy to delete repositories that still hold images"
  type        = bool
  default     = true
}
