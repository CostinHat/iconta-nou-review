# -*- coding: utf-8 -*-
"""Garda instrumentului P6 — inventarul starii din memoria procesului.

Ce pazeste: nu conformitatea P6 (aia e neatinsa, faza e deschisa), ci INSTRUMENTUL cu care se
masoara P6. Un detector necalibrat care raporteaza zero si unul care nu vede nimic arata identic
in raport, iar diferenta dintre ele e singurul lucru care face cifra utila.

Trei feluri de proba, in ordinea in care conteaza:
  A. CALIBRARE, in ambele directii, pe fiecare din cele cinci clase (METODA §22).
  B. MUTATIE pe propriul mod de esec — se strica o piesa a detectorului si probele pozitive
     TREBUIE sa cada. O proba pe care o mutatie n-o doboara nu masura nimic.
  C. CONTABILITATE — populatia detectorului si tabelul de clasificare se confrunta; un nume
     mutabil nou, neclasificat, pica aici.
"""
from __future__ import annotations

import os
import sys

import pytest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADACINA, "scripts"))
sys.path.insert(0, RADACINA)

import p6_clasificare as CL  # noqa: E402
import scan_stare_proces as S  # noqa: E402

#: Clichetul de DIAGNOSTIC, nu de conformitate: cate nume cer actiune la data masurarii.
#: P6 e DESCHISA (valurile 2 si 3 nu sunt facute), deci cifra nu e zero si nu trebuie sa fie.
#: Rolul ei e sa nu CREASCA pe tacute: o stare noua in memoria procesului pica aici.
#: 10 -> 8 pe 12.09.2026, dupa VALUL 1: `main._login_fail` si `main._alerte_ultima_trimitere` au
#: iesit din memoria procesului in `public.login_esecuri` / `public.alerte_cooldown`.
#: 8 -> 0 pe 12.09.2026, dupa VALUL 2: cele sapte cache-uri ramase si-au primit cele cinci lucruri,
#: iar declaratiile sunt verificate structural de `core/test_cache_declarat.py`.
#: ZERO AICI NU INSEAMNA «P6 gata» — v. `test_datoria_de_infrastructura_tine_P6_deschisa`.
CLICHET_ACTION_REQUIRED = 0

#: Anti-vacuum. Daca graful de import se rupe, inchiderea din `main.py` scade, inventarul iese
#: mic si curat, iar clichetul de mai sus trece degeaba. Pragurile sunt mult sub valorile
#: masurate (238 de fisiere, 3828 de nume), ca sa nu cada la fiecare fisier adaugat.
PRAG_FISIERE = 150
PRAG_NUME = 2500


