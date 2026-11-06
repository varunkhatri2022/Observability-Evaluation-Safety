# LangSmith, and what else is out there

## Logging vs monitoring vs observability

| | Logging | Monitoring | Observability |
| --- | --- | --- | --- |
| Answers | "Did error X happen?" | "Is the system healthy?" | "WHY did THIS request fail?" |
| Looks at | Individual events | Many requests over time | One request, step by step |
| Looks like | Flat list of lines (`print`, `logger.info`) | Dashboards and alerts (avg latency, error rate, p99) | A tree of runs: parent and child steps, each with input, output, tokens, latency |
| In our lessons | fintech_01: only the final answer | LangSmith Monitoring tab | fintech_03: one trace per run, open `policy_agent` to see the bug |

Monitoring tells you *that* something is wrong. Observability tells you *why*.
Every trace is also the input for the rest of the week: evaluation (Module B), guardrails (Module C), cost (Module D).

## What LangSmith gives you

| | |
| --- | --- |
| Records | Every request from every user, automatically, as a tree of steps |
| Shows per step | Input, output, the prompt sent to the LLM, the LLM reply, tokens, cost, latency, errors |
| Keeps | Traces stored and searchable, filtered by tag or metadata |
| Evaluates | Datasets of expected answers, experiments compared side by side (Module B) |
| Needs | No code changes for LangChain/LangGraph: 3 environment variables (slide 18) |

## Alternatives

| Tool | Open-source platform? | Choose it when |
| --- | --- | --- |
| **LangSmith** | No | You use LangChain/LangGraph and a hosted tool is fine |
| **Langfuse** | Yes (MIT) | You need open source or data on your own servers |
| **Arize Phoenix** | Source-available (Elastic License 2.0) | Your company is standardised on OpenTelemetry |
| **Helicone** | Yes (Apache 2.0) | You want logging by changing only the API base URL |
| **Microsoft Foundry + Application Insights** | No (Azure services) | You build with Microsoft Agent Framework (MAF) on Azure |

## The Microsoft equivalent, with Microsoft Agent Framework (MAF)

MAF emits standard OpenTelemetry traces. On Azure they go to **Application Insights** and show up in the **Microsoft Foundry** portal.

| LangSmith (this week) | Microsoft / MAF |
| --- | --- |
| Tracing: 3 environment variables | MAF's OpenTelemetry instrumentation, exported to Azure Monitor Application Insights |
| Trace viewer | Foundry portal trace view, or Application Insights |
| Tags, metadata, Monitoring tab | Span attributes, Azure Monitor dashboards and KQL queries |
| Datasets, evaluators, experiments (Module B) | Foundry evaluations: built-in evaluators such as Groundedness, Intent Resolution, Task Adherence, Tool Call Accuracy |
| Guardrails (Module C) | Azure AI Content Safety, including Prompt Shields for prompt injection |

Microsoft renames these services often, and some agent evaluators are in preview: check the current Microsoft Learn docs before you rely on a name.

The ideas (trace, run, dataset, experiment) are the same in all of them.
