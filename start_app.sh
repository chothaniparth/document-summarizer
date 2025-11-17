#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}  AI Document Summarizer - Starting Services${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with the following variables:${NC}"
    echo "OPENAI_API_KEY=your_key_here"
    echo "MONGO_URI=mongodb://admin:admin@localhost:27017/?authSource=admin"
    echo "MONGO_DB_NAME=document_summarizer"
    echo "JWT_SECRET=your_secret_here"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running!${NC}"
    echo -e "${YELLOW}Please start Docker Desktop and try again.${NC}"
    exit 1
fi

# Start Docker services
echo -e "${GREEN}✓ Starting Docker services (MongoDB, Qdrant, Valkey)...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check if services are running
echo -e "${GREEN}✓ Checking Docker services...${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}✅ Docker services are running!${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo ""
echo -e "1. ${GREEN}Start the FastAPI backend:${NC}"
echo -e "   ${BLUE}python main.py${NC}"
echo ""
echo -e "2. ${GREEN}Start the RQ worker (in another terminal):${NC}"
echo -e "   ${BLUE}cd queues && rq worker --with-scheduler${NC}"
echo ""
echo -e "3. ${GREEN}Start the Streamlit frontend (in another terminal):${NC}"
echo -e "   ${BLUE}streamlit run streamlit_app.py${NC}"
echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "📌 ${YELLOW}Service URLs:${NC}"
echo -e "   - FastAPI Backend: ${BLUE}http://localhost:8000${NC}"
echo -e "   - Streamlit Frontend: ${BLUE}http://localhost:8501${NC}"
echo -e "   - Qdrant Dashboard: ${BLUE}http://localhost:6333/dashboard${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo -e "${GREEN}🚀 Ready to go! Follow the steps above to start the application.${NC}"
echo ""