# ============================================================
#  A. CALIBRARE — pozitiv SI negativ, pe fiecare clasa
# ============================================================
#: (clasa, eticheta, sursa, numele pe care detectorul TREBUIE sa le dea pe acea clasa)
PROBE = [
    ("S1", "rebind sub `global`",
     "_N = 0\ndef creste():\n    global _N\n    _N = _N + 1\n", {"_N"}),
    ("S1", "NEGATIV: acelasi nume, dar local",
     "_N = 0\ndef creste():\n    _N = 1\n    return _N\n", set()),
    ("S1", "NEGATIV: `global` declarat, dar numai citit",
     "_N = 0\ndef vezi():\n    global _N\n    return _N\n", set()),

    ("S2", "scriere prin indice",
     "_C = {}\ndef pune(k, v):\n    _C[k] = v\n", {"_C"}),
    ("S2", "metoda mutatoare",
     "_L = []\ndef adauga(x):\n    _L.append(x)\n", {"_L"}),
    ("S2", "`del` pe indice",
     "_C = {}\ndef scoate(k):\n    del _C[k]\n", {"_C"}),
    ("S2", "NEGATIV: metoda NEmutatoare pe un obiect de modul",
     'import re\n_RE = re.compile("x")\ndef vezi(s):\n    return _RE.match(s)\n', set()),
    ("S2", "NEGATIV: citire prin indice",
     "_C = {}\ndef ia(k):\n    return _C[k]\n", set()),
    ("S2", "NEGATIV: umbrit de un local al functiei INCONJURATOARE",
     "def obligatii(x):\n    return x\n"
     "def genereaza():\n    obligatii = []\n"
     "    def add(x):\n        obligatii.append(x)\n    add(1)\n    return obligatii\n", set()),
    ("S2", "NEGATIV: parametru cu acelasi nume ca un dict de modul",
     "_C = {}\ndef pune(_C, k, v):\n    _C[k] = v\n", set()),

    ("S3", "stare pe un obiect de modul",
     "class Stare:\n    pass\n_S = Stare()\ndef marcheaza():\n    _S.gata = True\n", {"_S"}),
    ("S3", "NEGATIV: atribut citit, nu scris",
     "class Stare:\n    pass\n_S = Stare()\ndef vezi():\n    return _S.gata\n", set()),
    ("S3", "NEGATIV: atribut pe un obiect local",
     "class Stare:\n    pass\ndef f():\n    s = Stare()\n    s.gata = True\n    return s\n", set()),

    ("S4", "`@functools.lru_cache`",
     "import functools\n@functools.lru_cache(maxsize=1)\ndef scump():\n    return 1\n", {"scump"}),
    ("S4", "`@cache` importat direct",
     "from functools import cache\n@cache\ndef scump():\n    return 1\n", {"scump"}),
    ("S4", "`@cached_property` pe o clasa de modul",
     "import functools\nclass X:\n    @functools.cached_property\n"
     "    def greu(self):\n        return 1\n", {"greu"}),
    ("S4", "NEGATIV: decorator care nu tine nimic in memorie",
     "import functools\n@functools.wraps(print)\ndef f():\n    return 1\n", set()),

    ("S5", "atribut de CLASA schimbat la rulare",
     "class Config:\n    activ = False\ndef porneste():\n    Config.activ = True\n", {"Config"}),
    ("S5", "NEGATIV: atribut de clasa doar citit",
     "class Config:\n    activ = False\ndef vezi():\n    return Config.activ\n", set()),
]

CLASE = ("S1", "S2", "S3", "S4", "S5")


@pytest.mark.parametrize("clasa,eticheta,sursa,asteptat",
                         PROBE, ids=["%s: %s" % (p[0], p[1]) for p in PROBE])
def test_calibrare(clasa, eticheta, sursa, asteptat):
    gasit = {c.nume for c in S.analizeaza_sursa(sursa) if c.clasa == clasa}
    assert gasit == asteptat, (
        "%s / %s: detectorul a dat %s, se astepta %s" % (clasa, eticheta, sorted(gasit),
                                                         sorted(asteptat)))


@pytest.mark.parametrize("clasa", CLASE)
def test_fiecare_clasa_are_si_pozitiv_si_negativ(clasa):
    """`P6_UNCALIBRATED_DETECTORS=0` — scris ca aserțiune, ca sa nu fie o cifra din raport."""
    poz = [p for p in PROBE if p[0] == clasa and p[3]]
    neg = [p for p in PROBE if p[0] == clasa and not p[3]]
    assert poz, "clasa %s n-are control POZITIV: un zero de la ea n-ar putea fi citit" % clasa
    assert neg, "clasa %s n-are control NEGATIV: n-ar putea fi deosebita de «aprinde mereu»" % clasa


# ============================================================
#  B. MUTATIE pe propriul mod de esec
# ============================================================
def _cate_cad():
    n = 0
    for clasa, _e, sursa, asteptat in PROBE:
        if {c.nume for c in S.analizeaza_sursa(sursa) if c.clasa == clasa} != asteptat:
            n += 1
    return n


