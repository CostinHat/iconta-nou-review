# -*- coding: utf-8 -*-
"""GARDA părții 1 din comanda Costin 06.10.2026 (răspunsul la §6 din raportul „Fluxul de factură pe F1”), pe schemă efemeră.

§6.1, verbatim: „Seria devine obligatorie la emitere (CF art.319 alin.(20) lit.a). Refuzul nu blochează: seria se setează direct
din mesajul de refuz și emiterea continuă. Facturile deja emise nu se modifică.”
Temei: CF art.319 alin.(20) lit.a) — „numărul de ordine, în baza uneia sau a mai multor serii, care identifică factura în mod
unic” (`anaf_surse/cod_fiscal_227_2015_consolidat.txt`).
"""
import datetime
import io
import os

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot0610_p1"
LINII = [{"descriere": "Consultanță", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "cont_venit": "704"}]


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
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, urmator_numar_factura) "
                        "VALUES (1, 'ZT Serie SRL', '14399840', true, 'SRL', 200, 4)")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _urmator(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT urmator_numar_factura FROM firma_profil")
        return cur.fetchone()[0]


# ── §6.1 seria obligatorie ───────────────────────────────────────────────────────────────────────────────────────────────
def test_factura_fara_serie_se_refuza_numit_fara_sa_consume_numarul(conn):
    """CF art.319 alin.(20) lit.a: factura se numerotează „în baza uneia sau a mai multor serii”. MUTAȚIE: verificarea scoasă
    din `emite_factura` -> factura „4” fără serie se emite -> pică."""
    from core import facturi_api as fa
    with pytest.raises(ValueError) as e:
        fa.emite_factura(conn, LINII, tert_nume="Client SRL", tert_cui="14399840")
    assert (e.value.cod, e.value.temei, e.value.camp) == ("SERIE_LIPSA", "CF art.319 alin.(20) lit.a)", "serie")
    assert _urmator(conn) == 4, "refuzul a consumat un număr"


def test_dupa_setarea_seriei_emiterea_continua_cu_numarul_urmator_si_facturile_vechi_raman(conn):
    from core import facturi_api as fa
    with conn.cursor() as cur:   # o factură emisă înainte, fără serie (ca pe F1/F2 în producție)
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva) VALUES ('3', '', '2026-10-01', 'emisa', 121, 21)")
    fa.seteaza_numerotare(conn, serie="FCT")
    r = fa.emite_factura(conn, LINII, tert_nume="Client SRL", tert_cui="14399840")
    with conn.cursor() as cur:
        cur.execute("SELECT numar, serie FROM facturi ORDER BY id")
        assert cur.fetchall() == [("3", ""), ("FCT4", "FCT")]
    assert r["numar"] == "FCT4"


def test_storno_fara_serie_se_refuza_la_fel(conn):
    """Storno-ul e tot o factură (al doilea document cu numărul lui). MUTAȚIE: verificarea scoasă din `storneaza` -> pică."""
    from core import facturi_api as fa
    fa.seteaza_numerotare(conn, serie="FCT")
    r = fa.emite_factura(conn, LINII, tert_nume="Client SRL", tert_cui="14399840")
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET serie_factura = NULL")
    with pytest.raises(ValueError) as e:
        fa.storneaza(conn, r["factura_id"])
    assert e.value.cod == "SERIE_LIPSA"


def test_proforma_nu_cere_seria_facturii(conn):
    """Proforma nu e factură (art.319 se aplică facturii); are seria ei („PF”)."""
    from core import facturi_api as fa
    r = fa.emite_factura(conn, LINII, tip="proforma", tert_nume="Client SRL", tert_cui="14399840")
    assert r["numar"].startswith("PF")


def test_pregatirea_emiterii_spune_ca_lipseste_seria(conn):
    from core import facturi_api as fa
    r = fa.pregatire_emitere(conn, -1, datetime.date(2026, 10, 6))
    assert r["serie_lipsa"] is True
    fa.seteaza_numerotare(conn, serie="FCT")
    assert fa.pregatire_emitere(conn, -1, datetime.date(2026, 10, 6))["serie_lipsa"] is False


# ── §6.2 documentul intern generat odată cu nota ─────────────────────────────────────────────────────────────────────────
def _ref(conn, nid):
    with conn.cursor() as cur:
        cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (nid,))
        return cur.fetchone()[0]


