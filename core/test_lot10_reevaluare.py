# -*- coding: utf-8 -*-
"""429 — reevaluarea lunară în valută, PROPUSĂ de aplicație (lotul 10, comanda Costin 10.1 pct.8, verbatim în DECIZII „Comanda 10.1”):
„La închiderea lunii, aplicația propune singură creanțele și datoriile în valută neîncasate (pe factură), disponibilitățile în valută,
cursul din evidență, cursul BNR din ultima zi bancară și diferența pe 665/765; contabilul verifică și generează nota. Reevaluarea apare
în «Ce oprește închiderea» când există solduri în valută.”

Temei: OMFP 1802/2014 pct.325 alin.(1) „La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al
pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se
recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz.”; alin.(2) lit.b (disponibilitățile în
valută). Perioade SINTETICE 2099 (schemă efemeră din template, ștearsă la ieșire; cursurile BNR din 2099 în `public.curs_bnr_zilnic`,
scrise de test și șterse la ieșire — nicio zi reală nu se atinge).
"""
import datetime
import io
import re
from decimal import Decimal

import pytest

from core import db as _db
from core import reevaluare_valuta as _rv
from core import tenant_provisioning as _tprov

SCH = "efemer_429"
CURSURI = [("2099-09-30", "EUR", "5.0000"), ("2099-09-30", "USD", "4.5000"),
           ("2099-10-30", "EUR", "5.0500"), ("2099-10-30", "USD", "4.4000")]


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _nota(cur, data, linii, factura_id=None, sursa="manual", status="validata", doc="Extras test"):
    cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status, document_ref) VALUES (%s,%s,'t',%s,%s,%s) "
                "RETURNING id", (data, factura_id, sursa, status, doc))
    nid = cur.fetchone()[0]
    for d, c, s in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))
    return nid


@pytest.fixture()
def firma(monkeypatch):
    """Factura emisă 1.000 EUR la 4,97 (10.09.2099), neîncasată: 4111 = 707 4.970,00. Factura primită 500 USD la 4,40 (12.09.2099):
    628 = 401 2.200,00. Contul 5124.EUR („Cont BT EUR”) cu 4.950,00 lei (1.000 EUR la 4,95). Cursul BNR la 30.09.2099: EUR 5,0000,
    USD 4,5000; la 30.10.2099 (vineri; 31.10 e sâmbătă): EUR 5,0500, USD 4,4000."""
    from core import auth_api, common, uc_curs_bnr
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'F SRL', 'RO14399840')")
            cur.execute("INSERT INTO plan_conturi (simbol, denumire) VALUES ('5124.EUR', 'Cont BT EUR')")
            cur.execute("INSERT INTO facturi (numar, serie, data_emitere, total, tva, moneda, directie, status, tert_nume, curs_bnr, "
                        "total_lei, tva_lei, data_curs) VALUES ('1', 'EX', '2099-09-10', 1000, 0, 'EUR', 'emisa', 'emisa', 'Client GmbH', "
                        "4.97, 4970, 0, '2099-09-09') RETURNING id")
            fe = cur.fetchone()[0]
            cur.execute("INSERT INTO facturi (numar, serie, data_emitere, total, tva, moneda, directie, status, tert_nume, curs_bnr, "
                        "total_lei, tva_lei, data_curs) VALUES ('77', 'US', '2099-09-12', 500, 0, 'USD', 'primita', 'emisa', "
                        "'Supplier Inc', 4.40, 2200, 0, '2099-09-11') RETURNING id")
            fp = cur.fetchone()[0]
            _nota(cur, "2099-09-10", [("4111", "707", 4970)], fe, sursa="facturi")
            _nota(cur, "2099-09-12", [("628", "401", 2200)], fp, sursa="facturi")
            _nota(cur, "2099-09-05", [("5124.EUR", "456", 4950)])
            for d, m, k in CURSURI:
                cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (d, m, k))
        c.commit()
    monkeypatch.setattr(common, "azi_ro", lambda: datetime.date(2099, 12, 15))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    cerute = []
    monkeypatch.setattr(uc_curs_bnr, "asigura_cursul", lambda m, z, prag_zile=5: cerute.append((m, str(z), prag_zile)))
    yield {"fe": fe, "fp": fp, "cerute": cerute}
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute("DELETE FROM public.curs_bnr_zilnic WHERE data BETWEEN '2099-09-30' AND '2099-10-30' AND moneda IN ('EUR','USD')")
        c.commit()


