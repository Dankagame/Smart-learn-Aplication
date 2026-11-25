locals {
  app_url = var.enable_cdn ? module.cdn[0].url : module.loadbalancer.url
}

output "app_url" {
  description = "Public URL of the SmartLearn app"
  value       = local.app_url
}

output "health_url" {
  description = "Public health check URL"
  value       = "${local.app_url}/health"
}

output "alb_url" {
  description = "Direct HTTP URL of the load balancer behind CloudFront"
  value       = module.loadbalancer.url
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID, used for cache invalidation"
  value       = var.enable_cdn ? module.cdn[0].distribution_id : null
}

output "bastion_public_ip" {
  description = "Static public IP of the bastion host"
  value       = module.bastion.public_ip
}

output "app_private_ip" {
  description = "Private IP of the app server"
  value       = module.compute.private_ip
}

output "ssh_bastion" {
  description = "Command to SSH into the bastion"
  value       = "ssh -i ~/.ssh/smartlearn-key ubuntu@${module.bastion.public_ip}"
}

output "ssh_app" {
  description = "Command to SSH into the private app server through the bastion"
  value       = "ssh -i ~/.ssh/smartlearn-key -J ubuntu@${module.bastion.public_ip} ubuntu@${module.compute.private_ip}"
}

output "ecr_registry" {
  description = "ECR registry hostname used for docker login"
  value       = module.registry.registry_url
}

output "ecr_repository_urls" {
  description = "ECR repository URLs for each image"
  value       = module.registry.repository_urls
}

output "db_endpoint" {
  description = "Hostname of the RDS database"
  value       = module.database.endpoint
}

output "db_url_parameter" {
  description = "SSM parameter holding DATABASE_URL"
  value       = module.database.url_parameter_name
}

output "app_log_group" {
  description = "CloudWatch log group for the app containers"
  value       = module.compute.log_group_name
}

output "github_actions_role_arn" {
  description = "IAM role the CD pipeline assumes through OIDC"
  value       = module.cicd.role_arn
}

output "bastion_security_group_id" {
  description = "Bastion security group the CD pipeline opens briefly for its runner"
  value       = module.security.bastion_sg_id
}

output "target_group_arn" {
  description = "Target group ARN, used to check app health"
  value       = module.loadbalancer.target_group_arn
}

output "aws_region" {
  description = "AWS region of the deployment"
  value       = var.region
}
