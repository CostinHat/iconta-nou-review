# -*- coding: utf-8 -*-
"""[deficiența C63, găsită de Code 19.10.2026] Factura născută dintr-o proformă / un aviz („Transformă în factură”) pierdea ce scrisese
omul pe document: adresa beneficiarului, localitatea și județul, tipul operațiunii, plătitorul de TVA, iar pe linii unitatea de măsură
(„buc”) și contul de venit.

Temei: CF art.319 alin.(20) lit.f (anaf_surse/cod_fiscal_227_2015_consolidat.txt:8061): factura cuprinde „denumirea/numele și adresa
beneficiarului bunurilor sau serviciilor”; lit.h: „denumirea și cantitatea bunurilor livrate, denumirea serviciilor prestate”; în
e-Factura, eFactura regula BR-RO-110 (județul clientului român). Schemă efemeră din template (fixtura lui 417), tranzacție anulată."""
import pytest

from core import facturi_api, uc_tenants
from core.test_417_storno_trimitere import _db_ok, conn  # noqa: F401 — fixtura schemei efemere

_LINIE = {"descriere": "Consultanta C63", "cantitate": 3, "um": "ora", "pret_unitar": 100, "cota_tva": 21, "cont_venit": "704"}
_CLIENT = {"tert_nume": "DANTE INTERNATIONAL SA", "tert_cui": "RO14399840", "tert_adresa": "Str. Gara Herastrau 6",
           "tert_oras": "Sector 2", "tert_judet": "B", "tert_tara": "RO"}


def _transforma(conn, **extra):
    p = facturi_api.emite_factura(conn, [dict(_LINIE)], tip="proforma", platitor_tva=True, **dict(_CLIENT, **extra))
    f = facturi_api.detalii_factura(conn, p["factura_id"])
    r = facturi_api.emite_factura(conn, uc_tenants.linii_din_proforma(f["linii"]), platitor_tva=True, **uc_tenants.antet_din_proforma(f))
    return f, facturi_api.detalii_factura(conn, r["factura_id"])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c63_factura_din_proforma_pastreaza_beneficiarul_si_operatiunea(conn):
    """MUTAȚIE: `tert_adresa` scos din `uc_tenants.antet_din_proforma` -> adresa None pe factură -> pică."""
    p, f = _transforma(conn)
    campuri = ("tert_nume", "tert_cui", "tert_adresa", "tert_oras", "tert_judet", "tert_tara", "tip_operatiune", "moneda",
               "tert_platitor_tva")
    assert (f["tip"], f["directie"]) == ("factura", "emisa"), f
    assert {k: f[k] for k in campuri} == {k: p[k] for k in campuri}, ({k: f[k] for k in campuri}, {k: p[k] for k in campuri})
    assert (f["tert_adresa"], f["tert_oras"], f["tert_judet"]) == ("Str. Gara Herastrau 6", "Sector 2", "B"), f


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c63_liniile_pastreaza_unitatea_si_contul_de_venit(conn):
    """MUTAȚIE: `um` scos din `uc_tenants.linii_din_proforma` -> „buc” pe factură -> pică."""
    p, f = _transforma(conn)
    ce = lambda x: [(l["descriere"], float(l["cantitate"]), l["um"], l["cont_venit"]) for l in x["linii"]]  # noqa: E731
    assert ce(f) == ce(p) == [("Consultanta C63", 3.0, "ora", "704")], (ce(f), ce(p))


# ── [decizia Costin 19.10.2026, „Închiderea lotului 9”, pct.2] „la transformarea în factură se pune aceeași întrebare ca la orice factură,
# «Pleacă marfa acum?»” — articolul de stoc trece pe factură, cu poarta de la emitere (`facturi_api.poarta_marfa_ceruta`) ──────────────
# Drumul probat e use-case-ul rutei (`uc_tenants.proforma_transforma`), pe o schemă efemeră cu stoc cantitativ-valoric: `db.get_conn`
# întoarce aceeași conexiune reală (fără commit), anulată la final. Marfa C63: 22 buc la 10 lei; proforma / avizul vinde 2 buc.
import contextlib  # noqa: E402
import io  # noqa: E402

from core import db as _db, erori as _erori, stocuri_cv_api as _cv, tenant_provisioning as _tp  # noqa: E402

_SCH_CV = "test_c63_marfa"
_CTX = {"uid": 1}


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def cv(monkeypatch):
    from core import ai_client, uc_comun
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH_CV)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH_CV))
                cur.execute("SET search_path TO %s, public" % _SCH_CV)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc, "
                            "serie_factura) VALUES (1, 'C63 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric', 'F1A')")
            art = _cv.intrare(c, _SCH_CV, {"denumire": "Marfa C63", "um": "buc", "data": "2026-10-01", "cantitate": 22,
                                           "pret_unitar": 10})

            @contextlib.contextmanager
            def _gc(*a, **k):
                yield _FaraCommit(c)
            monkeypatch.setattr(_db, "get_conn", _gc)
            monkeypatch.setattr(ai_client, "disponibil", lambda: False)
            monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: _SCH_CV)
            yield c, art["articol_id"]
        finally:
            c.rollback()


def _document(c, aid, tip="proforma"):
    linie = {"descriere": "Marfa C63", "cantitate": 2, "um": "buc", "pret_unitar": 20, "cota_tva": 21, "cont_venit": "707",
             "articol_id": aid}
    return facturi_api.emite_factura(c, [linie], tip=tip, platitor_tva=True, **_CLIENT)["factura_id"]