@pytest.mark.parametrize("piesa,atribut,valoare", [
    ("lista de metode mutatoare", "MUTATORI", frozenset()),
    ("lista de memoizatori", "MEMOIZATORI", frozenset()),
])
def test_mutatia_doboara_probe(piesa, atribut, valoare):
    vechi = getattr(S, atribut)
    setattr(S, atribut, valoare)
    try:
        cazute = _cate_cad()
    finally:
        setattr(S, atribut, vechi)
    assert cazute > 0, (
        "golind %s nu cade nicio proba — inseamna ca probele nu masoara piesa aceea" % piesa)


def test_mutatia_pe_umbrire_doboara_probe():
    """Piesa care a produs singurul fals pozitiv real al detectorului (`d112::obligatii`)."""
    vechi = S._legate_direct
    S._legate_direct = lambda fn: set()
    try:
        cazute = _cate_cad()
    finally:
        S._legate_direct = vechi
    assert cazute > 0, "fara cunoasterea domeniilor inconjuratoare n-ar cadea nimic"


# ============================================================
#  C. CONTABILITATE — detector vs tabel de clasificare
# ============================================================
@pytest.fixture(scope="module")
def inv():
    return S.inventar()


def test_anti_vacuum(inv):
    """Un inventar mic si curat e forma pe care o ia un graf rupt."""
    assert len(inv["fisiere_in_proces"]) >= PRAG_FISIERE, (
        "inchiderea importurilor din %s are doar %d fisiere — graful e rupt, iar orice cifra "
        "de mai jos ar fi despre o lume pe care instrumentul n-o vede"
        % (S.RADACINA_PROCES, len(inv["fisiere_in_proces"])))
    assert len({(m, n) for m, _c, n, _l in inv["raw"]}) >= PRAG_NUME


def test_fiecare_nume_mutabil_e_clasificat(inv):
    neclasificate = sorted(set(inv["nume_mutabile"]) - set(CL.TABEL))
    assert not neclasificate, (
        "stare noua in memoria procesului, neclasificata: %s. Nu se poate raporta o cifra P6 "
        "peste un nume pe care nimeni nu l-a citit." % ["%s::%s" % x for x in neclasificate])


def test_nicio_clasificare_fara_obiect(inv):
    """Direcția cealalta: un nume care nu mai e mutabil trebuie sa iasa din tabel, altfel
    tabelul devine o amintire despre cod, nu o descriere a lui."""
    fantoma = sorted(set(CL.TABEL) - set(inv["nume_mutabile"]))
    assert not fantoma, "clasificari fara obiect in cod: %s" % ["%s::%s" % x for x in fantoma]


def test_clichetul_de_actiune_nu_creste(inv):
    ar = [x for x in inv["nume_mutabile"] if CL.TABEL[x].categorie == CL.AR]
    assert len(ar) <= CLICHET_ACTION_REQUIRED, (
        "P6 ACTION_REQUIRED a urcat la %d (clichet %d): %s"
        % (len(ar), CLICHET_ACTION_REQUIRED, ["%s::%s" % x for x in ar]))


def test_cele_doua_nume_din_textul_canonic_au_IESIT_din_memoria_procesului(inv):
    """VALUL 1, 12.09.2026 — proba s-a intors pe dos, si de-aia merita citita.

    Pana azi verifica pozitiv: `PLAN_HARDENING.md:699-701` numeste doua stari business, iar un
    detector care nu le vede nu masoara P6. Amandoua au fost mutate in baza, deci nu mai exista
    ca nume de modul. Proba pazeste acum sensul invers: **nu se pot intoarce**. O repunere in
    `main` a vreunui dictionar de esecuri sau de cooldown pica aici.
    """
    mutabile = set(inv["nume_mutabile"])
    for nume in (("main", "_login_fail"), ("main", "_alerte_ultima_trimitere")):
        assert nume not in mutabile, (
            "%s::%s a reaparut ca stare in memoria procesului — valul 1 il scosese in baza" % nume)


