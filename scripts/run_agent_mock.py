"""
Mock runner for SENTINEL agent that injects a fake `anthropic` client.
Run: python scripts/run_agent_mock.py
"""
import asyncio
import sys
import os
from types import SimpleNamespace

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Create a fake `anthropic` module with AsyncAnthropic that returns deterministic responses
class FakeAnthropicClient:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.messages = self

    async def create(self, model=None, max_tokens=None, messages=None):
        # messages is a list with a single dict containing the prompt in 'content'
        prompt = ""
        if messages and isinstance(messages, list) and len(messages) > 0:
            prompt = messages[0].get('content', '')

        if "Diagnose this CI failure" in prompt:
            payload = {
                "failure_type": "dep_conflict",
                "root_cause": "peer dependency mismatch for react version",
                "affected_files": ["package.json"],
                "error_summary": "Dependency resolution failed due to react version mismatch.",
                "confidence": 0.92,
                "suggested_approach": "align react versions or update peer dependencies"
            }
            text = json_str(payload)
        elif "Generate a minimal code fix" in prompt:
            payload = {
                "patches": [
                    {
                        "filename": "package.json",
                        "original_content": "{...react: \"17.0.2\"...}",
                        "patched_content": "{...react: \"18.2.0\"...}",
                        "explanation": "Bump react to satisfy @mui/material peer dependency"
                    }
                ],
                "explanation": "Bumped React to 18.2.0 to satisfy peer deps",
                "test_commands": ["npm install --legacy-peer-deps"],
                "confidence": 0.88
            }
            text = json_str(payload)
        else:
            text = json_str({"message": "unknown prompt"})

        # Return object with .content[0].text to match healing_agent expectations
        return SimpleNamespace(content=[SimpleNamespace(text=text)])


def json_str(obj):
    import json
    return json.dumps(obj)

# Inject fake module
import types
fake_anthropic = types.ModuleType('anthropic')
fake_anthropic.AsyncAnthropic = FakeAnthropicClient
sys.modules['anthropic'] = fake_anthropic

# Now run the real test runner
from agents.healing_agent import run_healing_job

SAMPLE_ERROR_LOG = """
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
"""

async def main():
    result = await run_healing_job(
        job_id="mock-001",
        repo_full_name="charan-happy/red2green",
        provider="github",
        commit_sha="abc1234def5678",
        branch="main",
        error_log=SAMPLE_ERROR_LOG,
        pipeline_url="https://example.com/mock",
        anthropic_api_key="mock-key",
    )

    print("=== MOCK RUN RESULT ===")
    print(f"Status: {result.status}")
    if result.diagnosis:
        print(f"Diagnosis: {result.diagnosis.failure_type} - {result.diagnosis.root_cause}")
    if result.fix_result:
        print(f"Fix patches: {len(result.fix_result.patches)}")
        for p in result.fix_result.patches:
            print(f" - {p.filename}: {p.explanation}")
    if result.errors:
        print(f"Errors: {result.errors}")

if __name__ == '__main__':
    asyncio.run(main())
