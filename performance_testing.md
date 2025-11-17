# Performance Testing Plan

## Objectives
- Ensure FastAPI backend sustains >100 concurrent sessions with <400 ms median response time
- Validate memory footprint stays <300 MB during 10-minute soak
- Confirm containerized deployment matches bare-metal profile

## Tooling
- locust or k6 for HTTP load (scripts referenced in comments)
- watch -n 5 docker stats when running containers
- Browser DevTools performance tab for frontend rendering metrics

## Scenarios
| ID | Scenario | Users | Spawn Rate | Duration | Success Criteria |
| --- | --- | --- | --- | --- | --- |
| PT-01 | Start session only (/api/ivr/start) | 50 | 5/s | 5 min | Avg latency < 300 ms |
| PT-02 | Full interaction loop (start  input  end) | 75 | 10/s | 10 min | Error rate < 1% |
| PT-03 | Flow exploration randomizer hitting /api/flows and /api/session/{id} | 100 | 15/s | 8 min | 95th percentile < 600 ms |
| PT-04 | Health probe storm (/health) | 150 | 20/s | 3 min | Zero failures |

## Metrics to Capture
- Response time (avg, p95, p99)
- Throughput (req/s)
- CPU + memory from container runtime
- Error codes distribution
- Notes on GC pauses or uvicorn warnings

## Procedure
1. Build Docker image via docker compose build
2. Run stack: docker compose -f milestone4/deployment/docker-compose.yml up -d
3. Execute load scripts against http://localhost:8000
4. Export reports to milestone4/test_report.md
5. Stop stack and archive logs in ackend/logs/perf_<timestamp>.txt

## Risks
- Local hardware limits; document specs before run
- Randomized NLP replies; pin seed via env var when possible

## Acceptance
Performance suite considered passed when all scenarios hit success criteria and resource usage stays within envelope.

