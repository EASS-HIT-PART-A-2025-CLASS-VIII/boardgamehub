# BoardGameHub 🎲

A full **CRUD API** and **dashboard application** built with **FastAPI**, **SQLModel**, and **SQLite**.
The project allows users to **create, list, update, and delete board games** through clean REST endpoints and a user-friendly **Streamlit** interface.
It supports **Dockerized deployment**, **health monitoring**, and **automated testing**.

---

## 🧭 Project Overview

| Component             | Description                                                    |
| --------------------- | -------------------------------------------------------------- |
| **Backend Framework** | **FastAPI** – high-performance Python REST API framework       |
| **ORM Layer**         | **SQLModel** – combines SQLAlchemy and Pydantic                |
| **Database**          | **SQLite** – lightweight file-based relational database        |
| **Frontend**          | **Streamlit** – interactive dashboard for managing board games |
| **HTTP Client**       | **httpx** – API communication layer used by the frontend       |
| **Environment Tool**  | **uv** – fast Python package and environment manager           |
| **Testing**           | **pytest** + FastAPI TestClient                                |
| **CLI Utility**       | **Typer** – database initialization and demo data seeding      |
| **Deployment**        | **Docker** + **Docker Compose**                                |
| **Health Monitoring** | `/health` endpoint + Docker healthcheck                        |

---

## 📁 Project Structure

```bash
BoardGameHub/
│
├── app/                    
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── routers/
│       └── boardgames.py
│
├── frontend/               
│   ├── client.py           
│   └── dashboard.py        
│
├── tests/                  
│
├── cli.py                  
├── Dockerfile              
├── Dockerfile.frontend     
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## 🔗 API Endpoints

| Method | Endpoint           | Description                   |
| ------ | ------------------ | ----------------------------- |
| POST   | `/boardgames/`     | Create a new board game       |
| GET    | `/boardgames/`     | Retrieve all board games      |
| GET    | `/boardgames/{id}` | Retrieve a board game by ID   |
| PUT    | `/boardgames/{id}` | Update an existing board game |
| DELETE | `/boardgames/{id}` | Delete a board game           |
| GET    | `/health`          | API and database health check |

---

## 🚀 Run Locally

### Install dependencies

```bash
uv sync
uv pip install -e .
```

### Run the backend

```bash
uv run uvicorn app.main:app --reload
```

* API docs → [http://localhost:8000/docs](http://localhost:8000/docs)
* Health check → [http://localhost:8000/health](http://localhost:8000/health)

### Run the frontend

```bash
uv run streamlit run frontend/dashboard.py
```

* Dashboard → [http://localhost:8501](http://localhost:8501)

---

## 🌱 Database Seeding (CLI)

### Seed the database (one-time)

Populate the database with sample board games:

```bash
uv run python -m cli seed
```

---

## 🧪 Running Tests

```bash
uv run pytest
```
**Expected output:**
8 passed in X.XXs

---

## 🐳 Docker Support

Build and run the entire system:

```bash
docker compose up --build
```

Services:

* API docs → [http://localhost:8000/docs](http://localhost:8000/docs)
* Health check → [http://localhost:8000/health](http://localhost:8000/health)
* Frontend → [http://localhost:8501](http://localhost:8501)

Check container health:

```bash
docker compose ps
```

Expected backend status:

```
(healthy)
```
### Close down Docker:
```bash
docker compose down
```
---