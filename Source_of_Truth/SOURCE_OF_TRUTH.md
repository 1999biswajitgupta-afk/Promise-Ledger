# Promise Ledger — Source of Truth

> The one file we follow. Every session starts by reading this, and ends by updating it.
> If it's not written here, it didn't happen.

---

## 1. What we're building (one line)

An AI system that extracts the promises company managements make on earnings calls, remembers them across quarters, checks them against actual results, and scores how credible each management is.

## 2. The business problem

- Every quarter, managements of listed Indian companies promise things on earnings calls: margin targets, capex, plant timelines, growth.
- Investors price stocks partly on these promises.
- **Nobody checks them systematically.** Promises sit in 25-page transcript PDFs; results arrive months later in separate filings. Analysts check by hand in Excel; retail investors don't check at all.
- So managements can over-promise, miss, move the goalpost or quietly drop a target with little consequence.

**We solve it by:** Extract → Remember → Verify → Score → Answer.

**Pitch:** "Managements make promises every quarter and nobody checks them. I built an AI system that tracks every promise and verifies it against actual results, so investors know whose word to trust."

## 3. How we work (rules)

1. **One step at a time.** Do the step, see it work, then move on.
2. **Understand before you copy.** For every piece of code: what does it do, why this way, what breaks if we remove it.
3. **You type the core logic yourself** (RAG, extraction, agents). AI help is fine for boilerplate.
4. **Measure everything.** Every change to retrieval or agents gets an eval number before and after.
5. **Commit to git at the end of every step.** Small commits, clear messages.
6. **End of each day:** update Section 8 (progress log) and Section 9 (what I can now explain).
7. **Stuck for more than 30 minutes?** Write down what you tried, then ask.

## 4. Tech stack (decided)

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.12 | Industry default for AI |
| Package manager | uv | Fast, modern, you've used it |
| Editor | VS Code | |
| Version control | git + GitHub | Portfolio lives here |
| Database | PostgreSQL + pgvector (in Docker) | One DB for text, vectors and numbers |
| PDF parsing | pdfplumber | Clean text from BSE transcripts |
| Data source libs | BseIndiaApi, NseIndiaApi | Maintained; avoid nsepy/nsetools/bsedata |
| LLM | TBD on Day 4 (OpenAI-compatible API) | |
| Agents | LangGraph | |
| API | FastAPI | |
| UI | Streamlit | Fast to build |
| Tracing | Langfuse | |
| Protocol | MCP | Fills a resume gap |

## 5. Scope (15-day version)

- ~20 companies × 4 quarters ≈ 80 transcripts
- 50 hand-labelled promises as the gold eval set
- Streamlit UI, runs locally with Docker Compose
- **Cut order if behind:** multimodal → MCP. **Never cut evals.**

## 6. Data sources

| What | Where | How |
|---|---|---|
| Transcripts (the promises) | BSE announcements, subcategory "Earnings Call Transcript" | BseIndiaApi; fetch **one day at a time** (multi-day ranges return nothing) |
| Actual results (the proof) | NSE financial results, XBRL files | NseIndiaApi + XBRL parser |
| Charts (multimodal) | BSE/NSE "Investor Presentation" filings | Vision model |
| Fallback | Company investor-relations pages | Manual download |

Known quirk: BSE has no ticker → scrip-code table; resolve codes through BSE's search.

## 7. The plan

Each day lists what you **build**, what you **learn**, and what you must be able to **explain** before ticking it off.

### Day 0 — Setup
- [ ] Install VS Code, Python (via uv), git, Docker Desktop
- [ ] Create GitHub account/repo `promise-ledger`
- [ ] Create project folder, open in VS Code, first commit
- **Learn:** terminal basics, virtual environments, what git does
- **Explain:** why a virtual environment? what is a commit?

### Day 1–2 — Data ingestion
- [ ] Pick 20 companies, resolve BSE scrip codes
- [ ] Download transcripts, extract text with pdfplumber
- [ ] Start Postgres in Docker, create `transcripts` table, load text
- **Learn:** APIs/HTTP, JSON, PDFs, SQL basics, Docker
- **Explain:** how data flows from BSE to your database

### Day 3 — Gold eval set
- [ ] Read 10 transcripts, hand-label 50 promises (metric, target, deadline, quote, page)
- [ ] Record the actual outcomes
- **Learn:** why evals come before models
- **Explain:** what is ground truth and why it matters

### Day 4–5 — Naive RAG from scratch
- [ ] Chunking, embeddings, pgvector search, prompt, answer
- [ ] Eval on gold set → baseline numbers
- **Learn:** embeddings, cosine similarity, chunk size trade-offs, context windows
- **Explain:** RAG end to end, with no framework

### Day 6–7 — Advanced RAG + extraction
- [ ] Hybrid search (BM25 + vector), reranker, metadata filters
- [ ] LLM extraction of promises into structured records (Pydantic)
- [ ] Re-run evals, record improvement
- **Learn:** hybrid search, reranking, structured outputs
- **Explain:** why plain RAG failed and what each fix improved (with numbers)

### Day 8–9 — Memory + first agent
- [ ] `promises` ledger table (long-term memory)
- [ ] `actuals` table from XBRL
- [ ] One LangGraph verifier agent with tools (SQL, calculator, transcript search)
- **Learn:** tool calling, agent loops, short-term vs long-term memory
- **Explain:** agent vs pipeline; when not to use an agent

### Day 10–11 — Multi-agent
- [ ] Extractor, memory manager, verifier, critic, supervisor
- [ ] Critic rejects unsupported verdicts
- **Learn:** orchestration, state, handoffs, failure modes
- **Explain:** why multi-agent here and not one big prompt

### Day 12 — Multimodal
- [ ] Read charts from investor presentations with a vision model
- **Learn:** vision-language models, image inputs
- **Explain:** when text extraction isn't enough

### Day 13 — MCP + UI
- [ ] MCP server exposing ledger tools
- [ ] Streamlit: company page, Ask, leaderboard
- **Learn:** MCP protocol, simple frontends
- **Explain:** what MCP is and why it matters

### Day 14 — Production polish
- [ ] Langfuse tracing, cost per query, latency
- [ ] Prompt-injection test, evals in a script/CI
- **Learn:** observability, LLM security basics
- **Explain:** how you'd monitor this in production

### Day 15 — Ship
- [ ] README with architecture diagram + eval table
- [ ] 2-minute demo video
- [ ] LinkedIn post

### After — Interview prep
- [ ] Project walkthrough (2-min and 10-min versions)
- [ ] Deep-dive questions per component
- [ ] System design: "scale this to all 5,000 listed companies"

## 8. Progress log

| Date | Day | Done | Problems / notes |
|---|---|---|---|
| 2026-09-24 | Planning | Project chosen, plan + UI mockup made | — |

## 9. What I can now explain (my learning log)

_Write in your own words after each day. This becomes interview prep._

-

## 10. Decisions log

| Date | Decision | Why |
|---|---|---|
| 2026-09-24 | Project = Management Promise Tracker | Unique angle, verifiable, forces each stage of the evolution |
| 2026-09-24 | Postgres + pgvector | One DB for vectors and numbers; already on resume |

## 11. Eval scoreboard

| Stage | Extraction recall | Verdict accuracy | Retrieval recall@5 | Cost/query | Latency |
|---|---|---|---|---|---|
| Naive RAG | | | | | |
| Advanced RAG | | | | | |
| Agent | | | | | |
| Multi-agent | | | | | |

## 12. Links

- UI mockup: https://claude.ai/artifact/HmiKy9FNdWeHj4iP6ohLVY
- GitHub repo: _(add on Day 0)_
