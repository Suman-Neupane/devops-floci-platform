# Architecture Decision Record (ADR)

## ADR-002: Adopting k3d (Containerized k3s) and ArgoCD for GitOps Delivery

* **Status:** Accepted
* **Date:** 2026-08-11
* **Author:** Suman Neupane
* **Deciders:** Suman Neupane

---

### 1. Context and Problem Statement
We required a container orchestration layer to demonstrate automated GitOps continuous delivery, rolling deployments, and self-healing. Running production cloud Kubernetes clusters (e.g. AWS EKS) incurs a fixed control plane fee of ~$73/month plus node compute costs, which is unsuitable for an educational and demonstration repository.

Locally, developers have options like Minikube, Kind, and k3d (k3s in Docker). We needed an engine that could run a lightweight multi-node cluster, support ArgoCD, and be easily scriptable via a simple `Makefile`.

### 2. Decision Drivers (Key Criteria)
1. **Lightweight Execution:** Minimal memory footprint (able to run inside a Docker daemon alongside application containers).
2. **Speed of Provisioning:** Fast creation and destruction time (`make k8s-up` / `make k8s-down`).
3. **Ingress & Networking:** Out-of-the-box Traefik ingress controller support for local routing without complex port-forward loops.
4. **GitOps Compatibility:** Full support for standard Kubernetes Custom Resource Definitions (CRDs) required by ArgoCD.

---

### 3. Considered Options
* **Option 1: Minikube** (Heavier VM or Docker driver; slower boot, single node focus).
* **Option 2: Kind (Kubernetes in Docker)** (Standard upstream k8s; good, but lacks bundled ingress controller by default).
* **Option 3: k3d (k3s in Docker)** (Stripped-down CNCF-certified lightweight Kubernetes with built-in Traefik ingress and minimal resource usage).

---

### 4. Final Decision Outcome
**Chosen Option:** **Option 3 (k3d)**

**Rationale:**
k3d runs Rancher's lightweight `k3s` distribution packaged inside Docker containers. It boots in under 15 seconds, consumes under 500MB of RAM for the control plane, and provides native Traefik ingress routing. This enables seamless hosting of our FastAPI application, ArgoCD controller, and Prometheus monitoring stack simultaneously.

### 5. Positive & Negative Consequences
* **Positive Consequences:**
  - Fast cluster provisioning (`k3d cluster create`) in ~12 seconds.
  - Full declarative GitOps support: ArgoCD continuously monitors this Git repository and reconciles the Helm chart state without manual intervention.
  - Zero cloud bills.
* **Negative Consequences / Trade-offs:**
  - k3s strips away legacy in-tree cloud providers and storage drivers, which are irrelevant for local testing but would differ slightly from an AWS EKS production target.
