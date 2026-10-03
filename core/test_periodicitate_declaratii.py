# -*- coding: utf-8 -*-
"""GARD — periodicitatea declarațiilor: D208 lunară, „semestrial” cere luna explicit, iar selectorul nu primește o
periodicitate pe care ecranul n-o știe (lot 19, defectul 8, 03.10.2026).

Ce s-a întâmplat: D208 era „semestrial”; ecranul n-avea ramură pentru asta, cădea pe cea lunară (arăta luna), dar
cererea trimitea luna numai pentru „lunar” — iar adaptorul punea `luna or 12`. Orice D208 ieșea pe decembrie, deși
CF art.113 o cere lunar. D407 (doar API) avea același `or 12`: semestrul I trimis fără lună ieșea pe decembrie.
"""
import os
import re

import pytest

from core import declaratii_api as da

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_d208_e_lunara():
    # CF art.113: notarii „au obligația să depună lunar, până la data de 25 inclusiv a lunii următoare”
    assert da.periodicitate("d208") == "lunar"
    assert da.valideaza_cerere("d208", {"an": 2026})            # fără lună -> refuz, nu decembrie tăcut
    from core import scadente
    assert scadente.scadenta("d208", 2026, luna=3) == "27.04.2026"   # 25.04.2026 sâmbătă -> luni 27


def test_semestrial_cere_luna_6_sau_12():
    # DUK regula RLuna (D407): luna de raportare 6 sau 12
    assert da.valideaza_cerere("d407", {"an": 2026}), "cerere D407 fără lună trebuie refuzată, nu completată cu 12"
    assert da.valideaza_cerere("d407", {"an": 2026, "luna": 3})
    # luna 3 primește EXACT o eroare în plus față de 6/12 — refuzul semestrial; restul (manual lipsă) e același
    e3 = da.valideaza_cerere("d407", {"an": 2026, "luna": 3})
    for luna in (6, 12):
        assert len(e3) == len(da.valideaza_cerere("d407", {"an": 2026, "luna": luna})) + 1


def test_adaptoarele_nu_completeaza_luna_in_tacere():
    src = open(os.path.join(RAD, "core", "declaratii_api.py"), encoding="utf-8").read()
    for tip in ("d208", "d407"):
        corp = src[src.index("def _%s(" % tip):src.index("\n\n", src.index("def _%s(" % tip))]
        cod = "\n".join(l.split("#")[0] for l in corp.splitlines())     # comentariile pot povesti forma veche
        assert "or 12" not in cod, "_%s completează luna cu 12 când lipsește" % tip


def test_selectorul_primeste_doar_periodicitati_tratate_de_ecran():
    js = open(os.path.join(RAD, "static", "js", "ecrane", "declaratii.js"), encoding="utf-8").read()
    corp = js[js.index("function randPerioada("):js.index("function legPerioada(")]
    tratate = set(re.findall(r'per === "(\w+)"', corp)) | {"lunar"}     # „lunar” e ramura implicită
    necunoscute = {t: da.periodicitate(t) for t in da.tipuri() if da.periodicitate(t) not in tratate}
    assert necunoscute == {}, "tipuri din selector cu periodicitate fără ramură în randPerioada: %s" % necunoscute


@pytest.mark.parametrize("per", ["semestrial"])
def test_CALIBRARE_garda_selectorului_prinde(per, monkeypatch):
    monkeypatch.setitem(da.DECLARATII, "d208", (per, da.DECLARATII["d208"][1]))
    with pytest.raises(AssertionError):
        test_selectorul_primeste_doar_periodicitati_tratate_de_ecran()
