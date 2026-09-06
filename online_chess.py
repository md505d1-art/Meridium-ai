"""Simple online chess lobby via match codes + JSON file store + toast notifications."""
from __future__ import annotations
import json
import time
import uuid
from pathlib import Path

def _dir() -> Path:
    d = Path(__file__).resolve().parent / "data" / "online_chess"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _path(code: str) -> Path:
    safe = "".join(c for c in code.upper() if c.isalnum())[:12]
    return _dir() / f"{safe}.json"

def create_match(name: str = "Player") -> str:
    code = uuid.uuid4().hex[:6].upper()
    data = {
        "code": code,
        "created": time.time(),
        "host": name or "Host",
        "guest": None,
        "moves": [],
        "fen": None,
        "turn": "w",
        "status": "waiting",
        "notify_host": False,
        "notify_guest": False,
        "last_move_by": None,
        "chat": [],
    }
    _path(code).write_text(json.dumps(data), encoding="utf-8")
    return code

def join_match(code: str, name: str = "Guest"):
    p = _path(code)
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("status") == "waiting" and not data.get("guest"):
        data["guest"] = name or "Guest"
        data["status"] = "active"
        data["notify_host"] = True
        p.write_text(json.dumps(data), encoding="utf-8")
    return data

def load_match(code: str):
    p = _path(code)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def push_move(code: str, move: str, by: str):
    p = _path(code)
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    data.setdefault("moves", []).append({"move": move, "by": by, "t": time.time()})
    data["last_move_by"] = by
    if by == data.get("host"):
        data["notify_guest"] = True
        data["notify_host"] = False
    else:
        data["notify_host"] = True
        data["notify_guest"] = False
    p.write_text(json.dumps(data), encoding="utf-8")
    return data

def clear_notify(code: str, role: str) -> None:
    p = _path(code)
    if not p.exists():
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    if role == "host":
        data["notify_host"] = False
    else:
        data["notify_guest"] = False
    p.write_text(json.dumps(data), encoding="utf-8")

def apply_online(code: str) -> str:
    """Inject an Online Play expander into the chess view."""
    block = r'''
    # === Online matchmaking (match codes + file store) ===
    with st.expander("Online Play · Match codes", expanded=False):
        st.caption("Create a match, share the code. Friend joins. Moves sync via refresh. Notifications appear as toasts.")
        from online_chess import create_match, join_match, load_match, push_move, clear_notify
        if "online_code" not in st.session_state:
            st.session_state.online_code = None
            st.session_state.online_role = None
            st.session_state.online_name = st.session_state.get("username", "Player") or "Player"
        on1, on2 = st.columns(2)
        with on1:
            my_name = st.text_input("Your name", value=st.session_state.online_name, key="on_name")
            st.session_state.online_name = my_name
            if st.button("Create match", key="on_create"):
                code = create_match(my_name)
                st.session_state.online_code = code
                st.session_state.online_role = "host"
                st.success(f"Match code: **{code}** — share it!")
                st.rerun()
        with on2:
            join_code = st.text_input("Join code", key="on_join_code", max_chars=8)
            if st.button("Join match", key="on_join") and join_code:
                data = join_match(join_code.strip().upper(), my_name)
                if data is None:
                    st.error("Match not found.")
                else:
                    st.session_state.online_code = data["code"]
                    st.session_state.online_role = "guest" if data.get("guest") == my_name else "host"
                    st.success(f"Joined {data['code']}")
                    st.rerun()
        if st.session_state.online_code:
            data = load_match(st.session_state.online_code)
            if data:
                st.info(f"Match **{data['code']}** · status: {data.get('status')} · host: {data.get('host')} · guest: {data.get('guest') or 'waiting…'}")
                role = st.session_state.online_role
                if role == "host" and data.get("notify_host"):
                    st.toast(f"Opponent moved! ({data.get('last_move_by')})", icon="♟️")
                    clear_notify(data["code"], "host")
                if role == "guest" and data.get("notify_guest"):
                    st.toast(f"Opponent moved! ({data.get('last_move_by')})", icon="♟️")
                    clear_notify(data["code"], "guest")
                move_txt = st.text_input("Push move (e.g. e2e4 or Nf3)", key="on_move_txt")
                if st.button("Send move", key="on_send") and move_txt:
                    push_move(data["code"], move_txt.strip(), my_name)
                    st.success("Move sent.")
                    st.rerun()
                if data.get("moves"):
                    st.write("Moves:", " · ".join(m["move"] for m in data["moves"][-12:]))
                if st.button("Leave match", key="on_leave"):
                    st.session_state.online_code = None
                    st.session_state.online_role = None
                    st.rerun()
                if data.get("status") in ("waiting", "active"):
                    st.caption("Refresh the page or re-open this expander to poll for updates.")
'''
    if "st.components.v1.html(" in code:
        code = code.replace(
            "st.components.v1.html(",
            block + "\n    st.components.v1.html(",
            1,
        )
    return code
