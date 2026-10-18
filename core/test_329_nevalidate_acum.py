# -*- coding: utf-8 -*-
"""[deficiența 329, comanda Costin 8.1, 18.10.2026] Avertismentul documentelor nevalidate se calculează la fiecare listare a cozii
(`coada_api.nevalidate_acum`), nu se mai îngheață la intrare. Lista cozii citește pe un cursor DICT: găsit de e2e-ul 329 la prima rulare —
`note_nevalidate` avea două `COALESCE` fără alias (ambele „coalesce”), cheia se suprascria, `tuple(x.values())` ieșea mai scurt ->
IndexError -> 500 pe `GET /coada`. Proba: aceeași interogare, pe cursor tuplu și pe cursor dict, dă aceleași note; după validare, nota
nu mai e numită. MUTAȚIE: aliasurile scoase din `note_nevalidate` -> pe cursorul dict IndexError -> pică."""
import psycopg2.extras as _E
import pytest

SCHEMA = "ztest_329_nevalidate"


def _db_ok():
    from core import db
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_329_nevalidate_acum_pe_cursor_dict_si_tuplu_dupa_validare_dispare():
    from core import coada_api, db, tenant_provisioning as _tp
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("INSERT INTO %s.inregistrari (data, descriere, document_ref, status) VALUES ('2099-06-10', 'Telefon', 'F1A6', "
                            "'ciorna') RETURNING id" % SCHEMA)
                nid = cur.fetchone()[0]
                cur.execute("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, '626', '401', 500)"
                            % SCHEMA, (nid,))
                tuplu = coada_api.nevalidate_acum(cur, SCHEMA, "d300", "2099-06-01", "2099-07-01")
            with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
                dict_ = coada_api.nevalidate_acum(cur, SCHEMA, "d300", "2099-06-01", "2099-07-01")
            assert tuplu[0] == dict_[0] and [n["nota_id"] for n in dict_[0]] == [nid], (tuplu[0], dict_[0])
            assert dict_[0][0]["eticheta"].startswith("nota din 10.06.2099 — F1A6, 500,00 lei"), dict_[0]
            assert (dict_[2]["fel"], dict_[2]["tip"]) == ("fapt", "documente_nevalidate"), dict_[2]
            with conn.cursor() as cur:
                cur.execute("UPDATE %s.inregistrari SET status = 'validata' WHERE id = %%s" % SCHEMA, (nid,))
            with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
                note, _f, nev = coada_api.nevalidate_acum(cur, SCHEMA, "d300", "2099-06-01", "2099-07-01")
            assert note == [] and nev is None, "[329] nota validată e încă numită: %s" % note
        finally:
            conn.rollback()
