data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-key"
  public_key = file(pathexpand(var.public_key_path))

  tags = {
    Name = "${var.project_name}-key"
  }
}

module "encryption" {
  source = "./modules/encryption"

  project_name = var.project_name
}

module "network" {
  source = "./modules/network"

  project_name       = var.project_name
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  kms_key_arn        = module.encryption.key_arn
}

module "security" {
  source = "./modules/security"

  project_name = var.project_name
  vpc_id       = module.network.vpc_id
  admin_cidrs  = var.admin_cidrs
  app_port     = var.app_port
}

module "registry" {
  source = "./modules/registry"

  project_name = var.project_name
}

module "database" {
  source = "./modules/database"

  project_name        = var.project_name
  subnet_ids          = module.network.private_subnet_ids
  security_group_id   = module.security.db_sg_id
  instance_class      = var.db_instance_class
  multi_az            = var.db_multi_az
  deletion_protection = var.db_deletion_protection
  kms_key_arn         = module.encryption.key_arn
}

module "bastion" {
  source = "./modules/bastion"

  project_name      = var.project_name
  ami_id            = data.aws_ami.ubuntu.id
  instance_type     = var.bastion_instance_type
  subnet_id         = module.network.public_subnet_ids[0]
  security_group_id = module.security.bastion_sg_id
  key_name          = aws_key_pair.deployer.key_name
}

module "compute" {
  source = "./modules/compute"

  project_name       = var.project_name
  ami_id             = data.aws_ami.ubuntu.id
  instance_type      = var.app_instance_type
  subnet_id          = module.network.private_subnet_ids[0]
  security_group_id  = module.security.app_sg_id
  key_name           = aws_key_pair.deployer.key_name
  ssm_parameter_arns = module.database.parameter_arns
  kms_key_arn        = module.encryption.key_arn
}

module "loadbalancer" {
  source = "./modules/loadbalancer"

  project_name      = var.project_name
  vpc_id            = module.network.vpc_id
  subnet_ids        = module.network.public_subnet_ids
  security_group_id = module.security.alb_sg_id
  instance_id       = module.compute.instance_id
  app_port          = var.app_port
}

module "cdn" {
  source = "./modules/cdn"
  count  = var.enable_cdn ? 1 : 0

  project_name = var.project_name
  alb_dns_name = module.loadbalancer.dns_name
}

module "cicd" {
  source = "./modules/cicd"

  project_name              = var.project_name
  github_repository         = var.github_repository
  github_subject_prefix     = var.github_subject_prefix
  ecr_repository_arns       = module.registry.repository_arns
  bastion_security_group_id = module.security.bastion_sg_id
}

moved {
  from = module.compute.aws_key_pair.deployer
  to   = aws_key_pair.deployer
}
