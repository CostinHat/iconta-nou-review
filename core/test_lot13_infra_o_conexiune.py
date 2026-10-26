# -*- coding: utf-8 -*-
"""Lotul 13, C201 — GARDA: o cerere lucrează pe O SINGURĂ conexiune; conexiunile aplicației poartă termene.

DE CE. Două conexiuni ținute deodată de aceeași cerere fac, cu o operație de structură pe aceeași firmă (`DROP SCHEMA`, o migrare), un
blocaj pe care PostgreSQL nu-l vede (reprodus în `core/test_lot13_infra_blocaj.py`). Pe o singură conexiune, același conflict e un
`deadlock` pe care îl vede și îl oprește. Reparația are două părți, și garda le ține pe amândouă:

  1. STATIC, peste tot codul (`scripts/scan_infra_conexiuni_imbricate.py`, pe modelul lui `scan_tranzactii`): mulțimea funcțiilor
     care țin o conexiune și mai deschid una e EXACT `PERMISE` — un loc nou pică, un loc reparat și uitat aici pică (clichet în
     ambele sensuri). Calibrată pe un corpus sintetic: fiecare formă (două deschideri într-un `with`, `with` imbricat, apel direct,
     apel tranzitiv) e văzută, iar formele corecte (deschideri succesive, conexiunea dată mai departe) nu.
  2. LA RULARE, pe drumurile Control fiscal (cele din C201): fiecare rută a ecranului rulează sub `db.o_singura_conexiune()`, pe o firmă
     efemeră; a doua conexiune ținută deodată ridică și se notează, chiar dacă drumul înghite excepția.
  3. Termenele: orice conexiune din pool-ul aplicației are `lock_timeout` și `idle_in_transaction_session_timeout`; pornirea (și
     numai tranzacția ei) așteaptă fără termen.

Temei: N/A — reparație tehnică (nu aplică o regulă fiscală).
"""
import os
import sys

import pytest

from core import db

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(RAD, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(RAD, "scripts"))
import scan_infra_conexiuni_imbricate as SC  # noqa: E402

#: Singurele locuri în care o funcție ține o conexiune și mai deschide una, fiecare cu motivul. Un loc nou nu intră aici fără motiv
#: scris; un loc reparat iese de aici în același commit.
PERMISE = {
    "core/firma_rezumat.py::recalculeaza_lot -> core/firma_rezumat.py::recalculeaza_firma":
        "`lock_conn` ține blocajul consultativ de SESIUNE al firmei (`pg_try_advisory_lock`) pe toată recalcularea; trebuie să fie "
        "aceeași sesiune la luare și la eliberare (garda `core/test_p2_infrastructura.py`). Nu atinge niciun tabel și, după commitul "
        "de după luare (petic C201 pe firma_rezumat), nu ține nicio tranzacție deschisă — deci nu poate intra în ciclul cu un DDL.",
    "core/firma_rezumat.py::recalculeaza_lot -> core/firma_rezumat.py::recalculeaza_greu":
        "același `lock_conn`, aceeași recalculare (aspectele grele): vezi rândul de mai sus.",
}


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


# ============================================================
#  1. STATIC — peste tot codul
# ============================================================
def test_nicio_functie_nu_tine_doua_conexiuni_in_afara_celor_permise():
    gasite, nedecise = SC.inventar()
    noi = sorted(gasite - set(PERMISE))
    reparate = sorted(set(PERMISE) - gasite)
    assert not noi, ("C201: funcții care țin o conexiune și mai deschid una (o cerere lucrează pe O SINGURĂ conexiune — dă conexiunea "
                     "ținută mai departe, sau închide-o înainte):\n  " + "\n  ".join(noi))
    assert not reparate, "locuri reparate, încă trecute în PERMISE — scoate-le de acolo:\n  " + "\n  ".join(reparate)
    assert not nedecise, ("apeluri omonime din interiorul unei conexiuni, cu o definiție posibilă care deschide una nouă — scanarea nu "
                          "le poate decide; dă apelului un alias de import:\n  " + "\n  ".join(nedecise))


