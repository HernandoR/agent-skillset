# ADR-0013: STE Register for English Artifacts

- Status: Accepted
- Date: 2026-09-10

## Context

ADR-0008 fixed the *language* of every durable artifact in this repo and in the
projects that install the `english-only-artifacts` skill. It says nothing about
form. English alone still permits dense, hedge-stacked prose that the next
reader — a future contributor, a fresh agent session, a translation pipeline —
must decode before acting on it.

The `asd-ste100` skill applies the aerospace controlled-language standard
ASD-STE100 to that problem: active voice, one instruction per sentence, short
sentences, no phrasal verbs, no nominalization, one name per thing. It was
maintained in the maintainer's user-level `~/.claude/skills/`, so it reached one
machine and no installer of this marketplace.

The skill already separates two modes. **Strict** covers text a machine or an
agent parses with no human present. **STE-flavored** applies the structural
rules to prose while leaving word choice advisory, because a strict rewrite of a
README reads as a personality transplant.

## Decision

- **Vendor `asd-ste100` into the `discuss` bundle**, verbatim from
  [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) at
  commit `d5ce157870cf9c41efd1d6e836706a2be3c7b9da` (MIT). The upstream
  `LICENSE` sits in the skill directory, and the upstream `examples/` directory
  stays alongside the standard skill layout. Only `agents/openai.yaml` is added,
  because `just validate` requires it.
- **`discuss`, not a new bundle.** The skill governs the form of written
  artifacts, which is the bundle that already owns RFCs, ADRs, project rules,
  and the English-only rule. A one-skill bundle would split that surface.
- **Make STE the register of the English-only rule, not a parallel option.**
  `english-only-artifacts` gains a "Which English" section that routes each
  artifact class to a mode: Strict for error and log strings, CLI help, tool
  descriptions, inter-agent instructions, and agent spec rules; STE-flavored for
  docs, RFCs, ADRs, READMEs, code comments, docstrings, and PR and commit
  bodies.
- **Bind it on the project too.** `.agents/spec/english-only-artifacts.md` goes
  to version 2 with the register paragraph and a BAD/GOOD example pair, mirrored
  in `AGENTS.md`. The skill's bundled copy under
  `references/agents-spec/` stays byte-identical apart from its drop-in comment.
- **Two limits are restated wherever the rule appears.** A rewrite never drops a
  hedge, a scope qualifier, or a safety condition to shorten a sentence, and STE
  never applies to localized product copy or to a verbatim quote — both are
  already outside the English-only rule's scope.
- **Versions.** `discuss` goes 0.5.0 → 0.6.0 (minor: new skill plus a
  behavioural change to an existing one). The marketplace and `package.json` go
  0.12.0 → 0.13.0.

## Consequences

- Every artifact this repo produces now has a checkable form, not only a
  checkable language. The failure mode it removes — English prose that a
  downstream agent misparses — was previously invisible to review.
- The rule reaches installers of `discuss` and, through the spec file, any
  project that adopts `.agents/spec/`. It reaches nothing that installs neither.
- Editing the vendored skill locally forks it from upstream. Re-sync only, and
  record the new commit in `README.md` and `AGENTS.md` when re-syncing.
- ASD's ~900-word approved dictionary is not redistributable, so the skill
  carries the rule categories and applies the underlying principle instead. The
  lexical rules therefore stay a direction of travel, and no artifact here
  claims dictionary compliance.
