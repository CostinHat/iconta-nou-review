"""
core/declaratii_api.py — dispatch pentru cele 9 declarații. O singură rută în
main.py cheamă aici; diferențele de semnătură genereaza() stau în ADAPTOARE,
izolate, ca ruta să fie uniformă.

Periodicitate (din realitatea declarațiilor, nu forțată uniform):
  lunar      : d112, d300, d301, d390, d394, d406
  trimestrial: d100
  anual      : d101, d205

Parametri speciali (în body, opționali):
  manual     : d300, d390, d394  (rânduri TVA introduse de contabil)
  cota       : d100
  date_extra, ca_an_precedent_eur : d101

CALCUL+DB stau în module (au pull+genereaza). Aici doar: validare cerere (pură)
+ alegere adaptor. Se dovedește pe server: apelul real genereaza pe schema tenant.
"""
from __future__ import annotations

from core import (d100, d101, d104, d107, d220, d223, d112, d177, d205, d207, d230, d300, d301, d311, d390, d394, d406, d710)
from core.common import Perioada

REGULI = "2026.1"
MODUL = "declaratii_api"


# ============================================================
#  ADAPTOARE — un loc unde se absoarbe diferența de semnătură.
#  Fiecare primește (conn, schema, body) și cheamă genereaza corect.
# ============================================================
def _d100(conn, schema, b):
    return d100.genereaza(conn, schema, Perioada(b["an"], trim=b["trim"]),
                          {"cota": b["cota"]} if b.get("cota") is not None else None)

def _d101(conn, schema, b):
    # d101.genereaza() a fost rescris 16.07.2026 pe ANAF structura D101 VERSIUNE NECUNOSCUTA
    # individual (nu D101G grup) - semnatura noua: (conn, schema, an, manual=None).
    # manual = suprascrieri optionale (venituri_totale, cheltuieli_totale etc.)
    manual = dict(b.get("date_extra") or {})
    if b.get("ca_an_precedent_eur"):
        manual.setdefault("ca_an_precedent_eur", b["ca_an_precedent_eur"])
    return d101.genereaza(conn, schema, Perioada(b["an"]), manual or None)

def _d112(conn, schema, b):
    return d112.genereaza(conn, schema, b["an"], b["luna"])

def _d205(conn, schema, b):
    return d205.genereaza(conn, schema, Perioada(b["an"]))

def _d300(conn, schema, b):
    return d300.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual"))

def _d301(conn, schema, b):
    return d301.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]))

def _d390(conn, schema, b):
    return d390.genereaza(conn, schema, b["an"], b["luna"], b.get("manual"))

def _d394(conn, schema, b):
    return d394.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual"))

def _d406(conn, schema, b):
    return d406.genereaza(conn, schema, b["an"], b["luna"])

def _d710(conn, schema, b):
    # D710 = rectificativa a D100 (corectie obligatii). `obligatii` = corectiile aduse
    # de contabil (ce a declarat gresit vs corect), nu se recalculeaza automat.
    return d710.genereaza(conn, schema, Perioada(b["an"], trim=b["trim"]), {"obligatii": b["obligatii"]})


# tip -> (periodicitate, adaptor). Adăugarea unei declarații = o linie aici.
def _d177(conn, schema, b):
    # D177 e MANUALA (redirectionare impozit profit -> ONG) - beneficiari + sume din corp cerere.
    return d177.genereaza(conn, schema, Perioada(b["an"], luna=b.get("luna") or 6), b.get("manual") or {})


def _d104(conn, schema, b):
    # D104 e MANUALA (distribuire venituri/cheltuieli intre asociati - asociere fara PJ).
    # Trimestrial cumulat + definitivare (trim 4 -> luna 12). manual: profit_pierd + asociati[] (+ asociere).
    return d104.genereaza(conn, schema, Perioada(b["an"], trim=b["trim"]), b.get("manual") or {})


def _d107(conn, schema, b):
    # D107 e MANUALA (informativa beneficiari sponsorizari/mecenat/burse) - lista de beneficiari din corp cerere.
    return d107.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


def _d207(conn, schema, b):
    # D207 e MANUALA (informativa impozit retinut nerezidenti) - lista de beneficiari din corp cerere.
    return d207.genereaza(conn, schema, Perioada(b["an"], luna=b.get("luna") or 12), b.get("manual") or {})


def _d220(conn, schema, b):
    # D220 e MANUALA (venit estimat / norma de venit - persoana fizica). Anuala (luna raportare=12 fix).
    return d220.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


def _d223(conn, schema, b):
    # D223 e MANUALA (venituri estimate asocieri fara PJ / transparenta fiscala). Anuala (luna=12 fix).
    return d223.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


