# -*- coding: utf-8 -*-
"""[lotul 11, AT] Afirmațiile adăugate în lotul 11 sunt OBIECTE (`core/afirmatii.afirmatie()`), nu proză în dicționar — decizia Costin
21.08.2026, antetul lui `core/afirmatii.py`: „o AFIRMAȚIE despre datele firmei e un OBIECT, nu un șir”. Clichetul
(`core/test_afirmatii_tipate.py`) numără pe FIȘIER; testele de aici numesc FUNCȚIA, ca o regresie într-un sit să nu fie mascată de o
conversie în altul din același fișier. Ce citește ecranul (`mesaj`, `motiv`, `gasit`, `schimbari`, `cod`, `asteptat`, `folosit`) rămâne
neschimbat, același text.

Situri (scanul `core.scan_afirmatii.netipate_in_scop()`, noi față de HEAD 22c71846):
  - `curs_bnr.cursul_zilei_lipsa` [460]: cursul BNR al zilei lipsește dintr-o sursă NUMITĂ (cursurile preluate) -> `absenta_observatie`;
  - `efactura_trimitere.refuz_din_efactura` [C86]: factura emisă a venit din e-Factura (are XML-ul importat) -> `fapt` despre factură
    (`unde` = factura); `uc_tenants.factura_trimite_spv` îl trimite ÎNTREG în 409, nu-l mai reîmpachetează ca proză;
  - `firma_profil_api._anaf_pentru_corectura` [459]: ANAF dă datele CUI-ului nou -> `fapt`; nu le are -> `absenta_observatie` (registrul
    contribuabililor); n-a răspuns -> `verificare_rupta` (precedentul `uc_regim_tva_incasare`, la fel: ANAF jos nu e „nu există”);
  - `uc_tenants.cui_firma_invalid` [459]: NU e afirmație despre datele firmei — e validarea CÂMPULUI CUI din formular („Adaugă firmă”,
    înregistrarea), de pus lângă câmp (`tenant_provisioning.motiv_cui_firma_invalid`; `CuiInvalid.camp = "cui"`) -> poartă `camp`, clasa
    D (în afara scopului), ca refuzurile 273c din `uc_tenants`.
"""
import contextlib
from datetime import date as Z

import pytest

from core import afirmatii as _af
from core import curs_bnr as cb
from core import efactura_trimitere as _eft
from core import erori as _erori
from core import firma_profil_api as fp
from core import scan_afirmatii as s
from core import tenant_provisioning as tp
from core import uc_tenants as uc

SITURI = (("core/curs_bnr.py", "cursul_zilei_lipsa"), ("core/efactura_trimitere.py", "refuz_din_efactura"),
          ("core/firma_profil_api.py", "_anaf_pentru_corectura"), ("core/uc_tenants.py", "factura_trimite_spv"),
          ("core/uc_tenants.py", "cui_firma_invalid"))
# `factura_trimite_spv` mai are UN dicționar netipat, de dinainte de lotul 11 (răspunsul trimiterii, `stare`/`mesaj`), numărat în BASELINE
# (`core/uc_tenants.py`: 2, cu `_z_in_rip`). Lotul 11 n-are voie să adauge altele în aceeași funcție.
VECHI = {("core/uc_tenants.py", "factura_trimite_spv"): 1}


def _valida(a):
    """Afirmația trece din nou prin constructor: fel din nomenclator, câmpurile cerute, niciunul gol unde nu poate fi."""
    camp = {k: v for k, v in a.items() if k not in ("fel", "tip", "motiv")}
    assert _af.afirmatie(a["fel"], a["tip"], a["motiv"], **camp) == a


def test_siturile_lotului_11_nu_mai_produc_proza():
    """Scanul, pe FUNCȚIE. MUTAȚIE: oricare conversie întoarsă la dicționarul cu `mesaj`/`motiv` fără `fel` -> pică, numind situl."""
    from collections import Counter
    n = Counter((x[0], x[1]) for x in s.netipate_in_scop())
    rele = ["%s · %s: %d netipate (admise %d)" % (f, fn, n[(f, fn)], VECHI.get((f, fn), 0))
            for f, fn in SITURI if n[(f, fn)] > VECHI.get((f, fn), 0)]
    assert not rele, "afirmații netipate în siturile lotului 11 (scrie-le cu `afirmatii.afirmatie()`):\n  " + "\n  ".join(rele)


