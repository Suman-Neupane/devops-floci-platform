.PHONY: help floci-up floci-down tf-init tf-plan tf-apply tf-destroy app-build app-run test k8s-cluster k8s-deploy k8s-destroy clean

AWS_ENDPOINT ?= http://localhost:4566
AWS_REGION ?= eu-central-1

help:
	@echo "======================================================================"
	@echo "           CloudOps-Floci-Platform Developer Commands                 "
	@echo "======================================================================"
	@echo "  make floci-up    - Start Floci AWS emulator container"
	@echo "  make floci-down  - Stop Floci AWS emulator container"
	@echo "  make tf-init     - Initialize Terraform working directory"
	@echo "  make tf-plan     - Generate and show Terraform execution plan"
	@echo "  make tf-apply    - Apply Terraform infrastructure to Floci"
	@echo "  make tf-destroy  - Destroy Terraform-managed infrastructure"
	@echo "  make app-build   - Build Docker container image for FastAPI service"
	@echo "  make app-run     - Run FastAPI app locally pointing to Floci"
	@echo "  make test        - Run Pytest integration tests against Floci"
	@echo "  make k8s-cluster - Spin up local k3d Kubernetes cluster"
	@echo "  make k8s-deploy  - Deploy Helm chart to k3d Kubernetes cluster"
	@echo "  make clean       - Remove temporary build & test artifacts"
	@echo "======================================================================"

floci-up:
	docker compose up -d
	@echo "Waiting for Floci to be ready on port 4566..."
	@sleep 3

floci-down:
	docker compose down -v

tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan

tf-apply:
	cd terraform && terraform apply -auto-approve

tf-destroy:
	cd terraform && terraform destroy -auto-approve

app-build:
	docker build -t cloud-app:latest ./app

app-run:
	cd app && AWS_ENDPOINT_URL=$(AWS_ENDPOINT) AWS_DEFAULT_REGION=$(AWS_REGION) uvicorn src.main:app --reload --port 8000

test:
	PYTHONPATH=app AWS_ENDPOINT_URL=$(AWS_ENDPOINT) AWS_DEFAULT_REGION=$(AWS_REGION) python3 -m pytest -v app/tests/

k8s-cluster:
	k3d cluster create devops-cluster --port "8080:80@loadbalancer" --agents 2 || kind create cluster --name devops-cluster

k8s-deploy:
	helm upgrade --install cloud-app ./k8s/helm/cloud-app --set image.repository=cloud-app --set image.tag=latest

k8s-destroy:
	k3d cluster delete devops-cluster || kind delete cluster --name devops-cluster

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".terraform" -exec rm -rf {} +
	rm -f terraform/tfplan terraform/terraform.tfstate*
