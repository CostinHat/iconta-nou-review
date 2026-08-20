# -*- coding: utf-8 -*-
"""Granite API — cota TVA lipsa = intrare INCOMPLETA -> eroare, nu default 21 ghicit.

DE CE (31.07.2026, directie Costin): la granita, `corp.get("cota", 21)` insemna "daca
apelantul n-a trimis cota, pun eu una". Dar o factura/linie fara cota e o intrare incompleta,
nu o factura cu cota standard. Regula bazei nule: se ridica eroare, nu se ghiceste - nici
macar corect. Un default cu common.cota() ar fi tot o valoare inventata, doar actualizata.

Distinctie cheie: cota 0 (scutit/neplatitor) e VALOARE VALIDA, nu absenta.
"""
import pytest

from core.common import cota_ceruta, Perioada


# ── TEMA A: helper de granita cota_ceruta(corp) ──────────────────────────────
def test_cota_lipsa_din_corp_ridica():
    """Cheie cota absenta -> ValueError (endpoint o prinde -> HTTP 422), NU 21 tacut."""
    with pytest.raises(ValueError) as e:
        cota_ceruta({"pret_vanzare": 100, "pret_cumparare": 80})
    assert "cot" in str(e.value).lower()


def test_cota_none_explicit_ridica():
    with pytest.raises(ValueError):
        cota_ceruta({"cota": None})


def test_cota_zero_scutit_e_valoare_valida_nu_absenta():
    """0 = scutit/neplatitor TVA: cota valida, NU absenta -> se intoarce 0, nu se ridica,
    nu se transforma in 21. (regula bazei nule distinge None de 0)."""
    assert cota_ceruta({"cota": 0}) == 0


def test_cota_prezenta_se_intoarce_ca_atare():
    assert cota_ceruta({"cota": 11}) == 11
    assert cota_ceruta({"cota": 21}) == 21


# ── TEMA B: emitere — cota NEDETERMINATA (AI picat) blocheaza, nu ghiceste 21 ──
import pytest as _pt
from core import db as _db, tenant_provisioning as _tp

SCHEMA_T = "ztest_granite_cota"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@_pt.fixture
def conn_schema():
    """Schema temporara din template + firma_profil minima. ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
                cur.execute("SET search_path TO %s, public" % SCHEMA_T)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, "
                    "platitor_tva, tip_decont) VALUES "
                    "(1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202',true,'L') "
                    "ON CONFLICT (id) DO UPDATE SET nume=EXCLUDED.nume")
            yield conn
        finally:
            conn.rollback()


@_pt.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_emitere_linie_fara_cota_cu_ai_picat_blocheaza(conn_schema, monkeypatch):
    """AI indisponibil + produs NOU fara cota -> potriveste_cota NEDETERMINAT -> linia ramane
    fara cota -> emiterea RIDICA, NU produce 21 tacut in decont. (azi: fallback 21, emite)."""
    from core import ai_client, facturi_api
    monkeypatch.setattr(ai_client, "disponibil", lambda: False)
    with _pt.raises(ValueError) as e:
        facturi_api._potriveste_linii(
            conn_schema,
            [{"descriere": "produs complet necunoscut zzz-qwerty", "cantitate": 1, "pret_unitar": 100}],
            platitor_tva=True)
    m = str(e.value).lower()
    assert "cot" in m and ("nedetermin" in m or "explicit" in m), "mesaj neclar: %s" % e.value


# ── TEMA C: cota 0 (scutit) e valoare VALIDA, nu absenta (bug produse_api:46) ──
@_pt.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_produs_scutit_cota_0_ramane_0_nu_devine_21(conn_schema):
    """Un produs cu cota 0 (scutit/neplatitor) citit din nomenclator trebuie sa intoarca 0,
    NU 21. `float(out[cota_tva] or 21)` transforma 0 in 21 (or pe 0 = fals). Distinge None
    (incomplet) de 0 (scutit). (azi: 0 -> 21)."""
    from core import produse_api
    with conn_schema.cursor() as cur:
        cur.execute("INSERT INTO produse (denumire, um, pret_unitar, cota_tva, sursa, confirmat) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    ("Serviciu scutit ABC", "buc", 100, 0, "manual", True))
    r = produse_api.cauta_dupa_denumire(conn_schema, "Serviciu scutit ABC")
    assert r is not None
    assert r["cota_tva"] == 0, "cota scutit 0 transformata gresit in %s" % r["cota_tva"]


# ── TEMA E: proba pana la declaratie — D300 cu factura SCUTITA (cota 0) prin granita reparata ──
from core import duk as _duk
_D300_DUK = _duk.poate_valida("d300")


@_pt.fixture
def conn_schema_d300():
    """Schema temporara cu firma_profil COMPLET (banca+iban) pentru D300. ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
                cur.execute("SET search_path TO %s, public" % SCHEMA_T)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "email, telefon, regim_fiscal, platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','BCR',"
                    "'RO49RNCB0000000000000001','a@b.ro','0700000000','real',true,'L','Pop','Ion','administrator') "
                    "ON CONFLICT (id) DO UPDATE SET banca=EXCLUDED.banca, iban=EXCLUDED.iban")
            yield conn
        finally:
            conn.rollback()