def test_operatiunile_speciale_si_amortizarea_poarta_documentul_lor_numerotat_pe_tip_si_an(conn):
    """Legea 82/1991 art.6 alin.(1): operațiunea „se consemnează în momentul efectuării ei într-un document”. Numerotarea e pe
    tip și pe an. MUTAȚIE: `_cu_document_intern` scos din `nota_facturi_ciorna` -> None -> pică."""
    from core import repo_contabilitate as rc
    with conn.cursor() as cur:
        a1 = rc.nota_amortizare_validata(cur, SCH, datetime.date(2026, 10, 28), "AMORT-2026-10", "Amortizare 10/2026")[0]
        n1 = rc.nota_facturi_ciorna(cur, SCH, "2026-10-06", "Leasing")[0]
        n2 = rc.nota_banca_ciorna(cur, SCH, "2026-10-07", "Reevaluare valută")[0]
        n3 = rc.nota_facturi_ciorna(cur, SCH, "2027-01-05", "Avans")[0]
        i1 = rc.nota_facturi_ciorna(cur, SCH, "2026-10-08", "Inventariere", "lista_inventariere")[0]
    assert _ref(conn, a1) == "Tablou de amortizare nr 1 din 28.10.2026"
    assert (_ref(conn, n1), _ref(conn, n2)) == ("Notă de calcul nr 1 din 06.10.2026", "Notă de calcul nr 2 din 07.10.2026")
    assert _ref(conn, n3) == "Notă de calcul nr 1 din 05.01.2027"     # anul nou începe de la 1
    assert _ref(conn, i1) == "Listă de inventariere nr 1 din 08.10.2026"


def test_stocul_primeste_bon_de_consum_si_lista_de_inventariere_un_document_pe_act(conn):
    """MUTAȚIE: lista de inventariere generată pe fiecare notă (nu pe act) -> numere diferite -> pică."""
    from core import stocuri_cv_api as cv
    _metoda(conn, "cantitativ_valoric")   # ieșirile pe articol sunt ale firmei CV (§6.3)
    a = cv.intrare(conn, SCH, {"denumire": "Făină", "um": "kg", "data": "2026-10-01", "cantitate": 10, "pret_unitar": 3})
    b = cv.intrare(conn, SCH, {"denumire": "Zahăr", "um": "kg", "data": "2026-10-01", "cantitate": 5, "pret_unitar": 4})
    e1 = cv.iesire(conn, SCH, {"articol_id": a["articol_id"], "data": "2026-10-06", "cantitate": 1})
    e2 = cv.iesire(conn, SCH, {"articol_id": a["articol_id"], "data": "2026-10-06", "cantitate": 1, "document": "Bon consum hârtie 9"})
    assert _ref(conn, e1["inregistrare_id"]) == "Bon de consum nr 1 din 06.10.2026"
    assert _ref(conn, e2["inregistrare_id"]) == "Bon consum hârtie 9"
    r = cv.inventar(conn, SCH, {"data": "2026-10-31", "linii": [{"articol_id": a["articol_id"], "faptic": 7}, {"articol_id": b["articol_id"], "faptic": 6}]})
    refs = {_ref(conn, x["inregistrare_id"]) for x in r["rezultate"]}
    assert refs == {"Listă de inventariere nr 1 din 31.10.2026"}, refs


def test_descarcarea_lunii_are_o_singura_situatie_pe_toate_notele(conn):
    from core import stocuri_api as sa
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET metoda_stoc = 'global_valoric'")
        for d, c, s, sursa in (("371", "401", 1000, "stocuri"), ("371", "378", 200, "stocuri"), ("371", "4428", 252, "stocuri"),
                               ("5311", "707", 500, "horeca_z")):
            cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2026-10-05','n',%s,'validata') RETURNING id", (sursa,))
            nid = cur.fetchone()[0]
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))
    r = sa.descarca_luna(conn, SCH, 2026, 10)
    assert len(r["inregistrari"]) >= 2
    assert {_ref(conn, x) for x in r["inregistrari"]} == {"Situația de descărcare a gestiunii nr 1 din 31.10.2026"}


def test_nota_manuala_ramane_fara_document(conn):
    from core import jurnal_api as j
    r = j.creeaza(conn, SCH, "Corecție", "2026-10-06", [{"debit": "628", "credit": "401", "suma": 10}])
    assert _ref(conn, r["id"]) is None


# ── §6.3 metoda de stoc: explicită, o singură descărcare pe ieșire ──────────────────────────────────────────────────────
def _metoda(conn, m):
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET metoda_stoc = %s, serie_factura = 'ZT'", (m,))


def _vanzare(conn, sursa, suma=500):
    with conn.cursor() as cur:
        for d, c, s, src in (("371", "401", 1000, "stocuri"), ("371", "378", 200, "stocuri"), ("371", "4428", 252, "stocuri"),
                             ("4111" if sursa == "facturi" else "5311", "707", suma, sursa)):
            cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2026-10-05','n',%s,'validata') RETURNING id", (src,))
            nid = cur.fetchone()[0]
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))


def test_metoda_nedeclarata_refuza_iesirile_si_descarcarea(conn):
    """Fără implicit tăcut. MUTAȚIE: `cere` care trece pe NULL -> descărcarea rulează -> pică."""
    from core import stocuri_api as sa, stocuri_cv_api as cv
    _vanzare(conn, "horeca_z")
    assert sa.descarca_luna(conn, SCH, 2026, 10)["cod"] == "METODA_STOC_NEDECLARATA"
    a = cv.intrare(conn, SCH, {"denumire": "Făină", "data": "2026-10-01", "cantitate": 5, "pret_unitar": 3})
    with pytest.raises(ValueError) as e:
        cv.iesire(conn, SCH, {"articol_id": a["articol_id"], "data": "2026-10-06", "cantitate": 1})
    assert e.value.cod == "METODA_STOC_NEDECLARATA"


