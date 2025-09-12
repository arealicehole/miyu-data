#!/bin/bash

# Miyu-Data Bot Docker Build Script
# Usage: ./build.sh [version]

VERSION=${1:-$(cat VERSION)}

echo "🚀 Building Miyu-Data Bot v${VERSION}"
echo "================================"

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t miyu-data-bot:${VERSION} -t miyu-data-bot:latest .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🏷️  Tagged as:"
    echo "  - miyu-data-bot:${VERSION}"
    echo "  - miyu-data-bot:latest"
    echo ""
    echo "📝 To run the bot:"
    echo "  docker-compose up -d"
    echo ""
    echo "🔍 To check logs:"
    echo "  docker-compose logs -f"
else
    echo "❌ Build failed!"
    exit 1
fi