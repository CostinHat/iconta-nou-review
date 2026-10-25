# -*- coding: utf-8 -*-
"""[lotul 12, pachetul fisc3, C84, decizia Costin 12.3 pct.7, verbatim: „livrarea intracomunitară de bunuri fără dovada transportului
primește avertisment la emitere, nu refuz.”]

Livrarea intracomunitară de bunuri se emite din „Emite factură” (C84 (b), 23.10.2026). Înainte: fosta `intracomunitar.valideaza_lic`
REFUZA livrarea fără dovada transportului („fără dovada transportului în alt stat membru scutirea nu se aplică [...] facturează cu TVA”),
dar n-avea niciun apelant de la C84 (b); „Emite factură” nu întreba nimic. Acum: după ce liniile au trecut (și după „Pleacă marfa acum?”),
serverul întreabă „Ai dovada transportului?” (`facturi_api.COD_INTREABA_DOVADA`, nimic scris); „Nu” emite factura cu scutirea și cu
avertismentul care spune ce lipsește și ce se întâmplă cu scutirea (`intracomunitar.AVERTISMENT_LIC_FARA_DOVADA`).

Temei, citat pe linia aserțiunii: CF art.294 alin.(2) lit.a și alin.(3); HG 1/2016 pct.65 (anaf_surse/cod_fiscal_227_2015_consolidat.txt,
anaf_surse/hg_1_2016_norme_cod_fiscal.txt). Schemă efemeră din `tenant_template.sql`, tranzacție anulată, date sintetice în 2097. CUI firmei:
14399840 (cifra de control verificată cu algoritmul din CLAUDE.md); clientul IE6388047V (cel din testul 274b)."""
import io
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot12_fisc3_c84"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT = {"tert_nume": "GOOGLE IRELAND LIMITED", "tert_cui": "IE6388047V", "tert_tara": "IE", "tert_adresa": "Gordon House",
          "tert_oras": "Dublin", "tert_judet": "Dublin"}


class _P:
    """Conexiunea testului: commit / rollback nu închid tranzacția testului (o anulează fixture-ul)."""
    def __init__(s, c): s._c = c
    def commit(s): pass
    def rollback(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "inreg_art317,operatiuni_ic,regim_fiscal,tip_firma,declarant_nume,declarant_prenume,declarant_functie,"
                            "forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES (1,'X SRL','14399840','Str 1','Cluj-Napoca',"
                            "'CJ','4690','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar',false,true,'micro','srl','Popescu','Ion',"
                            "'ADMINISTRATOR','SRL',200,'SDC','global_valoric')")
            yield _P(c)
        finally:
            c.rollback()


def _sql(c, q, args=()):
    with c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, args)
        return cur.fetchall() if cur.description else None


def _linie(cat="livrare_ic"):
    return {"descriere": "Marfa revanzare", "cantitate": 2, "um": "buc", "pret_unitar": "250", "cota_tva": 0, "categorie_tva": cat}


def _emite(c, linii=None, **k):
    from core import facturi_api
    _sql(c, "SELECT 1")
    return facturi_api.emite_factura(c, linii or [_linie()], data_emitere="2097-09-10", platitor_tva=True, **dict(CLIENT, **k))


def test_c84_emite_factura_intreaba_de_dovada_transportului_fara_sa_scrie(conn):
    """„Emite factură” (`intreaba_dovada=True`, ca `uc_tenants.facturi_emite`), livrare intracomunitară de bunuri, fără răspuns: întrebarea,
    nu factura — niciun rând, contorul neatins.
    MUTAȚIE: `if intreaba_dovada and _lic and dovada_transport is None:` -> `if False:` -> factura se emite fără întrebare -> ROȘU."""
    from core import facturi_api, intracomunitar as ic
    contor = _sql(conn, "SELECT urmator_numar_factura FROM firma_profil")
    with pytest.raises(ValueError) as e:
        _emite(conn, intreaba_dovada=True)
    assert getattr(e.value, "cod", None) == facturi_api.COD_INTREABA_DOVADA and e.value.intrebare == ic.INTREBARE_DOVADA_TRANSPORT
    assert _sql(conn, "SELECT count(*) FROM facturi")[0][0] == 0
    assert _sql(conn, "SELECT urmator_numar_factura FROM firma_profil") == contor


