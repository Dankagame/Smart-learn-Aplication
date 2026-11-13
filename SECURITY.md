# SmartLearn Security Policy & Vulnerability Findings

This document outlines the security architecture, automated security scanning results, and hardening practices implemented for the **SmartLearn** application, prepared for **Formative 3 (DevOps & DevSecOps)**.

---

## Table of Contents

1. [Security Architecture & Defense-in-Depth](#1-security-architecture--defense-in-depth)
2. [Dependency Security Findings (pip-audit)](#2-dependency-security-findings-pip-audit)
3. [Container Security Findings (Trivy)](#3-container-security-findings-trivy)
4. [Host & Configuration Hardening (Ansible)](#4-host--configuration-hardening-ansible)
5. [Infrastructure as Code Findings (Terraform / Checkov)](#5-infrastructure-as-code-findings-terraform--checkov)
6. [Incident Response & Security Contact](#6-incident-response--security-contact)

---

## 1. Security Architecture & Defense-in-Depth

SmartLearn adheres to a multi-layered security strategy:

```mermaid
flowchart TD
    subgraph Layer1 ["Layer 1: Perimeter / Infrastructure (Terraform)"]
        FW["Cloud Security Groups & VPC Isolation"]
    end

    subgraph Layer2 ["Layer 2: Host Operating System (Ansible)"]
        UFW["UFW Firewall (Default Deny Inbound)"]
        SSH["SSH Hardening (No Root, No Passwords, Rate Limiting)"]
    end

    subgraph Layer3 ["Layer 3: Container Runtime (Docker)"]
        ISO["Docker Isolated Bridge Network"]
        VOL["Persistent Named Volumes & Non-Root Containers"]
    end

    subgraph Layer4 ["Layer 4: Application & Dependencies"]
        AUDIT["pip-audit Automated Dependency Scanning"]
        JWT["Stateless JWT Authentication & Password Hashing (bcrypt)"]
    end

    FW --> UFW --> ISO --> AUDIT
    FW --> SSH
    ISO --> VOL
    ISO --> JWT
```

---

## 2. Dependency Security Findings (pip-audit)

### 2.1 Methodology
Automated software composition analysis (SCA) is executed in the CI pipeline via `pip-audit`. It checks all direct and transitive dependencies defined in `backend/requirements.txt` against the PyPA Advisory Database and OSV (Open Source Vulnerabilities).

### 2.2 Scanned Packages Overview

| Package | Version | Purpose | Known CVEs | Status |
| :--- | :--- | :--- | :--- | :--- |
| `fastapi` | `0.115.6` | Web API Framework | None | ✅ Verified Clean |
| `uvicorn[standard]` | `0.34.0` | ASGI Server | None | ✅ Verified Clean |
| `sqlalchemy` | `2.0.36` | ORM & Query Builder | None | ✅ Verified Clean |
| `psycopg[binary]` | `3.2.3` | PostgreSQL Driver | None | ✅ Verified Clean |
| `pydantic` | `2.10.4` | Data validation | None | ✅ Verified Clean |
| `pydantic-settings` | `2.7.1` | Environment settings | None | ✅ Verified Clean |
| `email-validator` | `2.2.0` | Email syntax verification | None | ✅ Verified Clean |
| `bcrypt` | `4.2.1` | Password hashing | None | ✅ Verified Clean |
| `PyJWT` | `2.10.1` | JSON Web Token encoding/decoding | None | ✅ Verified Clean |
| `python-multipart` | `0.0.32` | Form/File parsing | PYSEC-2026-3036, PYSEC-2026-3037 | ✅ Resolved by upgrading to >= 0.0.30 |
| `starlette` (transitive) | `0.41.3` | ASGI Core (FastAPI dependency) | PYSEC-2026-2281 | ⚠️ Low risk: Windows SMB SSRF (Production runs on Linux/Docker) |
| `httpx` | `0.28.1` | Async HTTP Client | None | ✅ Verified Clean |
| `pytest` | `8.3.4` | Test Framework (dev) | None | ✅ Verified Clean |
| `ruff` | `0.8.4` | Linter & Formatter (dev) | None | ✅ Verified Clean |

### 2.3 Vulnerability Analysis & Mitigations
- **`python-multipart` (PYSEC-2026-3036 & PYSEC-2026-3037):** Earlier versions (< 0.0.30) had quadratic parsing complexity and parameter smuggling when parsing semicolons in form bodies. Upgraded and pinned to `python-multipart==0.0.32` to ensure linear O(N) parsing and strict compliance with the WHATWG URL standard.
- **`starlette` (PYSEC-2026-2281):** Pertains to Windows UNC path handling in `StaticFiles`. The application runs on Linux containers (`python:3.12-slim`), which are inherently immune to Windows UNC/SMB exploits.
- **Strict Pinning Strategy:** All dependencies use exact version pins (`==`) in `backend/requirements.txt` to eliminate supply-chain drift and ensure deterministic builds across CI and production.
- **Transitive Dependency Auditing:** `pip-audit --local` verifies the fully resolved environment inside CI and documents any newly disclosed CVEs.

---

## 3. Container Security Findings (Trivy)

### 3.1 Methodology
Container image security is audited using **Aqua Security Trivy** directly within the GitHub Actions CI pipeline on every push and pull request. Both application images (`smartlearn-backend` and `smartlearn-frontend`) are inspected for:
- OS package vulnerabilities (Debian / Alpine CVEs)
- Embedded application libraries and configurations

### 3.2 Backend Container Analysis (`Dockerfile`)
- **Base Image:** `python:3.12-slim` (Debian Bookworm base).
- **Findings:**
  - Minimal OS packages: Slim variant excludes unnecessary compilers, debug tools, and legacy utilities, reducing total CVE footprint by ~80% compared to standard `python:3.12`.
  - Cache hygiene: `rm -rf /var/lib/apt/lists/*` and `--no-cache-dir` prevent package manager cache accumulation in image layers.
- **Container Hardening:**
  - Dedicated non-root system user (`appuser`, UID 1001) executes the Uvicorn process.
  - Secret isolation: No `.env` or credentials baked into image layers; secrets are mounted/passed at runtime only.

### 3.3 Frontend Container Analysis (`frontend/Dockerfile`)
- **Base Image:** `nginx:1.25-alpine`
- **Findings:**
  - Alpine Linux minimizes attack surface (< 25MB base image).
  - Unprivileged execution: Configured to listen on port 8080 internally, allowing non-root execution.
  - Custom `nginx.conf`: Restricts buffer sizes, disables server tokens (`server_tokens off;`), and adds security headers (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`).

---

## 4. Host & Configuration Hardening (Ansible)

Server configuration is governed by idempotent Ansible playbooks with built-in hardening:

1. **SSH Hardening (`roles/common/tasks/ssh.yml`):**
   - `PermitRootLogin no`: Direct root login is strictly disabled.
   - `PasswordAuthentication no`: SSH password authentication disabled; key-based authentication enforced (`smartlearn-key`).
   - `MaxAuthTries 4`: Mitigates brute-force authentication attempts.
   - `X11Forwarding no`: Prevents GUI forwarding exploits.
2. **Host Firewall (`roles/common/tasks/firewall.yml`):**
   - Default incoming policy: **DENY**.
   - Default outgoing policy: **ALLOW**.
   - SSH (Port 22): **Rate-limited** (`ufw limit 22/tcp`) to prevent brute-force abuse.
   - Web ports: Only Port 80 (HTTP) and Port 8000 (API) are explicitly allowed.
   - PostgreSQL (Port 5432): **Blocked from public internet**; strictly isolated within Docker's internal bridge network.
3. **Secrets & File Permissions (`roles/app/tasks/main.yml`):**
   - Application directory `/opt/smartlearn` set to `0750` mode, owned by `ubuntu:ubuntu`.
   - Production `.env` file containing database passwords and JWT secrets is restricted to `0600` permissions (read/write by owner only).

---

## 5. Infrastructure as Code Findings (Terraform / Checkov)

### 5.1 IaC Scanning Tool

- **Tool:** [Checkov](https://www.checkov.io/) 3.x, a static analysis scanner for infrastructure as code.
- **Workflow:** `.github/workflows/checkov.yml` scans the `terraform/` folder, including both modules, on every pull request that changes Terraform code, on pushes to `main`, and on demand.
- **Failure policy:** `soft_fail: false`, so any failed check fails the pull request. The accepted findings below are skipped by ID in the workflow, so a new problem can never hide behind them.

Run the same scan locally:

```bash
checkov -d terraform --framework terraform --compact
```

### 5.2 Scan Results Summary

| Stage | Passed | Failed |
|-------|--------|--------|
| First scan | 12 | 9 |
| After fixes | 15 | 6 |
| In CI, with the 6 accepted checks skipped | 15 | 0 |

### 5.3 Controls Already in Place (passed on the first scan)

| Check | Control | How |
|-------|---------|-----|
| CKV_AWS_24 | SSH is not open to the internet | Port 22 allows only the admin IP (`var.my_ip`, a `/32`) |
| CKV_AWS_8 | Server disk is encrypted at rest | `root_block_device { encrypted = true }` |
| CKV_AWS_79 | IMDSv1 is disabled | `metadata_options { http_tokens = "required" }` (IMDSv2 only) |
| CKV_AWS_386 | No look-alike or malicious AMIs | AMI lookup limited to Canonical's account `099720109477` |
| CKV_AWS_23 | Every security group rule is documented | Each rule has a `description` |
| CKV_AWS_41 | No AWS keys in code | Credentials come from an AWS CLI profile, never from `.tf` files |

### 5.4 Findings Fixed

| Check | Finding | Fix |
|-------|---------|-----|
| CKV_AWS_382 | Outbound traffic allowed on all ports to `0.0.0.0/0` | Outbound limited to TCP 443 (HTTPS: Docker images, GitHub, updates) and TCP 80 (Ubuntu package mirrors). Verified with `apt-get update` on the server |
| CKV2_AWS_12 | The VPC's default security group allowed traffic | `aws_default_security_group` manages it with no rules, so it denies everything |
| CKV_AWS_126 | No detailed monitoring on the EC2 instance | `monitoring = true` (1-minute CloudWatch metrics) |

### 5.5 Findings Accepted (with justification)

| Check | Finding | Why it is accepted | Risk reduction |
|-------|---------|--------------------|----------------|
| CKV_AWS_260 | Port 80 open to `0.0.0.0/0` | SmartLearn is a public website; students must reach it from anywhere | Only port 80 is public. The API (8000) and database (5432) are not opened in the security group |
| CKV_AWS_130 | Subnet assigns public IPs | The single server must be reachable for the website and for Ansible; there is no load balancer or bastion in this design | Inbound limited by the security group; SSH only from the admin IP |
| CKV_AWS_135 | Instance not marked EBS-optimized | `t3` instances are EBS-optimized by default. Setting the flag on the running server would force it to be destroyed and rebuilt | No security impact; performance setting only |
| CKV2_AWS_5 | Security group "not attached" | False positive: the group is created in the `network` module and attached in the `compute` module, which Checkov does not follow across modules | Verified attached with `aws ec2 describe-instances` |
| CKV2_AWS_11 | No VPC flow logs | Needs a CloudWatch log group, an IAM role, and KMS encryption, adding cost and complexity for a one-server student project | Detailed monitoring is enabled. Recommended before real production use |
| CKV2_AWS_41 | No IAM role on the EC2 instance | The server never calls AWS APIs, so a role would only add permissions it does not need (least privilege) | No AWS credentials exist on the server at all |

### 5.6 Other Infrastructure Security Practices

- **Secrets stay out of Git:** `terraform.tfvars` (admin IP), `*.tfstate` (resource details), and `.terraform/` are in `.gitignore`. A `terraform.tfvars.example` template with a documentation-only IP is committed instead.
- **Least-privilege SSH, and its trade-off:** SSH accepts only the admin's current IP. When that IP changes, SSH times out until `my_ip` is updated and `terraform apply` is run. This happened during testing and confirmed the rule works.
- **SSH key authentication:** only the public key (`ed25519`) is uploaded to AWS; the private key never leaves the admin's computer.
- **Dedicated IAM user for Terraform:** Terraform runs as a separate IAM user with an access key stored in a named AWS CLI profile, not as the root account.
- **Network layout:** a dedicated VPC (`10.0.0.0/16`) with one public subnet (`10.0.1.0/24`). The internet gateway and route table send only outbound internet traffic through the gateway.

---

## 6. Incident Response & Security Contact

To report potential security vulnerabilities or findings, please open a private GitHub advisory or reach out to the SmartLearn maintainers:
- **Team:** SmartLearn DevOps Team (Dan Kagame & Fatoumata Ndiaye)
- **Repository:** [Dankagame/Smart-learn-Aplication](https://github.com/Dankagame/Smart-learn-Aplication)