CORPUS = {
    "core/db.py": '''
from contextlib import contextmanager
@contextmanager
def get_conn(schema=None):
    yield None
''',
    "core/ajutor.py": '''
from core import db
def deschide_singur():
    with db.get_conn() as c:
        return c
def deschide_prin_altul():
    return deschide_singur()
def primeste_conexiunea(conn):
    return conn
''',
    "main.py": '''
from core import db
from core import ajutor as _a
def doua_intr_un_with():
    with db.get_conn("s") as cs, db.get_conn() as cp:
        return cs, cp
def with_imbricat():
    with db.get_conn() as c:
        with db.get_conn("s") as c2:
            return c, c2
def apel_care_deschide():
    with db.get_conn() as c:
        return _a.deschide_singur()
def apel_tranzitiv():
    with db.get_conn() as c:
        return _a.deschide_prin_altul()
def succesive_corect():
    with db.get_conn() as c:
        x = c
    with db.get_conn("s") as c2:
        return x, c2
def conexiunea_data_mai_departe_corect():
    with db.get_conn("s") as c:
        return _a.primeste_conexiunea(c)
def deschide_dupa_corect():
    with db.get_conn() as c:
        x = c
    return _a.deschide_singur(), x
''',
}


def test_calibrare_scanarea_vede_fiecare_forma_si_numai_pe_ele(tmp_path):
    fisiere = []
    for rel, text in CORPUS.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        fisiere.append(str(p))
    gasite, nedecise = SC.inventar(fisiere=fisiere, rad=str(tmp_path))
    assert gasite == {
        "main.py::doua_intr_un_with -> " + SC.WITH_DUBLU,
        "main.py::with_imbricat -> main.py::with_imbricat",
        "main.py::apel_care_deschide -> core/ajutor.py::deschide_singur",
        "main.py::apel_tranzitiv -> core/ajutor.py::deschide_prin_altul",
    }, sorted(gasite)
    assert nedecise == []


# ============================================================
#  2. LA RULARE — drumurile Control fiscal, pe o firmă efemeră
# ============================================================
SCH = "ztest_l13_infra_cf"
CUI = "14399840"   # DANTE INTERNATIONAL SA — cifra de control verificată cu algoritmul din CLAUDE.md


@pytest.fixture()
def firma_efemera():
    if not _db_ok():
        pytest.skip("fara baza de date")
    from core import tenant_provisioning as _tp
    _curata()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
        cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('Cabinet sintetic C201') RETURNING id")
        af = cur.fetchone()[0]
        cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id, creat_la) VALUES (%s, 'ZTEST C201 SRL', %s, "
                    "'2020-01-01') RETURNING id", (SCH, af))
        tid = cur.fetchone()[0]
        cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
        cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,tip_decont,platitor_tva,tip_firma,
             regim_fiscal,declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'ZTEST C201 SRL',%s,'Str 1','Buc','B','4719',
             'Banca Test','RO49AAAA1B31007593840000','lunar',true,'srl','micro','Ada','Ada','ADMINISTRATOR')""", (CUI,))
        c.commit()
    try:
        yield tid, af
    finally:
        _curata()


def _curata():
    from core import tenant_stergere as ts
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name = %s", (SCH,))
        r = cur.fetchone()
        if r:
            for t in ts.ordinea_stergerii(list(ts.TABELE_TENANT)):
                cur.execute('DELETE FROM public."%s" WHERE tenant_id = %%s' % t, (r[0],))
            cur.execute("DELETE FROM public.tenants WHERE id = %s", (r[0],))
            cur.execute("DELETE FROM public.accounting_firms WHERE id = %s AND nume = 'Cabinet sintetic C201'", (r[1],))
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def test_rutele_control_fiscal_lucreaza_pe_o_singura_conexiune(firma_efemera, monkeypatch):
    """Fiecare rută a ecranului Control fiscal, cap-coadă, sub garda la rulare. Înainte de reparație (`with db.get_conn(schema) as cs,
    db.get_conn() as cp`), prima rută ridica `ADouaConexiune` la a doua deschidere."""
    from core import auth_api, uc_control_fiscal as ucf
    tid, af = firma_efemera
    # accesul la firmă (`_schema_sau_404` și sub-verificările stocuri / Intrastat): utilizatorul probei are firma efemeră; restul rulează real
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tenant_id: SCH if tenant_id == tid else None)
    ctx = {"uid": 0, "firm": af, "nume": "proba C201", "rol": "admin_firma"}
    an = 2000   # perioadă evident nereală (cea mai veche primită de `_perioada`), pe o firmă sintetică — nicio coliziune cu date reale
    # un verificator care CADE devine constatarea gri „… — eșuată” prin `_constatare_esuata`: se numără apelurile (structura), nu textul
    from core import uc_comun as _ucc
    esuate, _orig = [], _ucc._constatare_esuata
    monkeypatch.setattr(_ucc, "_constatare_esuata", lambda eticheta, *a, **k: esuate.append(eticheta) or _orig(eticheta, *a, **k))
    with db.o_singura_conexiune() as incalcari:
        det = ucf.control_fiscal_detaliu(tid, ctx)
        aud = ucf.control_fiscal_audit_preluare(tid, ctx)
        ist = ucf.control_fiscal_audit_preluare_istoric(tid, ctx)
        ant = ucf.control_fiscal_depuse_anterior(tid, {"perioade": [{"tip": "d300", "an": an, "luna": 1}]}, ctx)
        ext = ucf.control_fiscal_depusa_extern(tid, {"tip": "d300", "an": an, "luna": 2, "data_depunere": "2000-03-20",
                                                     "recipisa": "C201"}, ctx)
        anul = ucf.control_fiscal_anuleaza_marcare(tid, {"tip": "d300", "an": an, "luna": 2}, ctx)
    assert incalcari == [], "a doua conexiune ținută deodată pe un drum Control fiscal:\n" + "\n".join(incalcari)
    assert det["stare"] in ("verde", "galben", "rosu", "gri") and "contabil" in det, det.keys()
    assert "ADouaConexiune" not in repr(det), "o verificare a ecranului a căzut pe garda C201 (înghițită ca constatare)"
    assert esuate == [], esuate   # nicio verificare a ecranului n-a căzut (înainte: căutarea „eșuată” în etichetele constatărilor)
    assert aud.get("data") and ist["rulari"] >= 1
    assert ant["marcate"] == 1 and ant["sarite"] == []              # 01/2000 e dinaintea preluării (firma e din 2020): se marchează
    assert ext["ok"] and ext["recipisa"] == "C201"
    assert anul["anulate"] == 1


def test_garda_insasi_prinde_a_doua_conexiune_si_nu_schimba_aplicatia():
    """Mutația gărzii: fără refuzul din `get_conn`, primul bloc nu ridică. În afara gărzii, aplicația se poartă ca înainte."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    with db.o_singura_conexiune() as incalcari:
        with db.get_conn():
            with pytest.raises(db.ADouaConexiune):
                with db.get_conn():
                    pass
            assert db.conexiuni_tinute() == 1      # refuzul nu lasă contorul stricat
    assert len(incalcari) == 1 and "schema None" in incalcari[0]
    assert db.conexiuni_tinute() == 0
    with db.get_conn():
        with db.get_conn():
            assert db.conexiuni_tinute() == 2
    assert db.conexiuni_tinute() == 0


