# URL Scraper API

This project allows users to upload a CSV file containing URLs, scrape metadata (title, description, keywords), and store results securely using FastAPI, PostgreSQL, Redis, and Celery.

## 🚀 Features
- **User Authentication** (OAuth2 + Access Tokens)
- **Upload CSV** containing URLs
- **Scrape Metadata** asynchronously using Celery workers
- **Store Data** in PostgreSQL Cloud
- **Monitor Performance** using Prometheus + Grafana
- **Deploy** via Docker
- **CI/CD** automated using GitHub Actions (Deploys Docker image to DockerHub)

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository
```sh
git clone <repo_url>
cd url-scraper
```

### 2️⃣ Setup Environment Variables
Create a `.env` file with the following:
```
DATABASE_URL=your_postgresql_cloud_url
REDIS_URL=your_redis_cloud_url
```

For **local development**, use:
```
DATABASE_URL=your_postgresql_cloud_url
REDIS_URL=redis://localhost:6379/0
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Start Local Redis (for development)
```sh
docker-compose up -d redis
```

### 5️⃣ Start FastAPI Server using Docker Compose
```sh
docker-compose up --build
```

---

## 🚀 Running Celery Workers
Celery is used for **asynchronous scraping**.
```sh
celery -A utils.celery_worker.celery_app worker --loglevel=info
```

To monitor tasks, start the Celery Flower dashboard:
```sh
celery -A utils.celery_worker.celery_app flower
```

---

## 📡 API Endpoints

### 🔐 Authentication (OAuth2 + Access Tokens)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get access token |
| POST | `/auth/token` | OAuth2 token authentication |

### 📤 Upload & Scraping
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload-csv/` | Upload a CSV file of URLs |
| GET | `/task-status/{task_id}` | Check scraping task status |
| GET | `/results/{task_id}` | View scraped data from task_id |
| GET | `/urls` | View scraped metadata of a user |

---

## 🏗️ Deployment

### 1️⃣ Docker Setup (Local)
```sh
docker-compose up --build
```

### 2️⃣ Deploy on Render.com
- **Deployed URL:** [CSV URL Metadata Scraper](https://csv-url-metadata-scraper.onrender.com)
- Create a **PostgreSQL database** and get the `DATABASE_URL`
- Deploy using Render's **FastAPI template**

### 3️⃣ Docker Image on DockerHub
Our Docker image is automatically built and pushed to DockerHub on every CI/CD pipeline execution:
- **DockerHub URL:** [anotherpersonwhodontknow/url_scraper](https://hub.docker.com/r/anotherpersonwhodontknow/url_scraper)

To pull and run the image locally:
```sh
docker pull anotherpersonwhodontknow/url_scraper
```
```sh
docker run -p 8000:8000 anotherpersonwhodontknow/url_scraper
```

---

## 📊 Monitoring (Prometheus + Grafana)
### 1️⃣ Start Prometheus
```sh
docker run -d --name=prometheus -p 9090:9090 prom/prometheus
```

### 2️⃣ Start Grafana
```sh
docker run -d --name=grafana -p 3000:3000 grafana/grafana
```

### 3️⃣ Configure Dashboards
- Add **Prometheus** as a data source in Grafana.
- Create dashboards for **API request count** and **error rates**.

---

## 📜 License
This project is open-source and available under the MIT License.
