'use client';

import { useState, useEffect } from 'react';

export default function Home() {
  const [jobs, setJobs] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const fetchData = async () => {
    try {
      const [jobsRes, metricsRes] = await Promise.all([
        fetch('/api/jobs').then(r => {
          if (!r.ok) throw new Error(`Jobs request failed: ${r.status}`);
          return r.json();
        }),
        fetch('/api/metrics/summary').then(r => {
          if (!r.ok) throw new Error(`Metrics request failed: ${r.status}`);
          return r.json();
        })
      ]);
      setJobs(jobsRes.jobs || []);
      setMetrics(metricsRes);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 10 seconds for real-time updates
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <main style={{ padding: '2rem' }}>
        <div style={{ textAlign: 'center', paddingTop: '2rem' }}>
          <h2>� Loading PatchPilot Dashboard...</h2>
          <p style={{ color: '#888', marginTop: '1rem' }}>Connecting to services...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main style={{ padding: '2rem' }}>
        <div style={{ color: '#ff6b6b', textAlign: 'center', paddingTop: '2rem' }}>
          <h2>⚠️ Error Loading Dashboard</h2>
          <p>{error}</p>
          <button 
            onClick={() => { setLoading(true); fetchData(); }}
            style={{ marginTop: '1rem', padding: '0.5rem 1rem', cursor: 'pointer', background: '#4dabf7', color: '#fff', border: 'none', borderRadius: '4px' }}
          >
            Retry
          </button>
        </div>
      </main>
    );
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ margin: 0 }}>🔧 PatchPilot Dashboard</h1>
        <div style={{ fontSize: '0.85rem', color: '#888' }}>
          Last updated: {lastUpdated.toLocaleTimeString()}
          <button 
            onClick={fetchData}
            style={{ marginLeft: '1rem', padding: '0.25rem 0.75rem', background: '#4dabf7', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem' }}
          >
            Refresh Now
          </button>
        </div>
      </div>

      {/* Key Metrics Row */}
      {metrics && (
        <>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
            marginBottom: '2rem'
          }}>
            <div style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              padding: '1.5rem', 
              borderRadius: '12px',
            }}>
              <div style={{ color: '#ddd', fontSize: '0.85rem', textTransform: 'uppercase', fontWeight: '600' }}>Success Rate</div>
              <div style={{ fontSize: '2.5rem', fontWeight: '900', marginTop: '0.5rem', color: '#fff' }}>
                {metrics.success_rate?.toFixed(1) || 0}%
              </div>
              <div style={{ color: '#ccc', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                {metrics.auto_fixed || 0} auto-fixed
              </div>
            </div>

            <div style={{ 
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              padding: '1.5rem', 
              borderRadius: '12px',
            }}>
              <div style={{ color: '#ddd', fontSize: '0.85rem', textTransform: 'uppercase', fontWeight: '600' }}>Total Failures</div>
              <div style={{ fontSize: '2.5rem', fontWeight: '900', marginTop: '0.5rem', color: '#fff' }}>
                {metrics.total_failures || 0}
              </div>
              <div style={{ color: '#ccc', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                {metrics.escalated || 0} escalated
              </div>
            </div>

            <div style={{ 
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              padding: '1.5rem', 
              borderRadius: '12px',
            }}>
              <div style={{ color: '#ddd', fontSize: '0.85rem', textTransform: 'uppercase', fontWeight: '600' }}>Time Saved</div>
              <div style={{ fontSize: '2.5rem', fontWeight: '900', marginTop: '0.5rem', color: '#fff' }}>
                {metrics.time_saved_hours || 0}h
              </div>
              <div style={{ color: '#ccc', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                vs manual fixes
              </div>
            </div>

            <div style={{ 
              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
              padding: '1.5rem', 
              borderRadius: '12px',
            }}>
              <div style={{ color: '#ddd', fontSize: '0.85rem', textTransform: 'uppercase', fontWeight: '600' }}>Avg Fix Time</div>
              <div style={{ fontSize: '2.5rem', fontWeight: '900', marginTop: '0.5rem', color: '#fff' }}>
                {metrics.avg_fix_time_seconds || 0}s
              </div>
              <div style={{ color: '#ccc', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                per failure
              </div>
            </div>
          </div>
        </>
      )}

      {/* Active Failures Section */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem', color: '#fff' }}>🚨 CI Pipeline Status</h2>
        {jobs && jobs.length > 0 ? (
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '1rem'
          }}>
            {jobs.map((job) => {
              const isResolved = job.status === 'resolved';
              const isFailed = job.status === 'failed' || job.status === 'failing';
              const isProcessing = job.status === 'processing' || job.status === 'in_progress';
              
              return (
                <div 
                  key={job.id}
                  style={{ 
                    background: isResolved ? '#1a3a1a' : isFailed ? '#3a1a1a' : '#1a2a3a',
                    padding: '1.5rem', 
                    borderRadius: '12px',
                    border: isResolved ? '1px solid #51cf66' : isFailed ? '1px solid #ff6b6b' : '1px solid #4dabf7',
                    borderLeft: `4px solid ${isResolved ? '#51cf66' : isFailed ? '#ff6b6b' : '#4dabf7'}`
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                    <div>
                      <div style={{ fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '0.25rem' }}>
                        📦 {job.repo}
                      </div>
                      <div style={{ color: '#888', fontSize: '0.85rem' }}>
                        Branch: <code style={{ background: '#333', padding: '0.2rem 0.4rem', borderRadius: '3px' }}>{job.branch}</code>
                      </div>
                    </div>
                    <div style={{ 
                      background: isResolved ? '#51cf66' : isFailed ? '#ff6b6b' : '#4dabf7',
                      color: '#000',
                      padding: '0.4rem 0.8rem',
                      borderRadius: '6px',
                      fontSize: '0.8rem',
                      fontWeight: 'bold',
                      textTransform: 'uppercase'
                    }}>
                      {isProcessing ? '⏳ ' : isResolved ? '✅ ' : '❌ '}{job.status}
                    </div>
                  </div>

                  <div style={{ background: '#0f1419', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
                    <div style={{ color: '#888', fontSize: '0.75rem', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: '600' }}>Failure Details</div>
                    <div style={{ color: '#ccc', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                      <strong>Type:</strong> {job.failure_type?.toUpperCase() || 'UNKNOWN'}
                    </div>
                    <div style={{ color: '#ccc', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
                      <strong>Root Cause:</strong> {job.root_cause || 'Analyzing...'}
                    </div>
                    <div style={{ color: '#ccc', fontSize: '0.9rem' }}>
                      <strong>Attempts:</strong> {job.attempts || 0}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    {job.pr_url && (
                      <a 
                        href={job.pr_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ 
                          flex: 1,
                          background: '#4dabf7',
                          color: '#fff',
                          padding: '0.6rem',
                          borderRadius: '6px',
                          textDecoration: 'none',
                          textAlign: 'center',
                          fontSize: '0.85rem',
                          fontWeight: '600'
                        }}
                      >
                        → View PR
                      </a>
                    )}
                    <button 
                      onClick={fetchData}
                      style={{ 
                        background: '#333',
                        color: '#888',
                        padding: '0.6rem 1rem',
                        borderRadius: '6px',
                        border: 'none',
                        cursor: 'pointer',
                        fontSize: '0.85rem'
                      }}
                    >
                      Refresh
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ 
            background: '#0f3a0f',
            padding: '2rem',
            borderRadius: '12px',
            border: '1px solid #51cf66',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
            <div style={{ fontSize: '1.1rem', color: '#51cf66', fontWeight: 'bold' }}>All CI Pipelines Healthy</div>
            <div style={{ color: '#888', marginTop: '0.5rem' }}>No active failures detected</div>
          </div>
        )}
      </div>

      {/* Tracked Repositories Summary */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem', color: '#fff' }}>📊 System Overview</h2>
        <div style={{
          background: '#1a1f2e',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid #333'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
            <div>
              <div style={{ color: '#888', fontSize: '0.85rem', marginBottom: '0.5rem' }}>Tracked Repositories</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                {jobs?.length || 1}
              </div>
            </div>
            <div>
              <div style={{ color: '#888', fontSize: '0.85rem', marginBottom: '0.5rem' }}>Detection Rate</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                {metrics?.success_rate?.toFixed(1) || 0}%
              </div>
            </div>
            <div>
              <div style={{ color: '#888', fontSize: '0.85rem', marginBottom: '0.5rem' }}>Processing Time</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                {metrics?.avg_fix_time_seconds || 0}s
              </div>
            </div>
            <div>
              <div style={{ color: '#888', fontSize: '0.85rem', marginBottom: '0.5rem' }}>Auto-Fix Rate</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                {metrics?.total_failures ? Math.round((metrics.auto_fixed / metrics.total_failures) * 100) : 0}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
