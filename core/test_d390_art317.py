# -*- coding: utf-8 -*-
"""#4 (plimbare vizuala 14.08.2026): verdictul D390 la neplatitorul cu operatiuni IC era permanent-fals
("nu avem inregistrata calitatea art.317") fiindca nu exista camp de completat. Acum inreg_art317 il face
satisfiabil: bifat -> D390 datorat; nebifat -> gri ACTIONABIL (completeaza in profil). pers_inreg D301 e
acoperit de core/test_d301_pers_inreg.py."""
import datetime
from core import control_fiscal_api as cf

AZI = datetime.date(2026, 8, 14)


def _vec(inreg):
    return {"regim_fiscal": "profit", "platitor_tva": False, "tip_decont": None,
            "operatiuni_ic": True, "partida_simpla": False, "inreg_art317": inreg}


def test_d390_neplatitor_art317_inregistrat_e_datorat():
    out = cf.declaratii_datorate(_vec(True), are_salariati=False, azi=AZI)
    assert "d390" in {d["tip"] for d in out["datorate"]}, "art.317 bifat -> D390 trebuie datorat: %r" % out


def test_d390_neplatitor_fara_art317_gri_actionabil_nu_permanent():
    out = cf.declaratii_datorate(_vec(False), are_salariati=False, azi=AZI)
    assert "d390" not in {d["tip"] for d in out["datorate"]}   # nebifat -> nu se fabrica datorat
    motiv = " ".join(n["motiv"] for n in out["neclar"] if n["tip"] == "d390")
    # mesaj ACTIONABIL (completeaza in profil), nu "nu avem inregistrata" permanent-fals
    assert "art. 317" in motiv and "marcat" in motiv.lower()
    assert "Nu avem înregistrată" not in motiv