def _d230(conn, schema, b):
    # D230 e MANUALA integral (redirectionare pana la 3,5% din impozit catre ONG) - fara pull automat.
    # ANUALA (an = anul venitului); luna de raportare = 12 (structura, fix).
    return d230.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d311(conn, schema, b):
    # D311 e MANUALA integral (TVA in situatii speciale, dupa anularea codului de TVA) -
    # fara pull automat; `manual` = bazele/TVA pe situatii + Data_A + d_anul1/d_anul2.
    return d311.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual") or {})


DECLARATII = {
    "d100": ("trimestrial", _d100),
    "d101": ("anual",       _d101),
    "d104": ("trimestrial", _d104),
    "d107": ("anual",       _d107),
    "d112": ("lunar",       _d112),
    "d177": ("anual",       _d177),
    "d205": ("anual",       _d205),
    "d207": ("anual",       _d207),
    "d220": ("anual",       _d220),
    "d223": ("anual",       _d223),
    "d230": ("anual",       _d230),
    "d300": ("lunar",       _d300),
    "d301": ("lunar",       _d301),
    "d311": ("lunar",       _d311),
    "d390": ("lunar",       _d390),
    "d394": ("lunar",       _d394),
    "d406": ("lunar",       _d406),
    # d710 = rectificativa (corecteaza D100 trimestrial). "trimestrial" pentru parametrul
    # `trim`; cere in plus `obligatii` (vezi valideaza_cerere). NU e obligatie periodica -
    # nu intra in semaforul de restante (control_fiscal_api / termene_api): e la cerere,
    # depusa doar cand exista o eroare de corectat. Vezi DECIZII 20.07.
    "d710": ("trimestrial", _d710),
}


# Tipuri disponibile DOAR prin API/dispecer, nu in selectorul generic din UI: cer parametri
# pe care ecranul generic (an/luna/trim) nu ii poate furniza. d710 (rectificativa) cere
# `obligatii` = corectiile contabilului -> flux dedicat viitor, nu selectorul generic (altfel
# ar aparea in dropdown si ar esua la generare). Ramane in DECLARATII (dispecer + test cheie DUK).
_DOAR_API = frozenset(("d104", "d107", "d177", "d207", "d220", "d223", "d230", "d311", "d710"))


def tipuri():
    """Lista tipurilor pentru selectorul generic din UI (periodice, an/luna/trim)."""
    return sorted(k for k in DECLARATII if k not in _DOAR_API)


def periodicitate(tip):
    """'lunar'|'trimestrial'|'anual' sau None dacă tip necunoscut."""
    rec = DECLARATII.get(tip)
    return rec[0] if rec else None


# ============================================================
#  VALIDARE CERERE — PURĂ (testabilă fără DB)
# ============================================================
def valideaza_cerere(tip, body):
    """
    Verifică tip + parametrii ceruți de periodicitate. Întoarce listă erori
    (gol = ok). Nu atinge DB.
    """
    erori = []
    per = periodicitate(tip)
    if per is None:
        return ["tip declarație necunoscut: %r (suportate: %s)"
                % (tip, ", ".join(tipuri()))]

    an = body.get("an")
    if not isinstance(an, int) or an < 2020 or an > 2100:
        erori.append("an invalid: %r (aștept întreg 2020-2100)" % (an,))

    if per == "lunar":
        luna = body.get("luna")
        if not isinstance(luna, int) or luna < 1 or luna > 12:
            erori.append("luna invalidă: %r (aștept 1-12)" % (luna,))
    elif per == "trimestrial":
        trim = body.get("trim")
        if not isinstance(trim, int) or trim < 1 or trim > 4:
            erori.append("trimestru invalid: %r (aștept 1-4)" % (trim,))
    # 'anual' nu cere nimic în plus față de an

    # d177 (redirectionare profit -> ONG, MANUALA): cere `manual` cu beneficiari + sume
    if tip == "d177":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("d177 cere `manual.beneficiari` + sumaMax/sumaRest")

    # d207 (informativa nerezidenti, MANUALA): cere `manual` cu lista de beneficiari
    if tip == "d207":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("d207 cere `manual.beneficiari` (lista de beneficiari nerezidenti)")

    # d104 (distribuire venituri asocieri, MANUALA trimestriala): cere trim + manual.asociati
    if tip == "d104":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("asociati"):
            erori.append("d104 cere `manual.asociati` (asociatii asocierii) + `manual.profit_pierd`")

    # d107 (informativa sponsorizari/mecenat/burse, MANUALA): cere `manual` cu lista de beneficiari
    if tip == "d107":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("d107 cere `manual.beneficiari` (beneficiari sponsorizari/mecenat/burse)")

    # d220 (venit estimat PF, MANUALA anuala): cere manual.cif (CNP) + manual.activitate
    if tip == "d220":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("cif") or not m.get("activitate"):
            erori.append("d220 cere `manual.cif` (CNP) + `manual.activitate` (venit estimat PF)")

    # d223 (venituri estimate asocieri, MANUALA anuala): cere manual.activitate + asociati
    if tip == "d223":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("activitate") or not m.get("asociati"):
            erori.append("d223 cere `manual.activitate` + `manual.asociati` (asocierea + asociatii)")

    # d230 (redirectionare 3,5%, MANUALA): cere `manual` (contribuabil + beneficiar ONG)
    if tip == "d230":
        if not isinstance(body.get("manual"), dict) or not body.get("manual"):
            erori.append("d230 cere `manual` (nume_c/cif_c contribuabil + den/cif/cont_entitate ONG)")

    # d311 (TVA situatii speciale, MANUALA): cere `manual` (bazele/TVA pe situatii)
    if tip == "d311":
        if not isinstance(body.get("manual"), dict) or not body.get("manual"):
            erori.append("d311 cere `manual` (bazele/TVA pe situatii + Data_A + d_anul1/d_anul2)")

    # d710 (rectificativa): cere lista de corectii `obligatii` [{cod_oblig, suma_dat_i, suma_dat_c}]
    if tip == "d710":
        obl = body.get("obligatii")
        if not isinstance(obl, list) or not obl:
            erori.append("d710 cere `obligatii` (lista de corectii, nevida)")

    return erori


