# SmartLearn — Operations Manual & System Guide

[![CI](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/ci.yml/badge.svg)](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/ci.yml)
[![CD](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/cd.yml/badge.svg)](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/cd.yml)
[![Checkov](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/checkov.yml/badge.svg)](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/checkov.yml)

> **Study smarter, even on low data.**  
> SmartLearn is a lightweight, responsive web application designed for secondary school students in Rwanda and East Africa. It delivers curriculum-aligned study materials and interactive quizzes optimized for low-bandwidth connections.

---

## Operations Quick Reference

- **Production Live URL:** http://smartlearn-alb-521972676.us-east-1.elb.amazonaws.com (Application Load Balancer)
- **Liveness Endpoint:** http://smartlearn-alb-521972676.us-east-1.elb.amazonaws.com/health
- **Readiness Probe:** http://smartlearn-alb-521972676.us-east-1.elb.amazonaws.com/ready
- **AWS Region:** `us-east-1` (N. Virginia)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Required Secrets & Environment Variables](#2-required-secrets--environment-variables)
3. [Setup & Local Development](#3-setup--local-development)
4. [Deployment Procedures](#4-deployment-procedures)
5. [Rollback Procedures](#5-rollback-procedures)
6. [Teardown Procedures](#6-teardown-procedures)
7. [Security & Quality Gates](#7-security--quality-gates)
8. [Troubleshooting Guide](#8-troubleshooting-guide)
9. [Team & Governance](#9-team--governance)

---

## 1. Architecture Overview

SmartLearn operates on a secure, multi-AZ AWS production architecture managed through Infrastructure as Code (Terraform) and Configuration as Code (Ansible):

```mermaid
flowchart TD
    Client(["Internet Users (Students / Teachers)"])

    subgraph AWS_Cloud ["AWS Cloud (VPC: 10.0.0.0/16 — us-east-1a, us-east-1b)"]
        IGW["Internet Gateway"]

        subgraph Public_Subnets ["Public Subnets"]
            ALB["Application Load Balancer\n(HTTP 80 — health check /health)"]
            Bastion["Bastion Host (t3.micro, Elastic IP)\n(SSH 22 — Admin & Runner IP Only)"]
            NAT["NAT Gateway"]
        end

        subgraph Private_App_Subnets ["Private App Subnets"]
            EC2["App Server EC2 (Ubuntu 22.04 LTS)"]
            subgraph Docker_Bridge ["Docker Compose Network"]
                Frontend["Nginx Frontend (Port 80 -> 8080)"]
                Backend["FastAPI Backend (Port 8000)"]
            end
        end

        subgraph Private_DB_Subnets ["Private DB Subnets"]
            RDS[("Managed RDS PostgreSQL 16\n(Port 5432 TLS — App SG Only)")]
        end

        SSM["AWS SSM Parameter Store\n(/smartlearn/db/url)"]
        CW["Amazon CloudWatch Logs\n(/smartlearn/app)"]

        EC2 --- Frontend
        EC2 --- Backend
        Frontend -->|Reverse Proxy API /health /ready| Backend
        Backend -->|TLS 5432| RDS
        EC2 -.->|IAM Instance Role| SSM
        EC2 -.->|awslogs| CW
        EC2 -->|443 Egress| NAT
    end

    subgraph CI_CD ["CI/CD Pipeline (GitHub Actions)"]
        OIDC["GitHub OIDC Provider\n(smartlearn-github-deploy)"]
        ECR[("Amazon ECR\nImmutable SHA Tags")]
    end

    Client --> IGW --> ALB -->|Port 80| Frontend
    NAT --> ECR
    CI_CD -->|Assume Role via OIDC| OIDC
    OIDC -->|Push SHA Images| ECR
    OIDC -->|Temporary SG Rule + SSH ProxyJump| Bastion
    Bastion -->|SSH 22| EC2
```

---

## 2. Required Secrets & Environment Variables

All sensitive values must be configured in **GitHub Repository Secrets** (`Settings -> Secrets and variables -> Actions`) and the **`production` Environment** (values come directly from `terraform output`):

| Secret Name | Terraform Output / Source | Example / Format |
| :--- | :--- | :--- |
| `AWS_ROLE_ARN` | `terraform output -raw github_actions_role_arn` | `arn:aws:iam::253490787868:role/smartlearn-github-deploy` |
| `AWS_REGION` | `terraform output -raw aws_region` | `us-east-1` |
| `ALB_DNS_NAME` | `terraform output -raw alb_url` (hostname) | `smartlearn-alb-521972676.us-east-1.elb.amazonaws.com` |
| `BASTION_HOST` | `terraform output -raw bastion_public_ip` | `3.94.215.33` |
| `BASTION_USER` | Default SSH user | `ubuntu` |
| `BASTION_SECURITY_GROUP_ID` | `terraform output -raw bastion_security_group_id` | `sg-0123456789abcdef0` |
| `APP_SERVER_PRIVATE_IP` | `terraform output -raw app_private_ip` | `10.0.11.80` |
| `SSH_PRIVATE_KEY` | Private key matching AWS key pair (`smartlearn-key`) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `ANSIBLE_VAULT_PASSWORD` | Password to decrypt `ansible/inventory/group_vars/all/vault.yml` | Complex alphanumeric string |

---

## 3. Setup & Local Development

### 3.1 Prerequisites
- Docker Engine >= 24.0 and Docker Compose >= 2.20
- Python 3.12 (with `pip` and `virtualenv`)
- Terraform >= 1.5.0
- Ansible Core >= 2.15

### 3.2 Running with Docker Compose
```bash
# 1. Clone repository
git clone https://github.com/Dankagame/Smart-learn-Aplication.git
cd Smart-learn-Aplication

# 2. Copy and customize local environment variables
cp .env.example .env

# 3. Launch the full stack (Database, Backend, Frontend)
docker compose up --build -d

# 4. Check application health
curl http://localhost:8000/health
curl http://localhost:8000/ready
# Access Web UI in browser at: http://localhost:80 or http://localhost:5500
```

### 3.3 Running Unit Tests & Linters
```bash
cd backend
python -m venv venv
source venv/bin/activate # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run pytest with code coverage
pytest --cov=app --cov-report=term

# Run ruff linter & formatting check
ruff check .
ruff format --check .
```

---

## 4. Deployment Procedures

### 4.1 Automated Continuous Deployment (Recommended)
1. Ensure all features and fixes are merged into `main` via an approved Pull Request.
2. The GitHub Actions **CD Workflow (`cd.yml`)** triggers automatically:
   - **Stage 1 (CI):** Runs Lint, Tests (Python 3.12 & 3.13), pip-audit scan, Docker build, and blocking Trivy scan.
   - **Stage 2 (AWS Login):** Authenticates via OIDC with AWS and logs into Amazon ECR.
   - **Stage 3 (Image Publication):** Builds and pushes immutable images tagged with `${{ github.sha }}`.
   - **Stage 4 (Ansible Deployment):** Connects to the private App Server through the Bastion host via SSH ProxyJump and deploys the release.
   - **Stage 5 (Smoke Test):** Probes `http://${ALB_DNS_NAME}/health` and `/ready` until 200 OK is verified.

### 4.2 Manual Deployment via Ansible
```bash
cd ansible

# Install necessary collections
ansible-galaxy collection install -r requirements.yml

# Execute deployment through bastion (hosts.ini defines [bastion] and [webservers] ProxyCommand)
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --vault-password-file ~/.ansible/vault_pass \
  -e "image_tag=<COMMIT_SHA>"
```

---

## 5. Rollback Procedures

If an incident or regression occurs after a production release:

### 5.1 Instant Image Rollback (Fastest)
1. Identify the last known good commit SHA from GitHub Releases or Git log:
   ```bash
   git log --oneline -n 5
   ```
2. Re-run the deployment targeting the previous SHA:
   ```bash
   cd ansible
   ansible-playbook -i inventory/hosts.ini playbook.yml \
     --vault-password-file ~/.ansible/vault_pass \
     -e "image_tag=<PREVIOUS_GOOD_SHA>"
   ```

### 5.2 Git Revert Rollback (Auditable)
```bash
git checkout main
git pull origin main
git revert HEAD -m 1
git push origin main
# The CD workflow will automatically build and deploy the reverted state.
```

---

## 6. Teardown Procedures

To decommission the entire cloud infrastructure and avoid unnecessary cloud costs:

```bash
cd terraform

# 1. Initialize Terraform
terraform init

# 2. Preview destruction plan
terraform plan -destroy -out=destroy.tfplan

# 3. Apply destruction
terraform apply destroy.tfplan

# 4. Verify clean state
terraform state list
# Expected: empty list
```

---

## 7. Security & Quality Gates

| Gate | Tool | Policy | Configuration File |
| :--- | :--- | :--- | :--- |
| **Linting** | Ruff | 0 errors permitted | `backend/pyproject.toml` |
| **Code Tests** | Pytest | Matrix: Python 3.12, 3.13 with coverage | `backend/tests/` |
| **Dependency Scan** | `pip-audit` | Blocking (`exit-code: 1`); non-applicable CVEs documented | `.github/workflows/ci.yml` |
| **Container Scan** | Aqua Trivy | Blocking on `CRITICAL`; accepted risks in `.trivyignore` | `.trivyignore`, `ci.yml` |
| **IaC Scan** | Checkov | Blocking on all PRs; 6 accepted baseline skips documented | `.github/workflows/checkov.yml` |
| **Host Hardening** | Ansible | UFW default deny, SSH key only, rate limiting | `ansible/roles/common/` |

---

## 8. Troubleshooting Guide

### 8.1 ALB Returns HTTP 502 Bad Gateway / 504 Gateway Timeout
- **Cause:** Backend service is starting, crashed, or failing its health checks.
- **Diagnosis:**
  ```bash
  ssh -i ~/.ssh/smartlearn-key -o ProxyJump=ubuntu@<BASTION_IP> ubuntu@<APP_PRIVATE_IP>
  docker ps
  docker logs smartlearn-backend --tail 50
  curl -i http://localhost:8000/ready
  ```
- **Remediation:** Verify that PostgreSQL is healthy (`docker logs smartlearn-db`). If database migrations failed, restart with `docker compose restart backend`.

### 8.2 Ansible Fails to Connect Through Bastion
- **Cause:** Security group rejecting admin IP, or invalid SSH key permissions.
- **Diagnosis:**
  ```bash
  ssh -v -i ~/.ssh/smartlearn-key ubuntu@<BASTION_IP>
  ```
- **Remediation:**
  1. Confirm local IP matches `var.my_ip` in Terraform. Update and run `terraform apply` if your ISP IP changed.
  2. Verify SSH key permissions: `chmod 600 ~/.ssh/smartlearn-key`.

### 8.3 Checkov or Trivy Scan Blocks Pull Request
- **Cause:** A newly introduced dependency, base image layer, or Terraform configuration triggered an unhandled finding.
- **Remediation:**
  1. Inspect the GitHub Actions run logs to identify the CVE or check ID (e.g., `CKV_AWS_xxx`).
  2. If fixable, upgrade the dependency or harden the configuration.
  3. If false positive or unfixable upstream risk, document architectural justification in `SECURITY.md` and add ID to `.trivyignore` or Checkov `--skip-check`.

### 8.4 Database Unreachable (`/ready` returns 503)
- **Cause:** Database container down or connection pool exhausted.
- **Remediation:**
  ```bash
  docker exec -it smartlearn-db pg_isready -U smartlearn -d smartlearn_db
  docker restart smartlearn-db
  ```

---

## 9. Team & Governance

- **Project:** ALU DevOps Summative Assignment — SmartLearn
- **Authors:** Dan Kagame & Fatoumata Ndiaye
- **Repository:** [Dankagame/Smart-learn-Aplication](https://github.com/Dankagame/Smart-learn-Aplication)
- **License:** MIT
