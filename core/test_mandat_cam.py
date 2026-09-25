# -*- coding: utf-8 -*-
"""GARD [25.09.2026, bug CAM mandat]: CAM 2,25% se datorează pe remunerația administratorului și a
directorului cu contract de mandat, dar NU pe cea a cenzorului.

SURSA: CF art. 220^3 alin. (1) (cota CAM = 2,25%); CF art. 220^4 alin. (1) lit. d) (remunerația
administratorilor) și lit. e) (directorii cu contract de mandat) intră în baza CAM; cenzorii NU sunt
enumerați (tip asigurat 4 în OPANAF 605/2026 = CAM Nu).

BUG reparat: `core/contracte_speciale.calcul_mandat` omitea CAM pentru toți (docstring vechi: «FARA
CAM»), producând o cifră validă-dar-falsă pentru administrator/director — netul angajatului era corect,
dar obligația de CAM a societății (cont 646=436) lipsea din notă și din declarație.

PROBA invalid->valid: administrator cu brut 3.000 lei -> CAM = 67,50 (2,25%); înainte de fix era 0.
MUTATIE: dacă `cu_cam` e ignorat (comportamentul vechi), `test_administrator_mandat_datoreaza_cam`
și `test_nota_mandat_are_linie_cam_646_436` cad — vezi și test_ANTI_VACUU (administratorul diferă de
cenzor exact pe linia CAM).
"""
import os
import sys
from decimal import Decimal

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core.contracte_speciale import calcul_mandat, nota  # noqa: E402


def test_administrator_mandat_datoreaza_cam_2_25():
    r = calcul_mandat(3000, cu_cam=True)
    assert r["cam"] == Decimal("67.50"), "CAM = 2,25%% x 3000 = 67,50 (CF art. 220^3/220^4 lit.d)"
    # CAM e a angajatorului, NU se reține din remunerație -> netul e neschimbat
    assert r["net"] == Decimal("3000") - r["cas"] - r["cass"] - r["impozit"]


def test_cenzor_NU_datoreaza_cam():
    r = calcul_mandat(3000, cu_cam=False)
    assert r["cam"] == Decimal("0.00"), "cenzorul nu e în baza CAM (art. 220^4 nu-l enumeră)"


def test_nota_mandat_are_linie_cam_646_436():
    linii_mandat = nota(3000, fel="mandat")["linii"]
    assert ("646", "436", Decimal("67.50")) in linii_mandat, \
        "nota de mandat administrator trebuie să conțină cheltuiala angajatorului cu CAM (646=436)"
    linii_cenzor = nota(3000, fel="cenzor")["linii"]
    assert not any(d == "646" and c == "436" for d, c, _ in linii_cenzor), \
        "cenzorul NU are linie de CAM"


def test_ANTI_VACUU_administrator_difera_de_cenzor_pe_cam():
    """Garda chiar discriminează: singura diferență e CAM."""
    a = calcul_mandat(3000, cu_cam=True)
    c = calcul_mandat(3000, cu_cam=False)
    assert a["cam"] != c["cam"]
    assert a["net"] == c["net"] and a["cas"] == c["cas"]  # restul identic