CTX = {"uid": 1, "firm": 1}


def _el(prop, cheie):
    return next(e for e in prop["elemente"] if e["cheie"] == cheie)


def _controale(an, luna):
    from core import uc_comun
    with _db.get_conn() as c:
        return uc_comun.controale_inchidere(c, SCH, an, luna)


def _valideaza(nid):
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("UPDATE %s.inregistrari SET status = 'validata' WHERE id = %%s" % SCH, (nid,))
        c.commit()


def _linii(nid):
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM %s.inregistrari_linii WHERE inregistrare_id = %%s ORDER BY id" % SCH, (nid,))
        return [(d, cr, str(s)) for d, cr, s in cur.fetchall()]


def test_def_429_propunerea_lunii_are_facturile_si_disponibilitatile_cu_cursurile_si_diferenta(firma):
    """MUTAȚIE: în `_cont_si_sens`, `castig = dif > 0 if tip in (...) else dif < 0` -> `dif > 0` pentru toate (datoria cu cursul crescut
    ar ieși câștig) -> pică pe 401."""
    from core import uc_reevaluare
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX)
    fe, fp, disp = _el(p, "f%d" % firma["fe"]), _el(p, "f%d" % firma["fp"]), _el(p, "c5124.EUR")
    # OMFP 1802/2014 pct.325 alin.(1): creanța în valută la cursul BNR din ultima zi bancară a lunii; crește cursul -> venit 765
    assert (fe["cont"], fe["moneda"], fe["sold_valuta"], fe["curs_evidenta"], fe["curs_bnr"], fe["data_curs"], fe["lei_evidenta"],
            fe["lei_bnr"], fe["diferenta"], fe["cont_diferenta"]) == (
        "4111", "EUR", "1000.00", "4.9700", "5.0000", "2099-09-30", "4970.00", "5000.00", "30.00", "765"), fe
    assert fe["document"] and fe["partener"] == "Client GmbH" and not fe["estimat"]
    # OMFP 1802/2014 pct.325 alin.(1) + planul de conturi, 665: „diferențele nefavorabile [...] din evaluarea datoriilor în valută, la
    # finele lunii (… 401 …)” — datoria crește cu cursul -> cheltuială 665
    assert (fp["cont"], fp["sold_valuta"], fp["curs_bnr"], fp["diferenta"], fp["cont_diferenta"]) == (
        "401", "500.00", "4.5000", "50.00", "665"), fp
    # OMFP 1802/2014 pct.325 alin.(2) lit.b: disponibilitățile în valută; soldul în VALUTĂ nu e în evidență -> se cere, nu se inventează
    assert (disp["moneda"], disp["sold_valuta"], disp["lei_evidenta"], disp["de_completat"], disp["editabile"]) == (
        "EUR", None, "4950.00", ["sold_valuta"], ["sold_valuta", "moneda"]), disp
    assert p["totaluri"]["venit"] == "30.00" and p["totaluri"]["cheltuiala"] == "50.00" and p["totaluri"]["de_completat"] == 1
    # cursul ultimei zile bancare se cere BNR-ului înaintea tranzacției (30.09.2099 e miercuri: pragul 0 zile)
    assert ("EUR", "2099-09-30", 0) in firma["cerute"] and ("USD", "2099-09-30", 0) in firma["cerute"]


