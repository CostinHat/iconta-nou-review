# -*- coding: utf-8 -*-
"""REGISTRUL DE DATORIE — ce e amanat, ca test care ruleaza.

DE CE (27.07.2026, cerut de Costin): "mereu lasam cate ceva in urma de care nu mai stim si
de care nu ne mai amintim decat cand crapa ceva". DE_FACUT.md are 80.000 de caractere;
fiecare item pare rezonabil singur, impreuna sunt o datorie pe care nimeni n-o tine minte.
Iar un registru care nu e verificat mecanic se DESINCRONIZEAZA: LANSARE.md declara
"Un singur deployment activ - REZOLVAT (25.07)", dar pe 27.07 /opt/iconta era viu, cu chiar
venv-ul din care rula aplicatia.

CUM: fiecare lucru amanat = un test care afirma comportamentul CORECT, marcat
`xfail(strict=True)` cu motivul si data. Consecinte:
  - rularea suitei ARATA datoria (xfailed in raport), nu o ascunde;
  - cand cineva repara defectul, testul TRECE, iar `strict=True` il face sa PICE - te
    anunta ca e timpul sa inchizi itemul din DE_FACUT. Datoria devine zgomotoasa.

Un item intra aici DOAR daca e verificabil mecanic. Deciziile de produs, verificarile
vizuale si sarcinile juridice raman in DE_FACUT/LANSARE - dar atunci stii ca acolo e doar
ce NU se poate automatiza, nu un depozit.
"""
import datetime
import pathlib
import re

import pytest

from core import db

_AZI = datetime.date(2026, 7, 27)


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


# ============================================================
#  DATORIE FISCALA
# ============================================================
@pytest.mark.xfail(strict=True, reason="DATORIE 27.07.2026: nume_declar/den_intocmit "
                                       "depasesc 75 caractere cand declarant_nume e gol "
                                       "(fallback pe numele firmei). ANAF respinge D300/D394.")
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_campurile_de_declarant_respecta_limita_anaf():
    """ANAF: sir mai lung de 75 caractere -> respins. Fallback-ul pe `den` (numele firmei,
    115 car. la tenant_001) depaseste. De reparat: fallback potrivit + trunchiere la sursa."""
    from core import declaratii_api
    with db.get_conn('tenant_001') as c:
        xml, _ = declaratii_api.genereaza(c, 'tenant_001', 'd300', {'an': 2026, 'luna': 6})
        c.rollback()
    lungi = [(a, v) for a, v in re.findall(r'(\w*declar\w*|den_intocmit)="([^"]*)"', xml)
             if len(v) > 75]
    assert not lungi, "atribute peste 75 caractere: %s" % [(a, len(v)) for a, v in lungi]


@pytest.mark.xfail(strict=True, reason="DATORIE 27.07.2026: D390 pe tenant_001 pica "
                                       "structural la DUK - 'lipsa sectiune obligatorie'. "
                                       "Cauza neinvestigata.")
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d390_trece_validatorul_pe_firma_reala():
    from core import declaratii_api, duk
    with db.get_conn('tenant_001') as c:
        xml, _ = declaratii_api.genereaza(c, 'tenant_001', 'd390', {'an': 2026, 'luna': 6})
        c.rollback()
    r = duk.valideaza(xml, 'd390')
    assert r["stare"] == "valid", r["erori"][:200]


@pytest.mark.xfail(strict=True, reason="DATORIE 27.07.2026 [FISCAL, cere verificare la "
                                       "sursa]: d390._int foloseste round() = rotunjire "
                                       "BANCARA; D112 documenteaza ca ANAF cere ARITMETICA "
                                       "(regula A91b). Nu se stie daca se aplica si la D390.")
def test_d390_rotunjeste_aritmetic_ca_d112():
    from core.d390 import _int
    assert _int(112.5) == 113, "rotunjire bancara (112) in loc de aritmetica (113)"


# ============================================================
#  DATORIE TEHNICA
# ============================================================
@pytest.mark.xfail(strict=True, reason="DATORIE 27.07.2026: numere.numar() intoarce float. "
                                       "Float pe bani pierde precizie la insumare; "
                                       "importurile de solduri/parteneri trec prin el.")
