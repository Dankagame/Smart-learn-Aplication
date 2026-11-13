# SmartLearn Infrastructure (Terraform)

This folder builds the AWS infrastructure that hosts SmartLearn: a small, secure network and one Ubuntu server. Ansible (in `ansible/`) then installs Docker on the server and deploys the app.

Everything is created with code, so the whole environment can be built, rebuilt, or deleted with one command.

## What it builds

```
                     Internet
                        │
              ┌─────────▼─────────┐
              │ Internet gateway  │
              └─────────┬─────────┘
  VPC 10.0.0.0/16       │  route 0.0.0.0/0 → gateway
  ┌─────────────────────┼──────────────────────────┐
  │  Public subnet 10.0.1.0/24 (us-east-1a)        │
  │   ┌────────────────────────────────────────┐   │
  │   │ Security group                         │   │
  │   │  in:  22 (SSH)  from my_ip only        │   │
  │   │  in:  80 (HTTP) from anywhere          │   │
  │   │  out: all                              │   │
  │   │   ┌──────────────────────────────┐     │   │
  │   │   │ EC2 t3.micro, Ubuntu 24.04   │     │   │
  │   │   │ encrypted 20 GB gp3 disk     │     │   │
  │   │   │ IMDSv2 required              │     │   │
  │   │   └──────────────────────────────┘     │   │
  │   └────────────────────────────────────────┘   │
  └────────────────────────────────────────────────┘
```

| Resource | Purpose |
|----------|---------|
| VPC (`10.0.0.0/16`) | Our own private network in AWS |
| Public subnet (`10.0.1.0/24`) | Where the server lives. Servers here get a public IP |
| Internet gateway | Connects the VPC to the internet |
| Route table + association | Sends internet traffic (`0.0.0.0/0`) through the gateway |
| Security group | Firewall: SSH only from your IP, HTTP from anyone, all outbound |
| Key pair | Uploads your SSH **public** key so you can log in |
| EC2 instance | Ubuntu 24.04 `t3.micro` server that runs SmartLearn |

## Folder structure

```
terraform/
├── main.tf                    Calls the two modules and connects them
├── variables.tf               Inputs for the whole setup
├── outputs.tf                 Values printed after apply (server IP, SSH command)
├── providers.tf               Terraform and AWS provider versions, AWS region
├── terraform.tfvars.example   Template for your own terraform.tfvars
└── modules/
    ├── network/               VPC, subnet, internet gateway, route table, security group
    └── compute/               Ubuntu AMI lookup, key pair, EC2 instance
```

The **network** module outputs `subnet_id` and `security_group_id`. The root `main.tf` passes them into the **compute** module, so the server is placed in the right subnet behind the right firewall.

## Prerequisites

