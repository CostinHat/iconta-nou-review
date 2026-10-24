# -*- coding: utf-8 -*-
"""[lotul 12, C159] Golul din registrul de parametri fiscali (plafonul tichetului de masă: verificat până la 30.09.2025 și din nou de la
01.11.2025) oprea statul de plată din 10/2025 cu 500, pentru ORICE firmă cu salariați — și pentru cele fără tichete —, cu un mesaj care
numea cheia tehnică („tichet_masa_plafon:”) și cerea „completează valoarea în registru”.

Acum: (1) salariul unui salariat FĂRĂ tichete nu mai cere plafonul (`salarizare`), deci luna se calculează; (2) salariatul CU tichete
primește blocajul motivat al perioadei (`common.PerioadaIndisponibila` cu `gol`), cu numele pentru om; (3) refuzul de perioadă împachetat
ca text de un use-case (`DateInvalide(str(e))`) iese 423 cu textul pentru contabil, nu 422 cu eticheta (`main._http_din`).
MUTAȚII: `salarizare` cere plafonul mereu -> (1) pică; `cota` ridică `ValueError` simplu pe gol -> (2) pică; `_http_din` fără ramura
perioadei -> (3) pică."""
from datetime import date
from decimal import Decimal

import pytest

from core import common, erori, salarizare


def test_def_c159_salariatul_fara_tichete_se_calculeaza_in_luna_fara_plafon():
    r = salarizare.calcul_salariu(Decimal("5000"), la_data=date(2025, 10, 1))
    assert Decimal(str(r["net"])) > 0, r


def test_def_c159_salariatul_cu_tichete_primeste_blocajul_motivat():
    with pytest.raises(common.PerioadaIndisponibila) as ei:
        salarizare.calcul_salariu(Decimal("5000"), la_data=date(2025, 10, 1), tichet_valoare=40, tichet_zile=20)
    assert ei.value.nume == "tichet_masa_plafon" and ei.value.gol == (date(2025, 9, 30), date(2025, 11, 1)), ei.value
    assert str(ei.value).startswith("PERIOADA_BLOCATA: ") and common.ETICHETE_COTE["tichet_masa_plafon"] in str(ei.value)


def test_def_c159_refuzul_de_perioada_impachetat_iese_423_cu_textul_contabilului():
    import main
    from core import perioada
    e = common.PerioadaIndisponibila("tichet_masa_plafon", date(2025, 10, 1), date(2025, 4, 1), gol=(date(2025, 9, 30), date(2025, 11, 1)))
    h = main._http_din(erori.DateInvalide(str(e)))   # forma celor 52 de use-case-uri: orice ValueError -> DateInvalide(str(e))
    assert h.status_code == 423 and h.detail == perioada.text_exceptie(e) and perioada.ETICHETA not in h.detail, (h.status_code, h.detail)
    # un refuz de date obișnuit rămâne 422, cu detaliul lui neatins
    h2 = main._http_din(erori.DateInvalide({"mesaj": "Alege contul.", "erori_campuri": []}))
    assert h2.status_code == 422 and h2.detail == {"mesaj": "Alege contul.", "erori_campuri": []}
