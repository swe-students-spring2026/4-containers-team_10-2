![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![Web App CI](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/web-app.yml/badge.svg)](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/web-app.yml)
[![ML Client CI](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/ml-client.yml/badge.svg)](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/ml-client.yml)

# StyleSense

A containerized web application that analyzes a user's face shape from webcam input and recommends hairstyles. The system consists of three services: a Flask web app, a machine-learning client, and a MongoDB database.

---

## Team

- [Aryaman Nagpal](https://github.com/aryamann04)
- [Ani Guduru](https://github.com/AniGuduru)
- [Zheqi Zhang](https://github.com/zheqi111)

---

## Architecture

- Web App (Flask): User interface, authentication, dashboard, history
- ML Client (Python + MediaPipe): Face-shape detection and recommendations
- MongoDB: Stores users, scans, preferences, and favorites

---

## Requirements

- Docker
- Docker Compose

---

## Setup (Docker — Recommended)

1. Clone repo
git clone https://github.com/swe-students-spring2026/4-containers-team_10-2
cd 4-containers-team_10-2

2. Build containers
docker compose build

3. Start all services
docker compose up

### Environment configuration (.env files)

This project uses environment variables for configuration. The `.env` files are not committed to the repository.

You must create them from the provided examples.

#### Web App

cd web-app
cp .env.example .env

#### Machine Learning Client

cd machine-learning-client
cp .env.example .env

---

## Access the app

Web App:
http://localhost:5000

ML Client Health:
http://localhost:5001/health

DB Health:
http://localhost:5000/db-health

---

## Reset database (clean state)

docker compose down -v
docker compose up

---

## Usage

1. Open http://localhost:5000  
2. Sign up or log in  
3. Navigate to live scan  
4. Allow camera access  
5. View detected face shape and recommendations  
6. Save favorites and preferences  
7. View history and dashboard  

---

## Testing

Machine-learning client:
cd machine-learning-client
export PYTHONPATH=.
pytest
coverage run --source=app -m pytest
coverage report -m

Web app:
cd web-app
export PYTHONPATH=.
pytest
coverage run --source=app -m pytest
coverage report -m

---

## Linting & formatting

python -m black app tests
python -m pylint app tests
