# SmartLearn

[![CI](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/ci.yml/badge.svg)](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/ci.yml)
[![Checkov](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/checkov.yml/badge.svg)](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/checkov.yml)

> **Study smarter, even on low data.**

**Live app:** [http://44.200.2.73](http://44.200.2.73) · **API health:** [http://44.200.2.73/health](http://44.200.2.73/health)

SmartLearn is a lightweight **web application** that runs in any web browser, so there is no app to download or install. Secondary school students in Rwanda and across East Africa can use it to find curriculum-aligned study materials and practise with quizzes before their national exams. Teachers get a simple, low-cost way to share notes and quizzes with all of their students.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Our Solution](#our-solution)
- [Target Users](#target-users)
- [Core Features](#core-features)
- [Technology Stack](#technology-stack)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Run with Docker Compose](#run-with-docker-compose)
- [How to Run Locally](#how-to-run-locally)
- [Running the Tests](#running-the-tests)
- [Linting and Code Style](#linting-and-code-style)
- [Continuous Integration](#continuous-integration)
- [Cloud Deployment (Terraform + Ansible)](#cloud-deployment-terraform--ansible)
- [Security Practices](#security-practices)
- [Branch Protection Rules](#branch-protection-rules)
- [Development Workflow](#development-workflow)
- [Why It Fits a 6-Week DevOps Course](#why-it-fits-a-6-week-devops-course)
- [Team](#team)
- [License](#license)

---

## Problem Statement

Many secondary school students in Rwanda and East Africa prepare for national exams without the resources they need. Textbooks, good notes, and past papers are hard to find, especially in rural schools, where one copy may be shared by a whole class. When digital resources do exist, they are usually spread across many WhatsApp groups. Files get buried under chat messages, are not organized by subject or level, and are hard to find again when a student needs them. Mobile data is expensive, and many students only have basic smartphones with slow connections, so heavy apps and video-based platforms are not realistic options for them.

Students also have few ways to practise and check what they understand before an exam. Without regular feedback, they often don't find their weak areas until it is too late. Teachers want to help, but most have no simple, affordable tool for sharing materials and quizzes with all of their students at once. The result is unequal access to exam preparation, which depends heavily on where a student lives and which school they attend.

## Our Solution

SmartLearn gives students **one organized place** to find curriculum-aligned learning materials and practice quizzes, grouped by subject and level (for example, *Mathematics – S6*). It is a **lightweight, responsive web application**: students and teachers open it in a web browser on a phone, tablet, or computer. Pages are simple, load quickly, and use little data, so the site works well even on basic smartphones and slow networks.

- **Students** stop searching through chat groups. They browse materials by course, practise with quizzes, and get feedback right away.
- **Teachers** publish a resource or quiz once and reach every student in the course, then use the results to see where students are struggling.

## Target Users

| User | Description | What they need |
|------|-------------|----------------|
| **Students** *(primary users)* | Secondary school learners preparing for national exams, often using basic smartphones on limited data. | Browse courses and learning materials, take practice quizzes, and see their marks and progress over time. |
| **Teachers** | Subject teachers who want to support their students beyond the classroom. | Create courses, post notes and resource links, build multiple-choice quizzes, and review student results. |
| **Schools & Education NGOs** *(future users)* | Institutions and organizations that support learners at scale. | Possible future use: share approved content across many classes or schools and track learning outcomes. |

## Core Features

1. **Registration & role-based login:** Students and teachers create accounts and sign in securely. Each role only sees and does what it is allowed to.
2. **Course management:** Teachers create courses organized by subject and level (for example, *Mathematics – S6*), so content is easy to find.
3. **Learning materials:** Teachers post notes and useful links to a course, and students browse them in one organized place.
4. **Practice quizzes:** Teachers create multiple-choice quizzes. Students submit their answers and get an instant score with feedback.
5. **Results tracking:** Students see their quiz history to follow their progress, and teachers see the results for the quizzes they created.

## Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Frontend** | HTML5 | Simple, standard page structure that loads quickly on any browser. |
| | Bootstrap 5 | Responsive design, so the website adapts to phone, tablet, and computer screens. |
| | JavaScript (vanilla) | Calls the backend API with `fetch()` and updates pages dynamically, with no heavy framework to download. |
| **Backend** | Python 3.12+ | Readable, widely used language with a strong ecosystem. |
| | FastAPI | Fast, modern framework for building REST APIs, with automatic interactive API docs. |
| | SQLite / PostgreSQL | SQLite needs no setup for local development. PostgreSQL is a reliable choice for production. |
| | SQLAlchemy 2.0 | ORM that lets the same code work with both SQLite and PostgreSQL. |
| | JWT + bcrypt | Stateless token-based authentication and secure password hashing. |
| | pytest | Simple, powerful framework for unit and API tests. |
| | Ruff | Fast linter and code formatter that keeps the Python code clean and consistent. |
| **Tools & DevOps** | Git, GitHub, GitHub Projects | Version control, code review through pull requests, and agile planning. |
| | Docker, Docker Compose | Each service runs in its own container, so the whole app starts the same way on every machine. |
| | GitHub Actions, GitHub Container Registry | CI runs lint, tests, and Docker builds on every push and pull request, then publishes the images. |
| | Terraform, AWS (VPC, EC2) | Builds the cloud network and server as code, so the environment can be recreated or deleted with one command. |
| | Ansible | Hardens the server, installs Docker, and deploys the app the same way every time. |
| | Checkov, Trivy, pip-audit | Scan the Terraform code, the Docker images, and the Python dependencies for security problems. |

## Architecture Overview

SmartLearn keeps the **frontend and backend separate**. The frontend is a set of static pages (HTML, Bootstrap, and JavaScript). It talks to the backend only through a **REST API** that sends and receives JSON.

```
┌──────────────────────┐        REST API (JSON)        ┌──────────────────────────┐
│       Frontend       │  ───────────────────────────► │      Backend (FastAPI)   │
│ HTML + Bootstrap + JS│  ◄─────────────────────────── │  auth · courses · quizzes│
└──────────────────────┘                               └────────────┬─────────────┘
                                                                    │ SQLAlchemy
                                                                    ▼
                                                       ┌──────────────────────────┐
                                                       │ SQLite (dev) / PostgreSQL│
                                                       └──────────────────────────┘
```

Because the two parts depend only on the API between them, each one can be **built, tested, containerized, and deployed on its own**. Inside the backend, the code is organized into separate modules for **authentication**, **courses & materials**, and **quizzes & results**, each with a clear responsibility.

## Project Structure

```
Smart-learn-Aplication/
├── backend/                FastAPI REST API
│   ├── app/
│   │   ├── core/           settings, database, security helpers
│   │   ├── auth/           registration, login, roles
│   │   ├── courses/        courses and learning materials
│   │   ├── quizzes/        quizzes, scoring, results
│   │   └── main.py         app entry point
│   ├── tests/              pytest test suite
│   ├── requirements.txt
│   └── .env.example        example settings (no real secrets)
├── frontend/               HTML, Bootstrap 5, JavaScript
│   ├── index.html          landing page
│   ├── pages/              login, register, dashboard
│   ├── css/
│   └── js/                 api.js (API client), auth.js, main.js
├── terraform/              AWS infrastructure as code (see terraform/README.md)
│   └── modules/            network (VPC, subnet, firewall) and compute (EC2 server)
├── ansible/                server setup and app deployment (see ansible/README.md)
│   └── roles/              common (hardening), docker, app
├── .github/
│   ├── workflows/          ci.yml (lint, test, build, scans), checkov.yml (Terraform scan)
│   └── CODEOWNERS
├── .gitignore
├── LICENSE
├── SECURITY.md             security findings, fixes, and accepted risks
└── README.md
```

## Run with Docker Compose

This is the quickest way to start SmartLearn. One command starts the database, the backend API, and the frontend, each in its own container. You don't need Python, PostgreSQL, or anything else installed, only Docker.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) on Windows or macOS, or Docker Engine with the Compose plugin on Linux
- Docker must be running before you use the commands below. Check with `docker compose version`.

### Quick start

```bash
git clone https://github.com/Dankagame/Smart-learn-Aplication.git
cd Smart-learn-Aplication
cp .env.example .env
docker compose up --build
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

The first build takes a few minutes. When the logs settle down, open **http://localhost:5500**.

Before sharing or deploying the app, change `POSTGRES_PASSWORD` and `SECRET_KEY` in `.env`. Docker Compose reads this file automatically, and Git ignores it, so your secrets stay on your machine.

### Services

`docker-compose.yml` defines three services:

| Service | Image | Container | What it does |
|---------|-------|-----------|--------------|
| `db` | `postgres:16-alpine` | `smartlearn-db` | PostgreSQL 16 database that stores users, courses, quizzes, and results. |
| `backend` | Built from `Dockerfile` | `smartlearn-backend` | FastAPI REST API, run by Uvicorn as a non-root user (`appuser`). It connects to `db` with `DATABASE_URL=postgresql+psycopg://...@db:5432/...`. |
| `frontend` | Built from `frontend/Dockerfile` | `smartlearn-frontend` | Nginx serves the HTML, CSS, and JavaScript, and forwards API calls such as `/auth`, `/courses`, `/quizzes`, `/me`, and `/health` to `backend`. |

The services start in order, and each waits until the one it depends on is healthy:

1. `db` is healthy when `pg_isready` succeeds.
2. `backend` starts after `db`. It is healthy when `GET /health` responds.
3. `frontend` starts after `backend`. It is healthy when `/nginx-health` responds.

### Ports

| Open on your computer | Goes to | Use it for |
|-----------------------|---------|------------|
| [http://localhost:5500](http://localhost:5500) (also [http://localhost](http://localhost) on port 80) | `frontend` port 8080 | The web app |
| [http://localhost:8000](http://localhost:8000) | `backend` port 8000 | The REST API directly |
| [http://localhost:8000/docs](http://localhost:8000/docs) | `backend` port 8000 | Interactive API docs (Swagger) |
| [http://localhost:8000/health](http://localhost:8000/health) | `backend` port 8000 | Health check, which also reports the database connection |
| `localhost:5432` | `db` port 5432 | Connecting a database tool such as pgAdmin or DBeaver, with the user and password from `.env` |

If one of these ports is already used on your computer, `docker compose up` fails with "port is already allocated". Stop the other program, or change the left-hand port in `docker-compose.yml` (for example `"5501:8080"`).

### Network

All three services join one bridge network, `smartlearn-network`. Inside this network, containers find each other by **service name**: the backend connects to the database at `db:5432`, and Nginx forwards requests to `backend:8000`. The network keeps the containers' traffic separate from other containers on your machine. Only the ports listed above are opened to your computer.

### Volume

The database files live in a named volume, `postgres_data`, mounted at `/var/lib/postgresql/data` in the `db` container. Because the data is stored in the volume and not in the container, it stays when you stop, rebuild, or remove the containers. `docker compose down -v` is the only command here that deletes it.

### Useful commands

| Command | What it does |
|---------|--------------|
| `docker compose up --build` | Build the images and start everything, with logs shown in your terminal |
| `docker compose up -d --build` | The same, but in the background |
| `docker compose ps` | Show each container's status and health |
| `docker compose logs -f backend` | Follow the logs of one service (`db`, `backend`, or `frontend`) |
| `docker compose restart backend` | Restart one service |
| `docker compose exec db psql -U smartlearn_user -d smartlearn_db` | Open a SQL shell in the database. Use your own values if you changed them in `.env` |
| `docker compose down` | Stop and remove the containers. The database data is kept |
| `docker compose down -v` | Stop the containers **and delete the database volume**, for a fresh start |

### Build images on their own

```bash
docker build -t smartlearn-backend .
docker build -t smartlearn-frontend ./frontend
```

CI also publishes ready-made images to GitHub Container Registry. See [Published Docker images](#published-docker-images).

## How to Run Locally

### Requirements

- Python 3.12+
- Git
- A web browser (and optionally the VS Code **Live Server** extension)

### 1. Clone the repository

```bash
git clone https://github.com/Dankagame/Smart-learn-Aplication.git
cd Smart-learn-Aplication
```

### 2. Start the backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

Install the dependencies and create your settings file:

```bash
pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env
```

Open `.env` and set your own `SECRET_KEY`. You can generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Start the server:

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 3. Start the frontend

Open a **second terminal** in the project folder:

```bash
cd frontend
python -m http.server 5500
```

Then open http://127.0.0.1:5500 in your browser. (Or, in VS Code, right-click `frontend/index.html` and choose **Open with Live Server**.)

### 4. Try it out

1. Register a **teacher** account, log in, then create a course and a quiz.
2. Register a **student** account, log in, take the quiz, and see your score.

## Running the Tests

The backend has an automated test suite written with **pytest**. The tests use a temporary in-memory SQLite database, so they don't need PostgreSQL and never touch real data.

With the virtual environment activated (see [How to Run Locally](#how-to-run-locally)):

```bash
cd backend
pytest
```

To see how much of the code the tests cover, install `pytest-cov` first:

```bash
pip install pytest-cov
pytest --cov=app --cov-report=term
```

| Test file | What it checks |
|-----------|----------------|
| `test_auth_register.py` | Registration, input validation, duplicate emails, bcrypt password hashing |
| `test_auth_login.py` | Login, JWT tokens, protected endpoints, role protection (401 / 403) |
| `test_security.py` | Password hashing and JWT creation and validation (unit tests) |
| `test_courses.py` | Course create, edit, delete, filters, and course ownership |
| `test_quizzes.py` | Quiz creation rules, and that correct answers are hidden from students |
| `test_quiz_submission.py` | Quiz submission, feedback, and the `/me/results` history |
| `test_scoring.py` | The scoring function (unit tests) |
| `test_health.py` | The `/health` endpoint |

These tests also run automatically in our CI pipeline. See [Continuous Integration](#continuous-integration).

## Linting and Code Style

The backend uses **[Ruff](https://docs.astral.sh/ruff/)** to check code style and catch common bugs, and to format the code consistently. Its settings live in `backend/pyproject.toml`:

- Line length of 100 characters, targeting Python 3.12.
- Rule sets: pycodestyle (`E`, `W`), Pyflakes (`F`), import sorting (`I`), flake8-bugbear (`B`), pyupgrade (`UP`), and flake8-simplify (`SIM`).

Ruff is included in `requirements.txt`. With the virtual environment activated (see [How to Run Locally](#how-to-run-locally)):

```bash
cd backend
ruff check .            # report lint errors
ruff format --check .   # report files that need formatting
```

To fix problems automatically:

```bash
ruff check . --fix      # fix the lint errors Ruff can fix safely
ruff format .           # reformat the code
```

Please make sure both `ruff check .` and `ruff format --check .` pass before opening a pull request.

## Continuous Integration

Our GitHub Actions pipeline lives in `.github/workflows/ci.yml`. The badge at the top of this README shows whether the latest run passed.

### When it runs

| Event | What runs |
|-------|-----------|
| Push to any branch except `main` | Lint, tests, then the Docker builds. The images are **published** to GitHub Container Registry |
| Pull request into `main` | Lint, tests, then the Docker builds. The images are **built only**, not published |
| Push directly to `main` | Nothing, because direct pushes are blocked. Code only reaches `main` through a pull request that already passed CI |

If you push new commits while an older run of the same branch is still going, the older run is cancelled so only the latest code is checked.

### What it checks

| Job | What it does |
|-----|--------------|
| **Lint** | Sets up Python 3.12, installs the dependencies, then runs `ruff check .` and `ruff format --check .` |
| **Test** | Runs the pytest suite with coverage on Python 3.12 and 3.13 (a version matrix) |
| **Build and publish Docker images** | Builds the backend and frontend images and publishes them to GitHub Container Registry. It starts only after Lint and Test pass |

If linting, any test, or a Docker build fails, the pipeline fails, and the pull request cannot be merged (see [Branch Protection Rules](#branch-protection-rules)). Click the ❌ next to a failed check on the pull request to open its log and see what broke. To keep runs fast, pip downloads are cached based on `backend/requirements.txt`, and Docker layers are cached with the GitHub Actions cache.

### Published Docker images

On every push to a branch other than `main`, after Lint and Test pass, the pipeline publishes both images to **GitHub Container Registry (GHCR)**:

| Image | Location |
|-------|----------|
| Backend | `ghcr.io/dankagame/smartlearn-backend` |
| Frontend | `ghcr.io/dankagame/smartlearn-frontend` |

Each image gets two tags from the commit it was built from: the full commit SHA (for example `ghcr.io/dankagame/smartlearn-backend:3f2c1a9...`) and a short one (`sha-3f2c1a9`). Pull requests only build the images, to check that they still build, and don't publish them.

The pipeline logs in to GHCR with the built-in `GITHUB_TOKEN` secret, which GitHub creates for each run and which only works while that run lasts. No password is stored in the workflow file. The `docker` job gets `packages: write` permission so it can push.

To pull an image, for example the one built from commit `3f2c1a9`:

```bash
docker pull ghcr.io/dankagame/smartlearn-backend:sha-3f2c1a9
```

New GHCR packages are private by default. To let anyone pull them without logging in, change the package visibility to public in each package's settings on GitHub.

To check your work locally before pushing, run the same commands from the `backend` folder:

```bash
ruff check .
ruff format --check .
pytest
```

## Cloud Deployment (Terraform + Ansible)

SmartLearn runs on AWS. Two tools take it from nothing to a running website:

```
 Terraform                         Ansible                          Browser
 builds the server       ──►       sets it up and deploys   ──►    http://44.200.2.73
 VPC, subnet, firewall,            SSH hardening, firewall,
 Ubuntu 24.04 EC2                  Docker, SmartLearn containers
```

| Link | What it is |
|------|------------|
| [http://44.200.2.73](http://44.200.2.73) | The live SmartLearn web app |
| [http://44.200.2.73/health](http://44.200.2.73/health) | API health check: returns `{"status":"ok","database":"connected"}` |
| [terraform/README.md](terraform/README.md) | How to build the AWS infrastructure, variables, and commands |
| [ansible/README.md](ansible/README.md) | How to configure the server and deploy the app, and how secrets are handled |
| [SECURITY.md](SECURITY.md) | Security scan results, fixes, and accepted risks |
| [Checkov workflow](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/checkov.yml) | Terraform security scan runs |
| [CI workflow](https://github.com/Dankagame/Smart-learn-Aplication/actions/workflows/ci.yml) | Lint, tests, image builds, and container scans |

### Deploy from scratch

```bash
cd terraform
terraform init
terraform apply
terraform output instance_public_ip

cd ../ansible
cp inventory/hosts.ini inventory/hosts.local.ini
ansible-galaxy collection install -r requirements.yml
ansible-playbook -i inventory/hosts.local.ini --vault-password-file smartlearn.vault.key playbook.yml
```

Put the IP from `terraform output` into `inventory/hosts.local.ini` before running the playbook. The vault password file is shared privately within the team and is never committed.

| Step | Result |
|------|--------|
| `terraform apply` | 9 AWS resources: VPC, subnet, internet gateway, route table and association, security group, locked default security group, key pair, and a `t3.micro` Ubuntu server |
| `ansible-playbook` (first run) | Server hardened, Docker installed, SmartLearn running and health-checked |
| `ansible-playbook` (second run) | `changed=0`: the playbook is idempotent |

### Who exposes what

| Port | Open to | Why |
|------|---------|-----|
| 80 | Everyone | The website. Nginx also forwards API calls to the backend |
| 22 | The admin's IP only | SSH for Terraform outputs and Ansible |
| 8000 | Nobody outside the server | The backend listens on `127.0.0.1` only |
| 5432 | Nobody outside Docker | The database stays inside the Docker network |

The server's IP changes if it is destroyed and rebuilt with Terraform. Update the links above after a rebuild. Run `terraform destroy` to delete everything when it is no longer needed.

## Security Practices

We follow a **"shift left"** approach: security is built in from the first commit, not added at the end.

- **No secrets in Git:** settings like `SECRET_KEY` and `DATABASE_URL` are read from a `.env` file, which Git ignores. Only `.env.example`, with placeholder values, is committed.
- **Comprehensive `.gitignore`:** organized by category to exclude secrets, virtual environments, caches, databases, logs, IDE files, and future Terraform state.
- **Password hashing:** passwords are hashed with bcrypt and are never stored or returned as plain text.
- **Token authentication:** protected endpoints require a JWT token, and role checks stop students from using teacher actions (and the reverse).
- **Protected `main` branch:** every change is reviewed and must pass CI before it is merged (see below).
- **Infrastructure scanning:** Checkov scans the Terraform code on every pull request, and Trivy and pip-audit scan the Docker images and Python dependencies.
- **Hardened server:** SSH accepts keys only from the admin's IP, the firewall opens only port 80, and production secrets are encrypted with Ansible Vault.

Every finding, fix, and accepted risk is documented in [SECURITY.md](SECURITY.md).

## Branch Protection Rules

The `main` branch is protected by a GitHub **ruleset** (Settings → Rules → Rulesets → `main`), so every change is reviewed and must pass CI before it reaches the main codebase. The bypass list is empty, so the rules apply to everyone.

| Rule | Why it matters |
|------|----------------|
| Require a pull request before merging | Nobody can push directly to `main`. Every change goes through a PR, so there is a clear record of what changed and why. |
| Require 1 approval | Another team member must review the code. This catches bugs early and makes sure both of us understand all of the code. |
| Dismiss stale approvals when new commits are pushed | If code changes after approval, it must be reviewed again, so unreviewed code cannot slip in. |
| Require status checks to pass before merging | The CI checks listed below must all pass before a pull request can be merged, so broken code cannot reach `main`. |
| Require branches to be up to date before merging | A PR must include the latest `main`, so it is checked against the current code and hidden conflicts are avoided. |
| Require conversation resolution before merging | Every review comment must be answered or fixed, so feedback is never ignored. |
| Include administrators | The rules apply to everyone, including the repository owner, so there are no shortcuts. |
| Block force pushes and deletion | Nobody can rewrite or delete the history of `main`. |

### Required CI checks

These four jobs from `.github/workflows/ci.yml` are **required status checks** on `main`. Each must be reported by **GitHub Actions** and must pass:

| Required check | What has to pass |
|----------------|------------------|
| `Lint` | `ruff check .` and `ruff format --check .` |
| `Test (Python 3.12)` | The full pytest suite on Python 3.12 |
| `Test (Python 3.13)` | The full pytest suite on Python 3.13 |
| `Build and publish Docker images` | The backend and frontend Docker images build successfully |

If any check fails or hasn't finished, the **Merge** button stays blocked. Fix the problem, push to the same branch, and CI runs again automatically. If you rename a job in `ci.yml`, update the required check names in the ruleset too, or pull requests will wait forever for a check that no longer exists.

## Development Workflow

1. Pick an issue from the [project board](LINK-TO-YOUR-PROJECT-BOARD) and move it to **In Progress**.
2. Create a branch from `main`, for example `feature/auth` or `issue-13-frontend-structure`.
3. Commit small, meaningful changes with clear messages.
4. Open a pull request with a description and `Closes #<issue-number>`.
5. CI runs automatically on the pull request. Fix anything it reports until all checks are green.
6. The other team member reviews the code, leaves comments, and approves it.
7. Merge the PR and delete the branch. The linked issue closes and moves to **Done**.

`.github/CODEOWNERS` automatically requests a review from the other team member on every pull request.

## Why It Fits a 6-Week DevOps Course

- **Simple in scope:** The feature set is small and well defined (accounts, courses, materials, quizzes, results), so the team can spend most of its effort on DevOps practices instead of complex application logic.
- **Meaningful:** It addresses a real problem: students preparing for national exams have limited access to organized study resources and practice.
- **Already functional:** The core flows (registering, logging in, creating a course, and taking a quiz) work today and will be improved each week.
- **Easy to containerize and deploy:** The frontend and backend are separate, and the backend is split into modules for auth, courses, and quizzes. Each part can get its own Docker image, CI pipeline, and cloud deployment, and the backend modules can later become independent **microservices**.

## Team

| Name | Role | Responsibilities |
|------|------|------------------|
| Dan Kagame | Backend Developer | FastAPI API, database, authentication, quizzes, tests |
| Fatoumata Ndiaye | Frontend Developer | Landing page, login and registration, dashboard, API integration |

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE).