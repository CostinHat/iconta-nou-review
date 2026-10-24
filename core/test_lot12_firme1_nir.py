# -*- coding: utf-8 -*-
"""Lotul 12, pachetul firme1 — NIR: 476 (grav).

476 (Costin, comanda 12.1): „NIR: TVA transport cu factură pe 4428 în loc de 4426 (grav).” TVA-ul transportului lua contul TVA-ului
MĂRFII: la NIR-ul fără factură al mărfii (371 = 408, TVA 4428.01 = 408), transportul facturat de transportator (datoria pe 401) ieșea
4428.01 = 401 — neexigibil, deși factura transportului există, și rămânea acolo (legarea facturii mărfii mută numai 4428.01 = 408).
Temei (citit la sursă, `anaf_surse/`):
  CF art.299 alin.(1) lit.a — „Pentru exercitarea dreptului de deducere a taxei, persoana impozabilă trebuie să îndeplinească următoarele
    condiții: a) [...] să dețină o factură emisă în conformitate cu prevederile art. 319”;
  OMFP 1802/2014, funcțiunea contului 4426 — „În debitul contului 4426 «Taxa pe valoarea adăugată deductibilă» se înregistrează: – sumele
    reprezentând taxa pe valoarea adăugată deductibilă potrivit legii (401, 404, 451, 453, 512 ...)”;
  OMFP 1802/2014, funcțiunea contului 408 — „În creditul contului 408 «Furnizori - facturi nesosite» se înregistrează: – valoarea bunurilor
    aprovizionate sau a serviciilor prestate de către furnizori [...] (301, 302, 303, 361, 371, 381, 4428, ...)” — 4428 numai pentru ce n-are
    încă factură.
Schemă efemeră din template, ștearsă la ieșire.
"""
import io
from decimal import Decimal

import pytest

from core import db as _db, stocuri as _m, stocuri_api as _s, tenant_provisioning as _tprov

SCH = "efemer_l12_firme1_nir"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


db_necesar = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _fixture(metoda):
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            # CUI 14399840 (DANTE INTERNATIONAL SA) — cifra de control verificată
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                        "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, %s)", (metoda,))
        c.commit()


def _sterge():
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


@pytest.fixture()
def conn_cv():
    _fixture("cantitativ_valoric")
    with _db.get_conn(SCH) as c:
        yield c
    _sterge()


@pytest.fixture()
def conn_gv():
    _fixture("global_valoric")
    with _db.get_conn(SCH) as c:
        yield c
    _sterge()


def _note(conn, ids):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = ANY(%s) ORDER BY id", (ids,))
        return [(d, c, str(s)) for d, c, s in cur.fetchall()]


def test_476_contul_tva_transportului_urmeaza_datoria_transportului():
    assert _m.cont_tva_transport("401", "4428.01") == "4426", "transportul cu factură (401): TVA deductibil — CF art.299 alin.(1) lit.a"
    assert _m.cont_tva_transport("408", "4428.01") == "4428.01", "transportul fără factură (408): TVA neexigibil până la factură"
    assert _m.cont_tva_transport("408", "4426") == "4428.01", "marfa cu factură, transportul fără: TVA-ul transportului tot neexigibil"
    assert _m.cont_tva_transport("401.02", "4428.01") == "4426"
    assert _m.cont_tva_transport("", "4426") == "4426"


def test_476_motorul_scrie_tva_transportului_facturat_pe_4426():
    """Marfa fără factură (408), transportul de 100 lei cu factura transportatorului (401), cota 21%: 4426 = 401 21,00 (înainte
    4428.01 = 401 21,00). La amândouă metodele."""
    l = [{"denumire": "Marfa A", "cantitate": 10, "pret_achizitie": 50, "cota_tva": 21, "pret_vanzare": 121}]
    for motor in (_m.nir_cost, _m.nir_gv):
        r = motor(l, transport=100, cont_transport="401", cont_furnizor="408", cont_tva="4428.01", cota_tva_transport=21)
        tr = [(n["debit"], n["credit"], n["suma"]) for n in r["note"] if n["credit"] == "401"]
        assert tr == [("371", "401", Decimal("100.00")), ("4426", "401", Decimal("21.00"))], (motor.__name__, tr)
        assert ("4428.01", "408", Decimal("105.00")) in [(n["debit"], n["credit"], n["suma"]) for n in r["note"]], "marfa: neschimbată"


