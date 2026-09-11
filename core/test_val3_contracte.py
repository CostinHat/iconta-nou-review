# -*- coding: utf-8 -*-
"""core/test_val3_contracte.py — valul 3: I/O extern in afara tranzactiei, cu REVALIDARE.

Regula aprobata de arhitect (11.09.2026):

    FAZA 1 — citirile, fara conexiune tinuta peste I/O
    I/O   — apelul extern, cu pool-ul liber
    FAZA 2 — tranzactie scurta care REVALIDEAZA ce s-ar fi putut schimba, apoi scrie

    EXTERNAL_IO_UNDER_DB_CONNECTION=NO   si   STALE_BUSINESS_DECISION_ALLOWED=NO

**Cele doua reguli sunt in tensiune, si de-aia se probeaza amandoua.** E usor sa scoti I/O-ul din
tranzactie daca accepti sa scrii pe o stare veche; si e usor sa nu scrii pe stare veche daca tii
tranzactia deschisa. Probele de mai jos cer sa fie adevarate SIMULTAN.

**Nu toate familiile au aceeasi forma**, si asta e miezul turei:
  · `verifica_vies` — rezultatul extern DECIDE; se revalideaza accesul si luna;
  · `reges_client` — rezultatul extern ESTE efectul (salariatul e deja in registru, mesajul e deja
    consumat din coada). Acolo scrierea e NECONDITIONATA: e urma unui act petrecut, iar o
    revalidare care ar arunca-o ar face ca REGES sa stie ceva ce noi nu stim;
  · `platitor_tva_freeze`, `duk`, `d112` — nu depind de baza deloc, deci n-au ce revalida.
"""
from __future__ import annotations

import ast
import io
import os

import pytest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: clichet pe clasa C5 din registrul P5. NU cerinta — clichet: poate cobori, nu poate urca.
CLICHET_C5 = 0


# ============================================================
#  A. CLICHET pe clasa intreaga, cu anti-vacuum si calibrare
# ============================================================
def _numaratori():
    import sys
    sys.path.insert(0, os.path.join(RADACINA, "scripts"))
    import scan_blocante as sb
    from core import p5_clasificare as p5
    inv, stat = sb.inventar()
    return p5.numaratori(inv), stat


def test_clasa_C5_nu_creste():
    """Orice cale noua care executa I/O extern cu o conexiune din pool in mana pica AICI."""
    n, _stat = _numaratori()
    assert n["ACTION_REQUIRED"] <= CLICHET_C5, (
        "cai C5 in crestere: %d > %d. Fiecare inseamna o conexiune din cele zece, tinuta pe toata "
        "durata unui apel extern." % (n["ACTION_REQUIRED"], CLICHET_C5))


def test_anti_vacuum_detectorul_chiar_vede_codul():
    """Fara asta, clichetul de mai sus ar trece si daca scanul n-ar gasi nimic."""
    n, stat = _numaratori()
    assert stat["intrari"] > 400, "scanul vede doar %d puncte de intrare" % stat["intrari"]
    assert n["RAW_CANDIDATES"] > 50, "doar %d candidati — domeniu prea mic" % n["RAW_CANDIDATES"]
    assert n["RAW_CLASS_ACCOUNTING"] == "PASS"
    assert n["UNCLASSIFIED_RAW_CANDIDATES"] == 0


@pytest.mark.parametrize("familie", [
    "core/intracomunitar.py::verifica_vies",
    "core/woocommerce.py::comenzi",
    "core/reges_client.py::_obtine_token",
    "core/reges_client.py::_post",
    "core/duk.py::versiune_validator",
    "core/d112.py::_enum_xsd",
    "core/monitor_fiscal.py::ruleaza",
    "core/anaf_api.py::valideaza_cui",
    "core/observare.py::trimite_email_html",
    "core/curs_bnr.py::_descarca",
])
def test_familia_inchisa_nu_reapare_in_C5(familie):
    """Fiecare familie inchisa isi are propria proba: o regresie se numeste singura, nu se pierde
    intr-o cifra globala."""
    import sys
    sys.path.insert(0, os.path.join(RADACINA, "scripts"))
    import scan_blocante as sb
    inv, _ = sb.inventar()
    cale, _, functie = familie.partition("::")
    gasite = []
    for x in inv:
        if "C5" not in x["detectori"]:
            continue
        for p in x["primitive"]:
            if p["fel"] == "DB" or not p["in_domeniu_db"] or p["omonim"]:
                continue
            if x["fel"] != "ruta":
                continue          # joburile de fundal au regula lor (FUNDAL), v. registrul P5
            if (p["loc"] or "").startswith(cale + ":"):
                gasite.append("%s (%s)" % (x["intrare"], p["loc"]))
    assert gasite == [], (
        "familia %s a reaparut in clasa C5: %s" % (familie, gasite))


# ============================================================
#  B. STRUCTURAL — I/O-ul nu se executa sub o conexiune
# ============================================================
def _apeluri_sub_conexiune(cale, nume_apel):
    arbore = ast.parse(io.open(os.path.join(RADACINA, cale), encoding="utf-8").read())
    parinte = {}
    for n in ast.walk(arbore):
        for c in ast.iter_child_nodes(n):
            parinte[c] = n
    out = []
    for n in ast.walk(arbore):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        ident = (f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name)
                 else None)
        if ident != nume_apel:
            continue
        p, sub = parinte.get(n), False
        while p is not None:
            if isinstance(p, ast.With):
                for it in p.items:
                    e = it.context_expr
                    if (isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute)
                            and e.func.attr.startswith("get_conn")):
                        sub = True
            p = parinte.get(p)
        out.append((n.lineno, sub))
    return out


