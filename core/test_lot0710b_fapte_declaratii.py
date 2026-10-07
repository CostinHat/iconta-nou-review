# -*- coding: utf-8 -*-
"""GARD — faptele din declarații pe care aplicația le punea în locul omului (lotul 07.10 B, comanda Costin A.2: „Restul îl
încadrezi tu după regulă”). Găsite măsurând clasa (input precompletat / fallback `|| "x"` / cheie trimisă fără câmp):

  · D204 `forma_org` — pleca „1” fără câmp pe ecran. Structura ANAF D204 pct.24: „Listă de valori (1,2)” — 1 asociere fără
    personalitate juridică / 2 entitate supusă regimului transparenței fiscale; validatorul instalat respinge 3.
  · D208 `mod_transfer` — pleca „1” (vânzare-cumpărare) fără câmp. Structura ANAF D208 v1.0.0 (19.02.2024) poz.22: 1 vânzare-
    cumpărare / 2 moștenire / 3 donație / 4 altă modalitate (poz.23: cu 4, `alt_mod_transfer` obligatoriu, altfel interzis).
  · D318 `currency` — pleca „EUR”. HG 1/2016 pct.73 alin.(6) lit.e-f: sumele „exprimate în moneda statului membru de rambursare”.
  · D398 `currency` — valoare FIXĂ, nu alegere: CF art.314 alin.(10) / art.315 alin.(12) / art.315^2 alin.(22) — „Declarația
    specială de TVA se întocmește în euro.”
Fiecare aserțiune e pe structură (lista erorilor, atributul XML), nu pe text.
"""
import xml.etree.ElementTree as ET

from core import d204, d208, d318, d398
from core.common import Perioada
from core.test_d204_formular import _m as _m204
from core.test_d208_formular import _m as _m208
from core.test_d318_formular import _m as _m318
from core.test_d398_formular import _m as _m398


def _noi(fn, prof, gresit, bun):
    """Erorile pe care le are `gresit` și nu le are `bun` — exact cele produse de faptul lipsă."""
    eb = fn(prof, bun)
    return [e for e in fn(prof, gresit) if e not in eb]


def test_d204_forma_de_organizare_se_cere():
    m = _m204()
    fara = _m204(activitate=dict(m["activitate"], forma_org=None))
    assert len(_noi(d204.erori_generare, {}, fara, m)) == 1           # structura ANAF D204 pct.24: forma_org obligatoriu
    assert d204.calcul_d204(fara)["activitati"][0]["forma_org"] is None  # nu mai devine „1”
    trei = _m204(activitate=dict(m["activitate"], forma_org=3))
    assert len(_noi(d204.erori_generare, {}, trei, m)) == 1           # validatorul: 3 „nu se afla in lista”


def test_d204_categoria_se_cere():
    m = _m204()
    fara = _m204(activitate=dict(m["activitate"], categ_venit=None))
    assert d204.calcul_d204(fara)["activitati"][0]["categ_venit"] is None
    assert len(_noi(d204.erori_generare, {}, fara, m)) >= 1


def test_d208_modalitatea_de_transfer_se_cere():
    m = _m208()
    assert len(_noi(d208.erori_generare, {}, _m208(mod_transfer=None), m)) == 1     # D208 v1.0.0 poz.22
    assert len(_noi(d208.erori_generare, {}, _m208(mod_transfer="4"), m)) == 1      # poz.23: 4 cere explicația


def test_d208_alta_modalitate_ajunge_in_xml():
    xml, _r = d208.genereaza(None, None, Perioada(2026, luna=12), _m208(mod_transfer="4", alt_mod_transfer="schimb"))
    tz = ET.fromstring(xml).find("{mfp:anaf:dgti:d208:declaratie:v1}tranzactie")
    assert (tz.get("mod_transfer"), tz.get("alt_mod_transfer")) == ("4", "schimb")


def test_d318_moneda_se_cere_si_liniile_o_preiau():
    m = _m318()
    assert len(_noi(d318.erori_generare, {}, _m318(currency=None), m)) == 1         # HG 1/2016 pct.73 alin.(6) lit.e
    xml, _r = d318.genereaza(None, None, Perioada(2025, luna=12), _m318(currency="HUF"))
    root = ET.fromstring(xml)
    pi = root.find("{mfp:anaf:dgti:d318:declaratie:v1}PurchaseInformation")
    assert (root.get("currency"), pi.get("currency_ta"), pi.get("currency_va"), pi.get("currency_dva")) == ("HUF",) * 4


def test_d398_moneda_e_euro_prin_lege():
    xml, _r = d398.genereaza(None, None, Perioada(2026, luna=3), _m398(currency="USD"))
    assert ET.fromstring(xml).get("currency") == d398.MONEDA_OSS == "EUR"            # CF art.314 alin.(10)
