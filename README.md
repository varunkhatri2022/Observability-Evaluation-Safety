# Agent Observability, Evaluation & Safety

This repository contains the Week 8 learning materials and **SecureBank**, a
multi-agent FinTech support assistant built with Python and LangGraph. The
agent itself is small. This week is about hardening it for production:
tracing it, measuring its quality, guarding its inputs and outputs, and
tracking what it costs.

## What is here

| Folder or file | Contents |
| --- | --- |
| `setup/` | Step-by-step guide for creating a LangSmith API key. Do this before class. |
| `fintech-agent-observability-evaluation/` | The SecureBank agent (`project/`) and four modules: A observability, B evaluation, C guardrails, D cost. |
| [Live class slides](Live%20Class%20Slides%20-%20Week%208%20_%20Agent%20Observability%2C%20Evaluation%20%26%20Safety.pdf) | The accompanying Week 8 class slides. |

The agent's basic flow is:

```text
customer question
       |
 classify_intent          (supervisor: one LLM call)
   /     |      \
policy  account  escalation
 (RAG)  (mock DB) (empathy)
   \     |      /
      response
```

Each module wraps this same agent with one new layer:

| Module | Question it answers | Tools |
| --- | --- | --- |
| A Observability | Which step failed? | LangSmith traces, tags |
| B Evaluation | Did my change make it better or worse? | LangSmith datasets and experiments, MRR, DeepEval, G-Eval |
| C Guardrails | Can a user make it leak data or say something unsafe? | Regex, OpenAI Moderation, Presidio, Guardrails AI |
| D Cost | What does each query cost, and how do we lower it? | tiktoken, `get_openai_callback`, caching |

## Run the SecureBank agent

The modules make real OpenAI API calls and send traces to LangSmith. These
calls may incur charges. Follow the guides in `setup/` first, then:

```powershell
cd .\fintech-agent-observability-evaluation
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt --only-binary litellm,tokenizers
Copy-Item .env.example .env
```

`--only-binary` makes pip use ready-built packages. Without it, pip may pick a
version of `litellm` (needed by Guardrails AI) that has to be compiled with
Rust, and the install fails. This was tested on Python 3.11 on Windows; the
project's own README asks for 3.12, but 3.11 works.

Open `fintech-agent-observability-evaluation/.env` in your editor and add your
own `OPENAI_API_KEY` and `LANGCHAIN_API_KEY`. Do not put keys in source files
or commit `.env`. The repository ignores `.env` and virtual environments;
`.env.example` contains only placeholders.

Run the first module from the `fintech-agent-observability-evaluation` folder:

```powershell
python module_a_observability/demo.py
```

If it prints answers and the runs appear in your LangSmith project, your setup
is working. See `fintech-agent-observability-evaluation/README.md` for all four
modules and for troubleshooting.

## Project notes

- The vector store (Chroma) is rebuilt in memory each time a script starts,
  so every run embeds the four policy documents again.
- The accounts in `project/fintech_support_agent.py` and the policy documents
  in `project/documents/` are demonstration data, not real bank data.
- Module C needs one extra download: the spaCy `en_core_web_lg` model (about
  560 MB) for Presidio: `python -m spacy download en_core_web_lg`.
  Guardrails validators are now plain PyPI packages (`guardrails-ai-regex-match`
  is in `requirements.txt`); no Guardrails Hub token is needed any more.
