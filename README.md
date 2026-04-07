# 🚀 Multi-Tenant SaaS: Cloud-Native POS & Inventory System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

A comprehensive, production-ready **Software-as-a-Service (SaaS)** platform built to empower small, local businesses with a modern, fast, and easy-to-use **Point of Sale (POS)** and **Inventory Management** solution. The system is architected with a secure, multi-tenant backend and is designed for deployment on cloud infrastructure like AWS using a fully containerized CI/CD pipeline.

---

## 🌟 Key Features

This platform is more than just an inventory tracker; it's a complete business management tool designed to solve real-world problems for local retailers.

- **Secure Multi-Tenant Architecture:** Every store gets its own isolated, secure space. One store's data is completely invisible to another, ensuring privacy and data integrity.
- **High-Speed Hybrid POS System:** A user-friendly Point of Sale interface that combines:
    - **"Favorite Buttons"** for instant, one-tap billing of frequently sold items during peak hours.
    - **Barcode Scanning** support for quick and accurate product entry.
- **"Bakir Khata" (Digital Due Ledger):** A powerful feature to manage customer credit. Track dues, record payments, and send reminders to customers via SMS or WhatsApp intents directly from the app.
- **Smart Global Product Catalog:** Drastically reduces manual data entry. Scanning a common branded product (like a Coke bottle) automatically fetches its name and price from a global catalog, which the owner can then customize.
- **Role-Based Staff Management:** `Store_Owner` and `Staff` roles with different permissions. Owners have full control, while staff can only manage sales, preventing unauthorized access to sensitive business data.
- **Business Intelligence Dashboard:** An insightful dashboard providing real-time analytics on daily sales, total outstanding dues, top-selling products, and low-stock alerts.

---

## 🏗️ System Architecture

The application follows a robust, scalable, and containerized 3-tier architecture orchestrated by Docker Compose.

```mermaid
graph LR
    subgraph "Browser / PWA (Next.js)"
        User[Shop Owner / Staff]
    end

    subgraph "Cloud Infrastructure (AWS EC2)"
        Nginx[Nginx Reverse Proxy]
        subgraph "Docker Containers"
            WebApp[Django + Gunicorn]
            DB[(PostgreSQL)]
            Cache[(Redis)]
        end
    end

    subgraph "DevOps & CI/CD"
        CI[GitHub Actions: Test, Lint, Build]
    end

    User -- HTTPS Request --> Nginx
    Nginx -- Serves Static Files --> User
    Nginx -- Proxy Pass --> WebApp
    WebApp -- Read/Write --> DB
    WebApp -- Caching --> Cache
    CI -- Pushes to --> Docker Hub
    CI -- Deploys on --> AWS EC2
```

---

## 🛠️ Tech Stack

| Category      | Technology                                                                                                   |
|---------------|--------------------------------------------------------------------------------------------------------------|
| **Backend**       | Python, Django, Django REST Framework                                                                        |
| **Database**      | PostgreSQL (Primary), Redis (Caching)                                                                       |
| **API & Auth**  | RESTful API, JWT (djangorestframework-simplejwt), Swagger/OpenAPI (drf-spectacular)                          |
| **DevOps**        | Docker, Docker Compose, Nginx, Gunicorn, GitHub Actions (CI/CD)                                                |
| **Cloud**         | AWS EC2                                                                                                      |
| **Testing**       | Pytest, Pytest-Django                                                                                        |

---

## ⚙️ Local Setup & Installation

To get the project running locally, ensure you have **Docker** and **Docker Compose** installed.

### 1. Clone the Repository
```bash
git clone https://github.com/[your-github-username]/[your-repo-name].git
cd [your-repo-name]
```

### 2. Create Environment Variables
Create a `.env` file in the project root by copying the example file.
```bash
cp .env.example .env
```
Now, open the `.env` file and fill in the necessary variables (default values are mostly fine for local development).

### 3. Build and Run the Containers
```bash
docker-compose up --build -d
```
This command will build the Docker images and start all the services (Django, Nginx, PostgreSQL, Redis) in detached mode.

### 4. Apply Database Migrations
```bash
docker-compose exec web python manage.py migrate
```

### 5. Create a Superuser (for Admin Panel)
```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Access the Application
- **API (Swagger UI):** [http://localhost/api/docs/](http://localhost/api/docs/)
- **Admin Panel:** [http://localhost/admin/](http://localhost/admin/)

### 7. Run Tests
```bash
docker-compose exec web pytest
```

---

## 👨‍💻 Author

**Abdullah Al Noman**

- **GitHub:** `[https://www.linkedin.com/in/abdullah-al-noman-772999376/](url)`
- **LinkedIn:** `https://www.linkedin.com/in/abdullah-al-noman-772999376/`
