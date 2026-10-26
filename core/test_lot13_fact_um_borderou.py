# -*- coding: utf-8 -*-
"""Lotul 13, zona `fact` — regula UM-ului pe borderoul de achiziție (decizia sesiunii principale, 26.10.2026: „UM gol NU devine «buc» pe
ascuns — se refuză, lângă câmp, cu o propoziție («Alege unitatea de măsură a liniei.») […] articolul nou din borderou […]. Excepție: o
linie cu articol din nomenclator își ia UM-ul articolului.”). Regula unică: `facturi.MESAJ_UM_LIPSA`; borderoul o aplică în
`uc_tenants.achizitie_neinregistrat` (refuzul `op-um`, numai pentru articolul NOU — cel din nomenclator își are UM-ul).

Temei: N/A — regulă de produs (CLAUDE.md §8; DS cap.6 v2.104, 504). Fixtura borderoului (450): schemă efemeră, tranzacție anulată."""
import pytest

from core import erori, facturi
from core.test_lot11_b_450_borderou import _BA, _articole, _borderou, _db_ok, _unu, conn  # noqa: F401 — fixtura și ajutoarele

pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def test_articolul_nou_fara_um_se_refuza_langa_camp_si_nu_se_creeaza(conn):
    """Articolul nou cerut explicit, fără UM -> refuzul `op-um` cu propoziția regulii, nimic scris (înainte: articolul intra în „buc”).
    Cu UM-ul scris -> articolul se creează în unitatea lui. MUTAȚIE: refuzul `op-um` scos din `achizitie_neinregistrat` -> pică."""
    with pytest.raises(erori.DateInvalide) as e:
        _borderou({**_BA, "articol": "Orz", "articol_nou": True, "um": ""})
    assert {x["camp"]: x["mesaj"] for x in e.value.args[0]["erori_campuri"]} == {"op-um": facturi.MESAJ_UM_LIPSA}, e.value.args
    assert _articole(conn) == [] and _unu(conn, "SELECT count(*) FROM facturi")[0] == 0
    _borderou({**_BA, "articol": "Orz", "articol_nou": True, "um": "kg"})
    assert _unu(conn, "SELECT um FROM articole WHERE denumire = 'Orz'")[0] == "kg"


def test_articolul_din_nomenclator_isi_ia_um_ul_lui(conn):
    """Articolul ales din nomenclator, fără UM pe ecran -> UM-ul articolului (nu „buc”, nu refuz)."""
    _borderou({**_BA, "articol": "Grâu", "articol_nou": True, "um": "t"})
    r = _borderou({**_BA, "furnizor_nume": "Ion Vanzator", "furnizor_act": "CJ 654321", "articol": "Grâu", "um": ""})
    assert r["intrare_stoc"]["articol_nou"] is False, r
    assert _unu(conn, "SELECT um FROM factura_linii l JOIN facturi f ON f.id = l.factura_id WHERE f.id = %s", r["factura_id"])[0] == "t"
