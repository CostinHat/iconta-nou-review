# -*- coding: utf-8 -*-
"""GARDĂ pentru interdicția 61 — lista dependenților unui articol, generabilă la cerere.

Unealta compune două hărți: `articol → cote care-l citează` și `cotă → funcții care depind de ea`.
**Modul ei propriu de eșec e tăcerea** (interdicția 76): dacă oricare hartă se golește — registrul nu
se mai parsează, graful se rupe — răspunsul devine „nimic nu depinde de articolul ăsta", care e exact
răspunsul greșit pe care nimeni nu-l verifică. De aceea cazurile de mai jos pinează CIFRE, nu forme.

Al doilea mod de eșec: potrivire **prea largă**. Un apel fără niciun câmp ar întoarce tot codebase-ul
și ar părea foarte util. Ridică.
"""
import pytest

from core import dependenti_act as da


def test_cazul_cunoscut_art291_tva():
    """CAZ CUNOSCUT. Art. 291 din Codul fiscal ține cotele de TVA; se schimbă des, prin acte diferite
    (Legea 227/2015 originar, Legea 141/2025 la zi). Lista dependenților lui nu are voie să fie mică."""
    d = da.dependenti(art="291")
    assert "tva_standard" in d["cote"], "art.291 nu duce la cota standard: %s" % d["cote"]
    assert len(d["cote"]) >= 3, "art.291 ține mai multe cote de TVA, văd doar %s" % d["cote"]
    assert len(d["functii"]) >= 50, (
        "doar %d funcții depind de art.291 — pe graful conflat, înainte de R17, cifrele erau de acest "
        "ordin de mărime mic; dacă a scăzut, graful s-a rupt din nou" % len(d["functii"]))
    assert len(d["fisiere"]) >= 3


def test_cazul_cunoscut_facilitatea_salariului_minim():
    """CAZ CUNOSCUT, alt act: OUG 156/2024 art.LXVI și OUG 89/2025 art.III țin facilitatea."""
    d = da.dependenti(tip="OUG", nr=89, an=2025)
    assert "facilitate_salariu_minim" in d["cote"], d["cote"]
    assert len(d["functii"]) >= 20, "doar %d funcții — compunerea s-a rupt" % len(d["functii"])


def test_un_articol_inexistent_nu_intoarce_tot():
    """POTRIVIRE PREA LARGĂ, celălalt mod de eșec: un articol care nu e în registru dă mulțimea VIDĂ,
    nu tot codebase-ul."""
    d = da.dependenti(art="99999")
    assert d["cote"] == [] and d["functii"] == [], "potrivirea a fost prea largă: %s" % d["cote"]


def test_apelul_fara_camp_ridica():
    """«Ce se atinge?» fără să spui de ce, nu e o întrebare — și un răspuns cu tot codul ar părea util."""
    with pytest.raises(ValueError):
        da.dependenti()


def test_acoperirea_nu_e_vida():
    """ANTI-VACUU. Dacă registrul sau graful se golesc, acoperirea cade la zero și unealta ar raporta
    liniște. Cifra măsurată la 23.08: 17 articole, 16 cu listă generabilă."""
    tot, gen = da.acoperire()
    assert tot >= 15, "doar %d articole citite din registru — harta s-a rupt" % tot
    assert gen >= 15, "doar %d articole cu listă generabilă din %d — compunerea s-a rupt" % (gen, tot)


def test_fisierele_sunt_reale():
    """Dependenții numesc fișiere care există — altfel lista e o afirmație despre nimic."""
    import pathlib
    rad = pathlib.Path(__file__).resolve().parents[1] / "core"
    d = da.dependenti(art="291")
    lipsa = [f for f in d["fisiere"] if not (rad / f).exists()]
    assert not lipsa, "fișiere inexistente în lista dependenților: %s" % lipsa
