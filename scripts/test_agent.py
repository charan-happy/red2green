"""
SENTINEL Agent Test
Tests the Claude-powered diagnosis and fix generation.
Run: python scripts/test_agent.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.healing_agent import run_healing_job

SAMPLE_ERROR_LOG = """
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR! 
npm ERR! While resolving: myapp@1.0.0
npm ERR! Found: react@17.0.2
npm ERR! node_modules/react
npm ERR!   react@"^17.0.2" from the root project
npm ERR! 
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^18.0.0" from @mui/material@5.15.0
npm ERR! node_modules/@mui/material
npm ERR!   @mui/material@"^5.15.0" from the root project
npm ERR! 
npm ERR! Fix the upstream dependency conflict, or retry
npm ERR! this command with --force or --legacy-peer-deps.
"""

async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        # Try reading from .env
        try:
            with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found. Set it in .env or environment.")
        sys.exit(1)

    print("🛡️  SENTINEL Agent Test")
    print("=" * 50)
    print("📋 Simulating CI failure: npm dependency conflict")
    print()

    result = await run_healing_job(
        job_id="test-001",
        repo_full_name="charan-happy/red2green",
        provider="github",
        commit_sha="abc1234def5678",
        branch="main",
        error_log=SAMPLE_ERROR_LOG,
        pipeline_url="https://github.com/charan-happy/red2green/actions/runs/test",
        anthropic_api_key=api_key,
    )

    print(f"✅ Status: {result.status.value}")
    print()
    if result.diagnosis:
        print(f"🔍 Diagnosis:")
        print(f"   Type:        {result.diagnosis.failure_type}")
        print(f"   Root Cause:  {result.diagnosis.root_cause}")
        print(f"   Confidence:  {result.diagnosis.confidence:.0%}")
        print(f"   Approach:    {result.diagnosis.suggested_approach}")
    print()
    if result.fix_result:
        print(f"🔧 Fix Generated:")
        print(f"   Files changed: {len(result.fix_result.patches)}")
        print(f"   Confidence:    {result.fix_result.confidence:.0%}")
        print(f"   Explanation:   {result.fix_result.explanation}")
        for patch in result.fix_result.patches:
            print(f"\n   📄 {patch.filename}")
            print(f"      {patch.explanation}")
    print()
    if result.pr_url:
        print(f"🔀 PR URL: {result.pr_url}")
    if result.errors:
        print(f"⚠️  Errors: {result.errors}")
    print()
    print("=" * 50)
    print("✅ SENTINEL agent test complete!")

if __name__ == "__main__":
    asyncio.run(main())
