

# ── GARD CALE NOMENCLATOR (01.08.2026): plan_oficial trebuie sa CITEASCA nomenclatorul oficial ──
# Bug prins de sweep-ul DUK: fisierul d406_nomenclatoare_anaf.properties a fost mutat in anaf_surse/,
# dar plan_oficial il cauta in radacina repo -> intorcea set GOL -> filtrarea pe norma nu rula ->
# conturile ONG (731-738, OMFP 3103/2017) scapau in SAF-T comercial -> DUK: "AccountID [731] trebuie
# sa se gaseasca in planul de conturi". Cu set gol nu se putea distinge "nomenclator lipsa" de "cale
# gresita" - de aceea gardul cere EXPLICIT continut, nu doar absenta erorii.
from core import d406 as _d406


def test_plan_oficial_citeste_nomenclatorul_norma_A():
    """Norma 'A' (societati comerciale, OMFP 1802/2014) are sute de conturi in nomenclatorul ANAF.
    Set gol = fisierul nu e gasit (cale stale) -> filtrarea moare tacut. Contul ONG 731 NU e in
    norma comerciala; un cont comercial standard (704) DA."""
    oficial = _d406.plan_oficial("A")
    assert len(oficial) > 100, "plan_oficial('A') GOL/mic (%d) - nomenclatorul nu e citit (cale?)" % len(oficial)
    assert "731" not in oficial, "731 (ONG) nu apartine normei comerciale 'A'"
    assert "704" in oficial, "704 (venituri servicii) trebuie sa fie in norma comerciala 'A'"
