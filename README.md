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
- [How to Run Locally](#how-to-run-locally)
- [Running the Tests](#running-the-tests)
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

For now, we run the tests before every merge into `main`. In Formative 2, our CI pipeline will run them automatically on every pull request as a required status check.

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
| Require status checks to pass before merging | Automated checks must pass before merging. Our CI pipeline (Formative 2) will run the tests here, so broken code cannot reach `main`. |
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