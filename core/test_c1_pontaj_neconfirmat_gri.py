# -*- coding: utf-8 -*-
"""C1 (audit tenant_003): starea 'pontaj neconfirmat' pe Stat de plata e o stare de PERIOADA
(an,luna,domeniu), afisata dupa DS cap.23 (semafor GRI + .caseta-info, NU rosu), o data la nivel
de luna. Marcajul per-salariat rosu 'pontaj neconfirmat' (fapt de luna afisat ca atribut de salariat,
care implica fals ca pontajul altui salariat ar fi confirmat) e INTERZIS. Consecinta reala per-salariat
e 'tichete blocate' (gri). Gard de continut pe firme.js.
"""
import io, os, re
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRME = io.open(os.path.join(_ROOT, "static/js/ecrane/firme.js"), encoding="utf-8").read()


def test_fara_marcaj_rosu_pontaj_neconfirmat_per_salariat():
    # DS cap.23: starea informativa de perioada NU se coloreaza rosu; marcajul per-salariat rosu e interzis.
    assert "⚠ pontaj neconfirmat" not in FIRME, (
        "marcaj rosu per-salariat 'pontaj neconfirmat' interzis (DS cap.23: stare de perioada "
        "informativa afisata gri, nu rosu; consecinta per-salariat = 'tichete blocate')")


def test_banner_pontaj_neconfirmat_e_card_informativ_nu_ecran_nota_rosu():
    # DS cap.23: starea de lună = informativă (gri), nu atenționare. [lotul 14, 687] banner-ul de lună e card-rezumat de un rând (DS cap.9 v2.105),
    # cu ton „info” (punct gri, nu galben / roșu), iar în fereastra lui textul stă într-o `.caseta-info` — ca ecranul de confirmare.
    assert 'pontajNeconf ? cardInfo("pontaj"' in FIRME, "banner-ul de luna 'pontaj neconfirmat' trebuie sa fie card-rezumat informativ (DS cap.23 + cap.9)"
    assert re.search(r'const cardInfo = \(id, text, titlu, html\) => \(\{ id, ton: "info", text, titlu, deschide: .*<div class="caseta-info">', FIRME), \
        "cardInfo = ton informativ (nu atentie / eroare) + .caseta-info in fereastra cardului"
    assert 'pontajNeconf ? `<div class="ecran-nota"' not in FIRME, (
        "banner-ul de luna NU ecran-nota rosu (DS cap.23: stare informativa, nu atentionare)")
    # [05.10.2026] DS cap.8 v2.70: bulina „●” e un caracter (text) — gri de text `--gri`, nu `--gri-semafor` (2,5:1 pe alb).
    # Starea rămâne GRI (informativă), cum a cerut decizia C1.
    assert '<span style="color:var(--gri)">●</span> Pontajul lunii' in FIRME, "semaforul gri (DS cap.8) lipseste din stat"
