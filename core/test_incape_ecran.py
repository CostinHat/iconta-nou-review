# -*- coding: utf-8 -*-
"""[lotul 14, deficiența 687] GARD: fiecare fereastră de lucru încape pe un singur ecran la 1920 × 1080 și la 1366 × 768 (comanda Costin 14.1,
verbatim: „Verificatorul face captura la ambele rezoluții și blochează lotul la orice derulare.”). Artefactul `frontend_test/vizual/incape_ecran.json`
e produs de `incape_ecran.py` (browser, aplicația de probă; ca `acoperire_vizuala.json`) și cuplat mecanic de sursele UI (`ui_hash`):

- UI schimbat de la ultima măsurătoare -> PICĂ (rulează `frontend_test/vizual/incape_ecran.py` și comite artefactul);
- un ecran din `nav_ecrane` fără măsurătoare, sau măsurat la altă pereche de rezoluții -> PICĂ;
- o fereastră care derulează (corpul, lateral, o cutie care nu e tabel) sau al cărei tabel a rămas fără loc (zona sub 30% din fereastră) -> PICĂ,
  afară de cele din `DE_REORGANIZAT` — lista ferestrelor încă nereorganizate, cu motivul: ea coboară NUMAI (o fereastră care a început să
  încapă trebuie scoasă din listă, altfel testul cade — un clichet, ca restul clichetelor numite ale proiectului).
MUTAȚIE: o fereastră măsurată „derulează” și absentă din `DE_REORGANIZAT` -> pică.
"""
import json
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "frontend_test", "vizual"))
from acoperire_hash import ui_hash, ecrane_incape  # noqa: E402

ARTEFACT = os.path.join(_RAD, "frontend_test", "vizual", "incape_ecran.json")
REZOLUTII = ["1920x1080", "1366x768"]
RELE = ("deruleaza", "deruleaza-cutie", "zona-ingusta", "eroare")

#: Ferestrele încă nereorganizate (lotul 14, 687 — parțial): {ecran: motivul}. Coboară numai.
DE_REORGANIZAT = {}


def _incarca():
    if not os.path.exists(ARTEFACT):
        pytest.fail("incape_ecran.json lipsește — rulează frontend_test/vizual/incape_ecran.py")
    return json.load(open(ARTEFACT, encoding="utf-8"))


def test_masuratoarea_e_proaspata_si_la_ambele_rezolutii():
    a = _incarca()
    assert a.get("ui_hash") == ui_hash(), "UI-ul s-a schimbat de la ultima măsurătoare a ferestrelor — rulează frontend_test/vizual/incape_ecran.py"
    assert a.get("rezolutii") == REZOLUTII, a.get("rezolutii")


def test_toate_ferestrele_sunt_masurate():
    a = _incarca()
    lipsa = [e for e in ecrane_incape() if e not in a.get("ecrane", {})]
    assert not lipsa, "ferestre din nav_ecrane fără măsurătoare: %s" % lipsa
    fara_rez = [e for e, d in a["ecrane"].items() if sorted(d) != sorted(REZOLUTII)]
    assert not fara_rez, "ferestre măsurate la altă pereche de rezoluții: %s" % fara_rez


def test_nicio_fereastra_nu_deruleaza():
    a = _incarca()
    rele = {e: {r: (v["verdict"], v.get("depasire"), v.get("zona_h")) for r, v in d.items() if v["verdict"] in RELE}
            for e, d in a["ecrane"].items() if any(v["verdict"] in RELE for v in d.values())}
    noi = {e: r for e, r in rele.items() if e not in DE_REORGANIZAT}
    assert not noi, "ferestre care derulează la 1920×1080 / 1366×768 (DS cap.9 v2.105): %s" % noi


def test_lista_de_reorganizat_coboara_numai():
    a = _incarca()
    reparate = [e for e in DE_REORGANIZAT if e in a["ecrane"] and not any(v["verdict"] in RELE for v in a["ecrane"][e].values())]
    assert not reparate, "ferestre care acum încap — scoate-le din DE_REORGANIZAT: %s" % reparate
    necunoscute = [e for e in DE_REORGANIZAT if e not in a["ecrane"]]
    assert not necunoscute, "DE_REORGANIZAT numește ecrane care nu există: %s" % necunoscute
