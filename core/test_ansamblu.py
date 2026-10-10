# -*- coding: utf-8 -*-
"""GARD — catalogul „Ce cuprinde aplicația” după rol (deficiența 5, retestul Costin 09.10.2026: „Ana vede în catalog funcții de
administrator”). `core/ansamblu.py`: funcționalitățile platformei (nivel `admin`) numai pentru administratorul platformei; cele ale
administratorului de cabinet își poartă ruta, pe care drepturile o ascund asistentului.
  · drum nou: o funcționalitate de cabinet accesată din Setări / Asistenți fără rută în `RUTA_FUNCTIONALITATE` -> pică;
  · fiecare rută din `RUTA_FUNCTIONALITATE` există între gărzile rutelor și e REFUZATĂ asistentului (altfel marcajul n-ar ascunde nimic).
"""
import csv
import os
import re

from core import ansamblu as an

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _registru():
    return [r for r in csv.reader(open(os.path.join(_RAD, "FUNCTIONALITATI.csv"), encoding="utf-8-sig"))][1:]


def test_drum_nou_functia_de_administrator_de_cabinet_are_ruta():
    """MUTAȚIE: un ID scos din `RUTA_FUNCTIONALITATE` -> pică."""
    lipsa = [(r[2], r[0]) for r in _registru()
             if r[3].strip() == "cabinet" and re.match(r"^(Setari|card Asistenti)", r[4].strip()) and r[2].strip() not in an.RUTA_FUNCTIONALITATE]
    assert lipsa == [], "funcții de administrator de cabinet fără rută în core/ansamblu.RUTA_FUNCTIONALITATE: %s" % lipsa


def test_rutele_exista_si_sunt_refuzate_asistentului():
    import main
    from core import drepturi as d
    g = d.garzi_rute(main.app)
    refuzate = set(d.interzise("angajat", {"poate_pregati": True, "poate_valida": True, "poate_depune": True}, g))
    rele = [(fid, r) for fid, r in sorted(an.RUTA_FUNCTIONALITATE.items()) if r not in refuzate]
    assert rele == [], "rute din RUTA_FUNCTIONALITATE pe care serverul NU le refuză asistentului (marcajul n-ar ascunde nimic): %s" % rele


def test_platforma_numai_pentru_administratorul_ei():
    """MUTAȚIE: filtrul pe nivelul `admin` scos -> „Suspendare cabinet” ajunge la cabinet -> pică."""
    grupe = [{"titlu": "G", "icon": "i", "functii": ["Suspendare cabinet", "Generare contracte", "Chei API publice per cabinet"]}]
    randuri = {"Suspendare cabinet": ("F109", "admin"), "Generare contracte": ("F999", "firma"),
               "Chei API publice per cabinet": ("F005", "cabinet")}
    pentru = {rol: [(f["nume"], f["actiune"]) for g in an.functii(grupe, randuri, rol, set()) for f in g["functii"]]
              for rol in ("angajat", "admin_firma", "superadmin")}
    assert pentru["angajat"] == pentru["admin_firma"] == [("Generare contracte", None), ("Chei API publice per cabinet", "POST /cabinet/api-chei")]
    assert ("Suspendare cabinet", None) in pentru["superadmin"]


def test_catalogul_vorbeste_limba_contabilului():
    """[deficiența 201] Titlurile grupelor și numele funcționalităților din „Ce cuprinde aplicația” (același registru alimentează și
    pagina publică de prezentare) — fără „->”, coduri F…, „v9”, jargon englezesc, diacritice lipsă. MUTAȚIE: un nume vechi
    („Dispatch declarații”) pus la loc în registru -> pică."""
    from genereaza_grupe_functii import repartizeaza
    rele = []
    for g in repartizeaza():
        rele += [(g["titlu"], d) for d in an.limbaj_tehnic(g["titlu"])]
        rele += [(f, d) for f in g["functii"] for d in an.limbaj_tehnic(f)]
    assert not rele, rele
    assert an.limbaj_tehnic("Dispatch declarații") and an.limbaj_tehnic("Calcul (brut->net)"), "anti-vacuu"

