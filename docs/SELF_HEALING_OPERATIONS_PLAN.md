# Self-healing operations plan

## Current deployed boundary

The public portfolio is a read-only CloudFront/S3 site. It is independently available from Ubuntu and has a verified release archive, source restore check and browser check. The S3/Lambda data-quality stack is an executable demonstration template; it is not currently the production scheduler for AIOS, Drive capture, RAG refresh or paper finance.

## Required operational path

Each cloud worker must use the same bounded pattern:

1. EventBridge schedule or an approved source event starts one idempotent worker.
2. The worker reads a versioned input snapshot from private S3 and writes a content-addressed result.
3. Invalid or stale input is quarantined; it cannot update the public summary.
4. Failure is retried with a bounded policy and sent to a dead-letter queue.
5. CloudWatch alarms monitor failures, age of the last successful result and queue depth.
6. A repair worker can re-run an idempotent job or mark it for human review; it cannot send email, place trades or control a drone.
7. A scheduled restore check copies a dated manifest into a clean location and verifies hashes before a release is accepted.

## Completion gates

- [ ] Private versioned S3 evidence bucket and scoped secret storage deployed.
- [ ] EventBridge schedule, Lambda/Step Functions worker and idempotency key deployed.
- [ ] SQS dead-letter queue and CloudWatch alarms tested with a forced failure.
- [ ] Drive/Gmail/Calendar workers use read-only scopes and publish only approved summaries.
- [ ] RAG refresh produces a source manifest, citation evaluation and rollback snapshot.
- [ ] Finance worker remains paper/advisory-only with execution-deny tests.
- [ ] Independent restore drill passes for the site, source manifests and worker state.

Until these gates pass, the public site must describe AWS as the portfolio/evidence host and the Ubuntu services as the local operational system. This boundary prevents a static portfolio deployment from being mistaken for unattended production automation.
