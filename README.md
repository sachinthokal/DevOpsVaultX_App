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

```bash

DevOpsVaultX_App/
|-- db_monitor                  # DB Health system for admin
|   |-- migrations
|   |-- static                  # html/css files
|   |   `-- db_monitor
|   |       `-- css
|   |-- templates
|   |   `-- admin
|   `-- utils                   # utility files
|-- devopsvaultx                # main project settings
|-- pages                       # main project pages (home, about, contact)
|   |-- migrations
|   |-- static
|   |   |-- images
|   |   `-- pages
|   |       `-- css
|   `-- templates
|       `-- pages
|-- payments                    # main apps
|   |-- migrations
|   |-- static
|   |   `-- payments
|   |       |-- css
|   |       `-- js
|   `-- templates
|       `-- payments
|-- products                    # main apps
|   |-- migrations
|   |-- static
|   |   `-- products
|   |       |-- css
|   |       |-- images
|   |       `-- js
|   `-- templates
|       `-- products
|-- static                      # main css/js/images files
|   |-- css
|   |-- images
|   `-- js
`-- templates                   # main html files

```

## 💳 Razorpay Payment Flow

1. User selects a product
2. Order created in backend
3. Razorpay Checkout opens
4. Payment success callback
5. Payment verification
6. Order marked as PAID
7. Download enabled


## ⚙️ DevOpsVaultX Deployment Guide
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

## 🏗 DevOpsVaultX Architecture
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

## 📝 Logging & Monitoring Setup

DevOpsVaultX uses **OpenSearch** as the centralized logging system and **Fluent Bit** as the log shipper to collect application logs from Django and send them to OpenSearch for monitoring and analysis.

### 🔹 Components

- **Fluent Bit**: Lightweight log forwarder
- **OpenSearch**: Search & analytics engine (fork of Elasticsearch)
- **OpenSearch Dashboards**: Visualization and monitoring UI

### 🔹 Fluent Bit Setup (Windows / Local)

**1️⃣ Install Fluent Bit**
Download from [Fluent Bit official site](https://fluentbit.io/download/).

**2️⃣ Configure `fluent-bit.conf`**

```ini
[SERVICE]
    Flush        5
    Log_Level    info
    Daemon       off
    Parsers_File parsers.conf

[INPUT]
    Name           tail
    Path           D:/Sachin/Projects/DevOpsVaultX_App/logs/*.log
    Tag            devopsvaultx.app
    Read_from_Head true

[OUTPUT]
    Name           opensearch
    Match          *
    Host           192.168.1.50
    Port           9200
    Index          devopsvaultx
    Type           _doc
    HTTP_User      opensearch_username
    HTTP_Passwd    opensearch_password
```

> 💡 **Tip:** Avoid hardcoding the `Path` by using environment variables if deploying across multiple environments.

**3️⃣ Start Fluent Bit**

```powershell
$ Start-Service -Name FluentBit
$ Stop-Service -Name FluentBit

OR

$ cd C:\fluent-bit\bin
$ .\fluent-bit.exe -c C:\fluent-bit\conf\fluent-bit.conf

```

Check logs for connection and parsing errors.

---

## 🔹 OpenSearch Setup


**1️⃣ Install OpenSearch**
Download [OpenSearch 3.x](https://opensearch.org/downloads.html) or use Docker:

```bash
docker run -d --name opensearch \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  opensearchproject/opensearch:3.4.0
```

**2️⃣ Install OpenSearch Dashboards**

```bash
docker run -d --name os-dashboards \
  -p 5601:5601 \
  --link opensearch:opensearch \
  opensearchproject/opensearch-dashboards:3.4.0
```

**3️⃣ Verify Connection**
- Open: `http://localhost:9200` → Should return cluster info  
- Open Dashboards: `http://localhost:5601` → Login and visualize logs

## ⚙️ Integration Flow

```text
Django App Logs → Local log files → Fluent Bit → OpenSearch → OpenSearch Dashboards
```

- All application logs (info, error, debug) can be viewed in **OpenSearch Dashboards**.
- Helps monitor **payments**, **product views**, and **server errors**.

### 🔹 Tips for Production

- Use **Docker Compose** to deploy **OpenSearch + Dashboards + Fluent Bit** together.
- Secure OpenSearch with **user authentication**.
- Rotate logs and manage disk space using **Fluent Bit buffering**.
- Optionally, integrate with **Grafana** for advanced dashboards.

## 🛠 Installation & Setup

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
