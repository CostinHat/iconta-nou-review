"""
core/pdf_fonturi.py — SURSA UNICA pentru fonturile din PDF-uri (reportlab).

REGULA PERMANENTA: orice PDF nou foloseste fonturile de aici, NICIODATA
Helvetica/Times/Courier (nu au diacritice romanesti -> patrate in PDF).

Utilizare:
    from core.pdf_fonturi import init_fonturi, FONTURI
    init_fonturi()                       # o data, la inceputul generarii
    regular, bold = FONTURI["sans"]      # sau "serif" / "mono"

Fonturile DejaVu au setul complet de diacritice (a i s t â). Text UTF-8 direct,
FARA transliterare.
"""
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TTF

_DEJAVU_DIR = "/usr/share/fonts/truetype/dejavu"
_INIT = False

# nume logic -> (font regular, font bold), toate DejaVu (cu diacritice)
FONTURI = {
    "sans": ("DejaVuSans", "DejaVuSans-Bold"),
    "serif": ("DejaVuSerif", "DejaVuSerif-Bold"),
    "mono": ("DejaVuSansMono", "DejaVuSansMono-Bold"),
}

_PERECHI = [
    ("DejaVuSans", "DejaVuSans.ttf"),
    ("DejaVuSans-Bold", "DejaVuSans-Bold.ttf"),
    ("DejaVuSerif", "DejaVuSerif.ttf"),
    ("DejaVuSerif-Bold", "DejaVuSerif-Bold.ttf"),
    ("DejaVuSansMono", "DejaVuSansMono.ttf"),
    ("DejaVuSansMono-Bold", "DejaVuSansMono-Bold.ttf"),
]


def init_fonturi():
    """Inregistreaza fonturile DejaVu o singura data (idempotent)."""
    global _INIT
    if _INIT:
        return
    for nume, fis in _PERECHI:
        try:
            _pm.registerFont(_TTF(nume, _DEJAVU_DIR + "/" + fis))
        except Exception:
            pass
    _INIT = True


def font(cheie="sans"):
    """Intoarce (regular, bold) pentru cheia data; default sans."""
    return FONTURI.get(cheie, FONTURI["sans"])
