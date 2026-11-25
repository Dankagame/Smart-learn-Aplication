variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid CIDR block, for example 10.0.0.0/16."
  }
}

variable "availability_zones" {
  description = "Exact availability zones to spread subnets across"
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) >= 2 && length(var.availability_zones) <= 3
    error_message = "Use 2 or 3 availability zones, because the load balancer and RDS need at least two."
  }
}

variable "kms_key_arn" {
  description = "KMS key used to encrypt the flow log group"
  type        = string
}

variable "log_retention_days" {
  description = "How long VPC flow logs are kept"
  type        = number
  default     = 365
}
