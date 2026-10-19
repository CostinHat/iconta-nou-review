# -*- coding: utf-8 -*-
"""[deficiența 405 — retestul Costin 19.10.2026] „Casă plată DANTE: «Nicio factură primită neplătită» deși NIR 1, 2, 3 neplătite; datoriile din
NIR (408/401) nu sunt oferite.” Decizia Costin (19.10.2026, verbatim în DECIZII „Închiderea lotului 9”): „Avans 409x = 5311” — plata fără
factură e avans acordat furnizorului; la sosirea facturii se compensează (401 = 409x).

Temei (citit la sursă, `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`):
  - OMFP 1802/2014, funcțiunea contului 408: „Cu ajutorul acestui cont se ține evidența decontărilor cu furnizorii pentru aprovizionările de
    bunuri și prestările de servicii, pentru care nu s-au primit facturi. [...] În debitul contului 408 «Furnizori - facturi nesosite» se
    înregistrează: – valoarea facturilor sosite (401)” — 408 nu se debitează pe plată, ci numai la factură (408 = 401);
  - OMFP 1802/2014, funcțiunea contului 409: „Cu ajutorul acestui cont se ține evidența avansurilor acordate furnizorilor pentru cumpărări de
    bunuri de natura stocurilor [...]. În debitul contului 409 «Furnizori - debitori» se înregistrează: – valoarea avansurilor acordate (401,
    404); [...] În creditul contului 409 «Furnizori - debitori» se înregistrează: – valoarea avansurilor acordate furnizorilor, cu ocazia
    regularizării plăților cu aceștia (401, 404)”. INTERPRETARE CU TEMEI: 4091 = 5311 e forma prescurtată (decizia Costin) a 4091 = 401 +
    401 = 5311; compensarea la factură e creditul lui 409 „cu ocazia regularizării plăților” (401 = 4091).
Schemă efemeră din template, ștearsă la ieșire. CUI 14399840 (DANTE INTERNATIONAL SA): cifra de control verificată (algoritmul din CLAUDE.md)."""
import io
from decimal import Decimal

import pytest

from core import casa_api as _ca, db as _db, migrare_avans_nir_ajustare_nota as _mig, stocuri_api as _s, tenant_provisioning as _tprov

SCH = "efemer_405_nir"
CUI = "14399840"


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
        _mig.aplica(c, SCH)   # idempotentă: `casa_operatiuni.nir_id` (până la oglinda ei în tenant_template.sql)
        with c.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                        "VALUES (1, 'F1 SRL', '18547290', true, 'SRL', 200, 'cantitativ_valoric')")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _nir(conn, numar, cui=CUI):
    """NIR fără factură (408): 2 buc × 25 lei, 21% -> 371 = 408 50,00 și 4428.01 = 408 10,50: datoria 60,50."""
    r = _s.adauga_nir(conn, SCH, {"numar": numar, "data": "2026-10-19", "furnizor": "DANTE INTERNATIONAL SA", "cui": cui,
                                  "linii": [{"denumire": "Marfa NIR %s" % numar, "articol_nou": True, "cantitate": 2, "pret_achizitie": 25, "cota_tva": 21}]})
    assert "eroare" not in r, r
    return r["id"]


def _op(suma, **x):
    return {"data": "2026-10-19", "categorie": "plata_furnizor", "suma": suma, "document": "DP405", "partener": "DANTE INTERNATIONAL SA",
            "cui": CUI, **x}


def _linii(conn, iid):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id", (iid,))
        return [(d, c, str(s)) for d, c, s in cur.fetchall()]


def _numerar(conn):
    assert _ca.adauga(conn, SCH, {"data": "2026-10-19", "categorie": "ridicare_banca", "suma": 1000, "document": "CEC1"}).get("eroare") is None


