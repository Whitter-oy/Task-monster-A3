"""Game icons, supplied monsters and generated expressions embedded for offline use."""

import base64
from functools import lru_cache
from pathlib import Path
from game import CATEGORIES


def gem_svg():
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" aria-hidden="true"><path d="M12 5 L36 5 L45 19 L24 44 L3 19Z" fill="#ae78fa" stroke="#35234d" stroke-width="3" stroke-linejoin="round"/><path d="M12 5 L18 19 L3 19 M36 5 L30 19 L45 19 M18 19 L24 44 L30 19Z" fill="#d6b1ff" stroke="#7947bd" stroke-width="2"/><path d="M12 5 L36 5 L30 19 L18 19Z" fill="#ead4ff"/><path d="M8 18 L12 11" stroke="white" stroke-width="3" stroke-linecap="round"/></svg>'


def star_svg(filled=True):
    fill = "#ffce5a" if filled else "#786a83"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" aria-hidden="true"><path d="M24 3 L30 16 L45 18 L34 29 L37 44 L24 37 L11 44 L14 29 L3 18 L18 16Z" fill="{fill}" stroke="#352637" stroke-width="3" stroke-linejoin="round"/><path d="M24 9 L27 19 L37 20" fill="none" stroke="#fff2b1" stroke-width="2" stroke-linecap="round"/></svg>'


def remove_svg():
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><path d="M8 9 L10 27 L23 27 L25 9 M5 8 L28 8 M12 8 L12 4 L21 4 L21 8 M14 13 L14 23 M20 13 L20 23" fill="none" stroke="#ffe0e5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def navigation_svg(page):
    """Small original game icons for the three navigation tabs."""
    if page == "home":
        drawing = '<path d="M15 9 L24 11 L52 42 L43 51 L12 20Z" fill="#d8f3ff"/><path d="M49 9 L40 11 L12 42 L21 51 L52 20Z" fill="#fff8cd"/><path d="M13 36 L27 50 L23 54 L9 40Z" fill="#ffcb46"/><path d="M37 50 L51 36 L55 40 L41 54Z" fill="#ffcb46"/><path d="M9 48 L16 55 M48 55 L55 48" stroke="#7ac7b1" stroke-width="9"/><path d="M20 16 L44 43 M44 16 L20 43" stroke="white" stroke-width="2"/>'
    elif page == "create":
        drawing = '<path d="M16 9 L48 9 L48 50 Q48 56 42 56 L15 56 L15 19 L9 19 Q6 9 16 9Z" fill="#ffdb78"/><path d="M9 19 L22 19 L22 14 Q22 7 15 9 M15 45 L39 45 L39 50 Q39 57 47 55" fill="#eaa447"/><path d="M28 22 L40 22 M28 29 L40 29" stroke="#be7739" stroke-width="3"/><circle cx="43" cy="42" r="14" fill="#8fd652"/><path d="M43 35 L43 49 M36 42 L50 42" stroke="white" stroke-width="5"/>'
    else:
        drawing = '<path d="M32 5 L44 12 L56 11 L54 38 Q52 52 32 60 Q12 52 10 38 L8 11 L20 12Z" fill="#ffd35c"/><path d="M32 13 L41 19 L48 18 L46 37 Q45 44 32 51 Q19 44 18 37 L16 18 L23 19Z" fill="#6bccec"/><path d="M32 23 L36 31 L45 32 L38 38 L40 47 L32 42 L24 47 L26 38 L19 32 L28 31Z" fill="#fff4cc"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><g stroke="#211b32" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">{drawing}</g></svg>'


@lru_cache(maxsize=19)
def image_data(filename):
    data = (Path(__file__).resolve().parent / "assets" / "monsters" / filename).read_bytes()
    return "data:image/webp;base64," + base64.b64encode(data).decode()


def monster_group_svg():
    return f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="All six Task Monster characters" viewBox="0 0 1254 1254"><image href="{image_data("group.webp")}" width="1254" height="1254"/></svg>'


def monster_state(damage=0, trophy=False):
    """Damage is the completed-step fraction, so undo restores the prior state."""
    if trophy:
        return "collected"
    if damage >= .65:
        return "weak"
    if damage > 0:
        return "hurt"
    return "healthy"


def monster_svg(category, seed="", damage=0, trophy=False):
    """Select real expression artwork using the same HP source as the health bar."""
    name = CATEGORIES[category][0]
    state = monster_state(damage, trophy)
    suffix = f"-{state}" if state in ("hurt", "weak") else ""
    filename = name.lower().replace(" ", "-") + suffix + ".webp"
    tilt = -3 if state == "weak" else 0
    sparkle = '<path d="M263 26L268 38L280 43L268 48L263 60L258 48L246 43L258 38Z" fill="#ffe08a" stroke="#30203c" stroke-width="2"/>' if trophy else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{name} · {state}" data-monster-state="{state}" viewBox="0 0 300 260"><g transform="rotate({tilt} 150 140)"><image href="{image_data(filename)}" width="300" height="260" preserveAspectRatio="xMidYMid meet"/></g>{sparkle}</svg>'
