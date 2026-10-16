# -*- coding: utf-8 -*-
"""core/alerta_load.py — când pleacă alerta de load (comanda Costin 15.10.2026 noaptea, „Lotul 5 — comanda 3” pct.6b, verbatim în
DECIZII: „Alerta de load pleacă doar dacă media pe 15 minute depășește un prag calculat pe numărul de procesoare și rămâne așa; nu pleacă
în timpul rulărilor tale de teste.”).

Până acum: `load1 ≥ 0,7 × procesoare` la o singură măsurătoare — pe 2 procesoare, 1,4; orice rulare de teste îl depășea, iar alerta pleca
în serie (o dată pe oră, cât ținea rularea). Acum, din istoricul buclei de sănătate (`public.metrici_sanatate`, un rând la 5 minute):
  · PRAGUL = numărul de procesoare (`prag(cpu)`): media pe 15 minute arată toate procesoarele ocupate;
  · „RĂMÂNE AȘA” = toate rândurile din ultimele `TINUT_MIN` minute (cel puțin `MIN_RANDURI`) au `load15 ≥ prag`;
  · „NU ÎN TIMPUL TESTELOR” = niciun rând din ultimele `FARA_TESTE_MIN` minute n-a văzut o rulare de teste (`core.rulari_teste`): media pe
    15 minute a ferestrei ținute ar conține încă încărcarea lor.
Gard: core/test_alerta_load.py."""
import datetime

TINUT_MIN = 15
MIN_RANDURI = 3
FARA_TESTE_MIN = 30


def prag(cpu):
    return float(max(1, int(cpu or 1)))


def de_alertat(istoric, cpu, acum):
    """PURĂ. `istoric` = [(creat_la, load15, teste)] (orice ordine), `acum` = ora ultimului rând. -> `(alerta, motiv)`."""
    p = prag(cpu)
    tinut = [r for r in istoric if r[0] > acum - datetime.timedelta(minutes=TINUT_MIN)]
    cu_teste = [r for r in istoric if r[0] > acum - datetime.timedelta(minutes=FARA_TESTE_MIN) and r[2]]
    if cu_teste:
        return False, "rulare de teste în ultimele %d de minute" % FARA_TESTE_MIN
    if len(tinut) < MIN_RANDURI:
        return False, "istoric prea scurt (%d rânduri în %d minute)" % (len(tinut), TINUT_MIN)
    if any(r[1] is None or float(r[1]) < p for r in tinut):
        return False, "media pe 15 minute nu stă peste %.0f" % p
    return True, "media pe 15 minute peste %.0f (numărul de procesoare) la %d măsurători la rând, din 5 în 5 minute: %s" % (
        p, len(tinut), ", ".join("%.2f" % float(r[1]) for r in sorted(tinut)))
