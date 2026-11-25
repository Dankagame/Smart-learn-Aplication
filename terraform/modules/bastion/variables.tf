variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "ami_id" {
  description = "AMI used for the bastion host"
  type        = string
}

variable "instance_type" {
  description = "EC2 size for the bastion host"
  type        = string
  default     = "t3.micro"
}

variable "subnet_id" {
  description = "Public subnet where the bastion is placed"
  type        = string
}

variable "security_group_id" {
  description = "Security group attached to the bastion"
  type        = string
}

variable "key_name" {
  description = "Name of the AWS key pair used for SSH"
  type        = string
}
