"""Online chess lobby: match codes + public open-games list + JSON store."""
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
    safe = "".join(c for c in (code or "").upper() if c.isalnum())[:12]
    return _dir() / f"{safe}.json"


def create_match(name: str = "Player", public: bool = True) -> str:
    code = uuid.uuid4().hex[:6].upper()
    data = {
        "code": code,
        "created": time.time(),
        "host": (name or "Host").strip()[:24],
        "guest": None,
        "moves": [],
        "status": "waiting",
        "public": bool(public),
        "notify_host": False,
        "notify_guest": False,
        "last_move_by": None,
    }
    _path(code).write_text(json.dumps(data), encoding="utf-8")
    return code


def join_match(code: str, name: str = "Guest"):
    p = _path(code)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    name = (name or "Guest").strip()[:24]
    if data.get("status") == "waiting" and not data.get("guest"):
        data["guest"] = name
        data["status"] = "active"
        data["notify_host"] = True
        p.write_text(json.dumps(data), encoding="utf-8")
    return data


def load_match(code: str):
    p = _path(code)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def list_open_matches(limit: int = 20) -> list:
    out = []
    now = time.time()
    for p in sorted(_dir().glob("*.json"), key=lambda x: -x.stat().st_mtime):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("status") == "waiting" and now - float(data.get("created") or 0) > 7200:
            try:
                p.unlink()
            except Exception:
                pass
            continue
        if data.get("status") == "waiting" and data.get("public", True) and not data.get("guest"):
            out.append({
                "code": data.get("code"),
                "host": data.get("host"),
                "age_s": int(now - float(data.get("created") or now)),
            })
        if len(out) >= limit:
            break
    return out


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


def leave_match(code: str, role: str) -> None:
    p = _path(code)
    if not p.exists():
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return
    if role == "host" and data.get("status") == "waiting":
        try:
            p.unlink()
        except Exception:
            pass
        return
    data["status"] = "ended"
    p.write_text(json.dumps(data), encoding="utf-8")


