# DevOpsVaultX 🚀

**DevOpsVaultX** is a Django-based digital product platform built for **DevOps & Cloud Engineers**.  
It provides high-quality **Guides, Tools, and Templates** with secure payments and downloadable content.

This project is built using **Django + Django REST Framework (DRF)** with **PostgreSQL**, Razorpay payment integration, and a clean HTML/CSS frontend with admin control.

---

## 📌 Project Overview

DevOpsVaultX allows users to:
- Browse DevOps-related digital products
- View product details
- Make secure payments using **Razorpay**
- Download purchased content
- Contact the team and learn about products via static pages

**Target Audience**
- DevOps Engineers
- Cloud Engineers
- SREs
- Freshers entering DevOps
- DevOps Learner's

## 🛠 Tech Stack

- **Backend:** Django, Django REST Framework (DRF)
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript (Django Templates)
- **Authentication:** Django Auth
- **Payments:** Razorpay
- **Media Storage:** Local Media (Product Images & Files)
- **Admin Control:** Django Admin (Superuser)
- **Deployment Ready:** Docker / Azure / Nginx

## ✨ Features

- Product Listing & Categories
- Secure Digital File Downloads
- Razorpay Payment Flow
- Order & Payment
- Admin Panel for Product & Order Management
- Static Pages (About, Contact, Sitemap)
- Responsive UI using HTML/CSS
- SEO-friendly URLs


## 📂 Updated Project Structure

```
DevOpsVaultX_App/
|-- db_monitor
|-- devopsvaultx
|-- media
|-- pages
|-- payments
|-- products
|-- static
|-- templates
```

## Razorpay Payment Flow

1. User selects a product
2. Order created in backend
3. Razorpay Checkout opens
4. Payment success callback
5. Payment verification
6. Order marked as PAID
7. Download enabled


## DevOpsVaultX Deployment Guide
```bash
## Local Deployment
- Python 3.10+
- PostgreSQL
- Virtualenv

## Docker (Planned)
- Dockerfile
- docker-compose.yml

## Cloud Deployment (Planned)
- Azure VM / App Service
- Nginx as Reverse Proxy
- Gunicorn as WSGI server
```

## DevOpsVaultX Architecture
```bash
## Components
- Frontend: Django Templates
- Backend: Django + DRF
- Database: PostgreSQL
- Payments: Razorpay
- Media: Local Storage

## Flow
User -> UI -> Backend API -> Database -> Razorpay
```

## DevOpsVaultX API Documentation

```bash
This document describes the REST APIs used in DevOpsVaultX.

## Authentication APIs
- POST /api/register/
- POST /api/login/
- POST /api/logout/

## Product APIs
- GET /api/products/
- GET /api/products/<id>/

## Order & Payment APIs
- POST /api/orders/create/
- POST /api/payments/verify/

All APIs are secured using Django Authentication.

```

## ⚙️ Installation & Setup

```bash
git clone https://github.com/your-username/devopsvaultx.git
cd DevOpsVaultX_App
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 👨‍💻 Authors

**Sachin Thokal**  
DevOps Engineer | Azure | Kubernetes | Docker  

**Pallavi Pawar**  
DBOps Engineer | PostgreSQL | Python | PySpark | Django  

---


## 📄 License

This project is licensed for personal and educational use.

---
