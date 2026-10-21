# -*- coding: utf-8 -*-
"""[lotul 10, deficiența C69] D101G: declarantul — din Date firmă, nu „ADMINISTRATOR” / „-”.

Ce era (core/d101g.py `build_xml`, înainte): `nume_declar` = `declarant_nume or "ADMINISTRATOR"`, `prenume_declar` = `or "-"`,
`functie_declar` = `or "ADMINISTRATOR"`. Comanda N2 pct.6: dacă sursa cere declarantul, aceeași poartă ca la D101 (`erori_declarant`).
Sursa: în anaf_surse/ nu există o structură D101G; validatorul ANAF D101G v2 e însă instalat (~/duk/dist/lib/D101GValidator.jar,
J2.0.0, sha256 identic cu cel publicat de ANAF la static.anaf.ro/…/update5/D101G_3), iar pe XML sintetic fără câmp răspunde
„eroare atribut: nume_declar: atributul trebuie sa existe” (la fel `prenume_declar`, `functie_declar`) — scratchpad N2/p_d101g_c.out.
"""
import xml.etree.ElementTree as ET

import pytest

from core import d101g
from core import firma_profil_api as fp
from core.common import Perioada

PROF = {"cui": "14399840", "nume": "FIRMA C69 SRL", "adresa": "Str. Probei 9", "caen": "6920",
        "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "ADMINISTRATOR"}


@pytest.mark.parametrize("camp", ["declarant_nume", "declarant_prenume", "declarant_functie"])
def test_declarantul_lipsa_opreste_D101G(camp):
    p = dict(PROF, **{camp: ""})
    assert d101g.erori_generare(p)                                   # validatorul D101G v2: „<camp>: atributul trebuie sa existe”
    with pytest.raises(ValueError):
        d101g.genereaza(None, None, Perioada(2025), dict(p, P01=1000, cota=16))
    res = d101g.calcul_d101g(p, 2025, intrari={"P01": 1000}, cota=16)
    with pytest.raises(ValueError):                                  # nici `build_xml` chemat direct nu completează
        d101g.build_xml(res)


def test_declarantul_firmei_ajunge_in_xml_nu_ADMINISTRATOR_implicit():
    xml, _r = d101g.genereaza(None, None, Perioada(2025), dict(PROF, declarant_functie="DIRECTOR", P01=1000, cota=16))
    rad = ET.fromstring(xml.encode("utf-8"))                         # atributele declarației, citite din XML, nu căutate ca text
    # validatorul D101G v2: „nume_declar / prenume_declar / functie_declar: atributul trebuie sa existe” — valorile din Date firmă
    assert (rad.get("nume_declar"), rad.get("prenume_declar"), rad.get("functie_declar")) == ("POPESCU", "ION", "DIRECTOR")
    assert set(fp.OBLIGATORII["declarant_functie"]) >= {"D101G"}    # panoul „Profil incomplet” o spune