def test_def_429_inchiderea_e_oprita_pana_la_reevaluare_si_nota_o_deblocheaza(firma):
    """MUTAȚIE: `blocaje.append(_ctl("REEVALUARE_VALUTA"` -> `semnale.append(` -> pică (reevaluarea lunară e obligatorie, nu semnal)."""
    from core import uc_reevaluare, erori
    ctl = _controale(2099, 9)
    b = [x for x in ctl["blocaje"] if x["cod"] == "REEVALUARE_VALUTA"]
    # OMFP 1802/2014 pct.325 alin.(1) „La finele fiecărei luni [...] se evaluează” — obligatoriu lunar -> blocaj
    # numărul elementelor și defalcarea lor, din locul ei în mesaj („(<temei>: <defalcare>)”), nu „apare undeva”
    assert len(b) == 1 and b[0]["elemente"] == 3, ctl["blocaje"]
    assert b[0]["mesaj"].partition("(%s: " % _rv.TEMEI)[2].partition(");")[0] == "2 facturi, 1 cont de disponibilități", b[0]["mesaj"]
    with pytest.raises(erori.DateInvalide) as ei:   # soldul în valută al lui 5124.EUR lipsește: nu se generează pe o valoare inventată
        uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9}, CTX)
    assert re.findall(r"contul (\S+?)(?=, |\.$)", str(ei.value)) == ["5124.EUR"], str(ei.value)   # exact contul care cere completarea
    r = uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "completari": {"c5124.EUR": {"sold_valuta": "1000,00"}}}, CTX)
    assert (r["venit"], r["cheltuiala"], r["elemente"]) == ("80.00", "50.00", 3), r
    # nota: 4111 = 765 (creanța), 665 = 401 (datoria), 5124.EUR = 765 (disponibilul: 1.000 x 5,00 - 4.950)
    assert sorted(_linii(r["inregistrare_id"])) == sorted([("4111", "765", "30.00"), ("665", "401", "50.00"), ("5124.EUR", "765", "50.00")])
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT status, document_ref FROM %s.inregistrari WHERE id = %%s" % SCH, (r["inregistrare_id"],))
        st, doc = cur.fetchone()
    assert st == "ciorna" and doc.startswith("Notă de calcul"), (st, doc)   # R36: ciornă; documentul intern al notei (R3)
    cod = [x["cod"] for x in _controale(2099, 9)["blocaje"]]
    assert cod == ["CIORNE"], cod   # ciorna lunii acoperă reevaluarea (REEVALUARE_VALUTA dispare); CIORNE cere validarea ei
    _valideaza(r["inregistrare_id"])
    assert _controale(2099, 9)["blocaje"] == [], _controale(2099, 9)["blocaje"]


def test_def_429_a_doua_generare_inlocuieste_ciorna_cu_acelasi_document(firma):
    """MUTAȚIE: scoaterea `_nd.sterge_ciorna_inlocuita(...)` din generare -> două note în lună -> pică."""
    from core import uc_reevaluare
    comp = {"c5124.EUR": {"sold_valuta": "1000"}}
    r1 = uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "completari": comp}, CTX)
    r2 = uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "completari": {"c5124.EUR": {"sold_valuta": "990"}}}, CTX)
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, document_ref FROM %s.inregistrari WHERE descriere LIKE 'Reevaluare valută%%'" % SCH)
        note = cur.fetchall()
        cur.execute("SELECT count(*) FROM %s.reevaluari_valuta" % SCH)
        randuri = cur.fetchone()[0]
    assert r2["inlocuita"] and len(note) == 1 and note[0][0] == r2["inregistrare_id"] != r1["inregistrare_id"], note
    assert note[0][1].startswith("Notă de calcul nr 1 "), note   # documentul ciornei înlocuite, fără număr nou
    assert randuri == 3   # rândurile ciornei vechi au căzut cu ea (ON DELETE CASCADE)
    # 990 EUR x 5,00 = 4.950,00 = soldul în lei -> nicio diferență pe 5124.EUR
    assert ("5124.EUR", "765", "50.00") not in _linii(r2["inregistrare_id"])


