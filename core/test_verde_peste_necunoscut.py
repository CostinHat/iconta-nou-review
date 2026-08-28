# -*- coding: utf-8 -*-
"""GARD [R35/XX3, 28.08.2026]: un verdict nu poate fi VERDE peste un necunoscut pe care il are in mana.

DE UNDE VINE. `compara_tva` dadea VERDE pe prima ramura - `abs(dif) <= TOLERANTA` - fara sa se uite
DELOC la `necontate`, desi lista aia e chiar in apelul curent. Cand ambii termeni sunt ZERO (o
factura neinregistrata lipseste deopotriva din rulaj SI din decontul regenerat din evidenta),
egalitatea se producea prin ABSENTA amandurora, iar ecranul spunea „D300 si contul coincid" pe o
luna in care o factura emisa statea in afara conturilor. **P6: absenta unei contradictii nu e o
verificare; necunoscutul domina favorabilul.** Plus interdictia 10 (verdict favorabil care coexista
cu un necunoscut nedeclarat) si 19 (favorabil pe zero randuri).

MASURAT inainte de reparatie, pe 27 de perechi (schema activa x luna cu facturi): **6 verzi peste
un necunoscut din propriul payload**. Dupa: **0**.

CE FACE IMPOSIBIL:
  1. intoarcerea culorii: cu facturi necontabilizate in directia comparata, starea NU are voie sa
     fie „verde" - nici cand cifrele coincid la banut;
  2. **colapsul GRI-ului la agregare**: `verifica_tva` calcula `rosu if any(rosu) else verde`, fara
     ramura de gri. Fara ea, reparatia de la (1) ar fi ARATAT facuta si n-ar fi fost - constatarea
     gri exista, dar verdictul de sus ramanea verde. E o a doua instanta, in aceeasi functie;
  3. transformarea gri-ului in rosu: nu se stie ca cifrele sunt gresite, se stie ca nu se poate
     afirma ca sunt bune. Un rosu ar afirma o cauza pe care masuratoarea n-o are;
  4. pierderea DOMENIULUI necunoasterii: mesajul trebuie sa numere facturile, nu sa spuna „exista
     o problema".

CE NU FACE, declarat: nu verifica daca facturile alea CHIAR trebuiau contabilizate in luna aia.
Spune doar ca, atat timp cat sunt in afara evidentei, egalitatea nu afirma nimic despre ele.
"""
import ast
import io
import os
from decimal import Decimal

import pytest

from core import control_incrucisat as _ci
from core import db

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rulaje(colectata=0, deductibila=0):
    return {"4427": {"credit": Decimal(str(colectata))},
            "4426": {"debit": Decimal(str(deductibila))}}


def _factura(fid=1, tva=0, directie="emisa", are_ciorna=False):
    return {"id": fid, "tva": Decimal(str(tva)), "directie": directie, "are_ciorna": are_ciorna}


def _colectata(rez):
    return next(c for c in rez if c["eticheta"] == "TVA colectată")


def test_ZERO_pe_ZERO_cu_factura_necontabilizata_NU_e_verde():
    """[1] Cazul masurat: ambii termeni zero, o factura emisa in afara evidentei. Egalitatea vine
    din absenta amandurora, deci nu afirma nimic."""
    rez = _ci.compara_tva({}, _rulaje(), 2026, 6, necontate=[_factura(tva=2000)])
    c = _colectata(rez)
    assert c["stare"] == "gri", (
        "verdict %s pe o luna cu factura necontabilizata cunoscuta in propriul payload" % c["stare"])
    assert c["stare"] != "rosu", "gri, nu rosu: nu se stie ca cifrele sunt gresite"


def test_CALIBRARE_fara_facturi_necontabilizate_ramane_VERDE():
    """A doua directie, fara de care testul de sus ar trece si daca as fi facut totul gri."""
    rez = _ci.compara_tva({}, _rulaje(), 2026, 6, necontate=[])
    assert _colectata(rez)["stare"] == "verde", "coincidenta curata trebuie sa ramana verde"


def test_CALIBRARE_o_factura_pe_CEALALTA_directie_nu_atinge_colectata():
    """Necunoscutul umbreste doar comparatia in care intra. O factura PRIMITA nu spune nimic
    despre TVA colectata - altfel gardul ar produce gri peste tot si n-ar mai discrimina."""
    rez = _ci.compara_tva({}, _rulaje(), 2026, 6,
                          necontate=[_factura(tva=500, directie="primita")])
    assert _colectata(rez)["stare"] == "verde"
    assert next(c for c in rez if c["eticheta"] == "TVA deductibilă")["stare"] == "gri"


