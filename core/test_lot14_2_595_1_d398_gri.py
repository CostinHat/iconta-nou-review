"""[595.1, comanda 14.2] „Cod de TVA” al formularului D398 vine numai de la o firmă care are cod de TVA românesc; generarea D398 refuză fără „Da” la OSS.
[D2, comanda 14.3] D398 gri / de lămurit / ascunsă pe răspunsul OSS: `core/test_lot14_3_d2_oss.py`."""
import pytest
from core.erori import RefuzGenerare
from core import declaratii_api as DA, uc_declaratii as UD
from core.test_lot11_t import conn_t, _SCHEMA as _SCHEMA_PENTRU_TEST  # noqa: F401 — fixtura schemei sintetice


def test_codul_de_tva_se_precompleteaza_numai_cu_cod_romanesc():
    assert UD._cod_tva_firma({"cui": "404000013", "platitor_tva": False, "inreg_art317": False}) is None, "F3: fără cod de TVA"
    assert UD._cod_tva_firma({"cui": "404000013", "platitor_tva": True, "inreg_art317": False}) == "RO404000013"
    assert UD._cod_tva_firma({"cui": "RO404000013", "platitor_tva": False, "inreg_art317": True}) == "RO404000013"
    assert UD._cod_tva_firma({"cui": None, "platitor_tva": True}) is None


def test_generarea_d398_refuza_fara_oss_da(conn_t):
    """Apărarea de rezervă: și dacă formularul ajunge la server (fila veche, cerere directă), generarea refuză fără „Da” la OSS. MUTAȚIE:
    `refuz_oss` scos din `_d398` -> nu mai refuză -> ROȘU."""
    for oss, text in ((None, "nu ai răspuns"), (False, "nu e înregistrată")):
        with conn_t.cursor() as cur:
            cur.execute("UPDATE firma_profil SET inregistrat_oss = %s", (oss,))
        with pytest.raises(RefuzGenerare) as e:
            DA._d398(conn_t, _SCHEMA_PENTRU_TEST, {"an": 2026, "luna": 9, "manual": {}})
        assert text in str(e.value), e.value
