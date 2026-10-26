# -*- coding: utf-8 -*-
"""[lotul 13, deficiența 536, comanda Costin 13.1] Centrul de cost pe tot ce se contează automat, pe schemă efemeră (ROLLBACK la capăt).

Verbatim: „Centre de cost | Centrul se pune doar pe notele manuale; tot ce se contează automat (facturi, NIR, salarii, amortizare) iese
«nealocat» — pe F2: Producție 0, nealocat cheltuieli 1.900 / venituri 5.000. Centrul se poate pune pe liniile facturilor, NIR-urilor,
salariilor și pe mijloacele fixe (amortizarea moștenește centrul activului). Adăugarea și raportul funcționează.”

Ce se probează: (1) factura emisă cu centrul pe linie -> rândul de venit al notei poartă centrul, iar raportul nu-l mai pune „nealocat”;
(2) factura primită: rândul de cheltuială poartă centrul liniei; (3) centrul unei linii pe un cont de stoc / TVA nu se pune; (4) amortizarea
(și orice rând de cheltuială al activului) moștenește centrul activului; (5) nota salariilor se împarte pe centrele salariaților, la ban,
cu suma contului neschimbată; (6) un centru dezactivat / inexistent se refuză lângă câmpul lui; (7) alocările salariaților și ale
mijloacelor fixe se scriu și se citesc. Firma de probă: CUI 14399840 (cifra de control verificată cu algoritmul oficial); CNP de probă 1800101400016 (cifra de control verificată).
"""
import io
import os
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot13_comp_536"
D = "2026-10-15"
IDS = []


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as k:
            k.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            k.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            k.execute("SET search_path TO %s, public" % SCH)
            k.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, serie_factura, "
                      "urmator_numar_factura) VALUES (1, 'ZT Centre SRL', '14399840', true, 'SRL', 200, 'CC', 1)")
            k.execute("INSERT INTO centre_cost (nume) VALUES ('Producție'), ('Vânzări'), ('Vechi') RETURNING id")
            ids = [r[0] for r in k.fetchall()]
            k.execute("UPDATE centre_cost SET activ = false WHERE id = %s", (ids[2],))
        IDS[:] = ids   # Producție, Vânzări, Vechi (dezactivat)
        try:
            yield c
        finally:
            c.rollback()


def _linii_notei(c, factura_id):
    with c.cursor() as k:
        k.execute("SELECT l.cont_debit, l.cont_credit, l.suma::text, l.centru_cost_id FROM inregistrari_linii l JOIN inregistrari i "
                  "ON i.id = l.inregistrare_id WHERE i.factura_id = %s ORDER BY l.cont_debit, l.cont_credit, l.suma, l.centru_cost_id", (factura_id,))
        return k.fetchall()


def test_def_536_factura_emisa_duce_centrul_liniei_pe_randul_de_venit(conn):
    """Linia de 1.000 pe Producție, cea de 500 fără centru: 4111 = 704 se scrie pe două rânduri (Producție 1.000, fără centru 500), TVA-ul
    fără centru; după validare raportul arată Producție 1.000 venituri și numai 500 „nealocat”.
    MUTAȚIE: `centru_cost_id` scos din INSERT-ul `factura_linii` (`facturi_api.creeaza_factura`) -> un singur rând 1.500 nealocat -> pică."""
    from core import centre_cost_api as cc, facturi_api as fa
    prod = IDS[0]
    r = fa.emite_factura(conn, [{"descriere": "Consultanță", "cantitate": 1, "um": "ora", "pret_unitar": 1000, "cota_tva": 21,
                                 "cont_venit": "704", "centru_cost_id": prod},
                                {"descriere": "Mentenanță", "cantitate": 1, "um": "ora", "pret_unitar": 500, "cota_tva": 21,
                                 "cont_venit": "704"}], tert_nume="Client SRL", tert_cui="14399840", data_emitere=D)
    assert _linii_notei(conn, r["factura_id"]) == [("4111", "4427", "315.00", None), ("4111", "704", "500.00", None),
                                                   ("4111", "704", "1000.00", prod)]
    with conn.cursor() as k:
        k.execute("UPDATE inregistrari SET status = 'validata', document_ref = coalesce(document_ref, 'F-CC1') WHERE factura_id = %s",
                  (r["factura_id"],))
    rap = cc.raport_realizat(conn, SCH, "2026-10-01", "2026-10-31")
    assert ({x["nume"]: x["venituri"] for x in rap["centre"]}["Producție"], rap["nealocat"]["venituri"]) == (1000.0, 500.0)


