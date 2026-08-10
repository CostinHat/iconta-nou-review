# -*- coding: utf-8 -*-
"""Teste gardian pentru D710 (Declaratie rectificativa - corectie D100).

Structura si regulile au fost extrase din D710Validator.jar (parameters v10,
versiuni.xml D710_56) si verificate/corectate iterativ pe validatorul oficial DUK
(20.07.2026). Fiecare test apara o regula dovedita pe validator - vezi core/d710.py.

Esenta: fiecare suma are pereche Initial (_I) / Corectat (_C). Motorul acopera
rectificarea sumei DATORATE (suma_plata = suma_dat); deducerile/reducerile (model 8#)
sunt LIMITA documentata, la caz real.
"""
import pytest
from core.d710 import calcul_d710 as _calcul_d710_real, build_xml, NS, _scadenta_d710
from core.common import Perioada as _Per710


def calcul_d710(prof, an, luna, obligatii):
    """Shim de test vizibil: apel vechi (an,luna,obligatii) -> contract calcul_d710(prof, perioada,
    date, manual). Modulul are contractul curat."""
    return _calcul_d710_real(prof, _Per710(an, luna=luna), {}, {"obligatii": obligatii})
from core.d100 import COD_BUGETAR
import core.duk as duk


def _prof():
    return {"cui": "456789123", "nume": "TEST RECTIFICATIVA SRL",
            "adresa": "Str. Test nr.1 Bucuresti Sector 1"}


def _obl(cod="121", i=100, c=150, cota="1"):
    return [{"cod_oblig": cod, "suma_dat_i": i, "suma_dat_c": c, "cota": cota}]


# ---- structura / calcul (pur, fara java) ----

def test_namespace_e_d710_nu_d100():
    """Namespace propriu - NU se reutilizeaza structura D100 (verificat la sursa)."""
    assert NS == "mfp:anaf:dgti:d710:declaratie:v2"
    xml = build_xml(calcul_d710(_prof(), 2025, 3, _obl()))
    assert "declaratie710" in xml and NS in xml
    assert "declaratie100" not in xml


def test_suma_plata_egala_suma_dat_pe_ambele_laturi():
    """Rectificare suma datorata: suma_plata = suma_dat (initial si corectat)."""
    o = calcul_d710(_prof(), 2025, 3, _obl(i=100, c=150)).obligatii[0]
    assert o.suma_plata_i == o.suma_dat_i == 100
    assert o.suma_plata_c == o.suma_dat_c == 150


def test_xml_are_perechea_initial_corectat():
    xml = build_xml(calcul_d710(_prof(), 2025, 3, _obl(i=100, c=150)))
    lin = [l for l in xml.split("\n") if "<obligatie" in l][0]
    assert 'suma_dat_I="100"' in lin and 'suma_dat_C="150"' in lin
    assert 'suma_plata_I="100"' in lin and 'suma_plata_C="150"' in lin


def test_totalPlata_A_suma_dat_plus_plata_ambele_laturi():
    """DUK regula R11b: totalPlata_A = dat_I + plata_I + dat_C + plata_C = 100+100+150+150 = 500."""
    res = calcul_d710(_prof(), 2025, 3, _obl(i=100, c=150))
    assert res.total_plata_a == 500
    assert 'totalPlata_A="500"' in build_xml(res)


def test_d_recN_doar_de_la_perioada_12_2025():
    """d_recN apare DOAR de la perioada de raportare 12.2025 (regula validator);
    pentru perioade anterioare NU se pune (validatorul il respinge)."""
    xml_vechi = build_xml(calcul_d710(_prof(), 2025, 3, _obl()))   # 03.2025
    assert "d_recN" not in xml_vechi
    xml_nou = build_xml(calcul_d710(_prof(), 2025, 12, _obl()))    # 12.2025
    assert 'd_recN="1"' in xml_nou
    xml_2026 = build_xml(calcul_d710(_prof(), 2026, 3, _obl()))    # 03.2026
    assert 'd_recN="1"' in xml_2026


