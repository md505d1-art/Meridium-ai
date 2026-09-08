"""Lab view — thin wrapper; base app also has builtin fallback."""
from __future__ import annotations


def render_lab():
    """Render observation lab. Prefer builtin rich lab via raising to trigger fallback? No — provide simple UI."""
    import streamlit as st

    st.markdown("### Observation Lab")
    st.caption("Residual instruments · hotspots · door channel")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Home", key="lab_view_home", use_container_width=True):
            st.session_state.view = "home"
            st.rerun()
    with c2:
        if st.button("Open Nadir door path", key="lab_view_nadir", use_container_width=True):
            if st.session_state.get("lab_door_unlocked") or st.session_state.get("archive_key"):
                st.session_state.view = "nadir"
                st.rerun()
            else:
                st.warning("Door sealed — recover the residual / archive key first.")

    st.markdown("---")
    st.write(
        "The full interactive lab (hotspots, fragments, residual dial) runs from the "
        "built-in lab path when this module is not used. Use the main Lab entry from home/menu."
    )

    # Glitch marker convenience
    try:
        found = list(st.session_state.get("glitches_found") or [])
        st.caption("Markers secured: " + (", ".join(found) if found else "none yet"))
    except Exception:
        pass

    return None
