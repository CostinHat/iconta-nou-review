# -*- coding: utf-8 -*-
"""[deficiențele 404 și 407 — retestul Costin 19.10.2026]
  404 „Inventar (lipsă 607=371 205,90): nu întreabă imputabil/neimputabil (TVA 635=4427 + nedeductibil).”
  407 „Casă: mesaj «avans plătit furnizorului» dar nota 401=5311; avansul 4091=5311; «Emite factura de avans» confuz.”
Temei:
  - HG 1/2016 titlul VII pct.78 alin.(6) lit.a: ajustarea negativă a TVA deductibile pentru „bunuri lipsă în gestiune din alte cauze
    decât cele prevăzute la art. 304 alin. (2) din Codul fiscal. În cazul bunurilor lipsă din gestiune care sunt imputate, sumele imputate
    nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA”; CF art.304 alin.(2) lit.a (bunuri distruse, pierdute,
    furate, dovedit: fără ajustare); CF art.25 alin.(4) lit.c (lipsa neimputabilă și TVA-ul ei: nedeductibile);
  - OMFP 1802/2014, funcțiunea contului 409: avansurile acordate furnizorilor (5311 ...) se înregistrează în debitul lui 409x.
Schemă efemeră din template, ștearsă la ieșire."""
import io
from decimal import Decimal

import pytest

from core import ajustari_fiscale as _aj, casa_api as _ca, db as _db, stocuri_cv_api as cv, tenant_provisioning as _tprov
from core import migrare_avans_nir_ajustare_nota as _mig

SCH = "efemer_404_407"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
        _mig.aplica(c, SCH)   # idempotentă: coloanele 404/405 (până la oglinda lor în tenant_template.sql)
        with c.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                        "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
            cur.execute("INSERT INTO produse (denumire, cota_tva, confirmat) VALUES ('Marfa A', 21, true)")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _art(conn):
    return cv.intrare(conn, SCH, {"denumire": "Marfa A", "um": "buc", "data": "2026-10-01", "cantitate": 10, "pret_unitar": 20.59})["articol_id"]


def _linii(conn, iid):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id", (iid,))
        return [(d, c, str(s)) for d, c, s in cur.fetchall()]


def test_404_lipsa_se_incadreaza_inainte_de_nota(conn):
    aid = _art(conn)
    r = cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 0}]})["rezultate"][0]
    assert r["camp"] == "cvi-a%d-lipsa" % aid and r["eroare"].startswith("Lipsa de 205.90 lei: alege dacă e imputabilă"), r


def test_404_neimputabila_ajusteaza_tva_si_spune_nedeductibilul(conn):
    aid = _art(conn)
    r = cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 0, "lipsa": "neimputabila"}]})["rezultate"][0]
    assert _linii(conn, r["inregistrare_id"]) == [("607", "371", "205.90"), ("635", "4427", "43.24")]
    assert r["semnal"]["fel"] == "fapt" and r["semnal"]["motiv"] == ("Lipsa neimputabilă: cheltuiala (205.90 lei) și TVA-ul ajustat (43.24 lei) sunt nedeductibile la impozitul pe "
                           "profit (CF art.25 alin.(4) lit.c). Suma de 249,14 lei a trecut la ajustările fiscale (Registrul de evidență "
                           "fiscală, rd.33 — alte cheltuieli nedeductibile, T4/2026); intră în D100 / D101 după validarea notei inventarului.")


def _valideaza(conn, iid):
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (iid,))


def test_404_neimputabila_trece_automat_la_ajustari_si_intra_in_calcul_numai_cu_nota_validata(conn):
    """[404, decizia Costin „Da, automat”] CF art.25 alin.(4) lit.c: nedeductibile „cheltuielile privind bunurile de natura stocurilor [...]
    constatate lipsă din gestiune [...], neimputabile, precum și taxa pe valoarea adăugată aferentă” -> rândul 33 D101 (OPANAF 206/2025:
    „cheltuielile prevăzute la art. 25 alin. (4) [...], cu excepţia celor menţionate la lit. a), b), e) şi i)”)."""
    aid = _art(conn)
    r = cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 0, "lipsa": "neimputabila"}]})["rezultate"][0]
    assert r["ajustare_fiscala"]["rand"] == "P33" and r["ajustare_fiscala"]["trim"] == 4, r
    with conn.cursor() as cur:
        lst = _aj.lista(cur, SCH, 2026)
        assert [(a["rand"], a["trim"], a["suma"], a["automata"], a["in_calcul"]) for a in lst] == [("P33", 4, "249.14", True, False)], lst
        assert lst[0]["descriere"] == ("Lipsă neimputabilă la inventarul din 19.10.2026 — Marfa A: cheltuiala 205,90 lei + TVA ajustat "
                                       "43,24 lei (CF art.25 alin.(4) lit.c)") and lst[0]["document"] == "Inventarul din 19.10.2026", lst
        assert _aj.cumulat(cur, SCH, 2026, 4) == {}                 # nota inventarului e ciornă: impozitul nu se mută încă
    _valideaza(conn, r["inregistrare_id"])
    with conn.cursor() as cur:
        assert _aj.cumulat(cur, SCH, 2026, 4) == {"P33": Decimal("249.14")}   # 205,90 + 43,24: cheltuiala + TVA-ul aferent (lit.c)
        assert _aj.cumulat(cur, SCH, 2026, 3) == {}                          # trimestrul inventarului (T4), nu înainte
        assert _aj.lista(cur, SCH, 2026)[0]["in_calcul"] is True


