# -*- coding: utf-8 -*-
"""D212 Etapa 5c — veniturile din străinătate (Secțiunea 2, Subsecțiunea 1, cap14): o secțiune pe țară și sursă, rândurile
după instrucțiunile D212 (OPANAF 2736/2025) pct.39.6, creditul fiscal după CF art.131, cotele după categoria venitului (CF
art.130 alin.(2)); veniturile din străinătate în CAS, CASS 2.1/2.2 și în sumarul I.7. Validatorul instalat (J13.0.1) e
judecătorul structurii; nomenclatorul de țări e confruntat cu jar-ul."""
import os
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET

import pytest

from core import d212
from core.common import Perioada

ID = {"cif": "1800101221144", "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}
RAD = pathlib.Path(__file__).resolve().parent.parent
JAR = pathlib.Path(os.path.expanduser("~/duk/dist/lib/D212Validator.jar"))


def _s(**a):
    return d212.cap14_sectiune(a, 2025)


def test_metoda_creditului_plafonata_la_impozitul_roman():
    c = _s(tara="DE", categ_venit=2027, dubla_impunere=1, venit_brut=80000, chelt_deduc=20000, impozit_platit=4000)
    # CF art.64 alin.(1): 10% x 60.000 = 6.000; CF art.131 alin.(4): credit = impozitul plătit (4.000) <= 6.000
    assert (c["str_venit_net_anual"], c["str_impozit_datorat_Ro"], c["str_credit_fiscal"], c["str_dif_impozit_datorat"]) == \
        (60000, 6000, 4000, 2000)
    a = _s(tara="AT", categ_venit=2003, dubla_impunere=1, venit_brut=20000, impozit_platit=2000)
    # CF art.72^1 alin.(1): 40% -> net 12.000, impozit 1.200; art.131 alin.(4): creditul „nu poate fi mai mare” decât 1.200
    assert (a["str_chelt_deduc"], a["str_impozit_datorat_Ro"], a["str_credit_fiscal"], a["str_dif_impozit_datorat"]) == \
        (8000, 1200, 1200, 0)


def test_metoda_scutirii_si_acordul_dau_zero():
    for metoda in (2, 4):
        c = _s(tara="FR", categ_venit=2004, dubla_impunere=metoda, venit_brut=30000, impozit_platit=5000)
        # instrucțiuni pct.39.6.8: metoda scutirii / venit scutit prin acord -> „se înscrie cifra zero”
        assert (c["str_chelt_deduc"], c["str_venit_recalculat"], c["str_impozit_datorat_Ro"], c["str_dif_impozit_datorat"]) == \
            (6000, 24000, 0, 0)
        assert "str_credit_fiscal" not in c


def test_fara_conventie_nu_exista_credit():
    c = _s(tara="US", categ_venit=2014, venit_brut=5000, impozit_platit=900)
    # CF art.131 alin.(1): creditul există doar când convenția prevede metoda creditului
    assert (c["str_impozit_datorat_Ro"], c["str_dif_impozit_datorat"]) == (500, 500) and "str_credit_fiscal" not in c


def test_dividendele_cu_cota_anului():
    c = _s(tara="US", categ_venit=2018, dubla_impunere=1, venit_brut=10000, impozit_platit=1500)
    # CF art.97 alin.(7) în forma OUG 156/2024: 10% pe dividendele 2025 (common.cota „impozit_dividend”)
    assert (c["str_impozit_datorat_Ro"], c["str_credit_fiscal"], c["str_dif_impozit_datorat"]) == (1000, 1000, 0)


def test_titluri_compensare_pe_tara():
    c = _s(tara="IT", categ_venit=2012, castig_net=6000, pierdere_precedenta=9000)
    # CF art.119 alin.(4): pierderile din străinătate „în limita a 70% din câștigurile nete anuale de aceeași natură și sursă”
    assert (c["str_pierdere_compensata"], c["str_venit_recalculat"], c["str_impozit_datorat_Ro"]) == (4200, 1800, 180)
    p = _s(tara="IT", categ_venit=2012, castig_net=-500)
    assert (p["str_pierdere_anuala"], p["str_impozit_datorat_Ro"]) == (500, 0)


def test_salarii_pe_venitul_baza_de_calcul():
    c = _s(tara="EL", categ_venit=2016, venit_baza=50000, dubla_impunere=1, impozit_platit=3000)
    # instrucțiuni pct.39.6.3: „venitul bază de calcul ... conform documentului menționat la art. 81 alin.(2)”; CF art.78 alin.(2)
    assert (c["str_venit_net_anual"], c["str_impozit_datorat_Ro"], c["str_dif_impozit_datorat"]) == (50000, 5000, 2000)
    with pytest.raises(ValueError, match="venitul bază de calcul"):
        _s(tara="EL", categ_venit=2016, venit_brut=50000)


def test_lichidare_cu_cota_proprie():
    c = _s(tara="BG", categ_venit=2028, venit_brut=9000, chelt_deduc=4000)
    # CF art.97 alin.(5): 10% (lichidare._cota_lichidare), alt articol decât dividendele
    assert (c["str_venit_net_anual"], c["str_impozit_datorat_Ro"]) == (5000, 500)


def test_refuzuri_de_forma_si_de_temei():
    with pytest.raises(ValueError, match="nomenclatorul ANAF"):
        _s(tara="GR", categ_venit=2014, venit_brut=100)          # Grecia e EL în nomenclatorul validatorului
    with pytest.raises(ValueError, match="nomenclatorul ANAF"):
        _s(tara="RO", categ_venit=2014, venit_brut=100)          # venit din străinătate
    with pytest.raises(ValueError, match="cheltuielile nu se scriu"):
        _s(tara="DE", categ_venit=2017, venit_brut=100, chelt_deduc=10)
    with pytest.raises(ValueError, match="art.118 alin.\\(5\\)"):
        _s(tara="DE", categ_venit=2004, venit_brut=100, pierdere_precedenta=10)
    with pytest.raises(ValueError, match="Legea 239/2025"):
        d212.cap14_sectiune({"tara": "DE", "categ_venit": 2014, "venit_brut": 100}, 2026)


def test_nomenclatorul_de_tari_e_al_validatorului():
    """Lista din d212 = `_nomenclatorTari` din Parameters_v7 (pachetul în vigoare), citită din jar-ul instalat."""
    if not JAR.exists():
        pytest.skip("validatorul D212 nu e instalat")
    clasa = subprocess.run(["unzip", "-p", str(JAR), "d212validator/parameters/Parameters_v7.class"],
                           capture_output=True, check=True).stdout
    coduri = re.findall(rb"\x01\x00\x02([A-Z]{2})", clasa)
    lista = []
    for c in coduri:
        lista.append(c.decode())
        if c == b"XK":
            break
    assert tuple(lista) == d212.TARI_STRAINATATE


def test_categoriile_ecranului_sunt_cele_din_server():
    js = (RAD / "static/js/ecrane/declaratii.js").read_text(encoding="utf-8")
    bloc = js[js.index("const _D212_CATEG_STR = ["):js.index("];", js.index("const _D212_CATEG_STR = ["))]
    assert set(int(c) for c in re.findall(r'\["(\d{4})"', bloc)) == set(d212.CATEG_STRAINATATE)
    harta = js[js.index("const _D212_CAMP_STR = {"):js.index("};", js.index("const _D212_CAMP_STR = {"))]
    lipsa = set(re.findall(r'"(d212-s-[a-z]+)"', harta)) - set(re.findall(r'id="(d212-s-[a-z]+)"', js))
    assert lipsa == set(), "câmpuri din harta categoriilor care nu există pe ecran: %s" % sorted(lipsa)


def test_strainatatea_in_cas_cass_si_sumar():
    S = [_s(tara="DE", categ_venit=2027, dubla_impunere=1, venit_brut=80000, chelt_deduc=20000, impozit_platit=4000),
         _s(tara="AT", categ_venit=2003, venit_brut=20000),
         _s(tara="US", categ_venit=2018, dubla_impunere=1, venit_brut=10000, impozit_platit=1500),
         _s(tara="EL", categ_venit=2016, venit_baza=50000)]
    o, b = d212.oblig_realizat(None, None, 2025, cap14=S)
    # pct.46.3: CAS pe veniturile „din România și din afara României” — 60.000 + 12.000 = 72.000 >= 12 sm
    assert (o["cas_total_ven"], o["cas_datorat"]) == (72000, 12150)
    # CASS 2.1 cu activitatea independentă din străinătate (INTERPRETARE, docstring oblig_realizat) — 60.000 x 10%
    assert (o["cass_total_ven_ai"], o["cass_datorat_ai"]) == (60000, 6000)
    # CASS 2.2 (pct.52.1.4): DPI 12.000 + dividendele nete de impozit 8.500 = 20.500 < 6 sm -> nu se datorează;
    # salariile nu intră în CASS 2.2
    assert "cass_datorat" not in o
    # I.7 rd.1 (pct.56.1): rd.11 din cap14 = 2.000 (DE) + 1.200 (AT, fără credit) + 0 (US) + 5.000 (EL)
    assert o["oblimpoz_real_total"] == 8200


def test_declaratia_cu_strainatate_valida_pe_duk():
    from core import duk
    S = [{"tara": "DE", "categ_venit": 2027, "dubla_impunere": 1, "venit_brut": 80000, "chelt_deduc": 20000, "impozit_platit": 4000},
         {"tara": "FR", "categ_venit": 2004, "dubla_impunere": 2, "venit_brut": 30000, "impozit_platit": 5000},
         {"tara": "IT", "categ_venit": 2012, "castig_net": 6000, "pierdere_precedenta": 9000},
         {"tara": "HU", "categ_venit": 2009, "venit_brut": 5000, "chelt_deduc": 7000}]
    x, r = d212.genereaza(None, None, Perioada(2025), dict(ID, strainatate=S))
    rad = ET.fromstring(x.split("?>", 1)[1])
    assert len(rad.findall("{%s}cap14" % d212.NS)) == 4 and rad.get("bifa121") == "1"
    rez = duk.valideaza(x, "d212", an=2025, luna=12, timeout=180)
    assert rez["stare"] == "valid", rez.get("erori")


def test_asigurat_in_alt_stat_fara_contributii():
    S = [{"tara": "DE", "categ_venit": 2027, "dubla_impunere": 1, "venit_brut": 80000, "chelt_deduc": 20000, "impozit_platit": 4000}]
    x, _ = d212.genereaza(None, None, Perioada(2025), dict(ID, strainatate=S))
    o = ET.fromstring(x.split("?>", 1)[1]).find("{%s}oblig_realizat" % d212.NS).attrib
    assert (o.get("cas_datorat"), o.get("cass_datorat_ai")) == ("12150", "6000")
    S[0]["fara_contributii"] = True
    x, _ = d212.genereaza(None, None, Perioada(2025), dict(ID, strainatate=S))
    o = ET.fromstring(x.split("?>", 1)[1]).find("{%s}oblig_realizat" % d212.NS).attrib
    # instrucțiuni pct.46.3 / 52.1.4: „cu respectarea legislației europene aplicabile în domeniul securității sociale” —
    # asigurat în alt stat -> fără CAS/CASS în România; impozitul rămâne (rd.11 = 2.000)
    assert (o.get("cas_datorat"), o.get("cass_datorat_ai"), o.get("oblimpoz_real_total")) == (None, None, "2000")
