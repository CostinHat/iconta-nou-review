# -*- coding: utf-8 -*-
"""core/documente_interne.py — documentul intern generat ODATĂ cu nota pe care aplicația o scrie fără un document extern.

Comanda Costin 06.10.2026 (§6.2), verbatim: „Notele generate de aplicație fără document extern poartă un document intern
generat odată cu nota (număr + dată), potrivit naturii operațiunii: tabloul de amortizare, situația de descărcare a
gestiunii, bonul de consum, lista de inventariere, nota de calcul pentru operațiunile speciale (Legea 82/1991 art.6
alin.(1)). «Fără document» rămâne doar pentru notele manuale. Cele 8 note vechi nu se ating.”

Temei — Legea 82/1991 art.6 alin.(1) (`anaf_surse/legea_82_1991_consolidat.txt`): „Orice operațiune economico-financiară
efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate,
dobândind astfel calitatea de document justificativ.”

Numerotarea: pe TIP de document și pe AN, atomic (un singur `INSERT … ON CONFLICT` care incrementează și întoarce numărul), în tranzacția notei — un
rollback al notei anulează și numărul. Documentul se scrie în `inregistrari.document_ref` („Notă de calcul nr 12 din
15.10.2026”), sursa unică pe care o citesc Registrul-jurnal și validarea (`jurnal_api.document_justificativ`).
"""
import datetime as _dt
import re

#: tipul -> felul documentului, cum îl citește omul
TIPURI = {
    "tablou_amortizare": "Tablou de amortizare",
    "situatie_descarcare": "Situația de descărcare a gestiunii",
    "bon_consum": "Bon de consum",
    "lista_inventariere": "Listă de inventariere",
    "nota_calcul": "Notă de calcul",
    "borderou_achizitie": "Borderou de achiziție",   # [401] numărul borderoului (BA-n) când omul nu scrie unul
    # [lotul 13, deficiența 518] „justificativul e «Listă de inventariere» în loc de proces-verbal de casare”: casarea are documentul ei
    "pv_casare": "Proces-verbal de casare",
    # [lotul 13, deficiențele 507 / 508] scoaterea obiectului de inventar din folosință: documentul înregistrării C 8035
    "pv_scoatere": "Proces-verbal de scoatere din folosință",
    # [lotul 13, deficiența 510] predarea produselor finite la magazie: OMFP 2634/2015 anexa 2, cod 14-3-3A — „document justificativ pentru
    # încărcare/descărcare în/din gestiune; document justificativ de înregistrare în contabilitate”
    "bon_predare": "Bon de predare, transfer, restituire",
}

#: [401, 434] numărul borderoului de achiziție scris de aplicație: „BA-<n>”
PREFIX_BORDEROU = "BA-"


def _p(schema):
    return ('"%s".' % schema) if schema else ""


def _data(d):
    if isinstance(d, _dt.date):
        return d
    return _dt.date.fromisoformat(str(d)[:10])


def _unu(cur):
    r = cur.fetchone()
    return (list(r.values())[0] if isinstance(r, dict) else r[0]) if r else None


def cel_mai_mare(cur, schema, tip, an):
    """[lotul 10, deficiența 434] Cel mai mare număr pe care îl poartă DEJA un document `tip` din anul `an`, oricine l-ar fi scris.
    Comanda Costin 10.2 pct.4, verbatim: „la F1, borderoul de achiziție nou (Maria Ionescu, 20.10) a primit numărul BA-1, deși BA-1
    există deja (Ion Popescu, 19.10). Numerotarea borderourilor e unică și continuă.” Cauza: contorul era SINGURA sursă a numărului,
    dar numărul se poate scrie și de mână — borderoul („Nr. borderou”), nota („Document justificativ”) —, iar un număr scris de mână
    (sau scris înaintea contorului) nu-l mișca. Sursele: borderoul = `facturi.numar` „BA-<n>” (tip `borderou`, anul datei); celelalte
    documente interne = `inregistrari.document_ref` „<Fel> nr <n> din zz.ll.<an>” (forma `jurnal_api.eticheta_document`)."""
    _cere_tip(tip)
    if tip == "borderou_achizitie":
        cur.execute("SELECT COALESCE(max((regexp_match(upper(btrim(numar)), %%s))[1]::bigint), 0) FROM %sfacturi "
                    "WHERE tip = 'borderou' AND EXTRACT(YEAR FROM data_emitere) = %%s" % _p(schema),
                    ("^" + re.escape(PREFIX_BORDEROU) + "([0-9]{1,9})$", int(an)))
    else:
        cur.execute("SELECT COALESCE(max((regexp_match(btrim(document_ref), %%s))[1]::bigint), 0) FROM %sinregistrari "
                    "WHERE document_ref LIKE %%s" % _p(schema),
                    ("^" + re.escape(TIPURI[tip]) + r" nr ([0-9]{1,9}) din [0-9]{2}\.[0-9]{2}\." + str(int(an)) + "( |$)",
                     TIPURI[tip] + " nr %"))
    return int(_unu(cur) or 0)


