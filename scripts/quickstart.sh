#!/bin/bash
echo "🛡️ SENTINEL Quick Start"
echo ""
echo "1. Starting services..."
docker-compose up -d postgres redis

echo "2. Waiting for DB..."
sleep 5

echo "3. Starting API..."
docker-compose up -d api

echo "4. Testing health..."
sleep 3
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "✅ SENTINEL is running!"
echo "   API:       http://localhost:8000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo "   Grafana:   http://localhost:3001"
echo ""
echo "Run a test: python scripts/test_agent.py"
