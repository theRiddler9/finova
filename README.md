<h1 align="center">FINOVA</h1>

<p align="center">
  <strong>Automated evidence collection and defense drafting for fraudulent PayPal disputes, built for merchants.</strong>
</p>

<p align="center">
  <img src="docs/assets/finova-demo.png" alt="Finova Dispute Dashboard" width="90%">
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#the-problem">The Problem</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#requirements">Requirements</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#team">Team</a>
</p>

---

## Overview

**Finova** is a merchant-facing platform that turns a new PayPal dispute into a complete, reviewable defense within minutes of it being filed.

Instead of asking support agents to search Shopify, carrier sites and helpdesks by hand, Finova **listens for PayPal dispute webhooks, pulls order, shipping and customer-communication data in parallel, reads delivery photos and labels with Vision AI, scores the likelihood of winning, and drafts a PayPal-compliant response** that cites only verified evidence. The merchant reviews, edits and approves before anything is submitted.

Finova is built strictly for sellers and e-commerce businesses. It is not a customer-facing product. Its value is revenue protection and operational time savings.

> [!IMPORTANT]
> **Human approval is mandatory.** Finova never submits evidence to PayPal without explicit merchant approval, and its drafts never include claims that are not backed by retrieved evidence.

---

## The Problem

Merchants lose revenue and hours of work chasing evidence across disconnected platforms to contest "item not received" fraud. Missed response deadlines result in default rulings against the seller.

**Example scenario.** A customer buys a $200 jacket, receives it, then opens a PayPal dispute claiming it never arrived. Today a support agent must:

1. Open **Shopify** to verify the order and fulfillment.
2. Open the **carrier site** (FedEx, UPS and others) to find delivery confirmation.
3. Open **Zendesk** to check for prior complaints or messages from the customer.
4. Manually write and format the defense.

This takes roughly 20 minutes per case, and the work repeats for every dispute.

---

## How It Works

When PayPal fires a `CUSTOMER.DISPUTE.CREATED` webhook, Finova runs the following pipeline:

| Step | Stage | Description |
|---|---|---|
| 1 | **Ingest** | Verifies the webhook signature and fetches full dispute details from the PayPal Disputes API. |
| 2 | **Collect** | Retrieves Shopify order and fulfillment data, carrier tracking (Shippo) and Zendesk ticket history in parallel. |
| 3 | **Extract** | Vision AI reads tracking IDs, addresses and delivery details from proof-of-delivery photos and shipping labels. |
| 4 | **Validate** | Cross-checks addresses, dates, amounts and customer messages for contradictions and gaps. |
| 5 | **Score** | A LightGBM model returns a win probability with SHAP-based explanations of each contributing factor. |
| 6 | **Draft** | An LLM writes a structured defense in PayPal's expected format, citing an evidence ID for every claim. |
| 7 | **Approve** | The merchant reviews the evidence timeline, edits the draft and submits through the PayPal `provide-evidence` endpoint. |

---

## Features

- **Webhook-Driven Evidence Pipeline:** Dispute events are acknowledged immediately and processed asynchronously through a Redis-backed queue, with idempotent handlers and automatic retries.
- **Evidence Timeline:** A single chronological view of order placed, fulfilled, in transit, delivered and customer messages, with the source of each event.
- **Vision Extraction:** Tracking numbers, delivery addresses and delivery signals are extracted from photos and labels, each returned with a confidence value. Low-confidence fields are flagged for human review.
- **Explainable Win Probability:** Every score is accompanied by the top contributing factors and a list of missing evidence that would improve the outcome.
- **Cited Defense Drafts:** The editable draft maps each statement to a retrieved evidence item. Unsupported claims are flagged rather than written.
- **Deadline Tracking:** Response deadlines are stored and surfaced on every case so that no dispute defaults silently.
- **Outcome History:** Case results are stored and used as the basis for retraining the scoring model.
- **Tenant Isolation:** Merchant data is separated with Row Level Security, and stored credentials are encrypted at rest.

---

## Architecture

