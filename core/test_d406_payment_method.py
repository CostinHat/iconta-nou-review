"""Gard: PaymentMethod (SD Payment) trebuie sa fie un cod de DOUA CIFRE din nomenclatorul
oficial ANAF (d406_schema_anaf.xlsx, "Nom_Mecanisme_plati", coloana "Code used for Payment
Method"): 01 Numerar, 02 Compensare, 03 Fara numerar, 98 Definit de comun acord, 99 Instrument
nedefinit. Literalii "VIR"/"NUM" NU exista in lista si sunt respinsi de validatorul oficial
("valoarea VIR nu se afla in lista"). Acest gard PICA pe codul de dinainte de reparatie
(default "VIR" emis brut) si TRECE dupa (mapat la 03)."""
import re
from datetime import date
from decimal import Decimal
from core import d406

VALID = {"01", "02", "03", "98", "99"}


def _payment_method_emis(metoda=None):
    prof = {"cui": "12345678", "nume": "TEST SRL", "platitor_tva": True}
    kw = {} if metoda is None else {"metoda": metoda}
    p = d406.Plata(ref="PL1", data=date(2026, 8, 10), partener_id="0012345678", **kw)
    p.linii.append(d406.LiniePlata(nr=1, cont="5121", descriere="x", suma=Decimal("100.00"), sens="D"))
    p.linii.append(d406.LiniePlata(nr=2, cont="4111", descriere="y", suma=Decimal("100.00"), sens="C"))
    res = d406.construieste(prof, 2026, 8, [], [], [], plati=[p])
    xml = d406.build_xml(res)
    return re.search(r"<PaymentMethod>([^<]*)</PaymentMethod>", xml).group(1)


def test_payment_method_default_este_cod_anaf_valid():
    m = _payment_method_emis()  # default dataclass Plata.metoda
    assert m in VALID, "PaymentMethod implicit %r nu e cod ANAF de 2 cifre (01/02/03/98/99)" % m


def test_payment_method_literal_vir_mapat_la_03():
    m = _payment_method_emis("VIR")
    assert m == "03", "VIR (virament, fara numerar) trebuie mapat la 03, emis %r" % m


def test_payment_method_numerar_mapat_la_01():
    m = _payment_method_emis("numerar")
    assert m == "01", "numerar trebuie mapat la 01, emis %r" % m
