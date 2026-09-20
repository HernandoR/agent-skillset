# ADR-0015: Skill Bodies Use Strict STE

- Status: Accepted
- Date: 2026-09-20

## Context

ADR-0013 made Simplified Technical English the register of the English-only
rule, and it routes each artifact class to one of two modes. **Strict** covers
text that a machine or an agent parses with no human present. **STE-flavored**
applies the structural rules to prose that a human reads, and leaves word choice
advisory.

The routing table classifies error and log strings, CLI help, tool and function
descriptions, inter-agent instructions, and agent spec rules as Strict. It
classifies docs, RFCs, ADRs, READMEs, code comments, docstrings, and PR and
commit bodies as STE-flavored. It classifies no `SKILL.md` body, and a skill
body matches neither list well. It is not an error string, and a human does not
read it for its own sake.

The question surfaced during review of ADR-0014. The new `shrink-tests` skill
was the first skill written after ADR-0013 landed, and its reviewer asked which
mode binds a skill body. ADR-0014 recorded an interim position and left the
routing open.

## Decision

- **A `SKILL.md` body is Strict.** A skill loads into an agent's context and
  directs that agent with no human present to resolve an ambiguity. That is the
  same condition the table already names for a tool description, so the same
  mode applies.
- **Strict also covers the skill's metadata**: the frontmatter `description`,
  the `agents/openai.yaml` interface text, and a subagent definition under
  `plugins/<bundle>/agents/<name>.md`. A harness reads each of these to decide
  when to load the skill, and a misparse there costs more than a misparse in the
  body, because the skill never loads at all.
- **The rule binds a skill body at creation, and at the next change in
  substance.** It does not require a rewrite of every skill that predates it.
  ADR-0013 set the same boundary for the artifacts it reclassified.
- **The two ADR-0013 limits carry over unchanged.** A rewrite never drops a
  hedge, a scope qualifier, or a safety condition to shorten a sentence. STE
  never applies to localized product copy or to a verbatim quote.
- **Record the routing in all four places the rule lives**: the
  `english-only-artifacts` skill table, `.agents/spec/english-only-artifacts.md`
  (version 2 → 3), the skill's bundled copy under `references/agents-spec/`, and
  the `AGENTS.md` mirror.
- **Versions.** `discuss` goes 0.6.0 → 0.7.0 (minor: a behavioural change to an
  existing skill). The marketplace and `package.json` are already at 0.14.0 on
  this branch, which is the minor bump this change also needs.

## Consequences

- `plugins/dev-loop/skills/shrink-tests/SKILL.md` is rewritten to Strict as the
  first application of the rule: one idea per sentence, active voice, no
  metaphor without a plain reading, and one name for one thing. The skill now
  defines **mirror** once and uses that term throughout, in place of the mixed
  "copy", "scaffolding", and "one-to-one" wording it carried before.
- The known cost is tone. A Common Rationalizations table works by stating a
  rebuttal with enough force to override an agent's own reasoning, and a strict
  lexical pass flattens some of that force. The table survives the rewrite with
  its claims intact, but it reads plainer. This cost is accepted, because an
  agent that misparses a rule is worse than an agent that reads a plain one.
- Six existing skills in `dev-loop`, and the other bundles' skills, are not
  rewritten. They are STE-flavored until they next change in substance, so the
  repository holds two registers for a period.
- Writing a new skill now costs an extra pass. `plugins/discuss/skills/asd-ste100`
  is the procedure for that pass.
