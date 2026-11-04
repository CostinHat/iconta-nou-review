# -*- coding: utf-8 -*-
"""scripts/productie_pass.py — gardul comun al scripturilor care SCRIU pe producție cu `--productie` (comanda 16.1-C3, pct.7). Un script cu `--productie` care face commit pe baza de producție
cheamă `cere_pass()` înainte să citească DSN-ul producției; fără verdictul `PASS <sha>` al lui scripts/publica_lot.py pentru commitul curent al lui `main` (aceeași funcție ca în
core/migrari_registru.py: `refuz_fara_pass`) iese cu refuz, fără nicio scriere. Scripturile care doar citesc producția (cifre_referinta, amprente_declaratii, ciorne_depasite: sesiune read-only)
nu cheamă nimic."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cere_pass(log=None):
    from core.migrari_registru import refuz_fara_pass
    motiv = refuz_fara_pass(log)
    if motiv:
        raise SystemExit(motiv)
