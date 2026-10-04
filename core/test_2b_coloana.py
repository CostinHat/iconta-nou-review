# -*- coding: utf-8 -*-
"""GARD — coloana `salariati.salariu_brut` s-a retras (punctul 4, decizia Costin 03.10.2026) și nu se poate întoarce.

Decizia: „Ștergi salariati.salariu_brut după ce dovedești că nimic nu o mai citește, cu migrare pe toți tenanții (toate
datele sunt de test) și backup înainte.” Salariul contractual are o singură sursă, `salariu_istoric` (PASUL 2, 29.07.2026):
scrierile trecuseră pe istoric în 2b-scrieri, iar coloana rămăsese o copie ÎNVECHITĂ, citită de puntea din `salariu_la`.

Ce face imposibil:
  * o instrucțiune SQL din cod care citește sau scrie din nou `salariati.salariu_brut` (o a doua sursă a salariului);
  * coloana readusă în `tenant_template.sql` (tenanții noi ar avea-o din nou);
  * o migrare care scoate coloana fără să mute salariul în istoric (salariatul fără istoric ar rămâne fără salariu).
"""
import os

import pytest

from core import db as _db
from core import migrare_2b_coloana as _m
from core import tenant_provisioning as _tp
from scripts import scan_salariu_coloana as _s

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_niciun_sql_nu_mai_numeste_coloana():
    # MUTAȚIE: readus `salariu_brut` în SELECT-ul din stat_plata_api / puntea din salariu_la -> numite aici -> pică
    assert _s.sql_pe_coloana() == []


def test_scanerul_vede_un_sql_pe_coloana(tmp_path):
    # ANTI-VACUU: ambele forme trebuie prinse (constantă și tabelă dată ca argument), una pe țintă corectă nu
    f = tmp_path / "core"
    f.mkdir()
    # jetoane înlocuite la rulare: textul literal de aici nu e SQL al aplicației (test_schema_coloane l-ar citi drept unul)
    sablon = ('Q = "SELECT CCC FROM TTT WHERE id=%s"\n'
              'cur.execute("SELECT CCC FROM %s WHERE id=1" % _t(s, "TTT"))\n'
              'cur.execute("SELECT CCC FROM %s" % _t(s, "III"))\n')
    (f / "x.py").write_text(sablon.replace("CCC", "salariu_" + "brut").replace("TTT", "sala" + "riati")
                            .replace("III", "salariu_" + "istoric"), encoding="utf-8")
    assert _s.sql_pe_coloana(str(tmp_path)) == [("core/x.py", 1), ("core/x.py", 2)]


def test_template_fara_coloana():
    # MUTAȚIE: coloana readusă în CREATE TABLE salariati -> intersecția nu mai e goală -> pică
    coloane = _s.coloane_template("salariati")
    assert (coloane & {"salariu_brut"}, coloane >= {"id", "cnp", "data_angajare"}) == (set(), True)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_migrarea_muta_salariul_in_istoric_apoi_scoate_coloana():
    """O schemă „de dinainte” (template + coloana readusă): un salariat fără istoric (puntea îi dădea 5000), unul cu
    istoric (rămâne neatins), unul fără dată de angajare (nu se inventează — raportat). MUTAȚIE: backfill-ul scos din
    `aplica` -> salariatul 1 rămâne fără salariu -> pică."""
    from core import salariu_istoric as _si
    import datetime as _dt
    schema = "ztest_2b_coloana"
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"),
                                                             encoding="utf-8").read(), schema))
                cur.execute("ALTER TABLE %s.salariati ADD COLUMN salariu_brut numeric DEFAULT 0" % schema)
                for sid, cnp, da, brut in ((1, "1900101410011", "2025-01-01", 5000), (2, "1900101410028", "2025-01-01", 9999),
                                           (3, "1900101410036", None, 4000)):
                    cur.execute("INSERT INTO %s.salariati (id, nume, prenume, cnp, data_angajare, salariu_brut) "
                                "OVERRIDING SYSTEM VALUE VALUES (%%s,'N','P',%%s,%%s,%%s)" % schema, (sid, cnp, da, brut))
                cur.execute("INSERT INTO %s.salariu_istoric (salariat_id, valabil_din, salariu_brut) VALUES "
                            "(2,'2025-01-01',7000)" % schema)
            rez = _m.aplica(conn, schema)
            assert (rez["completati"], rez["necompletati"], rez["scoasa"]) == (1, [3], True)
            with conn.cursor() as cur:
                assert _m.are_coloana(cur, schema) is False
                la = _dt.date(2026, 6, 30)
                assert [_si.salariu_la(cur, schema, s, la) for s in (1, 2, 3)] == [5000, 7000, None]
            assert _m.aplica(conn, schema) == {"completati": 0, "necompletati": [], "scoasa": False}   # idempotent
        finally:
            conn.rollback()