def test_405_nirul_fara_factura_e_oferit_la_plata_cu_suma_si_numele_lui(conn):
    n1, n2 = _nir(conn, "1"), _nir(conn, "2")
    _nir(conn, "9", cui="18547290")                                     # alt furnizor: nu e al lui DANTE
    p = _ca.previzualizare(conn, SCH, _op(60.50))
    assert [(n["id"], n["eticheta"], n["rest"]) for n in p["niruri"]] == [
        (n1, "NIR nr 1 din 19.10.2026", "60.50"), (n2, "NIR nr 2 din 19.10.2026", "60.50")], p["niruri"]
    assert p["facturi"] == []
    # fără NIR ales, semnalul spune că există și ce înseamnă plata lui
    assert ("Furnizorul are 2 NIR-uri fără factură neplătite (de 121,00 lei, marfa pe 408). Dacă dispoziția plătește unul, alege NIR-ul: "
            "plata lui e avans acordat furnizorului (4091 = 5311), compensat la sosirea facturii (401 = 4091).") in p["semnale"], p["semnale"]


def test_405_plata_nirului_e_avans_4091_legat_de_nir_si_nirul_platit_nu_se_mai_ofera(conn):
    n1 = _nir(conn, "1")
    _numerar(conn)
    r = _ca.adauga(conn, SCH, _op(60.50, niruri=[{"nir_id": n1, "suma": "60.50"}]))   # fără destinație: NIR-ul o dă (bunuri)
    assert r.get("eroare") is None and r["nota"] == "4091=5311" and r["operatiuni"][0]["nir_id"] == n1, r
    assert _linii(conn, r["inregistrare_id"]) == [("4091", "5311", "60.50")]
    assert r["avans"] is None, r                                          # nimic peste NIR: niciun avans „nealocat”
    with conn.cursor() as cur:
        cur.execute("SELECT descriere FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
        assert cur.fetchone()[0] == ("Plată către furnizor — document DP405 — avans pentru NIR nr 1 din 19.10.2026 (factura nesosită) — "
                                     "DANTE INTERNATIONAL SA")
    assert _ca.previzualizare(conn, SCH, _op(10))["niruri"] == []          # plătit integral: nu se mai oferă
    reg = [o for o in _ca.registru(conn, SCH, 2026, 10)["operatiuni"] if o["categorie"] == "plata_furnizor"]
    assert [(o["nir"], o["avans"], o["se_leaga"]) for o in reg] == [("NIR nr 1 din 19.10.2026", True, False)], reg


def test_405_plata_partiala_si_restul_peste_nir(conn):
    n1 = _nir(conn, "1")
    _numerar(conn)
    r = _ca.adauga(conn, SCH, _op(20, niruri=[{"nir_id": n1, "suma": "20"}]))
    assert r["nota"] == "4091=5311", r
    assert [n["rest"] for n in _ca.previzualizare(conn, SCH, _op(1))["niruri"]] == ["40.50"]     # 60,50 − 20
    r = _ca.adauga(conn, SCH, _op(50, niruri=[{"nir_id": n1, "suma": "50"}]))
    assert r["cod"] == _ca.COD_PESTE_SOLD and r.get("id") is None, r                     # refuzat, nimic scris
    assert [n["rest"] for n in _ca.previzualizare(conn, SCH, _op(1))["niruri"]] == ["40.50"]
    # 50 lei, 40,50 pe NIR, restul de 9,50: avans fără document, cu destinația cerută (407)
    r = _ca.adauga(conn, SCH, _op(50, niruri=[{"nir_id": n1, "suma": "40.50"}]))
    assert r["cod"] == _ca.COD_AVANS_DESTINATIE, r
    r = _ca.adauga(conn, SCH, _op(50, niruri=[{"nir_id": n1, "suma": "40.50"}], avans_destinatie="servicii"))
    assert [(o["nota"], o["suma"], o["nir_id"]) for o in r["operatiuni"]] == [("4091=5311", "40.50", n1), ("4092=5311", "9.50", None)], r
    assert r["avans"]["mesaj"].startswith("9,50 lei depășesc facturile și NIR-urile alese ale furnizorului"), r["avans"]


def test_405_nirul_legat_de_factura_sau_refuzat_nu_se_plateste_ca_nir(conn):
    n1 = _nir(conn, "1")
    r = _ca.adauga(conn, SCH, _op(10, niruri=[{"nir_id": n1 + 99, "suma": "10"}]))
    assert r["cod"] == _ca.COD_NIR_NEPOTRIVIT, r
    r = _ca.adauga(conn, SCH, dict(_op(10, niruri=[{"nir_id": n1, "suma": "10"}]), categorie="incasare_client"))
    assert r["cod"] == _ca.COD_FARA_FACTURI, r


def test_405_stornarea_platii_nirului_il_face_din_nou_neplatit(conn):
    n1 = _nir(conn, "1")
    _numerar(conn)
    r = _ca.adauga(conn, SCH, _op(60.50, niruri=[{"nir_id": n1, "suma": "60.50"}]))
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (r["inregistrare_id"],))
    s = _ca.storneaza(conn, SCH, r["id"], "2026-10-20")
    assert s.get("eroare") is None, s
    assert [n["rest"] for n in _ca.previzualizare(conn, SCH, _op(1))["niruri"]] == ["60.50"]