| Tool | Version | Check with |
|------|---------|------------|
| [Terraform](https://developer.hashicorp.com/terraform/install) | 1.6 or newer | `terraform version` |
| [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) | v2 | `aws --version` |
| An AWS account that allows EC2 | | `aws ec2 describe-vpcs --region us-east-1` |

### 1. AWS credentials

Create an IAM user with programmatic access, then save its access key as a named profile:

```bash
aws configure --profile smartlearn
export AWS_PROFILE=smartlearn
aws sts get-caller-identity
```

Run `export AWS_PROFILE=smartlearn` in every new terminal before using Terraform. Never put access keys in `.tf` files or commit them to Git.

### 2. SSH key

Create a key pair once. The private key stays on your computer; only the public key is uploaded:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/smartlearn-key -C "smartlearn"
```

If your key has a different path, set `public_key_path` in `terraform.tfvars`.

## Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `my_ip` | Your public IP in CIDR form, allowed to SSH in, e.g. `102.22.141.238/32` | none | **Yes** |
| `region` | AWS region for all resources | `us-east-1` | No |
| `project_name` | Prefix used in resource names and tags | `smartlearn` | No |
| `instance_type` | EC2 instance size | `t3.micro` | No |
| `public_key_path` | Path to your SSH public key | `~/.ssh/smartlearn-key.pub` | No |

### Setting your variables

Copy the template and put your own IP in it:

```bash
cp terraform.tfvars.example terraform.tfvars
curl https://checkip.amazonaws.com
```

Then edit `terraform.tfvars`, adding `/32` to the end of your IP:

```hcl
my_ip = "102.22.141.238/32"
```

Terraform reads `terraform.tfvars` automatically. Git ignores it, so your IP is never committed. If your network changes, your IP changes too: update `my_ip` and run `terraform apply` again, or SSH will stop working.

## Commands

Run all commands from this `terraform` folder.

| Step | Command | What it does |
|------|---------|--------------|
| 1 | `terraform init` | Downloads the AWS provider and registers the modules. Run once, and again after adding modules |
| 2 | `terraform fmt -recursive` | Formats all `.tf` files, including those in `modules/` |
| 3 | `terraform validate` | Checks the code for mistakes |
| 4 | `terraform plan` | Shows what will be created, changed, or destroyed, without doing it |
| 5 | `terraform apply` | Creates or updates the resources. Type `yes` to confirm |
| 6 | `terraform output` | Prints the outputs again (server IP, SSH command) |
| 7 | `terraform destroy` | Deletes **everything** this code created. Type `yes` to confirm |

A first deployment takes about 1 to 2 minutes and ends with:

```
Apply complete! Resources: 8 added, 0 changed, 0 destroyed.
```

## Outputs

| Output | Example | Used for |
|--------|---------|----------|
| `instance_public_ip` | `44.200.2.73` | The Ansible inventory |
| `instance_public_dns` | `ec2-44-200-2-73.compute-1.amazonaws.com` | A hostname instead of the IP |
| `ssh_command` | `ssh -i ~/.ssh/smartlearn-key ubuntu@44.200.2.73` | Logging in to the server |
| `app_url` | `http://44.200.2.73` | Opening SmartLearn after Ansible deploys it |

Test the server about 30 seconds after `apply`:

```bash
ssh -i ~/.ssh/smartlearn-key ubuntu@$(terraform output -raw instance_public_ip)
```

## Security

- SSH (port 22) is open **only** to the IP in `my_ip`, never to the whole internet.
- Only port 80 is public. The backend (8000) and database (5432) are not exposed; Nginx reaches the backend inside the server.
- The server's disk is encrypted, and IMDSv2 is required, which blocks a common credential-theft attack.
- The Ubuntu image is looked up from Canonical's official AWS account (`099720109477`) only.
- Secrets and local files are kept out of Git: `terraform.tfvars`, `*.tfstate`, and `.terraform/` are in `.gitignore`.
- Checkov scans this code on every pull request. Findings and decisions are recorded in [`SECURITY.md`](../SECURITY.md).

## Cost

The VPC, subnet, gateway, route table, security group, and key pair are free. The `t3.micro` server, its 20 GB disk, and its public IP cost roughly **$0.02 per hour** in total, which the AWS Free Tier or account credits usually cover.

**Run `terraform destroy` when you are finished**, so nothing keeps running. You can rebuild everything later with `terraform apply`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `var.my_ip: Enter a value:` | `terraform.tfvars` is missing. Create it as shown in [Setting your variables](#setting-your-variables) |
| `No configuration files` | You are in the wrong folder. `cd` into `terraform/` |
| `UnauthorizedOperation` | Wrong AWS account or missing permissions. Run `export AWS_PROFILE=smartlearn`, then `aws sts get-caller-identity` |
| `Invalid value for "path" parameter: no file exists` | The SSH public key is missing. Create it, or fix `public_key_path` |
| SSH times out | Your IP changed. Update `my_ip` in `terraform.tfvars` and run `terraform apply` |
| `Reference to undeclared input variable` | A variable is used but not declared in `variables.tf` |
