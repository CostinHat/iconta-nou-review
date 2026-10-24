# -*- coding: utf-8 -*-
"""Lotul 12, comanda 12.1, pachetul `ctrl` — deficiența 463: „e-Factura / SPV: termene SPV absente din Control fiscal; lipsa dreptului
aflată târziu”.

CE ERA. Control fiscal urmărea numai declarațiile. O factură emisă care trebuia transmisă în RO e-Factura și nu era (sau fusese respinsă)
se vedea doar deschizând factura („netrimisă în SPV · termen … (depășit)”), iar lipsa dreptului SPV pe CUI-ul firmei se afla abia la
„Trimite în SPV”, ca refuz.

CE E ACUM. `control_fiscal_api.facturi_spv_netransmise` (starea și termenul din `facturi_api._cu_stare_spv`, sursa unică a istoricului)
dă lista de la luna preluării; `uc_comun.constatari_efactura` face din ea constatările firmei (rândul din listă, pastila: galben), iar
detaliul are secțiunea «e-Factura — transmiterea în SPV», cu fiecare factură, termenul ei și starea dreptului SPV.

Temei: OUG 120/2021 art.10 alin.(7) — „Termenul-limită pentru transmiterea facturilor în sistemul național privind factura electronică
RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii” (anaf_surse/oug_120_2021.txt); art.10 alin.(1) — obligația de
transmitere în relația B2B cu persoane impozabile stabilite în România (`facturi_api.spv_obligatorie`).
Perioade sintetice nu se pot folosi (testul e despre „termen trecut față de azi”): ziua e dată explicit, iar schema e efemeră, ștearsă.
"""
import datetime
import os
import re

import pytest

from core import db as _db, tenant_provisioning as _tp
from core import control_fiscal_api as _cf, uc_comun

