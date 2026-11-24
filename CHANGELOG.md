# Changelog — SmartLearn DevOps Lifecycle

All notable changes to the **SmartLearn** application and DevOps infrastructure are documented in this file, organized across the three major course milestones: **F1**, **F2**, and **F3 / Summative**.

---

## [F3 / Summative] — Infrastructure as Code, Automated CD & DevSecOps

### Added
- **Continuous Delivery Pipeline (`.github/workflows/cd.yml`):**
  - Fully automated production deployment triggered exclusively on push to `main`.
  - Concurrency group `production-deployment` with zero in-progress cancellations.
  - OIDC passwordless authentication with AWS IAM via `aws-actions/configure-aws-credentials@v4`.
  - Automated login, build, and push of backend and frontend container images to Amazon ECR tagged with `${{ github.sha }}` and `latest`.
  - Ansible deployment executed through a Bastion jump host via SSH ProxyJump.
  - Automated post-deployment smoke test validating `/health` and `/ready` through the ALB.
- **Reusable CI Workflow (`.github/workflows/ci.yml`):**
  - Added `workflow_call` trigger enabling seamless orchestration from `cd.yml`.
  - Made `pip-audit` blocking on unaccepted CVEs, enforcing zero unknown supply-chain vulnerabilities.
  - Made `trivy` container scanning blocking on `CRITICAL` severity (`exit-code: 1`).
  - Added `.trivyignore` documenting explicit architectural risk justifications for base image packages.
- **Universal IaC Scanning (`.github/workflows/checkov.yml`):**
  - Configured Checkov static analysis to run on every Pull Request to `main`.
- **Infrastructure as Code (`terraform/`):**
  - Modularized Terraform architecture with `network` (VPC, subnets, route tables, security groups) and `compute` (EC2, EBS encryption, IMDSv2).
  - Outbound egress restricted to TCP 80/443; ingress restricted by IP CIDR.
- **Configuration Management (`ansible/`):**
  - Modular roles: `common` (SSH hardening, UFW firewall), `docker` (official Docker CE engine), and `app` (Docker Compose deployment).
  - Secrets encrypted with Ansible Vault (`vault.yml`).
  - Full idempotency guarantee: repeated runs yield zero unexpected changes.
- **Application Observability:**
  - Added `/ready` HTTP endpoint that verifies active database connectivity, returning 200 OK when ready or 503 Service Unavailable when the database is unreachable.
- **Documentation:**
  - Complete operations manual rewrite in `README.md` covering architecture, secrets, setup, deploy, rollback, and teardown.
  - Centralized security policy, scan results, and hardening findings in `SECURITY.md`.

### Changed
- Upgraded `python-multipart` to `0.0.32` to resolve quadratic parsing complexity and parameter smuggling vulnerabilities.
- Tightened UFW and Security Group rules to block direct database access from external networks.

---

## [F2] — Continuous Integration, Quality Gates & Branch Protection

### Added
- **Continuous Integration Pipeline (`.github/workflows/ci.yml`):**
  - Automated matrix testing on Python 3.12 and Python 3.13.
  - Code coverage measurement with `pytest-cov`.
  - Automated code linting and style checking using `ruff`.
  - Automated container image builds with layer caching via GitHub Container Registry (GHCR).
- **Branch Protection & Code Review:**
  - Protected `main` branch requiring Pull Requests with mandatory peer review.
  - Required status checks: Lint, Test (Python 3.12), Test (Python 3.13), and Docker builds.
  - Enforced linear history and prevented force-pushes on `main`.

### Fixed
- Fixed method not allowed assertion in health check test (`test_health_rejects_post_requests`) ensuring strict HTTP 405 compliance.

---

## [F1] — Core Application Architecture & Containerization

### Added
- **Backend Architecture:**
  - RESTful API built on FastAPI and Python 3.12.
  - Relational database schema with SQLAlchemy ORM and PostgreSQL integration.
  - Stateless JWT authentication and role-based access control (Student vs Teacher).
  - Subject-based courses, curriculum materials, and multiple-choice quizzes.
- **Frontend Architecture:**
  - Lightweight, responsive HTML5/CSS/JavaScript client served via Nginx on Alpine Linux.
  - Low-data consumption design optimized for low-end mobile devices and rural connectivity.
- **Containerization (`Dockerfile`, `docker-compose.yml`):**
  - Multi-stage Dockerfiles minimizing image sizes and build attack surfaces.
  - Local multi-container development environment with health checks and bridge networking.
