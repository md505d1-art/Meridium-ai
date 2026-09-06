"""Owner pad enhancements: chess admin, events/cutscenes, quality fixes."""
from __future__ import annotations


def _patch_owner_grants_coaches(code: str) -> str:
    """Make apply_owner_grants_for_user also restore unlocked_coaches."""
    if "unlocked_coaches from grants" in code:
        return code
    needle2 = '    title = grants.get("title")'
    inject2 = """    # unlocked_coaches from grants
    _uc = grants.get("unlocked_coaches") or []
    if isinstance(_uc, list) and _uc:
        cur = list(st.session_state.get("unlocked_coaches") or [])
        for _c in _uc:
            if _c and _c not in cur:
                cur.append(_c)
        st.session_state.unlocked_coaches = cur
    title = grants.get("title")"""
    if needle2 in code:
        code = code.replace(needle2, inject2, 1)
    return code

def apply_owner_enhancements(code: str) -> str:
    """Inject Chess admin tab + Events/cutscenes into the owner desk."""

    code = _patch_owner_grants_coaches(code)
    if "owner_chess_user" in code:
        return code

    chess_block = r'''
    # ---------- CHESS ADMIN (owner) ----------
    with st.expander("♟️ Chess control", expanded=False):
        st.caption("Give Elo, unlock coaches, reset chess progress for any user (session + save file).")
        _tuser = st.text_input("Target username", key="owner_chess_user", placeholder="exact name")
        c1, c2, c3 = st.columns(3)
        with c1:
            _elo = st.number_input("Set Elo", min_value=100, max_value=3000, value=1500, step=50, key="owner_chess_elo")
        with c2:
            if st.button("Apply Elo", key="owner_chess_elo_btn", type="primary", use_container_width=True):
                try:
                    from extra_features import load_ratings, save_ratings
                    r = load_ratings()
                    name = (_tuser or "").strip() or "anon"
                    e = r.get(name, {"elo": 1000, "wins": 0, "losses": 0})
                    e["elo"] = int(_elo)
                    r[name] = e
                    save_ratings(r)
                    st.success(f"Elo set to {int(_elo)} for {name}")
                except Exception as _e:
                    st.error(str(_e))
        with c3:
            if st.button("Unlock ALL coaches", key="owner_unlock_all_coaches", use_container_width=True):
                try:
                    from extra_features import ALL_COACHES, try_unlock
                    for _c in ALL_COACHES:
                        try_unlock(st.session_state, _c)
                    st.session_state.unlocked_coaches = list(ALL_COACHES)
                    st.session_state["_owner_all_coaches"] = True
                    st.success("All coaches unlocked for this session.")
                    try:
                        grants = owner_grants_load()
                        key = (_tuser or st.session_state.get("username") or "").strip().lower()
                        if key:
                            g = grants.get(key) or {}
                            g["unlocked_coaches"] = list(ALL_COACHES)
                            grants[key] = g
                            owner_grants_save(grants)
                            st.caption(f"Persisted unlock grant for `{key}`.")
                    except Exception:
                        pass
                except Exception as _e:
                    st.error(str(_e))

        st.markdown("##### Quick chess tools")
        q1, q2, q3 = st.columns(3)
        with q1:
            if st.button("Open Chess page", key="owner_goto_chess", use_container_width=True):
                st.session_state.view = "chess"
                st.rerun()
        with q2:
            if st.button("+100 Elo (self)", key="owner_self_elo", use_container_width=True):
                try:
                    from extra_features import load_ratings, save_ratings
                    me = (st.session_state.get("username") or "anon").strip()
                    r = load_ratings()
                    e = r.get(me, {"elo": 1000, "wins": 0, "losses": 0})
                    e["elo"] = int(e.get("elo", 1000)) + 100
                    r[me] = e
                    save_ratings(r)
                    st.success(f"Your Elo → {e['elo']}")
                except Exception as _e:
                    st.error(str(_e))
        with q3:
            if st.button("Reset my chess unlocks", key="owner_reset_chess_ul", use_container_width=True):
                st.session_state.unlocked_coaches = []
                st.session_state.pop("_owner_all_coaches", None)
                st.session_state.pop("_wins", None)
                st.success("Session chess unlocks cleared.")

        st.markdown("##### Leaderboard snapshot")
        try:
            from extra_features import load_ratings
            _lr = load_ratings()
            rows = sorted(
                ((k, int(v.get("elo", 1000)), int(v.get("wins", 0)), int(v.get("losses", 0))) for k, v in _lr.items()),
                key=lambda x: -x[1],
            )[:12]
            if rows:
                for name, elo, w, l in rows:
                    st.write(f"**{name}** · {elo} · W{w}/L{l}")
            else:
                st.caption("No rated games yet.")
        except Exception:
            st.caption("Ratings module offline.")

    with st.expander("🎬 Events & cutscenes", expanded=False):
        st.caption("Trigger narrative beats for yourself or broadcast site-wide flashes.")
        ev = st.selectbox(
            "Event",
            [
                "Voss file cutscene",
                "Lab complete flash",
                "Shadow contact whisper",
                "Chess residual analysis unlock",
                "Custom MOTD pulse",
                "Quiet hour",
                "Site violet storm",
            ],
            key="owner_event_pick",
        )
        custom_msg = st.text_input("Custom line (for MOTD / flash)", key="owner_event_msg", placeholder="Optional message")
        e1, e2 = st.columns(2)
        with e1:
            if st.button("Play for me", key="owner_event_self", type="primary", use_container_width=True):
                if ev == "Voss file cutscene":
                    st.session_state.voss_file_unlocked = True
                    st.session_state.voss_cutscene_stage = 0
                    st.session_state.view = "voss_file"
                    st.rerun()
                elif ev == "Lab complete flash":
                    st.session_state["_egg_flash"] = custom_msg or "All six lab fragments secured. Theme unlocked: Voss Static."
                    st.session_state["_glitch_flash"] = st.session_state["_egg_flash"]
                    st.success("Flash queued.")
                elif ev == "Shadow contact whisper":
                    st.session_state["_egg_flash"] = custom_msg or "Something on the residual line answered with your name."
                    st.success("Whisper queued.")
                elif ev == "Chess residual analysis unlock":
                    st.session_state["feat_chess_analysis"] = True
                    st.success("Chess analysis flag set for this session.")
                elif ev == "Custom MOTD pulse":
                    try:
                        cur = dict(site_effects_load())
                        cur["announce_enabled"] = True
                        cur["announce_text"] = custom_msg or "Meridium pulse."
                        cur["announce_style"] = "violet"
                        import uuid as _uuid
                        cur["announce_id"] = _uuid.uuid4().hex[:10]
                        site_effects_save(cur)
                        st.success("MOTD live.")
                    except Exception as _e:
                        st.error(str(_e))
                elif ev == "Quiet hour":
                    try:
                        cur = dict(site_effects_load())
                        cur["quiet_mode"] = True
                        site_effects_save(cur)
                        st.success("Quiet mode on.")
                    except Exception as _e:
                        st.error(str(_e))
                elif ev == "Site violet storm":
                    try:
                        cur = dict(site_effects_load())
                        fx = dict(cur.get("fx") or {})
                        fx["glitch_text"] = True
                        fx["violet_storm"] = True
                        cur["fx"] = fx
                        site_effects_save(cur)
                        st.success("Violet storm FX on.")
                    except Exception as _e:
                        st.error(str(_e))
        with e2:
            if st.button("Secure all 3 Voss markers (self)", key="owner_voss_all", use_container_width=True):
                st.session_state.glitches_found = ["home", "lab", "pixel"]
                st.session_state.voss_file_unlocked = True
                st.session_state.voss_cutscene_stage = 0
                st.success("Markers secured. Open Voss file when ready.")

        st.markdown("##### Cutscene jump")
        if st.button("▶ Open Voss residual file now", key="owner_open_voss", use_container_width=True):
            st.session_state.voss_file_unlocked = True
            st.session_state.voss_cutscene_stage = 0
            st.session_state.view = "voss_file"
            st.rerun()
'''

    marker = '    st.stop()\n\n\nif st.session_state.view == "owner_room":'
    if marker in code:
        code = code.replace(marker, chess_block + "\n    st.stop()\n\n\nif st.session_state.view == \"owner_room\":", 1)
        return code

    marker2 = 'if st.session_state.view == "owner_room":'
    if marker2 in code and "owner_chess_user" not in code:
        idx = code.find(marker2)
        prev = code.rfind("    st.stop()", 0, idx)
        if prev >= 0:
            code = code[:prev] + chess_block + "\n" + code[prev:]
            return code

    return code


def apply_chess_page_fixes(code: str) -> str:
    """Small chess-page reliability fixes applied to the bootstrapped app source."""
    if "Meridium Chess · stable" not in code:
        for old, new in (
            (
                'if st.session_state.view == "chess":',
                'if st.session_state.view == "chess":  # Meridium Chess · stable',
            ),
            (
                "if st.session_state.view == 'chess':",
                "if st.session_state.view == 'chess':  # Meridium Chess · stable",
            ),
        ):
            if old in code:
                code = code.replace(old, new, 1)
                break
    broken = 'if st.session_state.view == "chess"  # Meridium Chess · stable:'
    if broken in code:
        code = code.replace(
            broken,
            'if st.session_state.view == "chess":  # Meridium Chess · stable',
            1,
        )
    broken2 = "if st.session_state.view == 'chess'  # Meridium Chess · stable:"
    if broken2 in code:
        code = code.replace(
            broken2,
            "if st.session_state.view == 'chess':  # Meridium Chess · stable",
            1,
        )
    return code