@db_necesar
def test_476_nir_fara_factura_cu_transport_facturat(conn_cv):
    """Drumul ecranului (Stocuri -> NIR, `stocuri_api.adauga_nir`): factura mărfii nesosită, transport 100 lei, cota 21%, contul
    transportului 401 (factura transportatorului). Notele NIR-ului, cifrele exacte."""
    r = _s.adauga_nir(conn_cv, SCH, {"numar": "476", "data": "2026-10-19", "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840",
                                     "linii": [{"denumire": "Marfa 476", "articol_nou": True, "cantitate": 10, "pret_achizitie": 50,
                                                "cota_tva": 21}],
                                     "transport": 100, "cota_tva_transport": 21, "cont_transport": "401", "factura_sosita": False},
                      cere_decizia=True)
    assert "eroare" not in r, r
    assert _note(conn_cv, r["inregistrari"]) == [("371", "408", "500.00"), ("4428.01", "408", "105.00"), ("371", "401", "100.00"),
                                                 ("4426", "401", "21.00")]


@db_necesar
def test_476_migrarea_muta_ciorna_si_corecteaza_nota_validata(conn_gv):
    """Datele existente: NIR-ul scris înainte de reparație, cu 4428.01 = 401 pe transport. Ciorna: rândul trece pe 4426. Nota validată:
    nu se atinge; o ciornă de corectură 4426 = 4428.01 cu suma, data NIR-ului și NIR-ul ca document. A doua rulare: nimic nou."""
    import json
    from core import migrare_nir_tva_transport as mig
    with conn_gv.cursor() as cur:
        ids = []
        for st in ("ciorna", "validata"):
            cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES ('2026-09-15', 'NIR', 'stocuri', "
                        "'ciorna', 'NIR nr 9 din 15.09.2026') RETURNING id")
            iid = cur.fetchone()[0]
            for d, c, s in (("371", "408", 500), ("4428.01", "408", 105), ("371", "401", 100), ("4428.01", "401", 21)):
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (iid, d, c, s))
            if st == "validata":
                cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (iid,))
            ids.append(iid)
        for k, iid in enumerate(ids):
            cur.execute("INSERT INTO nir (numar, data, furnizor, cost_total, transport, taxe, inregistrari_ids, metoda_stoc) "
                        "VALUES (%s, '2026-09-15', 'F', 600, 100, 0, %s, 'global_valoric')", (str(9 + k), json.dumps([iid])))
    conn_gv.commit()
    assert mig.verifica(conn_gv, SCH) is False
    assert mig.aplica(conn_gv, SCH) == {"ciorne": 1, "corecturi": 1, "blocate": []}
    conn_gv.commit()
    assert _note(conn_gv, [ids[0]]) == [("371", "408", "500.00"), ("4428.01", "408", "105.00"), ("371", "401", "100.00"),
                                        ("4426", "401", "21.00")]
    assert _note(conn_gv, [ids[1]])[-1] == ("4428.01", "401", "21.00"), "nota validată nu se modifică (OMFP 1802/2014 pct.69)"
    with conn_gv.cursor() as cur:
        cur.execute("SELECT id, data::text, status, document_ref FROM inregistrari WHERE descriere LIKE %s", (mig.MARCAJ + "%",))
        (cid, data, st, doc), = cur.fetchall()
    assert (data, st, doc) == ("2026-09-15", "ciorna", "NIR nr 10 din 15.09.2026")
    assert _note(conn_gv, [cid]) == [("4426", "4428.01", "21.00")]
    assert mig.verifica(conn_gv, SCH) is True
    assert mig.aplica(conn_gv, SCH) == {"ciorne": 0, "corecturi": 0, "blocate": []}


@db_necesar
def test_476_migrarea_nu_scrie_in_luna_blocata(conn_gv):
    import json
    from core import migrare_nir_tva_transport as mig
    with conn_gv.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES ('2026-08-15', 'NIR', 'stocuri', "
                    "'ciorna', 'NIR nr 8') RETURNING id")
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'4428.01','401',21)", (iid,))
        cur.execute("INSERT INTO nir (numar, data, furnizor, cost_total, transport, taxe, inregistrari_ids, metoda_stoc) "
                    "VALUES ('8', '2026-08-15', 'F', 600, 100, 0, %s, 'global_valoric')", (json.dumps([iid]),))
        cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2026, 8)")
    conn_gv.commit()
    r = mig.aplica(conn_gv, SCH)
    assert (r["ciorne"], r["corecturi"], [n for n, _m in r["blocate"]]) == (0, 0, ["8"]), r
    assert "PERIOADA_BLOCATA" in r["blocate"][0][1]
