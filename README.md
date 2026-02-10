# BoardGameHub 🎲

A full **CRUD API** and **dashboard application** built with **FastAPI**, **SQLModel**, and **SQLite**.
The project allows users to **create, list, update, and delete board games** through clean REST endpoints and a user-friendly **Streamlit** interface.
It supports **Dockerized deployment**, **secure JWT authentication**, **advanced API features** (pagination, caching, CSV export), and **FastMCP integration** for AI agents.

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
| **AI Integration**    | **FastMCP** – Model Context Protocol tool for AI agents        |
| **Deployment**        | **Docker** + **Docker Compose**                                |

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

---

## ✨ Key Features

- **"The Board Room" Dashboard**:
    - **Visual Analytics**: Visual Analytics Chart (Rating vs Complexity).
    - **KPI Metrics**: Real-time stats for Total Games, Avg Rating, and Playtime.
- **Secure Authentication**: Role-based access control using JWT tokens and Bcrypt password hashing.
- **Advanced Data Retrieval**: 
    - **Pagination**: Efficiently browse large datasets (`?page=1&page_size=10`).
    - **CSV Export**: Download data directly (`?format=csv`).
    - **Caching**: ETag support for bandwidth optimization (`304 Not Modified`).
- **Real-time Stats**: Redis-backed statistics dashboard.
- **Automated Quality**: Integrated `pre-commit` hooks for linting, testing, and documentation.

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

### 🎯 Local Demo (Grader Version)
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