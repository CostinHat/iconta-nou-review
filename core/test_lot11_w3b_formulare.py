# -*- coding: utf-8 -*-
"""[lotul 11, subagentul w3b, deficiența 440 pe server — comanda Costin 11.1 pct.16, verbatim] „toate erorile apar deodată, fiecare cu
textul ei, în casetă și lângă câmp. Fără «motivul e mai sus». Pe toată aplicația.”

Formularele din lista U0 (`u0_lista_server.md`, punctele B21–B40) care refuzau la PRIMA greșeală a omului: fiecare corp de mai jos are
două (sau mai multe) greșeli, iar refuzul trebuie să le poarte pe TOATE în `erori_campuri` (`camp` = id-ul din ecran sau numele din
cerere), cu `mesaj` care le spune pe toate (`core.erori.ErorileFormularului`). Refuzurile de STARE a evidenței (perioada închisă, stocul
insuficient, CUI-ul deja în portofoliu) rămân unice — nu se testează aici.

Temei: N/A — contractul refuzului (G10, DS cap.6 v2.30 pct.4 „fail-fast e INTERZIS pe formularele multi-câmp”, v2.99 440).

MUTAȚII (fiecare face testul lui roșu; rulate cu backup de conținut, nu git checkout): vezi raportul w3b, secțiunea 3.
"""
import contextlib
import io
import os
from types import SimpleNamespace

import pytest

from core import db as _db, erori, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCH = "efemer_lot11_w3b_form"


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
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCH)   # pe tranzacție, nu rămâne pe conexiunea din pool
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,serie_factura,"
                            "urmator_numar_factura) VALUES (1,'W3B SRL','14399840','Str 1','Cluj-Napoca','CJ','4621','BCR',"
                            "'RO49RNCB0000000000000001','0700000000',true,'lunar','Popescu','Ion','ADMINISTRATOR','SRL',200,'W3B',7)")
            yield c
        finally:
            c.rollback()


def _uc(monkeypatch, c):
    """Use-case-ul pe conexiunea testului (tranzacția anulată la final), fără firmă în portofoliu."""
    from core import uc_tenants, uc_comun

    @contextlib.contextmanager
    def _gc(schema=None):
        yield c
    monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: _SCH)
    monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", lambda conn, uid, tid: _SCH)
    return uc_tenants


def _campuri(det):
    return [c["camp"] for c in det["erori_campuri"]]


def _randuri(mesaj):
    """Mesajul refuzului pe rânduri: antetul, apoi câte un rând „— …” pentru fiecare eroare (contractul `ErorileFormularului`: „toate
    deodată, fiecare cu textul ei”). Se compară lista întreagă, nu „fragmentul apare în mesaj” (core/test_garzi_pe_text.py)."""
    antet, *motive = mesaj.split("\n— ")
    return [antet] + motive


# ── B21 · numerotarea facturilor ────────────────────────────────────────────────────────────────────────────────────────────
def test_b21_numerotarea_refuza_seria_si_numarul_deodata(conn, monkeypatch):
    """Seria goală ȘI numărul de start sub contor (7): două erori. MUTAȚIE: `return dict(er.detaliu() …)` mutat în ramura seriei ->
    numărul lipsește -> pică."""
    from core import facturi_api
    r = facturi_api.seteaza_numerotare(conn, serie="   ", numar_start=3)
    assert r["ok"] is False and _campuri(r) == ["serie", "numar_start"], r       # 440: „toate erorile apar deodată”
    assert _randuri(r["mesaj"]) == [
        'Numerotarea nu s-a salvat:',
        'Seria e goală (numai spații). Nu se poate ghici dacă ai vrut s-o ștergi sau ai greșit tastarea, iar seria firmei e pe documentele deja emise.',
        'Numărul de start 3 e sub cel la care a ajuns seria (7). Dat înapoi, următoarea factură ar primi un număr deja emis, iar secvența cerută de OMFP 2634/2015 anexa 1 pct.24 s-ar rupe. Un număr mai mare sau egal se acceptă.',
    ], r["mesaj"]   # „fiecare cu textul ei”
    uc = _uc(monkeypatch, conn)
    with pytest.raises(erori.CerereGresita) as e:
        uc.facturi_numerotare_set(1, SimpleNamespace(serie="", numar_start="x"), {"uid": 1})
    assert _campuri(e.value.detaliu) == ["serie", "numar_start"], e.value.detaliu


