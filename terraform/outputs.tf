output "instance_public_ip" {
  description = "Public IP of the SmartLearn server"
  value       = module.compute.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the SmartLearn server"
  value       = module.compute.public_dns
}

output "ssh_command" {
  description = "Command to SSH into the server"
  value       = "ssh -i ~/.ssh/smartlearn-key ubuntu@${module.compute.public_ip}"
}

output "app_url" {
  description = "URL of the SmartLearn web app"
  value       = "http://${module.compute.public_ip}"
}
