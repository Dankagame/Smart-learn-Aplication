output "public_ip" {
  description = "Public IP of the server"
  value       = aws_instance.web.public_ip
}

output "public_dns" {
  description = "Public DNS name of the server"
  value       = aws_instance.web.public_dns
}