def test_404_stergerea_notei_inventarului_nu_lasa_ajustarea_orfana(conn):
    aid = _art(conn)
    r = cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 0, "lipsa": "neimputabila"}]})["rezultate"][0]
    with conn.cursor() as cur:
        cur.execute("DELETE FROM miscari_stoc WHERE inregistrare_id = %s", (r["inregistrare_id"],))
        cur.execute("DELETE FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
        assert _aj.lista(cur, SCH, 2026) == []


def test_404_imputabila_justificata_si_micro_nu_scriu_ajustari(conn):
    aid = _art(conn)
    cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 9, "lipsa": "imputabila", "suma_imputata": 30}]})
    cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 8, "lipsa": "justificata"}]})
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET regim_fiscal = 'micro' WHERE id = 1")
    r = cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 7, "lipsa": "neimputabila"}]})["rezultate"][0]
    assert "ajustare_fiscala" not in r and r["semnal"]["motiv"].endswith(
        "Firma e microîntreprindere: nu plătește impozit pe profit, deci lipsa nu trece la ajustările fiscale."), r
    with conn.cursor() as cur:
        assert _aj.lista(cur, SCH, 2026) == []


def test_404_imputabila_si_justificata(conn):
    aid = _art(conn)
    r = cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 5, "lipsa": "imputabila"}]})["rezultate"][0]
    assert r["camp"] == "cvi-a%d-imputat" % aid, r                       # suma imputată se cere
    r = cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 5, "lipsa": "imputabila",
                                                                 "suma_imputata": 120}]})["rezultate"][0]
    assert _linii(conn, r["inregistrare_id"]) == [("607", "371", "102.95"), ("635", "4427", "21.62"), ("4282", "7581", "120.00")]
    r = cv.inventar(conn, SCH, {"data": "2026-10-19", "linii": [{"articol_id": aid, "faptic": 4, "lipsa": "justificata"}]})["rezultate"][0]
    assert _linii(conn, r["inregistrare_id"]) == [("607", "371", "20.59")]   # art.304 alin.(2): fără ajustarea TVA


def _op(cat, suma, **x):
    return {"data": "2026-10-19", "categorie": cat, "suma": suma, "document": "DP1", "partener": "DANTE INTERNATIONAL SA",
            "cui": "14399840", **x}


def test_407_avansul_acordat_furnizorului_e_409x_si_mesajul_nu_cere_firmei_factura(conn):
    _ca.adauga(conn, SCH, _op("ridicare_banca", 1000))
    r = _ca.adauga(conn, SCH, _op("plata_furnizor", 300))   # niciun furnizor cu facturi deschise: totul e avans
    assert r["cod"] == _ca.COD_AVANS_DESTINATIE and r["erori_campuri"][0]["camp"] == "c-avans-dest", r
    r = _ca.adauga(conn, SCH, _op("plata_furnizor", 300, avans_destinatie="stocuri"))
    assert r.get("eroare") is None and r["nota"] == "4091=5311", r
    assert r["avans"]["mesaj"].startswith("300,00 lei depășesc facturile deschise ale furnizorului: sunt avans acordat furnizorului, cu "
                                          "nota 409x = 5311") and "Emite factura" not in r["avans"]["mesaj"], r["avans"]
    reg = _ca.registru(conn, SCH, 2026, 10)
    assert [o["se_leaga"] for o in reg["operatiuni"] if o["categorie"] == "plata_furnizor"] == [False]


def test_404_d100_pe_profit_ia_lipsa_neimputabila_ca_nedeductibila_dupa_validare(conn):
    """Capăt la capăt pe calculul impozitului: D100 T3 (`d100._impozit_cumulat`, aceeași aritmetică cu D101). Vânzări 10.000 lei; lipsa
    neimputabilă din 19.08.2026 (607 = 205,90 + 635 = 43,24) e cheltuială în contabilitate, dar nedeductibilă (CF art.25 alin.(4) lit.c):
    cu nota validată, rd.33 = 249 și impozitul rămâne 16% din 10.000 = 1.600 (fără ajustare ar fi ieșit 16% din 9.750,86 = 1.560)."""
    from core import d100
    aid = cv.intrare(conn, SCH, {"denumire": "Marfa A", "um": "buc", "data": "2026-08-01", "cantitate": 10, "pret_unitar": 20.59})["articol_id"]
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET regim_fiscal = 'profit' WHERE id = 1")
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2026-08-10', 'Vânzări', 'manual', 'validata') RETURNING id")
        vid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5311', '704', 10000)", (vid,))
    r = cv.inventar(conn, SCH, {"data": "2026-08-19", "linii": [{"articol_id": aid, "faptic": 0, "lipsa": "neimputabila"}]})["rezultate"][0]
    inainte = d100._impozit_cumulat(conn, SCH, 2026, 3)       # nota inventarului în ciornă: nici cheltuiala, nici ajustarea
    _valideaza(conn, r["inregistrare_id"])
    dupa = d100._impozit_cumulat(conn, SCH, 2026, 3)
    print("INAINTE P2=%s P33=%s impozit=%s | DUPA P2=%s P33=%s P34=%s impozit=%s" % (
        inainte["P"].get("P2"), inainte["P"].get("P33"), inainte["impozit"], dupa["P"].get("P2"), dupa["P"].get("P33"),
        dupa["P"].get("P34"), dupa["impozit"]))
    assert not inainte["P"].get("P33") and inainte["impozit"] == 1600, inainte
    assert dupa["ajustari"] == {"P33": Decimal("249.14")} and dupa["P"]["P33"] == 249, dupa   # rândurile D101: lei întregi
    assert dupa["P"]["P2"] == 249 and dupa["impozit"] == 1600, dupa["P"]   # cheltuiala dedusă contabil, adăugată înapoi fiscal
