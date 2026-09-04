#!/bin/bash
# AI Intent Radar - Production Startup Script
# Run this after deployment to start all services

set -e

echo "🚀 AI Intent Radar - Production Startup"
echo "======================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check for .env file
if [ ! -f backend/.env ] && [ ! -f backend/.env.production ]; then
    echo "⚠️  No .env file found. Copying .env.production to .env..."
    cp backend/.env.production backend/.env
    echo "📝 Please edit backend/.env with your production settings"
    echo "   Key settings to change:"
    echo "   - DATABASE_URL (your PostgreSQL connection)"
    echo "   - AI_PROVIDER (set to 'anthropic' for production)"
    echo "   - ANTHROPIC_API_KEY (your Claude API key)"
    echo "   - CORS_ORIGINS (your frontend domain)"
    echo ""
    read -p "Press Enter after editing .env to continue..."
fi

# Build and start containers
echo ""
echo "📦 Building and starting containers..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# Wait for PostgreSQL to be ready
echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if database is healthy
echo "🔍 Checking database health..."
docker-compose exec db pg_isready -U postgres || {
    echo "❌ PostgreSQL is not ready. Check docker-compose logs."
    exit 1
}

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
docker-compose exec backend alembic upgrade head || {
    echo "❌ Migration failed. Check the error message above."
    exit 1
}

# Seed demo data
echo ""
echo "🌱 Seeding demo data..."
docker-compose exec backend python -m app.utils.seed_data || {
    echo "⚠️  Seeding failed (may already exist). Continuing..."
}

# Process signals through AI pipeline
echo ""
echo "🤖 Processing signals through AI pipeline..."
docker-compose exec backend python -m app.workers.worker pipeline || {
    echo "⚠️  Pipeline processing failed. Signals will be processed by worker."
}

# Check health
echo ""
echo "🏥 Checking API health..."
sleep 5
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "✅ API is healthy!"
else
    echo "❌ API health check failed. Check docker-compose logs."
    echo "   Run: docker-compose logs backend"
    exit 1
fi

echo ""
echo "======================================="
echo "🎉 AI Intent Radar is running!"
echo "======================================="
echo ""
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🌐 Frontend:          http://localhost:3000"
echo "🔑 Demo Login:        demo@radar.ai / demo1234"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f backend    # Watch backend logs"
echo "  docker-compose logs -f worker     # Watch worker logs"
echo "  docker-compose down               # Stop all services"
echo "  docker-compose restart backend    # Restart backend"
echo ""
