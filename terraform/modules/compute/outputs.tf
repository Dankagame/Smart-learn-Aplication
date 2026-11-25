output "instance_id" {
  description = "Instance ID of the app server"
  value       = aws_instance.web.id
}

output "private_ip" {
  description = "Private IP of the app server"
  value       = aws_instance.web.private_ip
}

output "role_name" {
  description = "IAM role attached to the app server"
  value       = aws_iam_role.app.name
}

output "log_group_name" {
  description = "CloudWatch log group for the app containers"
  value       = aws_cloudwatch_log_group.app.name
}
