# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 436 afișare — clasa „paragraful repetă ce arată butoanele”] În coada „De validat” (`validat.js`), sub
paragraful documentelor nevalidate stau butoanele „Deschide nota …” (`coada_trimite.legaturiNote`), care numesc fiecare notă. Paragraful
(`coada_api.nevalidate_acum` -> `surse_nevalidate`) repeta lista notelor: același text de două ori, lângă butoane. Acum afirmația poartă și
`motiv_langa_note` — aceeași frază FĂRĂ lista notelor (facturile, care n-au butoane, rămân numite) —, lista cozii o pune în
`surse_nevalidate_langa_note`, iar ecranul o arată când are butoane de note. `motiv` (cu lista) rămâne pentru locurile fără butoane.
MUTAȚIE: `motiv_langa_note` cu lista notelor -> pică primul test; ecranul pe `surse_nevalidate` -> pică al doilea."""
import os

import pytest

SCHEMA = "ztest_lot11_k_langa_note"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    from core import db
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_motiv_langa_note_e_fraza_fara_lista_notelor():
    from core import coada_api, db, tenant_provisioning as _tp
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                for zi, doc in (("10", "F1A6"), ("12", "F1A7")):
                    cur.execute("INSERT INTO %s.inregistrari (data, descriere, document_ref, status) VALUES ('2099-06-%s', 'Telefon', %%s, "
                                "'ciorna') RETURNING id" % (SCHEMA, zi), (doc,))
                    nid = cur.fetchone()[0]
                    cur.execute("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, '626', '401', "
                                "500)" % SCHEMA, (nid,))
                note, facturi, nev = coada_api.nevalidate_acum(cur, SCHEMA, "d101", "2099-06-01", "2099-07-01")
            assert len(note) == 2 and facturi == [], (note, facturi)
            # motivul complet numește notele (locurile fără butoane) — fraza întreagă, nu un fragment care ar apărea oricum
            assert nev["motiv"] == (
                "În perioadă sunt 2 note nevalidate, pe care evidența nu le cuprinde până nu le validează un om: nota din 10.06.2099 — "
                "F1A6, 500,00 lei; nota din 12.06.2099 — F1A7, 500,00 lei. Validează-le înainte de depunere: după validare declarația "
                "devine depășită și se generează din nou."), nev["motiv"]
            # lângă butoane: aceeași frază, fără listă
            assert nev["motiv_langa_note"] == (
                "În perioadă sunt 2 note nevalidate, pe care evidența nu le cuprinde până nu le validează un om. Validează-le înainte de "
                "depunere: după validare declarația devine depășită și se generează din nou."), nev["motiv_langa_note"]
        finally:
            conn.rollback()


def test_coada_si_ecranul_folosesc_varianta_langa_note():
    """Lista cozii pune `surse_nevalidate_langa_note`; `validat.js` o arată când are butoanele notelor (`surse_note` nevid)."""
    import ast
    # structura, nu textul (core/test_garzi_pe_text.py): atribuirea `d["surse_nevalidate_langa_note"] = (_nev or {}).get("motiv_langa_note")`
    arb = ast.parse(open(os.path.join(_RAD, "core", "coada_api.py"), encoding="utf-8").read())
    atrib = [n for n in ast.walk(arb) if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Subscript)
             and getattr(n.targets[0].slice, "value", None) == "surse_nevalidate_langa_note"
             and isinstance(n.value, ast.Call) and getattr(n.value.func, "attr", None) == "get"
             and [getattr(a, "value", None) for a in n.value.args] == ["motiv_langa_note"]]
    assert len(atrib) == 1, "lista cozii nu mai pune `surse_nevalidate_langa_note` din `motiv_langa_note`"
    from core.arbore_js import arbore_js, noduri
    # ecranul: condiția ca nod acorn — cu butoanele notelor (`surse_note` nevid) fraza fără listă, altfel textul întreg
    arb, cod = arbore_js("validat.js")
    alegeri = [(cod(c["test"]), cod(c["consequent"]), cod(c["alternate"])) for c in noduri(arb, "ConditionalExpression")]
    assert ("(c.surse_note || []).length && c.surse_nevalidate_langa_note", "c.surse_nevalidate_langa_note", "c.surse_nevalidate") in alegeri
