# -*- coding: utf-8 -*-
"""GARDĂ: calea jurnalului refuză cu TEMEI, și confruntă conturile cu planul firmei.

**Cele trei găuri, găsite prin exercițiu, nu prin citire** (31.08.2026, seria de invalide cerută de
Costin — invalidele primele, *„dacă pornești cu cele valide și trece, nu știi dacă poarta
funcționează sau e deschisă"*):

| gaura | ce se întâmpla | de ce nu se vedea |
|---|---|---|
| **contul `9999` intra în evidență** | notă creată, 200 | **R54 nu vede calea asta**: domeniul ei recunoaște citirile de cont după **numele cheii** (`cont`, `cont_*`), iar aici cheile se numesc `debit` și `credit` — n-au fost niciodată în cele 27 măsurate, nici în cele 8 declarate NELEGATE |
| **data lipsă / în alt format → 500** | excepție neprinsă, fără mesaj | poarta de perioadă întreba «e luna închisă?» despre o valoare care nu era o dată — **ordinea**, nu poarta |
| **cele 12 refuzuri fără temei** | mesaj corect, autor absent | `jurnal_api` nu cita nicio normă, deci refuzurile lui cădeau în **UMBRA** interdicției 77 — populația despre care norma spune că nu se poate ști mecanic dacă aplică o regulă nenumită. **Aici s-a aflat că da**: partida dublă |

**A patra „gaură" era a sondei mele.** Am numit un caz *„notă dezechilibrată"* — dar schema ține
`cont_debit`, `cont_credit` și `suma` **pe aceeași linie**, deci fiecare linie e echilibrată prin
construcție și nota nu poate fi dezechilibrată pe calea asta. Aplicația a avut dreptate s-o accepte.
*Se scrie aici fiindcă altfel cineva ar „repara" un invariant care e deja garantat de schemă.*

**CE NU PĂZEȘTE, declarat:** că mesajul e bun. Păzește că refuzul **există**, că **poartă temeiul**,
și că un cont din afara planului **nu intră**.
"""
import pytest

from core import jurnal_api as _j


class _CurFals:
    """Cursor care spune că planul firmei conține exact conturile date. Fără bază: proba e despre
    ce face `_linii_valide`, nu despre ce e în plan."""

    def __init__(self, conturi):
        self._c = set(conturi)
        self._r = None

    def execute(self, sql, args=None):
        # `cont_valid.exista` face `SELECT 1 ... LIMIT 1` și citește `fetchone() is not None` — deci
        # cursorul fals trebuie să întoarcă un RÂND, nu un contor. Prima formă căuta „count" în SQL
        # și n-o potrivea niciodată, așa că toate conturile ieșeau inexistente: un fals fals-pozitiv.
        cont = (args or [None])[0]
        self._r = (1,) if str(cont) in self._c else None

    def fetchone(self):
        return self._r

    def fetchall(self):
        return []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _ConnFals:
    def __init__(self, conturi=("4111", "704", "602", "605", "401", "5121")):
        self._conturi = conturi

    def cursor(self, **kw):
        return _CurFals(self._conturi)


# ── TEMEIURILE ──────────────────────────────────────────────────────────────────────────────

def test_cele_doua_temeiuri_sunt_SEPARATE_si_sursate():
    """Două întrebări diferite, două articole: **ce trebuie să conțină** o înregistrare (partida
    dublă, art. 5) și **când se consemnează** (art. 6). Un singur temei ar trimite cititorul la
    articolul greșit — greșeala pe care am făcut-o ieri la registrul-inventar, cu `TEMEI_CONTINUT`
    pus pe un refuz de moment."""
    assert _j.TEMEI_PARTIDA_DUBLA.art == "5" and _j.TEMEI_PARTIDA_DUBLA.alin == "1"
    assert _j.TEMEI_CONSEMNARE.art == "6" and _j.TEMEI_CONSEMNARE.alin == "1"
    for t in (_j.TEMEI_PARTIDA_DUBLA, _j.TEMEI_CONSEMNARE):
        assert t.tip == "Lege" and t.nr == 82 and t.an == 1991
        assert t.text_citat and len(t.text_citat) > 80


# ── DATA: refuz, nu defecțiune ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("data", [None, "", "   ", "10.03.2025", "2025-13-45", "ieri"])
def test_o_data_care_nu_e_data_produce_REFUZ_cu_temei_nu_500(data):
    """Un 500 nu e un refuz: nu spune nimic omului și nu poate purta temei."""
    d, refuz = _j._data_valida(data)
    assert d is None and refuz, "data %r a trecut ca validă" % data
    assert refuz["temei"] == str(_j.TEMEI_CONSEMNARE)
    assert refuz.get("camp") == "data"


