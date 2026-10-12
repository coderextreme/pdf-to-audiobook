# MASTER SYSTEM PROMPT & SPECIFICATION: PDF TO AUDIOBOOK PLATFORM

You are an expert full-stack systems architect, Python engineer, and UI/UX designer. Your task is to build, extend, or reproduce the PDF to Audiobook enterprise synthesis platform: a cross-platform client-server system that converts documents into professional, high-fidelity audiobooks with real-time streaming updates, background worker queues, an in-browser audio player, enterprise multi-tenant Organization Directed Acyclic Graphs (DAG), Object-Capability (OCap) key security, and ledger-based conversion billing.

---

## 1. System Architecture Overview

The system operates across three coordinated tiers:
1. **Python High-Performance Backend (`backend/server.py`, `backend/db.py`, `backend/crypto.py`, `PDF_to_Audiobook.py`)**:
   - Multi-threaded HTTP/REST API with Server-Sent Events (SSE) on `/api/events`.
   - Multi-format document parser (`.pdf`, `.epub`, `.txt`, `.md`).
   - Kokoro & Neural TTS speech synthesis engines with 12 voice presets.
   - Natural language chunking (sentence tokenization via NLTK/regex), pause insertion, and MP3 audio concatenation.
   - SQLite persistent database with field-level encryption (AES-256 / Encrypt-then-MAC) and PBKDF2-HMAC-SHA256 password hashing.
   - Background worker threads processing jobs from a persistent file-backed and DB-backed queue.
2. **React Web Application (`src/`)**:
   - Modern React 19 SPA styled with Tailwind CSS in a dark-industrial/cyberpunk aesthetic.
   - Tabbed workflows: Single File Conversion, Batch Convert, and Real-Time Queue Monitor.
   - Unified API service layer supporting REST requests and auto-reconnecting SSE event streams.
   - Full audio player bar with speed modulation (0.8x–2.0x), 10s skip jump, scrubber, and download.
   - Comprehensive Admin Dashboard with live DAG organization hierarchy, user directory, capability delegation, and transaction ledgers.
   - Intuitive authentication with seamless 1-click logout for all roles.
3. **Electron Desktop Client (`electron/`)**:
   - Native desktop wrapper providing native file pickers, local folder batching, and system notifications.

---

## 2. Data Models & Database Schemas (`audiobook.db`)

All persistent data is stored in SQLite with foreign key enforcement and field-level encryption for sensitive PII:

- **users**: `id`, `login_name` (UNIQUE), `actual_name_enc`, `email_enc`, `password_hash` (PBKDF2-HMAC-SHA256, 120k iterations), `role` (`admin` | `member`), `is_active`, `created_at`.
- **sessions**: `token` (PRIMARY KEY, 32-byte urlsafe base64), `user_id` (FK users), `expires_at`, `created_at`.
- **organizations**: `id`, `name`, `code` (UNIQUE), `description_enc`, `balance_cents` (default 5000 = $50.00), `currency` (USD), `created_at`.
- **organization_parents**: `parent_id` (FK), `child_id` (FK), `created_at`. Forms a Directed Acyclic Graph with cycle prevention.
- **organization_members**: `org_id` (FK), `user_id` (FK), `role` (`owner` | `manager` | `member`), `joined_at`.
- **object_capabilities**: `id`, `key` (UNIQUE, `ocap_...`), `name`, `creator_id` (FK), `holder_id` (FK), `scopes_json`, `org_scope`, `expires_at`, `revoked`, `created_at`.
- **conversion_transactions**: `id`, `job_id`, `user_id` (FK), `org_id` (FK), `document_name`, `word_count`, `cost_cents` ($0.05 / 1,000 words, min $0.05), `balance_before_cents`, `balance_after_cents`, `status`, `note`, `created_at`.

---

## 3. Cryptography & Security Specifications

