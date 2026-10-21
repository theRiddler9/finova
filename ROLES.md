# ROLES.md: Team of 5

Each person **owns** a slice end-to-end. Contracts between slices (API schemas, DB models) are agreed on **Day 1** and live in `docs/contracts/`.

| # | Role | Owner | Primary stack |
|---|---|---|---|
| 1 | Integrations | Kartikay | FastAPI, PayPal / Shopify / Shippo / Zendesk APIs |
| 2 | Backend & Data Platform | Akash | FastAPI, Postgres, Redis/ARQ, Supabase |
| 3 | AI Engineer (LLM + Vision) | Joy | Gemini (Google AI Studio) / NVIDIA NIM, vision, prompt design |
| 4 | ML Engineer | Umika | LightGBM, SHAP, synthetic data, MLflow |
| 5 | Frontend | Shashwat | Next.js, Tailwind, shadcn/ui, pitch |

---

## 1. Integrations
**Mission:** Get real data flowing in from every external system.

**Owns**
- `apps/api/app/integrations/*` (PayPal, Shopify, Shippo, Zendesk clients)
- PayPal webhook receiver and signature verification
- PayPal `provide-evidence` submission flow
- Sandbox setup (PayPal sandbox, Shopify dev store, test Zendesk)
- Architecture decisions, PR reviews, merge gatekeeper

**Deliverables**
- Typed client per integration with retries and mocked tests
- Webhook handler for `CUSTOMER.DISPUTE.CREATED / UPDATED / RESOLVED`
- Merchant onboarding / credential connection flow (OAuth where applicable)

## 2. Backend & Data Platform
**Mission:** Make the pipeline reliable, fast and secure.

**Owns**
- `apps/api/app/pipeline/*`, `models/`, `core/`
- DB schema + Alembic migrations, Row Level Security policies
- Queue/worker orchestration (parallel evidence fetch, idempotency, retries)
- Case state machine: `RECEIVED → COLLECTING → READY_FOR_REVIEW → SUBMITTED → WON/LOST`
- Deadline tracking and notifications; credential encryption; file storage

**Deliverables**
- REST API consumed by the frontend (OpenAPI spec published Day 1)
- Evidence bundle schema (single source of truth for AI + ML + UI)
- Docker Compose, CI, deployment

## 3. AI Engineer (LLM + Vision)
**Mission:** Turn raw evidence into a trustworthy, compliant defense.

**Owns**
- `apps/api/app/ai/*` (prompts, vision extraction, draft generator)
- Vision: tracking ID, address, delivery signals from photos/labels
- Evidence validation (address mismatch, date conflicts, prior complaints)
- Draft generator with **source citations** and JSON-structured output
- Evaluation set: 20+ sample disputes to test hallucination and tone

**Rules**
- Never fabricate facts; every claim maps to an evidence item ID
- Prompt versions tracked in `ai/prompts/` with changelog

## 4. ML Engineer
**Mission:** Give merchants an honest, explainable win probability.

**Owns**
- `ml/` and `apps/api/app/ml/*`
- Synthetic dataset generator based on PayPal evidence rules
- Feature engineering: signature present, delivery photo, address match, prior customer messages, order value, customer dispute history, days to deliver
- LightGBM training, calibration, SHAP explanations, MLflow tracking
- "Missing evidence → score impact" suggestions
- Retraining hook for real outcomes

**Deliverables**
- Versioned model artifact + `predict(evidence_bundle)` function
- Model card documenting limits (synthetic data caveat)

## 5. Frontend
**Mission:** Make the merchant say "wow" within 10 seconds.

**Owns**
- `apps/web/*`: dispute list, evidence timeline, win-score gauge, draft editor, deadline badges
- UX writing, branding, landing page
- Demo script, seed data, pitch deck, 3-minute video
- Final QA of the end-to-end demo flow

**Deliverables**
- Dashboard screens against mocked API on Day 1, then real API
- Polished demo with a reliable fallback (recorded flow)

---

## Working Agreements
- **Branching:** `main` is protected; use `feat/<role>-<topic>`; PRs need 1 review
- **Contracts first:** change a schema → update `docs/contracts/` and tell the team in the same PR
- **Daily sync:** 15 min stand-up, blockers first
- **Cross-support:** #1 and #2 pair on pipeline; #3 and #4 share the evidence feature schema; #5 integrates against mocks early
- **Freeze:** code freeze 3 hours before submission; only bug fixes after

## Suggested Timeline
| Phase | Focus |
|---|---|
| Day 1 | Contracts, repo, sandboxes, mocked UI, schema |
| Day 2 | Integrations + pipeline + vision + synthetic data |
| Day 3 | LLM drafting, ML scoring, UI wired to real API |
| Final stretch | Integration testing, demo polish, pitch, freeze |