def test_o_data_buna_trece():
    """Anti-vacuu: un validator care refuză mereu ar trece toate probele de mai sus."""
    import datetime
    d, refuz = _j._data_valida("2025-03-31")
    assert refuz is None and d == datetime.date(2025, 3, 31)


# ── CONTURILE: confruntate cu planul firmei ─────────────────────────────────────────────────

def test_un_cont_din_AFARA_planului_e_refuzat_cu_temei():
    """Gaura pe care exercițiul a găsit-o: `9999` intra în evidență. *O notă cu un cont inexistent
    nu e evidență, e un rând care arată ca evidență* (decizia lui Costin din 26.08, R54)."""
    r = _j._linii_valide(_ConnFals(), "ztest",
                         [{"debit": "9999", "credit": "704", "suma": 1000}])
    assert r, "contul din afara planului a trecut"
    assert r["temei"] and r.get("camp") == "debit"


def test_conturile_din_plan_trec():
    """Anti-vacuu pe confruntare: dacă ar refuza orice cont, gardul de mai sus n-ar dovedi nimic."""
    assert _j._linii_valide(_ConnFals(), "ztest",
                            [{"debit": "4111", "credit": "704", "suma": 1000}]) is None


def test_se_verifica_AMBELE_conturi_nu_doar_primul():
    """Un creditor din afara planului e la fel de rupt ca un debitor."""
    r = _j._linii_valide(_ConnFals(), "ztest",
                         [{"debit": "4111", "credit": "8888", "suma": 1000}])
    assert r and r.get("camp") == "credit"


def test_se_verifica_TOATE_liniile_nu_doar_prima():
    r = _j._linii_valide(_ConnFals(), "ztest",
                         [{"debit": "4111", "credit": "704", "suma": 1000},
                          {"debit": "7777", "credit": "401", "suma": 500}])
    assert r and r["linia"] == 2, "refuzul nu poartă indicele liniei ca DATĂ"


# ── FIECARE REFUZ POARTĂ TEMEIUL ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("linii", [
    [],
    [{"debit": "", "credit": "704", "suma": 1000}],
    [{"debit": "4111", "credit": "", "suma": 1000}],
    [{"debit": "4111", "credit": "704", "suma": 0}],
    [{"debit": "4111", "credit": "704", "suma": -5}],
    [{"debit": "9999", "credit": "704", "suma": 1000}],
])
def test_niciun_refuz_al_liniilor_nu_ramane_fara_temei(linii):
    """Interdicția 77, pe cea mai folosită cale de scriere. Măsurat pe 31.08: **12 din 12 fără
    temei**; după reparație, 0 din 14."""
    r = _j._linii_valide(_ConnFals(), "ztest", linii)
    assert r, "cazul n-a fost refuzat: %r" % linii
    assert r.get("temei"), "refuz fără temei: %r" % r["eroare"][:70]
    assert str(r["temei"]).startswith("Lege"), "temeiul nu e citabil: %r" % r["temei"]


def test_partida_dubla_e_garantata_de_SCHEMA_nu_de_o_verificare():
    """A patra «gaură» era a sondei mele, și se scrie ca să nu fie «reparată».

    `inregistrari_linii` ține `cont_debit`, `cont_credit` și `suma` pe ACEEAȘI linie, amândouă
    `NOT NULL` — deci fiecare linie e o pereche echilibrată prin construcție, iar o notă nu poate fi
    dezechilibrată pe calea asta. Un cod care ar „verifica echilibrul" aici ar fi cod mort.
    """
    import io
    import os
    import re
    sql = io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "tenant_template.sql"), encoding="utf-8").read()
    m = re.search(r"CREATE TABLE \S+\.inregistrari_linii \((.*?)\);", sql, re.S)
    assert m, "tabelul de linii nu se mai găsește — invariantul nu se mai poate citi din schemă"
    # Pe LINIE, nu pe corp: `suma numeric(14,2) NOT NULL` conține o virgulă în tipul ei, iar o
    # potrivire „până la virgulă" o rupe. Tipul unei coloane nu e un separator de coloane.
    # Pe JETOANE, nu pe sir: linia se sparge in cuvinte si se cere perechea `NOT NULL` ca subsecventa.
    linii = {l.strip().split()[0]: l.split() for l in m.group(1).split(chr(10)) if l.strip()}

    def _not_null(jet):
        return any(jet[k].upper() == "NOT" and jet[k + 1].upper().rstrip(",") == "NULL"
                   for k in range(len(jet) - 1))

    for coloana in ("cont_debit", "cont_credit", "suma"):
        assert coloana in linii and _not_null(linii[coloana]), (
            "`%s` nu mai e NOT NULL pe aceeași linie — atunci partida dublă NU mai e garantată de "
            "schemă, și trebuie verificată în cod" % coloana)
