Use @project-governor context-indexer.

Build or query `.project-governor/context/CONTEXT_INDEX.json`, `DOCS_MANIFEST.json`, and `SESSION_BRIEF.md`.
Return relevant sections, line ranges, and a small file list for this request instead of reading all initialization docs.
Exclude stale or superseded docs unless the request explicitly needs history or cleanup.

Request:
<request>
