# -*- coding: utf-8 -*-
"""GARDA (lot 06.10, 06.10.2026): niciun `.quantize(...)` fără mod de rotunjire explicit în codul de producție.

DE CE. `Decimal.quantize` fără `rounding=` folosește contextul implicit, iar contextul implicit e ROUND_HALF_EVEN — rotunjirea
BANCARĂ (312,50 -> 312). Aplicația nu setează nicăieri un context global, deci fiecare astfel de apel rotunjea bancar pe ,5
exact, contrar regulii din CLAUDE.md („Rotunjire fiscală … aritmetic … NU bancar”) și structurii D112 („Contributiile se
rotunjesc aritmetic”). Găsit la generalizarea punctului 11 (salarii F5): `salarizare._taxe_cm_2018` rotunjea CAS/CASS/impozitul
indemnizației de concediu medical bancar, iar D112 prelua cifra. Clasa măsurată: 65 de apeluri în 24 de fișiere, toate reparate
(ROUND_HALF_UP; unde legea cere altceva — baza impozitului, HG 1/2016 Norme tit.IV pct.4 — modul era deja explicit).

CE FACE IMPOSIBIL: un `quantize` nou fără mod — de la oricine, în orice modul. Nu judecă CARE mod e corect (o normă poate cere
HALF_DOWN); cere doar ca alegerea să fie scrisă.
"""
import ast
import glob
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fisiere():
    for tipar in ("core/*.py", "scripts/*.py", "main.py"):
        for f in glob.glob(os.path.join(RAD, tipar)):
            if not os.path.basename(f).startswith("test_"):
                yield f


def _fara_mod(src):
    for n in ast.walk(ast.parse(src)):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "quantize"
                and len(n.args) == 1 and not any(k.arg == "rounding" for k in n.keywords)):
            yield n.lineno


def test_niciun_quantize_fara_mod_de_rotunjire():
    """MUTAȚIE: `rounding=ROUND_HALF_UP` scos din `salarizare._taxe_cm_2018` -> pică."""
    rele = ["%s:%d" % (os.path.relpath(f, RAD), l)
            for f in _fisiere() for l in _fara_mod(io.open(f, encoding="utf-8").read())]
    assert not rele, "quantize fără `rounding=` (implicit = bancar, ROUND_HALF_EVEN): %s" % rele


def test_scanul_vede_forma_interzisa():
    """Calibrare: scanul chiar prinde forma veche, și nu prinde formele corecte."""
    assert list(_fara_mod("x = d.quantize(Decimal('1'))\n")) == [1]
    assert list(_fara_mod("x = d.quantize(Decimal('1'), rounding=ROUND_HALF_UP)\n")) == []
    assert list(_fara_mod("x = d.quantize(Decimal('1'), ROUND_HALF_UP)\n")) == []


def test_concediul_medical_se_rotunjeste_aritmetic():
    """CF art.139 alin.(1) lit.o) + art.140 (CAS pe indemnizație), rotunjit aritmetic ca în D112 (structura D112:
    „Contributiile se rotunjesc aritmetic”). 1.250 x 25% = 312,50 -> 313 (bancar dădea 312).
    MUTAȚIE: modul scos de pe CAS -> 312 -> pică."""
    import datetime
    from decimal import Decimal
    from core import salarizare
    t = salarizare.taxe_cm(Decimal("1250"), "01", la_data=datetime.date(2026, 10, 1))
    assert t["cas"] == Decimal("313.00")                  # 312,50 -> 313 (aritmetic)
    assert t["cass"] == Decimal("125.00")
    assert t["impozit"] == Decimal("81.00")               # (1250 - 313 - 125) x 10% = 81,20 -> 81
