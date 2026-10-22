# -*- coding: utf-8 -*-
"""Lotul 11, deficiența 443 (comanda Costin 11.1 pct.19, verbatim): „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61).”
Subagentul W1, listele U0 `u0_lista_jurnal_api.md` și `u0_lista_alte_py_443.md` (fără casa_api — W3a).

Cauza: textele pentru om (documentul notei în Registrul jurnal, „stinge factura …”, nota derivată, ordinul de compensare, titlul PDF-ului
chitanței, „contravaloare factura …” de pe chitanță) compuneau numărul cu `pdf_util.numar_cu_serie` sau de mână (`serie + numar`), care
lipea seria de număr: „F6” + „1” = „F61” (ambiguu cu seria „F”, nr. 61). Acum trec prin `pdf_util.serie_nr` („F6 nr. 1”). Lista Istoric
(`facturi_api.lista_facturi`) aduce și `serie`, ca ecranul să le afișeze separat.

Temei: N/A — regulă de afișare (DS cap.4 v2.99). Forma „Seria X nr. Y” de pe factură: CF art.319 alin.(20) lit.a) („un număr secvențial,
bazat pe una sau mai multe serii, care identifică factura în mod unic”), `factura_pdf.serie_si_numar`.

CE FACE IMPOSIBIL: „F61” în locul lui „F6 nr. 1” în textele de mai sus (garda de clasă statică e `core/test_lot11_u0_serie_nr.py`).
"""
import datetime

import pytest

from core import db as _db, jurnal_api as _j, tenant_provisioning as _tp

ZI = datetime.date(2026, 10, 5)
_SCHEMA = "test_lot11_w1_443"


def test_documentul_notei_si_stinge_spun_f6_nr_1():
    """MUTAȚIE: `pdf_util.numar_cu_serie` repus în `eticheta_factura` -> „Factură F61 din …” -> pică."""
    assert _j.eticheta_factura("factura", "F6", "F61", ZI) == "Factură F6 nr. 1 din 05.10.2026"          # 443: „F6 nr. 1, nu F61”
    assert _j.eticheta_factura("factura", "F6", "1", ZI) == "Factură F6 nr. 1 din 05.10.2026"
    assert _j.document_justificativ(None, "factura", "F6", "F61", ZI) == "Factură F6 nr. 1 din 05.10.2026"
    assert _j.eticheta_factura("borderou", None, "BA-1", ZI) == "Borderou de achiziție BA-1 din 05.10.2026"   # fără serie: neschimbat
    # „stinge factura …” (chitanța în Registrul jurnal, `facturi_stinse`)
    assert _j.eticheta_factura_in_text("factura", "F6", "F61", ZI) == "factura F6 nr. 1 din 05.10.2026"


def test_pdf_ul_facturii_are_o_singura_sursa_pentru_serie_si_numar():
    """`factura_pdf.serie_si_numar` dubla logica de separare: acum cheamă `serie_nr`. MUTAȚIE: corpul vechi (`numar.startswith(serie)`,
    sensibil la majuscule, separatorul nețăiat) -> „Seria KAI- nr. 12” -> pică."""
    from core.factura_pdf import serie_si_numar
    assert serie_si_numar("FCT", "FCT12") == "Seria FCT nr. 12"     # CF art.319 alin.(20) lit.a): seria + numărul secvențial
    assert serie_si_numar("FCT", "12") == "Seria FCT nr. 12"
    assert serie_si_numar("F6", "F61") == "Seria F6 nr. 1"
    assert serie_si_numar("KAI-", "KAI-12") == "Seria KAI nr. 12"
    assert serie_si_numar(None, "A-77") == "Nr. A-77"
    assert serie_si_numar("FCT", None) == "Seria FCT nr. -"


def test_avertismentul_d394_numeste_facturile_excluse():
    """440 în D394: „N facturi excluse din declarație (vezi mai sus)” trimitea la alt text. Acum le numește. MUTAȚIE: textul vechi
    repus -> pică (și garda `test_textele_din_core_nu_trimit_la_mai_sus`)."""
    from decimal import Decimal
    from core.common import Perioada
    from core.d394 import calcul_d394
    from core.test_d394 import PROF

    def f(doc, cota):
        return {"cui": "RO14399840", "nume": "P", "directie": "emisa", "cota": cota, "baza": Decimal("100"), "tva": Decimal("7"),
                "taxare_inversa": False, "categorie_331": None, "judet": "B", "document": doc}
    res = calcul_d394(PROF, Perioada(2026, luna=6), {"facturi": [f("FX7", 7), f("FX8", 3), f("FX7", 7)], "serii": {}})
    # lista întreagă a avertismentelor (nu „fragmentul apare / nu apare” într-unul din ele — core/test_garzi_pe_text.py): rezumatul
    # le numește pe facturile excluse și nu trimite „mai sus”; o listă goală ar pica aici, nu ar trece
    ignorata = "Cotă TVA %d nedeclarabilă (acceptate: 0, 5, 9, 11, 19, 20, 21, 24) — factură ignorată."
    assert res.avertismente == [ignorata % 7, ignorata % 3, ignorata % 7,
                                "2 facturi excluse din declarație, fiindcă au o cotă de TVA pe care D394 n-o primește: FX7, FX8."], \
        res.avertismente


# ── pe o schemă efemeră din tenant_template ─────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
            cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)   # pe tranzacție (core/test_lot10_search_path_pool.py)
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_istoricul_aduce_seria_si_nota_derivata_spune_f6_nr_1(conn):
    """`lista_facturi` aduce `serie` (Istoric: „F6 nr. 1”, `numarCuSerie`); nota legată de factură spune documentul cu seria separat.
    MUTAȚIE: `serie, ` scos din SELECT-ul `lista_facturi` -> `KeyError` / None -> pică; `numar_cu_serie` repus în
    `note_derivate.documentul_sursa` -> „F61 din …” -> pică."""
    from core import facturi_api as fa, note_derivate as nd
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva) VALUES ('F61', 'F6', %s, 'emisa', 121, 21) "
                    "RETURNING id", (ZI,))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, factura_id) VALUES (%s, 'Factura F6', 'facturi', 'ciorna', %s) "
                    "RETURNING id", (ZI, fid))
        nid = cur.fetchone()[0]
    rand = [x for x in fa.lista_facturi(conn) if x["id"] == fid][0]
    assert (rand["serie"], rand["numar"]) == ("F6", "F61"), rand
    with conn.cursor() as cur:
        doc = nd.documentul_sursa(cur, _SCHEMA, nid)
    assert doc == ("factura", "F6 nr. 1 din 05.10.2026", "din 05.10.2026"), doc   # documentul cu seria separat, nu „F61 din …”
