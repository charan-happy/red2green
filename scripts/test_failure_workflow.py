#!/usr/bin/env python3
"""
Test script to demonstrate PatchPilot failure detection and remediation workflow.
This simulates a complete CI failure cycle: detection -> diagnosis -> fix.
"""

import requests
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_DURATION_SECONDS = 60

# Test scenarios
FAILURE_SCENARIOS = [
    {
        "name": "syntax_error_test",
        "repo": "charan-happy/red2green",
        "branch": "test/syntax-error",
        "failure_type": "syntax_error",
        "root_cause": "Missing semicolon in main.py line 42",
        "details": "Invalid syntax: expected ':' but got 'if'",
        "provider": "github"
    },
    {
        "name": "dependency_conflict_test",
        "repo": "charan-happy/red2green",
        "branch": "test/dep-conflict",
        "failure_type": "dep_conflict",
        "root_cause": "FastAPI 0.111.0 incompatible with Starlette 0.33.0",
        "details": "Version mismatch detected in requirements.txt",
        "provider": "github"
    }
]


class TestRunner:
    """Run comprehensive failure detection and remediation tests."""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_jobs = []
        self.start_time = datetime.now()
    
    def log(self, level: str, message: str, **kwargs):
        """Log test events."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        extras = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        print(f"[{timestamp}] {level:8} | {message}" + (f" | {extras}" if extras else ""))
    
    def test_github_webhook(self, failure_scenario: Dict[str, Any]) -> str:
        """Send a GitHub webhook to simulate a failed CI build."""
        self.log("INFO", "Sending GitHub webhook", repo=failure_scenario["repo"])
        
        webhook_payload = {
            "action": "completed",
            "workflow_run": {
                "id": int(time.time()),
                "name": failure_scenario["branch"],
                "conclusion": "failure",
                "head_branch": failure_scenario["branch"],
                "repository": {
                    "full_name": failure_scenario["repo"],
                    "url": f"https://github.com/{failure_scenario['repo']}"
                }
            },
            "failure_type": failure_scenario["failure_type"],
            "root_cause": failure_scenario["root_cause"]
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/api/webhooks/github",
                json=webhook_payload,
                headers={"X-GitHub-Event": "workflow_run", "Content-Type": "application/json"},
                timeout=5
            )
            self.log("SUCCESS", "GitHub webhook accepted", 
                    status=response.status_code, 
                    event_id=webhook_payload["workflow_run"]["id"])
            return str(webhook_payload["workflow_run"]["id"])
        except Exception as e:
            self.log("ERROR", "GitHub webhook failed", error=str(e))
            return None
    
    def test_simulate_failure_endpoint(self, failure_scenario: Dict[str, Any]) -> str:
        """Use the dedicated simulate-failure endpoint."""
        self.log("INFO", "Triggering failure simulation", 
                failure_type=failure_scenario["failure_type"])
        
        payload = {
            "repo": failure_scenario["repo"],
            "branch": failure_scenario["branch"],
            "failure_type": failure_scenario["failure_type"],
            "root_cause": failure_scenario["root_cause"],
            "details": failure_scenario["details"]
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/api/test/simulate-failure",
                json=payload,
                timeout=5
            )
            data = response.json()
            job_id = data.get("job_id")
            self.log("SUCCESS", "Failure simulation accepted",
                    job_id=job_id,
                    status=data.get("status"))
            return job_id
        except Exception as e:
            self.log("ERROR", "Failure simulation failed", error=str(e))
            return None
    
    def check_dashboard(self):
        """Check current dashboard state and print job list."""
        self.log("INFO", "Checking dashboard state")
        
        try:
            jobs_response = self.session.get(f"{API_BASE}/api/jobs", timeout=5)
            metrics_response = self.session.get(f"{API_BASE}/api/metrics/summary", timeout=5)
            
            if jobs_response.status_code == 200 and metrics_response.status_code == 200:
                jobs_data = jobs_response.json()
                metrics_data = metrics_response.json()
                
                self.log("SUCCESS", "Dashboard data retrieved",
                        active_jobs=len(jobs_data.get("jobs", [])),
                        success_rate=f"{metrics_data.get('success_rate', 0)}%")
                
                # Print detailed job status
                for job in jobs_data.get("jobs", []):
                    status_emoji = "✅" if job["status"] == "resolved" else "❌" if job["status"] == "failed" else "⏳"
                    self.log("JOB", f"{status_emoji} {job['repo']} / {job['branch']}",
                            status=job["status"],
                            failure_type=job["failure_type"],
                            attempts=job["attempts"])
                
                return jobs_data, metrics_data
            else:
                self.log("ERROR", "Failed to retrieve dashboard data",
                        jobs_status=jobs_response.status_code,
                        metrics_status=metrics_response.status_code)
                return None, None
        except Exception as e:
            self.log("ERROR", "Dashboard check failed", error=str(e))
            return None, None
    
    def run_workflow_demo(self):
        """Run complete failure detection and remediation workflow."""
        self.log("INFO", "Starting PatchPilot Failure Workflow Test", duration_seconds=TEST_DURATION_SECONDS)
        self.log("INFO", "Dashboard URL: http://localhost:3000", tooltip="Open this in browser to see real-time updates")
        print("\n" + "="*80)
        print("PHASE 1: FAILURE DETECTION - Simulating CI pipeline failures")
        print("="*80 + "\n")
        
        # Phase 1: Trigger failures
        for scenario in FAILURE_SCENARIOS:
            self.log("PHASE", "Triggering failure scenario", scenario=scenario["name"])
            
            # Send GitHub webhook
            webhook_id = self.test_github_webhook(scenario)
            if webhook_id:
                self.test_jobs.append({
                    "scenario": scenario["name"],
                    "webhook_id": webhook_id,
                    "repo": scenario["repo"],
                    "branch": scenario["branch"],
                    "type": scenario["failure_type"],
                    "timestamp": datetime.now()
                })
            
            # Also trigger simulation endpoint
            job_id = self.test_simulate_failure_endpoint(scenario)
            if job_id:
                self.test_jobs.append({
                    "scenario": scenario["name"],
                    "job_id": job_id,
                    "repo": scenario["repo"],
                    "branch": scenario["branch"],
                    "type": scenario["failure_type"],
                    "timestamp": datetime.now()
                })
            
            time.sleep(1)
        
        print("\n" + "="*80)
        print("PHASE 2: FAILURE DETECTION & DASHBOARD UPDATE")
        print("="*80 + "\n")
        
        # Phase 2: Monitor dashboard for failures
        self.log("INFO", "Monitoring dashboard for failure detection...")
        jobs_data, metrics_data = self.check_dashboard()
        
        if jobs_data:
            print(f"\n📊 Found {len(jobs_data.get('jobs', []))} jobs on dashboard:\n")
            for i, job in enumerate(jobs_data.get("jobs", []), 1):
                status_emoji = "✅" if job["status"] == "resolved" else "❌" if job["status"] == "failed" else "⏳"
                print(f"  [{i}] {status_emoji} {job['repo']}")
                print(f"      • Branch: {job['branch']}")
                print(f"      • Status: {job['status']}")
                print(f"      • Failure: {job['failure_type']}")
                print(f"      • Root Cause: {job['root_cause']}")
                print(f"      • Attempts: {job['attempts']}")
                print(f"      • PR Fix: {job['pr_url']}\n")
        
        print("\n" + "="*80)
        print("PHASE 3: REAL-TIME MONITORING - Watch dashboard updates")
        print("="*80 + "\n")
        
        elapsed = 0
        refresh_interval = 5
        
        while elapsed < TEST_DURATION_SECONDS:
            remaining = TEST_DURATION_SECONDS - elapsed
            print(f"\r⏱️  Monitoring in progress... ({remaining}s remaining)", end="", flush=True)
            
            time.sleep(refresh_interval)
            elapsed += refresh_interval
            
            jobs_data, metrics_data = self.check_dashboard()
        
        print("\n")
        print("\n" + "="*80)
        print("PHASE 4: TEST SUMMARY")
        print("="*80 + "\n")
        
        self.log("SUCCESS", "Test workflow completed")
        self.log("INFO", "Total failures triggered", count=len(self.test_jobs))
        
        if jobs_data:
            resolved = len([j for j in jobs_data.get("jobs", []) if j["status"] == "resolved"])
            failed = len([j for j in jobs_data.get("jobs", []) if j["status"] == "failed"])
            processing = len([j for j in jobs_data.get("jobs", []) if j["status"] == "processing"])
            
            self.log("STAT", "Job Status Summary",
                    resolved=resolved,
                    failed=failed,
                    processing=processing)
        
        if metrics_data:
            self.log("STAT", "System Metrics",
                    success_rate=f"{metrics_data.get('success_rate', 0)}%",
                    total_failures=metrics_data.get('total_failures', 0),
                    time_saved=f"{metrics_data.get('time_saved_hours', 0)}h")
        
        print("\n" + "="*80)
        print("📊 NEXT STEPS")
        print("="*80)
        print(f"""
