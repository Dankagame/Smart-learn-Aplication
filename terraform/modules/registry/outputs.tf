output "repository_urls" {
  description = "Map of short name to full ECR repository URL"
  value       = { for name, repo in aws_ecr_repository.this : name => repo.repository_url }
}

output "repository_arns" {
  description = "ARNs of the ECR repositories, used to scope push permissions"
  value       = [for repo in aws_ecr_repository.this : repo.arn]
}

output "registry_url" {
  description = "Registry hostname used for docker login"
  value       = split("/", values(aws_ecr_repository.this)[0].repository_url)[0]
}
