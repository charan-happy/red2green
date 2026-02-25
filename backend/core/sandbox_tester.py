"""Sandbox environment for testing fixes before PR creation"""

import os
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class SandboxTestResult:
    """Result of testing a fix in sandbox"""
    
    def __init__(self, passed: bool, output: str = "", errors: str = "", duration_ms: float = 0):
        self.passed = passed
        self.output = output
        self.errors = errors
        self.duration_ms = duration_ms
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "output": self.output,
            "errors": self.errors,
            "duration_ms": self.duration_ms
        }


def setup_sandbox_environment(repo_path: str, job_id: str) -> Optional[str]:
    """
    Create isolated sandbox directory with repo copy
    
    Args:
        repo_path: Path to original repository
        job_id: Job ID for sandbox naming
    
    Returns:
        Path to sandbox directory or None if setup failed
    """
    try:
        # Create temporary directory
        sandbox_dir = tempfile.mkdtemp(prefix=f"patchpilot_sandbox_{job_id[:8]}_")
        
        # Copy repo to sandbox
        temp_repo = os.path.join(sandbox_dir, "repo")
        shutil.copytree(repo_path, temp_repo, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'node_modules', '.env'))
        
        logger.info("Sandbox environment created", 
                   job_id=job_id, 
                   sandbox_path=sandbox_dir,
                   repo_path=temp_repo)
        
        return temp_repo
    except Exception as e:
        logger.error("Failed to create sandbox", job_id=job_id, error=str(e))
        return None


def cleanup_sandbox(sandbox_path: str) -> bool:
    """Clean up sandbox environment"""
    try:
        if sandbox_path and os.path.exists(sandbox_path):
            parent = os.path.dirname(sandbox_path)
            shutil.rmtree(parent)
            logger.info("Sandbox cleaned up", path=sandbox_path)
            return True
    except Exception as e:
        logger.warning("Failed to cleanup sandbox", path=sandbox_path, error=str(e))
    return False


