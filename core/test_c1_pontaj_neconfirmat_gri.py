# -*- coding: utf-8 -*-
"""C1 (audit tenant_003): starea 'pontaj neconfirmat' pe Stat de plata e o stare de PERIOADA
(an,luna,domeniu), afisata dupa DS cap.23 (semafor GRI + .caseta-info, NU rosu), o data la nivel
de luna. Marcajul per-salariat rosu 'pontaj neconfirmat' (fapt de luna afisat ca atribut de salariat,
care implica fals ca pontajul altui salariat ar fi confirmat) e INTERZIS. Consecinta reala per-salariat
e 'tichete blocate' (gri). Gard de continut pe firme.js.
"""
import io, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRME = io.open(os.path.join(_ROOT, "static/js/ecrane/firme.js"), encoding="utf-8").read()


def test_fara_marcaj_rosu_pontaj_neconfirmat_per_salariat():
    # DS cap.23: starea informativa de perioada NU se coloreaza rosu; marcajul per-salariat rosu e interzis.
    assert "⚠ pontaj neconfirmat" not in FIRME, (
        "marcaj rosu per-salariat 'pontaj neconfirmat' interzis (DS cap.23: stare de perioada "
        "informativa afisata gri, nu rosu; consecinta per-salariat = 'tichete blocate')")


def test_banner_pontaj_neconfirmat_e_caseta_info_nu_ecran_nota_rosu():
    # DS cap.23: banner-ul de luna = .caseta-info + semafor gri (ca ecranul de confirmare), nu ecran-nota rosu.
    assert 'pontajNeconf ? `<div class="caseta-info"' in FIRME, (
        "banner-ul de luna 'pontaj neconfirmat' trebuie sa fie .caseta-info (DS cap.23)")
    assert 'pontajNeconf ? `<div class="ecran-nota"' not in FIRME, (
        "banner-ul de luna NU ecran-nota rosu (DS cap.23: stare informativa, nu atentionare)")
    assert 'var(--gri-semafor)' in FIRME, "semaforul gri (DS cap.8) lipseste din stat"
