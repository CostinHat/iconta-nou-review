# -*- coding: utf-8 -*-
"""[T6, catalog D112 4.1-4.3] serie/numar/diagnostic (D_1/D_2/D_23) NETRUNCHIATE -> hard-block la overflow.

GAP inchis: identificatorii de certificat depaseau lungimea XSD (Str5/Str10/Str3) si plecau
NETRUNCHIATI (spre deosebire de nume/den trunchiate tacit prin text_anaf) -> XSD maxLength reject.
Un identificator trunchiat tacit ar fi UN ALT certificat la ANAF, deci se REFUZA (nu se trunchiaza),
numind campul + limita.

MUTATIE (HEAD 8b74ccb): emitea D_1/D_2/D_23 supra-lungi fara ValueError -> pytest.raises pica pe HEAD.
Dupa gard -> ValueError ridicat -> PASS.
"""
import re
import pytest
from core import d112


def _prof():
    return {"cui": "301111003", "nume": "TEST SRL", "caen": "6202", "judet": "bucuresti"}


def _sal_cm(**cm):
    cert = {"cod": "01", "zile_ang": 3, "zile_fnuass": 2, "brut_ang": 714,
            "brut_fnuass": 476, "baza": 5000, "serie": "AA", "numar": "111",
            "da": "01.08.2026", "di": "01.08.2026", "ds": "05.08.2026",
            "loc_prescriere": 1, "diagnostic": "999"}
    cert.update(cm)
    return {"id": 1, "nume": "TEST", "prenume": "X", "cnp": "1850315400125",
            "data_angajare": "2026-01-15", "brut": 5000, "brut_lucrat": 3810,
            "ore_zi": 8, "judet_casa": "bucuresti", "cas": 0, "cass": 0, "impozit": 0,
            "facilitate": 0, "deducere": 0, "zile_cm": 5, "cm": [cert]}


def test_baseline_certificat_in_limite_emite():
    xml, _ = d112._d112_genereaza(_prof(), [_sal_cm()], 2026, 8)
    d = re.search(r"<asiguratD[^>]*/>", xml).group(0)
    assert 'D_1="AA"' in d and 'D_2="111"' in d and 'D_23="999"' in d, d


@pytest.mark.parametrize("camp,valoare,eticheta,limita", [
    ("serie", "ABCDEF", "D_1 (serie)", 5),            # 6 > 5
    ("numar", "12345678901", "D_2 (număr)", 10),      # 11 > 10
    ("diagnostic", "ABCD", "D_23 (diagnostic)", 3),   # 4 > 3
])
def test_cert_overflow_blocheaza_cu_camp_si_limita(camp, valoare, eticheta, limita):
    with pytest.raises(ValueError) as ei:
        d112._d112_genereaza(_prof(), [_sal_cm(**{camp: valoare})], 2026, 8)
    msg = str(ei.value)
    assert eticheta in msg, "trebuie să numeasca campul %s: %s" % (eticheta, msg)
    assert "max %d" % limita in msg, "trebuie să dea limita: %s" % msg
    assert "1850315400125" in msg, "trebuie să numeasca salariatul: %s" % msg


def test_diagnostic_lung_nu_e_trunchiat_tacit():
    """Confirma clasa T6: un diagnostic supra-lung NU ajunge trunchiat in XML - se refuza."""
    with pytest.raises(ValueError):
        d112._d112_genereaza(_prof(), [_sal_cm(diagnostic="LUNGDEtot")], 2026, 8)