def test_def_536_factura_primita_duce_centrul_pe_randul_de_cheltuiala_nu_pe_stoc(conn):
    """Factura primită cu două linii: 628 pe Vânzări (200) și 371 cu centru (300) — centrul rămâne pe 628 = 401, nu pe 371 (stocul nu e
    cheltuială) și nu pe 4426. MUTAȚIE: `e_rand_de_centru` scos din `contare_facturi._note_pe_cote` -> 371 = 401 cu centru -> pică."""
    from core import contare_facturi as cf, facturi_api as fa, repo_facturi as rf
    vanz = IDS[1]
    r = fa.creeaza_factura(conn, "F-77", D, "primita", [{"descriere": "Transport", "cantitate": 1, "um": "buc", "pret_unitar": 200,
                                                         "cota_tva": 21},
                                                        {"descriere": "Marfă", "cantitate": 1, "um": "buc", "pret_unitar": 300,
                                                         "cota_tva": 21}], tert_nume="Furnizor SA", tert_cui="31654471")
    with conn.cursor() as k:
        rf.actualizeaza_conturi_linii(k, SCH, r["factura_id"], ["628", "371"])
        rf.actualizeaza_centre_linii(k, SCH, r["factura_id"], [vanz, vanz])
        k.execute("UPDATE facturi SET tert_platitor_tva = true WHERE id = %s", (r["factura_id"],))
    with cf.cursor_dict(conn) as k:
        cf.contabilizeaza(k, SCH, r["factura_id"], automat=True, cont_cheltuiala="628")
    assert _linii_notei(conn, r["factura_id"]) == [("371", "401", "300.00", None), ("4426", "401", "105.00", None),
                                                   ("628", "401", "200.00", vanz)]


def test_def_536_amortizarea_mosteneste_centrul_activului(conn):
    """6811 = 2813 poartă centrul activului; un rând fără clasa 6 / 7 (2813 = 2131) nu.
    MUTAȚIE: citirea centrului scoasă din `mf_note.adauga_linie` -> 6811 fără centru -> pică."""
    from core import mf_note
    prod = IDS[0]
    with conn.cursor() as k:
        k.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, dnf_luni, data_pif, metoda, "
                  "centru_cost_id) VALUES ('MF1', 'Strung', '2131', '2813', 12000, 60, '2026-01-15', 'liniara', %s) RETURNING id", (prod,))
        mid = k.fetchone()[0]
        k.execute("INSERT INTO inregistrari (data, descriere, document_ref, status) VALUES (%s, 'Amortizare', 'AM', 'ciorna') RETURNING id", (D,))
        iid = k.fetchone()[0]
        mf_note.adauga_linie(k, SCH, iid, "6811", "2813", Decimal("200.00"), mid)
        mf_note.adauga_linie(k, SCH, iid, "2813", "2131", Decimal("50.00"), mid)
        k.execute("SELECT cont_debit, centru_cost_id FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id", (iid,))
        assert k.fetchall() == [("6811", prod), ("2813", None)]


def test_def_536_nota_salariilor_se_imparte_pe_centrele_salariatilor():
    """PUR. 641 = 421 3.000 (salariatul 1: 2.000 pe Producție, salariatul 2: 1.000 fără centru) -> 2.000 Producție + 1.000 fără centru; CAM
    646 = 436 68 după CAM-ul fiecăruia (45 / 23); 421 = 4315 (reținere) nu se împarte; trei centre egale pe 100,00 -> 33,33 / 33,33 /
    33,34 (restul pe ultimul, suma contului neschimbată). MUTAȚIE: restul pe ultimul centru scos (fiecare parte rotunjită) -> 99,99 -> pică."""
    from core import salarii_contare as sc
    note = [("641", "421", Decimal("3000.00")), ("646", "436", Decimal("68.00")), ("421", "4315", Decimal("750.00"))]
    pond = {"641": {1: Decimal("2000"), 2: Decimal("1000")}, "646": {1: Decimal("45"), 2: Decimal("23")}}
    assert sc.pe_centre(note, pond, {1: 7}) == [("641", "421", Decimal("2000.00"), 7), ("641", "421", Decimal("1000.00"), None),
                                                 ("646", "436", Decimal("45.00"), 7), ("646", "436", Decimal("23.00"), None),
                                                 ("421", "4315", Decimal("750.00"), None)]
    trei = sc.pe_centre([("641", "421", Decimal("100.00"))], {"641": {1: Decimal("1"), 2: Decimal("1"), 3: Decimal("1")}}, {1: 1, 2: 2, 3: 3})
    assert ([x[2] for x in trei], sum(x[2] for x in trei)) == ([Decimal("33.33"), Decimal("33.33"), Decimal("33.34")], Decimal("100.00"))


def test_def_536_centrul_dezactivat_sau_inexistent_se_refuza_langa_camp(conn):
    """Linia 0 cu un centru activ trece, linia 1 cu centrul dezactivat și linia 2 cu un centru inexistent se refuză lângă câmpurile lor;
    linia fără centru trece. MUTAȚIE: `activ = true` scos din `centre_gresite` -> centrul dezactivat trece -> pică."""
    from core import centre_cost_api as cc
    prod, _v, vechi = IDS
    with conn.cursor() as k:
        assert cc.campuri_centru_gresit(k, SCH, [prod, vechi, 999999, None, ""], lambda i: "em-l%d-centru" % i) == [
            ("em-l1-centru", cc.MESAJ_CENTRU_INEXISTENT), ("em-l2-centru", cc.MESAJ_CENTRU_INEXISTENT)]