def test_scadenta_micro_trim4_e_25_iunie_an_urmator():
    """Cod 121 (micro) trim4 (luna 12): scadenta 25.06 an urmator, nu 25.01 (DUK regula R15)."""
    assert _scadenta_d710("121", 2025, 12) == (25, 6, 2026)
    # celelalte trimestre: 25 a lunii urmatoare
    assert _scadenta_d710("121", 2025, 3) == (25, 4, 2025)
    assert _scadenta_d710("103", 2025, 12) == (25, 1, 2026)


def test_cota_doar_la_cod_121():
    xm = build_xml(calcul_d710(_prof(), 2025, 3, _obl(cod="121", cota="1")))
    assert 'cota="1"' in [l for l in xm.split("\n") if "<obligatie" in l][0]
    xp = build_xml(calcul_d710(_prof(), 2025, 6, [{"cod_oblig": "103", "suma_dat_i": 500, "suma_dat_c": 400}]))
    assert 'cota=' not in [l for l in xp.split("\n") if "<obligatie" in l][0]


def test_cod_bugetar_din_nomenclator():
    o = calcul_d710(_prof(), 2025, 3, _obl(cod="121")).obligatii[0]
    assert o.cod_bugetar == COD_BUGETAR["121"] == "5503XXXXXX"


def test_nr_evid_23_caractere_poz_3_5_cod_oblig():
    o = calcul_d710(_prof(), 2025, 3, _obl(cod="121")).obligatii[0]
    assert len(o.nr_evid) == 23 and o.nr_evid.isdigit()
    assert o.nr_evid[2:5] == "121"


def test_luna_invalida_respinsa():
    with pytest.raises(ValueError):
        calcul_d710(_prof(), 2025, 5, _obl())


def test_obligatie_ambele_zero_nu_intra():
    res = calcul_d710(_prof(), 2025, 3, [{"cod_oblig": "121", "suma_dat_i": 0, "suma_dat_c": 0, "cota": "1"}])
    assert res.obligatii == []


# ---- validare pe DUK (judecatorul final ANAF) - gated ----
_DUK = duk.poate_valida("d710")


@pytest.mark.skipif(not _DUK, reason="validatorul D710 nu e instalat in pachetul DUK")
@pytest.mark.parametrize("an,luna,obl", [
    (2025, 3,  _obl(cod="121", i=100, c=150)),            # micro simplu
    (2025, 12, _obl(cod="121", i=100, c=150)),            # micro trim4 (scadenta speciala + d_recN)
    (2026, 3,  _obl(cod="121", i=100, c=150)),            # micro cu d_recN
    (2025, 6,  [{"cod_oblig": "103", "suma_dat_i": 1000, "suma_dat_c": 1600}]),  # profit
    (2025, 6,  _obl(cod="121", i=150, c=100)),            # corectie in scadere
])
def test_valid_pe_duk_fara_erori(an, luna, obl):
    xml = build_xml(calcul_d710(_prof(), an, luna, obl))
    r = duk.valideaza(xml, "d710")
    assert r["stare"] == "valid", "DUK a gasit erori: %s" % r["erori"]


@pytest.mark.skipif(not _DUK, reason="validatorul D710 nu e instalat in pachetul DUK")
def test_duk_respinge_gunoi():
    """Un validator care nu poate spune NU nu e validator."""
    gunoi = '<?xml version="1.0"?><aiurea xmlns="mfp:anaf:dgti:inventat:v99" x="1"/>'
    assert duk.valideaza(gunoi, "d710")["stare"] != "valid"


