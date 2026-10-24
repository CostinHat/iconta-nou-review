# -*- coding: utf-8 -*-
"""Lotul 12, pachetul `emit` — deficiența 462: „Facturi recurente: Șablonul ocolește verificările facturii obișnuite.”
Clasa (Costin): orice drum care creează o factură trece prin aceleași verificări.

Ce se probează (pe o schemă efemeră din `tenant_template.sql`, anulată la capăt):
  * la SALVARE, șablonul trece prin emiterea de probă (`facturi_recurente._proba_emiterii` -> `facturi_api.emite_factura` într-un
    SAVEPOINT anulat): un șablon bun se salvează și NU lasă în urmă nicio factură, notă sau număr consumat; unul pe care factura
    obișnuită l-ar refuza (firma fără formă juridică, fără serie, neplătitorul cu TVA pe linie, codul fiscal lipsă) nu se salvează,
    cu refuzul facturii obișnuite;
  * pe AMBELE drumuri (salvare și cron), verificările drumului obișnuit din afara lui `emite_factura` (`verificari_drum`): denumirea
    beneficiarului, linia cu articol de stoc, clientul din alt stat;
  * cronul nu emite un șablon salvat înainte de 462 care cade la ele, iar factura emisă poartă plătitorul de TVA al beneficiarului
    (ANAF, ca drumul obișnuit).
"""
import contextlib
import datetime
import json
import re

import pytest

from core import db as _db, tenant_provisioning as _tp

_SCHEMA = "test_lot12_emit_rec"
AZI = datetime.date(2099, 3, 10)   # perioadă sintetică (CLAUDE.md §10): cotele în vigoare sunt cele de azi, fără curs (RON)
CUI_CLIENT = "14399840"            # DANTE INTERNATIONAL SA — cifra de control verificată cu `cui_valid` (CLAUDE.md)
LINIE = {"descriere": "Abonament mentenanta lunara", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "cont_venit": "704"}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def mediu(monkeypatch):
    """Firmă SRL plătitoare de TVA, cu forma juridică, capitalul și seria „RC”; o singură conexiune reală (anulată la capăt), dată și
    cronului (`db.get_conn`); ANAF simulat (plătitorul beneficiarului = True)."""
    from core import facturi_api, uc_comun
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
            cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,tip_decont,"
                        "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris) VALUES (1,'Recurente 462 SRL',"
                        "'14399840','Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001','micro',true,'L','Pop','Ion',"
                        "'administrator','SRL',200)")
        assert facturi_api.seteaza_numerotare(c, serie="RC", numar_start=1)["ok"]

        @contextlib.contextmanager
        def _gc(*a, **k):
            with c.cursor() as cur:
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
            yield _FaraCommit(c)
        monkeypatch.setattr(_db, "get_conn", _gc)
        monkeypatch.setattr(uc_comun, "_platitor_tva_tert", lambda *a, **k: True)
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _numar(c, sql):
    with c.cursor() as cur:
        cur.execute(sql % {"s": _SCHEMA})
        return cur.fetchone()[0]


def _adauga(c, **k):
    from core import facturi_recurente as fr
    corp = dict({"tert_nume": "Client Recurent SRL", "tert_cui": CUI_CLIENT, "zi_emitere": 5, "moneda": "RON", "linii": [dict(LINIE)]}, **k)
    return fr.adauga(c, _SCHEMA, corp, azi=AZI)


def _campuri(r):
    return [x["camp"] for x in r.get("erori_campuri") or []]


def _pe_campuri(r):
    return [(x["camp"], x["mesaj"]) for x in r.get("erori_campuri") or []]


#: o citare de temei în formatul constant din CLAUDE.md §3.1 (`CF art.310 alin.(10) lit.b`) — refuzul se citește pe temeiul lui, ca DATĂ
_CITARE = re.compile(r"\b(?:CF|CPF|(?:Legea|OUG|OG|HG|OMF|OMFP|OPANAF) \d+/\d+) art\.\s?[\dIVXLC^]+(?: alin\.\s?\(\d+(?:\^\d+)?\))?"
                     r"(?: lit\.\s?[a-z]\b)?")


