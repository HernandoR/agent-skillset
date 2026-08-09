---
name: codegraph-usage
description: Use when exploring code, finding symbols, tracing call paths, understanding architecture, analyzing impact of changes, or building code context for a task. This is a code intelligence skill over an indexed knowledge graph — consult it BEFORE writing or editing code when you need to understand code structure, symbol relationships, or call flows. Also activates when the user asks how code works, where things are defined, what calls/references a symbol, what would break from a change, or how data flows through the system.
---

# CodeGraph Usage

CodeGraph is a SQLite knowledge graph of every symbol, edge, and file in the workspace. Reads are sub-millisecond; the index lags writes by about a second through the file watcher. Use it to answer code questions without grep/read loops.

## Tool Selection by Intent

| Intent | Tool |
|--------|------|
| "What is the symbol named X?" | `codegraph_search` |
| "What's the deal with this task / feature / area?" | `codegraph_context` — composes search + node + callers + callees in one call |
| "How does X reach Y? / trace the flow / the path from X to Y" | `codegraph_trace` — ONE call returns the whole call path, including dynamic-dispatch hops (callbacks, React re-render, JSX children) that grep cannot follow |
| "What calls this?" | `codegraph_callers` |
| "What does this call?" | `codegraph_callees` |
| "What would changing this break?" | `codegraph_impact` |
| "Show me this symbol's source / signature / docstring." | `codegraph_node` |
| "Show me several related symbols' source / survey an area." | `codegraph_explore` — ONE capped call; prefer over many `codegraph_node`/`Read` |
| "What's in directory X?" | `codegraph_files` |
| "Is the index ready / what's its size?" | `codegraph_status` |

## Common Workflows

### Explore a new feature area
1. `codegraph_context` with the task description — gets you the key symbols and their relationships
2. `codegraph_explore` on the key symbols from step 1 — shows you the actual source code
3. `codegraph_trace` if you need to understand the flow from entry point to outcome

### Before editing code
1. `codegraph_impact` on the symbol you're changing — reveals all dependents
2. `codegraph_callers` on the symbol — shows who calls it
3. If impact is large, `codegraph_explore` to read the relevant dependent code

### Trace data flow
1. `codegraph_trace` from the entry point (e.g., handler, event listener) to the destination
2. If intermediate hops are unclear, `codegraph_node` on the middle symbol
3. `codegraph_explore` with symbols from the path to see full implementations

### Find where a symbol is used
1. `codegraph_search` to locate the symbol by name (optionally filter by kind)
2. `codegraph_callers` to see everything that references it
3. `codegraph_impact` to understand the blast radius of changing it

## Best Practices

- **Answer directly — don't delegate exploration.** Use 2-3 codegraph calls directly. Do not spawn a separate sub-agent or run grep+read loops for things codegraph already indexes. Codegraph IS the pre-built search index.
- **Always trust the index.** Codegraph reads are millisecond-accurate and the file watcher keeps within ~1 second of edits. Do not re-verify codegraph results with Read/Grep unless you need to confirm a specific detail codegraph did not cover.
- **Prefer compound tools.** `codegraph_context` and `codegraph_explore` are more powerful than their individual parts. Reach for these first before composing many tool calls.
- **Check staleness after edits.** After making code changes, run `codegraph_status` to see if the index is still fresh. If it looks stale, the index will update via the file watcher within ~1 second, so wait briefly then retry.
- **Respect index boundaries.** Codegraph only knows about indexed files. If a file is new and not yet indexed, fall back to `Read`/`Grep`.
- **Missing `.codegraph/` directory?** Offer to run `codegraph init -i` to initialize and index the project.

## Input Reference

### codegraph_search
- `query` (required): Symbol name or pattern
- `kinds` (optional): Filter by node kind, e.g. `["function", "class"]`
- `limit` (optional, default 20, max 100)

### codegraph_context
- `task` (required): Task description (max 10,000 chars). Be specific about what you want to understand.
- `maxNodes` (optional, default 50): Maximum nodes to include
- `format` (optional, default "markdown"): "markdown" or "json"

### codegraph_trace
- `from` (required): Starting symbol name or qualified name
- `to` (required): Target symbol name or qualified name
- `maxDepth` (optional, default 5): Maximum path depth

### codegraph_callers / codegraph_callees
- `symbol` (required): Symbol name or qualified name
- `limit` (optional, default 20)

### codegraph_impact
- `symbol` (required): Symbol name or qualified name
- `maxDepth` (optional): How deep to traverse impact chain

### codegraph_node
- `symbol` (required): Symbol name or qualified name
- `includeCode` (optional, default false): Whether to include source code

### codegraph_explore
- `symbols` (required): Array of symbol names to explore together
- `maxFiles` (optional): Maximum files to include
- `maxCharsPerFile` (optional): Maximum chars per file

### codegraph_files
- `maxDepth` (optional): Directory tree depth
- `filter` (optional): Path filter, e.g. "src/**"
- `format` (optional): "tree" or "json"

### codegraph_status
- No parameters required

## Common Pitfalls

- **Using grep/Read to find what codegraph already knows.** If codegraph is installed and indexed, reach for it first. A grep+read exploration can cost dozens of tool calls; codegraph answers in 2-3.
- **Spawning sub-agents for code exploration.** Codegraph calls are fast (sub-millisecond reads). Delegating exploration to a sub-agent duplicates work and wastes context.
- **Calling many `codegraph_node`/`Read` instead of one `codegraph_explore`.** When you have a set of related symbols, `codegraph_explore` returns them all grouped by file in one call.
- **Forgetting `codegraph_impact` before editing.** Check the blast radius before changing a symbol to avoid breaking dependents.
- **Re-verifying codegraph output with Read/Grep.** The index is millisecond-accurate and within ~1 second of file-system changes. Trust it.
