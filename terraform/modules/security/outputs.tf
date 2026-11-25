output "alb_sg_id" {
  description = "Security group for the load balancer"
  value       = aws_security_group.alb.id
}

output "bastion_sg_id" {
  description = "Security group for the bastion host"
  value       = aws_security_group.bastion.id
}

output "app_sg_id" {
  description = "Security group for the private app server"
  value       = aws_security_group.app.id
}

output "db_sg_id" {
  description = "Security group for the RDS database"
  value       = aws_security_group.db.id
}
