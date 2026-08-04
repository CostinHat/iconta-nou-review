# -*- coding: utf-8 -*-
"""D390 art.284 "ziua 15" (A2): incadrarea in perioada pe EXIGIBILITATE = MIN(data_emitere, ziua 15 a lunii
urmatoare faptului generator). Camp data_faptului_generator OPTIONAL - NULL pastreaza comportamentul anterior
(data_emitere). Test round-trip pe schema scratch (gated pe DB)."""
import pytest


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_migrare_si_exigibilitate_ziua15():
    from core import db, d390
    import core.migrare_d390_faptul_generator as m
    SCH = "efemer_d390_test_a2"
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('DROP SCHEMA IF EXISTS %s CASCADE' % SCH)
                cur.execute('CREATE SCHEMA %s' % SCH)
                cur.execute('CREATE TABLE %s.firma_profil (id int PRIMARY KEY, nume text, cui text, adresa text, oras text, judet text, email text, telefon text, declarant_nume text, declarant_prenume text, declarant_functie text)' % SCH)
                cur.execute("INSERT INTO %s.firma_profil VALUES (1,'TEST SRL','RO14399840','Str 1','Buc','B','e@x.ro','0722','P','I','ADMIN')" % SCH)
                cur.execute('CREATE TABLE %s.clienti (id int PRIMARY KEY, nume text, cui text)' % SCH)
                # facturi VECHI - fara coloana (ca sa probam migrarea idempotenta)
                cur.execute('CREATE TABLE %s.facturi (id int PRIMARY KEY, client_id int, tert_nume text, tert_cui text, data_emitere date NOT NULL, total numeric, tva numeric, directie varchar(10))' % SCH)
            conn.commit()

        # migrare idempotenta
        with db.get_conn() as conn:
            assert m.verifica(conn, SCH) is False
            m.aplica(conn, SCH); conn.commit()
        with db.get_conn() as conn:
            m.aplica(conn, SCH); conn.commit()   # a doua oara -> fara eroare
            assert m.verifica(conn, SCH) is True

        with db.get_conn() as conn:
            with conn.cursor() as cur:
                # A: emisa iulie, FARA fapt -> exigibilitate = data_emitere = IULIE (backward-compat)
                cur.execute("INSERT INTO %s.facturi (id,tert_cui,tert_nume,data_emitere,total,tva,directie) VALUES (1,'DE811569869','X','2026-07-20',1000,0,'emisa')" % SCH)
                # B: emisa TARZIU (aug 20) + fapt iunie -> deadline 15.07 -> exigibilitate 15.07 -> IULIE (mutata din aug)
                cur.execute("INSERT INTO %s.facturi (id,tert_cui,tert_nume,data_emitere,data_faptului_generator,total,tva,directie) VALUES (2,'DE811569869','X','2026-08-20','2026-06-10',2000,0,'emisa')" % SCH)
                # C (control backward-compat): emisa aug, FARA fapt -> AUGUST
                cur.execute("INSERT INTO %s.facturi (id,tert_cui,tert_nume,data_emitere,total,tva,directie) VALUES (3,'DE811569869','X','2026-08-20',3000,0,'emisa')" % SCH)
            conn.commit()

        def totaluri(an, luna):
            with db.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute('SET search_path TO %s' % SCH)
                _p, fact = d390.pull(conn, SCH, an, luna)
            return sorted(int(round(float(f["total"]))) for f in fact)

        # IULIE: A (fara fapt) + B (mutata pe exigibilitate 15.07)
        assert totaluri(2026, 7) == [1000, 2000], totaluri(2026, 7)
        # AUGUST: doar C (backward-compat, fara fapt); B s-a mutat in iulie
        assert totaluri(2026, 8) == [3000], totaluri(2026, 8)
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('DROP SCHEMA IF EXISTS %s CASCADE' % SCH)
            conn.commit()
