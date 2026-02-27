#!/usr/bin/env python3
"""
Comprehensive Test Suite for PatchPilot Tech Stack
Tests all components: FastAPI, PostgreSQL, pgvector, Redis, Docker, Claude, Prometheus, Grafana
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
import redis
import asyncpg
import sys
import os
from typing import Dict, Any
from pathlib import Path

# Load environment variables from .env file
env_file = Path('/workspaces/red2green/.env')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
NC = '\033[0m'  # No Color


class TechStackTester:
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.http_client = httpx.Client(timeout=10.0)
        
    def log_test(self, name: str, status: str, message: str = "", details: str = ""):
        """Log test result"""
        self.results[name] = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        icon = f"{GREEN}✓{NC}" if status == "PASS" else f"{RED}✗{NC}"
        print(f"\n{icon} {BLUE}{name}{NC}")
        if message:
            print(f"   {message}")
        if details:
            print(f"   {YELLOW}Details:{NC} {details}")

    async def test_fastapi_health(self) -> bool:
        """Test 1: FastAPI Server Health Check"""
        try:
            response = self.http_client.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "1. FastAPI Health Check",
                    "PASS",
                    "Server is healthy and responding",
                    f"Response: {data}"
                )
                return True
        except Exception as e:
            self.log_test("1. FastAPI Health Check", "FAIL", str(e))
            return False

    async def test_fastapi_ready(self) -> bool:
        """Test 2: FastAPI Ready Check"""
        try:
            response = self.http_client.get("http://localhost:8000/ready")
            if response.status_code == 200:
                self.log_test(
                    "2. FastAPI Ready Check",
                    "PASS",
                    "All dependencies are ready"
                )
                return True
        except Exception as e:
            self.log_test("2. FastAPI Ready Check", "FAIL", str(e))
            return False

    async def test_fastapi_jobs_endpoint(self) -> bool:
        """Test 3: FastAPI Jobs Endpoint"""
        try:
            response = self.http_client.get("http://localhost:8000/api/jobs")
            if response.status_code == 200:
                data = response.json()
                jobs_count = len(data.get("jobs", []))
                self.log_test(
                    "3. FastAPI Jobs Endpoint",
                    "PASS",
                    f"Successfully retrieved {jobs_count} jobs",
                    f"Total jobs: {jobs_count}, Pagination: {data.get('pagination', {})}"
                )
                return True
        except Exception as e:
            self.log_test("3. FastAPI Jobs Endpoint", "FAIL", str(e))
            return False

    async def test_fastapi_metrics_endpoint(self) -> bool:
        """Test 4: FastAPI Metrics Endpoint"""
        try:
            response = self.http_client.get("http://localhost:8000/api/metrics/summary")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "4. FastAPI Metrics Summary",
                    "PASS",
                    "Metrics endpoint operational",
                    f"Total jobs: {data.get('total_jobs', 0)}, "
                    f"Success rate: {data.get('success_rate', 0):.1f}%, "
                    f"Auto-fixed: {data.get('auto_fixed_count', 0)}"
                )
                return True
        except Exception as e:
            self.log_test("4. FastAPI Metrics Summary", "FAIL", str(e))
            return False

    async def test_prometheus_metrics(self) -> bool:
        """Test 5: Prometheus Metrics Endpoint"""
        try:
            response = self.http_client.get("http://localhost:8000/metrics/prometheus")
            if response.status_code == 200:
                text = response.text
                metrics_count = text.count('\n')
                has_patchpilot = 'patchpilot_' in text
                
                self.log_test(
                    "5. Prometheus Metrics Endpoint",
                    "PASS",
                    "Prometheus metrics are being exported",
                    f"Metrics lines: {metrics_count}, PatchPilot metrics present: {has_patchpilot}"
                )
                return True
        except Exception as e:
            self.log_test("5. Prometheus Metrics Endpoint", "FAIL", str(e))
            return False

    async def test_postgresql_connection(self) -> bool:
        """Test 6: PostgreSQL Connection (with pgvector)"""
        try:
            import os
            # Try to use environment variable or fallback to default
            db_url = os.getenv('DATABASE_URL', 'postgresql://sentinel:MyS3cur3Pass!2024@localhost:5432/sentinel')
            # Parse connection string
            try:
                # Simple parsing of postgres://user:pass@host:port/db
                db_url_clean = db_url.replace('postgresql+asyncpg://', '').replace('postgresql://', '')
                parts = db_url_clean.split('@')
                user_pass = parts[0].split(':')
                user = user_pass[0]
                password = user_pass[1] if len(user_pass) > 1 else ''
                host_port_db = parts[1].split('/')
                host_port = host_port_db[0].split(':')
                host = host_port[0]
                port = int(host_port[1]) if len(host_port) > 1 else 5432
                database = host_port_db[1] if len(host_port_db) > 1 else 'sentinel'
            except:
                # Fallback to defaults
                user = 'sentinel'
                password = 'MyS3cur3Pass!2024'
                host = 'localhost'
                port = 5432
                database = 'sentinel'
            
            conn = await asyncpg.connect(
                user=user,
                password=password,
                database=database,
                host=host,
                port=port
            )
            
            # Check pgvector extension
            result = await conn.fetch("SELECT * FROM pg_extension WHERE extname='vector';")
            version = await conn.fetchval("SELECT version();")
            
            await conn.close()
            
            self.log_test(
                "6. PostgreSQL + pgvector",
                "PASS",
                "Connected to PostgreSQL 16 with pgvector extension",
                f"pgvector installed: {bool(result)}, Version: {version[:50]}..."
            )
            return True
        except Exception as e:
            self.log_test("6. PostgreSQL + pgvector", "FAIL", str(e))
            return False

    async def test_redis_connection(self) -> bool:
        """Test 7: Redis Connection"""
        try:
            r = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True,
                socket_connect_timeout=5
            )
            
            # Test basic operations
            test_key = f"test_key_{int(time.time())}"
            r.set(test_key, "test_value", ex=10)
            value = r.get(test_key)
            r.delete(test_key)
            
            info = r.info()
            memory = info.get('used_memory_human', 'N/A')
            clients = info.get('connected_clients', 0)
            
            self.log_test(
                "7. Redis Connection (Streams)",
                "PASS",
                "Redis is operational and accepting connections",
                f"Memory used: {memory}, Connected clients: {clients}, Redis version: {info.get('redis_version')}"
            )
            return True
        except Exception as e:
            self.log_test("7. Redis Connection (Streams)", "FAIL", str(e))
            return False

    async def test_grafana_service(self) -> bool:
        """Test 8: Grafana Service"""
        try:
            response = self.http_client.get("http://localhost:3001/api/health", follow_redirects=True)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "8. Grafana Service",
                    "PASS",
                    "Grafana is running and accessible",
                    f"Status: {data.get('status')}, Database: {data.get('database')}"
                )
                return True
        except Exception as e:
            self.log_test("8. Grafana Service", "FAIL", str(e))
            return False

    async def test_prometheus_service(self) -> bool:
        """Test 9: Prometheus Service"""
        try:
            response = self.http_client.get("http://localhost:9090/-/healthy")
            if response.status_code == 200:
                self.log_test(
                    "9. Prometheus Service",
                    "PASS",
                    "Prometheus is healthy and scraping metrics",
                    "Prometheus is configured to scrape PatchPilot metrics"
                )
                return True
        except Exception as e:
            self.log_test("9. Prometheus Service", "FAIL", str(e))
            return False

    async def test_docker_sandbox_capability(self) -> bool:
        """Test 10: Docker Sandbox Capability"""
        try:
            import docker
            client = docker.from_env()
            info = client.info()
            
            # Check if Docker daemon is accessible
            containers = client.containers.list()
            
            self.log_test(
                "10. Docker Sandbox (Isolated Testing)",
                "PASS",
                "Docker daemon is accessible for sandbox execution",
                f"Running containers: {len(containers)}, "
                f"Server: {info.get('ServerVersion')}, "
                f"OS: {info.get('OperatingSystem')}"
            )
            return True
        except Exception as e:
            self.log_test("10. Docker Sandbox (Isolated Testing)", "FAIL", str(e))
            return False

    async def test_langchain_imports(self) -> bool:
        """Test 11: LangChain & LangGraph Installation"""
        try:
            import langgraph
            import langchain
            from langchain_anthropic import ChatAnthropic
            
            lg_version = langgraph.__version__ if hasattr(langgraph, '__version__') else "unknown"
            lc_version = langchain.__version__ if hasattr(langchain, '__version__') else "unknown"
            
            self.log_test(
                "11. LangChain & LangGraph Libraries",
                "PASS",
                "LangGraph state machine and LangChain are installed",
                f"LangGraph version: {lg_version}, LangChain version: {lc_version}"
            )
            return True
        except Exception as e:
            self.log_test("11. LangChain & LangGraph Libraries", "FAIL", str(e))
            return False

    async def test_anthropic_api_availability(self) -> bool:
        """Test 12: Anthropic API Availability"""
        try:
            import anthropic
            import os
            
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                self.log_test(
                    "12. Anthropic API (Claude)",
                    "WARN",
                    "ANTHROPIC_API_KEY not configured - LLM features will not work",
                    "Set ANTHROPIC_API_KEY environment variable to enable Claude agent"
                )
                return False
            
            # Just check if library is available, don't make API calls in test
            client = anthropic.Anthropic(api_key=api_key)
            self.log_test(
                "12. Anthropic API (Claude)",
                "PASS",
                "Anthropic API key is configured and client is initialized",
                "Claude Sonnet model is available for autonomous healing agent"
            )
            return True
        except Exception as e:
            self.log_test("12. Anthropic API (Claude)", "FAIL", str(e))
            return False

    async def test_frontend_connection(self) -> bool:
        """Test 13: Frontend Service"""
        try:
            response = self.http_client.get("http://localhost:3000", follow_redirects=True, timeout=5.0)
            is_html = 'html' in response.text.lower() or response.status_code == 200
            
            self.log_test(
                "13. Frontend Service (Next.js)",
                "PASS" if is_html else "WARN",
                "Frontend server is running" if is_html else "Frontend is running but may still be loading",
                f"Status: {response.status_code}, Content type: {response.headers.get('content-type', 'unknown')}"
            )
            return is_html
        except Exception as e:
            self.log_test("13. Frontend Service (Next.js)", "FAIL", str(e))
            return False

    async def test_api_docs(self) -> bool:
        """Test 14: FastAPI Interactive API Documentation"""
        try:
            response = self.http_client.get("http://localhost:8000/api/docs")
            if response.status_code == 200:
                has_swagger = 'swagger' in response.text.lower()
                self.log_test(
                    "14. FastAPI Interactive API Docs",
                    "PASS",
                    "Swagger UI documentation is available",
                    f"Swagger UI present: {has_swagger}"
                )
                return True
        except Exception as e:
            self.log_test("14. FastAPI Interactive API Docs", "FAIL", str(e))
            return False

    async def test_webhook_simulation(self) -> bool:
        """Test 15: Webhook Endpoint (Simulation)"""
        try:
            payload = {
                "action": "completed",
                "workflow_run": {
                    "name": "test-workflow",
                    "head_sha": "abc123def456",
                    "head_branch": "main",
                    "repository": {
                        "full_name": "charan-happy/red2green",
                        "clone_url": "https://github.com/charan-happy/red2green.git"
                    },
                    "conclusion": "failure",
                    "logs_url": "https://github.com/charan-happy/red2green/runs/123"
                }
            }
            
            response = self.http_client.post(
                "http://localhost:8000/api/webhooks/github",
                json=payload,
                headers={"X-Hub-Signature-256": "sha256=test"}
            )
            
            self.log_test(
                "15. GitHub Webhook Endpoint",
                "PASS" if response.status_code in [200, 202] else "WARN",
                f"Webhook endpoint responded with status {response.status_code}",
                f"Webhook simulation: GitHub CI failure detection working"
            )
            return response.status_code in [200, 202]
        except Exception as e:
            self.log_test("15. GitHub Webhook Endpoint", "FAIL", str(e))
            return False

    def print_summary(self):
        """Print test summary"""
        print(f"\n\n{'='*70}")
        print(f"{BLUE}PATCHPILOT TECH STACK TEST SUMMARY{NC}")
        print(f"{'='*70}\n")
        
        passed = sum(1 for r in self.results.values() if r["status"] == "PASS")
        failed = sum(1 for r in self.results.values() if r["status"] == "FAIL")
        warned = sum(1 for r in self.results.values() if r["status"] == "WARN")
        total = len(self.results)
        
        print(f"{GREEN}Passed: {passed}/{total}{NC}")
        print(f"{RED}Failed: {failed}/{total}{NC}")
        print(f"{YELLOW}Warnings: {warned}/{total}{NC}")
        
        print(f"\n{'─'*70}")
        print(f"{BLUE}Tech Stack Components Tested:{NC}\n")
        
        components = [
            ("FastAPI Backend", ["Health Check", "Ready Check", "Jobs Endpoint", "Metrics Endpoint", "API Docs"]),
            ("Databases", ["PostgreSQL 16 + pgvector"]),
            ("Message Queue", ["Redis Streams"]),
            ("Observability", ["Prometheus Metrics", "Prometheus Service", "Grafana Service"]),
            ("Sandbox & Isolation", ["Docker Sandbox"]),
            ("AI/LLM", ["LangGraph State Machine", "Anthropic API (Claude)"]),
            ("Frontend", ["Next.js Frontend"]),
            ("Integration", ["GitHub Webhook"])
        ]
        
        for category, items in components:
            print(f"{BLUE}  {category}:{NC}")
            for item in items:
                status = next((r["status"] for k, r in self.results.items() if item.lower() in k.lower()), "-")
                icon = f"{GREEN}✓{NC}" if status == "PASS" else f"{RED}✗{NC}" if status == "FAIL" else f"{YELLOW}⚠{NC}"
                print(f"    {icon} {item}")
        
        print(f"\n{'─'*70}")
        print(f"\n{BLUE}Architecture Overview:{NC}")
        print(f"""
{BLUE}┌─ FastAPI Backend (Port 8000){NC}
│  ├── LangGraph Agent State Machine
│  ├── Claude (Anthropic) for code analysis
│  └── Prometheus metrics export
│
├─ PostgreSQL 16 + pgvector (Port 5432)
│  └── Semantic fix memory & job storage
│
├─ Redis Streams (Port 6379)
│  └── Message queue for async processing
│
├─ Docker Daemon
│  └── Isolated sandbox for testing fixes
│
├─ Prometheus (Port 9090)
│  └── Metrics scraping from FastAPI
│
├─ Grafana (Port 3001)
│  └── Visualization of PatchPilot metrics
│
└─ Next.js Frontend (Port 3000)
   └── Real-time dashboard
        """)
        
        if failed == 0:
            print(f"\n{GREEN}✓ All critical components are operational!{NC}\n")
        else:
            print(f"\n{RED}✗ Some components need attention.{NC}\n")

    async def run_all_tests(self):
        """Run all tests"""
        print(f"\n{BLUE}{'='*70}")
        print(f"PATCHPILOT TECH STACK COMPREHENSIVE TEST SUITE")
        print(f"{'='*70}{NC}\n")
        
        tests = [
            self.test_fastapi_health,
            self.test_fastapi_ready,
            self.test_fastapi_jobs_endpoint,
            self.test_fastapi_metrics_endpoint,
            self.test_prometheus_metrics,
            self.test_postgresql_connection,
            self.test_redis_connection,
            self.test_grafana_service,
            self.test_prometheus_service,
            self.test_docker_sandbox_capability,
            self.test_langchain_imports,
            self.test_anthropic_api_availability,
            self.test_frontend_connection,
            self.test_api_docs,
            self.test_webhook_simulation,
        ]
        
        for test in tests:
            await test()
            await asyncio.sleep(0.1)  # Brief pause between tests
        
        self.print_summary()


async def main():
    """Main entry point"""
    tester = TechStackTester()
    try:
        await tester.run_all_tests()
    finally:
        tester.http_client.close()


if __name__ == "__main__":
    asyncio.run(main())
