# deployment

CI/CD, environment configuration, and deployment manifests.

- CI pipeline: KPI regression tests, role-access tests, prompt/recommendation
  evaluation, security checks — run on every release (see [tests/](../tests/) and
  [evals/](../evals/))
- Environment config for approved commercial analytics environment (enterprise
  authentication, auditability, secure data access)
- Pilot/UAT rollout config (single brand/region pilot before wider deployment)
