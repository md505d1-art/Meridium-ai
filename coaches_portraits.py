"""Coach portrait data URIs (illustrated)."""
try:
    from coaches_portraits_a import PORTRAITS_A
except Exception:
    PORTRAITS_A = {}
try:
    from coaches_portraits_b import PORTRAITS_B
except Exception:
    PORTRAITS_B = {}
PORTRAITS = {**PORTRAITS_A, **PORTRAITS_B}
