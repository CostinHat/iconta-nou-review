"""core/pdf_util.py — utilitare comune generatoarelor PDF (reportlab).
Sursa unica pentru formatare numerica romaneasca, folosita de toate
generatoarele PDF (factura_pdf, documente_api, stat_plata_api) — Design System cap.7."""
from decimal import Decimal


def bani(x, mon=""):
    """Format romanesc: 1.234,56 (nu 1,234.56 american)."""
    if x is None:
        return ""
    n = Decimal(str(x)).quantize(Decimal("0.01"))
    s = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {mon}".strip()