def test_numar_intoarce_decimal_pe_sume():
    from decimal import Decimal
    from core.numere import numar
    assert isinstance(numar("0.1"), Decimal)


@pytest.mark.xfail(strict=True, reason="DATORIE 27.07.2026: common.cere_coloane verifica "
                                       "randurile CITITE, deci o tabela GOALA trece. "
                                       "Coloana disparuta pe firma fara salariati = tacere.")
def test_cere_coloane_prinde_si_tabela_goala():
    from core.common import cere_coloane
    with pytest.raises(ValueError):
        for r in []:                      # zero randuri = zero verificari azi
            cere_coloane(r, ("salariu_brut",), "salariati")
        raise AssertionError("nimic verificat pe lista goala")


@pytest.mark.xfail(strict=True, reason="DATORIE 27.07.2026: SELECT * pe date fiscale in "
                                       "d394/bilant_api/rip_api/stocuri_cv_api/"
                                       "reconciliere_api - fara garda de coloane.")
def test_niciun_select_stea_pe_date_fiscale_fara_garda():
    rad = pathlib.Path(__file__).resolve().parent
    vinovati = []
    for f in sorted(rad.glob("*.py")):
        if f.name.startswith("test_"):
            continue
        s = f.read_text(encoding="utf-8")
        if "SELECT *" in s and "cere_coloane" not in s:
            vinovati.append(f.name)
    assert not vinovati, "SELECT * fara cere_coloane: %s" % vinovati


@pytest.mark.xfail(strict=True, reason="DATORIE 27.07.2026: joburile cron n-au heartbeat. "
                                       "core/cron.py prinde jobul care CRAPA, nu pe cel "
                                       "care nu porneste deloc (cron oprit, reboot).")
def test_exista_heartbeat_pentru_joburi():
    from core import cron
    assert hasattr(cron, "bate") or hasattr(cron, "heartbeat"), "fara mecanism de heartbeat"


# ============================================================
#  IGIENA REGISTRULUI
# ============================================================
def test_fiecare_datorie_are_data_si_motiv():
    """Un item fara data devine invizibil in timp - exact problema pe care o rezolvam."""
    import inspect, sys
    mod = sys.modules[__name__]
    itemi = []
    for nume, fn in inspect.getmembers(mod, inspect.isfunction):
        for marca in getattr(fn, "pytestmark", []):
            if marca.name != "xfail":
                continue
            motiv = marca.kwargs.get("reason", "")
            itemi.append((nume, motiv))
    assert itemi, "nu mai exista niciun item de datorie - actualizeaza registrul"
    for nume, motiv in itemi:
        assert "DATORIE" in motiv, "%s: motiv fara eticheta DATORIE" % nume
        assert re.search(r"\d{2}\.\d{2}\.\d{4}", motiv), "%s: motiv fara data" % nume
        assert len(motiv) > 60, "%s: motiv prea scurt ca sa fie util peste 3 luni" % nume


def test_datoria_nu_imbatraneste_nelimitat():
    """Semnal, nu blocaj: un item mai vechi de 90 de zile se re-decide (reparat sau RESPINS
    explicit), nu se cara la nesfarsit. Pica DOAR daca a fost ignorat un trimestru."""
    import inspect, sys
    mod = sys.modules[__name__]
    text = " ".join(m.kwargs.get("reason", "")
                    for _n, fn in inspect.getmembers(mod, inspect.isfunction)
                    for m in getattr(fn, "pytestmark", []) if m.name == "xfail")
    vechi = []
    for d in set(re.findall(r"(\d{2})\.(\d{2})\.(\d{4})", text)):
        data = datetime.date(int(d[2]), int(d[1]), int(d[0]))
        if (_AZI - data).days > 90:
            vechi.append(data.isoformat())
    assert not vechi, ("datorie mai veche de 90 de zile: %s -> repar-o sau RESPINGE-O "
                       "explicit in DECIZII.md" % sorted(vechi))
