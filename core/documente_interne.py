# -*- coding: utf-8 -*-
"""core/documente_interne.py — documentul intern generat ODATĂ cu nota pe care aplicația o scrie fără un document extern.

Comanda Costin 06.10.2026 (§6.2), verbatim: „Notele generate de aplicație fără document extern poartă un document intern
generat odată cu nota (număr + dată), potrivit naturii operațiunii: tabloul de amortizare, situația de descărcare a
gestiunii, bonul de consum, lista de inventariere, nota de calcul pentru operațiunile speciale (Legea 82/1991 art.6
alin.(1)). «Fără document» rămâne doar pentru notele manuale. Cele 8 note vechi nu se ating.”

Temei — Legea 82/1991 art.6 alin.(1) (`anaf_surse/legea_82_1991_consolidat.txt`): „Orice operațiune economico-financiară
efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate,
dobândind astfel calitatea de document justificativ.”

Numerotarea: pe TIP de document și pe AN, atomic (`INSERT … ON CONFLICT DO UPDATE … RETURNING`), în tranzacția notei — un
rollback al notei anulează și numărul. Documentul se scrie în `inregistrari.document_ref` („Notă de calcul nr 12 din
15.10.2026”), sursa unică pe care o citesc Registrul-jurnal și validarea (`jurnal_api.document_justificativ`).
"""
import datetime as _dt

#: tipul -> felul documentului, cum îl citește omul
TIPURI = {
    "tablou_amortizare": "Tablou de amortizare",
    "situatie_descarcare": "Situația de descărcare a gestiunii",
    "bon_consum": "Bon de consum",
    "lista_inventariere": "Listă de inventariere",
    "nota_calcul": "Notă de calcul",
}


def _p(schema):
    return ('"%s".' % schema) if schema else ""


def _data(d):
    if isinstance(d, _dt.date):
        return d
    return _dt.date.fromisoformat(str(d)[:10])


def genereaza(cur, schema, tip, data, nota_ids):
    """Numerotează un document de tipul dat, la data dată, și îl scrie pe notele `nota_ids` care n-au deja document.
    Întoarce textul documentului. Un act cu mai multe note (descărcarea lunii, inventarul) primește UN document."""
    from core import jurnal_api as _j
    if tip not in TIPURI:
        raise ValueError("tip de document intern necunoscut: %r" % tip)
    ids = [int(x) for x in (nota_ids if isinstance(nota_ids, (list, tuple)) else [nota_ids]) if x is not None]
    if not ids:
        return None
    d = _data(data)
    cur.execute("INSERT INTO %sdocumente_interne_contor (tip, an, ultim) VALUES (%%s, %%s, 1) "
                "ON CONFLICT (tip, an) DO UPDATE SET ultim = %sdocumente_interne_contor.ultim + 1 RETURNING ultim"
                % (_p(schema), _p(schema)), (tip, d.year))
    r = cur.fetchone()
    numar = r["ultim"] if isinstance(r, dict) else r[0]
    ref = _j.eticheta_document(TIPURI[tip], numar, d)
    cur.execute("UPDATE %sinregistrari SET document_ref = %%s WHERE id = ANY(%%s) AND document_ref IS NULL" % _p(schema),
                (ref, ids))
    return ref
