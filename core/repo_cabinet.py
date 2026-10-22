# -*- coding: utf-8 -*-
"""REPOSITORY — datele cabinetului din `public.accounting_firms` cerute de use-case-urile din `core/uc_cabinet.py`.

[lotul 11, subagentul x — regula straturilor, `core/straturi.py`] Întocmitorul bilanțului (decizia Costin 10.3 pct.4; coloanele:
`core/migrare_intocmitor_bilant.py`): citirea și scrierea lui stăteau ca SQL în `uc_cabinet.citeste_intocmitor_conn` /
`salveaza_intocmitor_conn`; aici, mutate fără schimbare de comportament.

Fiecare funcție primește CURSORUL apelantului. Nu deschide conexiuni, nu comite, nu face rollback, nu construiește `HTTPException`.
"""


def intocmitorul(cur, firm_id):
    """(calit_intocmit, nume_intocmit, cif_intocmit, nri_intocmit) ale cabinetului, sau None."""
    cur.execute("SELECT calit_intocmit, nume_intocmit, cif_intocmit, nri_intocmit FROM public.accounting_firms WHERE id = %s",
                (firm_id,))
    return cur.fetchone()


def scrie_intocmitorul(cur, firm_id, calit, nume, cif, nri):
    """Întocmitorul cabinetului, valorile deja verificate de apelant."""
    cur.execute("UPDATE public.accounting_firms SET calit_intocmit = %s, nume_intocmit = %s, cif_intocmit = %s, nri_intocmit = %s "
                "WHERE id = %s", (calit, nume, cif, nri, firm_id))
