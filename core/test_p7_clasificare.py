# -*- coding: utf-8 -*-
"""Calibrarea celor trei detectoare P7 — în ambele direcții, plus anti-vacuum.

DE CE ÎNAINTE DE ORICE CLASIFICARE. Un detector necalibrat produce o cifră care arată la fel ca una
măsurată. Fiecare dintre cele trei primește aici: un POZITIV cunoscut (găsește ce pretinde), un
NEGATIV cunoscut (nu găsește ce nu e), o probă că nu confundă APARIȚIA LEXICALĂ cu operația, și o
aserțiune ANTI-VACUUM pe universul real (o măsurătoare pe zero obiecte nu e o măsurătoare).

Fragmentele sintetice sunt scrise aici, nu în repo: un detector care se poate hrăni numai din
codul existent nu se poate arăta nici greșind, nici nimerind.
"""
from __future__ import annotations

import ast
import os
import sys

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADACINA, "scripts"))
sys.path.insert(0, RADACINA)

import p7_clasificare as CL  # noqa: E402
import scan_p7_straturi as S  # noqa: E402


def _rute(sursa, rel="proba.py"):
    return S.rute_din_arbore(ast.parse(sursa), rel)


# ============================================================
#  D1 — SQL în rută
# ============================================================
RUTA_CU_SQL = '''
@app.get("/proba")
def proba(ctx=None):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
    return {}
'''

RUTA_FARA_SQL = '''
@app.get("/proba")
def proba(ctx=None):
    return {"ok": True}
'''

RUTA_CU_EXECUTE_CARE_NU_E_SQL = '''
@app.post("/proba")
def proba(ctx=None):
    executor.execute(ceva)
    return {}
'''

FUNCTIE_CU_SQL_DAR_FARA_DECORATOR = '''
def ajutor(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
'''


def test_D1_POZITIV_gaseste_SQL_ul_dintr_o_ruta():
    gasite, necunoscute = S.d1_din_rute(_rute(RUTA_CU_SQL))
    assert (len(gasite), len(necunoscute)) == (1, 0)
    assert gasite[0].detector == "D1_SQL_IN_RUTA"


def test_D1_NEGATIV_o_ruta_fara_SQL_nu_produce_nimic():
    assert S.d1_din_rute(_rute(RUTA_FARA_SQL)) == ([], [])


def test_D1_nu_confunda_cuvantul_execute_cu_operatia_SQL():
    """Miezul discriminatorului: `.execute` există și pe alte obiecte. Dacă ținta nu e legată de
    `.cursor()`, apelul NU e SQL — și se numără separat, ca să se vadă că întrebarea s-a pus."""
    gasite, necunoscute = S.d1_din_rute(_rute(RUTA_CU_EXECUTE_CARE_NU_E_SQL))
    assert (len(gasite), len(necunoscute)) == (0, 1)
    assert necunoscute[0].simbol == "executor.execute"


def test_D1_universul_e_RUTA_nu_orice_functie():
    """SQL într-o funcție fără decorator de rută nu e item: P7 vorbește despre RUTE."""
    assert _rute(FUNCTIE_CU_SQL_DAR_FARA_DECORATOR) == []
    assert S.d1_din_rute(_rute(FUNCTIE_CU_SQL_DAR_FARA_DECORATOR)) == ([], [])


def test_D1_ANTI_VACUUM_universul_real_nu_e_gol_si_contine_un_item_cunoscut():
    """Pe repo-ul real: universul are sute de rute, iar detectorul găsește un item pe care l-am
    citit cu ochii (`main.py`, ruta `admin_sanatate`). Fără asta, un detector care întoarce mereu
    lista goală ar trece toate probele de mai sus."""
    toate = S.rute()
    assert len(toate) >= 400, "universul rutelor s-a golit: %d" % len(toate)
    gasite, _ = S.d1_sql_in_ruta()
    cunoscute = {(i.fisier, i.cale.split(" ")[0]) for i in gasite}
    assert ("main.py", "admin_sanatate") in cunoscute, (
        "detectorul nu mai vede un item citit cu ochii în cod")


# ============================================================
#  D2 — motor fiscal care atinge baza
# ============================================================
MODUL_FARA_DB = '''
def calculeaza(conn, an):
    return 42
'''


def test_D2_POZITIV_gaseste_importul_de_db_intr_un_modul_care_chiar_il_are():
    """Pozitivul se ia din repo, nu sintetic: `core/firma_rezumat.py` chiar importă `db`."""
    assert S._atinge_db("core/firma_rezumat.py"), "detectorul nu mai vede un import real de `db`"


def test_D2_NEGATIV_un_modul_care_primeste_conn_nu_e_raportat(tmp_path):
    f = tmp_path / "zt_modul.py"
    f.write_text(MODUL_FARA_DB, encoding="utf-8")
    rel = os.path.relpath(str(f), RADACINA)
    assert S._atinge_db(rel) == []