def test_gri_ul_isi_NUMESTE_domeniul_si_nu_afirma_cauza():
    """[4] «Exista o problema» nu e o constatare. Mesajul poarta numarul, iar remediul e
    INVESTIGATIE - nu o cauza pe care masuratoarea n-o are."""
    rez = _ci.compara_tva({}, _rulaje(), 2026, 6,
                          necontate=[_factura(1, 2000), _factura(2, 0)])
    c = _colectata(rez)
    assert c["necunoscut"]["cate"] == 2, (
        "constatarea nu poarta CATE facturi sunt in afara evidentei, ca dato: %r"
        % c.get("necunoscut"))
    assert c["necunoscut"]["fara_nota"] == 2 and c["necunoscut"]["cu_ciorna"] == 0
    assert c["remediu"]["fel"] == "investigatie", (
        "gri-ul propune o actiune executabila, dar cauza nu e dovedita")
    assert c["remediu"]["facturi"] == [1, 2], "facturile nu sunt numite, deci omul nu le poate gasi"


def test_TVA_necunoscut_nu_se_rotunjeste_la_zero_in_mesaj():
    """O factura cu TVA 0 (sau lipsa) e tot un necunoscut - 4 din cele 6 perechi masurate erau
    exact asa. Mesajul nu are voie sa spuna «TVA 0,00» ca si cum ar fi o cifra stiuta."""
    c = _colectata(_ci.compara_tva({}, _rulaje(), 2026, 6, necontate=[_factura(tva=0)]))
    assert c["necunoscut"]["tva"] is None, (
        "un TVA absent e purtat ca zero CUNOSCUT (%r) - `None` inseamna «0 sau nu se stie», si "
        "cele doua nu se pot deosebi azi" % c["necunoscut"]["tva"])


def test_agregarea_de_sus_ARE_ramura_de_gri():
    """[2] Structural, pe AST - nu text cautat in fisier. Fara ramura asta, constatarea gri se
    colapseaza in verde la nivelul verdictului, iar reparatia de mai sus arata facuta fara sa fie."""
    sursa = io.open(os.path.join(_RAD, "core", "control_incrucisat.py"), encoding="utf-8").read()
    fn = next(n for n in ast.walk(ast.parse(sursa))
              if isinstance(n, ast.FunctionDef) and n.name == "verifica_tva")
    valori = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            tinta = n.targets[0]
            if isinstance(tinta, ast.Name) and tinta.id == "stare":
                if isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                    valori.add(n.value.value)
    assert valori == {"rosu", "gri", "verde"}, (
        "`verifica_tva` atribuie lui `stare` valorile %s — lipseste una din cele trei. "
        "Fara `gri`, orice constatare gri (semnalul pe 4428, verdele-peste-necunoscut) se pierde "
        "la agregare." % sorted(valori))


@pytest.mark.parametrize("clasa", ["verde_peste_necunoscut", "verde_peste_gri"])
def test_PE_DATE_pe_toate_schemele_active(clasa):
    """[R35, conditia de deblocare] «zero perechi verzi cu necontabilizate nenule, iar gardul care
    o probeaza are in domeniu TOATE schemele». Domeniul se ia din sonda, care are anti-vacuu propriu:
    daca n-ar gasi nicio pereche, ar RIDICA - prima ei forma a raportat linistit 0 pe 0."""
    import sys
    sys.path.insert(0, os.path.join(_RAD, "scripts"))
    import sonda_r35 as _s
    db.init_pool()
    with db.get_conn() as conn:
        p = _s.perechi(conn)
        assert len(p) >= 20, "domeniul s-a subtiat la %d perechi — sonda nu mai vede firmele" % len(p)
        rele = []
        for schema, an, luna in p:
            try:
                with conn.cursor() as cur:
                    cur.execute("SET search_path TO %s, public" % schema)
                v = _ci.verifica_tva(conn, schema, an, luna)
            except Exception:
                conn.rollback()
                continue
            finally:
                try:
                    with conn.cursor() as cur:
                        cur.execute("SET search_path TO public")
                except Exception:
                    conn.rollback()
            if v.get("stare") != "verde":
                continue
            if clasa == "verde_peste_necunoscut" and (v.get("facturi_necontabilizate") or []):
                rele.append("%s %d-%02d (%d facturi în afara evidenței)"
                            % (schema, an, luna, len(v["facturi_necontabilizate"])))
            if clasa == "verde_peste_gri" and any(
                    c.get("stare") == "gri" for c in (v.get("constatari") or [])):
                rele.append("%s %d-%02d (are constatări gri)" % (schema, an, luna))
    assert not rele, "verdicte VERZI peste un necunoscut, pe date reale: %s" % rele