def test_python_fix(sandbox_path: str, failure_type: str) -> SandboxTestResult:
    """
    Test Python fix in sandbox environment
    
    Args:
        sandbox_path: Path to sandbox repo
        failure_type: Type of failure to test for
    
    Returns:
        SandboxTestResult with test outcomes
    """
    try:
        start_time = datetime.now()
        
        # Detect Python project requirements
        req_file = os.path.join(sandbox_path, "backend", "requirements.txt")
        if os.path.exists(req_file):
            # Install dependencies
            install_result = subprocess.run(
                ["pip", "install", "-q", "-r", req_file],
                cwd=sandbox_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if install_result.returncode != 0:
                logger.warning("Dependency install failed", stderr=install_result.stderr)
        
        # Run syntax checks
        test_commands = [
            # Python syntax check using direct import
            ["python", "-c", "import sys; sys.path.insert(0, 'backend'); import main"],
            ["python", "-c", "import sys; sys.path.insert(0, 'backend'); from agents import healing_agent"],
        ]
        
        # Add failure-specific tests
        if failure_type == "syntax_error":
            # For syntax errors, if imports work, syntax is likely OK
            test_commands.extend([
                ["python", "-c", "import sys; sys.path.insert(0, 'backend'); import main; print('✓ Syntax validated')"],
            ])
        elif failure_type == "import_error":
            test_commands.append(["python", "-c", "import sys; sys.path.insert(0, 'backend'); import main"])
        elif failure_type == "type_error":
            test_commands.append(["python", "-c", "import sys; sys.path.insert(0, 'backend'); from core import config"])
        elif failure_type == "dep_conflict":
            # Test that imports work
            test_commands.append(["python", "-c", "import github; import anthropic; print('Dependencies OK')"])
        
        all_output = []
        all_passed = True
        
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=sandbox_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    all_passed = False
                    all_output.append(f"❌ {' '.join(cmd)}\nError: {result.stderr}")
                else:
                    all_output.append(f"✅ {' '.join(cmd)}")
                    if result.stdout:
                        all_output.append(result.stdout)
            except subprocess.TimeoutExpired:
                all_passed = False
                all_output.append(f"⏱️ {' '.join(cmd)} - Timeout")
            except Exception as e:
                all_passed = False
                all_output.append(f"❌ {' '.join(cmd)} - {str(e)}")
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return SandboxTestResult(
            passed=all_passed,
            output="\n".join(all_output),
            errors="" if all_passed else "Some tests failed",
            duration_ms=duration_ms
        )
    
    except Exception as e:
        logger.error("Sandbox test failed", error=str(e))
        return SandboxTestResult(
            passed=False,
            errors=str(e),
            output="Test execution failed"
        )


def test_nodejs_fix(sandbox_path: str, failure_type: str) -> SandboxTestResult:
    """
    Test Node.js fix in sandbox environment
    
    Args:
        sandbox_path: Path to sandbox repo
        failure_type: Type of failure to test for
    
    Returns:
        SandboxTestResult with test outcomes
    """
    try:
        start_time = datetime.now()
        
        # Install dependencies if needed
        frontend_dir = os.path.join(sandbox_path, "frontend")
        if os.path.exists(frontend_dir):
            install_result = subprocess.run(
                ["npm", "install", "--silent"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            if install_result.returncode != 0:
                logger.warning("npm install failed", stderr=install_result.stderr[:200])
        
        # Run Node.js tests
        test_commands = [
            ["node", "--check", "src/app/page.js"],
        ]
        
        all_output = []
        all_passed = True
        
        # Only test if frontend directory exists
        if not os.path.exists(frontend_dir):
            all_output.append(f"⚠️  Frontend directory not found - skipping Node.js tests")
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return SandboxTestResult(
                passed=True,  # Don't fail if frontend doesn't exist
                output="\n".join(all_output),
                errors="",
                duration_ms=duration_ms
            )
        
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    all_passed = False
                    all_output.append(f"❌ {' '.join(cmd)}\nError: {result.stderr}")
                else:
                    all_output.append(f"✅ {' '.join(cmd)}")
            except subprocess.TimeoutExpired:
                all_passed = False
                all_output.append(f"⏱️ {' '.join(cmd)} - Timeout")
            except Exception as e:
                all_passed = False
                all_output.append(f"❌ {' '.join(cmd)} - {str(e)}")
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return SandboxTestResult(
            passed=all_passed,
            output="\n".join(all_output),
            errors="" if all_passed else "Some tests failed",
            duration_ms=duration_ms
        )
    
    except Exception as e:
        logger.error("Node.js sandbox test failed", error=str(e))
        return SandboxTestResult(
            passed=False,
            errors=str(e),
            output="Test execution failed"
        )


def test_fix_in_sandbox(
    repo_path: str,
    failure_type: str,
    job_id: str,
    tech_stack: str = "python"
) -> Dict[str, Any]:
    """
    Test fix in isolated sandbox environment
    
    Args:
        repo_path: Path to repository
        failure_type: Type of failure
        job_id: Job ID for test isolation
        tech_stack: 'python' or 'nodejs' or 'fullstack'
    
    Returns:
        Dict with test results and sandbox info
    """
    log = logger.bind(job_id=job_id, failure_type=failure_type)
    
    # Setup sandbox
    sandbox_path = setup_sandbox_environment(repo_path, job_id)
    if not sandbox_path:
        return {
            "tested": False,
            "passed": False,
            "sandbox": None,
            "error": "Failed to create sandbox",
            "tests": []
        }
    
    results = {
        "tested": True,
        "sandbox": sandbox_path,
        "tests": [],
        "passed": False,
        "total_duration_ms": 0
    }
    
    try:
        # Run appropriate tests
        if tech_stack in ["python", "fullstack"]:
            log.info("Running Python tests in sandbox")
            py_result = test_python_fix(sandbox_path, failure_type)
            results["tests"].append({
                "framework": "python",
                "result": py_result.to_dict()
            })
            results["total_duration_ms"] += py_result.duration_ms
        
        if tech_stack in ["nodejs", "fullstack"]:
            log.info("Running Node.js tests in sandbox")
            node_result = test_nodejs_fix(sandbox_path, failure_type)
            results["tests"].append({
                "framework": "nodejs",
                "result": node_result.to_dict()
            })
            results["total_duration_ms"] += node_result.duration_ms
        
        # Overall result: passed only if all tests passed
        results["passed"] = all(
            test["result"]["passed"] 
            for test in results["tests"]
        )
        
        status = "✅ PASSED" if results["passed"] else "❌ FAILED"
        log.info(f"Sandbox testing complete - {status}", 
                results=results)
    
    finally:
        # Cleanup sandbox
        cleanup_sandbox(sandbox_path)
        results["sandbox"] = None  # Remove after cleanup
    
    return results


def generate_sandbox_report(test_result: Dict[str, Any]) -> str:
    """Generate human-readable test report"""
    report = []
    report.append("=" * 60)
    report.append("SANDBOX TEST REPORT")
    report.append("=" * 60)
    report.append("")
    
    if not test_result.get("tested"):
        report.append("❌ Sandbox setup failed")
        report.append(f"Error: {test_result.get('error', 'Unknown')}")
        return "\n".join(report)
    
    if test_result.get("passed"):
        report.append("✅ ALL TESTS PASSED")
    else:
        report.append("❌ SOME TESTS FAILED")
    
    report.append(f"Duration: {test_result.get('total_duration_ms', 0):.0f}ms")
    report.append("")
    
    for test in test_result.get("tests", []):
        framework = test.get("framework", "unknown")
        result = test.get("result", {})
        report.append(f"[{framework.upper()}]")
        report.append("-" * 40)
        report.append(result.get("output", "No output"))
        report.append("")
    
    report.append("=" * 60)
    return "\n".join(report)
