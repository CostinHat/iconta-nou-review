"""[723, comanda 15.0] Rezumatele firmelor se recalculează și din aplicație, iar cronul nu scrie epoca altui cod peste cea a procesului viu."""
import pytest

from core import db, firma_rezumat as FR


@pytest.fixture()
def conn_rollback():
    with db.get_conn() as c:
        yield c
        c.rollback()


def test_codul_viu_se_inregistreaza_si_se_citeste(conn_rollback):
    FR.aplica_ddl(conn_rollback)
    FR.inregistreaza_cod_viu(conn_rollback)
    assert FR.cod_viu(conn_rollback) == FR.COD
    with conn_rollback.cursor() as cur:
        cur.execute("UPDATE public.cod_aplicatie_viu SET cod = 'alt-cod'")
    assert FR.cod_viu(conn_rollback) == "alt-cod"


def test_cronul_sare_cand_discul_difera_de_procesul_viu(monkeypatch, capsys):
    """Discul cu alt cod decât procesul viu: cronul nu recalculează (altfel ar rescrie epoca și cardurile ar rămâne „în recalculare”)."""
    monkeypatch.setattr(FR, "cod_viu", lambda c: "alt-cod")
    apelat = []
    monkeypatch.setattr(FR, "recalculeaza_lot", lambda **k: apelat.append(1) or {})
    assert FR.main() == 0
    assert apelat == [] and "nu recalculez" in capsys.readouterr().out


def test_lucratorul_aplicatiei_nu_porneste_in_suita():
    """În suită firele de fundal sunt oprite (`ICONTA_FIRE_FUNDAL=0`), deci testele nu primesc un fir neașteptat."""
    assert FR.porneste_lucratorul_aplicatiei() is False
