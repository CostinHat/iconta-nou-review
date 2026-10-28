"""[712, comanda 14.2] Țara partenerului urmează codul fiscal; nepotrivirea oprește emiterea cu motiv."""
import pytest
from core import tara_cod_fiscal as T
from core.facturi_api import FacturaRefuzata
from core.test_lot11_t import conn_t  # noqa: F401 — fixtura schemei sintetice


@pytest.mark.parametrize("cui,tara,ok", [
    ("RO14399840", "RO", True), ("14399840", "RO", True), ("14399840", "IE", True),   # numai cifre: fără verdict
    ("RO14399840", "IE", False), ("ro 14399840", "DE", False),
    ("DE123456789", "DE", True), ("DE123456789", "RO", False), ("EL123456789", "EL", True), ("IE6388047V", "IE", True),
    ("IE6388047V", "RO", False), ("US12345", "RO", True),                               # stat în afara Uniunii: fără verdict
])
def test_tara_urmeaza_codul(cui, tara, ok):
    assert (T.nepotrivire(cui, tara) is None) is ok, (cui, tara, T.nepotrivire(cui, tara))


def test_motivul_numeste_codul_si_tara():
    m = T.nepotrivire("RO14399840", "IE")
    assert "IE" in m and "RO14399840" in m and "țării RO" in m and "Alege țara RO" in m, m


def test_emiterea_se_opreste_cu_motiv_pe_campul_tarii(conn_t):
    """Drumul real al emiterii, pe o schemă sintetică în rollback: refuz pe câmpul țării și nicio factură scrisă. MUTAȚIE: verificarea scoasă din
    `facturi_api.emite_factura` -> factura se emite -> ROȘU."""
    from core import facturi_api as F
    linii = [{"descriere": "Servicii", "cantitate": 1, "pret_unitar": "100", "cota_tva": 21}]
    with conn_t.cursor() as cur:
        cur.execute("UPDATE firma_profil SET serie_factura = 'ZT'")
    with pytest.raises(FacturaRefuzata) as e:
        F.emite_factura(conn_t, linii, tert_nume="DANTE INTERNATIONAL", tert_cui="RO14399840", tert_tara="IE",
                        data_emitere="2026-10-10", moneda="RON", platitor_tva=True, tip="factura")
    assert any(c["camp"] == "tert_tara" and "RO14399840" in c["mesaj"] for c in e.value.erori_campuri), e.value.erori_campuri
    with conn_t.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi")
        assert cur.fetchone()[0] == 0
