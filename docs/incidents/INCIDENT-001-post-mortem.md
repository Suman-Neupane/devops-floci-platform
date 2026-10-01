# Blameless Incident Post-Mortem

## Incident: INC-001 — FastAPI Worker Starvation During High-Concurrency Uploads to Local S3

* **Date:** 2026-08-15
* **Severity:** Sev-2 (Simulated Load Incident)
* **Author / On-Call:** Suman Neupane
* **Affected Component:** `app/main.py` (FastAPI Upload Endpoint) & Floci S3 Integration
* **Status:** Resolved & Mitigated

---

### 1. Incident Summary
During automated load testing with `k6` executing 150 concurrent multipart file uploads, the application experienced a sudden spike in HTTP 504 Gateway Timeouts and request drops. Container CPU utilization surged to 98%, and Kubernetes readiness probes failed, causing k3s to trigger pod restarts in a crashloop.

---

### 2. Timeline (UTC)
* **10:00** – Executed stress test (`k6 run --vus 150 --duration 2m scripts/stress-test.js`).
* **10:01** – Prometheus alert `High5xxRate` fired (> 8% of requests failing).
* **10:02** – k8s liveness and readiness probes timed out; container restarted by kubelet.
* **10:04** – Inspected application logs via `kubectl logs -l app=devops-floci-app`.
* **10:07** – Identified thread starvation: The synchronous `boto3` client was performing blocking disk and network I/O inside an `async def` FastAPI route, blocking the single-threaded asyncio event loop.
* **10:15** – Deployed mitigation: Wrapped blocking S3 calls with `run_in_threadpool` and tuned uvicorn worker pool concurrency.
* **10:22** – Re-ran load test with 200 concurrent VUs: 0 failed requests, p99 latency stabilized at 84ms. Incident closed.

---

### 3. Root Cause Analysis (The 5 Whys)
1. **Why did the API return 504 Gateway Timeouts?**  
   The Uvicorn event loop stopped processing inbound requests, causing ingress connections to time out.
2. **Why was the event loop unresponsive?**  
   It was blocked executing synchronous `boto3.client('s3').upload_fileobj()` calls.
3. **Why did blocking I/O run on the main event loop?**  
   The route was declared `async def`, but standard `boto3` is a synchronous blocking library.
4. **Why didn't tests catch this earlier?**  
   Unit tests and sequential integration tests only tested 1 request at a time, never exposing event loop starvation under concurrent load.
5. **Why were there no safeguards against event loop latency?**  
   Prometheus metrics initially only tracked HTTP status codes, not event loop lag or thread pool saturation.

---

### 4. Preventive Actions Taken

| Action Item | Category | Status |
| :--- | :--- | :--- |
| Migrated blocking S3 operations using `starlette.concurrency.run_in_threadpool` | Corrective | Done |
| Added Prometheus metrics for p95 / p99 request duration and active thread counts | Observability | Done |
| Configured Kubernetes Resource Requests & Limits (`cpu: 250m`, `memory: 256Mi`) | Reliability | Done |
| Integrated automated concurrent load tests (`k6`) into CI pull request validation | Prevention | Done |
