#!/usr/bin/env python3
"""
Daily Reflection Tree — CLI Agent
Part B: Loads reflection-tree.json and walks the employee through it.
No LLM calls at runtime. Fully deterministic.
"""

import json
import os
import sys
import time
from pathlib import Path


# ─────────────────────────── helpers ────────────────────────────

def load_tree(path: str) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    nodes = {node["id"]: node for node in data["nodes"]}
    return nodes, data.get("meta", {})


def interpolate(text: str, state: dict) -> str:
    """Replace {NODE_ID.answer} placeholders with recorded answers."""
    if not text:
        return ""
    for node_id, answer in state.get("answers", {}).items():
        placeholder = "{" + node_id + ".answer" + "}"
        text = text.replace(placeholder, answer)
    # Axis summary interpolations
    for axis in ["axis1", "axis2", "axis3"]:
        dominant = state.get("signals", {}).get(axis, {})
        if dominant:
            winner = max(dominant, key=dominant.get)
            text = text.replace("{" + axis + ".dominant}", winner)
    # Resolve summary insight
    if "{summary_insight}" in text:
        text = text.replace("{summary_insight}", resolve_summary_insight(state))
    return text


def resolve_summary_insight(state: dict) -> str:
    signals = state.get("signals", {})

    def dominant(axis):
        d = signals.get(axis, {})
        if not d:
            return "unknown"
        return max(d, key=d.get)

    a1 = dominant("axis1")   # internal / external
    a2 = dominant("axis2")   # contribution / entitlement / neutral
    a3 = dominant("axis3")   # other / self

    insights = {
        ("internal", "contribution", "other"): "You brought yourself fully today — not just to your work, but to the people around it. That compounds.",
        ("internal", "contribution", "self"):  "You drove today well. Tomorrow, try letting your radius grow just a little wider.",
        ("internal", "entitlement", "other"):  "You noticed your hand in things and you noticed others. The contribution side may have a gap — what did you give that nobody asked for?",
        ("internal", "entitlement", "self"):   "You're self-aware about your own role — now try turning that same curiosity onto what the people around you need.",
        ("external", "contribution", "other"): "Even on a day where circumstances felt against you, you found ways to give to others. That's a resilience that's hard to teach.",
        ("external", "contribution", "self"):  "Some of your energy went outward today. The internal question — where was your agency, even a small one — is worth returning to tomorrow.",
        ("external", "entitlement", "other"):  "You noticed others today, which is more than most in hard moments. The agency piece is still there to develop — not as blame, but as power.",
        ("external", "entitlement", "self"):   "This was a tough day with a narrowed frame. That happens. Tomorrow starts fresh — and now you know exactly where the edges are.",
    }

    # Normalize axis2 — could be "neutral" if no signal recorded
    a2_key = a2 if a2 in ("contribution", "entitlement") else "contribution"
    key = (a1, a2_key, a3)
    return insights.get(key, "Reflection recorded. Every honest look at a day is worth taking.")


def tally_signal(signal: str, state: dict):
    if not signal:
        return
    parts = signal.split(":")
    if len(parts) != 2:
        return
    axis, pole = parts
    state.setdefault("signals", {}).setdefault(axis, {})
    state["signals"][axis][pole] = state["signals"][axis].get(pole, 0) + 1


def route_decision(node: dict, state: dict, nodes: dict) -> str:
    """Parse routing rules and return next node id."""
    rules = node.get("options", [])
    last_answer = state.get("last_answer", "")

    for rule in rules:
        # Format: "answer=OPT1|OPT2:TARGET_ID"
        if rule.startswith("answer="):
            _, rest = rule.split("answer=", 1)
            conditions, target_id = rest.rsplit(":", 1)
            valid_answers = [a.strip() for a in conditions.split("|")]
            if any(last_answer.startswith(v) or v in last_answer for v in valid_answers):
                return target_id.strip()

    # fallback: find first child
    for nid, n in nodes.items():
        if n.get("parentId") == node["id"]:
            return nid
    return None


def find_next(node: dict, nodes: dict) -> str:
    """Follow target or find first child."""
    if node.get("target"):
        return node["target"]
    for nid, n in nodes.items():
        if n.get("parentId") == node["id"]:
            return nid
    return None


