variable "region" {
  description = "AWS region where all resources are created"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name used in resource names and tags"
  type        = string
  default     = "smartlearn"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.project_name))
    error_message = "project_name must be 3-21 lowercase letters, digits or dashes, starting with a letter."
  }
}

variable "environment" {
  description = "Environment name added as a tag to every resource"
  type        = string
  default     = "production"
}

variable "admin_cidrs" {
  description = "Public IPs in CIDR form allowed to SSH into the bastion, one per team member"
  type        = list(string)
}

variable "github_repository" {
  description = "GitHub repository allowed to deploy, in owner/name form"
  type        = string
  default     = "Dankagame/Smart-learn-Aplication"
}

variable "public_key_path" {
  description = "Path to the SSH public key uploaded to AWS"
  type        = string
  default     = "~/.ssh/smartlearn-key.pub"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Exact availability zones to use, at least two"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "app_port" {
  description = "Port the app server serves the website on"
  type        = number
  default     = 80
}

variable "enable_cdn" {
  description = "Put CloudFront in front of the load balancer to serve the app over HTTPS"
  type        = bool
  default     = false
}

variable "app_instance_type" {
  description = "EC2 size for the app server"
  type        = string
  default     = "t3.micro"
}

variable "bastion_instance_type" {
  description = "EC2 size for the bastion host"
  type        = string
  default     = "t3.micro"
}

variable "db_instance_class" {
  description = "RDS instance size"
  type        = string
  default     = "db.t3.micro"
}

variable "db_multi_az" {
  description = "Run a standby database in a second availability zone"
  type        = bool
  default     = false
}

variable "db_deletion_protection" {
  description = "Block terraform destroy from deleting the database"
  type        = bool
  default     = false
}
