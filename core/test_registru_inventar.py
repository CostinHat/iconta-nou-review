# -*- coding: utf-8 -*-
"""GARD: registrul-inventar (14-1-2) — si mai ales defectul care l-ar face sa arate perfect.

**Defectul central.** Coloana 3 (valoarea contabila) se deriva din balanta. Coloana 4 (valoarea de
inventar) NU se deriva din nimic — vine din numararea faptica. Daca a doua ar primi vreodata ca
default valoarea primei, registrul ar iesi cu **zero diferente pe toate conturile, in fiecare an**:
ar arata exact ca o inventariere facuta bine, si ar fi una care nu s-a facut deloc.

Asta nu e o ipoteza: e forma pe care o ia un registru „completat automat" ori de cate ori cineva
vrea sa scuteasca omul de munca. De-aia sunt trei probe pe ea, din trei directii — pe producator
(`valideaza` cere campul), pe ajutorul de completare (`solduri_de_pornire` nu atinge coloana 4), si
pe AST (nimic din modul nu atribuie `valoare_contabila` lui `valoare_inventar`).

**Al doilea defect pazit**: o diferenta fara cauza. Norma cere coloana 6 *pentru diferente*. Un plus
sau un minus fara explicatie e un necunoscut care arata ca un fapt.
"""
import ast
import io
import os
from decimal import Decimal

import pytest

from core import db as _db
from core import registru_inventar as _ri
from core import tenant_provisioning as _tp

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_registru_inventar"

_RAND = {"momentul": "sfarsit_exercitiu", "cont": "371", "element": "Marfuri",
         "valoare_contabila": "12500.00", "valoare_inventar": "12500.00"}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
            yield c
        finally:
            c.rollback()


# ── 1. VALOAREA DE INVENTAR NU SE POATE NASTE DIN CEA CONTABILA ──────────────────────────────

def test_valoarea_de_inventar_e_CERUTA():
    """Prima dintre cele trei directii: producatorul refuza randul fara ea."""
    date = {k: v for k, v in _RAND.items() if k != "valoare_inventar"}
    with pytest.raises(_ri.InregistrareIncompleta) as ex:
        _ri.valideaza(date)
    assert ex.value.camp == "valoare_inventar"
    assert ex.value.temei


def test_niciun_default_nu_leaga_valoarea_de_inventar_de_cea_contabila():
    """A doua directie, pe AST (METODA §23): nicio atribuire, niciun `or`, niciun `get(..., default)`
    care sa faca `valoare_inventar` sa se nasca din `valoare_contabila`.

    Se umbla pe structura, nu pe text: un `date.setdefault("valoare_inventar", ...)` scris altfel ar
    trece de o cautare de sir. Ce se cere e ca cele doua nume sa nu se atinga niciodata intr-o
    atribuire sau intr-un default.
    """
    arb = ast.parse(io.open(_ri.__file__, encoding="utf-8").read())
    rele = []

    def _mentioneaza_contabila(nod):
        for n in ast.walk(nod):
            if isinstance(n, ast.Constant) and n.value == "valoare_contabila":
                return True
            if isinstance(n, ast.Name) and n.id == "valoare_contabila":
                return True
            if isinstance(n, ast.Attribute) and n.attr == "valoare_contabila":
                return True
        return False

    for nod in ast.walk(arb):
        # atribuire catre `valoare_inventar` (ca nume, cheie de dict sau argument cu nume)
        tinte = []
        if isinstance(nod, ast.Assign):
            tinte = nod.targets
        elif isinstance(nod, (ast.AnnAssign, ast.AugAssign)):
            tinte = [nod.target]
        atinge = False
        for t in tinte:
            for n in ast.walk(t):
                if (isinstance(n, ast.Name) and n.id == "valoare_inventar") or \
                   (isinstance(n, ast.Constant) and n.value == "valoare_inventar") or \
                   (isinstance(n, ast.Attribute) and n.attr == "valoare_inventar"):
                    atinge = True
        if atinge and _mentioneaza_contabila(nod.value):
            rele.append(getattr(nod, "lineno", "?"))
        # `setdefault`/`get` cu default pe cheia valoare_inventar
        if isinstance(nod, ast.Call) and isinstance(nod.func, ast.Attribute) \
                and nod.func.attr in ("setdefault", "get") and len(nod.args) == 2 \
                and isinstance(nod.args[0], ast.Constant) and nod.args[0].value == "valoare_inventar":
            rele.append(getattr(nod, "lineno", "?"))
    assert not rele, (
        "`valoare_inventar` primeste valoare din `valoare_contabila` sau un default (liniile %s). "
        "Registrul ar iesi cu zero diferente pe toate conturile — o inventariere perfecta care nu "
        "s-a facut." % rele)


