# SmartLearn

> **Study smarter, even on low data.**

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
- [Running with Docker Compose](#running-with-docker-compose)
- [How to Run Locally](#how-to-run-locally)
- [Running the Tests](#running-the-tests)
- [Linting and Code Style](#linting-and-code-style)
- [Continuous Integration](#continuous-integration)
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
| | *Planned:* Docker, GitHub Actions, Terraform, cloud deployment | Containerization, CI/CD automation, infrastructure as code, and hosting, added later in the course. |

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
├── .github/CODEOWNERS
├── .gitignore
├── LICENSE
└── README.md
```

## Running with Docker Compose

SmartLearn is fully containerized with **Docker** and orchestrated using **Docker Compose**. This single command starts the PostgreSQL 16 database, the FastAPI backend, and the Nginx frontend reverse proxy on an isolated bridge network with persistent volume storage.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS) or Docker Engine & Docker Compose (Linux)

### 1. Configure environment variables and start services

Copy the example environment configuration into `.env` (Docker Compose automatically reads this file):

```bash
# On Linux / macOS / Git Bash
cp .env.example .env

# On Windows PowerShell
Copy-Item .env.example .env
```

Review the values in `.env` if you want to customize your database username or password. Then run:

```bash
docker compose up --build
```

Docker Compose will automatically:
1. Build the production multi-stage backend image (`Dockerfile`) running as non-root user `appuser`.
2. Build the lightweight production Nginx frontend image (`frontend/Dockerfile`) running as non-root user `nginx`.
3. Pull and launch PostgreSQL 16 Alpine (`postgres:16-alpine`).
4. Initialize the isolated bridge network `smartlearn-network` and persistent data volume `postgres_data`.
5. Wait for PostgreSQL and backend healthchecks before routing traffic.

### 2. Access the Application

| Service | URL | Notes |
|---|---|---|
| **Frontend Web App** | [http://localhost:5500](http://localhost:5500) | Complete learning portal, login, and dashboard (via Nginx reverse proxy) |
| **Backend REST API** | [http://localhost:8000](http://localhost:8000) | FastAPI ASGI server |
| **Interactive API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive OpenAPI documentation & testing |
| **API Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | Reports status and database connection state |
| **PostgreSQL Database** | `localhost:5432` | User: `smartlearn_user`, DB: `smartlearn_db` |

### 3. Stop services

To stop all containers:

```bash
docker compose down
```

To stop containers and reset the persistent database volume:

```bash
docker compose down -v
```

### 4. Build Individual Images

To build and run the services independently:

```bash
# Build backend container
docker build -t smartlearn-api .

# Build frontend container
docker build -t smartlearn-frontend ./frontend
```

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

Our GitHub Actions pipeline lives in `.github/workflows/ci.yml`. It runs on every push to any branch except `main`, and on every pull request into `main`.

| Job | What it does |
|-----|--------------|
| **Lint** | Sets up Python 3.12, installs the dependencies, then runs `ruff check .` and `ruff format --check .` |
| **Test** | Runs the pytest suite with coverage on Python 3.12 and 3.13 (a version matrix) |
| **Build and publish Docker images** | Builds the backend and frontend images and publishes them to GitHub Container Registry. It starts only after Lint and Test pass |

If linting, any test, or a Docker build fails, the pipeline fails, and the pull request cannot be merged. To keep runs fast, pip downloads are cached based on `backend/requirements.txt`, and Docker layers are cached with the GitHub Actions cache.

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

## Security Practices

We follow a **"shift left"** approach: security is built in from the first commit, not added at the end.

- **No secrets in Git:** settings like `SECRET_KEY` and `DATABASE_URL` are read from a `.env` file, which Git ignores. Only `.env.example`, with placeholder values, is committed.
- **Comprehensive `.gitignore`:** organized by category to exclude secrets, virtual environments, caches, databases, logs, IDE files, and future Terraform state.
- **Password hashing:** passwords are hashed with bcrypt and are never stored or returned as plain text.
- **Token authentication:** protected endpoints require a JWT token, and role checks stop students from using teacher actions (and the reverse).
- **Protected `main` branch:** every change is reviewed before it is merged (see below).

## Branch Protection Rules

The `main` branch is protected so that every change is reviewed before it reaches the main codebase.

| Rule | Why it matters |
|------|----------------|
| Require a pull request before merging | Nobody can push directly to `main`. Every change goes through a PR, so there is a clear record of what changed and why. |
| Require 1 approval | Another team member must review the code. This catches bugs early and makes sure both of us understand all of the code. |
| Dismiss stale approvals when new commits are pushed | If code changes after approval, it must be reviewed again, so unreviewed code cannot slip in. |
| Require status checks to pass before merging | Automated checks must pass before merging. Our CI pipeline runs linting, tests, and the Docker builds here, so broken code cannot reach `main`. |
| Require branches to be up to date before merging | A PR must include the latest `main`, so it is checked against the current code and hidden conflicts are avoided. |
| Require conversation resolution before merging | Every review comment must be answered or fixed, so feedback is never ignored. |
| Include administrators | The rules apply to everyone, including the repository owner, so there are no shortcuts. |

## Development Workflow

1. Pick an issue from the [project board](LINK-TO-YOUR-PROJECT-BOARD) and move it to **In Progress**.
2. Create a branch from `main`, for example `feature/auth` or `issue-13-frontend-structure`.
3. Commit small, meaningful changes with clear messages.
4. Open a pull request with a description and `Closes #<issue-number>`.
5. The other team member reviews the code, leaves comments, and approves it.
6. Merge the PR and delete the branch. The linked issue closes and moves to **Done**.

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