@_pt.mark.skipif(not _db_ok() or not _D300_DUK, reason="DB sau validator DUK d300 indisponibil")
def test_proba_d300_factura_scutita_prin_granita_reparata_duk_valid(conn_schema_d300):
    """LECTIA D3 + proba pana la declaratie: o factura emisa prin granita REPARATA (emite_factura,
    cu _potriveste_linii + creeaza_factura care acum cer cota explicit), cu o linie 21% SI o linie
    SCUTITA (cota 0 - valoare valida, nu absenta transformata in 21), genereaza un D300 care trece
    validatorul OFICIAL DUK. Dovada ca reparatia ajunge la o declaratie VALIDA, nu doar la teste
    unitare verzi (lectia 29.07: fix verde in suita dar declaratie gresita la generare)."""
    from core import facturi_api, d300
    r = facturi_api.emite_factura(
        conn_schema_d300,
        [{"descriere": "Consultanta IT", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21},
         {"descriere": "Servicii medicale scutite", "cantitate": 1, "pret_unitar": 500, "cota_tva": 0}],
        data_emitere="2026-06-15", moneda="RON", platitor_tva=True)
    assert r.get("factura_id"), "emitere esuata: %r" % r
    xml, res = d300.genereaza(conn_schema_d300, SCHEMA_T, Perioada(2026, luna=6))
    rez = _duk.valideaza(xml, "d300", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D300 (factura cu linie scutita): %s" % rez


@_pt.mark.skipif(not _db_ok() or not _duk.poate_valida("d394"), reason="DB sau DUK d394 indisponibil")
def test_proba_d394_factura_scutita_prin_granita_reparata_duk_valid(conn_schema_d300):
    """D394 (informativa domestica): factura emisa prin granita REPARATA, cu linie 21% + linie
    SCUTITA (cota 0), catre partener RO -> D394 valid la DUK. Fiecare generator isi trateaza
    propriile campuri: valid pe D300 nu e dovada pentru D394."""
    from core import facturi_api, declaratii_api
    r = facturi_api.emite_factura(conn_schema_d300,
        [{"descriere": "Consultanta IT", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21},
         {"descriere": "Servicii medicale scutite", "cantitate": 1, "pret_unitar": 500, "cota_tva": 0}],
        tert_nume="CLIENT RO SRL", tert_cui="RO14399840",
        data_emitere="2026-06-15", moneda="RON", platitor_tva=True)
    assert r.get("factura_id"), "emitere esuata: %r" % r
    xml, res = declaratii_api.genereaza(conn_schema_d300, SCHEMA_T, "d394", {"an": 2026, "luna": 6})
    rez = _duk.valideaza(xml, "d394", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D394 (linie scutita): %s" % rez


@_pt.mark.skipif(not _db_ok() or not _duk.poate_valida("d390"), reason="DB sau DUK d390 indisponibil")
def test_proba_d390_livrare_ic_scutita_prin_granita_reparata_duk_valid(conn_schema_d300):
    """D390 (recapitulativ VIES): livrare intracomunitara emisa prin granita reparata, cota 0
    (scutit cu drept, partener UE) -> D390 valid la DUK."""
    from core import facturi_api, declaratii_api
    r = facturi_api.emite_factura(conn_schema_d300,
        [{"descriere": "Livrare IC bunuri", "cantitate": 1, "pret_unitar": 2000, "cota_tva": 0}],
        tert_nume="KUNDE DE GMBH", tert_cui="DE811569869",
        data_emitere="2026-06-20", moneda="RON", platitor_tva=True)
    assert r.get("factura_id"), "emitere esuata: %r" % r
    xml, res = declaratii_api.genereaza(conn_schema_d300, SCHEMA_T, "d390", {"an": 2026, "luna": 6})
    rez = _duk.valideaza(xml, "d390", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D390 (livrare IC scutita): %s" % rez


# ── TEMA D: doc contra cod in cote_tva (20.08.2026) ──────────────────────────
# Doua constatari, aceeasi radacina: o afirmatie despre cota care n-a fost verificata la sursa.
# (1) docstring-ul lui `potriveste_cota` promitea "fallback: cota standard 21%" iar codul intoarce
#     NEDETERMINAT. Arbitrul e argumentul semantic, scris in `_nedeterminat`: un 21 marcat fallback
#     ajunge in decont exact ca unul tacit daca factura se emite oricum. Deci codul are dreptate,
#     docstring-ul s-a corectat catre cod, si se LEAGA aici - altfel se poate intoarce.
# (2) `cote_valide()` intorcea [21, 11, 0] fara data, cu zero consumatori. Stearsa.

def test_ai_indisponibil_da_nedeterminat_nu_fallback_21(monkeypatch):
    """Comportamentul, nu doar textul: fara AI, cota NU se ghiceste."""
    from core import ai_client, cote_tva
    monkeypatch.setattr(ai_client, "disponibil", lambda: False)
    r = cote_tva.potriveste_cota("produs complet necunoscut zzz-qwerty", platitor_tva=True)
    assert r["ok"] is False and r["cota"] is None, "a ghicit o cota fara AI: %r" % r
    assert r["cod"] == "NEDETERMINAT" and r["sursa"] == "nedeterminat"


def test_niciun_drum_nu_intoarce_o_cota_marcata_fallback():
    """Legatura doc-cod, pusa pe INVARIANTUL codului, nu pe cuvinte. Prima versiune a gardului
    cauta "fallback" langa "21" in docstring - si s-a aprins pe propria explicatie de ce fallback-ul
    e gresit. Un gard care nu deosebeste afirmatia de negatia ei nu pazeste nimic. Ce se pazeste de
    fapt: niciun drum din modul nu are voie sa intoarca o cota cu `sursa='fallback'`."""
    import inspect
    import re

    from core import cote_tva
    src = inspect.getsource(cote_tva)
    rau = re.findall(r"""["']sursa["']\s*:\s*["']fallback["']""", src)
    assert not rau, (
        "cote_tva intoarce iar o cota marcata 'fallback' (%d locuri). Un 21 marcat fallback ajunge "
        "in decont exact ca unul tacit - vezi `_nedeterminat`." % len(rau))
    d = (cote_tva.potriveste_cota.__doc__ or "").lower()
    assert "nedetermin" in d, "docstring-ul nu spune ce face de fapt functia cand AI lipseste"


def test_cote_valide_a_disparut_nu_se_intoarce():
    """Anti-vacuu pe stergere: `cote_valide()` intorcea [21, 11, 0] FARA perioada. Chemata pe o
    factura din iunie 2025 ar fi respins 19% ca invalida. Validarea period-aware traieste in
    `common.cota` / `common.cota_ceruta`; o a doua lista, oarba la perioada, e logica paralela."""
    from core import cote_tva
    assert not hasattr(cote_tva, "cote_valide"), (
        "`cote_valide` a revenit. O lista de cote valide fara data respinge cota corecta a unei "
        "perioade trecute - foloseste common.cota(...) cu perioada facturii.")