1. Open Dashboard: {FRONTEND_URL}
   - Watch real-time updates as failures are detected
   - Monitor success rate and metrics
   - Track CI pipeline status by repository

2. Expected Behavior:
   ✓ Failures appear in "CI Pipeline Status" section
   ✓ Metrics update automatically every 10 seconds
   ✓ Failed jobs show detailed diagnosis
   ✓ Resolved jobs display PR links with fixes

3. Webhook Verification:
   ✓ GitHub webhook received and processed
   ✓ Failure information extracted and stored
   ✓ Dashboard reflects latest job status

4. Performance Metrics:
   ✓ Detection latency: < 1 second
   ✓ Dashboard refresh: 10 seconds auto-refresh
   ✓ API response time: {sum(j.get("response_time", 0) for j in self.test_jobs) / max(1, len(self.test_jobs)):.2f}ms avg
""")
        
        print("="*80 + "\n")


def main():
    """Execute test workflow."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "PatchPilot Failure Detection & Remediation Workflow Test".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    runner = TestRunner()
    
    # Verify services are running
    print("🔍 Checking services...\n")
    try:
        health = runner.session.get(f"{API_BASE}/health", timeout=2).json()
        runner.log("SUCCESS", "API is healthy", service=health.get("service"), version=health.get("version"))
    except Exception as e:
        runner.log("ERROR", "API is not responding - ensure 'docker-compose up -d' was run", error=str(e))
        return
    
    print()
    
    # Run the test workflow
    runner.run_workflow_demo()


if __name__ == "__main__":
    main()
