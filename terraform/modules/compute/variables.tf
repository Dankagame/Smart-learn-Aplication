variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance size"
  type        = string
}

variable "public_key_path" {
  description = "Path to the SSH public key uploaded to AWS"
  type        = string
}

variable "subnet_id" {
  description = "Subnet where the server is placed"
  type        = string
}

variable "security_group_id" {
  description = "Security group attached to the server"
  type        = string
}
