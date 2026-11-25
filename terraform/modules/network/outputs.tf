output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets, used by the load balancer and bastion"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets, used by the app server and database"
  value       = aws_subnet.private[*].id
}

output "nat_public_ip" {
  description = "Public IP that private machines use for outbound traffic"
  value       = aws_eip.nat.public_ip
}
