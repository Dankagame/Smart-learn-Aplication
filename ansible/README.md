# SmartLearn Configuration & Deployment (Ansible)

This directory contains the automated configuration management and application deployment playbooks for **SmartLearn**, prepared for **Formative 3 (Configuration + App Security)**.

The setup is architected using **Ansible Roles** and designed for **idempotency** to meet the Mastery criteria.

---

## Table of Contents

- [Overview & Architecture](#overview--architecture)
- [Role Breakdown](#role-breakdown)
- [Shared Infrastructure Agreement](#shared-infrastructure-agreement)
- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [How to Test in Parallel (Local VM)](#how-to-test-in-parallel-local-vm)
- [Running the Playbook](#running-the-playbook)
- [Idempotency & Verification](#idempotency--verification)
- [Hardening & Security Features](#hardening--security-features)

---

## Overview & Architecture

Ansible configures an Ubuntu server from a bare OS installation to a production-ready, hardened environment running SmartLearn with Docker Compose:

```mermaid
flowchart TD
    AnsibleNode["Ansible Controller (Your Machine / CI)"]
    TargetVM["Target Ubuntu VM (AWS EC2 / VirtualBox / Multipass)"]
    
    AnsibleNode -->|SSH (Key Auth)| TargetVM
    
    subgraph TargetVM_Config ["VM Configuration"]
        R1["Role: common\n- System packages\n- SSH Hardening\n- UFW Firewall"]
        R2["Role: docker\n- Docker CE Engine\n- Docker Compose plugin\n- User permissions"]
        R3["Role: app\n- /opt/smartlearn\n- .env (0600) & Compose\n- Healthchecks"]
    end
    
    TargetVM --> TargetVM_Config
```

---

## Role Breakdown

| Role | Responsibility | Security & Mastery Highlights |
| :--- | :--- | :--- |
| **`common`** | Baseline OS packages, system time, firewall, and SSH server. | • **SSH Hardening:** Disables root login (`PermitRootLogin no`), disables password authentication (`PasswordAuthentication no`), limits max auth tries (`MaxAuthTries 4`).<br>• **UFW Firewall:** Default deny incoming, rate-limited SSH, allows only required ports (80, 443, 8000).<br>• **Idempotency:** Uses system handlers so `sshd` and `ufw` are only reloaded when changes occur. |
| **`docker`** | Official Docker Engine and Compose plugin installation. | • Cleans conflicting packages.<br>• Installs official signed repository via `/etc/apt/keyrings`.<br>• Enables and starts systemd service.<br>• Adds non-root user to `docker` group. |
| **`app`** | Production application deployment via Docker Compose. | • Secure directory `/opt/smartlearn` (`0750`).<br>• Secrets isolated in `.env` (`0600`).<br>• Pulls images from GitHub Container Registry (`ghcr.io/dankagame/...`).<br>• Automated healthcheck probes on `/health` and `/nginx-health`. |

---

## Shared Infrastructure Agreement

| Parameter | Agreed Value | Notes |
| :--- | :--- | :--- |
| **Cloud Provider & Region** | AWS (`eu-west-1` Ireland or `us-east-1` N. Virginia) | Low latency, free-tier eligible `t3.micro` or `t2.micro`. |
| **OS Image** | Ubuntu 22.04 LTS or 24.04 LTS (x86_64) | Consistent with Docker repository configurations. |
| **SSH Key Pair** | `~/.ssh/smartlearn-key` / `smartlearn-key.pub` | Generated and shared across deployment components. |
| **Frontend Port** | `80` (HTTP) | Exposed by UFW and mapped to container port 8080. |
| **Backend Port** | `8000` (HTTP) | FastAPI backend; healthcheck at `/health`. |
| **Database Port** | `5432` (Internal only) | Isolated inside Docker bridge network (`smartlearn-network`). Not exposed on host. |
| **Container Images** | `ghcr.io/dankagame/smartlearn-backend:latest`<br>`ghcr.io/dankagame/smartlearn-frontend:latest` | Published automatically by GitHub Actions CI pipeline. |

---

## Directory Structure

```text
ansible/
├── ansible.cfg                    # Default Ansible settings (roles_path, host_key_checking)
├── inventory/
│   ├── hosts.ini                  # Target server IP and connection parameters
│   └── group_vars/
│       └── all.yml                # Global default variables (ports, images, security settings)
├── playbook.yml                   # Master playbook orchestrating roles
├── roles/
│   ├── common/
│   │   ├── handlers/main.yml      # Service restart handlers (sshd, ufw)
│   │   └── tasks/
│   │       ├── main.yml           # Entry point
│   │       ├── system.yml         # Base packages
│   │       ├── ssh.yml            # SSH hardening
│   │       └── firewall.yml       # UFW firewall
│   ├── docker/
│   │   ├── handlers/main.yml      # Docker service handlers
│   │   └── tasks/main.yml         # Docker CE & Compose installation
│   └── app/
│       ├── defaults/main.yml      # Default deployment variables
│       ├── handlers/main.yml      # Compose restart handlers
│       ├── tasks/main.yml         # Deployment tasks and health verification
│       └── templates/
│           ├── docker-compose.yml.j2 # Jinja2 compose template
│           └── env.j2             # Jinja2 environment file template
└── README.md                      # Documentation (this file)
```

---

## Prerequisites

1. **Ansible installed on controller machine:**
   ```bash
   pip install ansible
   # or (Ubuntu/Debian)
   sudo apt update && sudo apt install -y ansible
   ```
2. **Install required Ansible collections:**
   ```bash
   ansible-galaxy collection install community.general community.docker
   ```
3. **SSH Key Pair created:**
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/smartlearn-key -C "smartlearn-deploy"
   ```

---

## How to Test in Parallel (Local VM)

You can test immediately using any Ubuntu VM without waiting for cloud provisioning:

1. **Using Multipass (Quickest Local VM):**
   ```bash
   multipass launch --name smartlearn-test --cpus 2 --memory 2G 22.04
   multipass info smartlearn-test # Note the IPv4
   # Copy your public key to the VM:
   multipass exec smartlearn-test -- bash -c "echo '$(cat ~/.ssh/smartlearn-key.pub)' >> ~/.ssh/authorized_keys"
   ```
2. **Update `inventory/hosts.ini`:**
   ```ini
   [webservers]
   smartlearn-server ansible_host=<VM_IP> ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/smartlearn-key
   ```
3. Once the production EC2 public IP is provisioned via Terraform, simply swap `<VM_IP>` in `inventory/hosts.ini`!

---

## Running the Playbook

### 1. Test connectivity
```bash
ansible -i inventory/hosts.ini webservers -m ping
```

### 2. Check syntax
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --syntax-check
```

### 3. Dry-run (Check mode)
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --check
```

### 4. Execute deployment
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml
```

---

## Idempotency & Verification

- **Idempotency Guarantee:** Running the playbook a second time yields `changed=0` (or only dynamic transient status checks). No duplicate lines in `sshd_config`, no redundant container restarts, and no firewall rule corruption.
- **Verification Commands:**
  ```bash
  # Check SSH hardening
  ssh -i ~/.ssh/smartlearn-key ubuntu@<VM_IP> "sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|maxauthtries'"

  # Check firewall status
  ssh -i ~/.ssh/smartlearn-key ubuntu@<VM_IP> "sudo ufw status verbose"

  # Check Docker containers
  ssh -i ~/.ssh/smartlearn-key ubuntu@<VM_IP> "docker ps"

  # Verify application endpoints
  curl -I http://<VM_IP>/
  curl http://<VM_IP>:8000/health
  ```
