"""[D2, comanda 14.3] D398 și răspunsul OSS: „Nu” -> ascunsă; nedeclarat -> „de lămurit” (activă, cu trimitere); „Da” -> nimic special."""
from core import declaratii_api as DA


def test_starea_oss_din_vector():
    assert DA.starea_oss({"inregistrat_oss": False}) == "ascunsa"
    assert DA.starea_oss({"inregistrat_oss": None}) == "de_lamurit"
    assert DA.starea_oss({"inregistrat_oss": True}) is None
    assert DA.starea_oss({}) is None, "vector fără cheia OSS (alți apelanți): neatins"
    assert DA.starea_oss(None) is None


def test_d398_nu_mai_e_gri_pe_raspunsul_oss():
    for oss in (False, None, True):
        assert "d398" not in DA.neaplicabile_regim({"platitor_tva": True, "inreg_art317": False, "inregistrat_oss": oss}), oss
    assert DA.neaplicabile_regim({"platitor_tva": False, "inreg_art317": False, "inregistrat_oss": True})["d398"] == DA.NEAPLICABILE_REGIM["d398"]
