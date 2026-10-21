# -*- coding: utf-8 -*-
"""[lotul 10, C71 — găsită de Code (subagentul P) la C69] „Profil incomplet” cerea câmpuri pentru declarații pe care forma firmei nu le
datorează: la PFA (partidă simplă) „Mare contribuabil” / „Forma de proprietate” (noi la C69) blocau „Bilanț”, CAEN / IBAN blocau D101 /
D406, iar după „Salvează” mesajul spunea „Salvat. Lipsesc …”. `lipsuri()` nu citea forma; acum folosește sursa unică a excluderii prin
formă, `control_fiscal_api.neaplicabile_forma` (căreia i s-a adăugat bilanțul, Legea 82/1991 art.28 alin.(1)).
MUTAȚIE: filtrul `neap` scos din `firma_profil_api.lipsuri` -> `test_pfa_nu_are_lipsuri_pentru_declaratiile_persoanei_juridice` pică.
"""
from core import control_fiscal_api as cf
from core import firma_profil_api as fp


def _decl(lips):
    return {d for x in lips for d in x["declaratii"]}


def test_pfa_nu_are_lipsuri_pentru_declaratiile_persoanei_juridice():
    lips = fp.lipsuri({"tip_firma": "pfa"})
    campuri = {x["camp"] for x in lips}
    # Legea 82/1991 art.28 alin.(1): „Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să întocmească situații financiare anuale.”
    assert "mare_contribuabil" not in campuri and "forma_proprietate" not in campuri, lips
    assert not {d for d in _decl(lips) if d.startswith("Bilanț")}, lips
    # D101 / D406: persoane juridice (CF — impozitul pe profit; OPANAF 407/2025 Anexa 5 pct.4 lit.a)–d) exclude PFA de la SAF-T)
    assert not _decl(lips) & {"D101", "D406", "D100"}, lips
    assert _decl(lips) & {"D112", "D300"}, lips                      # anti-vacuu: ce datorează PFA rămâne cerut


def test_srl_pastreaza_lipsurile_bilantului():
    lips = fp.lipsuri({"tip_firma": "srl"})
    campuri = {x["camp"]: x["declaratii"] for x in lips}
    assert campuri["mare_contribuabil"] == ["Bilanț"] and campuri["forma_proprietate"] == ["Bilanț"], campuri
    assert {"D101", "D406"} <= _decl(lips)


def test_bilantul_e_in_sursa_unica_a_excluderii_prin_forma():
    # Legea 82/1991 art.28 alin.(1): „Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să întocmească situații financiare anuale.”
    assert set(cf.neaplicabile_forma("pfa")) >= {"bilant"}           # PFA (partidă simplă) e la art.1 alin.(5)
    assert not set(cf.neaplicabile_forma("srl")) & {"bilant"}         # SRL e la art.1 alin.(1)
