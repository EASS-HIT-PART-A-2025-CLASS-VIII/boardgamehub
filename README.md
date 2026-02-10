# BoardGameHub 🎲

A full **CRUD API** and **dashboard application** built with **FastAPI**, **SQLModel**, and **SQLite**.
The project allows users to **create, list, update, and delete board games** through clean REST endpoints and a user-friendly **Streamlit** interface.
It supports **Dockerized deployment**, **secure JWT authentication**, **advanced API features** (pagination, rate limiting, caching, CSV export), and **real-time statistics counters**.

---

## 🧭 Project Overview

| Component             | Description                                                    |
| --------------------- | -------------------------------------------------------------- |
| **Backend Framework** | **FastAPI** – high-performance Python REST API framework       |
| **ORM Layer**         | **SQLModel** – combines SQLAlchemy and Pydantic                |
| **Database**          | **SQLite** – lightweight file-based relational database        |
| **Frontend**          | **Streamlit** – interactive dashboard for managing board games |
| **Security**          | **JWT** + **Bcrypt** – secure authentication and password hashing |
| **Tooling**           | **Ruff** (linting), **Mypy** (typing), **MkDocs** (documentation) |
| **Rate Limiting**      | **SlowAPI** – protects API from brute-force and abuse          |
| **Deployment**        | **Docker** + **Docker Compose**                                |

---

## ✨ Key Features

- **"The Board Room" Dashboard**:
    - **Visual Analytics**: Interactive Rating vs Complexity charts.
    - **KPI Metrics**: Dynamic stats that update based on your filters.
    - **Server-Side Filtering**: Search and filter (Solo/Duel) across the entire database.
- **Secure Authentication**: Role-based access control using JWT tokens and Bcrypt password hashing.
- **Advanced Data Retrieval**: 
    - **Pagination**: Efficiently browse large datasets (`?page=1&page_size=50`).
    - **Rate Limiting**: Integrated protection with `X-RateLimit` headers.
    - **CSV Export**: High-performance data export (`?format=csv`).
    - **Caching**: ETag support for bandwidth optimization (`304 Not Modified`).
- **Real-time Stats**: Redis-backed statistics and background worker for metric refreshing.

---

## 📁 Project Structure

```bash
BoardGameHub/
│
├── app/                    # Backend application
│   ├── routers/            # API endpoints (auth, boardgames, stats)
│   ├── crud.py             # Database operations
│   ├── models.py           # SQLModel database schemas
│   └── security.py         # JWT and password handling
│
├── frontend/               # Streamlit dashboard
├── docs/                   # Documentation (MkDocs)
├── scripts/                # Utility scripts (refresh, worker)
├── tests/                  # Pytest suite
├── Dockerfile              # Backend container
├── Dockerfile.frontend     # Frontend container
├── docker-compose.yml      # Orchestration
├── mkdocs.yml              # Documentation config
└── pyproject.toml          # Dependencies and project config
```

---

## 🔗 API Endpoints

| Method | Endpoint           | Description                   |
| ------ | ------------------ | ----------------------------- |
| POST   | `/auth/token`      | Login and get access token    |
| GET    | `/boardgames/`     | List games (supports pagination & CSV) |
| POST   | `/boardgames/`     | Create a new board game       |
| POST   | `/boardgames/upload`| Bulk upload games from CSV    |
| GET    | `/boardgames/{id}` | Retrieve a board game by ID   |
| PUT    | `/boardgames/{id}` | Update an existing board game |
| DELETE | `/boardgames/{id}` | Delete a board game           |
| GET    | `/stats`           | Get cached statistics         |

---

## 🚀 Run Locally

### 1. Install dependencies
```bash
uv sync
```

### 2. Run the backend
```bash
uv run uvicorn app.main:app --reload
```
* API docs → [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run the frontend
```bash
uv run streamlit run frontend/dashboard.py
```
* Dashboard → [http://localhost:8501](http://localhost:8501)
    * **Note**: To Create, Edit, or Delete games, use the **🔐 Admin Access** section in the sidebar (login with `admin`/`admin123`).

### 🎯 Local Demo
This script walks you through the entire project flow (API + Frontend + Feature Demo):
```bash
uv run python -m app.demo
```

### 🛠️ CLI Database Management
Use the CLI for administrative tasks like seeding sample data:
```bash
uv run python cli.py seed   # Seed with 5 sample games
uv run python cli.py reset  # Wipe and recreate database
```

---

## 📚 Documentation & Quality
**View Documentation:**
```bash
uv run mkdocs serve
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to view the full project documentation.

**Run Quality Checks:**
```bash
uv run ruff check .   # Linting
uv run mypy app       # Type checking
uv run pytest         # Tests
```

---

## 🐳 Docker Support

Build and run the entire system:
```bash
docker compose up --build
```

**Once running, access the services here:**
*   **Dashboard**: [http://localhost:8501](http://localhost:8501)
*   **API & Documentation**: [http://localhost:8000](http://localhost:8000) (auto-redirects to /docs)

---

## 🔐 Setup & Configuration

### 1. Environment Variables
This project requires an `.env` file for secrets.

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```
2. The default configuration uses:
   - **Username:** `admin`
   - **Password:** `admin123`

### 2. Changing the Password (Optional)
To use a different password, generate a new Bcrypt hash and update `BOARDGAME_ADMIN_PASSWORD_HASH` in `.env`:
```bash
# Run this command to generate a hash for "my-new-password"
uv run python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt'], deprecated='auto').hash('my-new-password'))"
```
