# -*- coding: utf-8 -*-
"""[deficiența 406, retestul Costin 19.10.2026, PRIORITAR] „Casă: plată 200 cu sold 142 acceptată, registru −58; validarea a trecut;
refuz la salvare și blocare la validare.”

Temei: OMFP 1802/2014, funcțiunea contului 531: „Contul 531 "Casa" este un cont de activ. [...] Soldul contului reprezintă numerarul
existent în casierie.” (anaf_surse/omfp_1802_2014.html) — numerarul existent nu poate fi sub zero.
Schemă efemeră din template, ștearsă la ieșire. Perioade 2026 pe o schemă proprie (nu tabele partajate)."""
import datetime
import io
from decimal import Decimal

import pytest

from core import casa_api as _ca, casa_sold as _cs, db as _db, jurnal_api as _j, tenant_provisioning as _tprov

_SCH = "efemer_casa_negativa"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,declarant_nume,declarant_prenume,
                           declarant_functie,platitor_tva) VALUES (1,'F1 SRL','RO14399840','s','B','B','e@x.ro','07','4690','P','I','A',true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _op(data, cat, suma, doc):
    # furnizorul n-are facturi deschise: plata e avans acordat (407), pe bunuri (4091 = 5311)
    return {"data": data, "categorie": cat, "suma": suma, "document": doc, "partener": "X SRL", "cui": "14399840",
            "avans_destinatie": "stocuri"}


def test_plata_peste_sold_e_refuzata_la_salvare(conn):
    assert _ca.adauga(conn, _SCH, _op("2026-10-15", "ridicare_banca", 142, "DI1")).get("eroare") is None
    r = _ca.adauga(conn, _SCH, _op("2026-10-19", "plata_furnizor", 200, "DP1"))
    assert r == {"cod": "CASA_NEGATIVA", "eroare": (
        "Plată către furnizor de 200,00 lei nu încape în casă (contul 5311): soldul casei pe 19.10.2026, în registru, e 142,00 lei, iar "
        "după ea casa ar ajunge la -58,00 lei pe 19.10.2026. Numerarul din casă nu poate fi negativ. Înregistrează întâi încasarea sau "
        "ridicarea de numerar din care s-a plătit.")}, r
    # nimic scris: o singură operațiune în registru, soldul final 142
    reg = _ca.registru(conn, _SCH, 2026, 10)
    assert [o["suma"] for o in reg["operatiuni"]] == ["142.00"] and reg["sold_final"] == "142.00", reg
    # previzualizarea spune același refuz înainte de „Adaugă”
    assert _ca.previzualizare(conn, _SCH, _op("2026-10-19", "plata_furnizor", 200, "DP1"))["refuz"] == r["eroare"]
    assert _ca.adauga(conn, _SCH, _op("2026-10-19", "plata_furnizor", 142, "DP2")).get("eroare") is None   # încape exact


def test_plata_pusa_in_trecut_strica_soldurile_de_dupa(conn):
    """O plată datată înaintea încasării: casa e zero în ziua ei — refuzată, deși soldul de azi ar acoperi-o."""
    _ca.adauga(conn, _SCH, _op("2026-10-15", "ridicare_banca", 500, "DI1"))
    r = _ca.adauga(conn, _SCH, _op("2026-10-10", "avans_decontare", 50, "DP1"))
    assert r["cod"] == "CASA_NEGATIVA" and r["eroare"].startswith(
        "Avans spre decontare de 50,00 lei nu încape în casă (contul 5311): soldul casei pe 10.10.2026, în registru, e 0,00 lei"), r
    # plata de azi care ar strica o plată deja înregistrată mai târziu
    _ca.adauga(conn, _SCH, _op("2026-10-20", "depunere_banca", 400, "DD1"))
    r = _ca.adauga(conn, _SCH, _op("2026-10-16", "plata_furnizor", 150, "DP2"))
    assert r["cod"] == "CASA_NEGATIVA" and r["eroare"].endswith(
        "casa ar ajunge la -50,00 lei pe 20.10.2026, după operațiunile înregistrate până atunci. Numerarul din casă nu poate fi negativ. "
        "Înregistrează întâi încasarea sau ridicarea de numerar din care s-a plătit."), r


def test_validarea_e_blocata_pe_evidenta_validata(conn):
    """Nota de plată nu se validează cât timp încasarea din care s-a plătit e ciornă; după validarea încasării, trece."""
    inc = _ca.adauga(conn, _SCH, _op("2026-10-15", "ridicare_banca", 142, "DI1"))
    pl = _ca.adauga(conn, _SCH, _op("2026-10-19", "plata_furnizor", 100, "DP1"))
    r = _j.valideaza(conn, _SCH, pl["inregistrare_id"])
    assert r["cod"] == "CASA_NEGATIVA" and r["eroare"] == (
        "Nota de 100,00 lei nu încape în casă (contul 5311): soldul casei pe 19.10.2026, în evidența validată, e 0,00 lei, iar după ea "
        "casa ar ajunge la -100,00 lei pe 19.10.2026. Numerarul din casă nu poate fi negativ. Înregistrează întâi încasarea sau "
        "ridicarea de numerar din care s-a plătit (și valideaz-o)."), r
    with conn.cursor() as cur:
        cur.execute("SELECT status FROM inregistrari WHERE id = %s", (pl["inregistrare_id"],))
        assert cur.fetchone()[0] == "ciorna"
    assert _j.valideaza(conn, _SCH, inc["inregistrare_id"]).get("eroare") is None
    assert _j.valideaza(conn, _SCH, pl["inregistrare_id"]).get("eroare") is None


def test_nota_manuala_pe_5311_si_analiticul_trec_prin_aceeasi_regula(conn):
    """Drumul notei manuale (nu dispoziția): creditul pe analiticul 5311.01 se refuză la validare."""
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES ('2026-10-19','Plată','manual','ciorna',
                       'Chitanța 7 din 19.10.2026') RETURNING id""")
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'628','5311.01',30)", (nid,))
    assert _j.valideaza(conn, _SCH, nid)["cod"] == "CASA_NEGATIVA"
    assert _cs.sintetic_casa("5311.01") == "5311" and _cs.sintetic_casa("5121") is None and _cs.sintetic_casa("5314") == "5314"


def test_registrul_porneste_de_la_soldul_casei_nu_de_la_zero(conn):
    """Soldul de preluare (31.08.2026) + septembrie -> soldul de la 1 octombrie; plafonul și sold_final îl folosesc."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES ('5311',300,0,'2026-08-31')")
    _ca.adauga(conn, _SCH, _op("2026-09-10", "ridicare_banca", 200, "DI1"))
    reg = _ca.registru(conn, _SCH, 2026, 10)
    assert (reg["sold_initial"], reg["sold_final"]) == ("500.00", "500.00"), reg
    with conn.cursor() as cur:
        assert _cs.sold_inainte(cur, _SCH, "5311", datetime.date(2026, 9, 1)) == Decimal("300.00")
    # plata din soldul preluat încape
    assert _ca.adauga(conn, _SCH, _op("2026-10-02", "plata_furnizor", 450, "DP1")).get("eroare") is None


def test_stornarea_incasarii_trece_prin_aceeasi_regula(conn):
    inc = _ca.adauga(conn, _SCH, _op("2026-10-15", "ridicare_banca", 142, "DI1"))
    assert _j.valideaza(conn, _SCH, inc["inregistrare_id"]).get("eroare") is None
    _ca.adauga(conn, _SCH, _op("2026-10-16", "plata_furnizor", 100, "DP1"))
    r = _ca.storneaza(conn, _SCH, inc["id"], "2026-10-17")
    assert r["cod"] == "CASA_NEGATIVA" and r["eroare"].startswith("Stornarea încasării de 142,00 lei nu încape în casă"), r
