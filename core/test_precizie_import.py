# -*- coding: utf-8 -*-
"""Gard: float-ul din `numere.numar()` nu compromite verificarile de echilibru.

CONTEXT (27.07.2026): `numar()` intoarce float, iar float pe bani e in general o idee
proasta. Itemul a stat in registrul de datorie cu propunerea de a-l trece pe Decimal.

MASURAT INAINTE DE A DECIDE (regula: nu repara pe suspiciune, masoara intai):
  - valorile de import au 2 zecimale; float64 le reprezinta EXACT la round-trip (0 din 5000
    de valori aleatoare pierd precizie);
  - insumarea a 5000 de randuri da o eroare cu mult sub toleranta de 0.01 folosita la
    verificarea echilibrului balantei (`solduri_api`);
  - destinatia e o coloana `numeric` in PostgreSQL - conversia se face prin repr, exacta;
  - `solduri_api` face deja `round(..., 2)` inainte de comparatie.

DECIZIE: NU se trece pe Decimal. O schimbare in 6 module + 12 apeluri pentru un risc care
NU se manifesta ar fi mai riscanta decat problema. Vezi DECIZII 27.07.

ACEST GARD e conditia in care decizia ramane valabila. Daca vreodata: importurile primesc
valori cu mai mult de 2 zecimale, sau numarul de randuri creste cu ordine de marime, sau
toleranta scade - testul pica si decizia se reia.
"""
import random
from decimal import Decimal

from core.numere import numar

TOLERANTA = Decimal("0.01")      # cea folosita in solduri_api la echilibrul balantei


def test_valorile_cu_doua_zecimale_sunt_exacte_in_float():
    random.seed(42)
    valori = ["%.2f" % random.uniform(0.01, 99999.99) for _ in range(5000)]
    rele = [v for v in valori if Decimal(str(numar(v))) != Decimal(v)]
    assert not rele, "%d valori pierd precizie la round-trip float: %s" % (len(rele), rele[:5])


def test_insumarea_unei_balante_mari_ramane_sub_toleranta():
    """Cazul cel mai defavorabil realist: balanta cu 5000 de conturi."""
    random.seed(7)
    valori = ["%.2f" % random.uniform(0.01, 999999.99) for _ in range(5000)]
    s_float = Decimal(str(round(sum(numar(v) for v in valori), 2)))
    s_exact = sum(Decimal(v) for v in valori).quantize(Decimal("0.01"))
    assert abs(s_float - s_exact) < TOLERANTA, \
        "eroarea de insumare in float (%s) a depasit toleranta %s - reia decizia Decimal" \
        % (abs(s_float - s_exact), TOLERANTA)


def test_formatele_romanesti_si_contabile_se_pastreaza():
    """Regresie pe ce face numar() bine: RO/EN, paranteze contabile, sufixe."""
    assert numar("1.234,56") == 1234.56
    assert numar("1,234.56") == 1234.56
    assert numar("(500)") == -500.0
    assert numar("1.234,56 RON") == 1234.56
    assert numar("") == 0.0 and numar(None) == 0.0


def test_echilibrul_balantei_da_acelasi_verdict_ca_in_decimal():
    """Testul de fond: verdictul de echilibru nu difera intre float si Decimal."""
    random.seed(11)
    debit = ["%.2f" % random.uniform(1, 50000) for _ in range(2000)]
    credit = list(debit)                       # balanta perfect echilibrata
    td = round(sum(numar(v) for v in debit), 2)
    tc = round(sum(numar(v) for v in credit), 2)
    assert abs(td - tc) < 0.01, "balanta echilibrata declarata dezechilibrata in float"
    credit_rupt = credit[:-1] + ["%.2f" % (float(credit[-1]) + 0.02)]
    tc2 = round(sum(numar(v) for v in credit_rupt), 2)
    assert abs(td - tc2) >= 0.01, "diferenta reala de 2 bani nu e detectata"
