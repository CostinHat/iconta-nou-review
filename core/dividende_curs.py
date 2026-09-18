# -*- coding: utf-8 -*-
"""[A6, 18.09.2026] Atribuirea plăților de dividende (debit 457) pe DISTRIBUIRI (credit 457), FIFO pe
dată, ca impozitul să se aplice cu cota de la DATA DISTRIBUIRII — nu de la 31.12 al anului declarației.

Legea 141/2025 art. VII: 16% pe dividendele DISTRIBUITE începând cu 01.01.2026; alin.(2): dividendele
interimare distribuite în 2025 rămân la 10% chiar dacă se plătesc/regularizează în 2026 (fără
recalculare). Deci cota se decide după data creditului 457 (distribuirea), nu după anul plății.

MODUL NEUTRU (intrare partajată, ca `common.cota`): primește mișcările 457 și o funcție de cotă,
întoarce impozitul PONDERAT pe rata fiecărei distribuiri. Cele două căi (generatorul `d205` și
reconcilierea `d205_reconciliere`) își trag SINGURE mișcările din registru (SQL propriu, fiecare cu
repo-ul ei), apoi cheamă acest atribuitor determinist. Independența rămâne acolo unde a fost mereu — la
CITIREA din sursă — nu la aritmetica ratei (care și azi era aceeași formulă `parte × cotă` în ambele).
"""
from decimal import Decimal


def impozit_ponderat(miscari, an, rate_fn):
    """`miscari`: iterabil de dict-uri {'data': date, 'distribuit': num, 'platit': num}, SORTATE
    crescător după (data, id) — o distribuire = credit 457, o plată = debit 457. `an`: anul declarației
    D205. `rate_fn(data_distribuire) -> Decimal` (fracție, ex. 0.10 / 0.16).

    Potrivește FIFO plățile pe distribuirile deschise (cea mai veche distribuire se stinge prima) și
    întoarce (impozit_ponderat, platit_an, distribuit_an):
      - impozit_ponderat = Σ, peste tranșele PLĂTITE în anul `an`, tranșă × rate_fn(data distribuirii ei);
      - platit_an     = Σ plăților (debit 457) cu data în anul `an` (baza divid_P / baza1);
      - distribuit_an = Σ distribuirilor (credit 457) cu data în anul `an` (pentru divid_D).
    O plată fără distribuire deschisă (inconsecvență de registru) se atribuie propriei date (rata anului
    plății) — conservator, și NU se pierde tăcut."""
    coada = []  # FIFO distribuiri deschise: [[data, ramas], ...]
    imp = Decimal(0)
    platit_an = Decimal(0)
    distribuit_an = Decimal(0)
    for m in miscari:
        d = m["data"]
        dist = Decimal(str(m.get("distribuit") or 0))
        plat = Decimal(str(m.get("platit") or 0))
        if dist > 0:
            coada.append([d, dist])
            if d.year == an:
                distribuit_an += dist
        if plat > 0:
            if d.year == an:
                platit_an += plat
            rest = plat
            while rest > 0 and coada:
                dd, ramas = coada[0]
                ia = rest if rest < ramas else ramas
                if d.year == an:
                    imp += ia * Decimal(str(rate_fn(dd)))
                ramas -= ia
                rest -= ia
                if ramas <= 0:
                    coada.pop(0)
                else:
                    coada[0][1] = ramas
            if rest > 0 and d.year == an:
                # plată fără distribuire deschisă (dividend distribuit necontabilizat pe 457, sau ordine
                # inconsistentă): se impozitează la rata anului plății, nu se pierde.
                imp += rest * Decimal(str(rate_fn(d)))
    return imp, platit_an, distribuit_an