# ── B22 · șablonul de contract ──────────────────────────────────────────────────────────────────────────────────────────────
def test_b22_sablonul_refuza_numele_si_toate_marcajele(conn, monkeypatch):
    """Fără nume + două marcaje necunoscute: trei erori, lângă `c-nume` și `c-continut`. MUTAȚIE: `return` după numele gol -> pică."""
    from core import contracte_api
    r = contracte_api.salveaza_sablon(conn, _SCH, None, " ", "Contract {{partener_nume}} {{zz}} {{aa}}", 1)
    assert r["ok"] is False and r["cod"] == "NUME_GOL" and _campuri(r) == ["c-nume", "c-continut", "c-continut"], r
    assert _randuri(r["mesaj"]) == [
        'Șablonul nu s-a salvat:',
        'Scrie numele șablonului.',
        'Marcajul {{aa}} nu e în lista „Marcaje disponibile”: ar rămâne necompletat în contract.',
        'Marcajul {{zz}} nu e în lista „Marcaje disponibile”: ar rămâne necompletat în contract.',
    ], r["mesaj"]
    uc = _uc(monkeypatch, conn)
    with pytest.raises(erori.DateInvalide) as e:
        uc.contracte_sabloane_salveaza(1, {"nume": "", "continut": ""}, {"uid": 1})
    assert _campuri(e.value.detaliu) == ["c-nume", "c-continut"], e.value.detaliu


# ── B23 · factura recurentă ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_b23_factura_recurenta_refuza_liniile_beneficiarul_si_ziua_deodata(conn):
    """Fără linii, fără beneficiar, ziua 40: trei erori, pe id-urile din ecran (`fr-zi`, nu `fr-zi_emitere`, care nu există).
    MUTAȚIE: `return` imediat după liniile lipsă -> pică."""
    from core import facturi_recurente
    _em = {"scadenta_zile": 15, "data_inceput": "2026-01-01", "valabil_pana": "oprire", "mod_emitere": "automata", "trimite_spv": False}   # [lotul 13, 680] întrebările emiterii, date: testul e despre linii / beneficiar / zi
    r = facturi_recurente.adauga(conn, _SCH, dict({"linii": [], "tert_nume": "", "zi_emitere": 40}, **_em))
    assert _campuri(r) == ["fr-linii", "fr-nume", "fr-zi"], r
    r = facturi_recurente.adauga(conn, _SCH, dict({"linii": [{"descriere": "", "cantitate": 1, "um": "buc", "pret_unitar": 10}], "zi_emitere": "prima"},   # [regula UM] UM-ul dat: testul e despre denumire
                                                  **_em))
    assert _campuri(r) == ["fr-nume", "fr-zi", "fr-l0-descriere"], r
    assert _randuri(r["eroare"]) == [
        'Șablonul nu s-a salvat:',
        'Scrie beneficiarul facturii (denumirea clientului).',
        "Ziua emiterii: 'prima' nu e un număr. Scrie o zi între 1 și 28.",
        'Linia 1: denumire — Denumirea liniei e obligatorie pe factură. Scrie ce se facturează.',
    ], r["eroare"]


# ── B27 · declarația marcată „depusă în afara iConta” ───────────────────────────────────────────────────────────────────────
def test_b27_depunerea_externa_refuza_data_si_recipisa_deodata(monkeypatch):
    """Data în viitor + recipisa peste 100 de caractere: două erori. MUTAȚIE: `er.refuza()` mutat înaintea recipisei -> pică."""
    from core import uc_comun, uc_control_fiscal as ucf
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: _SCH)
    with pytest.raises(erori.DateInvalide) as e:
        ucf.control_fiscal_depusa_extern(1, {"tip": "d300", "an": 2026, "luna": 8, "data_depunere": "2999-01-01",
                                             "recipisa": "R" * 101}, {"uid": 1})
    assert _campuri(e.value.detaliu) == ["data_depunere", "recipisa"], e.value.detaliu
    assert _randuri(e.value.detaliu["mesaj"]) == [
        'Marcarea nu s-a salvat:',
        'Data depunerii (01.01.2999) e în viitor.',
        'Numărul recipisei are peste 100 de caractere.',
    ], e.value.detaliu["mesaj"]