# ── 460: cursul zilei lipsă ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_cursul_zilei_lipsa_e_absenta_intr_o_sursa_numita():
    r = cb.cursul_zilei_lipsa(Z(2026, 10, 22), Z(2026, 10, 19), azi=Z(2026, 10, 22))
    assert r["fel"] == "absenta_observatie" and r["surse_consultate"], r
    _valida(r)
    # ce citește ecranul (`emitere_ecran.js`: `curs_zilei_lipsa.mesaj`) rămâne; `motiv` e ACELAȘI text, nu un al doilea
    assert r["mesaj"] == r["motiv"] == (
        "Cursul BNR comunicat pe 21.10.2026 (ultimul înaintea datei facturii, 22.10.2026) lipsește din aplicație: preluarea lui de la "
        "BNR n-a reușit încă; aplicația reîncearcă singură. Până atunci se folosește cursul din 19.10.2026, iar factura emisă acum îl "
        "păstrează (se fixează la emitere)."), r
    assert (r["asteptat"], r["folosit"]) == ("2026-10-21", "2026-10-19"), r
    # cursul corect nu e o lipsă (HG 1/2016 pct.35 alin.(1): cursul „comunicat de respectiva bancă în ziua anterioară”)
    assert cb.cursul_zilei_lipsa(Z(2026, 10, 22), Z(2026, 10, 21)) is None


# ── C86: factura venită din e-Factura ───────────────────────────────────────────────────────────────────────────────────────────────
class _Cur:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Conn:
    def cursor(self, *a, **k):
        return _Cur()


@pytest.fixture
def din_xml(monkeypatch):
    from core import repo_facturi as _rf
    monkeypatch.setattr(_rf, "stare_pentru_recunoastere", lambda cur, schema, fid: ("emisa", "emisa", True))
    # [lotul 12, 252] refuzul citește și tipul documentului (factura deschisă preluată nu pleacă în SPV): aici, o factură obișnuită
    monkeypatch.setattr(_rf, "tip_document", lambda cur, schema, fid: "factura")


def test_refuzul_din_efactura_e_un_fapt_despre_factura(din_xml):
    r = _eft.refuz_din_efactura(_Conn(), "tenant_x", 77)
    assert r["fel"] == "fapt" and r["temei_completitudine"], r
    assert r["unde"].fel == "factura" and r["unde"].id == 77, r["unde"]
    _valida(r)
    # ce citesc `trimite` (stare), ruta și ecranul (cod, mesaj) rămâne
    assert (r["stare"], r["cod"], r["mesaj"]) == ("din_efactura", _eft.COD_DIN_EFACTURA, _eft.MESAJ_DIN_EFACTURA), r
    assert r["motiv"] == r["mesaj"]


def test_factura_preluata_e_acelasi_refuz_cu_codul_ei(din_xml, monkeypatch):
    """[lotul 12, 252] Factura deschisă preluată (din soldurile pe parteneri) primește ACELAȘI refuz (aceeași stare, deci aceeași cale în
    `trimite` și în rută), cu codul și mesajul ei — chiar dacă nu are XML-ul importat."""
    from core import nomenclator_status_factura as _nsf
    from core import repo_facturi as _rf
    monkeypatch.setattr(_rf, "tip_document", lambda cur, schema, fid: _nsf.TIP_SOLD_PRELUAT)
    monkeypatch.setattr(_rf, "stare_pentru_recunoastere", lambda cur, schema, fid: ("emisa", "emisa", False))
    r = _eft.refuz_din_efactura(_Conn(), "tenant_x", 77)
    _valida(r)
    assert (r["stare"], r["cod"], r["mesaj"]) == ("din_efactura", "SOLD_PRELUAT", _nsf.MESAJ_SOLD_PRELUAT), r
    assert r["unde"].fel == "factura" and r["unde"].id == 77, r["unde"]


def test_ruta_trimite_spv_trimite_afirmatia_intreaga_in_409(din_xml, monkeypatch):
    """Ambele drumuri ale lui `factura_trimite_spv` (verificarea dinaintea conexiunii SPV și poarta 0 a lui `trimite`): detaliul 409 e
    afirmația tipată, cu `cod` și `mesaj` (pe care le citesc `api.js` și e2e-ul C86), nu un dicționar nou de proză."""
    from core import db, auth_api
    monkeypatch.setattr(db, "get_conn", lambda *a, **k: contextlib.nullcontext(_Conn()))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: "tenant_x")
    with pytest.raises(_erori.Conflict) as e:
        uc.factura_trimite_spv(1, 77, {"uid": 1})
    d = e.value.detaliu
    assert d["fel"] == "fapt" and (d["cod"], d["mesaj"]) == (_eft.COD_DIN_EFACTURA, _eft.MESAJ_DIN_EFACTURA), d
    # poarta 0 a lui `trimite` (factura importată între verificarea rutei și trimitere)
    real = _eft.refuz_din_efactura(_Conn(), "tenant_x", 77)
    monkeypatch.setattr(_eft, "refuz_din_efactura", lambda *a: None)
    monkeypatch.setattr(uc._spv_rute, "spv_principal", lambda ctx: ("cabinet", 1))
    monkeypatch.setattr(_eft, "trimite", lambda *a, **k: real)
    with pytest.raises(_erori.Conflict) as e:
        uc.factura_trimite_spv(1, 77, {"uid": 1})
    d = e.value.detaliu
    assert d["fel"] == "fapt" and (d["cod"], d["mesaj"]) == (_eft.COD_DIN_EFACTURA, _eft.MESAJ_DIN_EFACTURA), d