```
PayPal --webhook--> FastAPI (verify signature) --> Redis queue
                                                      |
                                              Evidence Worker
                                                      |
      +----------------+----------------+-------------+-----------------+
      |                |                |             |                 |
PayPal Disputes   Shopify Admin    Shippo / Carrier  Zendesk        Vision AI
     API              API           Tracking API      API       (photos and labels)
      |                |                |             |                 |
      +----------------+----------------+-------------+-----------------+
                                        |
                        Evidence Bundle (Postgres + Storage)
                                        |
              +-------------------------+-------------------------+
              |                         |                         |
     Win-Probability ML         LLM Draft Generator        Validation Rules
              |                         |                         |
              +-------------------------+-------------------------+
                                        |
                       Next.js Dashboard (merchant review)
                                        |
                        PayPal provide-evidence API
```

**Case lifecycle:** `RECEIVED` → `COLLECTING` → `READY_FOR_REVIEW` → `SUBMITTED` → `WON` | `LOST` (with `FAILED` and `EXPIRED` as terminal error states).

---

## Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | **Next.js 15 + TypeScript** | App Router, strict mode, Tailwind CSS, shadcn/ui, TanStack Query |
| **Backend** | **FastAPI (Python 3.12)** | Async I/O, Pydantic v2, SQLAlchemy 2, Alembic migrations |
| **Queue / Workers** | **Redis + ARQ** | Background evidence collection, retries, idempotent job handling |
| **Database** | **PostgreSQL (Supabase)** | Case states, merchant configuration, historical outcomes |
| **Storage** | **Supabase Storage** | Delivery photos, evidence files, generated PDFs |
| **Auth and Security** | **Supabase Auth + RLS** | Per-merchant isolation, encrypted credentials (Fernet / Supabase Vault) |
| **LLM** | **Google AI Studio (Gemini), free tier** | Structured JSON output for summarization, validation reasoning and drafting; NVIDIA NIM as a drop-in alternative |
| **Computer Vision** | **Gemini Vision (multimodal)** | Photo and label extraction; vision-capable NVIDIA NIM models or Google Document AI as optional fallbacks |
| **Predictive ML** | **LightGBM + SHAP** | Win-probability scoring with explanations, tracked with MLflow |
| **Integrations** | **PayPal, Shopify, Shippo, Zendesk** | PayPal Disputes API v1 and Webhooks, Shopify Admin GraphQL, Shippo Tracking, Zendesk Support |
| **DevOps** | **Docker Compose + GitHub Actions** | Vercel for the web app, Railway or Render for the API |
| **Observability** | **Structlog + Sentry** | Structured logs and error tracking across webhook flows |
| **Testing** | **Pytest, Vitest, Playwright** | `respx` for mocked external APIs |
| **Architecture** | **Monorepo** | `apps/web`, `apps/api`, `ml`, `infra`, `docs` |

> [!NOTE]
> Until real dispute outcomes are available, the win-probability model is trained on a **synthetic dataset** generated from documented PayPal "item not received" evidence rules. The pipeline is designed to retrain on real outcomes as they accumulate, and the UI and model card state this limitation.

---

## Requirements

Ensure the following are available before running Finova:

