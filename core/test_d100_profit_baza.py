# -*- coding: utf-8 -*-
"""GARD D100 (16.08.2026, campanie rețeta D300, pas 5/8) — baza impozitului pe PROFIT reparata.

BUG (grav, trecea toate gardurile): obligatia de profit (cod 103) = venituri x 16%, in loc de profit x 16%.
Impozitul pe profit se aplica pe PROFIT (venituri - cheltuieli +/- ajustari), NU pe venitul brut (CF art.17
"cota ... asupra profitului impozabil"; struct d100 poz.2 cod 103 "Impozit pe profit"). Un SRL cu venituri
1M si profit 100k primea o obligatie de 160k in loc de 16k - DUK-valid dar grosolan gresit. Eroarea era
PARTAJATA de ambele cai de reconciliere (ambele foloseau venituri x cota) -> nimeni n-o prindea.

FIX: pull() citeste si cheltuielile (6xx debit); pentru regim profit baza = venituri(70x) - cheltuieli(6xx)
(profit contabil; ajustarile fiscale + regularizarea la D101, avertizat). Profit <= 0 -> fara avans (refuz cu
mesaj de PIERDERE, nu "venituri=0" fals). Reconcilierea foloseste ACEEASI baza (fara fals-pozitiv). Micro
neschimbat (baza = venituri). Aserturi ASCII.
"""
import pytest
from core.common import Perioada
from core import d100
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d100_profit"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _setup(cur, venituri, cheltuieli, regim="profit"):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,"
                "platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                "(1,'PROBA PROFIT SRL','14399840','Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001',"
                "'%s',true,'L','Pop','Ion','administrator')" % regim)
    if venituri:
        cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere) VALUES ('2026-05-15','validata','t','V') RETURNING id")
        iv = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'4111','704',%s)", (iv, venituri))
    if cheltuieli:
        cur.execute("INSERT INTO inregistrari (data,status,sursa,descriere) VALUES ('2026-05-16','validata','t','C') RETURNING id")
        ic = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) VALUES (%s,'607','401',%s)", (ic, cheltuieli))


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_profit_baza_e_profit_nu_venituri(conn):
    """Venituri 100000, cheltuieli 60000 -> profit 40000 -> obligatie 103 = 40000 x 16% = 6400.
    RED pre-fix: venituri x 16% = 16000."""
    with conn.cursor() as cur:
        _setup(cur, 100000, 60000)
    conn.commit()
    _xml, res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=2))
    o = [x for x in res.obligatii if str(x.cod_oblig) == "103"]
    assert o and int(o[0].suma_dat) == 6400, "profit 40000 x 16%% = 6400; gasit %r (pre-fix ar fi 16000)" % (
        o and int(o[0].suma_dat))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_profit_fara_cheltuieli_neschimbat(conn):
    """CONTROL backward-compat: fara cheltuieli 6xx -> profit = venituri -> obligatie neschimbata (venituri x 16%)."""
    with conn.cursor() as cur:
        _setup(cur, 100000, 0)
    conn.commit()
    _xml, res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=2))
    o = [x for x in res.obligatii if str(x.cod_oblig) == "103"]
    assert o and int(o[0].suma_dat) == 16000, "fara cheltuieli: 100000 x 16%% = 16000"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_profit_pierdere_refuz_cu_mesaj_corect(conn):
    """Cheltuieli > venituri (pierdere) -> fara avans, refuz cu mesaj de PIERDERE (nu 'venituri=0' fals)."""
    with conn.cursor() as cur:
        _setup(cur, 50000, 80000)
    conn.commit()
    with pytest.raises(ValueError) as ei:
        d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=2))
    assert "PIERDERE" in str(ei.value), "pierderea trebuie numita explicit: %s" % ei.value


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_micro_baza_ramane_venituri(conn):
    """CONTROL: regim micro -> baza = venituri (NU se scad cheltuielile). 100000 x 1%% = 1000."""
    with conn.cursor() as cur:
        _setup(cur, 100000, 60000, regim="micro")
    conn.commit()
    _xml, res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=2))
    o = [x for x in res.obligatii if str(x.cod_oblig) == "121"]
    assert o and int(o[0].suma_dat) == 1000, "micro: venituri 100000 x 1%% = 1000 (cheltuielile nu scad baza)"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_profit_reconciliere_trece_si_duk_valid(conn):
    """Reconcilierea a-doua-cale foloseste ACEEASI baza (profit) -> nu da fals-pozitiv; D100 DUK-valid."""
    from core import duk
    with conn.cursor() as cur:
        _setup(cur, 100000, 60000)
    conn.commit()
    xml, _res = d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=2))  # reconcilierea wired -> crapa daca divergenta
    assert "<declaratie100" in xml
    if duk.poate_valida("d100"):
        rez = duk.valideaza(xml, "d100", an=2026, luna=6)
        assert rez["stare"] == "valid", "D100 profit trebuie DUK-valid; rez=%r" % rez
