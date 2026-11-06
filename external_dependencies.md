# External dependencies

Every outside library and service this week's project uses: what it does, where we use it,
whether it runs on your machine or calls an API, and whether it needs a key or costs money.

Install: `pip install -r fintech-agent-observability-evaluation/requirements.txt`, plus the spaCy model (see Presidio).

## Hosted services (need a key, send data over the internet)

| Service | What it does | Used in | Key | Cost |
| --- | --- | --- | --- | --- |
| **OpenAI chat model** (`gpt-4o-mini`) | The LLM behind the supervisor and the three agents | Every module | `OPENAI_API_KEY` | Paid per token: $0.15 / 1M input, $0.60 / 1M output |
| **OpenAI embeddings** (`text-embedding-3-small`) | Turns policy chunks and questions into vectors for search | Building the agent (RAG), Module D semantic cache | `OPENAI_API_KEY` | Paid per token, very small |
| **OpenAI Moderation API** | Flags harmful text: violence, self-harm, hate, harassment | Module C (input guard) | `OPENAI_API_KEY` | Free for OpenAI API users, rate-limited |
| **OpenAI Batch API** | Runs many requests within 24 hours at half price | Module D (demo) | `OPENAI_API_KEY` | 50% of normal price |
| **LangSmith** | Records every run as a trace; stores datasets and experiments | Module A (tracing), Module B (`evaluate()`) | `LANGCHAIN_API_KEY` | Free plan: 1 seat, 5,000 traces / month |

## Libraries (run on your machine)

| Library | What it does | Used in | Key / cost |
| --- | --- | --- | --- |
| **LangChain** (`langchain`, `langchain-openai`, `langchain-community`) | Prompts, chains (`prompt \| llm \| parser`), the OpenAI wrappers, `get_openai_callback` | Every module | Free. Calls OpenAI, so it uses your OpenAI key |
| **LangGraph** | The agent graph: `StateGraph`, nodes, conditional routing | `project/fintech_support_agent.py` | Free |
| **Chroma** (`chromadb`, `langchain-chroma`) | In-memory vector database for the policy chunks | Building the agent (RAG) | Free, local. Prints harmless "telemetry" warnings |
| **tiktoken** | Counts tokens exactly like the model, before you call it | Module D, lessons 16-17 | Free, local. Downloads the token table once |
| **DeepEval** | Ready-made evaluation metrics (faithfulness, hallucination) and G-Eval (score by criteria in plain English) | Module B (solution) | Free library, but its metrics use an LLM judge, so they call OpenAI |
| **Guardrails AI** (`guardrails-ai`, `guardrails-ai-regex-match`) | Validates LLM output; `RegexMatch` blocks SSN patterns | Module C (output guard) | Free, local. Validators are PyPI packages: no Hub token |
| **Presidio** (`presidio-analyzer`, `presidio-anonymizer`) | Finds personal data (names, emails, phones) and replaces it, e.g. `Alice Johnson` -> `<PERSON>` | Module C (output redaction) | Free, local (Microsoft open source). Nothing leaves your machine |
| **spaCy** + model `en_core_web_lg` | The ML model Presidio uses to recognise names | Module C, through Presidio | Free, local. One-time download, about 400 MB: `python -m spacy download en_core_web_lg` |
| **python-dotenv** | Loads the keys from `.env` into environment variables | Every module | Free |
| **numpy** | Cosine similarity for the semantic cache | Module D | Free |

## Optional (only for Module C exercise TODO 3)

| Library | What it does | Note |
| --- | --- | --- |
| `guardrails-ai-toxic-language` | Blocks toxic answers | Large install: torch + transformers |
| `guardrails-ai-competitor-check` | Blocks competitor names, using spaCy `en_core_web_trf` | Large install: torch. Must run with `use_local=True` |

## Which keys you need

| Key in `.env` | Needed for |
| --- | --- |
| `OPENAI_API_KEY` | Running any demo, exercise or solution (the agent itself) |
| `LANGCHAIN_API_KEY` + `LANGCHAIN_TRACING_V2=true` | Seeing traces (Module A) and running evaluations (Module B) |

The lessons in `fintech_lessons/` need **no key**, except `fintech_03.py`, which sends traces to LangSmith.
Never commit `.env`: it is listed in `.gitignore`.
