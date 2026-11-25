variable "project_name" {
  description = "Name used in tags for all resources"
  type        = string
}

variable "github_repository" {
  description = "GitHub repository allowed to deploy, in owner/name form"
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_repository))
    error_message = "github_repository must look like owner/name."
  }
}

variable "deploy_branch" {
  description = "Only workflows running on this branch may assume the deploy role"
  type        = string
  default     = "main"
}

variable "deploy_environment" {
  description = "GitHub environment name that may assume the deploy role"
  type        = string
  default     = "production"
}

variable "ecr_repository_arns" {
  description = "ECR repositories the pipeline may push to"
  type        = list(string)
}

variable "bastion_security_group_id" {
  description = "Bastion security group the pipeline may open briefly for its runner IP"
  type        = string
}
