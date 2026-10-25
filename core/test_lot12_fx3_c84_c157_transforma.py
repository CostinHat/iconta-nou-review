# -*- coding: utf-8 -*-
"""[lotul 12, pachetul fx3] C84 și C157 pe factura născută din proformă / aviz („Transformă în factură”, `uc_tenants.proforma_transforma`).

Pachetul fisc3 a pus regula pe „Emite factură” (`uc_tenants.facturi_emite`); „Transformă în factură” emite tot o factură
(`facturi_api.emite_factura`), dar fără întrebare — clasa are două drumuri prin care contabilul emite o factură cu livrare intracomunitară.
- C84, decizia Costin 12.3 pct.7, verbatim: „livrarea intracomunitară de bunuri fără dovada transportului primește avertisment la emitere,
  nu refuz.” ROȘU înainte: proforma cu linia „livrare_ic” se transforma fără întrebare și fără avertisment.
- C157, decizia Costin 12.3 pct.3, verbatim: „fără înregistrare art. 317, avertisment la emitere, nu refuz (C157)”. Avertismentul vine din
  `emite_factura` (`categorii_tva.avertismente_emitere`) și ajunge în răspunsul transformării (ecranul îl arată sub confirmare).

Drumul probat e use-case-ul rutei, pe o schemă efemeră din `tenant_template.sql`: `db.get_conn` întoarce conexiunea testului (fără commit),
anulată la final. CUI firmei 14399840 (cifra de control verificată cu algoritmul din CLAUDE.md); clienții IE6388047V (din testul 274b /
fisc3 C84) și DE811907980 (din probele R187 / C78 / C110 / C154 / fisc3 C156)."""
import contextlib
import io
import os

import pytest

from core import db as _db, erori as _erori, facturi_api, tenant_provisioning as _tp, uc_tenants

SCH = "tenant_test_lot12_fx3_c84"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTX = {"uid": 1}
CLIENT_IE = {"tert_nume": "GOOGLE IRELAND LIMITED", "tert_cui": "IE6388047V", "tert_tara": "IE", "tert_adresa": "Gordon House",
             "tert_oras": "Dublin", "tert_judet": "Dublin"}
CLIENT_DE = {"tert_nume": "KUNDE GMBH", "tert_cui": "DE811907980", "tert_tara": "DE", "tert_adresa": "Unter den Linden 1",
             "tert_oras": "Berlin", "tert_judet": "Berlin"}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def rollback(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


def _firma(monkeypatch, platitor, art317):
    from core import ai_client, uc_comun
    if not _db_ok():
        pytest.skip("DB indisponibil")
    real = _db.get_conn
    cm = real()
    c = cm.__enter__()
    with c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)   # în tranzacția testului (anulată), nu pe conexiunea din pool
        cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                    "inreg_art317,operatiuni_ic,regim_fiscal,tip_firma,declarant_nume,declarant_prenume,declarant_functie,"
                    "forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES (1,'X SRL','14399840','Str 1','Cluj-Napoca',"
                    "'CJ','4690','BCR','RO49RNCB0000000000000001','0700000000',%s,%s,%s,true,'micro','srl','Popescu','Ion',"
                    "'ADMINISTRATOR','SRL',200,'SDC','global_valoric')", (platitor, "lunar" if platitor else None, art317))
    p = _FaraCommit(c)

    @contextlib.contextmanager
    def _gc(*a, **k):
        yield p
    monkeypatch.setattr(_db, "get_conn", _gc)
    monkeypatch.setattr(ai_client, "disponibil", lambda: False)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: SCH)
    return c, cm


@pytest.fixture
def platitor(monkeypatch):
    c, cm = _firma(monkeypatch, True, False)
    try:
        yield c
    finally:
        c.rollback()
        cm.__exit__(None, None, None)


@pytest.fixture
def neinregistrat(monkeypatch):
    c, cm = _firma(monkeypatch, False, False)
    try:
        yield c
    finally:
        c.rollback()
        cm.__exit__(None, None, None)