def test_calibrare_proba_defaultului_VEDE_fiecare_forma(tmp_path):
    """CALIBRARE pe modul propriu de esec (METODA §22), pe cod SINTETIC — nu pe modulul real, care
    trebuie sa ramana curat si a carui curatenie n-ar dovedi ca detectorul vede ceva."""
    def _rele(sursa):
        arb = ast.parse(sursa)
        out = []

        def _ment(nod):
            return any((isinstance(n, ast.Constant) and n.value == "valoare_contabila")
                       or (isinstance(n, ast.Name) and n.id == "valoare_contabila")
                       or (isinstance(n, ast.Attribute) and n.attr == "valoare_contabila")
                       for n in ast.walk(nod))

        for nod in ast.walk(arb):
            tinte = nod.targets if isinstance(nod, ast.Assign) else (
                [nod.target] if isinstance(nod, (ast.AnnAssign, ast.AugAssign)) else [])
            atinge = any((isinstance(n, ast.Name) and n.id == "valoare_inventar")
                         or (isinstance(n, ast.Constant) and n.value == "valoare_inventar")
                         or (isinstance(n, ast.Attribute) and n.attr == "valoare_inventar")
                         for t in tinte for n in ast.walk(t))
            if atinge and _ment(nod.value):
                out.append(getattr(nod, "lineno", "?"))
            if isinstance(nod, ast.Call) and isinstance(nod.func, ast.Attribute) \
                    and nod.func.attr in ("setdefault", "get") and len(nod.args) == 2 \
                    and isinstance(nod.args[0], ast.Constant) \
                    and nod.args[0].value == "valoare_inventar":
                out.append(getattr(nod, "lineno", "?"))
        return out

    assert _rele('valoare_inventar = valoare_contabila\n'), "nu vede atribuirea directa"
    assert _rele('d["valoare_inventar"] = d["valoare_contabila"]\n'), "nu vede atribuirea pe cheie"
    assert _rele('d.setdefault("valoare_inventar", d["valoare_contabila"])\n'), "nu vede setdefault"
    assert _rele('x = d.get("valoare_inventar", 0)\n'), "nu vede `get` cu default"
    assert not _rele('valoare_inventar = date["valoare_inventar"]\n'), \
        "da fals-pozitiv pe citirea normala a campului — atunci n-ar mai fi pazit nimic"


