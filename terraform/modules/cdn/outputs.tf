output "domain_name" {
  description = "CloudFront domain name"
  value       = aws_cloudfront_distribution.app.domain_name
}

output "url" {
  description = "HTTPS URL of the app"
  value       = "https://${aws_cloudfront_distribution.app.domain_name}"
}

output "distribution_id" {
  description = "CloudFront distribution ID, used for cache invalidation"
  value       = aws_cloudfront_distribution.app.id
}
