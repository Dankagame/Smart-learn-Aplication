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
- [Why It Fits a 6-Week DevOps Course](#why-it-fits-a-6-week-devops-course)
- [Running the Tests](#running-the-tests)

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

## Why It Fits a 6-Week DevOps Course

- **Simple in scope:** The feature set is small and well defined (accounts, courses, materials, quizzes, results), so the team can spend most of its effort on DevOps practices instead of complex application logic.
- **Meaningful:** It addresses a real problem: students preparing for national exams have limited access to organized study resources and practice.
- **Already functional:** The core flows (registering, logging in, creating a course, and taking a quiz) can be demonstrated early and then improved each week.
- **Easy to containerize and deploy:** The frontend and backend are separate, and the backend is split into modules for auth, courses, and quizzes. Each part can get its own Docker image, CI pipeline, and cloud deployment, and the backend modules can later become independent **microservices**.

## Running the Tests

The backend has an automated test suite written with **pytest**. The tests use a temporary in-memory SQLite database, so they don't need PostgreSQL and never touch real data.

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
pytest
```

To see how much of the code the tests cover:

```bash
pytest --cov --cov-report=term
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

All tests must pass before a pull request is merged into `main`.
