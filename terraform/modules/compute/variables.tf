variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "ami_id" {
  description = "AMI used for the app server"
  type        = string
}

variable "instance_type" {
  description = "EC2 size for the app server"
  type        = string
}

variable "subnet_id" {
  description = "Private subnet where the app server is placed"
  type        = string
}

variable "security_group_id" {
  description = "Security group attached to the app server"
  type        = string
}

variable "key_name" {
  description = "Name of the AWS key pair used for SSH"
  type        = string
}

variable "ssm_parameter_arns" {
  description = "SSM parameters holding secrets the app server may read"
  type        = list(string)
}

variable "log_retention_days" {
  description = "How long container logs are kept in CloudWatch"
  type        = number
  default     = 365
}

variable "kms_key_arn" {
  description = "KMS key that encrypts the app logs and secrets"
  type        = string
}