# ── B28 · ordinul de compensare ─────────────────────────────────────────────────────────────────────────────────────────────
def test_b28_compensarea_refuza_data_numarul_si_perechile_deodata():
    """Fără dată, numărul peste 40 de caractere, perechile nu sunt listă: trei erori, înainte de orice citire din bază.
    MUTAȚIE: refuzul numărului ridicat pe loc (forma veche) -> data lipsește -> pică."""
    from core import uc_compensari
    with pytest.raises(erori.CerereGresita) as e:
        uc_compensari.compensari_genereaza(1, {"data": "", "numar": "N" * 41, "perechi": "x"}, {"uid": 0})
    assert _campuri(e.value.detaliu) == ["cz-data", "cz-numar"], e.value.detaliu
    assert _randuri(e.value.detaliu["mesaj"]) == [
        'Compensarea nu s-a generat:',
        'Perechile de facturi trebuie trimise ca listă.',
        'Alege data ordinului de compensare: la ea se sting datoriile.',
        'Numărul ordinului de compensare are cel mult 40 de caractere.',
    ], e.value.detaliu["mesaj"]


# ── B29 · transferul între locații ──────────────────────────────────────────────────────────────────────────────────────────
def test_b29_transferul_refuza_locatia_cantitatea_si_data_deodata(conn):
    """Aceeași locație + cantitatea zero + data greșită: trei erori, lângă `tr-in`, `tr-cant`, `tr-data`; nimic scris.
    MUTAȚIE: `return` pe locația dublată (forma veche) -> pică."""
    from core import stocuri_cv_api as cva
    a = cva.intrare(conn, _SCH, {"denumire": "Marfa W3B", "um": "buc", "data": "2099-10-01", "cantitate": 5, "pret_unitar": 2,
                                 "document": "Inventar inițial probă"})
    r = cva.transfer(conn, _SCH, {"articol_id": a["articol_id"], "din_locatie": "Depozit", "in_locatie": "Depozit", "cantitate": 0,
                                  "data": "31.10.2099"})
    assert _campuri(r) == ["tr-in", "tr-cant", "tr-data"], r
    assert _randuri(r["eroare"]) == [
        'Transferul nu s-a făcut:',
        'Locația destinație e aceeași cu locația sursă: alege altă locație.',
        'Cantitatea transferată trebuie să fie mai mare ca zero (are 0 buc).',
        "data '31.10.2099' nu e în formatul AAAA-LL-ZZ. Se cere o dată calendaristică, fiindcă înregistrarea se face la momentul operațiunii, iar ordinea cronologică a registrului-jurnal atârnă de ea",
    ], r["eroare"]     # cantitatea cu unitatea articolului, în formatul românesc
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM miscari_stoc WHERE articol_id = %s", (a["articol_id"],))
        assert cur.fetchone()[0] == 1               # numai intrarea; transferul n-a scris nimic


# ── B31 · rețeta ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_b31_reteta_refuza_denumirea_pretul_si_ingredientele_deodata(conn):
    """Fără denumire, prețul peste coloană, un ingredient fără articol: trei erori. MUTAȚIE: `return` pe denumirea lipsă -> pică."""
    from core import retete_api
    r = retete_api.salveaza(conn, _SCH, {"denumire": "", "pret_fara_tva": 1e11, "linii": [{"articol_id": None, "cantitate": 2}]})
    assert _campuri(r) == ["rt-den", "rt-pret", "rt-l0-articol"], r


# ── B32 · registratura ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_b32_registratura_refuza_langa_camp(conn, monkeypatch):
    """Data greșită -> lângă `rg-data`; descrierea goală -> lângă `rg-desc` (înainte: text fără câmp). PARȚIAL: cele două se adună
    deodată numai după patch-ul cerut în `registratura_api.inregistreaza` (raportul w3b, secțiunea 10). MUTAȚIE: harta `campuri` golită
    -> `erori_campuri` gol -> pică."""
    uc = _uc(monkeypatch, conn)
    with pytest.raises(erori.DateInvalide) as e:
        uc.registratura_creeaza(1, {"directie": "intrare", "data": "2026-13-01", "descriere": "x"}, {"uid": 1})
    assert _campuri(e.value.detaliu) == ["rg-data"], e.value.detaliu
    with pytest.raises(erori.DateInvalide) as e:
        uc.registratura_creeaza(1, {"directie": "intrare", "data": "2026-10-01", "descriere": " "}, {"uid": 1})
    assert _campuri(e.value.detaliu) == ["rg-desc"], e.value.detaliu


