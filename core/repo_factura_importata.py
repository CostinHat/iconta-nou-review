# -*- coding: utf-8 -*-
"""[lotul 12, C161] Scrierile clasificării unei facturi EMISE importate din XML care nu stau în inserarea ei (`repo_main.insert_facturi` /
`insert_factura_linii`, comune cu factura primită): categoria de TVA a fiecărei linii. Antetul (țara, axa, taxarea inversă) se scrie cu
`repo_facturi.actualizeaza_clasificarea`, ca la validarea facturii primite. Primește cursorul apelantului; nu deschide conexiuni, nu comite."""


def actualizeaza_categorii_linii(cur, schema, fid, categorii):
    """Categoria de TVA (`factura_linii.categorie_tva`, valorile `core/categorii_tva.VALORI`) a fiecărei linii, în ORDINEA liniilor (ORDER BY
    id — ordinea în care `uc_comun._factura_din_parsat` inserează `f["linii"]`, ca `repo_facturi.actualizeaza_conturi_linii`):
    categorii[i] <-> linia i; None lasă linia fără categorie."""
    if not any(categorii or ()):
        return
    cur.execute(f"SELECT id FROM {schema}.factura_linii WHERE factura_id=%s ORDER BY id", (fid,))
    for lid, cat in zip([r[0] for r in cur.fetchall()], categorii):
        if cat:
            cur.execute(f"UPDATE {schema}.factura_linii SET categorie_tva=%s WHERE id=%s", (cat, lid))