def test_def_429_luna_urmatoare_porneste_de_la_cursul_reevaluarii_iar_plata_scade_soldul(firma):
    """MUTAȚIE: în `propunere`, `curs_ev, sursa_ev = _dec(x["curs_nou"])` -> cursul facturii -> pică (luna următoare ar reevalua de
    la 4,97, a doua oară aceeași diferență)."""
    from core import uc_reevaluare
    r = uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "completari": {"c5124.EUR": {"sold_valuta": "1000"}}}, CTX)
    _valideaza(r["inregistrare_id"])
    with _db.get_conn() as c, c.cursor() as cur:   # încasare parțială 500 EUR, la cursul din evidență (5,00): 5124.EUR = 4111 2.500
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        _nota(cur, "2099-10-15", [("5124.EUR", "4111", 2500)], firma["fe"], sursa="banca")
        c.commit()
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 10, CTX)
    fe, fp, disp = _el(p, "f%d" % firma["fe"]), _el(p, "f%d" % firma["fp"]), _el(p, "c5124.EUR")
    # OMFP 1802/2014 pct.322 alin.(1): plata stinge creanța la cursul la care e înregistrată în contabilitate (5,00 după reevaluare)
    assert (fe["curs_evidenta"], fe["curs_evidenta_din"], fe["sold_valuta"], fe["estimat"], fe["lei_evidenta"], fe["lei_bnr"],
            fe["diferenta"], fe["cont_diferenta"]) == ("5.0000", "2099-09-30", "500.00", True, "2500.00", "2525.00", "25.00", "765"), fe
    assert fe["editabile"] == ["sold_valuta"]   # soldul unei facturi cu plăți în lei e estimat: se poate corecta
    # datoria: 500 USD de la 4,50 (evidența după septembrie) la 4,40 -> scade cu 50,00 -> favorabilă, 765
    assert (fp["curs_evidenta"], fp["lei_evidenta"], fp["diferenta"], fp["cont_diferenta"]) == ("4.5000", "2250.00", "-50.00", "765"), fp
    # disponibilul: moneda rămâne cunoscută, soldul în valută se cere din nou (s-a mișcat: 5.000 + 2.500 lei)
    assert (disp["moneda"], disp["lei_evidenta"], disp["sold_valuta"], disp["data_curs"]) == ("EUR", "7500.00", None, "2099-10-30"), disp


def test_def_429_factura_incasata_integral_nu_mai_intra_in_propunere(firma):
    """MUTAȚIE: `if valuta <= _TOL: continue` -> scos -> factura încasată apare cu sold 0 și diferență -> pică."""
    from core import uc_reevaluare
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        _nota(cur, "2099-09-20", [("5124.EUR", "4111", 4970)], firma["fe"], sursa="banca")
        c.commit()
    p = uc_reevaluare.reevaluare_valuta_propunere(1, 2099, 9, CTX)
    assert "f%d" % firma["fe"] not in [e["cheie"] for e in p["elemente"]], p["elemente"]


def test_def_429_completarea_unui_camp_needitabil_e_refuzata(firma):
    """Soldul unei facturi neîncasate vine din factură: nu se rescrie pe ecran."""
    from core import uc_reevaluare, erori
    with pytest.raises(erori.DateInvalide) as ei:
        uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "completari": {
            "f%d" % firma["fe"]: {"sold_valuta": "900"}, "c5124.EUR": {"sold_valuta": "1000"}}}, CTX)
    # câmpul refuzat, numit (eticheta lui, între ghilimele), pe elementul facturii — nu „apare undeva «sold în valută»”
    assert re.findall(r"„([^”]+)”", str(ei.value)) == ["sold în valută"], str(ei.value)


def test_def_429_luna_in_curs_nu_se_reevalueaza_si_nu_blocheaza(firma, monkeypatch):
    from core import common, uc_reevaluare, erori
    monkeypatch.setattr(common, "azi_ro", lambda: datetime.date(2099, 9, 20))
    with pytest.raises(erori.CerereGresita):
        uc_reevaluare.reevaluare_valuta_genereaza(1, {"an": 2099, "luna": 9, "completari": {"c5124.EUR": {"sold_valuta": "1000"}}}, CTX)
    assert "REEVALUARE_VALUTA" not in [x["cod"] for x in _controale(2099, 9)["blocaje"]]


def test_motorul_reevaluare_element_aduce_soldul_la_valuta_ori_curs():
    """Motorul pur: diferența = valuta x curs BNR (rotunjit ROUND_HALF_UP) - soldul în lei din evidență."""
    from core import diferente_curs as dc
    r = dc.reevaluare_element("333.33", "1666.65", "5.0123", "creanta", "4111")
    # 333,33 x 5,0123 = 1.670,750 -> 1.670,75 (ROUND_HALF_UP); 1.670,75 - 1.666,65 = 4,10 -> 765 (OMFP 1802/2014 pct.325 alin.(1))
    assert (r["lei_nou"], r["diferenta"], r["linie"]) == (Decimal("1670.75"), Decimal("4.10"), ("4111", "765", Decimal("4.10")))
    r = dc.reevaluare_element("100", "500", "4.9", "datorie", "401")
    assert (r["diferenta"], r["linie"]) == (Decimal("-10.00"), ("401", "765", Decimal("10.00")))
    assert dc.reevaluare_element("100", "490", "4.9", "disponibil", "5124")["linie"] is None