def _stoc(c, aid):
    with c.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(CASE WHEN tip = 'intrare' THEN cantitate ELSE -cantitate END), 0) FROM miscari_stoc "
                    "WHERE articol_id = %s", (aid,))
        return float(cur.fetchone()[0])


def _facturi_si_iesiri(c):
    with c.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE tip = 'factura'")
        n = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM miscari_stoc WHERE tip = 'iesire'")
        return n, cur.fetchone()[0]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("tip", ["proforma", "aviz"])
def test_c63_transformarea_cu_articol_intreaba_pleaca_marfa(cv, tip):
    """Fără răspuns: refuzul structurat al emiterii (`INTREABA_PLEACA_MARFA`, mesajul `MESAJ_INTREABA_MARFA`), nimic scris — nicio
    factură, nicio ieșire, documentul netransformat. Aviz și proformă: aceeași întrebare („ca la orice factură”).
    MUTAȚIE: `intreaba_marfa=poarta_ceruta` scos din `proforma_transforma` -> factura se emite fără întrebare -> pică."""
    c, aid = cv
    pid = _document(c, aid, tip)
    with pytest.raises(_erori.DateInvalide) as e:
        uc_tenants.proforma_transforma(1, pid, _CTX)
    assert e.value.detaliu == {"ok": False, "cod": facturi_api.COD_INTREABA_MARFA, "mesaj": facturi_api.MESAJ_INTREABA_MARFA}, \
        e.value.detaliu
    assert _facturi_si_iesiri(c) == (0, 0) and _stoc(c, aid) == 22.0
    assert facturi_api.detalii_factura(c, pid)["transformat_in_id"] is None


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c63_da_descarca_stocul_o_singura_data(cv):
    """„Da, pleacă marfa”: articolul trece pe factură și marfa se descarcă o dată (22 -> 20), în tranzacția emiterii; a doua transformare
    a aceluiași document se refuză (deja transformat), deci nu există a doua descărcare.
    MUTAȚIE: descărcarea scoasă din `proforma_transforma` -> stocul rămâne 22 -> pică."""
    c, aid = cv
    pid = _document(c, aid)
    r = uc_tenants.proforma_transforma(1, pid, _CTX, pleaca_marfa=True)
    assert [x["articol_id"] for x in r["descarcare"]["descarcate"]] == [aid] and r["descarcare"]["erori"] == [], r["descarcare"]
    assert _stoc(c, aid) == 20.0
    assert [l["articol_id"] for l in facturi_api.detalii_factura(c, r["factura_id"])["linii"]] == [aid]
    with pytest.raises(_erori.Conflict):
        uc_tenants.proforma_transforma(1, pid, _CTX, pleaca_marfa=True)
    assert _facturi_si_iesiri(c) == (1, 1) and _stoc(c, aid) == 20.0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c63_nu_nu_descarca_stocul(cv):
    """„Nu, doar factură”: factura se emite cu articolul pe linie, stocul nu se atinge (22), nicio ieșire.
    MUTAȚIE: condiția descărcării fără `pleaca_marfa is True` -> se descarcă și la „Nu” -> pică."""
    c, aid = cv
    pid = _document(c, aid)
    r = uc_tenants.proforma_transforma(1, pid, _CTX, pleaca_marfa=False)
    assert "descarcare" not in r, r
    assert _facturi_si_iesiri(c) == (1, 0) and _stoc(c, aid) == 22.0
    assert [l["articol_id"] for l in facturi_api.detalii_factura(c, r["factura_id"])["linii"]] == [aid]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c63_document_fara_articol_nu_intreaba(cv):
    """Serviciul (linie fără articol) nu are ce descărca: transformarea merge direct, ca emiterea fără articole."""
    c, aid = cv
    p = facturi_api.emite_factura(c, [dict(_LINIE)], tip="proforma", platitor_tva=True, **_CLIENT)
    r = uc_tenants.proforma_transforma(1, p["factura_id"], _CTX)
    assert r["factura_id"] and _facturi_si_iesiri(c) == (1, 0)


def test_c63_conditia_intrebarii_e_una_singura():
    """Emiterea din formular și transformarea întreabă după ACEEAȘI condiție (`facturi_api.poarta_marfa_ceruta`), nu după două copii.
    MUTAȚIE: condiția scrisă din nou în `facturi_emite` (`(date.tip == "factura") and are_stoc and not din_bon`) -> pică."""
    import ast
    arb = ast.parse(io.open("core/uc_tenants.py", encoding="utf-8").read())
    fn = {n.name: n for n in arb.body if isinstance(n, ast.FunctionDef)}
    for nume in ("facturi_emite", "proforma_transforma"):
        chemari = [n for n in ast.walk(fn[nume]) if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "poarta_marfa_ceruta"]
        assert len(chemari) == 1, (nume, len(chemari))
    assert facturi_api.poarta_marfa_ceruta("factura", [{"articol_id": 1}]) is True
    assert facturi_api.poarta_marfa_ceruta("proforma", [{"articol_id": 1}]) is False
    assert facturi_api.poarta_marfa_ceruta("factura", [{"articol_id": 1}], "0042") is False   # din bon: marfa a ieșit cu bonul
    assert facturi_api.poarta_marfa_ceruta("factura", [{"articol_id": None}]) is False
