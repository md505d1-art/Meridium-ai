"""Meridium extra features pack."""
from __future__ import annotations
import hashlib, json, zlib, base64
from datetime import date
from pathlib import Path

# Board JS extras (sounds, PGN, theme, mobile CSS) — packed
_JS_EXTRAS = zlib.decompress(base64.b64decode(
    "eJztWUtv4zYQ/i8C3RpIWqRsybZ8yAZosUCbQ5FDgR4WQWHaYhOVRJWU4wTIf99ZUrJfo/W6QJFfKIoczhDfN8PhjDj+"
    "8vXL1y+XL5eLy8WL5cvV4vLqcnH5cnn5crm4ulxcXq4ul1eLy6vLxeXXxU+fL3/6fPnT5eLy6nL5dfHT58ufP1/+dLm4"
    "/Lr46fPlz58vf7pcXH5d/PT58ufPlz9dLi6/Ln76fPnz58ufLheXXxc/fb78+fPlT5eLy6+Lnz5f/nz58+Xi8uvi0+fL"
    "nz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKn"
    "y8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8u"
    "fvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+f"
    "L3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi"
    "8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99"
    "vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/"
    "XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl1"
    "8dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+"
    "fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4X"
    "l18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp"
    "8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f778"
    "6XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uv"
    "i58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny"
    "58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5"
    "uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VP"
    "ny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPn"
    "y58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+"
    "Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+X"
    "P3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VP"
    "l4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5+"
    "+nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/"
    "X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy"
    "6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+"
    "/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/"
    "ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx"
    "0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78"
    "+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10u"
    "Lr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz"
    "5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz5"
    "0+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5df"
    "Fz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLn"
    "z5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Oly"
    "cfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4uf"
    "Pl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fL"
    "ny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8"
    "uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/"
    "f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+X"
    "i8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl38"
    "9Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f"
    "/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl"
    "18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8"
    "+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6"
    "XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvi"
    "p8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz5"
    "8+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4u"
    "vy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPn"
    "y58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz"
    "5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18X"
    "P32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XP"
    "ny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx"
    "+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+"
    "X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+X"
    "P10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6"
    "+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9/"
    "/nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58u"
    "F5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0"
    "+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++"
    "/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vL"
    "r4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz5"
    "8+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50"
    "ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Kn"
    "z5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz"
    "5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxc"
    "fl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fL"
    "nz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKn"
    "y8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8u"
    "fvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+f"
    "L3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi"
    "8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99"
    "vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/"
    "XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl1"
    "8dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+"
    "fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4X"
    "l18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp"
    "8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f778"
    "6XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uv"
    "i58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny"
    "58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5"
    "uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VP"
    "ny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPn"
    "y58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+"
    "Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+X"
    "P3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VP"
    "l4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5+"
    "+nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/"
    "X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy"
    "6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+"
    "/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/"
    "ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx"
    "0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78"
    "+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10u"
    "Lr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz"
    "5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz5"
    "0+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5df"
    "Fz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLn"
    "z5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Oly"
    "cfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4uf"
    "Pl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fL"
    "ny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8"
    "uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/"
    "f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+X"
    "i8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl38"
    "9Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f"
    "/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl"
    "18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8"
    "+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6"
    "XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvi"
    "p8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz5"
    "8+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4u"
    "vy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPn"
    "y58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz"
    "5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18X"
    "P32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XP"
    "ny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx"
    "+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+"
    "X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+X"
    "P10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6"
    "+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9/"
    "/nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58u"
    "F5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0"
    "+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++"
    "/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vL"
    "r4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz5"
    "8+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50"
    "ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Kn"
    "z5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz"
    "5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxc"
    "fl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fL"
    "nz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKn"
    "y8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8u"
    "fvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+f"
    "L3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi"
    "8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99"
    "vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/"
    "XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl1"
    "8dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+"
    "fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4X"
    "l18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp"
    "8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f778"
    "6XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uv"
    "i58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny"
    "58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5"
    "uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VP"
    "ny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPn"
    "y58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+"
    "Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+X"
    "P3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VP"
    "l4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5+"
    "+nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/"
    "X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy"
    "6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+"
    "/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/"
    "ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx"
    "0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78"
    "+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10u"
    "Lr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz"
    "5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz5"
    "0+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5df"
    "Fz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLn"
    "z5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Oly"
    "cfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4uf"
    "Pl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fL"
    "ny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8"
    "uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/"
    "f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+X"
    "i8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl38"
    "9Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f"
    "/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl"
    "18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8"
    "+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6"
    "XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvi"
    "p8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz5"
    "8+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4u"
    "vy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPn"
    "y58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz"
    "5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18X"
    "P32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XP"
    "ny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx"
    "+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+"
    "X/78+fKny8Xl18VPny9//nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+X"
    "P10uLr8ufvp8+fPny58uF5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6"
    "+Onz5c+fL3+6XFx+Xfz0+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9/"
    "/nz50+Xi8uvip8+XP3++/Olycfl18dPny58/X/50ubj8uvjp8+XPny9/ulxcfl389Pny58+XP10uLr8ufvp8+fPny58u"
    "F5dfFz99vvz58+VPl4vLr4ufPl/+fPnz5eLy6+Knz5c/f7786XJx+XXx0+fLnz9f/nS5uPy6+Onz5c+fL3+6XFx+Xfz0"
    "+fLnz5c/XS4uvy5++nz58+fLny4Xl18XP32+/Pnz5U+Xi8uvi58+X/78+fKny8Xl18VPny9"
)).decode()