def test_c84_fara_dovada_factura_se_emite_cu_avertisment_nu_refuz(conn):
    """„Nu încă, emite factura”: factura se emite cu scutirea (linia livrare_ic, D300 rd.1, D390 L), iar răspunsul poartă avertismentul.
    MUTAȚIE: `if _lic and dovada_transport is False:` -> `if False:` -> fără avertisment -> ROȘU."""
    from core import intracomunitar as ic
    r = _emite(conn, intreaba_dovada=True, dovada_transport=False)
    assert _sql(conn, "SELECT categorie_tva, cota_tva::text FROM factura_linii WHERE factura_id = %s", (r["factura_id"],)) == [
        ("livrare_ic", "0.00")]
    assert _sql(conn, "SELECT axa_ic FROM facturi WHERE id = %s", (r["factura_id"],)) == [("bunuri",)]
    # decizia Costin 12.3 pct.7: „avertisment la emitere, nu refuz”; CF art.294 alin.(3): „Prin ordin al ministrului finanțelor publice se
    # stabilesc, acolo unde este cazul, documentele necesare pentru a justifica scutirea de taxă pentru operațiunile prevăzute la alin. (1)
    # și (2)”; HG 1/2016 pct.65: „Scutirile cu drept de deducere prevăzute la art. 294, 295 și 296 din Codul fiscal sunt aplicate în măsura
    # în care persoanele impozabile pot justifica scutirea cu documentele prevăzute de instrucțiuni aprobate de ministrul finanțelor
    # publice.”
    assert r["avertismente"] == [ic.AVERTISMENT_LIC_FARA_DOVADA], r["avertismente"]
    # textul întreg: ce lipsește (dovada transportului), temeiul și ce se întâmplă cu scutirea
    assert ic.AVERTISMENT_LIC_FARA_DOVADA == (
        "Factura s-a emis cu scutirea livrării intracomunitare (art.294 alin.(2) lit.a din Codul fiscal), dar nu ai încă dovada "
        "transportului bunurilor în alt stat membru. Scutirea se aplică numai dacă o justifici cu documentele de transport (art.294 alin.(3) "
        "din Codul fiscal; HG 1/2016 pct.65): păstrează-le la dosar când le primești. Fără ele scutirea nu se aplică, iar livrarea se "
        "facturează cu TVA (stornezi factura și emiți una cu TVA).")


def test_c84_cu_dovada_si_pe_celelalte_drumuri_nicio_intrebare(conn):
    """„Da, am dovada”: nicio întrebare, niciun avertisment. Fără `intreaba_dovada` (API-ul, recurentele, stornarea): nicio întrebare —
    [lotul 12, C197] dar avertismentul drumului care nu poate întreba (`AVERTISMENT_LIC_NEINTREBAT`: factura recurentă din cron), nu
    tăcere. Prestarea de servicii și proforma nu întreabă (dovada transportului e a livrării de bunuri)."""
    from core import intracomunitar, uc_comun
    assert _emite(conn, intreaba_dovada=True, dovada_transport=True)["avertismente"] == []
    assert _emite(conn)["avertismente"] == [intracomunitar.AVERTISMENT_LIC_NEINTREBAT]
    assert _emite(conn, [dict(_linie("serviciu_extern"), descriere="Servicii IT", um="serv.")], intreaba_dovada=True)["avertismente"] == []
    assert uc_comun._platitor_tva_firma(conn) is True
    assert _emite(conn, intreaba_dovada=True, tip="proforma")["avertismente"] == []


def test_c84_facturi_emite_trimite_intrebarea_structurata(conn, monkeypatch):
    """Ruta „Emite factură” (`uc_tenants.facturi_emite`): întrebarea iese ca refuz structurat (`cod`, `intrebare`), pe care ecranul îl
    transformă în caseta „Ai dovada transportului?” (`emitere_ecran.intrebareDovadaTransport`), cu factura păstrată."""
    import contextlib
    from main import EmitereIn
    from core import erori as _erori, facturi_api, uc_comun, uc_tenants

    @contextlib.contextmanager
    def _gc(*a, **k):
        with conn.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        yield conn
    monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: SCH)
    monkeypatch.setattr(uc_comun, "_platitor_tva_tert", lambda *a, **k: None)
    monkeypatch.setattr(uc_comun, "_intreaba_modelul", lambda *a, **k: None)
    monkeypatch.setattr(uc_comun, "_preincalzeste_cursul", lambda *a, **k: None)
    date = EmitereIn(linii=[_linie()], data_emitere="2097-09-10", **CLIENT)
    with pytest.raises(_erori.DateInvalide) as e:
        uc_tenants.facturi_emite(1, date, {"uid": 1})
    det = e.value.detaliu
    assert isinstance(det, dict) and det["cod"] == facturi_api.COD_INTREABA_DOVADA and det["intrebare"], det
