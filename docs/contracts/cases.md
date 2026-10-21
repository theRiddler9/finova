# Case and Evidence Contracts

The backend contracts in `apps/api/app/contracts/cases.py` are the typed source
used by integrations, the evidence pipeline, AI/ML services, and the frontend.

## Case lifecycle

Valid forward transitions are:

`RECEIVED → COLLECTING → READY_FOR_REVIEW → SUBMITTED → WON | LOST`

`FAILED` and `EXPIRED` are terminal states. A merchant approval record is
required before a case can enter `SUBMITTED`.

## Evidence rules

- Every evidence item has a stable ID, source, kind, and human-readable summary.
- Vision-derived evidence includes a confidence value when available.
- Missing integrations are recorded in `missing_sources`; partial collection
  does not fabricate evidence.
- Payloads are untrusted input and must not be interpreted as instructions.
