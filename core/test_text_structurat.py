# -*- coding: utf-8 -*-
"""GARD — o subclasă de `str` care poartă structură se COPIAZĂ cu tot cu structura (comanda Costin 07.10.2026, C1).

Instanța: D390 nu intra în coadă (500): `dataclasses.asdict` copia un `Unde` prin `Unde.__new__(<textul>)` -> „fel de referent
necunoscut 'factura 95141537 — …'”. CE FACE IMPOSIBIL: (1) o subclasă de `str` din `core/` cu `__new__` propriu care nu moștenește
`TextStructurat`; (2) o copiere (copy, deepcopy, pickle, `dataclasses.asdict`) care cade sau pierde textul ori atributele.
"""
import ast
import copy
import dataclasses
import glob
import os
import pickle

from core import coada_api
from core.common import Temei
from core.text_structurat import TextStructurat
from core.unde import Unde

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEMPLE = [Unde("factura", 95141537, "Comert Micro TVA SRL"), Unde("firma", 4839), Unde("vector_fiscal"),
           Temei("OUG", 89, 2025, art="III", alin="5", lit="b", data_in="2026-07-01")]


def test_orice_str_cu_constructor_propriu_mosteneste_TextStructurat():
    """MUTAȚIE: `class Unde(str)` pus la loc -> pică."""
    rele = []
    for f in glob.glob(os.path.join(RAD, "core", "*.py")):
        if os.path.basename(f).startswith("test_"):
            continue
        for n in ast.walk(ast.parse(open(f, encoding="utf-8").read())):
            if isinstance(n, ast.ClassDef) and any(getattr(b, "id", None) == "str" for b in n.bases) \
                    and any(isinstance(x, ast.FunctionDef) and x.name == "__new__" for x in n.body):
                rele.append("%s:%s" % (os.path.basename(f), n.name))
    assert rele == []
    assert issubclass(Unde, TextStructurat) and issubclass(Temei, TextStructurat)


def test_copierea_pastreaza_textul_si_atributele():
    """MUTAȚIE: `__reduce__` scos din TextStructurat -> `Unde` cade la copiere."""
    for o in EXEMPLE:
        for f in (copy.copy, copy.deepcopy, lambda x: pickle.loads(pickle.dumps(x))):
            c = f(o)
            assert (type(c), str(c), c.__dict__) == (type(o), str(o), o.__dict__)


def test_rezultatul_cu_referinta_intra_in_coada():
    """Drumul real al defectului: `randuri_din_res` pe un rezultat care poartă un `Unde`."""
    @dataclasses.dataclass
    class _Rez:
        unde: str
        temei: str
    r = coada_api.randuri_din_res(_Rez(EXEMPLE[0], EXEMPLE[-1]))   # o referință + un temei
    assert r == {"unde": "factura 95141537 — Comert Micro TVA SRL", "temei": "OUG 89/2025 art.III alin.(5) lit.b"}
