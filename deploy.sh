#!/bin/bash

# Deploy script cho ứng dụng Exam System
# Sử dụng: bash deploy.sh

set -e

echo "=================================="
echo "  EXAM SYSTEM - DEPLOYMENT SCRIPT"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Docker & Docker Compose
echo -e "\n${YELLOW}1. Checking Docker & Docker Compose...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker $(docker --version | cut -d' ' -f3)${NC}"
echo -e "${GREEN}✓ Docker Compose $(docker-compose --version | cut -d' ' -f3)${NC}"

# 2. Check if .env exists
echo -e "\n${YELLOW}2. Checking configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.production...${NC}"
    if [ ! -f .env.production ]; then
        echo -e "${RED}❌ .env.production not found!${NC}"
        exit 1
    fi
    cp .env.production .env
    echo -e "${YELLOW}⚠️  Please edit .env with your configuration!${NC}"
    echo -e "${YELLOW}⚠️  Required: FLASK_SECRET_KEY, MONGO_ROOT_PASSWORD, GEMINI_API_KEY${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Configuration file found${NC}"

# 3. Create directories
echo -e "\n${YELLOW}3. Creating required directories...${NC}"
mkdir -p uploads/avatars logs certs
echo -e "${GREEN}✓ Directories created${NC}"

# 4. Build & Start containers
echo -e "\n${YELLOW}4. Building Docker images...${NC}"
docker-compose build

echo -e "\n${YELLOW}5. Starting services...${NC}"
docker-compose up -d

# 5. Wait for services
echo -e "\n${YELLOW}6. Waiting for services to be ready...${NC}"
sleep 10

# 6. Check services status
echo -e "\n${YELLOW}7. Checking services status...${NC}"
if docker-compose ps | grep -q "healthy"; then
    echo -e "${GREEN}✓ Services are running${NC}"
else
    echo -e "${YELLOW}⚠️  Services may still be starting...${NC}"
    docker-compose ps
fi

# 7. Initialize database
echo -e "\n${YELLOW}8. Initializing database...${NC}"
docker-compose exec -T web python init_db.py

# 8. Show access information
echo -e "\n${GREEN}=================================="
echo "  DEPLOYMENT COMPLETE! ✅"
echo "===================================${NC}"
echo -e "\n${GREEN}Access the application:${NC}"
echo "  HTTP:  http://localhost:8000"
echo "  HTTPS: https://localhost:443 (if configured)"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo "  View logs:       docker-compose logs -f web"
echo "  Stop services:   docker-compose down"
echo "  Restart:         docker-compose restart"
echo "  MongoDB shell:   docker-compose exec mongodb mongosh -u admin -p"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  1. Change FLASK_SECRET_KEY in .env"
echo "  2. Change MONGO_ROOT_PASSWORD in .env"
echo "  3. Set up HTTPS certificates (certs/cert.pem, certs/key.pem)"
echo "  4. Change default admin password after first login"
echo ""
