# DevOpsVaultX 🚀

**DevOpsVaultX** is a Django-based digital product platform tailored for **DevOps & Cloud Engineers**.  
It provides high-quality **Guides, Tools, and Templates** with secure payment integration and instant downloadable content.

This project leverages **Django + Django REST Framework (DRF)** with **PostgreSQL**, Razorpay integration, and a sleek HTML/CSS frontend with a robust admin control center.

---

## 📌 Project Overview

DevOpsVaultX enables users to:
- 🛒 Browse DevOps-specific digital products & categories.
- 🔍 View detailed product specifications.
- 💳 Make secure payments via **Razorpay**.
- 📥 Access instant downloads after successful purchase.
- 📞 Connect with the team via integrated static pages.

**Target Audience:**
- DevOps & Cloud Engineers
- SREs (Site Reliability Engineers)
- Freshers & Learners entering the DevOps ecosystem.

---

## 🛠 Tech Stack

- **Backend:** Django, Django REST Framework (DRF)
- **Database:** PostgreSQL
- **Frontend:** HTML5, CSS3, JavaScript (Django Templates)
- **Authentication:** Django Built-in Auth
- **Payments:** Razorpay API
- **Monitoring:** OpenSearch & Fluent Bit
- **Deployment Ready:** Docker / Azure / Nginx

---

## ✨ Key Features

- ✅ **Product Management:** Categorized listings with secure file handling.
- ✅ **Seamless Payments:** Integrated Razorpay checkout flow.
- ✅ **Admin Dashboard:** Full control over products, orders, and users.
- ✅ **Observability:** Centralized logging using the OpenSearch stack.
- ✅ **SEO Optimized:** Clean URLs and responsive design.

---

## 🏗 Architecture & Workflow



### **The Flow:**
`User` ➔ `UI` ➔ `Django Backend` ➔ `PostgreSQL` ➔ `Razorpay API` ➔ `Order Verification` ➔ `Download Access`

---
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
[INPUT]
    Name           tail
    Path           /path/to/your/DevOpsVaultX_App/logs/*.log
    Tag            devopsvaultx.app

[OUTPUT]
    Name           opensearch
    Match          *
    Host           127.0.0.1
    Port           9200
    Index          devopsvaultx
    HTTP_User      admin
    HTTP_Passwd    admin
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

## 👨‍💻 Authors

**Sachin Thokal**  
DevOps Engineer | Azure | Kubernetes | Docker  

**Pallavi Pawar**  
DBOps Engineer | PostgreSQL | Python | PySpark | Django  

---
## 📄 License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
---
