
# 🚀 Cloud-Native Inventory Management API

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

A production-ready **3-Tier REST API** built with Django & PostgreSQL, containerized with Docker, served via Nginx Reverse Proxy, and deployed on AWS EC2 with fully automated CI/CD pipelines.

---

## 🏗 Architecture
The system follows a microservices-style architecture orchestrated by Docker Compose:

```mermaid
graph LR
    User[User / Client] -- HTTP Request --> Nginx[Nginx Reverse Proxy]
    Nginx -- Forward Request --> Web[Django + Gunicorn]
    Web -- Read/Write Data --> DB[(PostgreSQL Database)]
    Web -- Logs/Monitor --> GitHub[GitHub Actions CI/CD] ```
 
🌟 Key Features

Containerization: Fully Dockerized environment (Web, DB, Nginx) ensuring consistency across Dev and Prod.

Reverse Proxy: Nginx configured as a gateway for security and static file handling.

CI/CD Automation: GitHub Actions pipeline triggers on every push to build Docker images.

Database Persistence: Uses Docker Volumes to persist PostgreSQL data.

Optimization: Configured Swap Memory on AWS EC2 (t2.micro) to prevent OOM crashes.

Resilience: Implemented healthchecks to prevent race conditions between Django and Database.

Dynamic DNS: Integrated with DuckDNS for consistent domain access.

🛠 Tech Stack

Backend: Python, Django REST Framework

Server: Gunicorn (WSGI)

Database: PostgreSQL 13

Infrastructure: AWS EC2 (Ubuntu 22.04 LTS)

DevOps: Docker, Docker Compose, GitHub Actions, Nginx, Linux Administration

⚙️ Installation & Local Setup
Prerequisites

Docker & Docker Compose installed

Git installed

Steps

Clone the repository

code
Bash
download
content_copy
expand_less
git clone https://github.com/official-noman/django-docker-aws-cicd.git
cd django-docker-aws-cicd

Create Environment Variables
Create a .env file in the root directory:

code
Env
download
content_copy
expand_less
SECRET_KEY=dev-secret-key
DEBUG=True
DB_NAME=devops_inventory
DB_USER=hello_django
DB_PASSWORD=supersecret
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=*

Build and Run

code
Bash
download
content_copy
expand_less
docker-compose up -d --build

Apply Migrations

code
Bash
download
content_copy
expand_less
docker-compose exec web python manage.py migrate

Access the API

Health Check: http://localhost/api/health/

Product Inventory: http://localhost/api/products/

🚀 API Endpoints
Method	Endpoint	Description
GET	/api/health/	Check system status (DevOps health check)
GET	/api/products/	Retrieve list of all products
POST	/api/products/	Create a new product (JSON body required)

Sample JSON for POST:

code
JSON
download
content_copy
expand_less
{
  "name": "Gaming Laptop",
  "price": "120000.00",
  "quantity": 5
}
☁️ Deployment Details (AWS)

This project is deployed on an AWS EC2 t2.micro instance.

Optimization for Low Memory (1GB RAM)

To handle the load of 3 containers on a free-tier instance, a 2GB Swap File was configured:

code
Bash
download
content_copy
expand_less
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
Nginx Configuration

Nginx is set up to listen on Port 80 and forward traffic to the Django container on Port 8000 using proxy_pass.

👨‍💻 Author
Abdullah Al Noman

