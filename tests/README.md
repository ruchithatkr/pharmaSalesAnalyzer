# tests

Unit and integration tests.

Coverage required:
- Reach/frequency/coverage/productivity/attainment/growth formulas
- Filters and aggregations (aggregation reconciliation against source-level sums)
- Ranking logic and deterministic tie handling
- Recommendation generation (evidence-linking, no unsupported claims)
- Role-based access restrictions (territory/region scoping)
- File ingestion/upload validation (schema checks, duplicate detection, malformed
  data)
- Chatbot evidence-linking (every answer traceable to a computed metric)

Run in CI on every PR — see [deployment/](../deployment/) for pipeline config.
