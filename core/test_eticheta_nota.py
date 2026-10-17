# -*- coding: utf-8 -*-
"""GARD — deficiența 258 (comanda Costin 15.10.2026, verbatim: „mesajul pentru asistent spune «Nota #24», iar pe card nota e «Nr. crt.
5»; numărul intern nu se afișează nicăieri.”): eticheta notei din bază (`eticheta_nota`, core/migrare_ciorne_proprii.py) e EXACT
numărul curent al Registrului jurnal (`repo_contabilitate.jurnal_pe_an`), iar `core/eticheta_nota.py` spune același lucru ca baza.
[302, 17.10.2026] numărul e PĂSTRAT, dat la validare (`registru_jurnal_numere`, core/migrare_nr_curent_note.py); ciorna n-are număr și
se numește „din ZZ.LL.AAAA” (fără număr).

Schemă EFEMERĂ din `tenant_template.sql` (deci și oglinda din șablon), date în 2098–2099, tranzacție anulată. MUTAȚII: în
`eticheta_nota` numărul citit din altă coloană decât a registrului -> ROȘU (paritatea)."""
import io

import pytest

from core import db as _db
from core import eticheta_nota as _et
from core import repo_contabilitate as _rc
from core import tenant_provisioning as _tp

SCH = "efemer_eticheta_nota"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def cur():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    c = conn.cursor()
    c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    c.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    conn.commit()
    c.execute('SET search_path TO "%s", public' % SCH)
    try:
        yield c
    finally:
        conn.rollback()
        c = conn.cursor()
        c.execute("RESET search_path")
        c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.commit()
        p.putconn(conn)


def _nota(cur, data, status="ciorna"):
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'proba', 'manual', %s, 'D1') "
                "RETURNING id", (data, status))
    n = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '371', '401', 10)", (n,))
    return n


def test_eticheta_e_numarul_curent_din_registrul_jurnal(cur):
    """Note pe doi ani, pe aceeași zi și în ordine de inserare amestecată, ciorne și validate: pentru FIECARE, eticheta din bază și cea
    din Python sunt „nr. crt. <Nr. crt. din jurnal> din <data>” la nota validată și „ciorna din <data>” la ciornă."""
    for d, st in (("2099-03-12", "ciorna"), ("2099-01-05", "validata"), ("2098-12-31", "ciorna"), ("2099-03-12", "validata"),
                  ("2099-01-05", "ciorna"), ("2098-06-01", "validata"), ("2099-12-31", "ciorna")):
        _nota(cur, d, st)
    asteptat, ordine = {}, {}
    for an in (2098, 2099):
        for luna in range(1, 13):
            for r in _rc.jurnal_pe_an(cur, SCH, "%d-01-01" % an, "%d-%02d-01" % (an, luna)):
                asteptat[r[0]] = ("nr. crt. %d din %s" % (r[8], r[1].strftime("%d.%m.%Y")) if r[8] is not None
                                 else "din %s" % r[1].strftime("%d.%m.%Y"))
                ordine[r[0]] = (r[1], r[0])
    assert len(asteptat) == 7 and sum(1 for v in asteptat.values() if v.startswith("nr. crt.")) == 3
    cur.execute("SELECT id, eticheta_nota(id) FROM inregistrari ORDER BY id")
    assert dict(cur.fetchall()) == asteptat
    assert {i: _et.nota(cur, SCH, i) for i in asteptat} == asteptat
    assert _et.note(cur, SCH, list(asteptat)) == sorted(asteptat.items(), key=lambda kv: ordine[kv[0]])


def test_ordinea_pe_aceeasi_zi_e_cea_din_jurnal_si_nota_inexistenta_nu_primeste_numar(cur):
    """[302] ciornele n-au număr; la validare numărul urmează ordinea validării, iar lista numește notele în ordinea Registrului jurnal."""
    a = _nota(cur, "2099-05-02")
    b = _nota(cur, "2099-05-01")
    c = _nota(cur, "2099-05-02")
    assert [_et.nota(cur, SCH, x) for x in (b, a, c)] == ["din 01.05.2099", "din 02.05.2099", "din 02.05.2099"]
    for x in (b, a, c):
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (x,))
    assert [_et.nota(cur, SCH, x) for x in (b, a, c)] == ["nr. crt. 1 din 01.05.2099", "nr. crt. 2 din 02.05.2099",
                                                           "nr. crt. 3 din 02.05.2099"]
    assert _et.lista(cur, SCH, [c, a, b]) == "nr. crt. 1 din 01.05.2099, nr. crt. 2 din 02.05.2099, nr. crt. 3 din 02.05.2099"
    assert _et.nota(cur, SCH, c + 1000) == _et.NOTA_INEXISTENTA


def test_operatiunea_din_registrul_de_incasari_si_plati_se_numeste_prin_data_si_suma(cur):
    cur.execute("INSERT INTO rip_operatiuni (data_operatiune, tip, suma, explicatie, categorie, metoda) VALUES "
                "('2099-10-07', 'plata', 1234.5, 'proba', 'cheltuiala', 'numerar'), "
                "('2099-10-08', 'incasare', 7, 'proba', 'venit', 'banca') RETURNING id")
    p, i = [r[0] for r in cur.fetchall()]
    assert [_et.rip(cur, SCH, x) for x in (p, i)] == ["plata din 07.10.2099 de 1.234,50 RON", "încasarea din 08.10.2099 de 7,00 RON"]


def test_raspunsul_unei_operatiuni_poarta_eticheta_langa_id(cur):
    a, b = _nota(cur, "2099-02-02", "validata"), _nota(cur, "2099-02-01")
    assert _et.in_raspuns(cur, SCH, {"inregistrare_id": a}) == {"inregistrare_id": a, "nota_eticheta": "nr. crt. 1 din 02.02.2099"}
    assert _et.in_raspuns(cur, SCH, {"inregistrari": [a, b]}) == {
        "inregistrari": [a, b], "note_etichete": ["din 01.02.2099", "nr. crt. 1 din 02.02.2099"]}
