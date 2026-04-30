Use @project-governor gpt55-auto-orchestrator.

Automatically choose the Project Governor workflow, models, context budget, subagents, and quality gates for this request.
Do not ask the user to name skills or subagents.
If selected subagents need host-runtime authorization, ask once for explicit consent before spawning.
Do not read all initialization docs. Read `DOCS_MANIFEST.json`, then query the context index and prefer section line ranges before full documents.
Use GPT-5.4-mini for fast read-only scouting and GPT-5.5 for complex implementation/review when available.

Request:
<request>
