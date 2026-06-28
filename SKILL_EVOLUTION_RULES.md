---
name: skill-evolution-rules
description: General rules for agents to identify, propose, and apply essential updates to cloned skills after real-world usage.
version: 1.0.0
---

# Skill Evolution Rules

When an agent clones and uses a skill (playbook + tools), it MUST follow these rules to keep the skill accurate, robust, and self-improving.

---

## Rule 1: Detect Gaps During Execution

After each phase execution, the agent MUST evaluate:

| Check | Question |
|-------|----------|
| **Input Mismatch** | Did the actual input format differ from what the skill documented? |
| **Tool Failure** | Did any tool fail due to unhandled data, missing logic, or wrong assumptions? |
| **Missing Handling** | Was there a real-world pattern (e.g., DML type, column name, edge case) the tool didn't cover? |
| **Dependency Issue** | Did a pinned version fail to install? Was a new dependency needed? |
| **Cycle/Error Resolution** | Did the agent need manual intervention to resolve an error the tool should have handled? |

If ANY answer is "yes", the agent MUST propose an update.

---

## Rule 2: Classify the Update Level

Every proposed change must be classified by scope:

| Level | Scope | What to Update | Example |
|-------|-------|----------------|---------|
| **L1 - Tool** | Python script logic | `tools/*.py` | Add support for new SQL statement type |
| **L2 - Sub-Skill** | Skill playbook instructions | `skills/*/SKILL.md` | Document new input format, add validation step |
| **L3 - Orchestrator** | Phase flow or gating | `SKILL.md` (root) | Add new phase, change gate conditions |
| **L4 - Project** | Entry points, dependencies, docs | `README.md`, `requirements.txt`, `run_pipeline.py` | Add new tool, update usage instructions |

**Rule: Updates MUST cascade upward.** If L1 changes tool behavior, L2 must reflect the new capability, L3 must know about it, and L4 must document it for users.

---

## Rule 3: Propose Before Applying

The agent MUST structure proposals as:

```
## Proposed Skill Update

**Trigger:** [What happened during execution that revealed the gap]
**Level:** L1/L2/L3/L4
**Files affected:**
- `path/to/file` — [what changes]

**Rationale:** [Why this makes the skill smarter for next use]

**Breaking change:** Yes/No
```

If the user is present, wait for approval. If running autonomously, apply non-breaking changes (L1-L2) and flag breaking changes (L3-L4) for review.

---

## Rule 4: Update Completeness Checklist

Before committing any skill update, ALL of these must be satisfied:

- [ ] **Tool works:** The modified tool runs successfully against the same input that triggered the gap.
- [ ] **SKILL.md reflects reality:** The sub-skill playbook matches what the tool actually does (commands, inputs, outputs, validation).
- [ ] **Orchestrator knows:** The root `SKILL.md` references any new capabilities, phases, or gate changes.
- [ ] **README is accurate:** Usage instructions, CSV formats, tool commands, and output files are all correct.
- [ ] **Dependencies pinned:** Any new package is in `requirements.txt` with a minimum version (not exact pin if version was yanked).
- [ ] **Pipeline runner updated:** If a new tool was added, `run_pipeline.py` includes it.

---

## Rule 5: Commit Discipline

Each skill update commit must:

1. **Scope the message** — prefix with `fix:`, `feat:`, or `docs:` depending on change type.
2. **List affected levels** — mention L1/L2/L3/L4 in the commit body.
3. **Explain the trigger** — one line on what real-world scenario caused this update.

Example:
```
feat: handle DELETE/UPDATE DML in lineage parser

L1: rewrite parse_lineage.py for proper AST-based table extraction
L2: update sql-column-lineage-parser SKILL.md with DML handling docs
L3: no change (orchestrator flow unchanged)
L4: README updated with supported SQL types

Trigger: Real CSV contained DELETE FROM / UPDATE SET statements that
the original naive parser couldn't extract table names from.
```

---

## Rule 6: Feedback Signal Categories

When the agent encounters issues, classify them for prioritized improvement:

| Priority | Signal | Action |
|----------|--------|--------|
| **P0 - Broken** | Tool crashes or produces wrong output | Fix immediately, block pipeline |
| **P1 - Incomplete** | Tool works but misses real patterns | Enhance tool, update docs |
| **P2 - Inaccurate Docs** | Tool works differently than SKILL.md describes | Update docs only |
| **P3 - Enhancement** | Could be smarter but works fine | Propose for future, don't block |

---

## Rule 7: Skill Version Tracking

After applying updates:

1. Bump the `version` in the affected SKILL.md frontmatter (patch for fixes, minor for features).
2. Keep a changelog pattern in commits so any agent can trace why a skill evolved.

---

## Summary: The Feedback Loop

```
Clone Skill → Execute Against Real Data → Detect Gaps → Classify Level
    → Propose Update → Validate Completeness → Commit with Discipline
    → Skill is now smarter for next agent/user
```

The goal: **Every real-world execution makes the skill better.** No gap encountered twice.
