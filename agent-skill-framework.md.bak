# Gemini Agent Skill Framework (Best Practices & Architecture)

This document serves as the definitive framework for creating deterministic, composable agent skills (plugins/extensions) for the Gemini Agentic system. It is based on lessons learned from building the Integration Architect and Batch Dependency Analyzer agents.

## 1. Directory Architecture
A robust agent plugin must adhere to the following file structure to be correctly parsed and installed via the `agy cli`:

```text
my-agent-plugin/
├── gemini-extension.json     # Required: Declares the repo as an extension package
├── plugin.json               # Required: Minimal configuration (usually just {"name": "plugin-name"})
├── SKILL.md                  # Required: The "Master Orchestrator" entry point
├── README.md                 # Required: User documentation (how to install/use)
├── requirements.txt          # Optional: Python dependencies for Layer 3 tools
└── skills/                   # Required: Directory for all composable sub-skills
    ├── sub-skill-a/
    │   ├── SKILL.md          # The execution playbook for Sub-Skill A
    │   └── tools/            # Python scripts, binaries, or utilities
    │       └── script_a.py
    └── sub-skill-b/
        ├── SKILL.md          # The execution playbook for Sub-Skill B
        └── tools/
            └── script_b.py
```

## 2. The Master Orchestrator (Root `SKILL.md`)
The root `SKILL.md` does **not** do the actual computing work. Instead, it acts as a "Master Orchestrator" or traffic controller. It dictates exactly *when* to trigger sub-skills and defines strict "Gates" to prevent hallucination.

**Key Components:**
- **Phase Definition**: Break the workflow into phases.
- **Conditions**: What must be true to start the phase? (e.g., "Files exist in `./inbox/`")
- **Action**: Explicitly name the sub-skill to invoke (e.g., "Invoke `sub-skill-a`").
- **Goal**: What is the expected output? (e.g., "`output.json`")
- **Verification Gates (🛑)**: Explicit rules the agent MUST check before proceeding. If the goal isn't met, the agent must halt and not proceed to the next phase.

## 3. Sub-Skills as "Execution Playbooks"
Sub-skills live in `skills/<name>/SKILL.md`. They must be structured as strict, deterministic **Playbooks** rather than vague instructions.

**Standard Playbook Sections:**
1. **Environmental Scan & Pre-flight Check**: Instruct the agent to verify that required input directories (like `./inbox/`) exist, output files from previous phases are present, and required packages (`pip install -r requirements.txt`) are installed.
2. **Deterministic Execution (Compute Tools)**: Provide the exact terminal commands the agent must run. 
   - *Crucial*: Scripts must reside in the `tools/` directory (e.g., `python tools/my_script.py`).
   - Use dynamic inputs (like an `./inbox/` directory) rather than hardcoding specific filenames (`my_data.csv`).
3. **Semantic Validation**: Tell the agent how to evaluate the output of the compute tool. (e.g., "Check if the JSON contains `"status": "success"`).
4. **Final Handover**: Instruct the agent to summarize its work and explicitly hand control back to the Master Orchestrator for the next phase.

## 4. Layer 3 Tools (`tools/`)
The AI should not be relied upon to perform complex math, parse ASTs, or do heavy data lifting. This logic belongs in Layer 3 Tools.
- Tools should be deterministic code (e.g., Python).
- Tools should output structured, readable data (like JSON or Markdown) so the agent can easily parse the result in the "Validation" step.

## 5. Anti-Patterns to Avoid
- ❌ **Buried Orchestrator**: Do not place the master orchestration `SKILL.md` inside a sub-directory. It must sit at the root.
- ❌ **Hardcoded Filenames**: Do not design tools to look for `data123.csv`. Instead, use patterns like "read all `.csv` files in the `./inbox/` folder".
- ❌ **Scripts Directory**: Do not place python files in a `scripts/` folder; use `tools/`.
- ❌ **Missing `gemini-extension.json`**: Without this, the system may not recognize the repository as a full extension suite.
