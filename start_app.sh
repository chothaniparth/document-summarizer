#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}  AI Document Summarizer - Starting Services${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# --- Check .env ---
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    exit 1
fi

# --- Start FastAPI, RQ, and Streamlit ---
echo -e "${GREEN}✓ Starting FastAPI backend...${NC}"
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &> fastapi.log &

echo -e "${GREEN}✓ Starting RQ worker...${NC}"
nohup rq worker --with-scheduler &> rq_worker.log &

echo -e "${GREEN}✓ Starting Streamlit frontend...${NC}"
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
