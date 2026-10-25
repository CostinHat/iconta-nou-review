# -*- coding: utf-8 -*-
"""[lotul 12, C110] Prestarea intracomunitară din Operațiuni (`uc_tenants.vanzare_ic`) nu transmitea starea de plătitor a firmei.

Constatarea (găsită de Code la C84): `vanzare_ic` chema `facturi_api.emite_factura` fără `platitor_tva`, deci cu implicitul „plătitor”;
toate celelalte emiteri (`facturi_emite`, API-ul `uc_api`, magazinul `woocommerce._importa`, facturile recurente) o citesc din profil
(`uc_comun._platitor_tva_firma`). Investigația, la sursă:
  · EFECTUL PE NOTĂ / DECLARAȚII al parametrului lipsă: niciunul. `creeaza_factura` (punctul unic al emiterii) recitește
    `firma_profil.platitor_tva` și pune din nou categoria liniei cu 0% (`categorii_tva.verifica_linii`): la neplătitor „neplatitor” (O),
    la plătitor „serviciu_extern” (AE). Nota e contarea de la emitere (4111 = 704), iar D390 ia axa „servicii” de pe document (P).
    `test_c110_efectul_pe_factura_nota_si_d390` o arată, pe plătitor și pe neplătitorul înregistrat art.317 (ca F3).
  · REPARAȚIA: `vanzare_ic` citește starea ca celelalte emiteri și o dă mai departe — verificarea liniilor din `emite_factura`, făcută
    înainte de rezervarea numărului, nu mai rulează pe o stare presupusă. Garda pe clasă: nicio emitere nu se mai bizuie pe implicit.

Temei (anaf_surse/cod_fiscal_227_2015_consolidat.txt):
  · CF art.317 alin.(1) lit.b — se înregistrează în scopuri de TVA persoana impozabilă din România „neînregistrat[ă] și care nu [are]
    obligația să se înregistreze conform art. 316 [...] dacă prestează servicii care au locul în alt stat membru, pentru care beneficiarul
    serviciului este persoana obligată la plata taxei [...], înainte de prestarea serviciului”;
  · CF art.325 alin.(1) lit.c — „Orice persoană impozabilă înregistrată în scopuri de TVA conform art. 316 sau 317” declară în D390
    „prestările de servicii prevăzute la art. 278 alin. (2) efectuate în beneficiul unor persoane impozabile nestabilite în România, dar
    stabilite în Uniunea Europeană”;
  · CF art.310 alin.(10) lit.b — neplătitorul „nu are voie să menționeze taxa pe factură” (linia rămâne cu 0%).

Schemă efemeră din `tenant_template.sql`, tranzacție anulată, date sintetice în 2099. CUI firmei: 14399840 (cifra de control verificată
cu algoritmul din CLAUDE.md). VIES simulat („valid”), codul clientului DE811907980 (cel din proba R187 / C78)."""
import ast
import contextlib
import glob
import inspect
import io
import os
from decimal import Decimal

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot12_c110"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COD_CLIENT = "DE811907980"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _P:
    """Conexiunea testului, dată use-case-ului: commit / rollback nu închid tranzacția testului (o anulează fixture-ul)."""
    def __init__(s, c): s._c = c
    def commit(s): pass
    def rollback(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


#: (plătitor, înregistrat art.317, tip decont): plătitorul art.316 și neplătitorul înregistrat art.317 (forma firmei de test F3)
FIRME = {"platitor": (True, False, "lunar"), "neplatitor_art317": (False, True, None)}


@pytest.fixture(params=sorted(FIRME))
def conn(request, monkeypatch):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    platitor, art317, decont = FIRME[request.param]
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "inreg_art317,declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,serie_factura,"
                            "metoda_stoc) VALUES (1,'X SRL','14399840','Str 1','Cluj-Napoca','CJ','6201','BCR','RO49RNCB0000000000000001',"
                            "'0700000000',%s,%s,%s,'Popescu','Ion','ADMINISTRATOR','SRL',200,'SDC','global_valoric')",
                            (platitor, decont, art317))
            from core import auth_api, intracomunitar, uc_comun, uc_tenants

            @contextlib.contextmanager
            def _gc(*a, **k):
                # ca `db.get_conn`: excepția întoarce tot ce a scris use-case-ul (aici: până la savepoint-ul cererii)
                with c.cursor() as cur:
                    cur.execute("SAVEPOINT cerere_c110")
                try:
                    yield _P(c)
                except BaseException:
                    with c.cursor() as cur:
                        cur.execute("ROLLBACK TO SAVEPOINT cerere_c110")
                    raise
            monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
            monkeypatch.setattr(intracomunitar, "verifica_vies", lambda cod: {
                "valid": True, "nume": "KUNDE GMBH", "adresa": "Berlin", "tara": "DE", "numar": cod[2:], "eroare": None})
            t = _P(c)
            t.platitor = platitor   # starea scrisă în profil, pentru aserțiuni
            yield t
        finally:
            c.rollback()


def _prestare(valoare=1000, data="2099-10-10"):
    from core import uc_tenants
    return uc_tenants.vanzare_ic(1, {"data": data, "valoare": valoare, "cod_tva_client": COD_CLIENT, "tip": "servicii",
                                     "cont_venit": "704", "descriere": "Consultanta IC"}, {"uid": 1})


def _sql(c, q, args=()):
    with c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, args)
        return cur.fetchall()


