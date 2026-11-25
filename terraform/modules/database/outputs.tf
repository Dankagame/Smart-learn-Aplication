output "endpoint" {
  description = "Hostname of the database"
  value       = aws_db_instance.main.address
}

output "port" {
  description = "Port of the database"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Name of the application database"
  value       = aws_db_instance.main.db_name
}

output "password_parameter_name" {
  description = "SSM parameter holding the database password"
  value       = aws_ssm_parameter.db_password.name
}

output "url_parameter_name" {
  description = "SSM parameter holding the full DATABASE_URL"
  value       = aws_ssm_parameter.database_url.name
}

output "parameter_arns" {
  description = "ARNs of the SSM parameters the app server may read"
  value       = [aws_ssm_parameter.db_password.arn, aws_ssm_parameter.database_url.arn]
}
