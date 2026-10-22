# -*- coding: utf-8 -*-
"""[lotul 11, C92] Serverul refuză la SALVARE certificatul care n-ar putea intra în D112: codul 10 fără numărul avizului medicului expert
(structura D112: „D_13#null pentru D_9 = 10”, DUK regula S102) și codurile 05 / 51 fără codul bolii infecto-contagioase („daca D_9= (05,51)
atunci D_12#null”, „D_12<= 36 daca (D_5<=29.05.2020 sau D_5>=24.10.2023)”). Refuzul stă lângă câmpul de pe ecran (`cm-urgenta`), ca la
codul 06. Validarea de formă rulează înaintea oricărei citiri din bază (conexiunea nu se atinge). MUTAȚIE: ramura codului 10 scoasă din
`salariati_api.salveaza_concediu` -> pică."""
import pytest

from core import salariati_api as sa
from core.erori import DateInvalide

_BAZA = {"serie": "AB", "numar": "77", "data_acordare": "2026-10-05", "data_inceput": "2026-10-05", "data_sfarsit": "2026-10-09",
         "zile_cm": 5, "venituri_6_luni": 24000, "zile_6_luni": 120, "an": 2026, "luna": 10}


def _campuri(date):
    with pytest.raises(DateInvalide) as e:
        sa.salveaza_concediu(None, 1, dict(_BAZA, **date))
    d = e.value.args[0] if e.value.args else {}
    return {c["camp"]: c["mesaj"] for c in d.get("erori_campuri", [])}


def test_cod_10_fara_aviz_se_refuza_langa_camp():
    assert _campuri({"cod": "10", "cod_urgenta": ""}).get("cm-urgenta") == (
        "La codul 10 completează numărul avizului medicului expert — D112 îl cere.")   # structura D112: D_13#null pentru D_9 = 10


@pytest.mark.parametrize("cod, valoare", [("05", ""), ("51", ""), ("05", "37")])
def test_cod_05_51_fara_codul_bolii_se_refuza_langa_camp(cod, valoare):
    assert _campuri({"cod": cod, "cod_urgenta": valoare}).get("cm-urgenta") == (
        "La codurile 05 și 51 completează codul bolii infecto-contagioase (1–36) — D112 îl cere.")   # D_12#null; D_12<= 36
