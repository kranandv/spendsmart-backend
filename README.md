# SpendSmart — Backend API

> A secure REST API for personal expense tracking, built with FastAPI and PostgreSQL.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Live Demo

| Service | URL |
|---|---|
| Frontend App | https://spendsmart-frontend-5q27.onrender.com/login.html |
| Backend API Docs | https://spendsmart-backend.onrender.com/docs |

> **Note:** Hosted on Render free tier. Server may take 30–60 seconds to wake up on first visit.

---

## What is SpendSmart?

SpendSmart is a full-stack personal expense tracker that allows users to:

- Register and login securely using JWT authentication
- Add, edit, and delete personal expenses
- Categorize expenses (Food, Transport, Bills, Health, etc.)
- Filter expenses by category and date range
- View a monthly spending summary by category
- Visualize spending through an interactive chart on the dashboard

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.128.0 |
| Language | Python 3.11+ |
| Database | PostgreSQL (hosted on Render) |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT (python-jose + passlib + bcrypt) |
| Migrations | Alembic |
| Deployment | Render.com |

---

## Project Structure

```
spendsmart-backend/
├── main.py            # App entry point, middleware, router registration
├── database.py        # Database connection and session setup
├── models.py          # SQLAlchemy ORM models (User, Expense)
├── routers/
│   ├── auth.py        # Register and login endpoints
│   └── expenses.py    # CRUD + filter + summary endpoints
└── requirements.txt   # All dependencies
```

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |

### Expenses (Protected — requires Bearer token)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/expenses` | Get all expenses of logged-in user |
| POST | `/expenses` | Add a new expense |
| PUT | `/expenses/{id}` | Edit an expense |
| DELETE | `/expenses/{id}` | Delete an expense |
| GET | `/expenses/summary` | Monthly total per category |
| GET | `/expenses/filter` | Filter by category and/or date range |

Full interactive API documentation available at: `https://spendsmart-backend.onrender.com/docs`

---

## Run Locally

### Prerequisites
- Python 3.11+
- PostgreSQL installed and running

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/kranandv/spendsmart-backend.git
cd spendsmart-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in root directory
```

Create a `.env` file with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/spendsmart
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

```bash
# 5. Run the application
uvicorn main:app --reload

# API will be available at: http://localhost:8000
# Interactive docs at:      http://localhost:8000/docs
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Secret key for JWT token signing |
| `ALGORITHM` | JWT algorithm (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry duration |

---

## Frontend Repository

The frontend for this project is available at:
https://github.com/kranandv/spendsmart-frontend

---

## Author

**Anand** — IT Professional | Python & FastAPI Developer
- GitHub: [@kranandv](https://github.com/kranandv)
