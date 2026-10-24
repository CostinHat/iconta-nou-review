# -*- coding: utf-8 -*-
"""GARD [lotul 12, 163/184] — refuzul de perioadă închisă venit din bază ajunge la contabil în limba lui.

Triggerele de perioadă (`tenant_template.sql`, `trg_verifica_perioada_blocata` & co., pe toate firmele) refuză cu „PERIOADA_BLOCATA: luna
09/2099 este inchisa”. Ecranul arăta „Perioada luna 09/2099 este inchisa.” (Registrul-jurnal, `jurnal_api._motiv_din_baza`) sau o
traducere locală (`solduri_parteneri_api`). Acum textul se compune într-un singur loc (`perioada.text_blocare`): „Luna 09/2099 e închisă.”
N/A temei fiscal — text de ecran."""
from core import jurnal_api as J
from core import perioada as P


def test_textul_triggerului_devine_propozitia_contabilului():
    """MUTAȚIE: `text_blocare` întoarce textul neschimbat -> „Luna 09/2099 e închisă.” lipsește -> pică."""
    assert P.text_blocare("luna 09/2099 este inchisa") == "Luna 09/2099 e închisă."
    assert P.text_blocare("luna 9/2099 este inchisa") == "Luna 09/2099 e închisă."
    assert P.text_blocare("Salariile nu se pot calcula pentru 10/2026: pontajul lunii nu e confirmat") == (
        "Salariile nu se pot calcula pentru 10/2026: pontajul lunii nu e confirmat.")


def test_registrul_jurnal_arata_refuzul_bazei_tradus():
    """Refuzul bazei, cum îl primește Registrul-jurnal (cu contextul plpgsql după rând): fără eticheta de protocol, fără „Perioada luna”."""
    assert J._motiv_din_baza(Exception("PERIOADA_BLOCATA: luna 09/2099 este inchisa\nCONTEXT: PL/pgSQL function")) == "Luna 09/2099 e închisă."