def apply_online(code: str) -> str:
    if "Online Play \u00b7 Open lobby" in code or "list_open_matches" in code:
        return code
    block = (
        "\n    # === Online matchmaking (public lobby + codes) ===\n"
        "    with st.expander(\"Online Play \u00b7 Open lobby\", expanded=True):\n"
        "        st.caption(\"Challenge anyone on the site \u2014 open games appear below. Or share a private code.\")\n"
        "        from online_chess import (\n"
        "            create_match, join_match, load_match, push_move, clear_notify,\n"
        "            list_open_matches, leave_match,\n"
        "        )\n"
        "        if \"online_code\" not in st.session_state:\n"
        "            st.session_state.online_code = None\n"
        "            st.session_state.online_role = None\n"
        "        if \"online_name\" not in st.session_state:\n"
        "            st.session_state.online_name = st.session_state.get(\"username\") or \"Player\"\n"
        "        my_name = st.text_input(\"Your display name\", value=st.session_state.online_name, key=\"on_name\")\n"
        "        st.session_state.online_name = (my_name or \"Player\").strip()[:24]\n"
        "        st.markdown(\"##### Open games\")\n"
        "        _opens = list_open_matches()\n"
        "        if not _opens:\n"
        "            st.caption(\"No open games right now \u2014 create one.\")\n"
        "        else:\n"
        "            for _g in _opens:\n"
        "                _gc1, _gc2, _gc3 = st.columns([2, 2, 1])\n"
        "                with _gc1:\n"
        "                    st.write(f\"**{_g.get('host') or 'Host'}**\")\n"
        "                with _gc2:\n"
        "                    st.caption(f\"code `{_g.get('code')}` \u00b7 {_g.get('age_s', 0)}s ago\")\n"
        "                with _gc3:\n"
        "                    if st.button(\"Join\", key=f\"on_join_open_{_g.get('code')}\"):\n"
        "                        _jd = join_match(str(_g.get(\"code\")), st.session_state.online_name)\n"
        "                        if _jd is None:\n"
        "                            st.error(\"Gone \u2014 refresh.\")\n"
        "                        else:\n"
        "                            st.session_state.online_code = _jd[\"code\"]\n"
        "                            st.session_state.online_role = \"guest\"\n"
        "                            st.success(f\"Joined {_jd['code']}\")\n"
        "                            st.rerun()\n"
        "        if st.button(\"Refresh lobby\", key=\"on_refresh_lobby\"):\n"
        "            st.rerun()\n"
        "        st.markdown(\"##### Create / join by code\")\n"
        "        on1, on2 = st.columns(2)\n"
        "        with on1:\n"
        "            _pub = st.checkbox(\"List in public lobby\", value=True, key=\"on_public\")\n"
        "            if st.button(\"Create match\", key=\"on_create\", type=\"primary\"):\n"
        "                _code = create_match(st.session_state.online_name, public=_pub)\n"
        "                st.session_state.online_code = _code\n"
        "                st.session_state.online_role = \"host\"\n"
        "                st.success(f\"Match code: **{_code}**\")\n"
        "                st.rerun()\n"
        "        with on2:\n"
        "            join_code = st.text_input(\"Join code\", key=\"on_join_code\", max_chars=8)\n"
        "            if st.button(\"Join with code\", key=\"on_join\") and join_code:\n"
        "                _jd = join_match(join_code.strip().upper(), st.session_state.online_name)\n"
        "                if _jd is None:\n"
        "                    st.error(\"Match not found.\")\n"
        "                else:\n"
        "                    st.session_state.online_code = _jd[\"code\"]\n"
        "                    st.session_state.online_role = \"guest\" if _jd.get(\"guest\") == st.session_state.online_name else \"host\"\n"
        "                    st.success(f\"Joined {_jd['code']}\")\n"
        "                    st.rerun()\n"
        "        if st.session_state.online_code:\n"
        "            data = load_match(st.session_state.online_code)\n"
        "            if not data:\n"
        "                st.warning(\"Match expired.\")\n"
        "                st.session_state.online_code = None\n"
        "            else:\n"
        "                st.info(f\"Match **{data['code']}** \u00b7 {data.get('status')} \u00b7 host: {data.get('host')} \u00b7 guest: {data.get('guest') or 'waiting\u2026'}\")\n"
        "                role = st.session_state.online_role\n"
        "                if role == \"host\" and data.get(\"notify_host\"):\n"
        "                    st.toast(f\"Opponent moved! ({data.get('last_move_by')})\", icon=\"\u265f\")\n"
        "                    clear_notify(data[\"code\"], \"host\")\n"
        "                if role == \"guest\" and data.get(\"notify_guest\"):\n"
        "                    st.toast(f\"Opponent moved! ({data.get('last_move_by')})\", icon=\"\u265f\")\n"
        "                    clear_notify(data[\"code\"], \"guest\")\n"
        "                move_txt = st.text_input(\"Send move (e.g. e2e4)\", key=\"on_move_txt\")\n"
        "                if st.button(\"Send move\", key=\"on_send\") and move_txt:\n"
        "                    push_move(data[\"code\"], move_txt.strip(), st.session_state.online_name)\n"
        "                    st.success(\"Move sent.\")\n"
        "                    st.rerun()\n"
        "                if data.get(\"moves\"):\n"
        "                    st.write(\"Moves:\", \" \u00b7 \".join(m[\"move\"] for m in data[\"moves\"][-16:]))\n"
        "                if st.button(\"Leave match\", key=\"on_leave\"):\n"
        "                    try:\n"
        "                        leave_match(data[\"code\"], role or \"guest\")\n"
        "                    except Exception:\n"
        "                        pass\n"
        "                    st.session_state.online_code = None\n"
        "                    st.session_state.online_role = None\n"
        "                    st.rerun()\n"
        "                st.caption(\"Stay on this page and refresh / send moves to sync.\")\n"
    )
    if "st.components.v1.html(" in code and "Online Play \u00b7 Open lobby" not in code:
        code = code.replace(
            "st.components.v1.html(",
            block + "\n    st.components.v1.html(",
            1,
        )
    return code
