variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC the security groups belong to"
  type        = string
}

variable "admin_cidrs" {
  description = "Public IPs in CIDR form allowed to SSH into the bastion"
  type        = list(string)

  validation {
    condition     = length(var.admin_cidrs) > 0 && alltrue([for c in var.admin_cidrs : can(cidrhost(c, 0)) && c != "0.0.0.0/0"])
    error_message = "admin_cidrs needs at least one valid CIDR and must not contain 0.0.0.0/0."
  }
}

variable "app_port" {
  description = "Port the app server listens on behind the load balancer"
  type        = number
  default     = 80
}

variable "db_port" {
  description = "Port the database listens on"
  type        = number
  default     = 5432
}