def test_D2_ANTI_VACUUM_universul_fiscal_nu_e_gol():
    """[V3, 13.09.2026] Universul lui D2 nu mai e o aproximare: sunt modulele DECLARATE motor fiscal.

    Proba s-a întors pe dos, și merită citit de ce. Până azi cerea `d2 == []` — și trecea, pe un
    univers de 25 de module derivat dintr-un singur instrument. Registrul a adus 96 de module
    declarate `FISCAL_ENGINE`, iar printre ele unul CHIAR importă `db`: `core/efactura_send.py`.
    *Aceeași întrebare, pe universul adevărat, dă alt răspuns — asta e tot rostul lui V3.*
    """
    fiscale, sursa = S.module_fiscale()
    assert len(fiscale) >= 90, "universul modulelor fiscale s-a golit: %d" % len(fiscale)
    assert sursa == "core/straturi.py::REGISTRU", (
        "D2 și-a luat definiția din altă parte decât registrul: %r" % sursa)
    gasite = {(i.fisier, i.linie) for i in S.d2_motor_fiscal_cu_db()}
    assert gasite == {("core/efactura_send.py", 368)}, (
        "încălcările D2 s-au schimbat fără ca proba să fie actualizată: %s" % sorted(gasite))


def test_D2_isi_ia_definitia_NUMAI_din_registru():
    """Contractul V3: `D2_RAW_ITEM = module.layer == FISCAL_ENGINE AND module uses core.db`.

    Cele două instrumente de dinainte n-au dispărut — dar rolul lor s-a mutat: definesc UNIVERSUL
    REGISTRULUI (cine trebuie să aibă o declarație), nu răspunsul. Proba cere exact asta: mulțimea
    pe care se uită D2 e identică cu cea din registru, nu cu vreuna dintre ele.
    """
    from core import straturi
    fiscale, _ = S.module_fiscale()
    assert fiscale == straturi.module_din_strat(straturi.FISCAL_ENGINE)
    assert fiscale != S.generatoare_declaratii(), "D2 s-a întors la definiția veche"
    assert fiscale != S.module_cu_valori_fiscale(), "D2 s-a întors la a doua definiție veche"


# ============================================================
#  D3 — HTTP sub stratul HTTP
# ============================================================
MODUL_CU_HTTP_IN_AFARA_RUTEI = '''
def ajutor(ctx):
    raise HTTPException(403, "nu")
'''

MODUL_CU_HTTP_IN_RUTA = '''
def monteaza(app):
    @app.get("/x")
    def x(ctx=None):
        raise HTTPException(403, "nu")
'''


def test_D3_POZITIV_HTTPException_in_afara_unei_rute_e_item():
    gasite = S.d3_din_arbore(ast.parse(MODUL_CU_HTTP_IN_AFARA_RUTEI), "proba.py")
    assert len(gasite) == 1 and gasite[0].detector == "D3_HTTP_SUB_HTTP"


def test_D3_NEGATIV_HTTPException_INTR_O_ruta_nu_e_item():
    """O rută CHIAR e stratul HTTP, oriunde ar sta fișierul ei. Fără deosebirea asta, detectorul
    ar raporta stratul HTTP ca pe o încălcare a stratului HTTP."""
    assert S.d3_din_arbore(ast.parse(MODUL_CU_HTTP_IN_RUTA), "proba.py") == []


def test_D3_ANTI_VACUUM_universul_real_si_itemul_cunoscut():
    assert len(S.module_core()) >= 300, "universul modulelor s-a golit"
    gasite = S.d3_http_sub_http()
    assert {(i.fisier, i.linie) for i in gasite} == {("core/spv_rute.py", 42)}, (
        "itemul D3 cunoscut s-a schimbat fără ca proba să fie actualizată: %s" % gasite)


# ============================================================
#  CONTABILITATEA
# ============================================================
def test_contabilitatea_se_inchide():
    n = CL.numaratori()
    assert n["P7_CLASSIFIED_ITEMS"] == n["P7_RAW_ITEMS"]
    assert n["P7_UNCLASSIFIED_ITEMS"] == 0
    assert n["P7_UNEXPLAINED_EXCLUSIONS"] == 0
    assert (n["P7_ACTION_REQUIRED"] + n["P7_ACCEPTABLE_BY_DESIGN"] + n["P7_FALSE_POSITIVES"]
            + n["P7_EVIDENCE_LIMITATIONS"]) == n["P7_RAW_ITEMS"]


def test_fiecare_item_are_o_regula_cu_temei_scris():
    """O clasificare fără temei e o părere. Fiecare regulă își citează linia din textul canonic."""
    for _it, cheie in CL.itemi():
        assert cheie in CL.REGULI, "item fără regulă: %s" % cheie
        r = CL.REGULI[cheie]
        assert r.clasa in (CL.AR, CL.ABD, CL.FP, CL.EL)
        assert r.temei.strip() and r.de_ce.strip()


def test_universurile_sunt_DERIVATE_nu_scrise():
    """Dacă vreun univers ar fi o listă scrisă de mână, cifra ar îmbătrâni în tăcere. Toate trei se
    recalculează din repo la fiecare rulare — proba cere doar să nu fie goale și să se potrivească
    cu ce raportează clasificarea."""
    n = CL.numaratori()
    u = n["universuri"]
    assert u["rute"] == len(S.rute())
    assert u["module_core"] == len(S.module_core())
    assert u["module_fiscale"] == len(S.module_fiscale()[0])
    assert all(v > 0 for v in u.values())
