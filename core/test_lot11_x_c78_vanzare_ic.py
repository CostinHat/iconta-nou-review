# -*- coding: utf-8 -*-
"""[lotul 11, subagentul x] C78 — „Vânzare intracomunitară” (Operațiuni, `uc_tenants.vanzare_ic`) scria DOUĂ note pe aceeași factură.

Constatarea (S2, la 451): emiterea facturii (`facturi_api.emite_factura` -> `creeaza_factura` -> `_conteaza_la_creare`) scrie deja nota
de contare 4111 = 707 (bunuri) / 704 (servicii); use-case-ul scria apoi încă o notă proprie 4111 = 707 pe aceeași factură
(`repo_contabilitate.nota_facturi_cu_factura` + `adauga_linie_client`). Venitul și creanța ieșeau dublate: 2.000 lei în registrul-jurnal
pentru o factură de 1.000. Reparația: nota livrării e chiar contarea de la emitere; contarea refuzată -> refuz numit, nimic scris.

Temei (anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt): OMFP 2634/2015 pct.58 lit.c — „fiecare dată înregistrată în contabilitate
trebuie să se regăsească în conținutul unui document, la care să poată avea acces atât beneficiarii, cât și organele de control”; Legea
82/1991 art.6 alin.(1) (anaf_surse/legea_82_1991_consolidat.txt) — „Orice operațiune economico-financiară efectuată se consemnează în
momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate”. Factura de 1.000 lei justifică 1.000 lei
de venit, nu 2.000. D390 / D300 citesc `facturi` (nu notele): baza lor rămâne 1.000 (proba de mai jos o arată).

GARDA pe clasă (structurală + funcțională): nicio funcție care emite o factură prin `emite_factura` / `creeaza_factura(..., "emisa")`
nu mai scrie ea însăși o notă (`nota_*`, `contabilizeaza`, `INSERT INTO inregistrari`) — contarea emiterii e singura; și, pe drumurile
din Operațiuni care produc o factură (vânzare IC bunuri / servicii), nicio factură nu rămâne cu ≥ 2 note de sursă „facturi”.

Schemă efemeră din `tenant_template.sql`, tranzacție anulată, date sintetice în 2099. CUI firmei: 14399840 (DANTE INTERNATIONAL SA, cifra
de control verificată cu algoritmul din CLAUDE.md). VIES simulat (răspuns „valid”), codul clientului DE811907980 (cel din proba R187)."""
import ast
import contextlib
import glob
import io
import os
from decimal import Decimal

import pytest

from core import db as _db, erori, tenant_provisioning as _tp

SCH = "tenant_test_lot11_x_c78"
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


@pytest.fixture
def conn(monkeypatch):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES (1,'X SRL',"
                            "'14399840','Str 1','Cluj-Napoca','CJ','4621','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar','Popescu',"
                            "'Ion','ADMINISTRATOR','SRL',200,'SDA','global_valoric')")
            from core import auth_api, intracomunitar, uc_comun, uc_tenants

            @contextlib.contextmanager
            def _gc(*a, **k):
                # ca `db.get_conn`: excepția întoarce tot ce a scris use-case-ul (aici: până la savepoint-ul cererii)
                with c.cursor() as cur:
                    cur.execute("SAVEPOINT cerere_x")
                try:
                    yield _P(c)
                except BaseException:
                    with c.cursor() as cur:
                        cur.execute("ROLLBACK TO SAVEPOINT cerere_x")
                    raise
            monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
            monkeypatch.setattr(intracomunitar, "verifica_vies", lambda cod: {
                "valid": True, "nume": "KUNDE GMBH", "adresa": "Berlin", "tara": "DE", "numar": cod[2:], "eroare": None})
            yield c
        finally:
            c.rollback()


def _vanzare(tip="bunuri", valoare=1000, data="2099-10-10"):
    from core import uc_tenants
    return uc_tenants.vanzare_ic(1, {"data": data, "valoare": valoare, "cod_tva_client": COD_CLIENT, "tip": tip,
                                     "dovada_transport": True, "descriere": "Marfa IC"}, {"uid": 1})


def _note_facturii(c, fid):
    with c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute("SELECT i.id, l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.factura_id = %s AND i.sursa = 'facturi' ORDER BY i.id, l.id", (fid,))
        return cur.fetchall()


def _facturi_cu_mai_multe_note(c):
    with c.cursor() as cur:
        cur.execute("SELECT factura_id, count(*) FROM %s.inregistrari WHERE sursa = 'facturi' AND factura_id IS NOT NULL "
                    "GROUP BY factura_id HAVING count(*) > 1" % SCH)
        return cur.fetchall()


