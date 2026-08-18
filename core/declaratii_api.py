"""
core/declaratii_api.py — dispatch pentru TOATE declarațiile pe care le produce aplicația.
Registrul DECLARATII (mai jos) = SURSA UNICĂ a tipurilor produse: 50 de tipuri, fiecare cu
periodicitate + adaptor către core/<tip>.py::genereaza(). O singură rută în main.py cheamă aici;
diferențele de semnătură genereaza() stau în ADAPTOARE, izolate, ca ruta să fie uniformă.
Cele 9 periodice GENERICE (tipuri() = DECLARATII − _DOAR_API: d100 d101 d112 d205 d300 d301
d390 d394 d406) apar în selectorul per-firmă; restul (41) sunt _DOAR_API (parametri manuali /
fără ecran dedicat, stare AMÂNAT în FUNCTIONALITATI.csv). Coerența cod↔CSV↔CHEIE_DUK↔generator
e gardată de core/test_registru_functionalitati.py.

Periodicitate — cele 9 generice (din realitatea declarațiilor, nu forțată uniform):
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

from core import (d100, d101, d104, d107, d110, d220, d221, d223, d307, d112, d177, d205, d207, d230, d300, d301, d311, d390, d394, d406, d710,
                  d120, d200, d201, d204, d208, d216, d393, d395, d397, d600,
                  d106, d108, d114, d130, d318, d603,
                  d119, d169n, d213, d214, d401, d402,
                  d101g, d169, d398, d399, d403, d407,
                  d212)
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


def _d110(conn, schema, b):
    # D110 e MANUALA (regularizare/restituire impozit pe venit retinut la sursa). Lunara (luna+an).
    return d110.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual") or {})


def _d220(conn, schema, b):
    # D220 e MANUALA (venit estimat / norma de venit - persoana fizica). Anuala (luna raportare=12 fix).
    return d220.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


def _d221(conn, schema, b):
    # D221 e MANUALA (venituri agricole pe norme de venit - PF/asociere). Anuala (luna=12 fix).
    return d221.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


def _d223(conn, schema, b):
    # D223 e MANUALA (venituri estimate asocieri fara PJ / transparenta fiscala). Anuala (luna=12 fix).
    return d223.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


def _d230(conn, schema, b):
    # D230 e MANUALA integral (redirectionare pana la 3,5% din impozit catre ONG) - fara pull automat.
    # ANUALA (an = anul venitului); luna de raportare = 12 (structura, fix).
    return d230.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d307(conn, schema, b):
    # D307 e MANUALA (ajustare/corectie/regularizare TVA). Lunara (luna+an). operatiuni tip A/L/C.
    return d307.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual") or {})


def _d311(conn, schema, b):
    # D311 e MANUALA integral (TVA in situatii speciale, dupa anularea codului de TVA) -
    # fara pull automat; `manual` = bazele/TVA pe situatii + Data_A + d_anul1/d_anul2.
    return d311.genereaza(conn, schema, Perioada(b["an"], luna=b["luna"]), b.get("manual") or {})


def _d393(conn, schema, b):   # informativa bilete transport international (anuala)
    return d393.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d395(conn, schema, b):   # informativa trimiteri postale contra ramburs (lunara)
    return d395.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d397(conn, schema, b):   # informativa transport alternativ (lunara)
    return d397.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d200(conn, schema, b):   # venituri realizate din Romania (PF, anuala)
    return d200.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d201(conn, schema, b):   # venituri din strainatate (PF, anuala)
    return d201.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d204(conn, schema, b):   # venit asocieri fara personalitate juridica (anuala)
    return d204.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d208(conn, schema, b):   # transfer proprietati imobiliare - notari (semestriala)
    return d208.genereaza(conn, schema, Perioada(b["an"], luna=int(b.get("luna") or 12)), b.get("manual") or {})


def _d216(conn, schema, b):   # impozit special bunuri de valoare mare (anuala)
    return d216.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d120(conn, schema, b):   # decont accize (anual)
    return d120.genereaza(conn, schema, Perioada(b["an"], luna=int(b.get("luna") or 12)), b.get("manual") or {})


def _d600(conn, schema, b):   # baza CAS/CASS estimata (PF, anuala)
    return d600.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d106(conn, schema, b):   # informativa dividende actionari de stat (anuala); header din firma_profil
    return d106.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d108(conn, schema, b):   # impozit pe reprezentanta (anuala)
    return d108.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d114(conn, schema, b):   # contributia asiguratorie pentru munca - CAM (lunara)
    return d114.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d130(conn, schema, b):   # decont impozit titei productie interna (anuala)
    return d130.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d318(conn, schema, b):   # rambursare TVA din alt stat membru UE (la cerere/anuala)
    return d318.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d603(conn, schema, b):   # exceptare CASS - declaratie pe propria raspundere (anuala)
    return d603.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d119(conn, schema, b):   # declaratie speciala BNR - obligatii buget din venituri nete (lunara)
    return d119.genereaza(conn, schema, Perioada(b["an"], luna=int(b["luna"])), b.get("manual") or {})


def _d169n(conn, schema, b):  # neconcordante beneficiar real fiducie - AML (anuala)
    return d169n.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d213(conn, schema, b):   # instrainare pachet control - terenuri agricole extravilan (anuala/eveniment)
    return d213.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d214(conn, schema, b):   # instrainare teren agricol extravilan prin hotarare judecatoreasca (anuala/eveniment)
    return d214.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d401(conn, schema, b):   # informativa proprietati imobiliare - schimb automat DAC (anuala)
    return d401.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d402(conn, schema, b):   # informativa venituri salariale nerezidenti - DAC1 (anuala)
    return d402.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d101g(conn, schema, b):  # impozit profit grup fiscal consolidat (anuala)
    return d101g.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d169(conn, schema, b):   # inregistrare contracte de fiducie (anuala)
    return d169.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d398(conn, schema, b):   # TVA regim special OSS (UE/non-UE), trimestriala
    return d398.genereaza(conn, schema, Perioada(b["an"], luna=int(b.get("luna") or 12)), b.get("manual") or {})


def _d399(conn, schema, b):   # TVA regim special import IOSS, trimestriala
    return d399.genereaza(conn, schema, Perioada(b["an"], luna=int(b.get("luna") or 12)), b.get("manual") or {})


def _d403(conn, schema, b):   # informativa asigurari de viata - DAC2/CRS (anuala)
    return d403.genereaza(conn, schema, Perioada(b["an"], luna=12), b.get("manual") or {})


def _d407(conn, schema, b):   # informativa institutii financiare raportoare (semestriala)
    return d407.genereaza(conn, schema, Perioada(b["an"], luna=int(b.get("luna") or 12)), b.get("manual") or {})


def _d212(conn, schema, b):   # declaratia unica (PFA/II/IF - venituri persoane fizice), anuala
    return d212.genereaza(conn, schema, Perioada(b["an"]), b.get("manual") or {})


DECLARATII = {
    "d100": ("trimestrial", _d100),
    "d101": ("anual",       _d101),
    "d104": ("trimestrial", _d104),
    "d107": ("anual",       _d107),
    "d110": ("lunar",       _d110),
    "d112": ("lunar",       _d112),
    "d177": ("anual",       _d177),
    "d205": ("anual",       _d205),
    "d207": ("anual",       _d207),
    "d220": ("anual",       _d220),
    "d221": ("anual",       _d221),
    "d223": ("anual",       _d223),
    "d230": ("anual",       _d230),
    "d300": ("lunar",       _d300),
    "d301": ("lunar",       _d301),
    "d307": ("lunar",       _d307),
    "d311": ("lunar",       _d311),
    "d390": ("lunar",       _d390),
    "d394": ("lunar",       _d394),
    "d406": ("lunar",       _d406),
    # d710 = rectificativa (corecteaza D100 trimestrial). "trimestrial" pentru parametrul
    # `trim`; cere in plus `obligatii` (vezi valideaza_cerere). NU e obligatie periodica -
    # nu intra in semaforul de restante (control_fiscal_api / termene_api): e la cerere,
    # depusa doar cand exista o eroare de corectat. Vezi DECIZII 20.07.
    "d710": ("trimestrial", _d710),
    "d393": ("anual",       _d393),
    "d395": ("lunar",       _d395),
    "d397": ("lunar",       _d397),
    "d200": ("anual",       _d200),
    "d201": ("anual",       _d201),
    "d204": ("anual",       _d204),
    "d208": ("semestrial",  _d208),
    "d216": ("anual",       _d216),
    "d120": ("anual",       _d120),
    "d600": ("anual",       _d600),
    "d106": ("anual",       _d106),
    "d108": ("anual",       _d108),
    "d114": ("lunar",       _d114),
    "d130": ("anual",       _d130),
    "d318": ("anual",       _d318),
    "d603": ("anual",       _d603),
    "d119": ("lunar",       _d119),
    "d169n": ("anual",      _d169n),
    "d213": ("anual",       _d213),
    "d214": ("anual",       _d214),
    "d401": ("anual",       _d401),
    "d402": ("anual",       _d402),
    "d101g": ("anual",      _d101g),
    "d169": ("anual",       _d169),
    "d398": ("trimestrial", _d398),
    "d399": ("trimestrial", _d399),
    "d403": ("anual",       _d403),
    "d407": ("semestrial",  _d407),
    "d212": ("anual",       _d212),
}


# Tipuri disponibile DOAR prin API/dispecer, nu in selectorul generic din UI: cer parametri
# pe care ecranul generic (an/luna/trim) nu ii poate furniza. d710 (rectificativa) cere
# `obligatii` = corectiile contabilului -> flux dedicat viitor, nu selectorul generic (altfel
# ar aparea in dropdown si ar esua la generare). Ramane in DECLARATII (dispecer + test cheie DUK).
_DOAR_API = frozenset(("d104", "d110", "d220", "d221", "d223", "d230",
                       "d393", "d395", "d397", "d200", "d201", "d204", "d208", "d216", "d120", "d600",
                       "d106", "d108", "d114", "d130", "d318", "d603",
                       "d119", "d169n", "d213", "d214", "d401", "d402",
                       "d101g", "d169", "d398", "d399", "d403", "d407", "d212"))


def tipuri():
    """Lista tipurilor pentru selectorul generic din UI (periodice, an/luna/trim)."""
    return sorted(k for k in DECLARATII if k not in _DOAR_API)


def periodicitate(tip):
    """'lunar'|'trimestrial'|'anual' sau None dacă tip necunoscut."""
    rec = DECLARATII.get(tip)
    return rec[0] if rec else None


# [selector_periodicitate_v1] setul TVA-decont a carui periodicitate URMEAZA tip_decont-ul firmei
_TVA_PERIODIC = frozenset({"d300", "d394", "d406"})


def periodicitate_firma(tip, tip_decont=None):
    """Periodicitatea AFISATA in selector. Pt setul TVA-decont (d300/d394/d406) urmeaza tip_decont-ul
    firmei (L->lunar, T->trimestrial), ca semaforul (emite_tva); altfel mapul static. Fara tip_decont
    cunoscut -> static. #2 plimbare vizuala 14.08.2026 (afisa 'lunar' si pt firme trimestriale)."""
    baza = periodicitate(tip)
    if tip in _TVA_PERIODIC and tip_decont:
        try:
            from core.common import perioada_tva_tip, DECONT_LUNG
            d = perioada_tva_tip({"tip_decont": tip_decont})
            return DECONT_LUNG.get(d, baza)
        except ValueError:
            return baza
    return baza


