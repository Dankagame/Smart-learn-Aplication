variable "region" {
  description = "AWS region where all resources are created"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
  default     = "smartlearn"
}

variable "my_ip" {
  description = "Your public IP in CIDR form, allowed to SSH into the server"
  type        = string

}

variable "public_key_path" {
  description = "Path to the SSH public key uploaded to AWS"
  type        = string
  default     = "~/.ssh/smartlearn-key.pub"

}

variable "instance_type" {
  description = "EC2 instance size"
  type        = string
  default     = "t3.micro"
}