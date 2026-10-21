# -*- coding: utf-8 -*-
"""429 — riscul de dublare găsit de subagentul V (lotul 10): formularul manual „Reevaluare lunară solduri valută” nu lăsa nicio urmă,
deci propunerea din Închidere lună nu-l vedea: aceeași diferență s-ar fi înregistrat de două ori (o dată pe soldul agregat al contului,
o dată factură cu factură). Comanda 10.1 pct.8 / pct.9: „Formularul manual rămâne pentru cazuri speciale” — deci:
  - pe un cont de terți cu facturi în valută în evidență, formularul manual REFUZĂ (le reevaluează propunerea, factură cu factură);
  - pe un cont fără factură (disponibilitățile), reevaluarea manuală se consemnează în `reevaluari_valuta`, iar propunerea o vede.
Temei: OMFP 1802/2014 pct.325 alin.(1) — fiecare element se reevaluează o dată pe lună, la cursul BNR din ultima zi bancară.
Fixtura și perioadele sintetice 2099: `core/test_lot10_reevaluare.py`.
MUTAȚII: refuzul (`if _dublate`) scos din `uc_tenants.reevaluare_valuta` -> primul test pică; `_rv.consemneaza(...)` scos -> al doilea pică.
"""
import pytest

from core.test_lot10_reevaluare import CTX, _db_ok, _el, firma   # noqa: F401 — fixtura, refolosită


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_formularul_manual_refuza_contul_ale_carui_facturi_le_reevalueaza_propunerea(firma):   # noqa: F811
    from core import erori, uc_tenants
    corp = {"data": "2099-09-30", "solduri": [{"cont": "4111", "valoare_valuta": 1000, "moneda": "EUR", "curs_evidenta": 4.97,
                                               "tip": "creanta"}]}
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.reevaluare_valuta(1, corp, CTX)
    # OMFP 1802/2014 pct.325 alin.(1): o singură reevaluare a creanței pe lună — propunerea o face pe factură
    assert str(e.value) == uc_tenants.MESAJ_REEVALUARE_PE_FACTURI % "4111"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reevaluarea_manuala_a_disponibilitatilor_e_vazuta_de_propunere(firma):   # noqa: F811
    from core import uc_reevaluare, uc_tenants
    r = uc_tenants.reevaluare_valuta(1, {"data": "2099-09-30", "solduri": [{"cont": "5124.EUR", "valoare_valuta": 1000, "moneda": "EUR",
                                                                            "curs_evidenta": 4.95, "tip": "disponibil"}]}, CTX)
    assert r["inregistrare_id"], r
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX)
    disp = _el(p, "c5124.EUR")
    # reevaluat deja în lună: soldul în valută și cursul nou vin din urma reevaluării manuale (+50,00 lei pe 765), nu se cer din nou
    assert (disp["moneda"], disp["sold_valuta"], disp["curs_evidenta"], disp["de_completat"]) == ("EUR", "1000.00", "5.0000", []), disp
    assert disp["diferenta"] in ("0.00", None) or float(disp["diferenta"]) == 0, disp


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_generarea_propunerii_nu_sterge_reevaluarea_manuala(firma):   # noqa: F811
    """Generarea înlocuiește ciorna PROPUNERII lunii (T1); nota manuală rămâne a omului. MUTAȚIE: `and r["sursa"] == "propunere"` scos
    din `reevaluare_valuta.propunere` -> nota manuală intră în `ciorna_lunii` și e ștearsă la generare -> pică."""
    from core import db, uc_reevaluare, uc_tenants
    m = uc_tenants.reevaluare_valuta(1, {"data": "2099-09-30", "solduri": [{"cont": "5124.EUR", "valoare_valuta": 1000, "moneda": "EUR",
                                                                            "curs_evidenta": 4.95, "tip": "disponibil"}]}, CTX)
    g = uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9}, CTX)
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id FROM efemer_429.inregistrari WHERE id = %s", (m["inregistrare_id"],))
        assert cur.fetchone(), "nota manuală a fost ștearsă de generare"
        cur.execute("SELECT sursa, count(*) FROM efemer_429.reevaluari_valuta GROUP BY sursa ORDER BY sursa")
        # 5124.EUR reevaluat manual o dată; propunerea scrie numai cele două facturi (diferența contului e 0, deja reevaluat)
        assert cur.fetchall() == [("manual", 1), ("propunere", 3)], g
