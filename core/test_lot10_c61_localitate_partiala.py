# -*- coding: utf-8 -*-
"""[lotul 10 — observația deschisă din lotul 9 „adresa cu localitatea parțială”, decisă de Code (DECIZII „Comanda 10.1: observațiile din
lotul 9”)] Adresa beneficiarului pe factură (CF art.319 alin.(20) lit.f: „denumirea/numele și adresa beneficiarului”) nu repetă o parte
din localitate: „Str. Lalelelor 3, Sector 2” + „Sector 2 Mun. Bucureşti” ieșea „…, Sector 2, Sector 2 Mun. Bucureşti”.
MUTAȚIE: ramura care scoate rândul cuprins în localitate (`pastrate`) scoasă din `adresa_tert` -> pică."""
from core import factura_pdf as fp


def test_randul_adresei_cuprins_in_localitate_nu_se_mai_scrie_o_data_in_plus():
    # CF art.319 alin.(20) lit.f — adresa beneficiarului, scrisă o dată
    assert fp.adresa_tert("Str. Lalelelor 3, Sector 2", "Sector 2 Mun. Bucureşti", "B", "RO") == "Str. Lalelelor 3, Sector 2 Mun. Bucureşti"
    assert fp.adresa_tert("Str. Mare 1\nSector 2", "Sector 2 Mun. Bucureşti", "B", "RO") == "Str. Mare 1, Sector 2 Mun. Bucureşti"


def test_randurile_cu_alte_cuvinte_raman_neatinse():
    assert fp.adresa_tert("Str. Cluj 5", "Turda", "CJ", "RO") == "Str. Cluj 5, Turda, Cluj"
    assert fp.adresa_tert("Str. Sector 2 Nr 4", "Sector 2 Mun. Bucureşti", "B", "RO") == "Str. Sector 2 Nr 4, Sector 2 Mun. Bucureşti"
    # adresa făcută numai din localitate nu se golește
    assert fp.adresa_tert("Sector 2", "Sector 2 Mun. Bucureşti", "B", "RO").endswith("Sector 2 Mun. Bucureşti")
    # localitatea cuprinsă integral rămâne ca înainte (C61)
    adr = "MUNICIPIUL BUCUREŞTI, SECTOR 2, STR. X NR 1"
    assert fp.adresa_tert(adr, "Sector 2 Mun. Bucureşti", "B", "RO") == adr
