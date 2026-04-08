# 🚀 FIX Log Analyzer – CI/CD Pipeline Project

This project demonstrates a production-style CI/CD pipeline for deploying a Python-based log analysis service using Jenkins, Docker, and shell automation.

The application is a FIX (Financial Information eXchange) log analyzer that parses trading logs and provides insights such as logon/logout tracking, market data requests, and quote-level analysis.

---

## 📌 Project Overview

* Built a Flask-based web application to analyze FIX 4.4 logs
* Containerized using Docker for consistent deployments
* Automated build, test, and deployment using Jenkins pipelines
* Implemented health checks and automated container redeployment

---

## 🏗️ Architecture

```
Developer → GitHub → Jenkins Pipeline → Docker Build → Container Deployment → Web App (Port 8090)
```

---

## ⚙️ Tech Stack

* Backend: Python (Flask, Gunicorn)
* CI/CD: Jenkins (Dockerized)
* Containerization: Docker
* Scripting: Bash
* Domain: Financial FIX Protocol

---

## 📂 Project Structure

```
.
├── fix_log_analyzer.py   # Flask app for parsing FIX logs
├── requirements.txt      # Python dependencies
├── Dockerfile            # App container build
├── Dockerfile.jenkins    # Custom Jenkins image
├── Dockerfile.agent      # Jenkins agent with Docker access
├── Jenkinsfile           # CI/CD pipeline definition
├── build.sh              # Docker image build script
├── deploy.sh             # Container deployment script
├── test.sh               # Health check script
└── README.md
```

---

## 🔍 Application Features

### FIX Log Parsing

* Supports multiple delimiters: SOH (`\x01`), `|`, `^A`
* Extracts structured FIX messages
* Sorts messages by SendingTime (tag 52)

### Analytics Provided

* Logon (`35=A`) and Logout (`35=5`) tracking
* Market Data / Quote Requests (`35=V / 35=R`)
* Streaming quotes (`35=S`, `537=0`)
* Unique subscribed symbols
* QuoteID-based search (tag 117)

### UI Features

* Upload log file or paste logs
* Real-time summary dashboard
* Symbol-level insights
* Quote search functionality

---

## 🔄 CI/CD Pipeline Flow

### 1. Build Stage

* Docker image is created with version tagging:

```
sivabalansp/fix_log_analyzer:$BUILD_NUMBER
```

### 2. Test Stage

* Application health is verified using:

```
http://host.docker.internal:8090
```

### 3. Deploy Stage

* Stops and removes existing container
* Deploys a new container with the latest image:

```
docker run -d -p 8090:5000 --name fix_log_analyzer fix_log_analyzer
```

---

## 🐳 Docker Setup

### Build Image

```
docker build -t fix_log_analyzer .
```

### Run Container

```
docker run -d -p 8090:5000 fix_log_analyzer
```

---

## ⚡ Jenkins Setup

* Jenkins runs inside Docker
* Uses a custom Jenkins agent with Docker access to execute Docker commands

### Pipeline Stages:

* Checkout
* Build
* Test
* Deploy

---

## 🚀 How to Run Locally

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run the application

```
python fix_log_analyzer.py
```

### 3. Access the UI

```
http://localhost:5000
```

---

## 🧠 Key DevOps Concepts Demonstrated

* Dockerized application deployment
* Jenkins pipeline automation
* Dynamic image versioning using build numbers
* Container lifecycle management
* Health check validation before deployment
* Jenkins agent setup for Docker workloads

---

## 🎯 Key Learning Outcomes

* Handling real-world FIX protocol logs
* Building end-to-end CI/CD pipelines
* Deploying and managing containerized applications
* Debugging production-like systems