def test_structura_cota_bidirectional_gard():
    """Cluster structura declaratie710: atributul `cota` pe <obligatie> respecta regula STRUCTURALA a
    validatorului D710 - OBLIGATORIU si NUMAI pentru cod_oblig 121 (micro). Dovedit pe DUK (04.08.2026):
    cod 121 FARA cota -> respins 'R17: cota (lipsa) - Cota impozitare eronata'; cota pe cod != 121 ->
    respins 'R17: cota nu se completeaza'. Valoarea = rata micro (1 sau 3 acceptate de DUK, 16 respinsa
    'nu se incadreaza in intervalul cerut') - period-aware, o range-checkuieste validatorul; aici pazim
    regula STRUCTURALA (prezenta/absenta), invizibila pana la DUK. Gard bidirectional ca la d100 - d710 il
    lipsea, putea genera XML respins in ambele directii."""
    import pytest
    from core.d710 import calcul_d710 as _c, build_xml
    from core.common import Perioada
    prof = {"cui": "456789123", "nume": "TEST SRL", "adresa": "Str Test 1 Bucuresti"}
    def mk(obl, luna=3):
        return build_xml(_c(prof, Perioada(2025, luna=luna), {}, {"obligatii": obl}))

    # 121 CU cota -> emisa
    x = mk([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"}])
    assert 'cota="1"' in x
    # 121 rata 3 (micro 3%) -> emisa (nu hardcodam "1")
    x3 = mk([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "3"}])
    assert 'cota="3"' in x3
    # 121 FARA cota -> ValueError (nu XML respins de DUK)
    with pytest.raises(ValueError):
        mk([{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150}])
    # cod != 121 CU cota -> ValueError
    with pytest.raises(ValueError):
        mk([{"cod_oblig": "103", "suma_dat_i": 500, "suma_dat_c": 400, "cota": "1"}], luna=6)
    # cod != 121 FARA cota -> OK, fara atribut cota
    xp = mk([{"cod_oblig": "103", "suma_dat_i": 500, "suma_dat_c": 400}], luna=6)
    assert "cota=" not in [l for l in xp.split("\n") if "<obligatie" in l][0]


def test_cod_bugetar_nomenclator_duk_si_antidrop():
    """Cluster nomenclator COD_BUGETAR | d710. cod_bugetar per cod_oblig, SURSA UNICA d100.COD_BUGETAR
    (cluster d100 verificat 03.08). Codurile dominante 121/103 -> 5503XXXXXX. Confirmat pe DUK 04.08.2026
    (DUK regula R14a): validatorul D710 accepta 5503XXXXXX pentru 121 SI 103; mesajul la valoare gresita releva
    inca vechiul cont 20470101 (validator tolerant/invechit in text) DAR 5503XXXXXX (forma curenta, cont unic
    5503 din 26.07.2018) e VALID - codul emite forma curenta. Gard anti-drop (ca la d100): un cod_oblig fara
    cod_bugetar (nu-i in nomenclator, fara valoare manuala) -> ValueError, nu XML tacit incomplet respins de
    DUK. DATORIE: coduri D710 valide dar nemapate (130/131/132) sunt in afara LIMITEI motorului (cer data_I /
    modele suma diferite)."""
    import pytest
    from core.d710 import calcul_d710 as _c, build_xml
    from core.d100 import COD_BUGETAR
    from core.common import Perioada
    import core.duk as duk
    prof = {"cui": "456789123", "nume": "TEST SRL", "adresa": "Str Test 1 Bucuresti"}

    # sursa unica + valorile dominante
    assert COD_BUGETAR["121"] == COD_BUGETAR["103"] == "5503XXXXXX"

    # anti-drop: cod nemapat FARA cod_bugetar manual -> ValueError (nu XML tacit incomplet)
    with pytest.raises(ValueError):
        _c(prof, Perioada(2025, luna=3), {}, {"obligatii": [{"cod_oblig": "999", "suma_dat_i": 100, "suma_dat_c": 150}]})
    # TURA 3 (C2/C3, FIXTURA REPARATA): un cod_oblig necunoscut e RESPINS pe nomenclator (COD_BUGETAR) chiar
    # CU un cod_bugetar manual. Vechea "extindere controlata" lasa un cod garbage sa ocoleasca gardul (emis
    # tacit -> DUK 'cod_oblig nu se afla in lista'). Nomenclatorul e acum poarta unica; extinderea legitima =
    # adaugare in COD_BUGETAR, nu ocolire prin cod_bugetar manual.
    with pytest.raises(ValueError):
        _c(prof, Perioada(2025, luna=3), {}, {"obligatii": [{"cod_oblig": "999", "suma_dat_i": 100, "suma_dat_c": 150, "cod_bugetar": "5503XXXXXX"}]})

    # TURA 3 (D4, FIXTURA REPARATA): un cod_bugetar MANUAL divergent de nomenclator e prins PRE-DUK cu motiv
    # (DUK regula R14a), nu mai ajunge la validator. (Inainte se emitea XML si DUK il respingea cu R14a.)
    with pytest.raises(ValueError):
        _c(prof, Perioada(2025, luna=3), {}, {"obligatii": [{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1", "cod_bugetar": "9999999999"}]})

    # DUK-backed (gated): nomenclatorul (cod_bugetar corect din COD_BUGETAR) e acceptat de validator - dinti
    if duk.poate_valida("d710"):
        for cod, cota, luna in [("121", "1", 3), ("103", "", 6)]:
            o = {"cod_oblig": cod, "suma_dat_i": 100, "suma_dat_c": 150}
            if cota:
                o["cota"] = cota
            good = duk.valideaza(build_xml(_c(prof, Perioada(2025, luna=luna), {}, {"obligatii": [o]})), "d710")
            assert good["stare"] == "valid", "DUK: nomenclator %s respins: %s" % (cod, good["erori"])


def test_checksum_r11b_multi_obligatie_si_duk():
    """Cluster checksum R11b | d710. totalPlata_A = suma de control ceruta de validator (DUK regula R11b):
    SUMA pe TOATE obligatiile a (suma_dat_I + suma_plata_I + suma_dat_C + suma_plata_C). Cum suma_plata =
    suma_dat pe fiecare latura (rectificare a sumei datorate), rezulta 2*(dat_I + dat_C) pe obligatie.
    Confirmat pe DUK 04.08.2026: multi-obligatie 121(100->150)+103(200->300) -> totalPlata_A=1500 VALID;
    o valoare gresita -> respins 'R11b: Suma de control totalPlata_A(X) = ... calculata cf. regulii(1500)'.
    Sursa unica: build_xml emite res.total_plata_a direct (clasa d100/d394)."""
    from core.d710 import calcul_d710 as _c, build_xml
    from core.common import Perioada
    import core.duk as duk
    import re
    prof = {"cui": "456789123", "nume": "TEST SRL", "adresa": "Str Test 1 Bucuresti"}
    obl = [{"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"},
           {"cod_oblig": "103", "suma_dat_i": 200, "suma_dat_c": 300}]
    res = _c(prof, Perioada(2025, luna=6), {}, {"obligatii": obl})

    # checksum peste TOATE obligatiile: 2*(100+150) + 2*(200+300) = 500 + 1000 = 1500
    assert res.total_plata_a == 1500
    xml = build_xml(res)
    # sursa unica: valoarea emisa == res.total_plata_a
    emis = int(re.search(r'totalPlata_A="(\d+)"', xml).group(1))
    assert emis == res.total_plata_a == 1500

    # DUK-backed (gated): corect valid, gresit respins R11b (dinti)
    if duk.poate_valida("d710"):
        assert duk.valideaza(xml, "d710")["stare"] == "valid", "R11b corect ar trebui valid"
        xbad = re.sub(r'totalPlata_A="\d+"', 'totalPlata_A="9999"', xml)
        bad = duk.valideaza(xbad, "d710")
        assert bad["stare"] != "valid" and "R11b" in bad["erori"], "totalPlata_A gresit ar trebui respins R11b"


def test_r15_termen_definitivare_micro_trim4_duk():
    """Cluster R15 termen definitivare | d710. Cod 121 (micro), trimestrul 4 (luna 12): scadenta = 25.06
    an urmator = termenul de DEFINITIVARE, NU 25.01. Confirmat pe DUK 04.08.2026 (DUK regula R15): pentru
    cod_oblig=121 luna=12, o scadenta gresita e respinsa cu EROARE 'R15: scadenta (X) ar fi trebuit sa fie
    25.06.2026' (valoare UNICA, eroare - nu avertisment). Celelalte trimestre 121: 25 a lunii urmatoare.
    (Contrast cod 103 profit trim4: 25.01 sau 25.12, doar avertisment.)"""
    from core.d710 import _scadenta_d710, calcul_d710 as _c, build_xml
    from core.common import Perioada
    import core.duk as duk

    # unit: cod 121 trim4 -> 25.06 an+1 (stabil pe an); alt trimestru -> 25 luna urmatoare
    assert _scadenta_d710("121", 2025, 12) == (25, 6, 2026)
    assert _scadenta_d710("121", 2026, 12) == (25, 6, 2027)
    assert _scadenta_d710("121", 2025, 3) == (25, 4, 2025)

    # DUK-backed: scadenta calculata (25.06.2026) valida; una gresita -> R15 cu 25.06.2026 revelat (dinti)
    if duk.poate_valida("d710"):
        prof = {"cui": "456789123", "nume": "TEST SRL", "adresa": "Str Test 1 Bucuresti"}
        def mk(scad=None):
            o = {"cod_oblig": "121", "suma_dat_i": 100, "suma_dat_c": 150, "cota": "1"}
            if scad:
                o["scadenta"] = scad
            return build_xml(_c(prof, Perioada(2025, luna=12), {}, {"obligatii": [o]}))
        assert duk.valideaza(mk(), "d710")["stare"] == "valid", "scadenta definitivare calculata ar trebui valida"
        bad = duk.valideaza(mk("25.01.2026"), "d710")
        assert bad["stare"] != "valid" and "R15" in bad["erori"] and "25.06.2026" in bad["erori"], \
            "R15 ar trebui sa ceara 25.06.2026 pt cod 121 trim4"


def test_scadente_nr_evid_urmeaza_scadenta_emisa():
    """Cluster scadente | d710. Scadenta calculata: 25 a lunii urmatoare (standard) + exceptia micro trim4
    (cod 121 luna 12 -> 25.06 an urmator, cluster R15). Confirmat pe DUK 04.08.2026 (DUK regula R15): cod 121
    toate trimestrele (25.04/25.07/25.10 + 25.06 trim4, EROARE strict), cod 103 (25.01 sau 25.12 trim4,
    avertisment). NECONFORMITATE reparata (footgun pe override): nr_evid EMBEDA scadenta (poz.12-17) si
    DUK regula R16 o verifica fata de atributul scadenta. Codul folosea scadenta CALCULATA pentru nr_evid chiar
    cand atributul scadenta era override manual -> mismatch. Dovedit pe DUK 04.08: cod 103 trim4 cu scadenta
    alternativa VALIDA (25.12.2025, acceptata de R15) primea nr_evid pe 25.01 -> respins DUK regula R16
    'nr_evid - scadenta platii eronata'. REPARAT: nr_evid derivat din ACEEASI data ca scadenta emisa."""
    import pytest
    from core.d710 import _scadenta_d710, calcul_d710 as _c, build_xml
    from core.common import Perioada
    import core.duk as duk

    # unit: standard = 25 a lunii urmatoare
    assert _scadenta_d710("103", 2025, 3) == (25, 4, 2025)
    assert _scadenta_d710("103", 2025, 12) == (25, 1, 2026)

    prof = {"cui": "456789123", "nume": "TEST SRL", "adresa": "Str Test 1 Bucuresti"}

    # nr_evid URMEAZA scadenta emisa: cu override, poz.12-17 (index 11:17) = ZZLLAA al scadentei override
    o = {"cod_oblig": "103", "suma_dat_i": 500, "suma_dat_c": 400, "scadenta": "25.12.2025"}
    ob = _c(prof, Perioada(2025, luna=12), {}, {"obligatii": [o]}).obligatii[0]
    assert ob.scadenta == "25.12.2025"
    assert ob.nr_evid[11:17] == "251225", "nr_evid nu urmeaza scadenta override: %s (poz12-17=%s)" % (ob.nr_evid, ob.nr_evid[11:17])

    # fara override, nr_evid urmeaza scadenta calculata
    ob2 = _c(prof, Perioada(2025, luna=12), {}, {"obligatii": [{"cod_oblig": "103", "suma_dat_i": 500, "suma_dat_c": 400}]}).obligatii[0]
    assert ob2.scadenta == "25.01.2026" and ob2.nr_evid[11:17] == "250126"

    # scadenta override in format gresit -> ValueError (nu XML tacit stricat)
    with pytest.raises(ValueError):
        _c(prof, Perioada(2025, luna=12), {}, {"obligatii": [{"cod_oblig": "103", "suma_dat_i": 500, "suma_dat_c": 400, "scadenta": "2025-12-25"}]})

    # DUK-backed: scadenta alternativa valida (25.12.2025) NU mai da R16 (nr_evid consistent)
    if duk.poate_valida("d710"):
        r = duk.valideaza(build_xml(_c(prof, Perioada(2025, luna=12), {}, {"obligatii": [o]})), "d710")
        assert "R16" not in r["erori"], "nr_evid inca inconsistent cu scadenta override (R16): %s" % r["erori"]