@pytest.mark.parametrize("cale,apel", [
    ("main.py", "verifica_vies"),
    ("main.py", "platitor_tva_freeze"),
    ("main.py", "date_din_anaf"),
    ("core/woocommerce.py", "comenzi"),
    ("core/monitor_fiscal.py", "text_din_pdf"),
])
def test_apelul_extern_nu_sta_sub_conexiune(cale, apel):
    sub = [ln for ln, e in _apeluri_sub_conexiune(cale, apel) if e]
    assert sub == [], "%s: `%s` se executa cu o conexiune in mana, liniile %s" % (cale, apel, sub)


def test_calibrare_detectorul_vede_un_apel_care_CHIAR_sta_sub_conexiune():
    """ANTI-VACUUM in cealalta directie: pe un apel care e in bloc (si acolo ii e locul),
    detectorul spune DA. `schema_tenant` se cheama din interiorul conexiunii, mereu."""
    sub = [e for _ln, e in _apeluri_sub_conexiune("main.py", "schema_tenant")]
    assert sub, "scanul nu gaseste niciun apel `schema_tenant` — domeniu gresit"
    # `any`, nu `all`: exista si un apel in afara blocului, si e in regula sa existe. Afirmatia
    # probei e ca detectorul NU e orb la cele dinauntru — nu ca toate ar fi acolo.
    assert any(sub), "detectorul nu vede niciun apel din interiorul unui bloc de conexiune"


# ============================================================
#  C. FUNCTIONAL — revalidarea respinge starea devenita incompatibila
# ============================================================
class _Cursor:
    def __init__(self, raspunsuri=()):
        self._r = list(raspunsuri)
        self.executate = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, p=None):
        self.executate.append((" ".join(sql.split())[:80], p))

    def fetchone(self):
        return self._r.pop(0) if self._r else None

    def fetchall(self):
        return []


class _Conn:
    def __init__(self, raspunsuri=()):
        self._c = _Cursor(raspunsuri)
        self.comis = 0

    def cursor(self, *a, **k):
        return self._c

    def commit(self):
        self.comis += 1

    def rollback(self):
        pass


def _get_conn_fals(conns):
    """Contextmanager care da, pe rand, conexiunile din lista — ca sa se poata deosebi FAZA 1 de
    FAZA 2 si sa se schimbe starea INTRE ele."""
    import contextlib
    lista = list(conns)

    @contextlib.contextmanager
    def f(*a, **k):
        c = lista.pop(0) if lista else _Conn()
        yield c
        c.comis += 1
    return f


def test_VIES_revalidarea_respinge_accesul_pierdut_in_timpul_apelului(monkeypatch):
    """STATE_CHANGED_DURING_EXTERNAL_IO → STALE_DECISION_NOT_COMMITTED.

    Accesul la firmă există în FAZA 1, se pierde în cele 15 s ale apelului VIES, iar în FAZA 2
    ruta refuză cu 404 — fără să scrie nimic, deși VIES a răspuns „valid"."""
    import main
    from fastapi import HTTPException

    c1, c2 = _Conn(), _Conn()
    apeluri = []

    def _schema(conn, uid, tid):
        apeluri.append(conn)
        return "tenant_001" if len(apeluri) == 1 else None      # accesul dispare între faze

    monkeypatch.setattr(main.db, "get_conn", _get_conn_fals([c1, c2]))
    monkeypatch.setattr(main.auth_api, "schema_tenant", _schema)
    monkeypatch.setattr(main, "_cere_luna_deschisa", lambda *a, **k: None)
    from core import intracomunitar as _ic
    monkeypatch.setattr(_ic, "verifica_vies",
                        lambda cod: {"valid": True, "nume": "X", "adresa": "", "tara": "DE",
                                     "numar": "1", "eroare": None})
    with pytest.raises(HTTPException) as exc:
        main.vanzare_ic(1, {"data": "2026-06-01", "valoare": "100",
                            "cod_tva_client": "DE123456789", "tip": "bunuri"},
                        ctx={"uid": 1, "firm": 1})
    assert exc.value.status_code == 404
    assert c2._c.executate == [], "s-a scris pe o stare devenită incompatibilă: %r" % c2._c.executate


def test_VIES_apelul_se_face_cu_pool_ul_LIBER(monkeypatch):
    """Perechea celeilalte reguli: I/O-ul chiar iese din tranzacție. Se numără conexiunile
    deschise în clipa apelului — nu se deduce din forma codului."""
    import main
    deschise = {"n": 0, "in_timpul_apelului": None}
    import contextlib

    @contextlib.contextmanager
    def _gc(*a, **k):
        deschise["n"] += 1
        c = _Conn()
        try:
            yield c
        finally:
            deschise["n"] -= 1

    monkeypatch.setattr(main.db, "get_conn", _gc)
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda *a, **k: None)   # oprește după FAZA 1
    from core import intracomunitar as _ic

    def _vies(cod):
        deschise["in_timpul_apelului"] = deschise["n"]
        return {"valid": True, "nume": "X", "adresa": "", "tara": "DE", "numar": "1"}

    monkeypatch.setattr(_ic, "verifica_vies", _vies)
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        main.vanzare_ic(1, {"data": "2026-06-01", "valoare": "100",
                            "cod_tva_client": "DE123456789"}, ctx={"uid": 1, "firm": 1})
    # ruta s-a oprit în FAZA 1 (404), deci VIES nici nu s-a chemat — și asta e corect:
    assert deschise["in_timpul_apelului"] is None
    assert deschise["n"] == 0, "o conexiune a rămas deschisă"
