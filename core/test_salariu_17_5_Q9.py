"""F080, noiembrie 2026. Două persoane, repartizarea raportată în stat și suma datorată."""
from datetime import date
from decimal import Decimal
from core.salarizare import calcul_salariu
from core.stat_plata_api import _imparte_cam

def test_f080_calcul_si_repartizare_cam():
    ref = date(2026, 11, 1)
    stat = []
    for brut, cas, cass, deducere, impozit, net, cam in (
        (5000, 1250, 500, 562, 269, 2981, "112.50"),
        (7000, 1750, 700, 0, 455, 4095, "157.50"),
    ):
        r = calcul_salariu(brut, la_data=ref)
        assert (r["cas"], r["cass"], r["deducere"]["baza"], r["impozit"], r["net"]) == (cas, cass, deducere, impozit, net)
        assert Decimal(str(r["cam"])) == Decimal(cam)
        stat.append(dict(_bazac=brut, cam=float(r["cam"]), cost=float(r["cost_angajator"])))
    _imparte_cam(stat, ref)
    assert [r["cam"] for r in stat] == [113, 157]
    assert sum(r["cam"] for r in stat) == 270
    assert sum(r["cost"] for r in stat) == 12270
