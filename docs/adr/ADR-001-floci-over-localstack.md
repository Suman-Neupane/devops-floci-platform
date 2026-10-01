# Architecture Decision Record (ADR)

## ADR-001: Choosing Floci over LocalStack for Zero-Cost Local Cloud Emulation

* **Status:** Accepted
* **Date:** 2026-08-11
* **Author:** Suman Neupane
* **Deciders:** Suman Neupane

---

### 1. Context and Problem Statement
When developing cloud-native microservices backed by AWS services (S3 for binary object storage, DynamoDB for metadata indexing, and SQS for event processing), testing directly against live AWS infrastructure presents notable drawbacks:
- Incurring continuous AWS cloud billing for ephemeral dev/test environments.
- Requiring dedicated internet bandwidth and IAM credential provisioning for every local test run.
- High latency during test suites due to round-trips over the public internet.

To enable rapid, zero-cost developer workflows and fast CI pipelines, we needed a reliable local AWS emulator. The primary standard in the industry has historically been **LocalStack**. However, during initial profiling, LocalStack exhibited significant operational overhead.

### 2. Decision Drivers (Key Criteria)
1. **Startup Latency:** Time required to start the emulator container inside GitHub Actions CI runners and local developer laptops.
2. **Resource Footprint:** Memory (RAM) and CPU overhead, particularly when running alongside a local Kubernetes cluster (k3d) and Docker containers on dev machines.
3. **API Compatibility:** High-fidelity implementation of required AWS APIs (`s3`, `dynamodb`, `sqs`).
4. **Licensing & Cost:** Completely open-source without artificial feature paywalls for core testing.

---

### 3. Considered Options
* **Option 1: LocalStack (Community Edition)**
* **Option 2: Floci (GraalVM / Quarkus native AWS emulator)**
* **Option 3: Ephemeral AWS Cloud Sandbox Accounts**

---

### 4. Evaluation and Benchmarking

| Benchmark / Metric | Option 1: LocalStack | Option 2: Floci (Selected) | Option 3: Real AWS Sandbox |
| :--- | :--- | :--- | :--- |
| **Cold Start Time** | 35 – 60 seconds (Python runtime initialization) | **~25 milliseconds** (Pre-compiled native binary) | N/A (Always running, but network bound) |
| **Idle Memory Usage** | 800 MB – 1.4 GB RAM | **~15 MB – 25 MB RAM** | 0 MB local |
| **CI Integration Test Speed** | ~2m 30s per PR run | **~18 seconds total** | 1m 45s (network dependent) |
| **AWS Endpoint Override** | Supported (`http://localhost:4566`) | Supported (`http://localhost:4566`) | Standard AWS endpoints |
| **Cost** | Free (Tiered features) | **100% Free & Open Source** | Variable ($15–$50/mo dev spend) |

---

### 5. Final Decision Outcome
**Chosen Option:** **Option 2 (Floci)**

**Rationale:**
Floci is built using Quarkus and compiled to a native executable with GraalVM. Its 25ms startup time and tiny 15MB memory footprint allow our entire stack (AWS emulation + FastAPI + k3d Kubernetes + Prometheus + Grafana) to run comfortably on standard developer hardware and standard GitHub Actions hosted runners without hitting OOM limits or stalling CI pipelines.

### 6. Positive & Negative Consequences
* **Positive Consequences:**
  - **98% faster startup time** compared to LocalStack, dramatically tightening the local test-and-debug feedback loop.
  - Zero cloud costs for running end-to-end integration and smoke tests.
  - Standard AWS SDKs (`boto3`, Terraform AWS Provider) work identically by redirecting `endpoint_url = "http://localhost:4566"`.
* **Negative Consequences / Trade-offs:**
  - Floci implements a focused subset of AWS services (S3, DynamoDB, SQS, SNS, SES, Secrets Manager). If we require advanced esoteric services (e.g., AWS Glue, Kinesis Video), fallback to live AWS staging or LocalStack Pro would be necessary.
