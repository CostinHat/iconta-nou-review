# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 434 — comanda Costin 10.2 pct.4, verbatim] „la F1, borderoul de achiziție nou (Maria Ionescu, 20.10) a primit
numărul BA-1, deși BA-1 există deja (Ion Popescu, 19.10). Numerotarea borderourilor e unică și continuă.”

Cauza: contorul documentelor interne (`documente_interne_contor`) era SINGURA sursă a numărului, iar un număr scris de mână (sau
scris înaintea contorului) nu-l mișca. Clasa: toate documentele interne numerotate de `documente_interne` (bonul de consum, nota de
calcul, lista de inventariere ...), al căror număr se poate scrie și de mână în „Document justificativ”.
Temei: OMFP 2634/2015 anexa 1 pct.2 — documentul justificativ cuprinde „denumirea, numărul și data întocmirii documentului”; un număr
dat a doua oară nu mai identifică documentul. Schemă efemeră din template, în tranzacție anulată."""
import contextlib
import io
import re

import psycopg2
import pytest

from core import db as _db, erori, tenant_provisioning as _tp

SCH = "tenant_test_434_borderou"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _P:
    def __init__(s, c): s._c = c
    def commit(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@pytest.fixture
def conn(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                            "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
            from core import auth_api, uc_comun, uc_tenants
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_P(c)))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
            yield c
        finally:
            c.rollback()


_ION = {"data": "2026-10-19", "furnizor_nume": "Ion Popescu", "furnizor_adresa": "Str. Florilor 1, Ploiești", "furnizor_act": "PH 123456",
        "valoare": 200, "cont_cheltuiala": "371", "articol": "Grâu", "cantitate": 100, "um": "kg"}
_MARIA = {**_ION, "data": "2026-10-20", "furnizor_nume": "Maria Ionescu", "furnizor_act": "PH 654321", "valoare": 150}


def _borderou(corp):
    from core import uc_tenants
    return uc_tenants.achizitie_neinregistrat(1, dict(corp), {"uid": 1})


def _numere(c):
    with c.cursor() as cur:
        cur.execute("SELECT numar, tert_nume FROM facturi WHERE tip = 'borderou' ORDER BY id")
        return cur.fetchall()


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def test_def_434_borderoul_nou_continua_dupa_numarul_scris_de_mana(conn):
    """Cazul F1: BA-1 scris de mână (Ion Popescu, 19.10), apoi borderoul fără număr (Maria Ionescu, 20.10) -> BA-2, nu BA-1 a doua oară."""
    assert _borderou({**_ION, "numar": "BA-1"})["numar"] == "BA-1"
    r = _borderou(_MARIA)
    # comanda 10.2 pct.4: „Numerotarea borderourilor e unică și continuă” — după BA-1 vine BA-2
    assert r["numar"] == "BA-2", r
    assert _numere(conn) == [("BA-1", "Ion Popescu"), ("BA-2", "Maria Ionescu")]
    # continuă și după: al treilea borderou fără număr -> BA-3
    assert _borderou({**_MARIA, "furnizor_nume": "Vasile Pop"})["numar"] == "BA-3"


def test_def_434_numarul_scris_de_mana_deja_dat_se_refuza_langa_camp(conn):
    _borderou({**_ION, "numar": "BA-1"})
    with pytest.raises(erori.DateInvalide) as e:
        _borderou({**_MARIA, "numar": " ba-1 "})   # aceeași formă ca indexul: fără spații, fără deosebire de literă
    d = e.value.args[0]
    # comanda 10.2 pct.4: „unică” — refuzul numește borderoul care are deja numărul și numărul următor
    assert [x["camp"] for x in d["erori_campuri"]] == ["op-numar"], d
    camp = d["erori_campuri"][0]["mesaj"]
    # lângă câmp: al cui e numărul (borderoul, data, vânzătorul) și numărul următor — exact datele astea, nimic în plus
    assert re.findall(r"BA-\d+", camp) == ["BA-1", "BA-2"], camp
    assert re.findall(r"\d\d\.\d\d\.\d{4}", camp) == ["19.10.2026"] and re.findall(r"\(([^)]*)\)", camp) == ["Ion Popescu", "BA-2"], camp
    # jos: regula, nu a doua oară ce stă lângă câmp (DS cap.6 v2.89 „un mesaj, o singură dată”)
    assert d["mesaj"] and camp not in d["mesaj"] and re.findall(r"BA-\d+|Ion Popescu", d["mesaj"]) == [], d
    assert _numere(conn) == [("BA-1", "Ion Popescu")]   # nimic scris


def test_def_434_baza_refuza_dublura_pe_orice_drum(conn):
    """Gardul din bază (`facturi_borderou_numar_an_uniq`): o scriere directă cu un număr deja dat în același an pică."""
    _borderou({**_ION, "numar": "BA-1"})
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT s")
        with pytest.raises(psycopg2.errors.UniqueViolation):
            cur.execute("INSERT INTO facturi (numar, data_emitere, directie, tip, status) VALUES ('ba-1 ', '2026-12-01', 'primita', "
                        "'borderou', 'importata')")
        cur.execute("ROLLBACK TO SAVEPOINT s")
        # alt an: numerotarea pe an (documente_interne_contor pe tip și an) — BA-1 din 2027 e alt document
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, tip, status) VALUES ('BA-1', '2027-01-05', 'primita', "
                    "'borderou', 'importata')")


def test_434_clasa_bonul_de_consum_continua_dupa_numarul_scris_de_mana(conn):
    """Clasa: orice document intern numerotat de `documente_interne` continuă după cel mai mare număr existent al anului lui, nu după
    contor. O notă cu „Bon de consum nr 4 din 05.10.2026” scrisă de mână -> bonul generat e nr 5; „nr 9” din 2025 nu contează."""
    from core import documente_interne as di
    with conn.cursor() as cur:
        for ref, data in (("Bon de consum nr 4 din 05.10.2026", "2026-10-05"), ("Bon de consum nr 9 din 05.10.2025", "2025-10-05")):
            cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'consum', 'manual', 'ciorna', %s)",
                        (data, ref))
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2026-10-20', 'consum', 'stocuri', 'ciorna') RETURNING id")
        nid = cur.fetchone()[0]
        # OMFP 2634/2015 anexa 1 pct.2: „denumirea, numărul și data întocmirii documentului” — nr 4 e deja dat, următorul e 5
        assert di.genereaza(cur, SCH, "bon_consum", "2026-10-20", [nid]) == "Bon de consum nr 5 din 20.10.2026"
        assert di.cel_mai_mare(cur, SCH, "bon_consum", 2025) == 9