# ─────────────────────────── display ────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
MAGENTA= "\033[35m"
WHITE  = "\033[97m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def hr(char="─", width=60, color=DIM):
    print(color + char * width + RESET)

def slow_print(text: str, delay: float = 0.018):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def print_header():
    clear()
    print()
    hr("═", color=CYAN)
    print(CYAN + BOLD + "  🌙  DAILY REFLECTION  ".center(60) + RESET)
    hr("═", color=CYAN)
    print()

def prompt_continue():
    input(DIM + "  [ press Enter to continue ]" + RESET)

def ask_question(node: dict) -> str:
    options = node.get("options", [])
    print()
    print(WHITE + BOLD + "  " + node["text"] + RESET)
    print()
    for i, opt in enumerate(options, 1):
        print(f"  {CYAN}{i}.{RESET} {opt}")
    print()
    while True:
        try:
            raw = input(DIM + "  Your choice (1-" + str(len(options)) + "): " + RESET).strip()
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print(DIM + "  Please enter a number between 1 and " + str(len(options)) + RESET)
        except (ValueError, KeyboardInterrupt):
            print(DIM + "  Please enter a number." + RESET)


# ─────────────────────────── walker ────────────────────────────

def walk(nodes: dict):
    state = {"answers": {}, "signals": {}, "last_answer": "", "path": []}
    current_id = "START"

    while current_id:
        node = nodes.get(current_id)
        if not node:
            print(f"  [ERROR] Node '{current_id}' not found.")
            break

        ntype = node.get("type")
        state["path"].append(current_id)
        text = interpolate(node.get("text", "") or "", state)

        print_header()

        if ntype == "start":
            slow_print("  " + CYAN + text + RESET, delay=0.012)
            print()
            prompt_continue()
            current_id = find_next(node, nodes)

        elif ntype == "question":
            node_display = dict(node)
            node_display["text"] = text
            answer = ask_question(node_display)
            state["answers"][current_id] = answer
            state["last_answer"] = answer
            tally_signal(node.get("signal"), state)
            # find decision child or next node
            next_id = None
            for nid, n in nodes.items():
                if n.get("parentId") == current_id and n.get("type") == "decision":
                    next_id = nid
                    break
            if not next_id:
                next_id = find_next(node, nodes)
            current_id = next_id

        elif ntype == "decision":
            current_id = route_decision(node, state, nodes)

        elif ntype == "reflection":
            print("  " + BLUE + "✦ Reflection" + RESET)
            print()
            slow_print("  " + text, delay=0.015)
            tally_signal(node.get("signal"), state)
            print()
            prompt_continue()
            current_id = find_next(node, nodes)

        elif ntype == "bridge":
            print()
            print(GREEN + "  ─── " + text + " ───" + RESET)
            print()
            time.sleep(1.2)
            current_id = node.get("target") or find_next(node, nodes)

        elif ntype == "summary":
            print("  " + YELLOW + BOLD + "✦ Today's Reflection Summary" + RESET)
            hr()
            print()
            slow_print("  " + text, delay=0.013)
            print()
            hr()
            prompt_continue()
            current_id = find_next(node, nodes)

        elif ntype == "end":
            print()
            slow_print("  " + MAGENTA + BOLD + text + RESET, delay=0.020)
            print()
            hr("═", color=CYAN)
            print()
            break

        else:
            # Unknown node type — just advance
            current_id = find_next(node, nodes)

    return state


# ─────────────────────────── main ────────────────────────────

def main():
    script_dir = Path(__file__).parent
    tree_path = script_dir.parent / "tree" / "reflection-tree.json"

    if not tree_path.exists():
        print(f"Error: Tree file not found at {tree_path}")
        sys.exit(1)

    nodes, meta = load_tree(str(tree_path))
    final_state = walk(nodes)

    # Optionally print debug path
    if "--debug" in sys.argv:
        print("\nDEBUG — Path taken:", " → ".join(final_state["path"]))
        print("Signals:", json.dumps(final_state.get("signals", {}), indent=2))


if __name__ == "__main__":
    main()
