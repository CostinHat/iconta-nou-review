

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



def test_taxcode_livrari_period_aware():
    """TaxCode-ul SAF-T pentru livrari e PERIOD-AWARE pe data facturii: ANAF a schimbat codurile cu
    01.08.2025 (Legea 141/2025). O factura dinainte foloseste codurile epocii (19/9/5), una de dupa
    cele noi (21/11/9/5). Fara period-awareness, o raportare retroactiva (luna < 08.2025) emitea
    coduri gresite (19% negasit in tabela noua -> default 310312 = taxare inversa)."""
    from core.d406 import _taxcode_livrari
    from datetime import date
    assert _taxcode_livrari(21, date(2026, 3, 1)) == "310344"     # post: 21%
    assert _taxcode_livrari(11, date(2025, 8, 1)) == "310351"     # post: 11% (chiar la granita)
    assert _taxcode_livrari(19, date(2025, 6, 1)) == "310309"     # pre: 19% (exista DOAR pre)
    assert _taxcode_livrari(9,  date(2025, 6, 1)) == "310310"     # pre: 9%
    assert _taxcode_livrari(9,  date(2026, 1, 1)) == "310357"     # post: 9% (cod DIFERIT de pre!)
    assert _taxcode_livrari(21, None) == "310344"                 # data lipsa -> tabela curenta (post)