def _proforma_lic(c, tip="proforma"):
    """Proforma / avizul unei livrări intracomunitare de bunuri (2 × 250, cota 0, categoria „livrare_ic”), ca din „Emite factură”."""
    linie = {"descriere": "Marfa revanzare", "cantitate": 2, "um": "buc", "pret_unitar": "250", "cota_tva": 0, "categorie_tva": "livrare_ic"}
    return facturi_api.emite_factura(c, [linie], tip=tip, platitor_tva=True, **CLIENT_IE)["factura_id"]


def _facturi(c):
    with c.cursor() as cur:
        cur.execute("SELECT count(*) FROM %s.facturi WHERE tip = 'factura'" % SCH)
        return cur.fetchone()[0]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("tip", ["proforma", "aviz"])
def test_c84_transformarea_livrarii_ic_intreaba_dovada_transportului(platitor, tip):
    """Fără răspuns: întrebarea emiterii (`INTREABA_DOVADA_TRANSPORT`, cu textul `intracomunitar.INTREBARE_DOVADA_TRANSPORT`), nimic scris —
    nicio factură, documentul netransformat.
    TEMEI: CF art.294 alin.(3) — „Prin ordin al ministrului finanțelor publice se stabilesc, acolo unde este cazul, documentele necesare
    pentru a justifica scutirea de taxă pentru operațiunile prevăzute la alin. (1) și (2)”; HG 1/2016 pct.65 — scutirile „sunt aplicate în
    măsura în care persoanele impozabile pot justifica scutirea cu documentele prevăzute de instrucțiuni”.
    MUTAȚIE: `intreaba_dovada=True` -> `intreaba_dovada=False` în `uc_tenants.proforma_transforma` -> factura se emite fără întrebare -> pică."""
    from core import intracomunitar as ic
    pid = _proforma_lic(platitor, tip)
    with pytest.raises(_erori.DateInvalide) as ex:
        uc_tenants.proforma_transforma(1, pid, CTX)
    assert ex.value.detaliu == {"ok": False, "cod": facturi_api.COD_INTREABA_DOVADA,
                                "mesaj": "Răspunde la întrebare: " + ic.INTREBARE_DOVADA_TRANSPORT,
                                "intrebare": ic.INTREBARE_DOVADA_TRANSPORT}, ex.value.detaliu
    assert _facturi(platitor) == 0
    assert not facturi_api.detalii_factura(platitor, pid).get("transformat_in_id")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c84_fara_dovada_factura_se_emite_cu_avertisment_nu_refuz(platitor):
    """„Nu încă, emite factura” (`dovada_transport=False`): factura se emite cu scutirea (cota 0, „livrare_ic”) și cu avertismentul
    `intracomunitar.AVERTISMENT_LIC_FARA_DOVADA` în răspuns; proforma e legată de factură.
    TEMEI: decizia Costin 12.3 pct.7 („avertisment la emitere, nu refuz”); CF art.294 alin.(2) lit.a (scutirea livrării intracomunitare de
    bunuri expediate sau transportate în alt stat membru), alin.(3); HG 1/2016 pct.65.
    MUTAȚIE: `dovada_transport=dovada_transport` -> `dovada_transport=True` în `uc_tenants.proforma_transforma` -> fără avertisment -> pică."""
    from core import intracomunitar as ic
    pid = _proforma_lic(platitor)
    r = uc_tenants.proforma_transforma(1, pid, CTX, dovada_transport=False)
    assert r["avertismente"] == [ic.AVERTISMENT_LIC_FARA_DOVADA], r.get("avertismente")
    f = facturi_api.detalii_factura(platitor, r["factura_id"])
    assert (f["tip"], [(float(l["cota_tva"]), l["categorie_tva"]) for l in f["linii"]]) == ("factura", [(0.0, "livrare_ic")]), f
    assert facturi_api.detalii_factura(platitor, pid)["transformat_in_id"] == r["factura_id"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c84_cu_dovada_factura_se_emite_fara_avertisment(platitor):
    """„Da, am dovada transportului”: factura se emite, fără avertisment."""
    r = uc_tenants.proforma_transforma(1, _proforma_lic(platitor), CTX, dovada_transport=True)
    assert r["factura_id"] and r["avertismente"] == [], r.get("avertismente")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c84_proforma_fara_livrare_ic_nu_intreaba(platitor):
    """O proformă internă (21%, client român) se transformă direct: întrebarea e numai a livrării intracomunitare de bunuri."""
    linie = {"descriere": "Consultanta", "cantitate": 1, "um": "ora", "pret_unitar": 100, "cota_tva": 21, "cont_venit": "704"}
    pid = facturi_api.emite_factura(platitor, [linie], tip="proforma", platitor_tva=True, tert_nume="DANTE INTERNATIONAL SA",
                                    tert_cui="RO14399840", tert_adresa="Str. Gara Herastrau 6", tert_oras="Sector 2", tert_judet="B",
                                    tert_tara="RO")["factura_id"]
    r = uc_tenants.proforma_transforma(1, pid, CTX)
    assert r["factura_id"] and r["avertismente"] == [], r


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c157_transformarea_neplatitorului_neinregistrat_art317_avertizeaza(neinregistrat):
    """Neplătitorul NEînregistrat art.317 transformă proforma unui serviciu către clientul din DE (cod de TVA): factura se emite (nu se
    refuză), cu avertismentul `categorii_tva.AVERTISMENT_FARA_ART317` în răspuns.
    TEMEI: CF art.317 alin.(1) lit.b — are obligația să solicite înregistrarea persoana impozabilă neînregistrată „dacă prestează servicii
    care au locul în alt stat membru, pentru care beneficiarul serviciului este persoana obligată la plata taxei [...], înainte de prestarea
    serviciului”; decizia Costin 12.3 pct.3: „fără înregistrare art. 317, avertisment la emitere, nu refuz (C157)”.
    MUTAȚIE: răspunsul transformării fără avertismentele emiterii (`return rez` -> `return dict(rez, avertismente=[])` la capătul lui
    `uc_tenants.proforma_transforma`) -> pică."""
    from core import categorii_tva as ct
    linie = {"descriere": "Servicii de consultanta IT", "cantitate": 1, "um": "serv.", "pret_unitar": "500", "cota_tva": 0,
             "categorie_tva": None}
    pid = facturi_api.emite_factura(neinregistrat, [linie], tip="proforma", platitor_tva=False, **CLIENT_DE)["factura_id"]
    r = uc_tenants.proforma_transforma(1, pid, CTX)
    assert r["factura_id"] and r["avertismente"] == [ct.AVERTISMENT_FARA_ART317], r.get("avertismente")


# ── C84, aceeași clasă: calea de API a integratorului (`uc_api.apiv1_factura_emite`) ──────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c84_api_livrarea_ic_fara_dovada_se_emite_cu_avertisment(platitor, monkeypatch):
    """Pe calea de API nu e nimeni de întrebat: livrarea intracomunitară de bunuri se emite (nu se refuză), iar fără `dovada_transport: true`
    răspunsul poartă avertismentul — ca „Nu încă” din ecran; cu `dovada_transport: true`, fără avertisment.
    TEMEI: decizia Costin 12.3 pct.7 („avertisment la emitere, nu refuz”); CF art.294 alin.(3); HG 1/2016 pct.65.
    MUTAȚIE: `dovada_transport=corp.get("dovada_transport") is True` scos din `uc_api.apiv1_factura_emite` -> fără avertisment -> pică."""
    from core import intracomunitar as ic, uc_api, uc_comun
    monkeypatch.setattr(uc_comun, "_api_schema", lambda *a, **k: SCH)
    corp = dict(CLIENT_IE, linii=[{"descriere": "Marfa revanzare", "cantitate": 2, "um": "buc", "pret_unitar": "250", "cota_tva": 0,
                                   "categorie_tva": "livrare_ic"}], moneda="RON")
    r = uc_api.apiv1_factura_emite(1, dict(corp), {"firm": 1})
    assert r["factura_id"] and r["avertismente"] == [ic.AVERTISMENT_LIC_FARA_DOVADA], r
    r2 = uc_api.apiv1_factura_emite(1, dict(corp, dovada_transport=True), {"firm": 1})
    assert r2["factura_id"] and r2["avertismente"] == [], r2
