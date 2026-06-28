# dataflow.md  

## System Dataflow Architecture for **game‑scaffold**

```
+-------------------+        +-------------------+        +-------------------+
|  External Data    |        |   Ingestion Layer |        |  Processing /    |
|  Sources          |        |   (API / Workers) |        |  Transform Layer |
|-------------------|        |-------------------|        |-------------------|
| • Game asset libs |  --->  | • Auth Gateway    |  --->  | • Asset Cleaner   |
|   (textures,      |        | • Rate Limiter    |        |   (format, size) |
|   models, audio) |        | • Queue (Kafka)  |        | • Prompt Engine   |
| • LLM APIs (OpenAI|        |                   |        |   (prompt gen)    |
|   / Anthropic)   |        |                   |        | • Code Synthesizer|
| • Version control |        |                   |        |   (Unity/C#)      |
|   (GitHub)        |        |                   |        | • Dependency      |
| • Telemetry /     |        |                   |        |   Resolver        |
|   Analytics (GA) |        |                   |        | • Test Harness    |
+-------------------+        +-------------------+        +-------------------+

        |                               |                               |
        v                               v                               v
+-------------------+        +-------------------+        +-------------------+
|   Storage Tier    |<-------|   Query / Serve   |------->|   Egress to User  |
|-------------------|        |   Layer           |        |   (CLI / UI)      |
| • Object Store    |        |-------------------|        |-------------------|
|   (S3/MinIO)      |  <---  | • GraphQL API     |  --->  | • VSCode Plugin   |
| • Metadata DB    |        | • REST Endpoints  |        | • Web Dashboard   |
|   (Postgres)      |        | • AuthZ Middleware|        | • CI/CD Hooks     |
| • Artifact Cache  |        | • Rate Limiter    |        | • Email/Webhooks  |
|   (Redis)         |        +-------------------+        +-------------------+

```

### 1. External Data Sources
| Source | Type | Purpose | Access |
|--------|------|---------|--------|
| Game asset libraries (e.g., Unity Asset Store, OpenGameArt) | Object storage / HTTP | Provide base textures, models, audio for scaffold generation | OAuth2 + API keys |
| Large Language Model APIs (OpenAI, Anthropic, Cohere) | REST | Generate code snippets, design docs, narrative text | API‑key auth, usage throttling |
| Version control (GitHub, GitLab) | Git | Pull existing project skeletons, push generated scaffolds | Personal Access Token (PAT) scoped to repo |
| Telemetry / Analytics (Google Analytics, Mixpanel) | Event stream | Capture usage metrics for validation loop | Service‑account JWT |
| Community prompts / design patterns (public repos) | HTTP/HTTPS | Enrich prompt library for domain‑specific generation | Public read‑only |

### 2. Ingestion Layer
- **Auth Gateway** – API gateway (Kong/Envoy) enforcing OAuth2/JWT per client (dev‑tool, CI, UI).  
- **Rate Limiter** – Token‑bucket per client to protect LLM quota & asset API limits.  
- **Message Queue** – Apache Kafka topics: `asset_requests`, `prompt_jobs`, `generation_tasks`.  
- **Worker Entrypoints** – Python/Go micro‑services (Docker) that pull from Kafka, validate payloads, and forward to processing.

### 3. Processing / Transform Layer
| Component | Function | Tech |
|-----------|----------|------|
| Asset Cleaner | Validate/convert assets to engine‑agnostic formats (FBX → GLTF, PNG → WebP) | Rust + `image` crate |
| Prompt Engine | Assemble context‑aware prompts (asset metadata + design intent) | Python + Jinja2 |
| Code Synthesizer | Call LLM, post‑process into compilable Unity C# scripts | Node.js + OpenAI SDK |
| Dependency Resolver | Map generated code to required Unity packages / NuGet | Go + `go-mod` style resolver |
| Test Harness | Auto‑run unit & integration tests in headless Unity build | Unity Test Runner + Docker |
| Orchestrator | DAG scheduler (Airflow) coordinating the above steps per job | Apache Airflow |

### 4. Storage Tier
- **Object Store (S3/MinIO)** – Raw assets, generated bundles, intermediate files. Bucket policies isolate per‑project namespace.  
- **Metadata DB (PostgreSQL)** – Job descriptors, asset catalogs, prompt versions, audit logs. Row‑level security (RLS) enforces per‑user/project access.  
- **Artifact Cache (Redis)** – Fast lookup of recent generation results, deduplication hashes. TTL = 48 h.  
- **Backup / Archive** – Daily snapshots to cold‑storage (Glacier) for compliance.

### 5. Query / Serving Layer
- **GraphQL API** – Exposes flexible queries: `project(id) { assets, scaffold, status }`. AuthZ middleware checks JWT scopes (`read:project`, `write:scaffold`).  
- **REST Endpoints** – Legacy `/generate`, `/status`, `/download`. Rate‑limited per API key.  
- **AuthZ Middleware** – OPA (Open Policy Agent) policies enforce role‑based access (developer, reviewer, admin).  
- **Caching Layer** – CDN edge cache for static bundles; Redis for API response caching.  
- **Observability** – Prometheus metrics, Grafana dashboards, OpenTelemetry tracing across all services.

### 6. Egress to User
| Channel | Format | Interaction |
|---------|--------|-------------|
| VSCode Extension | JSON over WebSocket | Real‑time scaffold preview, one‑click insert |
| Web Dashboard | React SPA | Project dashboard, asset browser, job logs |
| CLI (`game-scaffold`) | stdout / file system | Scriptable CI pipelines (`game-scaffold generate --ci`) |
| CI/CD Hooks | GitHub Actions, GitLab CI | Auto‑run on PRs, post results as PR comment |
| Email / Webhooks | HTML/JSON | Notification of job completion, error alerts |

### Auth Boundaries
1. **External → Ingestion** – Mutual TLS + OAuth2 JWT; each client must present a scoped token.
2. **Ingestion → Processing** – Internal service‑to‑service mTLS; Kafka ACLs restrict producers/consumers per namespace.
3. **Processing → Storage** – IAM roles (AWS IAM or MinIO policies) scoped to job‑specific prefixes.
4. **Storage → Query** – PostgreSQL RLS + S3 bucket policies; Redis ACLs per service account.
5. **Query → Egress** – API gateway validates JWT; OPA enforces fine‑grained permissions before returning assets or code.
6. **Egress → User** – End‑to‑end TLS; VSCode/Web UI use short‑lived signed URLs for large bundle downloads.

---  

*All components are container‑native and orchestrated via Kubernetes (Helm charts). The architecture isolates untrusted AI‑generated code in sandboxed pods (gVisor) before exposing to the user, preserving the integrity of the final product.*