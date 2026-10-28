"""[527.1, comanda 14.2] Preluarea: soldul de pe 117 (rezultat reportat) fără analitic se pune pe analiticul ales (1171 / 1172 / 1174)."""
import pytest
from core import solduri_api as S
from core.test_lot11_t import conn_t  # noqa: F401 — fixtura schemei sintetice

B = [{"cont": "5121", "denumire": "Conturi la bănci", "debit": 14000.0, "credit": 0.0},
     {"cont": "117", "denumire": "Rezultatul reportat", "debit": 0.0, "credit": 14000.0}]


def test_cere_analitic_numai_cu_sold_pe_117_fara_analitic():
    assert S.cere_analitic_117(B) is True
    assert S.cere_analitic_117([B[0], dict(B[1], cont="1171")]) is False, "fișierul spune deja analiticul"
    assert S.cere_analitic_117([B[0], dict(B[1], debit=0, credit=0)]) is False, "fără sold nu e nimic de preluat"
    assert S.cere_analitic_117([B[0], {"cont": "121", "debit": 0, "credit": 14000.0}]) is False


def test_muta_pe_analiticul_ales_si_refuza_orice_altceva():
    for a in ("1171", "1172", "1174"):
        m = S.muta_pe_analitic_117(B, a)
        assert [r["cont"] for r in m] == ["5121", a] and m[1]["credit"] == 14000.0
    with pytest.raises(ValueError):
        S.muta_pe_analitic_117(B, "117")
    with pytest.raises(ValueError):
        S.muta_pe_analitic_117(B, None)


def test_importul_scrie_soldul_pe_analitic(conn_t):
    S.importa(conn_t, S.muta_pe_analitic_117(B, "1171"), data_referinta="2026-08-31")
    with conn_t.cursor() as cur:
        cur.execute("SELECT cont, sold_creditor FROM solduri_initiale WHERE sold_creditor > 0")
        assert [(c, float(s)) for c, s in cur.fetchall()] == [("1171", 14000.0)]
