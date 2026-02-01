# Content Generation Guide — Using OpenClaw + Codex for Bulk Content

How to use OpenClaw's sub-agent system to generate large volumes of structured educational content.

## Overview

This guide covers generating structured JSON content (deep dive articles, curriculum, reference materials) at scale using OpenClaw's sub-agent spawning with Codex (GPT-5.2).

## Architecture

```
Main Agent (Opus) — orchestrates, validates, merges
├── Sub-Agent 1 (Codex) — Category A: 5 articles
├── Sub-Agent 2 (Codex) — Category B: 5 articles
├── Sub-Agent 3 (Codex) — Category C: 5 articles
└── Sub-Agent 4 (Codex) — Fact-check / QA
```

## Key Principles

### 1. Define Your Schema First
Before generating, lock down the JSON schema. Every sub-agent needs the same contract.

```json
{
  "id": "dd-category-topic-01",
  "title": "Article Title",
  "subtitle": "One-sentence hook",
  "readTime": 35,
  "sections": [
    {"heading": "Section Title", "content": "2000-4000 chars..."}
  ],
  "sources": [
    {"name": "Source Name", "author": "Author", "year": 2023, "type": "paper"}
  ],
  "keyTakeaways": ["Takeaway 1", "Takeaway 2"]
}
```

### 2. Parallel Sub-Agent Dispatch
Spawn one sub-agent per content category. Each generates 5 articles independently:

```
sessions_spawn({
  task: "Generate 5 articles about [CATEGORY]...",
  label: "category-batch",
  model: "Codex"
})
```

### 3. Validate Before Merging
After sub-agents complete, validate:
- JSON parses correctly
- Required fields present
- Section count (12-16 per article)
- Section character count (2000-4000 each)
- No duplicate IDs
- Sources are real, traceable works

### 4. Fact-Check Critical Content
Spawn a separate fact-check sub-agent for high-stakes content:
- Quote verification
- Source existence
- Technical accuracy
- Terminology correctness

## Content Quality Checklist

- [ ] 12-16 sections per article
- [ ] 2000-4000 characters per section
- [ ] 10-15 real academic sources with author/year
- [ ] 6-10 key takeaways
- [ ] Image descriptions with position and type
- [ ] No markdown within section content (use \n\n for paragraphs)
- [ ] readTime calculated at ~250 words per minute

## Token Economics

Each 5-article batch costs roughly:
- ~5K input tokens (prompt + schema)
- ~20-25K output tokens (5 articles)
- Total: ~$0.30-0.35 per batch at Codex pricing

For 20 articles across 4 categories: ~$1.20-1.40 total.

## Common Pitfalls

1. **Output truncation**: Very long articles may be cut off. Use `--max-tokens` or split into smaller batches.
2. **Schema drift**: Sub-agents may deviate from schema. Include a sample article in the prompt.
3. **Hallucinated sources**: Always verify academic citations exist. Spawn a fact-check agent.
4. **Inconsistent formatting**: Some agents use string arrays for sections instead of {heading, content} objects. Normalize in the merge step.

## Example Workflow

```bash
# 1. Spawn content agents (parallel)
# In OpenClaw:
sessions_spawn("Generate 5 Health articles...", label="health-batch")
sessions_spawn("Generate 5 Finance articles...", label="finance-batch")

# 2. Wait for completion (check sessions_list)

# 3. Extract from session transcripts
python3 extract_articles.py --session-id <id> --output articles.json

# 4. Validate
python3 validate_schema.py --input articles.json

# 5. Merge into existing data
python3 merge_articles.py --existing deepdives.json --new articles.json

# 6. Commit
git add -A && git commit -m "content: add 10 new deep dives"
```

## Tips

- **Bundle related work**: One sub-agent per 5 articles is efficient. Fewer spawns = less overhead.
- **Provide existing article IDs**: Tell agents what already exists to avoid duplicates.
- **Use outlines for complex topics**: Generate outlines first, then expand in a second pass.
- **Multi-pass for philosophy/dense content**: Some topics need section-by-section expansion.