# ============================================================
#  DISPATCH — alege adaptorul, cheamă genereaza. Parte DB (pe server).
# ============================================================
def genereaza(conn, schema, tip, body):
    """
    Validează cererea, apoi cheamă adaptorul potrivit.
    Întoarce (xml, rezultat) de la modul.
    Ridică ValueError cu erorile dacă cererea e invalidă.
    """
    erori = valideaza_cerere(tip, body)
    if erori:
        raise ValueError("; ".join(erori))
    # [G1] POARTA PRIN FORMA: tipul neaplicabil pt tip_firma-ul firmei (ex. D101/D406 la un PFA) -> refuz cu
    # TEMEI, nu XML gol. UI-ul dezactiveaza optiunea; backendul decide (o firma nu poate depune ce n-o priveste).
    # Sursa unica de excludere = control_fiscal_api.neaplicabile_forma (aceeasi ca semaforul/termene). DECIZII 23.07.
    from core import control_fiscal_api as _cf
    with conn.cursor() as cur:
        cur.execute("SELECT tip_firma FROM firma_profil WHERE id = 1")
        _row = cur.fetchone()
    _neap = _cf.neaplicabile_forma(_row[0] if _row else None)
    if tip in _neap:
        raise ValueError(_neap[tip])
    _per, adaptor = DECLARATII[tip]
    return adaptor(conn, schema, body)


# ============================================================
#  CATE OPERATIUNI ARE DECLARATIA (27.07.2026)
# ============================================================
def numar_operatiuni(tip, res):
    """Numarul de operatiuni din declaratia generata. None = NU se poate numara.

    DE CE: o declaratie goala LEGITIMA (firma fara activitate) si una goala pentru ca
    s-a rupt un query arata IDENTIC - acelasi XML valid structural, aceleasi zero randuri.
    DUKIntegrator nu poate face diferenta: un D390 cu zero operatiuni e corect structural.
    Toata ziua de 27.07 a fost despre exact clasa asta de defect.

    Numarul urca la UI, care pune o POARTA inainte de trimiterea in coada: omul confirma
    ca firma chiar n-a avut activitate. Nu blocheaza depunerea pe zero - e obligatie reala
    pentru multe declaratii - dar nu o mai lasa sa treaca tacut.

    None, NU zero, pentru ce nu se poate numara: d112 intoarce o LISTA de avertismente (nu
    dataclass), iar d101 n-are notiunea de operatiuni (lucreaza pe solduri). "Nu stiu" nu se
    falsifica in "zero" - aceeasi regula ca verdictul GRI de la validator.
    """
    if res is None or isinstance(res, list):
        return None
    t = (tip or "").lower()
    if t in ("d100", "d710"):
        return len(getattr(res, "obligatii", None) or [])
    if t == "d205":
        return len(getattr(res, "beneficiari", None) or [])
    if t == "d104":
        return int(getattr(res, "nr_asociati", 0) or 0)
    if t == "d107":
        return (int(getattr(res, "nr_beneficiari", 0) or 0) +
                int(getattr(res, "nr_neindividualizati", 0) or 0))
    if t == "d301":
        return len(getattr(res, "operatiuni", None) or [])
    if t == "d390":
        return int(getattr(res, "nr_opi", 0) or 0)
    if t == "d394":
        return int(getattr(res, "op_efectuate", 0) or 0)
    if t == "d406":
        return (len(getattr(res, "note", None) or []) +
                len(getattr(res, "facturi_vanzare", None) or []) +
                len(getattr(res, "facturi_cumparare", None) or []))
    if t == "d300":
        R = getattr(res, "R", None)
        if not isinstance(R, dict):
            return None
        return sum(1 for v in R.values() if v)      # randuri completate, nenule
    return None