# ============================================================
#  VALIDARE CERERE — PURĂ (testabilă fără DB)
# ============================================================
def valideaza_cerere(tip, body, per_efectiv=None):
    """
    Verifică tip + parametrii ceruți de periodicitate. Întoarce listă erori
    (gol = ok). Nu atinge DB. [C7] per_efectiv: periodicitatea REALĂ a firmei — setul
    TVA-decont (d300/d394/d406) urmează tip_decont-ul (ca /declaratii/tipuri și wizardul);
    fără ea, o firmă trimestrială (care trimite `trim`) pică pe periodicitatea statică.
    """
    erori = []
    per = periodicitate(tip)
    if per is None:
        return ["tip declarație necunoscut: %r (suportate: %s)"
                % (tip, ", ".join(tipuri()))]
    per = per_efectiv or per   # [C7] efectivă bate statica pentru setul TVA-decont

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

    # d177 (redirectionare impozit profit -> ONG/cult, MANUALA anuala): cere manual.beneficiari. Mesaj de
    # CONTABIL (formularul manual din UI trimite mereu beneficiari -> aici cade doar apelul API gol). Detaliile
    # pe beneficiar (tip/cod fiscal/IBAN/contract/suma) si plafoanele le da d177.genereaza.
    if tip == "d177":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("D177 nu are ce genera: adaugă în formular cel puțin un beneficiar către care "
                         "redirecționezi o parte din impozitul pe profit.")

    # d207 (informativa nerezidenti, MANUALA anuala): cere manual.beneficiari. Mesaj de CONTABIL (formularul
    # manual din UI trimite mereu beneficiari -> aici cade doar apelul API gol). Detaliile pe beneficiar
    # (tip venit/stat/cod fiscal/baza/impozit/act normativ) le da d207.genereaza.
    if tip == "d207":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("D207 nu are ce genera: adaugă în formular cel puțin un beneficiar nerezident căruia "
                         "i-ai plătit venituri cu reținere la sursă (dividende, dobânzi, redevențe etc.).")

    # d104 (distribuire venituri asocieri, MANUALA trimestriala): cere trim + manual.asociati
    if tip == "d104":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("asociati"):
            erori.append("d104 cere `manual.asociati` (asociații asocierii) + `manual.profit_pierd`")

    # d107 (informativa sponsorizari/mecenat/burse, MANUALA anuala): cere manual.beneficiari. Mesaj de CONTABIL
    # (formularul manual din UI trimite mereu beneficiari -> aici cade doar apelul API gol). Detaliile pe
    # beneficiar (denumire/cod fiscal/adresa/sume) le da d107.genereaza.
    if tip == "d107":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("beneficiari"):
            erori.append("D107 nu are ce genera: adaugă în formular cel puțin un beneficiar al "
                         "sponsorizării, mecenatului sau bursei.")

    # d110 (regularizare impozit retinut la sursa, MANUALA lunara): cere manual.obligatii
    if tip == "d110":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("obligatii"):
            erori.append("d110 cere `manual.obligatii` (obligații de regularizat: cod_oblig/suma_dat/suma_rest)")

    # d220 (venit estimat PF, MANUALA anuala): cere manual.cif (CNP) + manual.activitate
    if tip == "d220":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("cif") or not m.get("activitate"):
            erori.append("d220 cere `manual.cif` (CNP) + `manual.activitate` (venit estimat PF)")

    # d221 (venituri agricole pe norme, MANUALA anuala): cere manual.cif + activitati
    if tip == "d221":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("cif") or not m.get("activitati"):
            erori.append("d221 cere `manual.cif` (CNP) + `manual.activitati` (activități agricole)")

    # d223 (venituri estimate asocieri, MANUALA anuala): cere manual.activitate + asociati
    if tip == "d223":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("activitate") or not m.get("asociati"):
            erori.append("d223 cere `manual.activitate` + `manual.asociati` (asocierea + asociații)")

    # d230 (redirectionare 3,5%, MANUALA): cere `manual` (contribuabil + beneficiar ONG)
    if tip == "d230":
        if not isinstance(body.get("manual"), dict) or not body.get("manual"):
            erori.append("d230 cere `manual` (nume_c/cif_c contribuabil + den/cif/cont_entitate ONG)")

    # d307 (ajustare TVA, MANUALA lunara): cere manual.operatiuni. Mesaj de CONTABIL (formularul manual din
    # UI trimite mereu operatiuni -> aici cade doar apelul API gol). Detaliile pe operatiune le da d307.genereaza.
    if tip == "d307":
        m = body.get("manual")
        if not isinstance(m, dict) or not m.get("operatiuni"):
            erori.append("D307 nu are ce genera: adaugă în formular cel puțin o operațiune de ajustare TVA "
                         "(transfer de active, leasing, sau anularea codului de TVA).")

    # d311 (TVA situatii speciale, MANUALA): cere `manual`. Mesaj de CONTABIL (formularul manual din UI
    # trimite mereu `manual` populat -> aici cade doar apelul API gol). Detaliile de camp le da d311.genereaza.
    if tip == "d311":
        if not isinstance(body.get("manual"), dict) or not body.get("manual"):
            erori.append("D311 nu are ce genera: completează în formular data anulării codului de TVA, "
                         "motivul anulării și sumele pe operațiuni.")

    # d710 (rectificativa): cere lista de corectii `obligatii` [{cod_oblig, suma_dat_i, suma_dat_c}]
    if tip == "d710":
        obl = body.get("obligatii")
        if not isinstance(obl, list) or not obl:
            erori.append("d710 cere `obligații` (lista de corecții, nevidă)")

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
    # [C7] periodicitatea EFECTIVĂ a firmei pentru setul TVA-decont (d300/d394/d406): urmează
    # tip_decont (ca /declaratii/tipuri și wizardul). Fără asta, firma trimestrială trimite `trim`,
    # iar validatorul static (lunar) cere `luna` -> "luna invalidă: None (aștept 1-12)".
    per_ef = None
    if tip in _TVA_PERIODIC:
        with conn.cursor() as cur:
            cur.execute("SELECT tip_decont FROM firma_profil WHERE id = 1")
            _rd = cur.fetchone()
        per_ef = periodicitate_firma(tip, _rd[0] if _rd else None)
    erori = valideaza_cerere(tip, body, per_ef)
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
    # [C7] setul TVA trimestrial: wizardul trimite `trim`; generatoarele d300/d394/d406 sunt ancorate
    # pe LUNĂ (agregă trimestrul din ultima lună). Convertim într-un SINGUR loc, după validare:
    # T1->luna 3, T2->6, T3->9, T4->12 (DUK regula R18: trimestrial cere luna în 03/06/09/12).
    if per_ef == "trimestrial" and body.get("trim") and body.get("luna") is None:
        body = {**body, "luna": int(body["trim"]) * 3}
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
    if t == "d110":
        return int(getattr(res, "nr_obligatii", 0) or 0)
    if t == "d307":
        return int(getattr(res, "nr_operatiuni", 0) or 0)
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