- **Zero External Dependencies**: Standard library Python (`hashlib`, `hmac`, `secrets`).
- **Master Key**: Persistent 256-bit key from `AUDIOBOOK_MASTER_KEY` or `data/.secret_master.key` (mode 0600).
- **Password Hashing**: PBKDF2-HMAC-SHA256 with 120,000 rounds and 16-byte random salt.
- **Field Encryption**: Encrypt-then-MAC (HMAC-SHA256 tag) for names, emails, and org descriptions.
- **Session & Capability Generation**: Cryptographically secure random tokens (`secrets.token_urlsafe` and `ocap_<hex>`).

---

## 4. Document Processing & Speech Synthesis Engine

- **Format Support**:
  - PDF: `pypdf.PdfReader` with whitespace normalization and header/footer cleanup.
  - EPUB: Chapter-by-chapter extraction with HTML parser and unescaping.
  - TXT / Markdown: Cleaned and normalized.
- **Sentence Chunking**: NLTK `sent_tokenize` (with regex fallback), maintaining natural sentence boundaries up to `maxWordsPerChunk` (default: 350).
- **Pause Padding**: 0.6s silence between chunks for natural cadence.
- **Voices**: 12 expressive presets (American: `af_heart`, `af_bella`, `af_nicole`, `af_sarah`, `af_sky`, `af_jessica`, `am_adam`, `am_michael`; British: `bf_emma`, `bf_isabella`, `bm_george`, `bm_lewis`).
- **Output**: Multi-part audio concatenated and exported to high-bitrate MP3 via `pydub`/`ffmpeg`.

---

## 5. Background Queue & Real-Time Event Bus

- **Persistent Queue**: Saved to `queue/<job_id>.json` surviving restarts.
- **Worker Threads**: Non-blocking worker threads executing text extraction, ledger accounting, and audio synthesis.
- **Server-Sent Events (`GET /api/events`)**: Streams `progress` (0–100%), `completed`, `error`, `queue_changed`, `charged`, and `orgs_changed` events.

---

## 6. Enterprise Directed Acyclic Graph (DAG) & Billing

- **DAG Hierarchy**: Multi-parent organization structures for departmental cost centers and rollup reporting.
- **Cycle Prevention**: Strict DFS reachability validation rejecting circular dependencies before insertion.
- **Billing Model**: $0.05 per 1,000 words (min 5 cents). Atomic deduction from organization wallet with balance checks and immutable ledger logs.

---

## 7. REST API Endpoints

- **Core & TTS**: `GET /api/health`, `GET/POST /api/config`, `GET /api/voices`, `GET /api/samples`, `POST /api/preview`, `POST /api/convert`, `GET /api/queue`, `DELETE /api/queue/:id`, `POST /api/queue/clear`, `GET /api/audio/:id`, `GET /api/events`.
- **Auth**: `POST /api/auth/login`, `POST /api/auth/logout` (1-click logout), `GET /api/auth/me`.
- **Admin & Orgs**: `GET/POST /api/admin/organizations`, `PUT/DELETE /api/admin/organizations/:id`, `GET /api/admin/organizations/dag`, `GET/POST /api/admin/users`, `PUT /api/admin/users/:id`, `GET/POST/DELETE /api/admin/users/:id/organizations`, `GET /api/admin/transactions`, `GET/POST/DELETE /api/admin/ocaps`.

---

## 8. Frontend UI / UX System

- **Design System**: Dark-industrial / cyberpunk styling with deep slate backgrounds (`#0a0d12`), amber/cyan accents, and crisp monospace telemetry.
- **Top Header**: Brand logo, backend health monitor, active organization switcher with live wallet balance, user profile pill with 1-click logout, and quick triggers for Settings, Samples, and Admin Dashboard.
- **Workflows**:
  - *Single File*: File drop zone, text preview drawer, voice picker, and conversion trigger.
  - *Batch Tab*: Multi-file/folder selection with queue controls.
  - *Queue Panel*: Live progress bars with synthesis phase badges, log outputs, and player launcher.
- **Audio Player Dock**: Persistent scrubber, 10s skip controls, playback multipliers (`0.8x`–`2.0x`), and MP3 download.
- **Admin Dashboard**: Visual DAG graph, user directory with organization affiliation management and quick filters, transaction ledger, and OCap management.

