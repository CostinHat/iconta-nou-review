# -*- coding: utf-8 -*-
"""core/d101_randuri.py — rândul din formularul D101 pentru un atribut XML „Pn” (date, nu calcul).

Comanda Costin 09.10.2026, „Retest 2” pct.2: ecranul nu arată numele atributului XML („P081”), ci rândul formularului („rândul 8.1”).
Atributele D101 (anaf_surse/d101_struct_anaf.txt, OPANAF 206/2025) codifică rândul POZIȚIONAL: două cifre de rând (cu zero în față
sub 10 când urmează un subrând) și câte o cifră pe nivel de subrând — P081 = rd.8.1, P121 = rd.12.1, P4221 = rd.42.2.1; un număr de
una-două cifre e rândul însuși (P1 … P53), iar P91 (scris și P091 în structură) e rd.9.1, fiindcă formularul n-are rândul 91. Litera
rămâne pe rând (P38a = rd.38a). Păzit de core/test_d101_rand_formular.py, care confruntă rândul cu textul formularului.
"""
import re as _re

ULTIMUL_RAND = 53   # formularul OPANAF 206/2025 se oprește la rd.53 („Diferenţa de impozit pe profit de recuperat”)


def rand_d101(cheie):
    """„P081” -> „rândul 8.1”; o cheie care nu e atribut D101 rămâne cum e (e o eroare de program, nu un rând)."""
    m = _re.fullmatch(r"P(\d+)([a-z]?)", str(cheie or ""))
    if not m:
        return str(cheie)
    d, lit = m.group(1), m.group(2)
    if len(d) <= 2 and int(d) <= ULTIMUL_RAND:
        rand = str(int(d))
    elif len(d) == 2:
        rand = "%s.%s" % (d[0], d[1])
    else:
        rand = str(int(d[:2])) + "".join("." + c for c in d[2:])
    return "rândul %s%s" % (rand, lit)