def test_datoria_de_infrastructura_nu_poate_DISPAREA_tacut():
    """[12.09.2026] Proba s-a intors pe dos — asa cum cerea chiar mesajul ei de dinainte.

    Pana azi cerea ca datoria sa fie DESCHISA: `PLAN_HARDENING.md:709-711` spune ca P6 «include
    infrastructura, nu doar codul», iar partea aia nu se vede in niciun AST. Cat timp productia
    rula un singur proces, o cifra de cod la zero s-ar fi citit drept «P6 gata».

    Azi unitatea poarta `WEB_CONCURRENCY=2` si productia serveste din doua procese, cu criteriile
    canonice exercitate pe ele. Deci datoria e INCHISA — dar paza ramane, mutata pe ce se poate
    strica de-acum inainte: intrarea n-are voie sa **dispara**. O cifra care atinge zero fiindca
    cineva a sters randul nu se deosebeste, la citire, de una care atinge zero fiindca s-a facut
    treaba; singura deosebire e ca prima minte. Proba cade daca intrarea e stearsa, daca isi pierde
    starea, sau daca se inchide fara sa spuna CINE a inchis-o.
    """
    # multime, nu `in`: `in` peste un dict se transforma tacut in sub-sir daca dreapta devine
    # vreodata un sir, si arata identic. `>=` crapa in loc sa treaca (METODA §23).
    assert set(CL.TABEL_INFRA) >= {"un_singur_proces"}, (
        "intrarea de infrastructura a fost STEARSA din `TABEL_INFRA`. Cifra atinge zero prin "
        "absenta, nu prin fapt — iar din raport nu se mai poate deosebi una de alta.")
    intrare = CL.TABEL_INFRA["un_singur_proces"]
    assert intrare.stare == CL.INCHIS, (
        "datoria de infrastructura nu mai e nici deschisa, nici inchisa, ci %r" % intrare.stare)
    assert intrare.inchis_de and intrare.inchis_de.strip(), (
        "inchisa fara sa spuna de cine — o inchidere fara autor nu se poate confrunta")
    n = CL.numaratori()
    assert n["P6_INFRA_ACTION_REQUIRED"] == 0
    assert n["P6_ACTION_REQUIRED"] == 0, (
        "codul a capatat stare nedeclarata inapoi: %d" % n["P6_ACTION_REQUIRED"])


def test_fiecare_cache_acceptat_are_declaratie_ceruta_de_regula():
    """Legatura dintre cele doua garzi, ca regula sa nu devina o eticheta.

    Un `ACCEPTABLE_BY_DESIGN` cu `fel == 'declarat'` e acceptat NUMAI fiindca declaratia exista.
    Daca maine cineva ar pune eticheta fara declaratie, `core/test_cache_declarat.py` ar cadea —
    proba asta doar face legatura vizibila de aici, unde se citeste clichetul."""
    declarate = [k for k, v in CL.TABEL.items() if v.fel == "declarat"]
    assert declarate, "nicio intrare `declarat`: regula s-a golit"
    for k in declarate:
        assert CL.TABEL[k].regula == CL.REGULA_DECLARAT, (
            "%s::%s e acceptat pe alta regula decat cea a cache-ului declarat" % k)


def test_detectorul_NU_e_orb_pe_corpusul_real(inv):
    """Perechea probei de mai sus, si motivul pentru care ea singura n-ar fi de ajuns: «nu le
    gasesc» si «nu gasesc nimic» arata identic. Un nume de stare care CHIAR exista trebuie sa fie
    tot acolo, altfel absenta celor doua n-ar dovedi nimic."""
    mutabile = set(inv["nume_mutabile"])
    assert ("core.db", "_pool") in mutabile, (
        "detectorul nu mai gaseste nici macar `core.db::_pool` — masoara o alta lume")
    assert len(mutabile) >= 5, "inventar suspect de mic: %d" % len(mutabile)