1. **Python:** 3.12 or later.
2. **Node.js:** 20 LTS or later, with **pnpm**.
3. **Docker:** For local PostgreSQL and Redis via Docker Compose.
4. **PayPal Developer Account:** Sandbox app credentials and a configured webhook ID.
5. **Shopify Development Store:** An app with Admin API access to orders and fulfillments.
6. **Shippo Account:** API token for tracking lookups.
7. **Zendesk Account:** Subdomain and API token with read access to tickets.
8. **LLM Provider Key (free tier):** A [Google AI Studio](https://aistudio.google.com/) API key (default) or an [NVIDIA NIM](https://build.nvidia.com/) API key. Any OpenAI-compatible endpoint works, so no paid subscription is required.
9. **Supabase Project:** For database, storage and authentication.
10. **ngrok (or equivalent):** To expose local webhooks to the PayPal sandbox.

---

## Quick Start

Follow these steps from the repository root.

### 1. Clone and Configure

```bash
git clone https://github.com/<your-org>/finova.git
cd finova
cp .env.example .env
```

Open `.env` and fill in your sandbox credentials:

```bash
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_WEBHOOK_ID=
PAYPAL_ENV=sandbox

SHOPIFY_API_KEY=
SHOPIFY_API_SECRET=
SHOPIFY_STORE_DOMAIN=

SHIPPO_API_TOKEN=

ZENDESK_SUBDOMAIN=
ZENDESK_EMAIL=
ZENDESK_API_TOKEN=

# LLM provider (OpenAI-compatible). Default: Google AI Studio
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_API_KEY=
LLM_MODEL=
VISION_MODEL=
# Alternative: NVIDIA NIM
# LLM_BASE_URL=https://integrate.api.nvidia.com/v1

SUPABASE_URL=
SUPABASE_SERVICE_KEY=
DATABASE_URL=
REDIS_URL=
ENCRYPTION_KEY=
```

### 2. Start Infrastructure

```bash
docker compose up -d
```

### 3. Run the Backend

```bash
cd apps/api
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

### 4. Start the Worker

```bash
cd apps/api
arq app.worker.WorkerSettings
```

### 5. Launch the Dashboard

```bash
cd apps/web
pnpm install
pnpm dev
```

### 6. Receive Sandbox Webhooks

```bash
ngrok http 8000
```

Register the generated HTTPS URL as a webhook endpoint in your PayPal sandbox app, subscribing to `CUSTOMER.DISPUTE.CREATED`, `CUSTOMER.DISPUTE.UPDATED` and `CUSTOMER.DISPUTE.RESOLVED`.

---

## Demo Walkthrough

1. Trigger a sandbox "item not received" dispute for a $200 order.
2. The case appears in the dashboard within seconds.
3. The evidence timeline populates from Shopify, the carrier, Zendesk and the delivery photo.
4. A win probability is displayed alongside the factors that produced it.
5. The merchant reviews and edits the cited draft, then approves submission to PayPal.

---

## Success Metrics

| Metric | Target |
|---|---|
| Time to first draft | From approximately 20 minutes to under 2 minutes |
| Evidence coverage | Share of cases with order, tracking and communication evidence attached |
| Deadline compliance | Disputes defended before the PayPal response deadline |
| Win-rate lift | Improvement compared with the manual baseline |

---

## Roadmap

- [x] **Project Foundation:** Monorepo structure, integration contracts and sandbox environments.
- [ ] **PayPal Webhook Ingestion:** Signature verification, idempotent handling and case creation.
- [ ] **Evidence Collection:** Shopify, Shippo and Zendesk clients with parallel retrieval and partial-failure handling.
- [ ] **Vision Extraction:** Tracking ID, address and delivery signal extraction with confidence values.
- [ ] **Win-Probability Scoring:** LightGBM model with SHAP explanations and missing-evidence guidance.
- [ ] **Defense Drafting:** Cited, structured drafts with unsupported-claim flagging.
- [ ] **Merchant Dashboard:** Dispute list, evidence timeline, draft editor and deadline indicators.
- [ ] **Outcome Feedback Loop:** Store real dispute outcomes and retrain the scoring model.
- [ ] **Additional Dispute Types:** Extend beyond "item not received" to "significantly not as described" cases.

---

## Safety and Compliance

- Human approval is required before any submission to PayPal.
- Drafts cite only retrieved evidence, and claims without a source are flagged.
- PayPal webhook signatures and Shopify HMAC signatures are verified before processing.
- Customer messages, tickets and images are treated as untrusted input to guard against prompt injection.
- Merchant data is isolated through Row Level Security, and PII is redacted from logs.
- Finova does not provide legal advice. The merchant remains responsible for all submissions.

---

## Code Quality and Verification

Before opening a pull request, run the full verification suite:

```bash
# Backend: lint, format, type-check and test
cd apps/api
ruff check . && ruff format . && mypy app && pytest -q

# Frontend: lint, type-check and test
cd apps/web
pnpm lint && pnpm typecheck && pnpm test
```

Architecture rules and coding standards for contributors and AI coding agents are detailed in [AGENTS.md](AGENTS.md).

---

## Team

| Name | Role |
|---|---|
| Kartikay | Integrations |
| Akash | Backend and Data Platform |
| Joy | AI Engineer (LLM and Vision) |
| Umika | ML Engineer |
| Shashwat | Frontend |

Responsibilities and working agreements are documented in [ROLES.md](ROLES.md).

---

## License

This project is licensed under the [MIT License](LICENSE).