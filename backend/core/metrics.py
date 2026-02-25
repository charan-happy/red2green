"""Prometheus metrics for PatchPilot application"""
from prometheus_client import Counter, Gauge, Histogram, Summary
import time

# Counters
webhook_events_total = Counter(
    'patchpilot_webhook_events_total',
    'Total webhook events received',
    ['provider']
)

jobs_resolved_total = Counter(
    'patchpilot_jobs_resolved_total',
    'Total jobs successfully resolved',
    ['failure_type']
)

jobs_escalated_total = Counter(
    'patchpilot_jobs_escalated_total',
    'Total jobs escalated to humans',
    ['failure_type']
)

# Gauges
current_jobs_total = Gauge(
    'patchpilot_current_jobs_total',
    'Current total number of jobs'
)

current_jobs_processing = Gauge(
    'patchpilot_current_jobs_processing',
    'Current jobs being processed'
)

success_rate = Gauge(
    'patchpilot_success_rate',
    'Current success rate percentage'
)

auto_fixed_count = Gauge(
    'patchpilot_auto_fixed_count',
    'Total auto-fixed jobs'
)

escalated_count = Gauge(
    'patchpilot_escalated_count',
    'Total escalated jobs'
)

time_saved_hours = Gauge(
    'patchpilot_time_saved_hours',
    'Total time saved in hours'
)

avg_fix_time_seconds = Gauge(
    'patchpilot_avg_fix_time_seconds',
    'Average fix time in seconds'
)

# Histograms
fix_time_seconds = Histogram(
    'patchpilot_fix_time_seconds',
    'Time taken to fix a failure in seconds',
    buckets=(5, 10, 30, 60, 120, 300, 600)
)

# Summaries
webhook_processing_time = Summary(
    'patchpilot_webhook_processing_seconds',
    'Time to process a webhook',
    ['provider']
)


def record_webhook_event(provider: str):
    """Record a webhook event"""
    webhook_events_total.labels(provider=provider).inc()


def record_job_resolved(failure_type: str, duration_seconds: float):
    """Record a successfully resolved job"""
    jobs_resolved_total.labels(failure_type=failure_type).inc()
    fix_time_seconds.observe(duration_seconds)


def record_job_escalated(failure_type: str):
    """Record a job escalated to humans"""
    jobs_escalated_total.labels(failure_type=failure_type).inc()


def update_metrics_summary(total: int, auto_fixed: int, escalated: int, 
                          success_rate_pct: float, avg_fix_time: float,
                          time_saved_hrs: float):
    """Update summary metrics from API data"""
    current_jobs_total.set(total)
    auto_fixed_count.set(auto_fixed)
    escalated_count.set(escalated)
    success_rate.set(success_rate_pct)
    avg_fix_time_seconds.set(avg_fix_time)
    time_saved_hours.set(time_saved_hrs)
