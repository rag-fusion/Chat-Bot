#!/bin/bash

# Build and package script for offline multimodal RAG
# Creates Docker image and release tarball

set -e

VERSION=${1:-"0.1.0"}
PROJECT_NAME="offline-multimodal-rag"
IMAGE_NAME="${PROJECT_NAME}:${VERSION}"
TARBALL_NAME="${PROJECT_NAME}-${VERSION}.tar.gz"

echo "Building ${PROJECT_NAME} version ${VERSION}"

# Build Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} -f scripts/docker/Dockerfile .

# Test the image
echo "Testing Docker image..."
docker run --rm ${IMAGE_NAME} python -c "import app; print('App imports successfully')"

# Save Docker image as tarball
echo "Creating release tarball..."
docker save ${IMAGE_NAME} | gzip > ${TARBALL_NAME}

# Create release directory
mkdir -p release
cp ${TARBALL_NAME} release/

# Create install script
cat > release/install.sh << 'EOF'
#!/bin/bash
# Install script for offline multimodal RAG

echo "Installing Offline Multimodal RAG..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Load Docker image
if [ -f "offline-multimodal-rag-*.tar.gz" ]; then
    echo "Loading Docker image..."
    docker load < offline-multimodal-rag-*.tar.gz
else
    echo "Error: Docker tarball not found."
    exit 1
fi

echo "Installation complete!"
echo "Run with: docker run -p 7860:7860 offline-multimodal-rag:0.1.0"
EOF

chmod +x release/install.sh

# Create quickstart guide
cat > release/quickstart.md << EOF
# Offline Multimodal RAG - Quick Start

## System Requirements
- Docker installed
- 8GB+ RAM recommended
- 20GB+ disk space for models

## Installation

1. Download the release tarball: \`offline-multimodal-rag-${VERSION}.tar.gz\`
2. Run the install script: \`./install.sh\`

## Usage

1. Start the application:
   \`\`\`bash
   docker run -p 7860:7860 offline-multimodal-rag:${VERSION}
   \`\`\`

2. Open your browser to: http://localhost:7860

3. Upload documents (PDF, DOCX, images, audio)

4. Ask questions about your documents

## Features
- Offline processing (no internet required)
- Support for PDF, DOCX, images, and audio
- Local LLM inference
- Cross-modal search and linking
- Gradio web interface

## Troubleshooting
- If you get out-of-memory errors, try reducing the model size in config.yaml
- For GPU acceleration, add \`--gpus all\` to the docker run command
EOF

echo "Build complete!"
echo "Release files created in ./release/"
echo "Docker image: ${IMAGE_NAME}"
echo "Tarball: ${TARBALL_NAME}"