def test_detaliul_409_se_serializeaza_json(din_xml):
    """`unde` e `Unde` (subclasă de `str`): răspunsul HTTP rămâne JSON, iar `unde` ajunge ca textul „factura 77”."""
    import json
    from fastapi.encoders import jsonable_encoder
    r = _eft.refuz_din_efactura(_Conn(), "tenant_x", 77)
    j = json.loads(json.dumps(jsonable_encoder(r)))
    assert j["unde"] == "factura 77" and j["mesaj"] == _eft.MESAJ_DIN_EFACTURA, j


# ── 459: corectura CUI-ului, datele ANAF ale CUI-ului nou ───────────────────────────────────────────────────────────────────────────
class _CurProfil(_Cur):
    def execute(self, *a):
        pass

    def fetchone(self):
        return {c: None for c, _e, _k in tp.CAMPURI_ANAF}


class _ConnProfil:
    def cursor(self, *a, **k):
        return _CurProfil()


def test_anaf_gasit_e_un_fapt():
    a = fp._anaf_pentru_corectura(_ConnProfil(), "14399840", {"denumire": "DANTE INTERNATIONAL SA", "adresa": "Str. X"}, None)
    assert a["fel"] == "fapt" and a["gasit"] is True and a["unde"].fel == "camp_profil", a
    _valida(a)
    assert a["motiv"] == a["mesaj"] and a["mesaj"].startswith("La ANAF, CUI-ul 14399840 e al firmei „DANTE INTERNATIONAL SA”."), a
    assert {x["camp"] for x in a["schimbari"]} >= {"nume", "adresa"}, a["schimbari"]


def test_anaf_negasit_e_absenta_in_registrul_contribuabililor():
    a = fp._anaf_pentru_corectura(_ConnProfil(), "14399840", None, None)
    assert (a["fel"], a["surse_consultate"]) == ("absenta_observatie", "registrul contribuabililor ANAF, pentru CUI-ul 14399840"), a
    _valida(a)
    assert (a["gasit"], a["schimbari"]) == (False, []) and a["motiv"] == a["mesaj"], a
    assert a["mesaj"] == ("ANAF nu are date pentru CUI-ul 14399840 (nu apare în registrul contribuabililor). "
                          + fp.DE_VERIFICAT_FARA_ANAF), a["mesaj"]


def test_anaf_care_nu_raspunde_e_verificare_rupta_nu_absenta():
    """ANAF jos nu e „CUI-ul nu există la ANAF”: verificarea s-a oprit (precedentul `uc_regim_tva_incasare`, același fel)."""
    from core import anaf_api
    a = fp._anaf_pentru_corectura(_ConnProfil(), "14399840", None, anaf_api.MESAJ_ANAF_NU_RASPUNDE)
    assert a["fel"] == "verificare_rupta" and a["eroare"] == anaf_api.MESAJ_ANAF_NU_RASPUNDE, a
    _valida(a)
    assert a["mesaj"] == anaf_api.MESAJ_ANAF_NU_RASPUNDE + " " + fp.DE_VERIFICAT_FARA_ANAF and a["gasit"] is False, a


# ── 459: CUI-ul greșit la verificarea publică = validare de formular ────────────────────────────────────────────────────────────────
def test_cui_invalid_e_validarea_campului_cui():
    r = uc.cui_firma_invalid("14399841")     # 14399840 e CUI-ul real al DANTE INTERNATIONAL SA; 1 = cifra de control greșită
    assert r["camp"] == tp.CuiInvalid.camp == "cui", r
    # ce citesc `login.js` și `firme.js` rămâne
    assert (r["gasit"], r["cui_invalid"], r["cui"], r["motiv"]) == (False, True, "14399841", tp.MESAJ_CUI_CONTROL % "14399841"), r
    assert s.clasa("core/uc_tenants.py", "cui_firma_invalid", r.keys()) == "D_formular"
    assert uc.cui_firma_invalid("14399840") is None