def _dir():
    d = Path(__file__).resolve().parent / "data" / "meridium_extra"
    d.mkdir(parents=True, exist_ok=True)
    return d

def get_rating(user="anon"):
    p = _dir() / "ratings.json"
    r = json.loads(p.read_text()) if p.exists() else {}
    return int(r.get(user or "anon", {}).get("elo", 1000))

def update_rating(user, won, opp_elo=1000):
    user = user or "anon"
    p = _dir() / "ratings.json"
    r = json.loads(p.read_text()) if p.exists() else {}
    e = r.get(user, {"elo": 1000, "wins": 0, "losses": 0})
    elo = int(e.get("elo", 1000))
    exp = 1 / (1 + 10 ** ((opp_elo - elo) / 400))
    elo = max(100, int(round(elo + 32 * ((1.0 if won else 0.0) - exp))))
    e["elo"] = elo
    e["wins" if won else "losses"] = int(e.get("wins" if won else "losses", 0)) + 1
    r[user] = e
    p.write_text(json.dumps(r, indent=2))
    return elo

_PUZ = [
    ("White to move — mate in 1", "Back rank", "Back-rank mate", "Gotham Chess", "THE ROOOOOOOOOOOOOOOOOOOOOK finishes it."),
    ("White to move — win material", "Fork", "Knight fork", "Hikaru", "Chat is this real? Free queen."),
    ("Black to move — equalize", "Trade", "Trade queens", "Magnus", "Simple is strong."),
    ("White to move — discovery", "Tempo", "Discovered attack", "Naroditsky", "The discovery wins material."),
    ("Black to move — tactic", "Pin", "Exploit the pin", "Anna Cramling", "You got this!!"),
    ("White to move — sacrifice?", "h7", "Greek gift idea", "Fabi", "Calculate everything."),
    ("Black to move — resource", "In-between", "Zwischenzug", "Eric Rosen", "Hello everyone! Beautiful."),
]

def puzzle_of_day():
    day = date.today().isoformat()
    i = int(hashlib.md5(day.encode()).hexdigest(), 16) % len(_PUZ)
    a, h, ans, c, line = _PUZ[i]
    return {"day": day, "fen_desc": a, "hint": h, "answer": ans, "coach": c, "line": line}

_SIG = [
    "Residual hum on Corridor 4.",
    "Note under the lab door: the board remembers unplayed moves.",
    "Static resolves: KEEP THE CENTER.",
    "Tactical accuracy up after Soju session.",
    "Copper vespers fragment unlocked overnight.",
    "Furnace thermometer spiked during online match.",
    "Lobby whisper: challenge code starts with R.",
    "Dossier: love is not a residual anomaly.",
    "Puzzle vault rotated — back-rank motifs.",
    "Sticky note from Gotham: THE ROOK.",
]

def daily_signal():
    day = date.today().isoformat()
    i = int(hashlib.md5(("sig:" + day).encode()).hexdigest(), 16) % len(_SIG)
    return _SIG[i]

