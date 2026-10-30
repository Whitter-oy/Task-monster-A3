"""Original vector monsters drawn in code; no external artwork or font required."""

import hashlib
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


def monster_svg(category, seed="", damage=0, trophy=False):
    name, kind, color, shade = CATEGORIES[category]
    variant = int(hashlib.sha256(seed.encode()).hexdigest()[:6], 16)
    accent = ["#ffe49b", "#9ff6e5", "#ffbde5", "#ddd2ff"][variant % 4]
    tilt = -7 if damage >= 0.65 else (3 if damage > 0 else 0)
    outline = 'stroke="#211c35" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"'
    body = ""
    if kind == "slime":
        body = f'<path d="M62 198 Q40 156 74 122 Q82 61 136 75 Q189 51 210 118 Q250 132 230 189 Q215 220 174 215 L98 216Z" fill="{color}"/><path d="M76 174 Q97 202 130 192 Q182 214 222 172 L226 197 Q190 231 89 211Z" fill="{shade}" stroke="none"/><path d="M98 112 Q110 93 128 98" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="9"/>'
    elif kind == "owl":
        body = f'<path d="M75 192 Q50 150 76 90 L64 49 L113 74 Q150 59 184 77 L227 51 L216 107 Q238 168 210 197Z" fill="{color}"/><path d="M79 126 L49 181 L100 174 M213 125 L246 179 L196 175" fill="{shade}"/><path d="M116 168 Q147 145 182 169 L171 202 L122 202Z" fill="{accent}"/><path d="M96 207 L91 220 M112 208 L112 222 M182 210 L181 222 M196 207 L200 220" fill="none"/>'
    elif kind == "dragon":
        body = f'<path d="M77 137 L30 101 L40 163 L81 185 M210 137 L260 99 L247 169 L210 188" fill="{shade}"/><path d="M80 184 Q54 132 86 90 L83 52 L122 77 Q164 61 195 81 L226 60 L213 109 Q241 162 209 203 L99 210Z" fill="{color}"/><path d="M112 182 Q147 155 182 183 L177 214 L117 215Z" fill="{accent}"/><path d="M112 80 L116 52 L136 73 M175 73 L187 49 L194 84" fill="{accent}"/>'
    elif kind == "golem":
        body = f'<path d="M76 119 L43 135 L42 192 L89 203 M211 122 L249 139 L247 194 L205 205" fill="{shade}"/><path d="M86 70 L176 60 L214 91 L220 178 L194 209 L91 210 L69 178 L69 104Z" fill="{color}"/><path d="M89 209 L86 229 L119 230 L126 210 M171 211 L178 231 L210 228 L204 203" fill="{shade}"/><path d="M86 88 L132 95 L151 71 M204 173 L184 180 L193 200" fill="none" stroke="{shade}" stroke-width="6"/><path d="M131 178 L148 163 L166 178 L149 194Z" fill="{accent}"/>'
    elif kind == "plant":
        body = f'<path d="M114 89 Q65 56 84 31 Q127 27 143 77 Q157 26 204 36 Q217 76 164 92" fill="{shade}"/><path d="M80 178 Q47 153 55 124 Q92 113 104 158 M204 171 Q242 127 253 144 Q255 177 220 190" fill="{color}"/><path d="M81 168 Q63 83 140 79 Q217 70 219 154 L207 203 Q155 230 99 205Z" fill="{color}"/><path d="M104 187 Q150 166 196 189 L186 213 L116 213Z" fill="{accent}"/>'
    else:
        body = f'<path d="M75 202 Q58 190 70 161 L78 109 Q83 55 144 57 Q211 53 219 117 L224 164 Q252 191 221 212 L196 200 L174 219 L146 203 L120 219 L97 201 L78 218Z" fill="{color}"/><path d="M91 112 Q98 83 126 83" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="10"/><path d="M55 116 L44 103 M241 98 L255 87" fill="none" stroke="{accent}"/>'
    if trophy:
        eyes = '<path d="M106 135 Q118 120 130 135 M169 135 Q181 120 192 135" fill="none"/>'
    elif damage >= 0.65:
        eyes = '<path d="M106 125 L127 141 M127 125 L106 141 M169 125 L189 141 M189 125 L169 141" fill="none"/>'
    else:
        eyes = '<ellipse cx="118" cy="132" rx="13" ry="18" fill="#211c35"/><ellipse cx="180" cy="132" rx="13" ry="18" fill="#211c35"/><circle cx="121" cy="126" r="4" fill="white" stroke="none"/><circle cx="183" cy="126" r="4" fill="white" stroke="none"/>'
    mouth = '<path d="M137 155 Q150 168 163 155" fill="none"/>' if trophy else ('<path d="M139 162 Q150 147 161 162" fill="none"/>' if damage >= 0.65 else '<path d="M136 157 Q148 173 164 157Z" fill="#fff"/>')
    badge = f'<path d="M145 30 L152 14 L161 30 L180 24 L173 47 L128 47 L120 25Z" fill="{accent}"/>' if variant % 2 == 0 else f'<path d="M233 58 L238 44 L244 58 L257 64 L244 69 L238 83 L232 69 L219 64Z" fill="{accent}"/>'
    hurt = '<path d="M220 94 Q235 78 235 104 Q234 117 224 112Z" fill="#8feaff"/>' if damage > 0 and not trophy else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{name}" viewBox="0 0 300 260"><ellipse cx="150" cy="232" rx="85" ry="14" fill="#111022" opacity=".3"/><g transform="rotate({tilt} 150 160)" {outline}>{body}{eyes}{mouth}<ellipse cx="96" cy="154" rx="10" ry="5" fill="#ed7c9f" opacity=".6" stroke="none"/><ellipse cx="202" cy="154" rx="10" ry="5" fill="#ed7c9f" opacity=".6" stroke="none"/>{badge}{hurt}</g></svg>'
