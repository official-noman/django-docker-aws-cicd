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
    Web -- Logs/Monitor --> GitHub[GitHub Actions CI/CD]
