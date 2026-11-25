variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC the target group belongs to"
  type        = string
}

variable "subnet_ids" {
  description = "Public subnets the load balancer is placed in"
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "An application load balancer needs at least two subnets in different availability zones."
  }
}

variable "security_group_id" {
  description = "Security group attached to the load balancer"
  type        = string
}

variable "instance_id" {
  description = "App server instance that receives traffic"
  type        = string
}

variable "app_port" {
  description = "Port the app server listens on"
  type        = number
  default     = 80
}

variable "health_check_path" {
  description = "Path the load balancer calls to decide if the app is healthy"
  type        = string
  default     = "/health"
}

variable "deletion_protection" {
  description = "Block terraform destroy from deleting the load balancer"
  type        = bool
  default     = false
}
