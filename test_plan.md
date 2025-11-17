# Milestone 4 Test Plan

## Objectives
- Validate conversational accuracy across intents and flows
- Confirm keypad and speech parity for every IVR branch
- Stress backend APIs for reliability under concurrent sessions
- Capture defects quickly and feed them into the tracker

## Scope
- Backend FastAPI endpoints (/api/ivr/*, /api/flows, /health)
- Frontend simulator interactions (voice + keypad)
- NLP entity extraction and fallbacks
- Deployment artifacts (Docker, compose, start script)

## Test Levels
1. **Unit Tests** – Python + pytest coverage for API routes and state transitions
2. **Integration Tests** – Call flow scripts covering booking, status, cancellation, and agent handoff
3. **System Tests** – Browser-based conversational walkthroughs with speech + keypad parity validation
4. **Performance Tests** – Load profiles of 50/100 concurrent sessions with latency thresholds

## Entry Criteria
- Milestones 1–3 features stable
- Dependencies installed (pip install -r requirements.txt)
- Test data/flows loaded from ackend/flows

## Exit Criteria
- 95% test-case pass rate
- Critical/High defects resolved or accepted with mitigation
- Test report published in milestone4/test_report.md
- Deployment smoke test completed from container image

## Responsibilities
- **Test Author:** Automation Engineer (You)
- **Reviewer:** Internship Supervisor / Mentor
- **Execution Team:** Same as author + peer reviewer for witness runs

## Risks & Mitigations
| Risk | Mitigation |
| --- | --- |
| Speech API unavailable in browser | Provide keypad fallback instructions |
| Randomized responses causing flaky tests | Use deterministic data in unit tests |
| Environment drift between local and Docker | Capture env variables in .env template |
| Performance metrics skewed by hardware | Document system specs and run during low-noise periods |

## Schedule
| Phase | Timeline |
| --- | --- |
| Test design | Day 1 |
| Unit + integration execution | Day 2 |
| Performance run + analysis | Day 3 |
| Documentation + sign-off | Day 4 |