def test_c110_vanzarea_ic_transmite_platitorul_firmei(conn, monkeypatch):
    """Emiterea facturii prestării primește starea de plătitor din profil (aceeași citire ca `facturi_emite`), nu implicitul ei.
    MUTAȚIE: `platitor_tva=_platitor` scos din apelul `emite_factura` din `uc_tenants.vanzare_ic` -> pe neplătitor primește implicitul
    True -> ROȘU."""
    from core import facturi_api, uc_comun
    primit = []
    original = facturi_api.emite_factura
    implicit = inspect.signature(original).parameters["platitor_tva"].default

    def _spion(*a, **k):
        primit.append(k.get("platitor_tva", implicit))
        return original(*a, **k)
    monkeypatch.setattr(facturi_api, "emite_factura", _spion)
    _prestare()
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
    assert primit == [uc_comun._platitor_tva_firma(conn)] == [conn.platitor], (primit, conn.platitor)


def test_c110_efectul_pe_factura_nota_si_d390(conn):
    """Efectul stării firmei pe prestarea IC, cap la cap pe date: categoria liniei din regimul firmei (plătitor -> `serviciu_extern`,
    art.278 alin.(2); [lotul 12, C156, decizia Costin 12.3 pct.3] neplătitorul înregistrat art.317 -> aceeași, `PRESTARE_IC_317`: „fără TVA
    român, mențiunea «taxare inversă», codul RO art. 317 pe factură, P în D390” — cota 0, CF art.310 alin.(10) lit.b; înainte `NEPLATITOR`,
    O), axa „servicii” înghețată pe factură, o singură notă 4111 = 704
    (OMFP 2634/2015 pct.58 lit.c) și D390 cu P pe baza facturii (CF art.325 alin.(1) lit.c — și pentru înregistratul art.317).
    Verde și fără parametrul reparat: `creeaza_factura` recitește profilul (de aceea C110, așa cum fusese consemnată, nu schimba nici
    nota, nici declarațiile)."""
    from core import categorii_tva, d390
    r = _prestare()
    fid = r["factura_id"]
    linii = _sql(conn, "SELECT categorie_tva, cota_tva FROM factura_linii WHERE factura_id = %s", (fid,))
    asteptat = categorii_tva.PRESTARE_IC_317 if conn.platitor is False else "serviciu_extern"   # [C156] neplătitorul art.317: AE
    assert linii == [(asteptat, Decimal("0.00"))], linii
    assert _sql(conn, "SELECT axa_ic, tert_tara FROM facturi WHERE id = %s", (fid,)) == [("servicii", "DE")]
    note = _sql(conn, "SELECT i.id, l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l "
                      "ON l.inregistrare_id = i.id WHERE i.factura_id = %s AND i.sursa = 'facturi' ORDER BY i.id, l.id", (fid,))
    assert [(d, c, s) for _i, d, c, s in note if s] == [("4111", "704", Decimal("1000.00"))], note
    assert {n[0] for n in note} == {r["inregistrare_id"]}, note
    prof, facturi = d390.pull(conn, SCH, 2099, 10)
    res = d390.calcul_d390(prof, 2099, 10, facturi)
    assert sorted((k[0], v) for k, v in res.ops.items()) == [("P", 1000)], res.ops


# ── GARDA pe clasă: nicio emitere nu se bizuie pe implicitul „plătitor” al lui `emite_factura` ────────────────────────────────────────
def _nume(x):
    f = x.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)


def _emiteri(fisiere):
    """[(fișier, funcția care cheamă, linia, transmite platitor_tva)] pentru fiecare apel `emite_factura(...)`."""
    out = []
    for f in fisiere:
        arb = ast.parse(io.open(f, encoding="utf-8").read())
        for fn in ast.walk(arb):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or fn.name == "emite_factura":
                continue
            for x in ast.walk(fn):
                if isinstance(x, ast.Call) and _nume(x) == "emite_factura":
                    out.append((os.path.relpath(f, RAD), fn.name, x.lineno, any(k.arg == "platitor_tva" for k in x.keywords)))
    return out


def _fisierele_aplicatiei():
    return [f for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))) + [os.path.join(RAD, "main.py")]
            if not os.path.basename(f).startswith(("test_", "migrare_"))]


def test_GARDA_c110_orice_emitere_transmite_platitorul_firmei():
    """Clasa C110: o emitere care nu dă `platitor_tva` primește implicitul „plătitor” — pe o firmă neplătitoare verificarea liniilor de
    dinaintea numărului rulează pe o stare falsă. MUTAȚIE: `platitor_tva=_platitor` scos din `vanzare_ic` -> pică, numind funcția."""
    rele = [(f, fn, ln) for f, fn, ln, are in _emiteri(_fisierele_aplicatiei()) if not are]
    assert rele == [], "emiteri fără starea de plătitor a firmei (implicitul „plătitor” al lui emite_factura): %s" % rele


def test_GARDA_c110_anti_vacuu_universul_are_emitentii(tmp_path):
    """Gardul vede emitentii reali (prestarea IC, emiterea din ecran, API-ul, magazinul, recurentele) și se aprinde pe un apel sintetic
    fără `platitor_tva` — altfel ar fi verde pe un univers gol."""
    emitenti = {fn for _f, fn, _l, _a in _emiteri(_fisierele_aplicatiei())}
    assert {"vanzare_ic", "facturi_emite", "_importa"} <= emitenti, emitenti
    p = tmp_path / "zt_emitere.py"
    p.write_text("def f(conn):\n    return facturi_api.emite_factura(conn, [])\n"
                 "def g(conn):\n    return facturi_api.emite_factura(conn, [], platitor_tva=False)\n", encoding="utf-8")
    assert [(fn, are) for _f, fn, _l, are in _emiteri([str(p)])] == [("f", False), ("g", True)]