DEFAULT_UNLOCKED = {"Soju", "Gotham Chess", "Hikaru"}
ALL_COACHES = ["Soju", "Gotham Chess", "Hikaru", "Magnus", "Anna Cramling", "Botez", "Fabi", "Naroditsky", "Eric Rosen"]
UNLOCK_RULES = {
    "Magnus": "Win 3 games",
    "Anna Cramling": "Solve today's puzzle",
    "Botez": "Join online match",
    "Fabi": "Reach 1100 rating",
    "Naroditsky": "Mark PGN export",
    "Eric Rosen": "Residual terminal unlock",
}

def unlocked_coaches(ss):
    u = set(DEFAULT_UNLOCKED) | set(ss.get("unlocked_coaches") or [])
    return [c for c in ALL_COACHES if c in u]

def try_unlock(ss, coach):
    cur = set(ss.get("unlocked_coaches") or [])
    if coach in cur or coach in DEFAULT_UNLOCKED:
        return False
    cur.add(coach)
    ss["unlocked_coaches"] = list(cur)
    return True

def apply_extra_to_html(html, coach_name="Soju"):
    theme = {"Gotham Chess": "gotham", "Hikaru": "hikaru", "Magnus": "magnus", "Anna Cramling": "anna", "Botez": "botez", "Fabi": "fabi", "Naroditsky": "danya", "Eric Rosen": "eric"}.get(coach_name or "Soju", "soju")
    boot = "<script>setTimeout(function(){try{window.__merTheme&&window.__merTheme('%s')}catch(e){}},50);</script>" % theme
    inj = _JS_EXTRAS + boot
    return html.replace("</body>", inj + "</body>", 1) if "</body>" in html else html + inj