def test_global_valoric_descarca_lunar_si_factura_fara_articol(conn):
    """Cazul numit de Costin: la global-valoric, factura fără articol se descarcă — prin descărcarea lunii, singura ei
    descărcare (ieșirile pe articol sunt refuzate). MUTAȚIE: `facturi` scos din sursele vânzărilor -> „fără vânzări” -> pică."""
    from core import stocuri_api as sa, stocuri_cv_api as cv
    _metoda(conn, "global_valoric")
    _vanzare(conn, "facturi")
    r = sa.descarca_luna(conn, SCH, 2026, 10)
    assert r.get("inregistrari") and r["cmv"] != "0", r
    a = cv.intrare(conn, SCH, {"denumire": "Făină", "data": "2026-10-01", "cantitate": 5, "pret_unitar": 3})
    with pytest.raises(ValueError) as e:
        cv.iesire(conn, SCH, {"articol_id": a["articol_id"], "data": "2026-10-06", "cantitate": 1})
    assert e.value.cod == "METODA_STOC_ALTA"


def test_cantitativ_valoric_refuza_descarcarea_globala_si_linia_de_marfa_fara_articol(conn):
    """Cazul HoReCa: la cantitativ-valoric raportul Z nu mai intră în descărcarea globală (refuzată) — marfa iese prin rețete.
    MUTAȚIE: verificarea scoasă din `descarca_luna` -> descarcă Z-ul a doua oară -> pică."""
    from core import stocuri_api as sa, facturi_api as fa
    _metoda(conn, "cantitativ_valoric")
    _vanzare(conn, "horeca_z")
    assert sa.descarca_luna(conn, SCH, 2026, 10)["cod"] == "METODA_STOC_ALTA"
    linii = [{"descriere": "Făină", "cantitate": 1, "pret_unitar": 10, "cota_tva": 11, "cont_venit": "707"},
             {"descriere": "Transport", "cantitate": 1, "pret_unitar": 50, "cota_tva": 21, "cont_venit": "704"}]
    with pytest.raises(fa.LiniiIncomplete) as e:
        fa.emite_factura(conn, linii, tert_nume="Client SRL", tert_cui="14399840")
    assert [c["camp"] for c in e.value.campuri] == ["em-l0-articol"]
    r = fa.emite_factura(conn, linii, tert_nume="Client SRL", tert_cui="14399840", pleaca_marfa=False)   # „Nu, doar factură”
    assert r["numar"].startswith("ZT")


def test_factura_cu_marfa_la_metoda_nedeclarata_se_refuza_iar_serviciile_trec(conn):
    from core import facturi_api as fa
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET serie_factura = 'ZT'")
    with pytest.raises(ValueError) as e:
        fa.emite_factura(conn, [{"descriere": "Făină", "cantitate": 1, "pret_unitar": 10, "cota_tva": 11, "cont_venit": "707"}],
                         tert_nume="Client SRL", tert_cui="14399840")
    assert e.value.cod == "METODA_STOC_NEDECLARATA"
    assert fa.emite_factura(conn, LINII, tert_nume="Client SRL", tert_cui="14399840")["numar"] == "ZT4"


def test_retetele_numai_la_cantitativ_valoric(conn):
    from core import retete_api
    _metoda(conn, "global_valoric")
    with pytest.raises(ValueError) as e:
        retete_api.descarca(conn, SCH, {"reteta_id": 1, "portii": 1, "data": "2026-10-06"})
    assert e.value.cod == "METODA_STOC_ALTA"


# ── §6.4 jurnalul Date firmă ─────────────────────────────────────────────────────────────────────────────────────────────
def test_orice_camp_din_date_firma_se_jurnalizeaza_cu_cine_si_vechi_nou(conn):
    """MUTAȚIE: jurnalizarea scoasă din `salveaza_date` -> jurnal gol -> pică."""
    from core import firma_profil_api as fpa, repo_firma_profil as rfp
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.users ORDER BY id LIMIT 1")
        uid = cur.fetchone()[0]
    r = fpa.salveaza_date(conn, {"telefon": "0712345678", "forma_juridica": "SA", "capital_subscris": "90000",
                                 "capital_varsat": "90000", "metoda_stoc": "cantitativ_valoric"}, user_id=uid)
    assert r["ok"], r
    with conn.cursor() as cur:
        j = {x["camp"]: (x["vechi"], x["nou"]) for x in rfp.jurnal_firma(cur)}
    assert j == {"telefon": (None, "0712345678"), "forma_juridica": ("SRL", "SA"), "capital_subscris": ("200.00", "90000.00"),
                 "capital_varsat": (None, "90000.00"), "metoda_stoc": (None, "cantitativ_valoric")}, j
    assert fpa.salveaza_date(conn, {"telefon": "0700000000"})["ok"] is False      # fără autor nu se salvează
    assert fpa.salveaza_date(conn, {"metoda_stoc": ""}, user_id=uid)["camp"] == "metoda_stoc"   # nu se șterge
