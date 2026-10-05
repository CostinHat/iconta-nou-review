# -*- coding: utf-8 -*-
"""core/horeca.py — ce firmă e HoReCa (hoteluri, restaurante, cafenele), după codul CAEN principal din Date firmă.

Sursa UNICĂ a listei. Temei — Codul fiscal (`anaf_surse/cod_fiscal_227_2015_consolidat.txt`):
  - CF art.48 alin.(2^2): „activități corespunzătoare codurilor CAEN: 5510 - Hoteluri și alte facilități de cazare similare,
    5520 - Facilități de cazare pentru vacanțe și perioade de scurtă durată, 5530 - Parcuri pentru rulote, campinguri și
    tabere, 5590 - Alte servicii de cazare, 5610 - Restaurante, 5621 - Activități de alimentație (catering) pentru evenimente,
    5629 - Alte servicii de alimentație n.c.a., 5630 - Baruri și alte activități de servire a băuturilor”;
  - CF art.54 alin.(4): „Începând cu 1 ianuarie 2025, … se au în vedere, după caz, și activitățile corespunzătoare codurilor
    CAEN 5611 - Restaurante, 5612 - Activități ale unităților mobile de alimentație, 5622 - Alte servicii de alimentație n.c.a.”

Folosită de ecranul Stocuri (comanda Costin 05.10.2026 pct.10: „Rețete apare doar la firmele HoReCa”). INTERPRETARE CU TEMEI:
lista e cea prin care legea definește sectorul HoReCa (la impozitul pe veniturile microîntreprinderilor); o folosim ca
definiție a „firmei HoReCa” din interfață. De reconfirmat dacă apare o normă care o definește altfel.
"""

#: CF art.48 alin.(2^2) + CF art.54 alin.(4)
CODURI = frozenset({"5510", "5520", "5530", "5590", "5610", "5621", "5629", "5630",
                    "5611", "5612", "5622"})


def e_horeca(caen):
    return str(caen or "").strip() in CODURI
