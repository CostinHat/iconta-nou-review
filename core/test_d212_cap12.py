# -*- coding: utf-8 -*-
"""D212 Etapa 3 — venit din activități independente pe NORMĂ DE VENIT: datele contabilului -> cap12 -> XML -> DUK.

Rândurile subsecțiunii I.1.2 (Subsecțiunea a 2-a lit.A) urmează instrucțiunile de completare (OPANAF 2736/2025,
anexa 2, pct.19.1 A2), cota urmează CF art.69^2 alin.(1), structura (15 atribute opționale, element repetabil,
R8 bifa112 => cap12) urmează D212Validator.jar v9 instalat. Aserțiuni pe valori, pe arborele XML (ElementTree)
și pe verdictul DUK — nu pe șiruri din mesaje.
"""
import xml.etree.ElementTree as ET

import pytest

from core import d212
from core.common import Perioada

NSX = "{%s}" % d212.NS
CNP = "1800101221144"          # cifra de control verificată (algoritmul oficial)
ID = {"cif": CNP, "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}
AN = 2025


def _rad(xml):
    return ET.fromstring(xml.split("?>", 1)[1])


# ── rândurile (pct.19.1 A2) ───────────────────────────────────────────────────────────────────────────────
def test_an_intreg_venitul_net_e_norma_si_impozitul_10_la_suta():
    # rd.9 lit.a: „suma de la rd.7 «Norma de venit»”; CF art.69^2 alin.(1): „prin aplicarea cotei de 10% asupra normei"
    c = d212.cap12_norma({"norma": 30000}, AN)
    assert (c["real_norma_venit"], c["real_venit_net_anual"], c["real_venit_impozit"], c["real_impozit"]) == \
        (30000, 30000, 30000, 3000)
    assert "real_ajustare" not in c and "norma_data_incep" not in c and c["norma_forma_org"] == 1


def test_norma_ajustata_inlocuieste_norma():
    # rd.9 lit.a: „sau suma de la rd.8 «Norma ajustată potrivit legii», după caz”
    c = d212.cap12_norma({"norma": 30000, "norma_ajustata": 24000}, AN)
    assert (c["real_ajustare"], c["real_venit_net_anual"], c["real_impozit"]) == (24000, 24000, 2400)


@pytest.mark.parametrize("a,net", [
    ({"data_incep": "2025-07-01"}, 15123),                              # 184 zile: 30000 / 365 × 184 = 15123,29
    ({"data_sf": "31.03.2025"}, 7397),                                  # 90 zile: 30000 / 365 × 90 = 7397,26
    ({"zile_intrerupere": 30}, 27534),                                  # 335 zile: 30000 / 365 × 335 = 27534,25
    ({"data_incep": "2025-03-01", "data_sf": "2025-03-31", "zile_intrerupere": 10}, 1726),  # 21 zile -> 1726,03
])
def test_perioada_partiala_se_raporteaza_la_365_de_zile(a, net):
    # instrucțiuni rd.9: „prin raportarea … la 365 de zile, iar rezultatul se înmulțește cu numărul zilelor de activitate”
    # MUTAȚIE: rd.9 = norma oricât ar fi durat activitatea -> 30000 -> pică
    c = d212.cap12_norma(dict(a, norma=30000), AN)
    assert (c["real_venit_net_anual"], c["real_venit_impozit"]) == (net, net)
    assert c["real_impozit"] == int((net * 10 + 50) // 100)            # 10% half-up pe lei întregi


def test_an_bisect_proratarea_nu_depaseste_norma():
    # 2024: 01.01–31.12 cu dată de început completată = 366 zile; 30000 / 365 × 366 > norma -> rd.9 rămâne norma
    # (CF art.69 alin.(5): norma „se reduce proporțional” — niciodată nu crește)
    c = d212.cap12_norma({"norma": 30000, "data_incep": "2024-01-01"}, 2024)
    assert c["real_venit_net_anual"] == 30000


@pytest.mark.parametrize("a,impozabil", [
    ({"nr_zile_scutite": 73}, 24000),                                   # an întreg: 30000 − 30000 / 365 × 73 = 24000
    ({"data_incep": "2025-07-01", "nr_zile_scutite": 84}, 8219),        # 184 − 84 = 100 zile: 30000 / 365 × 100 = 8219,18
])
def test_zilele_scutite_reduc_venitul_impozabil_rd_9_1(a, impozabil):
    # rd.9.1 lit.a: „suma de la rd.9 … redusă proporțional cu numărul de zile calendaristice … pentru care venitul este
    # scutit”; impozitul se aplică pe rd.9.1. MUTAȚIE: impozit pe rd.9 în loc de rd.9.1 -> 3000 / 1512 -> pică
    c = d212.cap12_norma(dict(a, norma=30000), AN)
    assert (c["real_venit_impozit"], c["norma_nr_zile_scutite"]) == (impozabil, a["nr_zile_scutite"])
    assert c["real_impozit"] == int((impozabil * 10 + 50) // 100)


@pytest.mark.parametrize("a", [
    {},                                                                 # norma lipsă
    {"norma": 30000, "norma_ajustata": -1},
    {"norma": 30000, "data_incep": "2024-12-01"},                       # în afara anului de impunere
    {"norma": 30000, "data_incep": "2025-06-01", "data_sf": "2025-05-01"},
    {"norma": 30000, "zile_intrerupere": 400},
    {"norma": 30000, "data_sf": "2025-01-10", "nr_zile_scutite": 11},   # mai multe zile scutite decât de activitate
    {"norma": 30000, "forma_org": 3},                                   # validator: interval [1,2]
    {"norma": 30000, "data_incep": "1 iulie"},
])
def test_date_incoerente_refuzate(a):
    with pytest.raises(ValueError):
        d212.cap12_norma(a, AN)


# ── XML + bife + DUK ─────────────────────────────────────────────────────────────────────────────────────────
NORME = [{"norma": 30000, "caen": "9602", "sediu": "Bucuresti, Str. Lunga 1", "nr_doc_autoriz": "12345",
          "data_doc_autoriz": "2020-05-04"},
         {"norma": 27000, "norma_ajustata": 24000, "caen": "4520", "data_incep": "2025-07-01", "nr_zile_scutite": 20,
          "forma_org": 2}]


def test_xml_o_sectiune_cap12_pe_activitate_si_bifa112():
    # instrucțiuni: „câte o secțiune pentru fiecare activitate și loc”; R8: bifa112=1 => cap12
    # MUTAȚIE: scos `manual["bifa112"] = "1"` -> bifa112="0" -> pică
    xml, r = d212.genereaza(None, None, Perioada(an=AN), dict(ID, norma=NORME))
    rad = _rad(xml)
    secs = rad.findall(NSX + "cap12")
    assert rad.get("bifa112") == "1" and r.capitole == ["cap12"] and len(secs) == 2
    assert (secs[0].get("norma_caen"), secs[0].get("norma_data_doc_autoriz"), secs[0].get("real_impozit")) == \
        ("9602", "04.05.2020", "3000")
    assert (secs[1].get("norma_forma_org"), secs[1].get("norma_data_incep"), secs[1].get("real_venit_net_anual"),
            secs[1].get("real_venit_impozit")) == ("2", "01.07.2025", "12099", "10784")
    assert set(secs[1].attrib) <= d212._CAMPURI["cap12"]


def test_fara_activitati_pe_norma_nu_apare_cap12():
    xml, _ = d212.genereaza(None, None, Perioada(an=AN), dict(ID))
    rad = _rad(xml)
    assert rad.find(NSX + "cap12") is None and rad.get("bifa112") == "0"


def test_eroarea_numeste_activitatea():
    with pytest.raises(ValueError) as e:
        d212.genereaza(None, None, Perioada(an=AN), dict(ID, norma=[{"norma": 1000}, {"norma": 0}]))
    assert str(e.value).startswith("Activitatea 2 ")


def test_venitul_agricol_pe_norma_refuzat_nu_tacut():
    # Subsecțiunea a 4-a (CF art.107 alin.(2)) n-are loc în structura validatorului instalat (J13.0.1): refuz numit
    with pytest.raises(ValueError):
        d212.genereaza(None, None, Perioada(an=AN), dict(ID, agricol=[{"norma": 5000}]))


def _duk():
    try:
        from core import duk
        return duk if duk.poate_valida("d212") else None
    except Exception:
        return None


def test_DUK_valid_pe_cap12_generat():
    duk = _duk()
    if duk is None:
        pytest.skip("DUK indisponibil")
    xml, _ = d212.genereaza(None, None, Perioada(an=AN), dict(ID, norma=NORME))
    v = duk.valideaza(xml, "d212", an=AN, luna=12, timeout=120)
    assert v.get("stare") == "valid", v.get("erori")
