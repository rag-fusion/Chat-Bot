# Makefile for Offline Multimodal RAG

.PHONY: help install test run build clean docker-build docker-run

help: ## Show this help message
	@echo "Offline Multimodal RAG - Available Commands:"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	cd backend && pip install -r requirements.txt

test: ## Run tests
	cd backend && python -m pytest tests/ -v

test-system: ## Run system test
	python test_system.py

run-gradio: ## Run Gradio interface
	python main.py --interface gradio --port 7860

run-fastapi: ## Run FastAPI backend
	python main.py --interface fastapi --port 8000

run-frontend: ## Run React frontend (if available)
	cd frontend && npm install && npm run dev

build: ## Build release package
	cd backend && chmod +x scripts/build_release.sh && ./scripts/build_release.sh

docker-build: ## Build Docker image
	cd backend && docker build -t offline-multimodal-rag:latest -f scripts/docker/Dockerfile .

docker-run: ## Run Docker container
	docker run -p 7860:7860 offline-multimodal-rag:latest

docker-run-gpu: ## Run Docker container with GPU support
	docker run --gpus all -p 7860:7860 offline-multimodal-rag:latest

clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf backend/storage/faiss.index
	rm -rf backend/storage/metadata.db
	rm -rf backend/storage/metadata.json

ingest-demo: ## Ingest sample documents
	cd backend && python scripts/ingest_all.py --data-dir ../samples --index ./storage/faiss.index

setup-models: ## Download required models
	cd backend && ./scripts/download_models.sh

check-deps: ## Check system dependencies
	@echo "Checking Python version..."
	@python --version
	@echo "Checking pip..."
	@pip --version
	@echo "Checking Docker..."
	@docker --version || echo "Docker not installed"
	@echo "Checking system resources..."
	@echo "RAM: $(shell free -h | grep Mem | awk '{print $$2}')"
	@echo "Disk: $(shell df -h . | tail -1 | awk '{print $$4}')"

dev-setup: install test-system ## Complete development setup
	@echo "Development setup complete!"

ci-test: ## Run CI tests
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=xml

format: ## Format code
	cd backend && python -m black app/ tests/
	cd backend && python -m isort app/ tests/

lint: ## Lint code
	cd backend && python -m flake8 app/ tests/
	cd backend && python -m mypy app/

docs: ## Generate documentation
	@echo "Documentation available at:"
	@echo "- README.md (main documentation)"
	@echo "- docs/quickstart.md (quick start guide)"
	@echo "- docs/troubleshooting.md (troubleshooting guide)"

release: build ## Create release package
	@echo "Release package created in backend/release/"

all: clean install test build ## Run all steps
	@echo "Complete build process finished!"