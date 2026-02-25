# PatchPilot Workflow Demonstration - What to See in the Dashboard

## 🎯 Overview
This demonstrates the complete PatchPilot workflow:
1. **Failure Detection** - CI pipeline failures are detected via webhooks
2. **Real-Time Display** - Dashboard updates every 10 seconds
3. **Auto-Remediation** - Failures are automatically diagnosed and fixed
4. **Metrics Tracking** - Success rate, time saved, and other metrics update

---

## 📊 Dashboard URL
Open your browser to: **http://localhost:3000**

---

## ✅ What You Should See

### 1. **Metrics Cards** (Top Section)
These update in real-time every 10 seconds:

```
┌─────────────────────┐  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Success Rate       │  │ Total Failures    │  │ Time Saved   │  │ Avg Fix Time     │
│                     │  │                   │  │              │  │                  │
│      87.3%          │  │     1,247         │  │   312 hours  │  │   74 seconds     │
│                     │  │                   │  │              │  │                  │
└─────────────────────┘  └──────────────────┘  └──────────────┘  └──────────────────┘
```

### 2. **CI Pipeline Status Section** (Main Area)

You'll see multiple job cards:

#### ✅ **Resolved Jobs** (Green)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  charan-happy/red2green
  Branch: main
  Status: ✅ RESOLVED
  Failure Type: dep_conflict
  Root Cause: lodash version mismatch - auto-fixed by updating package.json
  Attempts: 1
  PR: https://github.com/charan-happy/red2green/pull/127
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### ⏳ **Processing Jobs** (Blue - while being fixed)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  charan-happy/red2green
  Branch: test/syntax-error
  Status: ⏳ PROCESSING (Auto-fixing...)
  Failure Type: syntax_error
  Root Cause: Missing colon in function definition line 42
  Attempts: 1
  PR: https://github.com/charan-happy/red2green/pull/716 (Creating...)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### ❌ **Failed Jobs** (Red - if auto-fix fails)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  mycompany/api-service
  Branch: feature/auth
  Status: ❌ FAILED (Requires Manual Review)
  Failure Type: type_error
  Root Cause: Missing return statement in async function
  Attempts: 2
  PR: https://github.com/mycompany/api-service/pull/456
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3. **System Overview Section** (Bottom)
```
Tracked Repositories: 3
  • charan-happy/red2green
  • mycompany/api-service
  • mycompany/web-ui

Detection Rate: 100%
Auto-Fix Rate: 87.3%
Processing Time: 2.3 minutes avg
System Uptime: 99.8%
```

---

## 🔄 Real-Time Update Behavior

### Timeline: What Happens When You Trigger Failures

**T+0s** - Failure Triggered
```
Status: ⏳ PROCESSING
(Dashboard fetches data every 10 seconds)
```

**T+2s** - Failure Visible in Dashboard
```
Status: ⏳ PROCESSING
PatchPilot agent analyzing the failure...
```

**T+10s** - First Dashboard Refresh
```
Card updates with latest status
Auto-fix attempt in progress
```

**T+15s** - Auto-Fix Complete
```
Status: ✅ RESOLVED
"lodash version mismatch - auto-fixed by updating package.json"
Button becomes green
PR link becomes active
```

**T+20s+** - Metrics Update
```
Success Rate: Still 87.3% (baseline)
Time Saved: Incremented
Total Jobs Resolved: Incremented
```

---

## 🧪 How to Test the Live Updates

### Option 1: Watch Real-Time Updates
1. Open dashboard at http://localhost:3000
2. Run the workflow test script
3. Watch the job cards appear and status change from ⏳ → ✅

### Option 2: Manual Failure Trigger
```bash
# Open another terminal and run:
curl -X POST http://localhost:8000/api/test/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "test/repo",
    "branch": "test-branch",
    "failure_type": "syntax_error",
    "root_cause": "Test failure to watch dashboard update"
  }'
```

3. Watch the dashboard immediately show the new job
4. See status change automatically after 15 seconds

### Option 3: Full Workflow Demo
```bash
cd /workspaces/red2green
bash scripts/demo_complete_workflow.sh
```

This will:
- Trigger 3 different failure types
- Show them appearing in the dashboard
- Monitor auto-remediation
- Display final metrics

---

## 📈 Metrics Interpretation

| Metric | What It Means |
|--------|---------------|
| **Success Rate** | Percentage of CI failures that were auto-fixed |
| **Total Failures** | Cumulative count of failures detected |
| **Auto-Fixed** | How many were automatically remediated |
| **Escalated** | Failures requiring manual intervention |
| **Time Saved** | Hours saved by automatic fixes (avoids manual work) |
| **Avg Fix Time** | Average seconds per failure to diagnose and fix |

---

## 🔧 Job Status Transitions

```
┌──────────────┐
│   QUEUED     │  (Initial state when failure detected)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PROCESSING   │  (Agent analyzing and applying fixes)
└──────┬───────┘
       │
       ├─────────────────────┬──────────────────┐
       ▼                     ▼                  ▼
    ┌──────────┐         ┌──────────┐      ┌──────────┐
    │ RESOLVED │         │ FAILED   │      │ ESCALATED│
    │  (Fixed) │         │ (Manual) │      │ (Review) │
    └──────────┘         └──────────┘      └──────────┘
```

---

## 📝 Failure Types You'll See

1. **dep_conflict** - Dependency version mismatch
2. **type_error** - Type checking failure
3. **syntax_error** - Python syntax issues
4. **import_error** - Circular imports or missing modules
5. **pipeline_failure** - CI/CD workflow failure
6. **build_failure** - Compilation/build error

---

## 🚀 Advanced: Webhook Integration

The system accepts webhooks from:
- **GitHub** - POST to `/api/webhooks/github`
- **GitLab** - POST to `/api/webhooks/gitlab`
- **Jenkins** - POST to `/api/webhooks/jenkins`
- **CircleCI** - POST to `/api/webhooks/circleci`

When a failure webhook arrives:
1. PatchPilot creates a job entry
2. Job appears on dashboard within 1-2 seconds
3. Status shows as "processing"
4. Auto-fix logic analyzes the error
5. Fix is applied (if possible)
6. Status updates to "resolved"
7. PR is created with the fix

---

## 💡 Pro Tips

1. **Auto-Refresh**: Dashboard refreshes every 10 seconds automatically
2. **Status Colors**: Green = good, Red = needs attention, Blue = in progress
3. **Real-Time**: Open multiple browser tabs to see updates in real-time
4. **Metrics**: Reload page to see metrics update
5. **Logs**: Watch backend logs with `docker logs red2green-api-1 -f`

---

## 🔍 Verifying the System

### Check API Health
```bash
curl http://localhost:8000/health | jq .
```

### List Current Jobs
```bash
curl http://localhost:8000/api/jobs | jq '.jobs'
```

### Get Metrics
```bash
curl http://localhost:8000/api/metrics/summary | jq .
```

### See Metrics in Grafana
```
http://localhost:3001 (admin/patchpilot)
```

---

## 📞 Need Help?

1. Check API logs: `docker logs red2green-api-1`
2. Check frontend logs: `docker logs red2green-frontend-1`
3. View API docs: `http://localhost:8000/api/docs`
4. Test endpoints manually with curl (examples above)

---

**Dashboard is live and ready to test!** 🎉