def test_ajutorul_de_completare_NU_atinge_coloana_4():
    """A treia directie. `solduri_de_pornire` propune coloana 3 din balanta. Daca ar propune si
    coloana 4, ar transforma registrul in oglinda balantei — documentul care nu dovedeste nimic."""
    src = io.open(_ri.__file__, encoding="utf-8").read()
    arb = ast.parse(src)
    fn = next(f for f in ast.walk(arb)
              if isinstance(f, ast.FunctionDef) and f.name == "solduri_de_pornire")
    chei = {n.value for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert "valoare_inventar" not in chei, (
        "`solduri_de_pornire` atinge valoarea de inventar — ajutorul de completare ar face "
        "inventarierea in locul omului")
    assert chei >= {"valoare_contabila"}, (
        "anti-vacuu: functia nu propune nici macar coloana 3, deci proba de mai sus nu inseamna nimic")


# ── 2. O DIFERENTA FARA CAUZA ────────────────────────────────────────────────────────────────

def test_diferenta_se_CALCULEAZA_dupa_definitia_din_norma():
    """Coloana 5 = coloana 3 − coloana 4. Semnul conteaza: contabil 100 / inventar 80 e un MINUS
    de 20, nu un plus."""
    assert _ri.diferenta("100.00", "80.00") == Decimal("20.00")
    assert _ri.diferenta("80.00", "100.00") == Decimal("-20.00")
    assert _ri.diferenta("100.00", "100.00") == Decimal("0")


def test_o_diferenta_fara_cauza_e_refuzata():
    date = dict(_RAND, valoare_inventar="11900.00")
    with pytest.raises(_ri.InregistrareIncompleta) as ex:
        _ri.valideaza(date)
    assert ex.value.camp == "cauza"


def test_un_rand_FARA_diferenta_nu_cere_cauza():
    """Anti-vacuu pe regula de mai sus: daca ar cere cauza mereu, proba n-ar spune nimic despre
    conditionare, iar registrul ar deveni imposibil de completat pe conturile care se potrivesc."""
    assert _ri.valideaza(dict(_RAND)) == Decimal("0")


def test_o_diferenta_CU_cauza_trece():
    assert _ri.valideaza(dict(_RAND, valoare_inventar="11900.00",
                              cauza="depreciere marfuri cu termen depasit")) == Decimal("600.00")


# ── 3. NOMENCLATOARE SI CAMPURI ──────────────────────────────────────────────────────────────

def test_momentele_sunt_exact_cele_TREI_din_norma():
    """Norma numeste ocaziile, nu da exemple: la inceputul activitatii, la sfarsitul exercitiului,
    la incetarea activitatii."""
    assert set(_ri.MOMENTE) == {"inceput_activitate", "sfarsit_exercitiu", "incetare_activitate"}


def test_un_moment_inventat_e_refuzat():
    with pytest.raises(_ri.InregistrareIncompleta) as ex:
        _ri.valideaza(dict(_RAND, momentul="trimestrial"))
    assert ex.value.camp == "momentul"


def test_cele_sase_coloane_ale_formularului_sunt_declarate():
    assert _ri.COLOANE == ("nr_curent", "element", "valoare_contabila", "valoare_inventar",
                           "diferenta", "cauza")
    # `nr_curent` si `diferenta` nu se primesc: prima se deriva, a doua se calculeaza
    assert "nr_curent" not in _ri.CAMPURI_CERUTE
    assert "diferenta" not in _ri.CAMPURI_CERUTE


def test_obligatia_si_continutul_sunt_sursate_SEPARAT():
    """Doua niveluri, doua temeiuri — chiar lectia METODA §30. Legea spune CA se tine registrul;
    ordinul spune CE contine. Un singur temei ar ascunde ca sunt doua acte."""
    assert _ri.TEMEI_OBLIGATIE.tip == "Lege" and _ri.TEMEI_OBLIGATIE.nr == 82
    assert _ri.TEMEI_CONTINUT.tip == "OMFP" and _ri.TEMEI_CONTINUT.nr == 2634
    assert len(_ri.TEMEI_CONTINUT.text_citat) > 800, "citarea nu acopera cele sase coloane"


# ── 4. PE DATE REALE ─────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_numarul_curent_se_deriva_si_curge_pe_moment(conn):
    a = _ri.adauga(conn, SCHEMA, 2026, dict(_RAND))
    b = _ri.adauga(conn, SCHEMA, 2026, dict(_RAND, cont="301", element="Materii prime"))
    c = _ri.adauga(conn, SCHEMA, 2026, dict(_RAND, momentul="incetare_activitate"))
    assert (a["nr_curent"], b["nr_curent"]) == (1, 2)
    assert c["nr_curent"] == 1, "momentele impart aceeasi numerotare"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_registrul_gol_spune_ca_nu_s_a_INVENTARIAT_nu_ca_nu_sunt_diferente(conn):
    """Cea mai ieftina minciuna a registrului asta: gol = «totul se potriveste». Temeiul de
    completitudine trebuie sa spuna ce inseamna golul, altfel cineva il citeste ca pe o confirmare."""
    a = _ri.registru(conn, SCHEMA, 2026)
    assert a["randuri"] == []
    assert a["randuri_cu_diferenta"] == 0
    assert a["temei_completitudine"], "registru gol fara temei de completitudine"
    assert a["temei_obligatie"] and a["temei"], "registru fara cele doua temeiuri"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_diferenta_iese_CALCULATA_pe_fiecare_rand_si_se_serializeaza(conn):
    import json
    _ri.adauga(conn, SCHEMA, 2026, dict(_RAND))
    _ri.adauga(conn, SCHEMA, 2026, dict(_RAND, cont="301", element="Materii prime",
                                        valoare_inventar="11900.00", cauza="perisabilitati legale"))
    a = _ri.registru(conn, SCHEMA, 2026)
    assert [r["diferenta"] for r in a["randuri"]] == [0.0, 600.0]
    assert a["randuri_cu_diferenta"] == 1
    json.dumps(a)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_propunerea_din_balanta_nu_inventeaza_coloana_4(conn):
    """Pe date reale: orice ar propune ajutorul, valoarea de inventar lipseste din propunere."""
    prop = _ri.solduri_de_pornire(conn, SCHEMA, 2026)
    assert all("valoare_inventar" not in p for p in prop)
    assert all(set(p) >= {"cont", "element", "valoare_contabila", "sens"} for p in prop)


# ── 5. PRODUCATORUL AJUNGE LA OM ─────────────────────────────────────────────────────────────

def test_exista_rutele_si_ecranul_care_livreaza_registrul():
    """Lista 3 pazeste «producator fara livrare». Proba sta langa producator."""
    arb = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    cai = set()
    for f in ast.walk(arb):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in f.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and isinstance(d.func.value, ast.Name) and d.func.value.id == "app"
                        and d.args and isinstance(d.args[0], ast.Constant)):
                    cai.add((d.func.attr, d.args[0].value))
    assert ("get", "/tenants/{tenant_id}/registru-inventar") in cai
    assert ("post", "/tenants/{tenant_id}/registru-inventar") in cai, (
        "fara inscriere, coloana 4 n-ar avea de unde sa vina — registrul ar ramane gol")
    assert ("get", "/tenants/{tenant_id}/registru-inventar/propunere") in cai

    # Pe STRUCTURA, nu pe text (clichet 50 / METODA §23) — vezi acelasi tipar in
    # `core/test_registre_art321.py`. Inventarul de ecrane e o MULTIME, iar verdictul de ancora e o
    # clasificare: `ACCEPTAT` inseamna ca ruta chiar e chemata din JS, nu doar pomenita acolo.
    from core import test_harta_ecrane as _harta
    assert _harta._ecrane_din_cod() >= {"fa-reginventar"}, "nu exista ecran care sa-l deschida"

    from scripts import scan_ancore_rute as _anc
    v = _anc.verdicte()
    for metoda, cale in (("GET", "/tenants/{tenant_id}/registru-inventar"),
                         ("POST", "/tenants/{tenant_id}/registru-inventar"),
                         ("GET", "/tenants/{tenant_id}/registru-inventar/propunere")):
        assert v.get((metoda, cale)) == "ACCEPTAT", (
            "%s %s nu e ACCEPTAT de detectorul de apelanti: %r" % (metoda, cale, v.get((metoda, cale))))
