"""core/pdf_util.py — utilitare comune de formatare pentru text destinat UTILIZATORULUI
(PDF-uri + orice mesaj/temei/descriere construit in backend). SURSA UNICA pentru formatare
numerica SI de data romaneasca — Design System cap.7 (sume) + cap.4 (date). Echivalentul
Python al bani()/dataRo() din static/js/api.js: o singura regula, doua limbaje."""
from decimal import Decimal, ROUND_HALF_UP
import datetime as _dt

_LUNI_RO = ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
            "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"]


def bani(x, mon=""):
    """Format romanesc: 1.234,56 (nu 1,234.56 american)."""
    if x is None:
        return ""
    n = Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    s = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {mon}".strip()


def moneda_scrisa(m):
    """[lotul 12, C158] Moneda pentru om: „lei” pentru RON (sau fără monedă), codul altfel — oglinda `monedaScrisa` din facturi_ecran.js."""
    return "lei" if not m or str(m).strip().upper() == "RON" else str(m).strip().upper()


def sold(v):
    """[lotul 11, C100] Soldul unui cont pentru om: „debitor 1.234,56 lei” / „creditor 500,00 lei” — nu „-500,00 lei” (semnul e al
    calculului, nu al contabilului). Sursa unică: refuzul importului soldurilor pe parteneri și auditul de preluare."""
    v = Decimal(str(v or 0))
    if v == 0:
        return bani(v, "lei")   # un sold zero n-are fel
    return "%s %s" % ("debitor" if v > 0 else "creditor", bani(abs(v), "lei"))


def diferenta(ce, declarat, recalculat, dif=None, sursa="în declarație"):
    """[Retest 2 pct.2] Un rând de diferență al porților de reconciliere, în cuvintele contabilului: „TVA colectată 21%:
    în declarație 9.999,00 lei, recalculat 1.500,00 lei (diferență 8.499,00 lei)” — nu „generator=9999 vs cale2=1500”. Sursa
    unică pentru toate porțile (D100, D101, D112, D205, D300, D301, D390, D394, D406)."""
    if dif is None:
        dif = Decimal(str(declarat)) - Decimal(str(recalculat))
    return "%s: %s %s, recalculat %s (diferență %s)" % (ce, sursa, bani(declarat, "lei"), bani(recalculat, "lei"), bani(dif, "lei"))


def cantitate(x, um=""):
    """Cantitate pentru om: „2 buc”, „1,5 kg”, „0,125 l” — fără zecimalele de prisos ale coloanei NUMERIC(12,3) („x2.000”).
    Oglinda lui `cantitate()` din api.js (comanda Costin 05.10.2026 pct.9)."""
    if x is None or x == "":
        return ""
    n = Decimal(str(x)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP).normalize()
    s = f"{n:,f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {um or ''}".strip()


def numar_cu_serie(serie, numar):
    """Numărul unui document cu seria în față, o singură dată. Sursa UNICĂ (gard `core/test_flux_factura_f1_c.py`).

    Numărul unei facturi emise conține deja seria (`facturi_api`: număr = serie + număr; măsurat 05.10.2026: 19 din 19 facturi
    emise cu serie, în baza de test). Compus „serie + număr” peste el ieșea „FCTFCT12” — în Registrul-jurnal, la bancă și în
    ID-ul e-Factura către ANAF. Seria se pune în față numai când numărul n-o poartă deja."""
    nr, s = str(numar if numar is not None else ""), str(serie or "")
    return nr if (not s or nr.startswith(s)) else s + nr


#: [lotul 11, deficiența 443] separatorii de la capătul seriei („KAI-”) nu intră în textul afișat: „KAI nr. 12”, nu „KAI- nr. 12”
_SEPARATORI_SERIE = " -/._"


def serie_nr(serie, numar):
    """„F6 nr. 1” — seria și numărul unui document AFIȘATE SEPARAT, în orice text pe care îl citește omul (ecran, mesaj, PDF, descrierea
    notei). Sursa UNICĂ pentru afișare; oglinda JS e `numarCuSerie` din api.js.

    [lotul 11, deficiența 443, comanda Costin 11.1 pct.19, verbatim] „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”.
    Cauza: `numar_cu_serie` lipea seria de număr („F6” + „1” = „F61”, ambiguu cu seria „F” nr. 61), iar textul ăsta ajungea în
    Registrul jurnal, în refuzuri și în listele de facturi. Numărul unei facturi emise poartă deja seria în față („F1A3” în seria „F1A”):
    se taie, ca la `numar_in_serie`. Fără serie, numărul rămâne cum e („BA-1”, „12”).

    `numar_cu_serie` rămâne NUMAI pentru IDENTIFICATORUL documentului (ID-ul facturii în e-Factura, BT-1 / BT-25), unde ANAF primește un
    singur șir — garda `core/test_lot11_u0_serie_nr.py` numește locurile admise."""
    nr = str(numar if numar is not None else "").strip()
    s = str(serie or "").strip()
    if not s or s == "-":
        return nr
    if nr.upper().startswith(s.upper()):
        rest = nr[len(s):].lstrip(_SEPARATORI_SERIE)
        if rest:
            nr = rest
    s = s.rstrip(_SEPARATORI_SERIE) or s
    return "%s nr. %s" % (s, nr) if nr else s


def forme_lipite(serie, numar):
    """[lotul 11, 443 — datele existente; regula Costin 11.2 pct.3a: „Orice reparație acoperă și datele existente.”] Formele în care textele
    scrise ÎNAINTE de 443 purtau numărul documentului cu seria lipită: `numar_cu_serie` („F1A3”, „F61”) și seria lipită de mână peste
    numărul care o poartă deja („F6F61”, `contare_facturi` la diferența de preț a NIR-ului) — fără forma de acum (`serie_nr`). NUMAI ca să
    fie RECUNOSCUTE în datele existente (`jurnal_api.fara_serie_lipita`: core/migrare_serie_nr_descrieri.py și Registrul jurnal), nu ca să
    se scrie. Fără serie: nimic de recunoscut."""
    s = str(serie or "").strip()
    if not s or s == "-":
        return set()
    return {numar_cu_serie(serie, numar), s + str(numar if numar is not None else "").strip()} - {serie_nr(serie, numar), ""}


def numar_in_serie(serie, numar):
    """Numărul de ordine al unui document ÎN SERIA LUI (int), sau None dacă n-are cifre. Inversa lui `numar_cu_serie`, cu aceeași regulă:
    numărul unei facturi emise poate purta deja seria în față („F1A3” în seria „F1A” e numărul 3, nu 13). [08.10.2026, retest pct.6]
    Forma veche lua toate cifrele din număr — inclusiv cele ale seriei."""
    nr, s = str(numar if numar is not None else "").strip(), str(serie or "").strip()
    if s and s != "-" and nr.upper().startswith(s.upper()):
        nr = nr[len(s):]
    cifre = "".join(ch for ch in nr if ch.isdigit())
    return int(cifre) if cifre else None


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
