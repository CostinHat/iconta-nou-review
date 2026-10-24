# -*- coding: utf-8 -*-
"""[lotul 12, C116, găsită de pachetul `prod`] „Reevaluează” din rândul registrului mijloacelor fixe trimite numai valoarea justă, iar
`uc_tenants.reevaluare_imobilizare` lua `sold_105_activ = 0` și `pierdere_655_anterioara = 0`: la a doua reevaluare a unui activ cu surplus
în 105, descreșterea mergea toată pe 655, iar creșterea de după o descreștere trecută pe 655 mergea toată pe 105.

TEMEI (anaf_surse/omfp_1802_2014_reglementari_consolidat.txt), OMFP 1802/2014 pct.111:
  alin.(1) creșterea se tratează „ca o creștere a rezervei din reevaluare […], dacă nu a existat o descreștere anterioară recunoscută ca o
  cheltuială aferentă acelui activ; sau ca un venit care să compenseze cheltuiala cu descreșterea recunoscută anterior la acel activ”;
  alin.(2) descreșterea se tratează „ca o scădere a rezervei din reevaluare […], cu minimul dintre valoarea acelei rezerve și valoarea
  descreșterii, iar eventuala diferență rămasă neacoperită se înregistrează ca o cheltuială”;
  alin.(3) conturile 755 / 655.

Reparația: când cererea nu le dă, serverul calculează rezerva (105) și pierderea necompensată (655 − 755) ale ACTIVULUI din notele
reevaluărilor lui aplicate (`repo_reevaluari.rezerva_si_pierderea`).

Scenariul (cifrele se refac cu creionul): activ 3.000 lei, 60 de luni, liniar, PIF 05.03.2026 (amortizarea începe în aprilie, deci la
reevaluările din martie amortizarea cumulată e 0 și valoarea netă = valoarea brută):
  1) 20.03 justă 3.500: +500 -> 2131 = 105 500                         (rezerva 500)
  2) 31.03 justă 3.200: −300 -> 105 = 2131 300 (min(500, 300))           (rezerva 200)   ÎNAINTE: 655 = 2131 300
  3) 31.03 justă 2.700: −500 -> 105 = 2131 200 + 655 = 2131 300          (rezerva 0, pierdere 300)
  4) 31.03 justă 3.000: +300 -> 2131 = 755 300 (compensează pierderea)   ÎNAINTE: 2131 = 105 300
Schemă efemeră din `tenant_template.sql`, tranzacție anulată (fără commit), date în 2026 pe o schemă sintetică."""
import contextlib
import json
import os
from decimal import Decimal

import pytest

from core import db as _db

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "ztest_lot12_c116"


class _FaraCommit:
    """Conexiunea testului, fără commit: use-case-ul comite la final, iar proba rămâne în tranzacția anulată."""

    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, k):
        return getattr(self._c, k)


@pytest.fixture
def uc(monkeypatch):
    try:
        _db.init_pool()
    except Exception:
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp, uc_tenants, uc_comun
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, "
                            "data_pif, metoda, activ) VALUES ('MF-C116', 'Utilaj C116', '2131', '2813', 3000, 0, 60, '2026-03-05', "
                            "'liniara', true) RETURNING id")
                mid = cur.fetchone()[0]
            fc = _FaraCommit(c)

            @contextlib.contextmanager
            def _gc(schema=None):
                yield fc
            monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
            monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda conn, schema, data: None)

            def reev(data, justa, **extra):
                r = uc_tenants.reevaluare_imobilizare(1, dict({"operatie": "reevaluare", "mijloc_fix_id": mid, "data": data,
                                                               "valoare_justa": justa}, **extra), {"uid": 1})
                d = json.loads(r.body) if hasattr(r, "body") else r
                # validarea notei (R59): reevaluarea se aplică pe registru (`_aplica_reevaluarea`, drumul lui `jurnal_valideaza`)
                with c.cursor() as cur:
                    cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (d["inregistrare_id"],))
                assert uc_tenants._aplica_reevaluarea(c, SCH, d["inregistrare_id"]) is True
                return [(a, b, Decimal(s)) for a, b, s in d["linii"]]
            yield reev
        finally:
            c.rollback()


def test_def_c116_reevaluarile_succesive_folosesc_rezerva_si_pierderea_activului(uc):
    """ROȘU înainte (rezerva și pierderea luate 0): pasul 2 -> [655 = 2131 300], pasul 4 -> [2131 = 105 300]. MUTAȚIA:
    `rezerva_si_pierderea` care întoarce (0, 0) -> pică la pasul 2."""
    # OMFP 1802/2014 pct.111 alin.(1): creștere fără descreștere anterioară -> rezerva din reevaluare
    assert uc("2026-03-20", 3500) == [("2131", "105", Decimal("500.00"))]
    # pct.111 alin.(2): descreșterea scade rezerva „cu minimul dintre valoarea acelei rezerve și valoarea descreșterii” = min(500, 300)
    assert uc("2026-03-31", 3200) == [("105", "2131", Decimal("300.00"))]
    # pct.111 alin.(2): rezerva rămasă 200, „eventuala diferență rămasă neacoperită se înregistrează ca o cheltuială” = 300 pe 655
    assert uc("2026-03-31", 2700) == [("105", "2131", Decimal("200.00")), ("655", "2131", Decimal("300.00"))]
    # pct.111 alin.(1): creșterea compensează întâi „cheltuiala cu descreșterea recunoscută anterior la acel activ” -> 755 300
    assert uc("2026-03-31", 3000) == [("2131", "755", Decimal("300.00"))]


def test_c116_cifrele_date_in_cerere_raman_ale_cererii(uc):
    """Rezerva / pierderea scrise explicit în cerere (de ex. dintr-o reevaluare dinaintea preluării, care nu e în registrul iConta) nu
    se înlocuiesc cu cele calculate: 20.03 justă 2.800 (−200) cu rezerva declarată 150 -> 105 = 2131 150 + 655 = 2131 50."""
    assert uc("2026-03-20", 2800, sold_105_activ=150, pierdere_655_anterioara=0) == [
        ("105", "2131", Decimal("150.00")), ("655", "2131", Decimal("50.00"))]
