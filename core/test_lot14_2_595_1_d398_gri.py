"""[595.1, comanda 14.2] D398 gri la pasul 1 când firma a răspuns „nu” la înregistrarea OSS; „Cod de TVA” al formularului vine numai de la o
firmă care are cod de TVA românesc."""
from core import declaratii_api as DA, d398, uc_declaratii as UD


def test_d398_gri_cu_motiv_cand_oss_e_nu():
    n = DA.neaplicabile_regim({"platitor_tva": True, "inreg_art317": False, "inregistrat_oss": False})
    assert n["d398"] == d398.MOTIV_OSS_NU, n


def test_d398_nu_e_gri_cand_oss_e_da_sau_nedeclarat():
    for oss in (True, None):
        assert "d398" not in DA.neaplicabile_regim({"platitor_tva": True, "inreg_art317": False, "inregistrat_oss": oss}), oss


def test_d398_gri_si_fara_cod_romanesc_ca_inainte():
    n = DA.neaplicabile_regim({"platitor_tva": False, "inreg_art317": False, "inregistrat_oss": True})
    assert n["d398"] == DA.NEAPLICABILE_REGIM["d398"], n


def test_codul_de_tva_se_precompleteaza_numai_cu_cod_romanesc():
    assert UD._cod_tva_firma({"cui": "404000013", "platitor_tva": False, "inreg_art317": False}) is None, "F3: fără cod de TVA"
    assert UD._cod_tva_firma({"cui": "404000013", "platitor_tva": True, "inreg_art317": False}) == "RO404000013"
    assert UD._cod_tva_firma({"cui": "RO404000013", "platitor_tva": False, "inreg_art317": True}) == "RO404000013"
    assert UD._cod_tva_firma({"cui": None, "platitor_tva": True}) is None