def test_def_c78_vanzarea_ic_de_bunuri_are_o_singura_nota(conn):
    """Roșu înainte: 2 note (contarea emiterii + nota proprie), 4111 = 707 de două ori, 2.000 lei. Acum: 1 notă, cea a contării.
    MUTAȚIE: nota proprie pusă la loc (`nota_facturi_cu_factura` + `adauga_linie_client` după `fid`) -> pică."""
    r = _vanzare("bunuri")
    note = _note_facturii(conn, r["factura_id"])
    # OMFP 2634/2015 pct.58 lit.c: „fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul unui document”
    assert {n[0] for n in note} == {r["inregistrare_id"]}, note
    assert [(d, cr, s) for _i, d, cr, s in note if s] == [("4111", "707", Decimal("1000.00"))], note
    assert _facturi_cu_mai_multe_note(conn) == []


def test_def_c78_prestarea_ic_de_servicii_are_o_singura_nota(conn):
    """Aceeași clasă pe ramura „servicii” (contul de venit 704): o notă, 4111 = 704, 1.000 lei."""
    r = _vanzare("servicii")
    note = _note_facturii(conn, r["factura_id"])
    assert {n[0] for n in note} == {r["inregistrare_id"]}, note
    assert [(d, cr, s) for _i, d, cr, s in note if s] == [("4111", "704", Decimal("1000.00"))], note
    assert _facturi_cu_mai_multe_note(conn) == []


def test_c78_baza_d390_si_d300_ramane_1000(conn):
    """D390 și D300 citesc `facturi`, nu notele: baza livrării (L, 1.000) și a prestării (P, 1.000) e aceeași înainte și după reparație."""
    from core import d300, d390
    from core.common import Perioada
    _vanzare("bunuri")
    _vanzare("servicii")
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
    prof, facturi = d390.pull(conn, SCH, 2099, 10)
    res = d390.calcul_d390(prof, 2099, 10, facturi)
    # D390: o operațiune L și una P pe client, fiecare cu baza 1.000 (axa de pe factură, R186), totalul 2.000
    assert sorted((k[0], v) for k, v in res.ops.items()) == [("L", 1000), ("P", 1000)], res.ops
    assert res.total_baza == 2000, res.total_baza
    prof3, facturi3 = d300.pull(conn, SCH, Perioada(2099, luna=10))
    r3 = d300.calcul_d300(prof3, Perioada(2099, luna=10), facturi3)
    # D300 rd.1 (livrarea IC) și rd.3 (prestarea IC), rutarea din `d300.calcul_d300` pe categoria liniei / axa facturii: câte 1.000
    assert (r3.R["R1_1"], r3.R["R3_1"]) == (1000, 1000), {k: r3.R.get(k) for k in ("R1_1", "R3_1")}


def test_def_c78_contarea_refuzata_refuz_numit_nimic_scris(conn):
    """O notă manuală fără factură, 4111 = 707 1.000 în aceeași lună, oprește contarea automată (`POSIBILA_DUBLARE`): livrarea se refuză
    numit, iar nici factura, nici vreo notă pe ea nu rămân. Roșu înainte: factura emisă, nota proprie scrisă fără contare."""
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2099-10-05', 'Livrare DE (manual)', 'manual', 'ciorna') "
                    "RETURNING id")
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4111', '707', 1000)", (nid,))
        cur.execute("SELECT count(*) FROM facturi")
        inainte = cur.fetchone()[0]
    with pytest.raises(erori.DateInvalide) as e:
        _vanzare("bunuri")
    msg = e.value.args[0]   # mesajul refuzului (câmpul lui), nu reprezentarea excepției
    assert msg.startswith("Livrarea intracomunitară nu s-a înregistrat: nota contabilă a facturii nu s-a putut scrie (") and \
        msg.endswith("Nimic nu s-a scris."), msg
    assert msg == ("Livrarea intracomunitară nu s-a înregistrat: nota contabilă a facturii nu s-a putut scrie (există deja o notă care "
                   "pare să conteze factura asta, fără să o numească (nota din 05.10.2099). Nu se scrie automat: leag-o sau contează "
                   "manual.). Nimic nu s-a scris."), msg   # mesajul întreg (core/test_garzi_pe_text.py)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi")
        assert cur.fetchone()[0] == inainte
        cur.execute("SELECT count(*) FROM inregistrari WHERE factura_id IS NOT NULL")
        assert cur.fetchone()[0] == 0


