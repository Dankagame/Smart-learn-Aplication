module "network" {
  source = "./modules/network"

  project_name = var.project_name
  region       = var.region
  my_ip        = var.my_ip
}

module "compute" {
  source = "./modules/compute"

  project_name      = var.project_name
  instance_type     = var.instance_type
  public_key_path   = var.public_key_path
  subnet_id         = module.network.subnet_id
  security_group_id = module.network.security_group_id
}

moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}

moved {
  from = aws_subnet.public
  to   = module.network.aws_subnet.public
}

moved {
  from = aws_internet_gateway.main
  to   = module.network.aws_internet_gateway.main
}

moved {
  from = aws_route_table.public
  to   = module.network.aws_route_table.public
}

moved {
  from = aws_route_table_association.public
  to   = module.network.aws_route_table_association.public
}

moved {
  from = aws_security_group.web
  to   = module.network.aws_security_group.web
}

moved {
  from = aws_key_pair.deployer
  to   = module.compute.aws_key_pair.deployer
}

moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