# ── B39 · firma nouă ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_b39_firma_noua_refuza_denumirea_cui_ul_si_emailul_deodata(monkeypatch):
    """Fără denumire, CUI cu cifra de control greșită (14399841; corect 14399840), email fără „@”: trei erori, înainte de orice
    scriere. MUTAȚIE: refuzul emailului ridicat pe loc (forma veche) -> pică."""
    from core import uc_comun, uc_tenants
    assert _tp.cui_valid("14399840") and not _tp.cui_valid("14399841")   # algoritmul oficial (CLAUDE.md, „Date de test”)
    monkeypatch.setattr(uc_comun, "_TENANT_TEMPLATE", "--")
    with pytest.raises(erori.CerereGresita) as e:
        uc_tenants.tenant_creeaza(SimpleNamespace(nume=" ", cui="14399841", email_client="fara-arond", tip_firma="srl"),
                                  {"uid": 1, "firm": 1})
    assert _campuri(e.value.detaliu) == ["nume", "cui", "email_client"], e.value.detaliu


# ── B40 · asistentul invitat ────────────────────────────────────────────────────────────────────────────────────────────────
def test_b40_emailul_asistentului_refuzat_langa_camp():
    """Emailul invalid stă lângă câmpul lui (`email` -> `asi-email` pe ecran), nu numai ca frază. MUTAȚIE: forma veche
    (`DateInvalide(EMAIL_INVALID)`) -> pică."""
    from core import uc_asistenti
    with pytest.raises(erori.DateInvalide) as e:
        uc_asistenti.asistent_creeaza(SimpleNamespace(email="«»@#$%", nume="", poate_pregati=False, poate_valida=False,
                                                      poate_depune=False, firme=[]), {"uid": 1, "firm": 1, "rol": "admin_cabinet"})
    assert _campuri(e.value.detaliu) == ["email"], e.value.detaliu


# ── B37 · balanța de deschidere ─────────────────────────────────────────────────────────────────────────────────────────────
def test_b37_balanta_refuza_contul_din_afara_planului_si_metoda_lipsa_deodata(conn, monkeypatch):
    """Contul 999 (în afara planului legal) + sold pe 371 fără metoda de stoc: două erori, nimic scris. MUTAȚIE: refuzul contului
    ridicat pe loc (forma veche) -> metoda lipsește din refuz -> pică."""
    uc = _uc(monkeypatch, conn)
    r = lambda cont, d, c: SimpleNamespace(cont=cont, denumire="", debit=d, credit=c, rand_fisier=None)   # noqa: E731
    corp = SimpleNamespace(randuri=[r("371", 1000, 0), r("999", 0, 500), r("1012", 0, 500)], data_referinta="2099-09-30",
                           inlocuieste=False, metoda_stoc=None)
    with pytest.raises(erori.DateInvalide) as e:
        uc.solduri_salveaza(1, corp, {"uid": 7})
    assert _campuri(e.value.detaliu) == ["metoda_stoc"], e.value.detaliu
    assert _randuri(e.value.detaliu["mesaj"]) == [
        'Balanța nu s-a salvat:',
        'Contul 999 nu există în planul de conturi al normei firmei, deci balanța nu se poate prelua așa: corectează contul în fișier (un analitic se scrie sub sinteticul lui, de exemplu 401.00012) și încarcă din nou.',
        'Balanța are sold pe mărfuri (371): alege metoda de stoc a firmei — global-valoric (preț cu amănuntul) sau cantitativ-valoric (fișe de magazie, CMP). De ea depinde cum se descarcă marfa; fără ea nu se emite nicio factură cu marfă.',
    ], e.value.detaliu["mesaj"]
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM solduri_initiale")
        assert cur.fetchone()[0] == 0