def _refuzul_emiterii(text):
    """Refuzul emiterii obișnuite, așa cum îl spune salvarea șablonului (`facturi_recurente._proba_emiterii`)."""
    from core import facturi_recurente as fr
    assert text.startswith(fr._REFUZ_EMITERE), text
    return fr.PREFIX_PROBA + text[len(fr._REFUZ_EMITERE):]


def test_sablonul_bun_trece_prin_emiterea_de_proba_si_nu_lasa_nimic_scris(mediu):
    """Șablonul complet se salvează; emiterea de probă (aceleași verificări ca factura obișnuită) nu lasă factură, notă sau număr
    consumat: următorul număr rămâne 1. MUTAȚIE: `ROLLBACK TO SAVEPOINT proba_sablon` -> `RELEASE SAVEPOINT` (proba nu se anulează)
    -> rămâne o factură RC1 și contorul sare la 2 -> pică."""
    r = _adauga(mediu)
    assert "eroare" not in r and r["id"], r
    assert _numar(mediu, "SELECT count(*) FROM %(s)s.facturi") == 0
    assert _numar(mediu, "SELECT count(*) FROM %(s)s.inregistrari") == 0
    assert _numar(mediu, "SELECT urmator_numar_factura FROM %(s)s.firma_profil WHERE id = 1") == 1
    assert _numar(mediu, "SELECT count(*) FROM %(s)s.facturi_recurente") == 1


def test_firma_fara_forma_juridica_nu_poate_salva_sablonul(mediu):
    """Legea 31/1990 art.74 alin.(1) și (3): factura unei societăți menționează forma juridică, iar a unui SRL și capitalul social —
    factura obișnuită se refuză până se completează în Date firmă; șablonul la fel, la salvare, nu la cron.
    MUTAȚIE: apelul `_proba_emiterii` scos din `adauga` -> șablonul se salvează -> pică."""
    with mediu.cursor() as cur:
        cur.execute("UPDATE %s.firma_profil SET forma_juridica = NULL WHERE id = 1" % _SCHEMA)
    r = _adauga(mediu)
    from core import capital_social
    # refuzul e cel al emiterii obișnuite pentru forma juridică lipsă, nu altul (capital_social.mesaj_refuz)
    assert r.get("eroare") == _refuzul_emiterii(capital_social.mesaj_refuz(capital_social.lipsa({"tip_firma": "srl"}))), r
    assert _numar(mediu, "SELECT count(*) FROM %(s)s.facturi_recurente") == 0


def test_firma_fara_serie_nu_poate_salva_sablonul(mediu):
    """CF art.319 alin.(20) lit.a: factura cuprinde „numărul de ordine, în baza uneia sau a mai multor serii, care identifică factura
    în mod unic” — fără serie, factura obișnuită se refuză; șablonul la fel. MUTAȚIE: aceeași cu cea de sus."""
    with mediu.cursor() as cur:
        cur.execute("UPDATE %s.firma_profil SET serie_factura = NULL WHERE id = 1" % _SCHEMA)
    r = _adauga(mediu)
    from core import facturi_api
    assert r.get("eroare") == _refuzul_emiterii(facturi_api.MESAJ_SERIE_LIPSA), r
    assert _numar(mediu, "SELECT count(*) FROM %(s)s.facturi_recurente") == 0


def test_neplatitorul_nu_poate_salva_un_sablon_cu_tva(mediu):
    """CF art.310 alin.(10) lit.b: persoana care aplică regimul special de scutire „nu are voie să menționeze taxa pe factură sau pe
    alt document” — linia cu 21% se refuză și în șablon. MUTAȚIE: aceeași cu cea de sus."""
    with mediu.cursor() as cur:
        cur.execute("UPDATE %s.firma_profil SET platitor_tva = false WHERE id = 1" % _SCHEMA)
    r = _adauga(mediu)
    from core import facturi_recurente as fr
    assert r.get("eroare", "").startswith(fr.PREFIX_PROBA) and {"CF art.310 alin.(10) lit.b"} <= set(_CITARE.findall(r["eroare"])), r
    assert _numar(mediu, "SELECT count(*) FROM %(s)s.facturi_recurente") == 0


