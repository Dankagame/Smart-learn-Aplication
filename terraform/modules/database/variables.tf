variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "subnet_ids" {
  description = "Private subnets the database can be placed in"
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "RDS needs at least two subnets in different availability zones."
  }
}

variable "security_group_id" {
  description = "Security group attached to the database"
  type        = string
}

variable "engine_version" {
  description = "Major Postgres version"
  type        = string
  default     = "16"
}

variable "instance_class" {
  description = "RDS instance size"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Name of the application database"
  type        = string
  default     = "smartlearn_db"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "smartlearn"
}

variable "db_port" {
  description = "Port the database listens on"
  type        = number
  default     = 5432
}

variable "multi_az" {
  description = "Run a standby copy in a second availability zone"
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  description = "Days of automatic backups to keep"
  type        = number
  default     = 7

  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 35
    error_message = "backup_retention_days must be between 1 and 35 so backups stay enabled."
  }
}

variable "deletion_protection" {
  description = "Block terraform destroy from deleting the database"
  type        = bool
  default     = false
}

variable "final_snapshot" {
  description = "Take a snapshot when the database is deleted"
  type        = bool
  default     = false
}

variable "kms_key_arn" {
  description = "KMS key used to encrypt the SSM secrets"
  type        = string
}