# ── GARDA pe clasă: emiterea facturii își scrie singură nota; apelantul nu mai scrie una ─────────────────────────────────────────────
_EMIT = {"emite_factura", "creeaza_factura"}


def _nume(x):
    f = x.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)


def _emite_emisa(x):
    """Apelul emite o factură EMISĂ (singura direcție contată la creare, `facturi_api._conteaza_la_creare`)."""
    if _nume(x) == "emite_factura":
        return True
    if _nume(x) != "creeaza_factura":
        return False
    vals = [a for a in x.args] + [k.value for k in x.keywords if k.arg == "directie"]
    return any(isinstance(v, ast.Constant) and v.value == "emisa" for v in vals) or not any(
        isinstance(v, ast.Constant) and v.value == "primita" for v in vals)


def _scrie_nota(x):
    n = _nume(x) or ""
    if n.startswith("nota_") or n == "contabilizeaza":
        return True
    if n == "execute" and x.args:
        # tabelul în care scrie instrucțiunea, citit cu același cititor ca restul repo-ului (`scan_trasee.RE_W`), nu căutat ca șir
        from scripts import scan_trasee as _T
        txt = " ".join(v.value for v in ast.walk(x.args[0]) if isinstance(v, ast.Constant) and isinstance(v.value, str))
        return {m.group(2) for m in _T.RE_W.finditer(txt)} >= {"inregistrari"}
    return False


#: funcții care emit o factură emisă ȘI scriu legitim altă notă (alt fapt economic, nu contarea facturii), cu motivul
EXCEPTII = {}


def _incalcari(fisiere):
    rele = []
    for f in fisiere:
        arb = ast.parse(io.open(f, encoding="utf-8").read())
        for fn in ast.walk(arb):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or fn.name in _EMIT:
                continue
            apeluri = [x for x in ast.walk(fn) if isinstance(x, ast.Call)]
            if any(_emite_emisa(x) for x in apeluri):
                note = [x.lineno for x in apeluri if _scrie_nota(x)]
                if note and (os.path.relpath(f, RAD), fn.name) not in EXCEPTII:
                    rele.append((os.path.relpath(f, RAD), fn.name, note))
    return rele


def _fisierele_aplicatiei():
    return [f for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))) + [os.path.join(RAD, "main.py")]
            if not os.path.basename(f).startswith(("test_", "migrare_"))]


def test_GARDA_c78_cine_emite_o_factura_nu_mai_scrie_o_nota_proprie():
    """Clasa C78: o funcție care emite o factură EMISĂ și scrie apoi ea însăși o notă (pe aceeași factură) dublează contarea făcută la
    emitere. MUTAȚIE: nota proprie pusă la loc în `vanzare_ic` -> pică, numind funcția."""
    rele = _incalcari(_fisierele_aplicatiei())
    assert rele == [], "emit o factură și scriu încă o notă (contarea emiterii e singura, OMFP 2634/2015 pct.58 lit.c): %s" % rele


def test_GARDA_c78_anti_vacuu_universul_are_emitentii(tmp_path):
    """Gardul vede emitentii reali (vânzarea IC, emiterea din ecran, stornarea, magazinul) și se aprinde pe un emitent sintetic care scrie
    o notă — altfel ar fi verde pe un univers gol."""
    emitenti = set()
    for f in _fisierele_aplicatiei():
        for fn in ast.walk(ast.parse(io.open(f, encoding="utf-8").read())):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name not in _EMIT and any(
                    isinstance(x, ast.Call) and _emite_emisa(x) for x in ast.walk(fn)):
                emitenti.add(fn.name)
    assert {"vanzare_ic", "facturi_emite", "proforma_transforma", "storneaza", "_importa"} <= emitenti, emitenti
    p = tmp_path / "zt_emitent.py"
    p.write_text("def f(conn, cur, s):\n    r = facturi_api.emite_factura(conn, [])\n"
                 "    repo_contabilitate.nota_facturi_cu_factura(cur, s, '2099-01-01', r['factura_id'], 'x')\n", encoding="utf-8")
    q = tmp_path / "zt_primita.py"   # primita: contarea NU se face la creare, nota proprie e singura (borderou, achiziții) — nu e încălcare
    q.write_text("def g(conn, cur, s):\n    r = facturi_api.creeaza_factura(conn, numar='1', data_emitere='2099-01-01', directie='primita', linii=[])\n"
                 "    repo_contabilitate.nota_facturi_cu_factura(cur, s, '2099-01-01', r['factura_id'], 'x')\n", encoding="utf-8")
    assert [(x[1], len(x[2])) for x in _incalcari([str(p), str(q)])] == [("f", 1)]
