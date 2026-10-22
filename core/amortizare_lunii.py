# -*- coding: utf-8 -*-
"""core/amortizare_lunii.py — rândurile notei de amortizare a unei luni, din registrul mijloacelor fixe de ACUM (lotul 11, deficiența 451).

Comanda Costin 11.1 pct.6, verbatim: „ciornele generate înainte de o reparație rămân validabile cu regula veche. [...] Toate trebuie
refăcute din sursă sau marcate depășite și oprite de la validare, pe toate firmele.” Ciorna de amortizare se compară la validare cu ce ar
scrie ACUM „Generează amortizarea” (`ciorne_depasite`); ca cele două să nu poată spune lucruri diferite, rândurile se calculează într-un
singur loc — aici —, iar `uc_tenants.tenant_amortizare` îl cheamă (patch-ul cerut în raportul lotului 11, S: corpul buclei lui de acum
e chiar funcția de mai jos, mutată).

Calculul: metoda reală a fiecărui mijloc fix (CF art.28, `d406_active.amortizare_luna`), pe mijloacele fixe active, cu PIF și durată;
contul de amortizare al mijlocului (implicit 2813), cheltuiala pe 6811.
"""
#: contul de cheltuială al notei de amortizare (`repo_contabilitate.adauga_linie_cheltuiala_amortizare`)
CONT_CHELTUIALA = "6811"


def numar(an, luna):
    """Numărul notei de amortizare a lunii (cheia ei: `repo_contabilitate.nota_de_amortizare`)."""
    return "AMORT-%d-%02d" % (int(an), int(luna))


def linii(cur, schema, an, luna):
    """[(cont_amortizare, rata, denumirea mijlocului fix)] — o linie pe mijloc fix cu rată pozitivă în luna cerută. Ridică ValueError cu
    motivul pentru contabil („Amortizarea nu se poate genera pentru <mijloc> până nu corectezi fișa lui: <motiv>”). Nu scrie nimic."""
    from core import d406_active as _d406, repo_mijloace_fixe
    with cur.connection.cursor() as c:   # rândurile de tuplu ale depozitului, oricare ar fi cursorul apelantului
        mf = repo_mijloace_fixe.de_amortizat(c, schema)
    out = []
    for mid, den, cont_am, val, rez, dnf, pif, cont_imob, met, reev, dcd, prel, dprel in mf:
        if not pif or not dnf:
            continue
        mf_d = {"cod": den, "denumire": den, "cont_imobilizare": cont_imob,
                "cont_amortizare": cont_am, "valoare": val, "rezidual": rez,
                "dnf_luni": dnf, "data_pif": pif, "metoda": met, "reevaluari": reev,
                "destinatie_cd": dcd, "amortizare_preluata": prel, "data_preluare": dprel}   # [359, A.1]
        try:
            rata = _d406.amortizare_luna(mf_d, an, luna)   # metoda reala (CF art.28), nu liniar
        except ValueError as e:
            raise ValueError(f"Amortizarea nu se poate genera pentru {den} până nu corectezi fișa lui: {e}")
        if rata > 0:
            out.append((cont_am or "2813", float(rata), den))
    return out
