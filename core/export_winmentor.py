# -*- coding: utf-8 -*-
"""core/export_winmentor.py — F187: export facturi EMISE catre WinMENTOR.

WinMENTOR importa prin MENTOR > INTERNE > IMPORT DATE DIN ALTE APLICATII > Facturi iesire.
Format text INI (sectiuni [InfoPachet]/[Factura_N]/[Items_N]/[ArticoleNoi_<cod>]). Structura
verificata la sursa OFICIALA (download.winmentor.ro/.../22 Structuri import din alte aplicatii/,
Facturi clienti.pdf Rev.1.2 + Articole noi.pdf, extrase cu pdftotext 19.07.2026).

DOUA fisiere CO-LOCATE (WinMentor cauza articolul in nomenclator, altfel in Articole.txt din aceeasi
locatie, altfel importul esueaza - NU auto-creeaza):
  - Facturi.txt: antet pachet + o sectiune per factura + liniile (Items) referind un COD de articol.
  - Articole.txt: defineste articolele referite (cod DERIVAT determinist din descriere, CONSECVENT
    intre cele doua fisiere - daca diverg, WinMentor nu gaseste articolul).

REUTILIZEAZA conducta SAGA (export_saga.date_factura/facturi_emise_luna/_firma) - doar IESIREA difera.
Doar facturi EMISE cu status='emisa' (nu 'de_preluat'/'anulata'; facturi n-au status 'validata').

DEPENDENTA DE CONFIG (NU e self-contained ca SAGA - declarat explicit, DECIZII 19.07):
  WinMentor cere ca UM, clasa, gestiunea sa PRE-EXISTE in nomenclatorul cabinetului. v1 = facturi de
  SERVICII (Serviciu=D, ContServiciu=cont venit) + articole simple; Clasa/GestiuneImplicita GOALE (valide
  in spec). UM vine din TRANZACTIE (linia Facturi.txt), NU din Articole.txt (spec oficial - blogul gresea).
  simbol_clasa/simbol_gestiune/cont_serviciu = constante setabile per cabinet, default servicii.
  Stoc complex cu gestiune = v2. Round-trip real (import in WinMentor) = pending cabinet real (ca proba SPV).

MAPARE (decizii Costin 19.07): CodClient=CIF (tert_cui; cabinetul seteaza constanta "cod partener=cod
fiscal"); TipTVA=0 (intern standard; regimuri speciale=v2); SerieCarnet=facturi.serie, NrDoc=facturi.numar
(coloane existente); Localitate=gol; encoding Windows-1250 cu gard.
"""
import hashlib
from decimal import Decimal, ROUND_HALF_UP

REGULI = "2026.1"
MODUL = "export_winmentor"

# config default (servicii) - setabil per cabinet in v2
CONFIG_DEFAULT = {"serviciu": "D", "cont_serviciu": "704", "simbol_clasa": "", "simbol_gestiune": ""}


