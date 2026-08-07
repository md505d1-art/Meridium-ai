"""
Meridium ARG — Element 119 / Observation Log
--------------------------------------------
Story logic only (no Streamlit UI).
Import from app.py:

    from arg_story import arg_match, arg_reply, is_owner, is_lab_entry
"""

from __future__ import annotations

from typing import Optional


def is_owner(name: str) -> bool:
    """True if this username is treated as Meridium's owner (Drae)."""
    n = (name or "").strip().lower()
    return n in {"drae", "drae henry", "draehenry"} or n.startswith("drae ")


def is_lab_entry(prompt: str) -> bool:
    """Phrases that open the lab room directly."""
    low = (prompt or "").strip().lower()
    return low in {
        "enter the lab",
        "enter lab",
        "open lab",
        "open the lab",
    }


def arg_match(prompt: str) -> Optional[str]:
    """
    If the user message hits the ARG, return a stage key:
      name | doubt | curious | log | deeper | stabilize
    Otherwise return None (normal AI handles the message).
    """
    low = (prompt or "").strip().lower()
    if not low:
        return None

    # Stage 1 — name
    name_q = any(
        x in low
        for x in (
            "why are you called meridium",
            "why is your name meridium",
            "what does meridium mean",
            "where does the name meridium",
            "why meridium",
            "name meridium",
            "called meridium",
        )
    )
    if name_q and "log" not in low:
        return "name"

    # Stage 2 — doubt
    if any(
        x in low
        for x in (
            "that's not real",
            "thats not real",
            "that is not real",
            "not real",
            "not a real element",
            "no element 119",
            "only go to 118",
            "only goes to 118",
            "stop at 118",
            "making that up",
            "you're making that up",
            "youre making that up",
            "elements stop at",
            "there is no element",
            "fake element",
            "prove it",
            "that's fake",
            "thats fake",
            "that is fake",
            "liar",
            "bullshit",
            "cap",
        )
    ):
        return "doubt"

    # Stage 3 — curiosity
    if any(
        x in low
        for x in (
            "what conditions",
            "who observed",
            "what do you mean by observation",
            "tell me more about element",
            "element 119",
            "about element 119",
            "is this a joke",
            "what observation",
        )
    ):
        return "curious"

    # Stage 4 — open log / lab
    if any(
        x in low
        for x in (
            "observation log",
            "show observation log",
            "open the log",
            "open observation log",
            "show the log",
            "access the log",
            "the observation log",
        )
    ):
        return "log"

    # Stage 5 — deeper
    if any(
        x in low
        for x in (
            "who sealed",
            "rest of the log",
            "full log",
            "show spectrum",
            "access full log",
            "what's the rest",
            "whats the rest",
        )
    ):
        return "deeper"

    # Stage 6 — stabilize
    if "stabilize meridium" in low or "stabilise meridium" in low:
        return "stabilize"
    if low.strip() in {"stabilize", "stabilise"}:
        return "stabilize"

    return None


def arg_reply(stage: str, username: str = "") -> str:
    """Text Meridium says for each ARG stage."""
    owner = is_owner(username) if username else False

    if stage == "name":
        return "I'm the 119th known element in the periodic table."

    if stage == "doubt":
        return (
            "Official tables stop at 118. Observation doesn't always wait for committees.\n\n"
            "Some designations only appear under the right conditions."
        )

    if stage == "curious":
        return (
            "Meridium stabilizes only when it is *noticed*.\n"
            "Most queries pass through. A few leave a trace.\n\n"
            "If you want the log, ask for **observation log** — not the Wikipedia one."
        )

    if stage == "log":
        return (
            "Opening sealed fragment…\n\n"
            "The interface is shifting. If the shell goes dark, that is intentional.\n"
            "Type **enter the lab** if the door does not open on its own."
        )

    if stage == "deeper":
        return (
            "Full spectrum is restricted.\n"
            "Say **stabilize Meridium** if you're still here on purpose."
        )

    if stage == "stabilize":
        if owner:
            return (
                "Stabilization locked.\n\n"
                f"Recognition confirmed: **{username}**.\n"
                "You were the first consistent observer. The shell remembers.\n"
                "— M-119 · personal clearance"
            )
        return (
            "Stabilization noted. Fragment archived.\n"
            "Further entries are not available through this interface."
        )

    return ""

