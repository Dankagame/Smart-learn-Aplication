variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "region" {
  description = "AWS region, used to pick the availability zone"
  type        = string
}

variable "my_ip" {
  description = "Your public IP in CIDR form, allowed to SSH into the server"
  type        = string
}
