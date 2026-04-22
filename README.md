# Daily Reflection Tree

**DT Fellowship Assignment — Submission**  
*The Daily Reflection Tree: A Deterministic End-of-Day Reflection Agent*

---

## What This Is

An end-of-day reflection tool that walks an employee through a structured, branching conversation across three psychological axes:

1. **Locus** — Victim ↔ Victor (Rotter, 1954; Dweck, 2006)
2. **Orientation** — Entitlement ↔ Contribution (Campbell et al., 2004; Organ, 1988)
3. **Radius** — Self-Centric ↔ Altrocentric (Maslow, 1969; Batson, 2011)

**No LLM at runtime.** Every path is deterministic. Same answers → same conversation → same reflection, every time.

---

## Repository Structure

```
/tree/
  reflection-tree.json     ← Part A: the full tree (36 nodes, all 3 axes)
  tree-diagram.md          ← Part A: Mermaid visual diagram of all branches

/agent/
  agent.py                 ← Part B: Python CLI agent (no dependencies beyond stdlib)

/transcripts/
  persona-1-transcript.md  ← Victor / Contributing / Altrocentric path
  persona-2-transcript.md  ← Victim / Entitled / Self-Centric path + comparison table

write-up.md                ← Part A: Design rationale (≤2 pages)
README.md                  ← This file
```

---

## Part A: Reading the Tree

The tree lives in `tree/reflection-tree.json`. It is a flat array of node objects. To trace any path manually:

1. Start at node `"id": "START"`
2. Follow `target` (if set) or find the child node whose `parentId` matches the current node's `id`
3. At `decision` nodes, parse the `options` array — each rule is `answer=VALUE1|VALUE2:TARGET_ID`
4. At `question` nodes, the employee's answer is stored in state as `answers[node_id]`
5. `{NODE_ID.answer}` placeholders in text are interpolated at render time

### Node Types

| Type | Employee sees | Auto-advances? |
|------|--------------|----------------|
| `start` | Opening message | Yes |
| `question` | Question + fixed options | No — waits for pick |
| `decision` | Nothing | Yes — routes silently |
| `reflection` | Reframe insight | No — waits for "continue" |
| `bridge` | Axis transition | Yes |
| `summary` | Synthesis + insight | No — waits for "continue" |
| `end` | Closing message | Yes — exits |

### Tree Stats

| Metric | Count |
|--------|-------|
| Total nodes | 36 |
| Question nodes | 11 |
| Decision nodes | 8 |
| Reflection nodes | 8 |
| Bridge nodes | 2 |
| Summary nodes | 1 |
| Distinct full paths | 8 |
| Axes covered | 3 (in sequence) |

---

## Part B: Running the Agent

**Requirements:** Python 3.7+. No external libraries.

```bash
# From repo root
python agent/agent.py

# Debug mode (prints path + signal tallies after session)
python agent/agent.py --debug
```

The agent loads `tree/reflection-tree.json` relative to its own location — no hardcoded paths, no LLM calls, no network.

**What it does:**
- Renders each node with appropriate formatting (color, pacing)
- Waits for numbered input at question nodes
- Routes silently through decision nodes
- Interpolates `{node_id.answer}` placeholders in reflection and summary text
- Tallies axis signals and selects the correct summary insight from 8 pre-written options
- Produces a complete session summary

---

## Key Design Decisions

See `write-up.md` for the full rationale. In brief:

- **Weather metaphor** at opening uses externalizing language to reduce defensiveness (Motivational Interviewing technique)
- **Setback question** is the crux of Axis 1 — two variants surface differently based on prior routing, calibrated to the employee's already-revealed tendency
- **Scoreboard framing** in Axis 2 makes entitlement visible without the word "entitlement"
- **"Frame" framing** in Axis 3 invokes cognitive perspective-taking naturally
- **8 pre-written summary insights** cover all axis-combination keys — no LLM needed for personalization

---

## The Anti-Hallucination Architecture

This tool has no runtime AI dependency by design. All possible outputs are pre-authored:

- Reflection nodes: 8 fixed texts, each crafted for a specific signal context
- Summary insights: 8 fixed texts, selected by composite axis key `(axis1, axis2, axis3)`
- Interpolation: simple string replacement from recorded answers, no generation

The tree is the intelligence. The code is just a walker.
