output "role_arn" {
  description = "IAM role GitHub Actions assumes through OIDC"
  value       = aws_iam_role.github_deploy.arn
}
