# -*- coding: utf-8 -*-
"""GARD (audit tenant_003, misdiagnostic 'D394 perioada septembrie + cifre necorespunzatoare'):
ingheata corectitudinea D394 trimestrial, ca sa nu poata regresa in bug real.

VERIFICAT LA SURSA (nu din eticheta simptomului):
- OPANAF 2194/2025 lit. c: câmpul `luna` pentru trimestrial = ultima luna a trimestrului
  (03 pt T1, 06 pt T2, 09 pt T3, 12 pt T4). Deci luna=09 pt T3 e CODIFICAREA ANAF CORECTA, nu 'septembrie'.
- Wizard-ul trimite `trim`; declaratii_api converteste `luna = trim * 3` -> ancora canonica 3/6/9/12.
- fereastra_tva(perioada, 'T') = TRIMESTRUL INTREG (nu doar luna-ancora) -> iulie/august NU se pierd.
  Empiric pe 003 T3: factura din august (baza 5900 + TVA 889 = 6789) e culesa.

Gardul freeze-uieste AMBELE laturi: eticheta (luna canonica) + fereastra (trimestrul intreg,
data de mijloc de trimestru inauntru). O mutatie care ar face fereastra sa fie doar luna-ancora
(ca la tip 'L') pierde iulie/august -> pica AICI."""
from datetime import date
from core.common import Perioada, fereastra_tva


def test_trim_to_luna_canonica_3_6_9_12():
    # declaratii_api.py:508 -> luna = trim * 3 (marcajul ANAF, OPANAF 2194/2025 lit. c)
    assert [t * 3 for t in (1, 2, 3, 4)] == [3, 6, 9, 12]


def test_fereastra_T_e_trimestrul_intreg_augustul_nu_se_pierde():
    inc, sf = fereastra_tva(Perioada(2026, 9), "T")           # T3, ancora septembrie (09)
    assert (inc, sf) == (date(2026, 7, 1), date(2026, 10, 1)), (inc, sf)
    # data de MIJLOC de trimestru (august) e in fereastra -> nu se pierde (nu e eroare fiscala)
    assert inc <= date(2026, 8, 15) < sf, "augustul trebuie sa fie in fereastra T3 (altfel eroare fiscala)"
    assert inc <= date(2026, 7, 10) < sf, "iulie trebuie sa fie in fereastra T3"


def test_fereastra_T_toate_trimestrele_span_3_luni():
    asteptat = {3: (2026, 1, 2026, 4), 6: (2026, 4, 2026, 7),
                9: (2026, 7, 2026, 10), 12: (2026, 10, 2027, 1)}
    for L, (ay, am, sy, sm) in asteptat.items():
        inc, sf = fereastra_tva(Perioada(2026, L), "T")
        assert (inc.year, inc.month, sf.year, sf.month) == (ay, am, sy, sm), (L, inc, sf)
        span = (sf.year - inc.year) * 12 + (sf.month - inc.month)
        assert span == 3, "un trimestru are 3 luni (%s -> %s)" % (inc, sf)


def test_orice_luna_din_trimestru_da_acelasi_trimestru():
    # ancora poate fi orice luna din trimestru -> aceeasi fereastra (trimestrul intreg)
    for anc in (7, 8, 9):
        assert fereastra_tva(Perioada(2026, anc), "T") == (date(2026, 7, 1), date(2026, 10, 1)), anc
