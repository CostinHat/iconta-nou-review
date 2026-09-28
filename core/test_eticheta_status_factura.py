# -*- coding: utf-8 -*-
"""GARD [28.09.2026, P13 / interdictia 31]: eticheta de status factura se DERIVA din stare, nu o alege
cine randeaza.

Interdictia 31 - o eticheta aleasa de cine randeaza (JS), nu derivata din stare - poate contrazice starea
tacut. Instanta reala (CONFORMITATE, restanta T05): `static/js/ecrane/facturi_ecran.js` tinea
`STATUS_ETICHETA` cu 4 intrari, iar `core/nomenclator_status_factura.STARI` are 8 - CINCI stari
(`ciorna, de_recunoscut, descarcata, importata, stornata`) apareau contabilului ca TOKEN BRUT prin
`STATUS_ETICHETA[f.status] || f.status`, iar o eticheta FANTOMA (`platita`) numea o stare inexistenta in
nomenclator. *Clasa greseste in AMANDOUA directiile (METODA §22): rateaza stari reale si afirma una inexistenta.*

SURSA UNICA: `nomenclator_status_factura.ETICHETE`. Garda confrunta, in AMBELE directii:
  (1) ETICHETE acopera exact STARI (nicio stare fara eticheta, nicio eticheta fantoma) - consistenta interna;
  (2) STATUS_ETICHETA din facturi_ecran.js are exact aceleasi chei ca ETICHETE - ecranul oglindeste sursa.

MUTATIE: scoaterea unei stari din ETICHETE (sau din harta JS), ori adaugarea uneia fantoma, aprinde garda.
PROBA (portofoliu): o factura `stornata` (stare reala, nedeclarabila) - inainte de fix ecranul afisa tokenul
"stornata"; dupa fix afiseaza eticheta "stornată" derivata din nomenclator.
"""
import io
import os
import re

from core import nomenclator_status_factura as nsf

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_JS = os.path.join(RAD, "static/js/ecrane/facturi_ecran.js")


def _chei_js():
    js = io.open(_JS, encoding="utf-8").read()
    m = re.search(r"STATUS_ETICHETA\s*=\s*\{([^}]*)\}", js)
    assert m, "STATUS_ETICHETA n-a fost gasit in facturi_ecran.js - parser rupt sau harta redenumita"
    return set(re.findall(r"(\w+)\s*:", m.group(1)))


def test_ETICHETE_acopera_exact_STARI():
    stari, etich = set(nsf.STARI), set(nsf.ETICHETE)
    assert not (stari - etich), "stari fara eticheta (interdictia 31, contabilul vede tokenul): %s" % sorted(stari - etich)
    assert not (etich - stari), "etichete fantoma (stare inexistenta in nomenclator): %s" % sorted(etich - stari)


def test_JS_STATUS_ETICHETA_oglindeste_nomenclatorul():
    js, etich = _chei_js(), set(nsf.ETICHETE)
    assert not (etich - js), "stari cu eticheta in nomenclator dar FARA in facturi_ecran.js (vede tokenul brut): %s" % sorted(etich - js)
    assert not (js - etich), "etichete in facturi_ecran.js FARA stare in nomenclator (fantoma, ex. vechea 'platita'): %s" % sorted(js - etich)


def test_ANTI_VACUU_parserul_chiar_vede_harta():
    # daca regexul se rupe, _chei_js ar da set gol si testul de mai sus ar trece vacuu
    assert len(_chei_js()) >= 8, "STATUS_ETICHETA parsat cu <8 chei - parserul JS s-a rupt, garda ar trece in gol"


def test_eticheta_deriva_din_stare_nu_token_brut():
    # o stare reala nedeclarabila (stornata) are eticheta proprie, nu tokenul
    assert nsf.eticheta("stornata") == "stornată"
    assert nsf.eticheta("de_recunoscut") == "de recunoscut"
