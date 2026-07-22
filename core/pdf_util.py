"""core/pdf_util.py — utilitare comune de formatare pentru text destinat UTILIZATORULUI
(PDF-uri + orice mesaj/temei/descriere construit in backend). SURSA UNICA pentru formatare
numerica SI de data romaneasca — Design System cap.7 (sume) + cap.4 (date). Echivalentul
Python al bani()/dataRo() din static/js/api.js: o singura regula, doua limbaje."""
from decimal import Decimal
import datetime as _dt

_LUNI_RO = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
            "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"]


def bani(x, mon=""):
    """Format romanesc: 1.234,56 (nu 1,234.56 american)."""
    if x is None:
        return ""
    n = Decimal(str(x)).quantize(Decimal("0.01"))
    s = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {mon}".strip()


def data_ro(d, stil="scurt"):
    """Format romanesc canonic pentru DATE afisate utilizatorului — oglinda dataRo din api.js
    (DS cap.4). Sursa UNICA in backend; NU se reimplementeaza strftime('%d.%m.%Y') local.
      stil 'scurt' (implicit): zz.ll.aaaa   ·   'lung': '11 iulie 2026'
      stil 'cu_ora': zz.ll.aaaa hh:mm       ·   'zi_luna': zz.ll
    Accepta date/datetime, string ISO ('yyyy-mm-dd' sau cu ora), None/'' -> ''.
    NU se foloseste pentru XML/SAF-T (ISO cerut de spec) sau exporturi cu format propriu al
    destinatiei (ex. WinMentor) — acolo formatul nu e ales de UI."""
    if d is None or d == "":
        return ""
    if isinstance(d, _dt.datetime):
        dt = d
    elif isinstance(d, _dt.date):
        dt = _dt.datetime(d.year, d.month, d.day)
    else:
        s = str(d)
        try:
            dt = _dt.datetime.fromisoformat(s[:19]) if len(s) > 10 else _dt.datetime.strptime(s[:10], "%Y-%m-%d")
        except ValueError:
            return str(d)
    zz, ll = "%02d" % dt.day, "%02d" % dt.month
    if stil == "lung":
        return "%d %s %d" % (dt.day, _LUNI_RO[dt.month - 1], dt.year)
    if stil == "cu_ora":
        return "%s.%s.%d %02d:%02d" % (zz, ll, dt.year, dt.hour, dt.minute)
    if stil == "zi_luna":
        return "%s.%s" % (zz, ll)
    return "%s.%s.%d" % (zz, ll, dt.year)