SCH = "ztest_l12c_463"
AZI = datetime.date(2026, 10, 23)
CUI_CLIENT = "14399840"   # DANTE INTERNATIONAL SA — cifra de control verificată
# CUI-ul firmei de probă: 46300014 — cifra de control verificată cu algoritmul din CLAUDE.md (sintetic, nu o firmă reală)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def firma_cu_facturi():
    """Firmă preluată în 09/2026, cu facturi emise: F 1 din 20.08 (înainte de preluare), F 2 din 01.10 (RO, netrimisă: termen 08.10,
    depășit), F 3 din 21.10 (RO, netrimisă: termen 28.10), F 4 din 02.10 (client din Irlanda: fără obligație), F 5 din 05.10 (acceptată
    de ANAF), F 6 din 06.10 (respinsă de ANAF, termen 13.10, depășit)."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
        cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
        cur.execute("""INSERT INTO firma_profil (id,nume,cui,tip_decont,platitor_tva,tip_firma,regim_fiscal,luna_preluare)
             VALUES (1,'ZTEST L12 463 SRL','46300014','lunar',true,'srl','micro','2026-09-01')""")
        ids = {}
        for nr, data, cui, tara in (("1", "2026-08-20", CUI_CLIENT, "RO"), ("2", "2026-10-01", CUI_CLIENT, "RO"),
                                    ("3", "2026-10-21", CUI_CLIENT, "RO"), ("4", "2026-10-02", "IE9999999ZZ", "IE"),
                                    ("5", "2026-10-05", CUI_CLIENT, "RO"), ("6", "2026-10-06", CUI_CLIENT, "RO")):
            cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva, tert_cui, tert_nume, tert_tara, status) "
                        "VALUES (%s, 'F', %s, 'emisa', 121, 21, %s, 'CLIENT SRL', %s, 'emisa') RETURNING id", ("F" + nr, data, cui, tara))
            ids[nr] = cur.fetchone()[0]
        for nr, stare, err in (("5", "ok", None), ("6", "nok", "BR-RO-010 cod poștal")):
            cur.execute("INSERT INTO efactura_trimiteri (factura_id, mediu, stare, error_message, xml_sha256) VALUES (%s,'prod',%s,%s,'x')",
                        (ids[nr], stare, err))
        c.commit()
    try:
        yield ids
    finally:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


def test_facturile_netransmise_de_la_luna_preluarii_cu_termenul_lor(firma_cu_facturi):
    with _db.get_conn(SCH) as cs:
        lista = _cf.facturi_spv_netransmise(cs, (2026, 9), AZI)
    pe_numar = {f["numar"]: f for f in lista}
    # F 1 (înainte de preluare), F 4 (fără obligație, art.10 alin.(1)), F 5 (acceptată) nu sunt de transmis
    assert sorted(pe_numar) == ["F nr. 2", "F nr. 3", "F nr. 6"], sorted(pe_numar)
    # OUG 120/2021 art.10 alin.(7): 5 zile lucrătoare de la emitere — 01.10 (joi) -> 08.10; 21.10 (miercuri) -> 28.10; 06.10 -> 13.10
    assert (pe_numar["F nr. 2"]["termen"], pe_numar["F nr. 2"]["depasit"]) == ("2026-10-08", True)
    assert (pe_numar["F nr. 3"]["termen"], pe_numar["F nr. 3"]["depasit"]) == ("2026-10-28", False)
    assert (pe_numar["F nr. 6"]["stare"], pe_numar["F nr. 6"]["depasit"], pe_numar["F nr. 6"]["eroare"]) == ("respinsa", True,
                                                                                                         "BR-RO-010 cod poștal")


def test_constatarile_firmei_termen_depasit_si_drept_spv(firma_cu_facturi):
    with _db.get_conn(SCH) as cs:
        lista = _cf.facturi_spv_netransmise(cs, (2026, 9), AZI)
    fara_conexiune = uc_comun.constatari_efactura(lista, {"conectat": False}, 2026, 10)
    assert [c["eticheta"] for c in fara_conexiune] == [uc_comun.ETICHETA_SPV_DEPASIT, uc_comun.ETICHETA_SPV_FARA_DREPT], fara_conexiune
    assert all(c["stare"] == "galben" for c in fara_conexiune), fara_conexiune
    m = fara_conexiune[0]["mesaj"]
    assert m == ("2 facturi emise n-au fost transmise în SPV în 5 zile lucrătoare (cea mai veche: F nr. 2 din 01.10.2026, către "
                 "CLIENT SRL, termen 08.10.2026)."), m
    assert fara_conexiune[0]["temei"] == _cf.TEMEI_TERMEN_SPV and _cf.TEMEI_TERMEN_SPV.startswith("OUG 120/2021 art.10 alin.(7): "), \
        fara_conexiune[0]["temei"]
    assert fara_conexiune[1]["mesaj"] == ("3 facturi de transmis în SPV, dar facturile nu pot pleca din aplicație: cabinetul nu e "
                                          "conectat la SPV."), fara_conexiune[1]["mesaj"]
    fara_drept = uc_comun.constatari_efactura(lista, {"conectat": True, "are_drept": False, "mesaj": "Fără drept pe CUI 46300014."},
                                              2026, 10)
    assert fara_drept[1]["mesaj"].endswith("nu pot pleca din aplicație: Fără drept pe CUI 46300014."), fara_drept[1]["mesaj"]
    cu_drept = uc_comun.constatari_efactura(lista, {"conectat": True, "are_drept": True}, 2026, 10)
    assert [c["eticheta"] for c in cu_drept] == [uc_comun.ETICHETA_SPV_DEPASIT], cu_drept
    # fără nimic de transmis, dreptul lipsă nu e o constatare (se vede în secțiunea SPV, nu urcă firma)
    assert uc_comun.constatari_efactura([], {"conectat": False}, 2026, 10) == []


def test_ecranul_scoate_din_verificari_contabile_exact_constatarile_e_factura():
    """Secțiunea «e-Factura» le arată în detaliu; `DEJA_IN_EFACTURA` din `control_verdict.js` e oglinda etichetelor din `uc_comun`."""
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    js = open(os.path.join(rad, "static", "js", "ecrane", "control_verdict.js"), encoding="utf-8").read()
    m = re.search(r"const DEJA_IN_EFACTURA = \[(.*?)\];", js, re.S)
    assert m, "DEJA_IN_EFACTURA lipsește din control_verdict.js"
    assert re.findall(r'"([^"]+)"', m.group(1)) == [uc_comun.ETICHETA_SPV_DEPASIT, uc_comun.ETICHETA_SPV_FARA_DREPT]
    # pe ARBORE (core/arbore_js.py): termenii sumei întoarse de `randeazaCorpVerdict` (instrucțiunea din corpul ei, nu dintr-o funcție
    # imbricată) cuprind secțiunea e-Factura
    from core.arbore_js import arbore_js, functia
    arb, cod = arbore_js("control_verdict.js")
    intoarse = [n["argument"] for n in functia(arb, "randeazaCorpVerdict")["body"]["body"] if n["type"] == "ReturnStatement"]

    def termeni(n):
        return termeni(n["left"]) + termeni(n["right"]) if n["type"] == "BinaryExpression" and n["operator"] == "+" else [cod(n)]
    assert len(intoarse) == 1 and set(termeni(intoarse[0])) >= {"declaratii", "sectEfactura"}, \
        "secțiunea e-Factura nu e în corpul verdictului: %s" % [cod(n) for n in intoarse]