def _factura(conn, total_net=50):
    from core import facturi_api as fa
    return fa.creeaza_factura(conn, "FP405", "2026-10-25", "primita",
                              [{"descriere": "Marfa NIR 1", "cantitate": 2, "pret_unitar": total_net / 2, "cota_tva": 21}],
                              tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO" + CUI)["factura_id"]


def _conteaza(conn, fid, nir_legat):
    from core import contare_facturi as cf
    with cf.cursor_dict(conn) as cur:
        return cf.contabilizeaza(cur, SCH, fid, automat=False, nir_legat=nir_legat)


def test_405_compensarea_la_factura_e_401_4091_cel_mult_cat_datoreaza_factura(conn):
    """Contractul funcției pe care `contare_facturi.contabilizeaza` o cheamă după `nir_legare.note_factura_legata`."""
    from core import contare_facturi as cf
    n1 = _nir(conn, "1")
    _numerar(conn)
    _ca.adauga(conn, SCH, _op(60.50, niruri=[{"nir_id": n1, "suma": "60.50"}]))
    note = [{"debit": "408", "credit": "401", "suma": Decimal("60.50")}, {"debit": "4426", "credit": "4428.01", "suma": Decimal("10.50")}]
    with cf.cursor_dict(conn) as cur:
        assert _ca.compensare_avans_nir(cur, SCH, n1, note) == [{"debit": "401", "credit": "4091", "suma": Decimal("60.50")}]
        # factura mai mică decât avansul: se compensează cât datorează ea, restul avansului rămâne pe 4091
        assert _ca.compensare_avans_nir(cur, SCH, n1, [{"debit": "408", "credit": "401", "suma": Decimal("40")}]) == [
            {"debit": "401", "credit": "4091", "suma": Decimal("40.00")}]
    with conn.cursor() as cur:   # fără plată pe NIR: nimic de compensat
        assert _ca.compensare_avans_nir(cur, SCH, _nir(conn, "2"), note) == []


def test_405_la_sosirea_facturii_avansul_nirului_se_compenseaza_si_factura_nu_mai_e_de_plata(conn):
    """Capăt la capăt, pe drumul real: NIR 1 plătit în numerar (4091 = 5311, 60,50) -> factura FP405 (50 + 10,50 TVA) contată legată de NIR 1
    -> nota facturii: 408 = 401 60,50, 4426 = 4428.01 10,50 ȘI 401 = 4091 60,50 -> 4091 și 401 închise, iar factura nu mai e oferită la plată.
    Cere apelul `casa_api.compensare_avans_nir` în `contare_facturi.contabilizeaza` (după `nir_legare.note_factura_legata`)."""
    n1 = _nir(conn, "1")
    _numerar(conn)
    _ca.adauga(conn, SCH, _op(60.50, niruri=[{"nir_id": n1, "suma": "60.50"}]))
    fid = _factura(conn)
    r = _conteaza(conn, fid, n1)
    linii = [(x["debit"], x["credit"], x["suma"]) for x in r["linii"]]
    assert ("401", "4091", "60.50") in linii and ("408", "401", "60.50") in linii, linii
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(CASE WHEN cont_debit = '4091' THEN suma ELSE -suma END), 0) FROM inregistrari_linii "
                    "WHERE '4091' IN (cont_debit, cont_credit)")
        assert cur.fetchone()[0] == 0                                      # avansul compensat integral
    assert [f["id"] for f in _ca.facturi_partener(conn, SCH, "plata_furnizor", CUI)] == []   # factura e plătită prin compensare
