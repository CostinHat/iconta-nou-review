# -*- coding: utf-8 -*-
"""core/test_reconciliere_d100_wiring.py - GARD end-to-end pentru reconcilierea D100 pe semafor
(control_incrucisat.reconciliaza_declaratii -> _thunk_d100), cablaj, nu logica pura.

Fratele lui test_control_incrucisat_wiring.py, aceeasi clasa de defect: _thunk_d100 replica de mana
orchestrarea din d100.genereaza. Cand d100.pull a fost schimbat sa intoarca (prof, venituri, cheltuieli)
- trei valori, nu doua - iar impozitul pe profit sa se aplice pe PROFIT (venituri - cheltuieli), copia
din thunk a ramas in urma: despacheta doua valori si aplica cota pe VENITURI. Rezultat pe ORICE firma:
  - despachetarea `prof, venituri = pull(...)` ridica ValueError('too many values to unpack (expected 2)');
  - _ruleaza_una PASUL 1 prinde ValueError si il CLASIFICA drept 'gri' (nu se poate genera: date/profil),
    exact opusul intentiei ('deriva de semnatura = ROSU rupt') - un bug de cod ascuns ca lipsa de date,
    cu textul intern Python ('too many values to unpack') scurs in motivul verdictului.
Dupa reparatie thunk-ul CHEAMA d100.deriva_obligatii (sursa unica) -> nu mai poate drifta.

Gardul construieste doua scheme efemere (micro cu venituri; profit cu venituri SI cheltuieli, unde
venituri x cota != (venituri - cheltuieli) x cota) si cere ca reconcilierea D100 sa fie 'verde'. Pe codul
vechi: micro -> gri (crash despachetare), profit -> gri (crash) sau (daca doar aritatea ar fi reparata)
rosu (cota pe venituri, nu pe profit). Oricare != verde -> PICA. Efemer: scheme sterse + rollback."""
import pytest

from core import db as _db, tenant_provisioning as _tp, control_incrucisat


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _constatare_d100(constatari):
    for c in constatari:
        if c.get("declaratie") == "d100":
            return c
    return None


def _profil_sql(regim):
    return ("""INSERT INTO firma_profil
        (id,nume,cui,adresa,oras,judet,caen,banca,iban,tip_decont,platitor_tva,regim_fiscal,tip_firma,
         declarant_nume,declarant_prenume,declarant_functie)
        VALUES (1,'ZTEST D100 SRL','14399840','Str 1','Buc','B','6202','Banca Test',
         'RO49AAAA1B31007593840000','T',false,'%s','srl','Ada','Ada','ADMINISTRATOR')""" % regim)


def _ruleaza(schema, linii):
    """Creeaza schema efemera, insereaza o nota validata cu `linii` (cont_debit,cont_credit,suma) in
    T2/2026, ruleaza reconciliaza_declaratii si intoarce constatarea d100. Rollback + drop la final."""
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), schema))
            cur.execute('SET search_path TO "%s", public' % schema)
            regim = "profit" if "profit" in schema else "micro"
            cur.execute(_profil_sql(regim))
            cur.execute("INSERT INTO inregistrari (data,descriere,status) "
                        "VALUES ('2026-05-15','nota test','validata') RETURNING id")
            nid = cur.fetchone()[0]
            for cd, cc, suma in linii:
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) "
                            "VALUES (%s,%s,%s,%s)", (nid, cd, cc, suma))
        rap = control_incrucisat.reconciliaza_declaratii(conn, schema, 2026, 6)
        return _constatare_d100(rap["constatari"])
    finally:
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
        conn.commit()
        p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d100_micro_reconciliaza_nu_crapa():
    """Micro cu venituri 10000 (credit 707) -> D100 121 = 100 lei. Reconcilierea trebuie sa fie VERDE.
    Pe codul vechi: _thunk_d100 despacheta 2 din 3 -> ValueError -> gri cu 'too many values to unpack'."""
    c = _ruleaza("ztest_d100_micro", [("4111", "707", 10000)])
    assert c is not None, "lipseste constatarea d100 din reconciliere"
    mesaj = (c.get("mesaj") or "")
    assert "unpack" not in mesaj and "too many values" not in mesaj, (
        "reconcilierea D100 a scurs eroarea interna Python (thunk driftat de d100.pull): %r" % mesaj)
    assert c.get("stare") == "verde", (
        "D100 micro nu se reconciliaza (asteptat verde): stare=%r mesaj=%r" % (c.get("stare"), mesaj))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d100_profit_baza_pe_profit_nu_pe_venituri():
    """Profit cu venituri 10000 (credit 707) SI cheltuieli 6000 (debit 607) -> baza = profit 4000,
    impozit 103 = 640 lei (16%). Reconcilierea trebuie VERDE. Pe codul vechi: crash la despachetare (gri)
    sau, daca doar aritatea ar fi reparata, cota aplicata pe VENITURI (10000 x 16% = 1600) != cale2
    (4000 x 16% = 640) -> ROSU fals. Ambele != verde. Prinde SI aritatea SI formula."""
    c = _ruleaza("ztest_d100_profit", [("4111", "707", 10000), ("607", "401", 6000)])
    assert c is not None, "lipseste constatarea d100 din reconciliere"
    mesaj = (c.get("mesaj") or "")
    assert "unpack" not in mesaj and "too many values" not in mesaj, (
        "reconcilierea D100 a scurs eroarea interna Python (thunk driftat de d100.pull): %r" % mesaj)
    assert c.get("stare") == "verde", (
        "D100 profit nu se reconciliaza pe baza corecta (venituri - cheltuieli): stare=%r mesaj=%r"
        % (c.get("stare"), mesaj))
