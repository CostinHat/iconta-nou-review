# -*- coding: utf-8 -*-
"""[lotul 11, F] Refuzul generării reevaluării pentru partenerul cu facturi în MAI MULTE monede (decizia 10.3: plata lui nelegată nu se
atribuie unei monede) — cum îl citește contabilul.

Defectul (găsit de G3, 22.10.2026): „leagă de factura pe care o stinge plata nelegată de 200.00 lei din 2099-09-22 (4111): partenerul
Factură EX nr. 3 din 11.09.2099 are facturi în mai multe monede …” — suma și data în forma tehnică (nu `bani` / `data_ro`, DS cap.4), iar
partenerul numit prin factura lui. Acum: „… de 200,00 lei din 22.09.2099 (4111): partenerul FISCALOS ICONTA S.R.L. are facturi …”.

Datele: schemă efemeră din șablon (`efemer_429f`, a lui, nu a testului V), perioadă SINTETICĂ 2099; partenerul B are F3 100 EUR și F4
300 RON (cod fiscal 55229657, FISCALOS ICONTA S.R.L., cifra de control verificată mai jos) și o încasare nelegată de 200,00 lei pe 4111 la
22.09.2099. Inserările directe sunt datele de PORNIRE (facturi contate, încasare din bancă) — ce se verifică e refuzul produs de
`uc_reevaluare.reevaluare_valuta_genereaza`, pe drumul ecranului.
"""
import datetime
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core.test_lot11_v_reevaluare import _cui_valid, _db_ok, _factura, _incasare

SCH = "efemer_429f"
CTX = {"uid": 1, "firm": 1}
B = "55229657"

pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def firma(monkeypatch):
    from core import auth_api, common, uc_curs_bnr
    assert _cui_valid(B)   # CLAUDE.md „Date de test — CUI/CNP”: cifra de control, algoritmul oficial
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'F SRL', 'RO14399840')")
            cur.execute("INSERT INTO plan_conturi (simbol, denumire) VALUES ('5124.EUR', 'Cont BT EUR')")
            _factura(cur, "3", "2099-09-11", 100, "5.00", B, "FISCALOS ICONTA S.R.L.")
            _factura(cur, "4", "2099-09-12", 300, "1", B, "FISCALOS ICONTA S.R.L.", moneda="RON")
            _incasare(cur, "2099-09-22", 200, B, doc="Extras B")
            cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES ('2099-09-30', 'EUR', 5.0000) "
                        "ON CONFLICT (data, moneda) DO UPDATE SET curs = EXCLUDED.curs")
        c.commit()
    monkeypatch.setattr(common, "azi_ro", lambda: datetime.date(2099, 12, 15))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    monkeypatch.setattr(uc_curs_bnr, "asigura_cursul", lambda *a, **k: None)
    yield
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute("DELETE FROM public.curs_bnr_zilnic WHERE data = '2099-09-30' AND moneda = 'EUR'")
        c.commit()


def test_plata_de_legat_se_spune_in_forma_romaneasca_cu_numele_partenerului(firma):
    """MUTAȚII: `bani(p["lei"], "lei")` -> `"%s lei" % p["lei"]` / `data_ro(p["data"])` -> `p["data"]` / `e.get("partener")` ->
    `e.get("document")` -> pică."""
    from core import erori, uc_reevaluare
    with pytest.raises(erori.DateInvalide) as e:
        uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9}, CTX)
    camp = "rv-sold_valuta-p:4111:%s:EUR" % B
    asteptat = ("leagă de factura pe care o stinge plata nelegată de 200,00 lei din 22.09.2099 (4111): partenerul FISCALOS ICONTA S.R.L. "
                "are facturi în mai multe monede, deci nu se poate afla în ce monedă e plata")
    # rândul EXACT de lângă câmpul elementului EUR al partenerului (și numai el: elementul RON n-are sold în valută de reevaluat)
    assert [(x["camp"], x["mesaj"]) for x in e.value.detaliu["erori_campuri"] if x["camp"] == camp] == [(camp, asteptat)], e.value.detaliu
    assert e.value.detaliu["mesaj"].count(asteptat) >= 1, e.value.detaliu["mesaj"]


def test_partenerul_fara_nume_e_numit_prin_codul_fiscal():
    """Elementul pe partener, forma din `reevaluare_valuta._elemente_parteneri` (`partener` = numele de pe facturi, aici gol)."""
    from core import uc_reevaluare
    el = {"cheie": "p:4111:%s:EUR" % B, "partener": None, "partener_cheie": B, "document": "Factură EX nr. 3 din 11.09.2099",
          "cont": "4111", "de_completat": [], "plati_de_legat": [{"data": "2099-09-22", "lei": "1234.5", "document": "Extras B",
                                                                    "nota_id": 1}]}
    assert uc_reevaluare._ce_lipseste(el) == (
        "leagă de factura pe care o stinge plata nelegată de 1.234,50 lei din 22.09.2099 (4111): partenerul cu codul fiscal 55229657 are "
        "facturi în mai multe monede, deci nu se poate afla în ce monedă e plata")