def test_def_536_alocarile_salariatilor_si_ale_activelor(conn):
    """Salariatul și activul primesc centrul din ecranul Centre de cost; un centru dezactivat se refuză lângă rândul lui și nimic nu se
    scrie. MUTAȚIE: refuzul scos din `seteaza_alocari` -> centrul dezactivat se scrie -> pică."""
    from core import centre_cost_api as cc
    prod, _v, vechi = IDS
    with conn.cursor() as k:
        k.execute("INSERT INTO salariati (cnp, nume, prenume, data_angajare) VALUES ('1800101400016', 'Pop', 'Ion', '2026-01-01') RETURNING id")
        sid = k.fetchone()[0]
        k.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, dnf_luni, data_pif, metoda) "
                  "VALUES ('MF2', 'Laptop', '2131', '2813', 5000, 36, '2026-01-15', 'liniara') RETURNING id")
        mid = k.fetchone()[0]
    rau = cc.seteaza_alocari(conn, SCH, {sid: vechi}, {mid: prod})
    assert [e["camp"] for e in rau["erori_campuri"]] == ["cc-sal-%d" % sid]
    assert cc.seteaza_alocari(conn, SCH, {sid: prod}, {mid: str(prod)})["ok"] is True
    a = cc.alocari(conn, SCH)
    assert ([(x["id"], x["centru_cost_id"]) for x in a["salariati"]], [(x["id"], x["centru_cost_id"]) for x in a["mijloace"]]) == (
        [(sid, prod)], [(mid, prod)])


# ── 536 / NIR — decizia Costin, varianta (a): „centrul pe articol sau pe gestiune, ieșirea din stoc îl moștenește” ──────────────────────
def test_def_536_iesirea_din_stoc_mosteneste_centrul_articolului(conn):
    """NIR-ul scrie numai stoc / TVA / furnizor; cheltuiala apare la IEȘIRE. Articolul „Făină” pe Producție: intrarea (fără notă de cheltuială)
    și ieșirea la CMP -> 607 = 371 poartă centrul articolului; reclasificarea 371 -> 301 (stoc = stoc) nu poartă centru.
    MUTAȚIE: `centrul_articolului` întoarce mereu None (`scrie_rand_stoc`) -> 607 fără centru -> pică."""
    from core import stocuri_cv_api as cv
    prod = IDS[0]
    with conn.cursor() as k:
        k.execute("UPDATE firma_profil SET metoda_stoc = 'cantitativ_valoric'")
        k.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala, centru_cost_id) VALUES ('Făină', 'kg', '371', '607', %s) "
                  "RETURNING id", (prod,))
        aid = k.fetchone()[0]
    assert cv.intrare(conn, SCH, {"articol_id": aid, "data": "2026-10-01", "cantitate": "10", "pret_unitar": "5", "document": "NIR 1"}).get("id")
    r = cv.iesire(conn, SCH, {"articol_id": aid, "data": "2026-10-05", "cantitate": "4", "document": "Bon consum 1"})
    rc = cv.reclasificare(conn, SCH, {"articol_id": aid, "cont_stoc_nou": "301", "data": "2026-10-06", "document": "NC 1"})
    with conn.cursor() as k:
        k.execute("SELECT inregistrare_id, cont_debit, cont_credit, suma::text, centru_cost_id FROM inregistrari_linii "
                  "WHERE inregistrare_id = ANY(%s) ORDER BY inregistrare_id", ([r["inregistrare_id"], rc["inregistrare_id"]],))
        assert [x[1:] for x in k.fetchall()] == [("607", "371", "20.00", prod), ("301", "371", "30.00", None)]


def test_def_536_articolul_primeste_centrul_din_alocare(conn):
    """Articolul de stoc apare în alocare și primește centrul (al treilea tabel al ferestrei); centrul dezactivat se refuză lângă rândul
    articolului. MUTAȚIE: grupa `articole` scoasă din `seteaza_alocari` -> centrul articolului nu se scrie -> pică."""
    from core import centre_cost_api as cc
    prod, _v, vechi = IDS
    with conn.cursor() as k:
        k.execute("INSERT INTO articole (denumire, um) VALUES ('Zahăr', 'kg') RETURNING id")
        aid = k.fetchone()[0]
    assert [e["camp"] for e in cc.seteaza_alocari(conn, SCH, articole={aid: vechi})["erori_campuri"]] == ["cc-art-%d" % aid]
    assert cc.seteaza_alocari(conn, SCH, articole={aid: prod})["articole"] == 1
    assert [(x["id"], x["centru_cost_id"]) for x in cc.alocari(conn, SCH)["articole"]] == [(aid, prod)]
