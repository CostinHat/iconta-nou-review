# -*- coding: utf-8 -*-
"""302 — „Nr. crt.” al notei se dă la validare și nu se mai schimbă (comanda Costin 17.10.2026 7.2 pct.5, verbatim în DECIZII; mecanismul
în `core/migrare_nr_curent_note.py`). Pe o schemă efemeră din `tenant_template.sql`, an sintetic 2099.

Temei: OMFP 2634/2015, Registrul-jurnal (cod 14-1-1) — „numărul curent al operațiunilor înregistrate”: numărul e al înregistrării din
evidență; ciorna nu e încă înregistrată.
"""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core import migrare_nr_curent_note as m

_SCH = "efemer_302"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()


@pytest.fixture()
def lume():
    if not _DB:
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
        c.rollback()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _nota(cur, data, status="ciorna"):
    cur.execute("INSERT INTO inregistrari (data, descriere, status, document_ref) VALUES (%s, 'n', %s, 'DOC') RETURNING id",
                (data, status))
    nid = cur.fetchone()[0]
    return nid, _nr(cur, nid)[0]


def _nr(cur, nid):
    cur.execute("SELECT r.nr_curent, eticheta_nota(i.id) FROM inregistrari i LEFT JOIN registru_jurnal_numere r ON r.inregistrare_id = i.id "
                "WHERE i.id = %s", (nid,))
    return cur.fetchone()


def test_302_oglinda_din_sablon_e_migrarea():
    sablon = io.open("tenant_template.sql", encoding="utf-8").read()
    bloc = sablon[sablon.index(m.MARCAJ_INCEPUT):sablon.index(m.MARCAJ_SFARSIT) + len(m.MARCAJ_SFARSIT)]
    assert bloc == m.sql("TENANT_PLACEHOLDER")


def test_302_numarul_se_da_la_validare_si_nu_se_muta(lume):
    """Cazul din 302: ciorna din 17.10 numită, apoi o încasare din 16.10 introdusă după — numerele validate nu se mută.
    MUTAȚIE: triggerul `trg_nr_curent_la_validare` scos (numărul nu se mai dă) -> pică."""
    with lume.cursor() as cur:
        a, nr_a = _nota(cur, "2099-08-05", "validata")
        b, nr_b = _nota(cur, "2099-10-17")                       # ciorna F1A5: n-are număr
        assert (nr_a, nr_b) == (1, None)
        assert _nr(cur, b)[1] == "din 17.10.2099", "ciorna se numește fără număr — nu poate lua numărul altei note"
        c, _ = _nota(cur, "2099-10-16")                          # încasarea din 16.10, introdusă după
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (c,))
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (b,))
        assert [_nr(cur, x)[0] for x in (a, c, b)] == [1, 2, 3], "ordinea intrării în evidență, nu a datelor"
        assert _nr(cur, b)[1] == "nr. crt. 3 din 17.10.2099"
        d, _ = _nota(cur, "2099-01-02")                          # o notă nouă cu dată mai veche nu mută nimic
        assert [_nr(cur, x)[0] for x in (a, c, b)] == [1, 2, 3]
        e, nr_e = _nota(cur, "2100-01-03", "validata")           # anul următor începe de la 1
        assert nr_e == 1


def test_302_numarul_unei_note_validate_nu_se_schimba(lume):
    """MUTAȚIE: refuzul din `nr_curent_la_validare` scos -> schimbarea trece -> pică."""
    import psycopg2
    with lume.cursor() as cur:
        a, _ = _nota(cur, "2099-08-05", "validata")
        cur.execute("SAVEPOINT s")
        with pytest.raises(psycopg2.Error, match="numărul ei nu se mai schimbă"):
            cur.execute("UPDATE registru_jurnal_numere SET nr_curent = 7 WHERE inregistrare_id = %s", (a,))
        cur.execute("ROLLBACK TO SAVEPOINT s")


def test_302_migrarea_pastreaza_numarul_aratat_azi(lume):
    """La migrare, nota validată își păstrează locul de acum (orice stare, după data și id), iar ciorna rămâne fără număr.
    MUTAȚIE: `x.status = 'validata' AND` scos din completare -> ciorna primește număr -> pică."""
    with lume.cursor() as cur:
        cur.execute("ALTER TABLE inregistrari DISABLE TRIGGER trg_nr_curent_la_validare")   # schema „de dinainte” de numere păstrate
        ids = [_nota(cur, d, s)[0] for d, s in (("2099-03-01", "validata"), ("2099-04-01", "ciorna"), ("2099-05-01", "validata"))]
        cur.execute("ALTER TABLE inregistrari ENABLE TRIGGER trg_nr_curent_la_validare")
        cur.execute(m.sql('"%s"' % _SCH))
        assert [_nr(cur, x)[0] for x in ids] == [1, None, 3], "numerele arătate azi: 1 și 3 (ciorna e azi a doua)"
        cur.execute(m.sql('"%s"' % _SCH))                      # idempotentă
        assert [_nr(cur, x)[0] for x in ids] == [1, None, 3]
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (ids[1],))
        assert _nr(cur, ids[1])[0] == 4, "ciorna validată după migrare ia următorul număr"


def test_302_registrul_jurnal_arata_numarul_pastrat(lume):
    from core import repo_contabilitate
    with lume.cursor() as cur:
        a, _ = _nota(cur, "2099-10-17", "validata")
        b, _ = _nota(cur, "2099-10-16")
        for nid in (a, b):
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5121', '4111', 10)",
                        (nid,))
        rows = repo_contabilitate.jurnal_pe_an(cur, _SCH, "2099-01-01", "2099-10-01")
        assert {r[0]: r[8] for r in rows} == {a: 1, b: None}
