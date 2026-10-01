# 🚀 CloudOps Floci Platform: End-to-End GitOps & Cloud Infrastructure

[![CI/CD Pipeline](https://github.com/Suman-Neupane/devops-floci-platform/actions/workflows/ci-pipeline.yml/badge.svg)](https://github.com/Suman-Neupane/devops-floci-platform/actions)
[![Terraform Checks](https://github.com/Suman-Neupane/devops-floci-platform/actions/workflows/terraform-validate.yml/badge.svg)](https://github.com/Suman-Neupane/devops-floci-platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AWS Emulator: Floci](https://img.shields.io/badge/AWS_Emulator-Floci-blue)](https://github.com/floci/floci)
[![IaC: Terraform](https://img.shields.io/badge/IaC-Terraform-purple)](https://www.terraform.io/)
[![Orchestration: Kubernetes](https://img.shields.io/badge/K8s-k3d%2Fkind-blue)](https://k3d.io/)

A production-grade, zero-cost DevOps & Cloud Infrastructure platform using **Floci** (high-performance local AWS emulator) alongside **Terraform**, **FastAPI**, **Kubernetes (k3d)**, **Helm**, **ArgoCD (GitOps)**, and **Prometheus/Grafana**.

---

## 🏛️ Architecture Overview

```mermaid
graph TD
    subgraph Developer Desktop
        Dev[Developer / Git Push] -->|Push Code| GH[GitHub Repository]
        Make[Makefile CLI] -->|make up| DC[Docker Compose]
    end

    subgraph Floci AWS Emulation Layer localhost:4566
        Floci[Floci Container - Quarkus / GraalVM]
        S3[S3 Bucket: user-documents-bucket]
        DDB[DynamoDB Table: document-metadata]
        SQS[SQS Queue: document-processing-events]
        Floci --- S3
        Floci --- DDB
        Floci --- SQS
    end

    subgraph Kubernetes Cluster k3d / Kind
        ArgoCD[ArgoCD GitOps Controller]
        App[FastAPI Container Replicas x2]
        Prom[Prometheus Server]
        Graf[Grafana Dashboard]
        
        ArgoCD -->|Syncs Helm Manifests| App
        App -->|AWS SDK to localhost:4566| Floci
        Prom -->|Scrapes /metrics| App
        Graf -->|Visualizes Metrics| Prom
    end

    subgraph GitHub Actions CI/CD Pipeline
        GH -->|Triggers| GHA[GitHub Actions]
        GHA -->|1. IaC Lint| TFCheck[TFlint & Checkov]
        GHA -->|2. Integration Tests| PyTest[PyTest against Floci]
        GHA -->|3. Container Security| Trivy[Trivy Scanner]
    end
```

---

## ⚖️ Architecture Decisions & Trade-offs

This project is built around **conscious engineering judgment** rather than default tool choices. All major design choices are documented as formal Architecture Decision Records:

* **[ADR-001: Choosing Floci over LocalStack for Zero-Cost Local Cloud Emulation](docs/adr/ADR-001-floci-over-localstack.md)**  
  *Context:* LocalStack requires 800MB–1.4GB RAM and 30–60s cold-start in CI. Floci (GraalVM native binary) boots in **25ms with 15MB RAM**, slashing CI test runtime by 90% and eliminating local memory contention.
* **[ADR-002: Adopting k3d & ArgoCD for GitOps Delivery](docs/adr/ADR-002-k3d-gitops-workflow.md)**  
  *Context:* Eliminates the $73+/month AWS EKS control plane cost for dev/demo setups while preserving CNCF-compliant Kubernetes manifests, Traefik ingress routing, and GitOps self-healing reconciliation.

### 📊 Local Cloud Benchmark: Floci vs. LocalStack
| Metric | LocalStack Community | Floci (Used Here) | Improvement |
| :--- | :--- | :--- | :--- |
| **Cold Start Time** | 35 – 60 seconds | **~25 milliseconds** | **99% faster** |
| **Idle Memory Footprint** | ~1.2 GB RAM | **~15 MB RAM** | **98% lighter** |
| **Full Integration Test CI Duration** | ~2m 30s | **~18 seconds** | **88% faster feedback** |
| **Cloud Billing Incurred** | $0 | **$0** | Identical zero-cost |

---

## 🚨 Incident Handling & Blameless Post-Mortem

Production reliability is proven through failure management. This repository includes documentation of simulated failure testing:
* **[INC-001: FastAPI Worker Starvation During High-Concurrency Uploads](docs/incidents/INCIDENT-001-post-mortem.md)**  
  *Root Cause:* Synchronous blocking `boto3` file uploads starving the asyncio event loop under 150 concurrent VUs.  
  *Mitigation:* Thread-pooling migration via `run_in_threadpool`, container resource limits (`cpu: 250m`, `memory: 256Mi`), and RED metric alerting.

---

## 🌟 Key Features & Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **AWS Emulator** | **Floci** | Local native binary AWS emulator starting in ~25ms with 15MB RAM footprint on port `4566`. |
| **Infrastructure as Code** | **Terraform** | Modular IaC defining S3, DynamoDB, SQS with custom endpoint overrides (`http://localhost:4566`). |
| **Microservice** | **FastAPI + Boto3** | Async Python REST service processing file uploads to S3, records to DynamoDB, and events to SQS. |
| **Containerization** | **Docker** | Multi-stage security-hardened Dockerfile running under non-root user account. |
| **Kubernetes Packaging** | **Helm** | Templated Kubernetes manifests with configurable probes, resources, and environment bindings. |
| **GitOps Deployment** | **ArgoCD** | Automated continuous deployment syncing Kubernetes state directly from Git commits. |
| **Observability** | **Prometheus + Grafana** | Custom dashboard tracking request rates, p95 latency, and cluster metric scrapers. |
| **DevSecOps & CI** | **GitHub Actions + Trivy + Checkov** | Automated pipeline running container scans, integration tests, and static analysis. |


---

## ⚡ Quickstart Guide

### Prerequisites
- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Terraform](https://developer.hashicorp.com/terraform/downloads) (>= 1.5.0)
- [Python 3.11+](https://www.python.org/)
- `make` utility

### 1. Launch Floci AWS Emulator
```bash
make floci-up
```
*Floci will start on `http://localhost:4566`.*

### 2. Provision Infrastructure via Terraform
```bash
make tf-init
make tf-apply
```
*This creates the S3 bucket, DynamoDB table, and SQS queue locally on Floci.*

### 3. Run FastAPI Application
```bash
make app-run
```
*The service will be available at `http://localhost:8000`. Access interactive API docs at `http://localhost:8000/docs`.*

### 4. Run Integration Test Suite
```bash
make test
```
*Runs PyTest assertions verifying real upload, S3 object storage, DynamoDB persistence, and SQS messaging against Floci.*

---

## 🧪 Testing the API via cURL

### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@README.md"
```

### List Uploaded Documents
```bash
curl -X GET "http://localhost:8000/documents"
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