def _q(x):
    return Decimal(str(x or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _num(x):
    return format(_q(x), "f")


def _cant(c):
    v = Decimal(str(c or 0))
    s = format(v, "f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def _d_ro(d):
    """Data dd.mm.yyyy (formatul WinMentor). Accepta date sau str."""
    if d is None:
        return ""
    if hasattr(d, "strftime"):
        return d.strftime("%d.%m.%Y")
    return str(d)


# --- Windows-1250 cu gard (F187 #6): ș/ț moderne (virgula, U+0219/021B) NU sunt in cp1250;
#     se normalizeaza la ş/ţ (cedila, forma legacy WinMentor), apoi encode STRICT. Orice caracter
#     tot neencodabil -> EXCEPTIE cu context (NU byte gresit tacit - riscul BR-RO).
_RO_LEGACY = {"ș": "ş", "ț": "ţ",   # ș->ş, ț->ţ
              "Ș": "Ş", "Ț": "Ţ"}    # Ș->Ş, Ț->Ţ


def encode_1250(text, unde=""):
    t = "".join(_RO_LEGACY.get(ch, ch) for ch in (text or ""))
    try:
        return t.encode("cp1250")
    except UnicodeEncodeError as e:
        ch = t[e.start:e.end]
        raise ValueError("Caracter neencodabil in Windows-1250 (%r) la %s: %r. "
                         "WinMentor ar respinge fisierul - corecteaza textul." % (ch, unde or "text", t[:60]))


def cod_articol(descriere):
    """Cod de articol DETERMINIST din descriere: 'A' + 11 hex din sha1(descriere normalizata).
    Acelasi algoritm in Facturi.txt (Item) SI Articole.txt (definitie) - daca diverg, importul esueaza.
    NU descrierea bruta ca cod (codurile WinMentor au format alfanumeric fix)."""
    baza = (descriere or "").strip().lower()
    h = hashlib.sha1(baza.encode("utf-8")).hexdigest()[:11].upper()
    return "A" + h


# ---- serializere PURE (dict-uri -> text INI) ----

def _linii_valorizate(linii):
    """(cod, um, cant, pret_unitar, tva_valoare, descriere) per linie."""
    out = []
    for l in linii:
        cant = Decimal(str(l.get("cantitate") or 0))
        pret = Decimal(str(l.get("pret_unitar") or 0))
        cota = Decimal(str(l.get("cota_tva") or 0))
        tva = _q(cant * pret * cota / Decimal(100))
        out.append({"cod": cod_articol(l.get("descriere")), "um": l.get("um") or "BUC",
                    "cant": cant, "pret": pret, "tva": tva, "descriere": l.get("descriere") or ""})
    return out


def facturi_txt(firma, facturi, an, luna):
    """[InfoPachet] + o [Factura_N] + [Items_N] per factura. facturi = [(factura_dict, linii)].
    Intoarce STRING (encoding se face la scriere)."""
    L = ["[InfoPachet]", "AnLucru=%d" % an, "LunaLucru=%d" % luna,
         "Tipdocument=FACTURA IESIRE", "TotalFacturi=%d" % len(facturi)]
    for k, (f, linii) in enumerate(facturi, start=1):
        val = _linii_valorizate(linii)
        L.append("[Factura_%d]" % k)
        L.append("NrDoc=%s" % (f.get("numar") or ""))
        L.append("SerieCarnet=%s" % (f.get("serie") or ""))
        L.append("Data=%s" % _d_ro(f.get("data_emitere")))
        L.append("Scadenta=%s" % _d_ro(f.get("data_scadenta")))
        L.append("CodClient=%s" % (f.get("tert_cui") or ""))     # CIF (decizie #1)
        L.append("Localitate=")                                   # gol (decizie #5)
        L.append("TVAINCASARE=%s" % ("D" if firma.get("tva_la_incasare") else "N"))
        L.append("TaxareInversa=%s" % ("D" if f.get("taxare_inversa") else "N"))
        L.append("TipTVA=0")                                       # intern standard (decizie #3)
        L.append("ClasificareSAFT=380")                           # factura initiala
        L.append("TotalArticole=%d" % len(val))
        L.append("Operat=N")
        L.append("[Items_%d]" % k)
        for j, v in enumerate(val, start=1):
            L.append("Item_%d=%s;%s;%s;%s" % (j, v["cod"], v["um"], _cant(v["cant"]), _num(v["pret"])))
            L.append("Item_%d_TVA=%s" % (j, _num(v["tva"])))
    return "\n".join(L) + "\n"


def articole_txt(linii_toate, config=None):
    """[InfoPachet] + o [ArticoleNoi_<cod>] per articol DISTINCT (dedup pe cod). linii_toate = lista de
    linii (din toate facturile). config: serviciu/cont_serviciu/simbol_clasa/simbol_gestiune."""
    cfg = dict(CONFIG_DEFAULT, **(config or {}))
    vazute = {}
    for l in linii_toate:
        cod = cod_articol(l.get("descriere"))
        if cod not in vazute:
            vazute[cod] = l.get("descriere") or ""
    L = ["[InfoPachet]"]
    for cod, den in vazute.items():
        L.append("[ArticoleNoi_%s]" % cod)
        L.append("Denumire=%s" % den)
        L.append("Serviciu=%s" % cfg["serviciu"])
        L.append("ContServiciu=%s" % (cfg["cont_serviciu"] if cfg["serviciu"] == "D" else ""))
        L.append("GestiuneImplicita=%s" % cfg["simbol_gestiune"])
        L.append("Clasa=%s" % cfg["simbol_clasa"])
        L.append("PretVanzare=")
        L.append("TVAInclus=N")
    return "\n".join(L) + "\n"


# ---- orchestrator (reutilizeaza conducta SAGA) ----

def export_luna(conn, schema, an, luna, config=None):
    """Intoarce {'Facturi.txt': bytes, 'Articole.txt': bytes} (cp1250) pentru facturile EMISE cu
    status='emisa' din luna. Gol (None) daca nicio factura. Reutilizeaza export_saga.facturi_emise_luna
    (cu status='emisa') + date_factura."""
    from core import export_saga as _xs
    ids = _xs.facturi_emise_luna(conn, schema, an, luna, status="emisa")
    if not ids:
        return None
    facturi = []
    linii_toate = []
    for fid in ids:
        d = _xs.date_factura(conn, schema, fid)
        if not d:
            continue
        firma, factura, linii = d
        facturi.append((factura, linii))
        linii_toate.extend(linii)
    if not facturi:
        return None
    ftxt = facturi_txt(firma, facturi, an, luna)
    atxt = articole_txt(linii_toate, config)
    return {"Facturi.txt": encode_1250(ftxt, "Facturi.txt"),
            "Articole.txt": encode_1250(atxt, "Articole.txt")}
