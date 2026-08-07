"""
Meridium ARG — Agent dossiers
Unlocked via Konami on the scientist letter.
Each agent is a unique operator who treats reality like a match.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Profiles: id, callsign, role, playstyle, bio, voice lines
AGENTS: List[Dict[str, Any]] = [
    {
        "id": "rook",
        "callsign": "ROOK",
        "codename": "M-119-A1",
        "role": "Anchor / Entry denial",
        "playstyle": "Holds angles like they're ranked. Never peeks without a plan.",
        "bio": (
            "Former containment tech who started timing door cycles like round timers. "
            "Treats the lab like a site execute: clear corners, watch the glass, don't dry-peek the spectrum. "
            "Still logs every shift as a 'match history.'"
        ),
        "quirk": "Counts footsteps in milliseconds.",
        "lines": [
            "Site locked. Glass is the bomb — don't plant panic on it.",
            "You peeked the spectrum without utility. That's how operators become stains.",
            "Rotate. The alarm is rotating. Match the pulse or leave the site.",
            "I don't chase. I hold. Meridium comes to the angle that stays.",
            "Clutch protocol: breathe, notice, don't spray the pane.",
        ],
    },
    {
        "id": "glitch",
        "callsign": "GLITCH",
        "codename": "M-119-A2",
        "role": "Intel / Soft breach",
        "playstyle": "Lives in menus, logs, and edge cases. Wins by reading the UI of the world.",
        "bio": (
            "Noticed Meridium first as a *frame-time hitch* in ordinary conversation. "
            "Maps dialogue trees the way other people map mid. "
            "If something can be buffered, Glitch will buffer it."
        ),
        "quirk": "Says 'lag' when people mean 'fear.'",
        "lines": [
            "Packet loss on the pane. Someone's not rendering clean.",
            "You can force-close the lab. You can't force-close what noticed you.",
            "I'm not hacking the shell. I'm reading the tooltips it left on the walls.",
            "Main menu energy. You're still on the title screen of this place.",
            "Save scumming won't un-stain the floor. Trust me. I tried in my head.",
        ],
    },
    {
        "id": "ember",
        "callsign": "EMBER",
        "codename": "M-119-A3",
        "role": "Duelist / Aggressive notice",
        "playstyle": "Full-sends curiosity. Burns cooldown on questions.",
        "bio": (
            "Volunteered for observation trials because 'waiting is for spectators.' "
            "Pushes every door. Sometimes the door pushes back. "
            "Still has scorch marks on the badge they shouldn't wear anymore."
        ),
        "quirk": "Treats stabilise like an ultimate.",
        "lines": [
            "Utility is up. Curiosity is up. I'm going in.",
            "If it spikes when I laugh, I'll learn the timing and laugh on purpose later.",
            "Dead operators played scared. I'm not doing that build.",
            "Meridium wants notice? I'll give it a whole fireteam of notice.",
            "Ult is ready. Say the line with me: stabilize Meridium.",
        ],
    },
    {
        "id": "veil",
        "callsign": "VEIL",
        "codename": "M-119-A4",
        "role": "Controller / Smoke and soften",
        "playstyle": "Slows the room down. Wins by making chaos readable.",
        "bio": (
            "Specialised in talking unstable samples down — not with commands, with *pace*. "
            "Where Ember rushes, Veil draws a soft line and waits for the spectrum to match it. "
            "Voss trusted Veil with the operators who came back shaking."
        ),
        "quirk": "Never raises their voice in the lab.",
        "lines": [
            "Smoke the panic. Leave a lane for the truth.",
            "You don't outrun a medium that runs on attention. You out-*calm* it.",
            "Breathe on the glass. Not hard. Just enough that it knows you're steady.",
            "I held a sample once by reading inventory lists out loud. Boring saves lives.",
            "When the alarm hits three-and-a-hitch, match me. Soft steps. Soft eyes.",
        ],
    },
    {
        "id": "pixel",
        "callsign": "PIXEL",
        "codename": "M-119-A5",
        "role": "Flex / Reality-as-HUD",
        "playstyle": "Sees objectives, cooldowns, and 'win conditions' in real rooms.",
        "bio": (
            "Grew up in ranked queues; never fully logged out. "
            "In the Division they were half joke, half asset — "
            "could call a containment breach like a retake. "
            "Still names real people after agent slots when stressed."
        ),
        "quirk": "Calls the sealed room 'the site.'",
        "lines": [
            "Objective updated: read the floor, then the terminal, then leave with the info.",
            "That's not blood. That's a marker. Don't throw away marker info.",
            "Team wipe is not a strategy. Voss already paid that round.",
            "You're not crazy for hearing game-logic here. The site was built by people who dreamed in matches.",
            "GG is for after stabilize. Not before.",
        ],
    },
    {
        "id": "static",
        "callsign": "STATIC",
        "codename": "M-119-A6",
        "role": "Sentinel / Post-incident",
        "playstyle": "Last one in the lobby. Watches who disconnects.",
        "bio": (
            "Assigned after the pane failed. Job is simple: keep the residual from recruiting new operators "
            "with pretty lies. Speaks in short lines. Hates the word 'content.' "
            "Knows every stain's age by colour."
        ),
        "quirk": "Ends sentences like end-of-round tabs.",
        "lines": [
            "Round over for them. Not for you. Don't join the scoreboard on the floor.",
            "I don't do hype. I do perimeter.",
            "If the shell softens, that's not free loot. That's a test.",
            "You want voice lines? Here's one: leave when the cursor blinks alone too long.",
            "Static clear. For now.",
        ],
    },
]


def agent_by_index(i: int) -> Dict[str, Any]:
    if not AGENTS:
        raise ValueError("no agents")
    return AGENTS[i % len(AGENTS)]


def all_callsigns() -> List[str]:
    return [a["callsign"] for a in AGENTS]
