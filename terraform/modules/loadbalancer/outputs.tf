output "dns_name" {
  description = "Public DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "url" {
  description = "Public URL of the app"
  value       = "http://${aws_lb.main.dns_name}"
}

output "target_group_arn" {
  description = "ARN of the app target group, used to check target health"
  value       = aws_lb_target_group.app.arn
}

output "arn_suffix" {
  description = "ARN suffix of the load balancer, used for CloudWatch metrics"
  value       = aws_lb.main.arn_suffix
}