# ============================================================
#  3. TERMENELE
# ============================================================
def test_optiunile_de_sesiune_si_valorile_lor():
    assert db.optiuni_sesiune({}) == "-c lock_timeout=30s -c idle_in_transaction_session_timeout=10min"
    assert db.optiuni_sesiune({"ICONTA_LOCK_TIMEOUT": "2s", "ICONTA_IDLE_TX_TIMEOUT": "0"}) == \
        "-c lock_timeout=2s -c idle_in_transaction_session_timeout=0"
    with pytest.raises(ValueError):
        db.optiuni_sesiune({"ICONTA_LOCK_TIMEOUT": "30s -c statement_timeout=1"})   # nimic altceva nu intră pe acolo


def test_conexiunile_din_pool_poarta_termenele():
    """Pe conexiunea reală din pool-ul aplicației (`db.init_pool`), nu pe un șir: PostgreSQL le-a primit."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SHOW lock_timeout")
        lock = cur.fetchone()[0]
        cur.execute("SHOW idle_in_transaction_session_timeout")
        idle = cur.fetchone()[0]
    assert (lock, idle) == ("30s", "10min"), (lock, idle)


def test_pornirea_asteapta_fara_termen_numai_in_tranzactia_ei():
    """`instante.blocaj_pornire`: pornirea unui worker așteaptă instalarea altuia (DDL pe toate firmele) — fără termen, ca înainte; la
    capătul tranzacției pornirii conexiunea revine la termenul aplicației."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    from core import instante
    p = db.pool()
    conn = p.getconn()
    try:
        instante.blocaj_pornire(conn)
        with conn.cursor() as cur:
            cur.execute("SHOW lock_timeout")
            assert cur.fetchone()[0] == "0"
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("SHOW lock_timeout")
            assert cur.fetchone()[0] == "30s"
        conn.rollback()
    finally:
        p.putconn(conn)


def test_textul_pentru_contabil_la_termen():
    class _E(Exception):
        def __init__(self, cod, text=""):
            super().__init__(text)
            self.pgcode = cod
    assert db.text_blocaj(_E("55P03")).startswith("Datele firmei sunt ocupate chiar acum")
    assert db.text_blocaj(_E("25P03")).startswith("Operația a durat prea mult")
    assert db.text_blocaj(_E(None, "terminating connection due to idle-in-transaction timeout")).startswith("Operația a durat")
    assert db.text_blocaj(_E("23505")) is None and db.text_blocaj(ValueError("x")) is None