def _numar(cur, schema, tip, d):
    # [434] contorul pornește de la cel mai mare număr existent al anului: un număr nu se dă de două ori, iar șirul continuă
    peste = cel_mai_mare(cur, schema, tip, d.year)
    # upsert-ok: contor atomic pe (tip, an) - incrementarea E operatiunea, nu o suprascriere (numarul urmator al documentului)
    cur.execute("INSERT INTO %sdocumente_interne_contor (tip, an, ultim) VALUES (%%s, %%s, %%s + 1) "
                "ON CONFLICT (tip, an) DO UPDATE SET ultim = GREATEST(%sdocumente_interne_contor.ultim, %%s) + 1 RETURNING ultim"
                % (_p(schema), _p(schema)), (tip, d.year, peste, peste))
    return _unu(cur)


def _cere_tip(tip):
    if tip not in TIPURI:
        raise ValueError("tip de document intern necunoscut: %r" % tip)


def urmatorul(conn, schema, tip, data):
    """Numărul următor al documentului `tip` în anul datei — același contor atomic ca `genereaza`, fără să scrie pe o notă (documentul
    își poartă singur numărul: borderoul de achiziție)."""
    _cere_tip(tip)
    with conn.cursor() as cur:
        return _numar(cur, schema, tip, _data(data))


def borderou_cu_numarul(cur, schema, numar, data):
    """[434] Borderoul de achiziție care poartă deja numărul `numar` în anul datei (aceeași formă ca indexul unic din bază:
    `upper(btrim(numar))`, anul datei) — (numărul, data, vânzătorul) sau None. Un număr scris de mână nu se dă a doua oară."""
    cur.execute("SELECT numar, data_emitere, tert_nume FROM %sfacturi WHERE tip = 'borderou' AND upper(btrim(numar)) = upper(btrim(%%s)) "
                "AND EXTRACT(YEAR FROM data_emitere) = %%s ORDER BY id LIMIT 1" % _p(schema), (str(numar), _data(data).year))
    r = cur.fetchone()
    return (tuple(r.values()) if isinstance(r, dict) else tuple(r)) if r else None


def e_generat(document_ref, tip):
    """[lotul 11, 451] Textul `document_ref` e documentul intern `tip` generat de aplicație („Bon de consum nr 3 din 20.10.2026” — forma
    `jurnal_api.eticheta_document`, aceeași pe care o citește `cel_mai_mare`), nu un document scris de om. PURĂ."""
    _cere_tip(tip)
    return re.fullmatch(re.escape(TIPURI[tip]) + r" nr [0-9]{1,9} din [0-9]{2}\.[0-9]{2}\.[0-9]{4}", str(document_ref or "").strip()) is not None


def genereaza(cur, schema, tip, data, nota_ids):
    """Numerotează un document de tipul dat, la data dată, și îl scrie pe notele `nota_ids` care n-au deja document.
    Întoarce textul documentului. Un act cu mai multe note (descărcarea lunii, inventarul) primește UN document."""
    from core import jurnal_api as _j
    _cere_tip(tip)
    ids = [int(x) for x in (nota_ids if isinstance(nota_ids, (list, tuple)) else [nota_ids]) if x is not None]
    if not ids:
        return None
    d = _data(data)
    numar = _numar(cur, schema, tip, d)
    ref = _j.eticheta_document(TIPURI[tip], numar, d)
    cur.execute("UPDATE %sinregistrari SET document_ref = %%s WHERE id = ANY(%%s) AND document_ref IS NULL" % _p(schema),
                (ref, ids))
    return ref
