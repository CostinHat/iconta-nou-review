# -*- coding: utf-8 -*-
"""Contul din afara planului legal al normei firmei (decizia Costin 08.10.2026, V3, verbatim în DECIZII).

„Planul de conturi al F1 conține 731, 732, 733, 734, 736, 738, care nu există în planul contabil. Spune-mi de unde vin. Decizie: un cont
care nu e în planul legal nu se poate crea sau folosi fără avertisment.”

DE UNDE VIN: `tenant_template.sql` semănă la crearea ORICĂREI firme un plan care cuprinde și conturile de venituri ale entităților fără
scop patrimonial (731–738, OMFP 3103/2017) — deci și o societate comercială (norma OMFP 1802/2014) le are în plan.

PLANUL LEGAL = nomenclatorul validatorului oficial ANAF pe norma firmei (`d406.plan_oficial`, `firma_profil.baza_contabila`; norma
implicită „A” = OMFP 1802/2014). Un cont e în plan dacă el sau un prefix al lui de cel puțin 3 cifre (sinteticul) e în nomenclator.
Nomenclator absent -> nu se afirmă nimic (nu inventăm un plan al nostru).
"""
COD = "CONT_IN_AFARA_PLANULUI"


def norma_firmei(cur, schema=None):
    p = ('"%s".' % str(schema).strip('"')) if schema else ""
    cur.execute("SELECT baza_contabila FROM %sfirma_profil LIMIT 1" % p)
    r = cur.fetchone()
    return ((r["baza_contabila"] if isinstance(r, dict) else r[0]) if r else None) or None


def in_afara(cur, schema, conturi):
    """Conturile (din cele date) al căror sintetic nu e în planul legal al normei firmei; [] dacă nomenclatorul lipsește."""
    from core import d406 as _d406
    plan = _d406.plan_oficial(norma_firmei(cur, schema))
    if not plan:
        return []
    out = []
    for c in conturi:
        s = "".join(ch for ch in str(c or "").split(".")[0] if ch.isdigit())
        if s and not any(s[:k] in plan for k in range(3, len(s) + 1)) and c not in out:
            out.append(c)
    return out


def avertisment(cur, schema, conturi):
    """Afirmația de avertisment (sau None) pentru conturile din afara planului legal."""
    afara = in_afara(cur, schema, conturi)
    if not afara:
        return None
    from core import afirmatii as _af
    norma = norma_firmei(cur, schema) or "A"
    return dict(_af.afirmatie(
        "neconformitate", COD,
        "Contul %s nu e în planul de conturi al normei firmei (%s): verifică dacă e cel potrivit — un cont din alt plan (de "
        "exemplu 731–738, veniturile entităților fără scop patrimonial) nu are ce căuta în evidența unei societăți comerciale, iar "
        "D406 îl respinge." % (", ".join(afara), "OMFP 1802/2014" if norma == "A" else norma),
        unde="plan de conturi", regula="nomenclatorul validatorului ANAF pe norma firmei (d406.plan_oficial)"),
        cod=COD, conturi=afara)
