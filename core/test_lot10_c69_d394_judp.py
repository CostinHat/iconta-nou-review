# -*- coding: utf-8 -*-
"""[lotul 10, deficiența C69] D394: județul partenerului neînregistrat fără cod (judP) — al partenerului, nu inventat.

Ce era (core/d394.py `build_xml`, înainte): „Proxy = judetul FIRMEI (partenerul neinregistrat n-are adresa stocata)”, iar fără el
`judP="40"` (București) cu un avertisment. Sursa: anaf_surse/d394_struct_anaf.txt, pct.222: „judP Judet beneficiar/ furnizor/ prestator
C(2) Nomenclator … null pt tip_partener <>2 sau cuiP<>null … Obligatoriu pt tip_partener=2 și cuiP=null și taraP=RO” — câmpul e
cerut, deci se aplică decizia Costin C69 pct.1 prin analogie (comanda N2 pct.5): „Completez din ANAF … se blochează numai ce rămâne
necompletat” — județul de pe factură / operațiunea manuală, altfel din ANAF pentru codul fiscal al partenerului, altfel D394 se oprește.
ANAF simulat (`interogare=`); CUI 2864518 (cifra de control verificată).
"""
import re
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from core import anaf_api
from core.common import Perioada
from core.d394 import build_xml, calcul_d394

LOCALITATI_ANAF_REAL = True   # cache-ul ANAF se umple aici printr-o interogare simulată (core/conftest.py)

PROF = {"cui": "14399840", "nume": "FIRMA C69 SRL", "judet": "B", "tva_la_incasare": False, "platitor_tva": True, "tip_decont": "L"}


def _f(cui, nume, judet=None, platitor=None, directie="emisa"):
    return {"cui": cui, "nume": nume, "directie": directie, "cota": 21, "baza": Decimal(100), "tva": Decimal(21),
            "taxare_inversa": False, "categorie_331": None, "judet": judet, "platitor_tva": platitor}


def _judp(xml):
    """judP al fiecărui element op1 care îl poartă, citit din XML (nu căutat ca text)."""
    rad = ET.fromstring(xml.encode("utf-8"))
    return [e.get("judP") for e in rad.iter() if e.tag.rsplit("}", 1)[-1] == "op1" and e.get("judP") is not None]


def _numiti(mesaj):
    """Partenerii numiți de refuzul `d394.judete_partener` — lista dintre „obligatoriu): ” și „. Completează”."""
    return mesaj.split("obligatoriu): ", 1)[1].split(". Completează", 1)[0]


def test_fixtura_e_valida():
    from core.identitate import valideaza_cui
    assert valideaza_cui("2864518")[0]


def test_judetul_de_pe_factura_nu_al_firmei():
    r = calcul_d394(PROF, Perioada(2026, luna=6), {"facturi": [_f("", "POPESCU ION", judet="Cluj")]})
    assert _judp(build_xml(r)) == ["12"]           # pct.222 judP „Nomenclator”: Cluj 12 (firma e în București, 40 — proxy-ul vechi)


def test_fara_judet_d394_se_opreste_numit():
    with pytest.raises(ValueError) as ei:
        calcul_d394(PROF, Perioada(2026, luna=6), {"facturi": [_f("", "POPESCU ION")]})
    m = str(ei.value)
    assert re.findall(r"^D394 nu se poate genera: lipsește (\w+) pe factură la ", m) == ["județul"], m                                      # pct.222 „Obligatoriu pt tip_partener=2 și cuiP=null” — nu „40”
    assert _numiti(m) == "POPESCU ION (operațiunea L)", m                    # partenerul fără județ, numit (și numai el)


def test_firma_neplatitoare_cu_cui_ia_judetul_din_anaf():
    """Partener cu CUI valid, dar neînregistrat în scopuri de TVA (factura îl îngheață `platitor_tva=False`) -> tip_partener 2, cuiP
    null; județul din ANAF (domiciliul fiscal, `dcod_JudetAuto`), adus înaintea tranzacției."""
    anaf_api.aduce_localitati(["2864518"], interogare=lambda l: [{"cui": "2864518", "gasit": True, "localitate": "Pantelimon",
                                                                  "judet": "IF"}])
    r = calcul_d394(PROF, Perioada(2026, luna=6), {"facturi": [_f("RO2864518", "ALTEX ROMANIA SRL", platitor=False)]})
    assert _judp(build_xml(r)) == ["23"]           # Ilfov 23 (Nomenclator 1 - Judete)


def test_judete_diferite_pe_acelasi_partener_nu_se_aleg():
    with pytest.raises(ValueError) as ei:
        calcul_d394(PROF, Perioada(2026, luna=6), {"facturi": [_f("", "POPESCU ION", judet="CJ"), _f("", "POPESCU ION", judet="IS")]})
    # aplicația nu alege între ele: partenerul e numit cu ambele județe (Nomenclator 1 - Judete: Cluj 12, Iași 22)
    assert _numiti(str(ei.value)) == "POPESCU ION (operațiunea L, pe facturi cu județe diferite: 12, 22)"


def test_build_xml_nu_inventeaza_nici_chemat_direct():
    r = calcul_d394(PROF, Perioada(2026, luna=6), {"facturi": [_f("", "POPESCU ION", judet="CJ")]})
    r.judP.clear()
    with pytest.raises(ValueError):
        build_xml(r)
