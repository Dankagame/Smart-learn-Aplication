output "key_arn" {
  description = "ARN of the customer managed KMS key"
  value       = aws_kms_key.main.arn
}