def apply_extra_features(code: str) -> str:
    if "Daily residual signal" not in code:
        home = (
            "\n    try:\n"
            "        from extra_features import daily_signal as _mds\n"
            "        st.info(\"📡 Daily residual signal · \" + _mds())\n"
            "    except Exception:\n"
            "        pass\n"
            "    with st.expander(\"💻 Residual terminal\", expanded=False):\n"
            "        st.caption(\"help · scan · dossier · unlock · signal · clear\")\n"
            "        if \"term_log\" not in st.session_state:\n"
            "            st.session_state.term_log = [\"MERIDIUM TERM v0.9\"]\n"
            "        _tc = st.text_input(\">\", key=\"term_cmd\", label_visibility=\"collapsed\")\n"
            "        if st.button(\"Run\", key=\"term_run\") and _tc:\n"
            "            _c = _tc.strip().lower(); _log = st.session_state.term_log; _log.append(\"> \" + _tc)\n"
            "            if _c == \"help\": _log.append(\"help scan dossier unlock signal clear\")\n"
            "            elif _c == \"scan\": _log.append(\"Anomaly in Corridor 4.\")\n"
            "            elif _c == \"dossier\": _log.append(\"Callaghan margin note restored.\")\n"
            "            elif _c == \"unlock\":\n"
            "                from extra_features import try_unlock as _tu\n"
            "                if _tu(st.session_state, \"Eric Rosen\"): st.toast(\"Unlocked: Eric Rosen!\", icon=\"🎩\"); _log.append(\"Unlocked Eric Rosen\")\n"
            "                else: _log.append(\"Already unlocked\")\n"
            "            elif _c == \"signal\":\n"
            "                from extra_features import daily_signal as _ds; _log.append(_ds())\n"
            "            elif _c == \"clear\": st.session_state.term_log = [\"MERIDIUM TERM v0.9\"]\n"
            "            else: _log.append(\"Unknown. Type help.\")\n"
            "            st.session_state.term_log = _log[-30:]; st.rerun()\n"
            "        for _ln in st.session_state.get(\"term_log\") or []: st.text(_ln)\n"
        )
        for m in ['if st.session_state.view == "home":', "if st.session_state.view == 'home':"]:
            if m in code:
                code = code.replace(m, m + home, 1)
                break
    if "Puzzle of the day" not in code:
        panel = (
            "\n    try:\n"
            "        from extra_features import puzzle_of_day as _pod, get_rating as _gr, update_rating as _ur, unlocked_coaches as _uc, try_unlock as _tu, UNLOCK_RULES as _UR\n"
            "        _user = st.session_state.get(\"username\") or \"anon\"\n"
            "        st.caption(\"⭐ Meridium rating: **\" + str(_gr(_user)) + \"**\")\n"
            "        with st.expander(\"🧩 Puzzle of the day\", expanded=False):\n"
            "            _pz = _pod(); st.markdown(\"**\" + _pz[\"fen_desc\"] + \"**\"); st.caption(_pz[\"coach\"] + \" — \" + _pz[\"line\"])\n"
            "            if st.button(\"Show hint\", key=\"pz_hint\"): st.info(_pz[\"hint\"])\n"
            "            if st.button(\"Show idea\", key=\"pz_ans\"):\n"
            "                st.success(_pz[\"answer\"])\n"
            "                if _tu(st.session_state, \"Anna Cramling\"): st.toast(\"Unlocked: Anna Cramling!\", icon=\"✨\")\n"
            "        with st.expander(\"🔓 Coach unlocks\", expanded=False):\n"
            "            _have = set(_uc(st.session_state))\n"
            "            for _n, _r in _UR.items(): st.write((\"✅\" if _n in _have else \"🔒\") + \" **\" + _n + \"** — \" + _r)\n"
            "            _a, _b, _c = st.columns(3)\n"
            "            if _a.button(\"I won\", key=\"ul_win\"):\n"
            "                st.session_state[\"_wins\"] = int(st.session_state.get(\"_wins\") or 0) + 1; _ur(_user, True)\n"
            "                if st.session_state[\"_wins\"] >= 3 and _tu(st.session_state, \"Magnus\"): st.toast(\"Unlocked: Magnus!\", icon=\"👑\")\n"
            "                if _gr(_user) >= 1100 and _tu(st.session_state, \"Fabi\"): st.toast(\"Unlocked: Fabi!\", icon=\"🎯\")\n"
            "            if _b.button(\"Mark PGN\", key=\"ul_pgn\"):\n"
            "                if _tu(st.session_state, \"Naroditsky\"): st.toast(\"Unlocked: Naroditsky!\", icon=\"📚\")\n"
            "            if _c.button(\"Joined online\", key=\"ul_on\"):\n"
            "                if _tu(st.session_state, \"Botez\"): st.toast(\"Unlocked: Botez!\", icon=\"🔥\")\n"
            "        with st.expander(\"✍️ Custom coach\", expanded=False):\n"
            "            _cn = st.text_input(\"Name\", key=\"cc_name\"); _ct = st.text_input(\"Tagline\", key=\"cc_tag\"); _cl = st.text_area(\"Line\", key=\"cc_line\")\n"
            "            if st.button(\"Save coach\", key=\"cc_save\") and _cn:\n"
            "                _customs = st.session_state.get(\"custom_coaches\") or {}; _customs[_cn] = {\"title\": _cn, \"tagline\": _ct or \"\", \"line\": _cl or \"Nice.\"}\n"
            "                st.session_state.custom_coaches = _customs\n"
            "                _ul = set(st.session_state.get(\"unlocked_coaches\") or []); _ul.add(_cn); st.session_state.unlocked_coaches = list(_ul); st.success(\"Saved \" + _cn)\n"
            "        with st.expander(\"🔁 Results & rating\", expanded=False):\n"
            "            _r1, _r2 = st.columns(2)\n"
            "            if _r1.button(\"I won — rate\", key=\"rate_w\"): st.success(\"Rating \" + str(_ur(_user, True)))\n"
            "            if _r2.button(\"I lost — rate\", key=\"rate_l\"): st.warning(\"Rating \" + str(_ur(_user, False)))\n"
            "    except Exception:\n"
            "        pass\n"
        )
        if 'st.caption("vs " + st.session_state.chess_opponent' in code:
            idx = code.find('st.caption("vs " + st.session_state.chess_opponent')
            end = code.find("\n", idx)
            code = code[: end + 1] + panel + code[end + 1 :]
        else:
            code = code.replace("st.components.v1.html(", panel + "\n    st.components.v1.html(", 1)
    if "apply_extra_to_html as _mer_xhtml" not in code:
        extra = (
            "\n        try:\n"
            "            from extra_features import apply_extra_to_html as _mer_xhtml\n"
            "            html = _mer_xhtml(html, st.session_state.get(\"chess_coach\", \"Soju\"))\n"
            "        except Exception:\n"
            "            pass\n"
        )
        needle = (
            '            html = _mer_apply_coach_html(html, st.session_state.get("chess_coach", "Soju"))\n'
            '        except Exception:\n'
            '            pass\n'
        )
        if needle in code:
            code = code.replace(needle, needle + extra, 1)
        else:
            m2 = 'html = html.replace("__SOJU_THINK__", _b64img("soju_think.jpg"))'
            if m2 in code:
                code = code.replace(m2, m2 + extra, 1)
    return code
