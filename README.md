![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![Web App CI](https://github.com/swe-students-spring2026/4-containers-team_10-2/actions/workflows/web-app.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-team_10-2/actions/workflows/web-app.yml)
[![ML Client CI](https://github.com/swe-students-spring2026/4-containers-team_10-2/actions/workflows/ml-client.yml/badge.svg)](https://github.com/swe-students-spring2026/4-containers-team_10-2/actions/workflows/ml-client.yml)

# StyleSense

A containerized web application that analyzes a user's face shape from webcam input and recommends hairstyles. The system consists of three services: a Flask web app, a machine-learning client, and a MongoDB database.

---

## Team

- [Aryaman Nagpal](https://github.com/aryamann04)
- [Ani Guduru](https://github.com/AniGuduru)
- [Zheqi Zhang](https://github.com/zheqi111)

---

## Architecture

| Service | Technology | Role |
|---|---|---|
| Web App | Flask | User interface, authentication, dashboard, history |
| ML Client | Python + MediaPipe | Face-shape detection and recommendations |
| Database | MongoDB | Users, scans, preferences, and favorites |

---

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/swe-students-spring2026/4-containers-team_10-2
cd 4-containers-team_10-2
```

### 2. Configure environment variables

The `.env` files are not committed to the repository. Create them from the provided examples.

**Web App:**

```bash
cd web-app
cp .env.example .env
cd ..
```

**Machine Learning Client:**

```bash
cd machine-learning-client
cp .env.example .env
cd ..
```

### 3. Build and start all services

```bash
docker compose build
docker compose up
```

---

## Access the app

| Service | URL |
|---|---|
| Web App | http://localhost:5000 |
| ML Client health | http://localhost:5001/health |
| DB health | http://localhost:5000/db-health |

---

## Usage

1. Open [http://localhost:5000](http://localhost:5000)
2. Sign up or log in
3. Navigate to **Live Scan**
4. Allow camera access
5. View your detected face shape and hairstyle recommendations
6. Save favorites and preferences
7. View scan history on the dashboard

---

## Reset the database

```bash
docker compose down -v
docker compose up
```

---

## Testing

**Machine Learning Client:**

```bash
cd machine-learning-client
export PYTHONPATH=.
pytest
coverage run --source=app -m pytest
coverage report -m
```

**Web App:**

```bash
cd web-app
export PYTHONPATH=.
pytest
coverage run --source=app -m pytest
coverage report -m
```

---

## Linting and formatting

```bash
python -m black app tests
python -m pylint app tests
```