def test_beneficiarul_codul_fiscal_articolul_si_clientul_strain_lange_campurile_lor(mediu):
    """Verificările drumului obișnuit din afara lui `emite_factura`, fiecare lângă câmpul ei din formularul șablonului:
    denumirea beneficiarului (CF art.319 alin.(20) lit.f: „denumirea/numele și adresa beneficiarului”, `fr-nume`; înainte trecea și numai
    `client_id`), codul fiscal (aceeași literă, `fr-cui`), linia cu articol de stoc (`fr-l0-descriere`: emiterea automată nu poate
    întreba „Pleacă marfa acum?”, R57) și clientul din alt stat (`fr-cui`: șablonul n-are țara și categoria livrării).
    MUTAȚIE: `verificari_drum` întoarce `[]` -> se salvează -> pică."""
    from core import facturi_recurente as fr
    r = _adauga(mediu, tert_nume="", client_id=7)
    assert _campuri(r) == ["fr-nume"] and fr.MESAJ_BENEFICIAR in r["eroare"], r
    from core import facturi_api
    r = _adauga(mediu, tert_cui="")
    with pytest.raises(ValueError) as fara_cod:   # refuzul emiterii obișnuite, pentru același beneficiar
        facturi_api.cere_cod_partener("", False, "Client Recurent SRL")
    assert _pe_campuri(r) == [("fr-cui", str(fara_cod.value))], r
    r = _adauga(mediu, linii=[dict(LINIE, articol_id=3)])
    assert _pe_campuri(r) == [("fr-l0-descriere", fr.MESAJ_ARTICOL_STOC % 1)], r
    r = _adauga(mediu, tert_cui="DE123456789")
    assert _pe_campuri(r) == [("fr-cui", fr.MESAJ_CLIENT_STRAIN % "DE123456789")], r
    assert _numar(mediu, "SELECT count(*) FROM %(s)s.facturi_recurente") == 0


def test_cronul_aplica_aceleasi_verificari_sabloanelor_vechi_si_poarta_platitorul_beneficiarului(mediu):
    """Două șabloane scrise direct în tabelă (ca înainte de 462, fără verificările de la salvare): unul fără denumirea beneficiarului
    nu se emite (eroarea în jurnalul cronului, nicio factură), celălalt se emite — iar factura lui poartă plătitorul de TVA al
    beneficiarului (din ANAF, ca drumul obișnuit `uc_tenants.facturi_emite`). Totalul: 100 + 21% = 121,00.
    MUTAȚIE: `verificari_drum(s)` scos din `emite_scadente` -> se emit două facturi -> pică; `tert_platitor_tva=` scos -> NULL -> pică."""
    from core import facturi_recurente as fr
    with mediu.cursor() as cur:
        for i, nume in ((1, None), (2, "Client Recurent SRL")):
            cur.execute("INSERT INTO %s.facturi_recurente (id, tert_nume, tert_cui, linii, zi_emitere) VALUES (%%s, %%s, %%s, %%s, 1)"
                        % _SCHEMA, (i, nume, CUI_CLIENT, json.dumps([LINIE])))
    e = fr.emite_scadente(_SCHEMA, AZI)
    assert [(x["sablon"], bool(x.get("eroare"))) for x in e if x.get("sablon") is not None] == [(1, True), (2, False)], e
    assert fr.MESAJ_BENEFICIAR in [x for x in e if x.get("sablon") == 1][0]["eroare"]
    with mediu.cursor() as cur:
        cur.execute("SELECT tert_nume, tert_platitor_tva, total::text, tva::text FROM %s.facturi" % _SCHEMA)
        assert cur.fetchall() == [("Client Recurent SRL", True, "121.00", "21.00")]
