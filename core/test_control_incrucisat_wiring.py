# -*- coding: utf-8 -*-
"""core/test_control_incrucisat_wiring.py — GARD end-to-end pentru verifica_tva (cablaj, nu logica pura).

Cele 61 de teste din test_control_incrucisat.py exercita compara_tva (functia PURA) cu dict-uri
sintetice. NICIUNUL nu cheama verifica_tva() end-to-end, care ruleaza d300.genereaza pe schema reala.
De aceea o derivare de semnatura a d300.genereaza (schimbat sa ceara un obiect Perioada, nu (an, luna))
a ramas nedetectata: apelul ridica TypeError, prins de `except Exception -> gri`, iar cross-check-ul TVA
a fost MORT tacit (verdict permanent gri, niciodata rosu) — inclusiv in cronul zilnic alerte_control_fiscal.

Gardul cheama verifica_tva pe o schema efemera cu o factura emisa NEcontabilizata (contul 4427 = 0) si
cere stare=='rosu'. Daca apelul d300.genereaza se rupe iar (semnatura, sau except care inghite eroarea),
verdictul redevine 'gri' si testul PICA. Efemer: schema stearsa + rollback la final, fara reziduuri.
"""
import pytest

from core import db as _db, tenant_provisioning as _tp, control_incrucisat

SCH = "ztest_ci_wiring"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_verifica_tva_prinde_factura_necontabilizata_end_to_end():
    """Factura emisa cu TVA 210, fara nota validata (4427=0) -> verifica_tva ROSU (nu gri).
    Exercita calea reala verifica_tva -> d300.genereaza(Perioada) care s-a rupt (bug semnatura)."""
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("""INSERT INTO firma_profil
                (id,nume,cui,adresa,oras,judet,caen,banca,iban,tip_decont,platitor_tva,
                 declarant_nume,declarant_prenume,declarant_functie)
                VALUES (1,'ZTEST WIRING SRL','14399840','Str 1','Buc','B','6202','Banca Test',
                 'RO49AAAA1B31007593840000','lunar',true,'Ada','Ada','ADMINISTRATOR')""")
            cur.execute("""INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status)
                VALUES ('E-1','2026-06-10','emisa',1210,210,'RO14399840','CLIENT SRL','emisa') RETURNING id""")
            fid = cur.fetchone()[0]
            cur.execute("""INSERT INTO factura_linii (factura_id,descriere,cantitate,pret_unitar,cota_tva)
                VALUES (%s,'serviciu',1,1000,21)""", (fid,))
        # calea reala: verifica_tva -> d300.genereaza (aici s-a rupt semnatura)
        r = control_incrucisat.verifica_tva(conn, SCH, 2026, 6)
        assert r["stare"] == "rosu", (
            "verifica_tva a intors %r, asteptat 'rosu'. Daca e 'gri', apelul d300.genereaza "
            "s-a rupt iar (semnatura/except): %s" % (r["stare"], r.get("limita")))
        etichete = [c.get("eticheta", "") for c in r["constatari"]]
        assert any("TVA colect" in e for e in etichete), (
            "lipseste constatarea 'TVA colectata' necontabilizata: %s" % etichete)
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)
