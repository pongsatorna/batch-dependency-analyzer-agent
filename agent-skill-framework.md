# Agent Skill Framework

This framework is based on Anthropic's guidelines for creating composable agent skills.

## 1. Break the Domain Down into Composable Skills
Instead of building a massive, single prompt, break the process down into small, highly focused, reusable skills. This makes it easier to handle edge cases, maintain logic, and isolate bugs.

## 2. Define the Three Layers of Each Skill
For each skill you build, map out the three layers to maximize leverage:

- **Layer 1: Description (Vitals for AI Routing)**
  What the skill does and when it should be used, helping the agent's routing logic know when to trigger it.
  
- **Layer 2: Instructions (The Integration Architecture Playbook)**
  The detailed prompt, rules, and logic dictating how the agent should perform the task.
  
- **Layer 3: Tools (Deterministic Engineering Assets)**
  Code, scripts, or external functions that the agent can use to execute deterministic parts of the skill (e.g., parsing files, generating reports).
