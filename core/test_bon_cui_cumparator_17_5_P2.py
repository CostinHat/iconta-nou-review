# -*- coding: utf-8 -*-
"""[lotul 17.5-P2, AC153 și AC154 din constatari_audit_complet.tsv; decizii_17_5_P2.txt] Scris de arhitect; Code nu îl modifică: dacă pică pe C, repară aplicația.
Probă pe bază: pică (core/bon_tva_deductibil.py și core/migrare_bon_cui_cumparator.py nu există); pe C: trece.

CE FACE IMPOSIBIL: (a) un bon fără codul firmei cumpărătoare, sau cu alt cod, care își dedude TVA la 4426; (b) un bon cu codul firmei dar peste 100 euro,
tratat ca verde fără nicio observație; (c) un motiv de verdict fără text sau cu text fără temei; (d) o coloană `bonuri.cui_cumparator` care nu e în șablonul
firmelor noi sau pe care migrarea n-o adaugă la o schemă existentă, sau care nu e idempotentă; (e) un bon vechi (coloana NULL) tratat ca «fără cod»; (f) parametrul nou al lui adauga_bon pus în coloana greșită sau uitat în apelul din portal_bon; (g) data bonului (șir) dată neconvertită funcțiilor de curs; (h) TVA 0 cu observație de TVA nedeductibil.
TEMEI (citit pe ~/iconta_nou/anaf_surse): Cod fiscal art. 319 alin. (12) lit. a) (cod_fiscal_227_2015_consolidat.txt:8057), alin. (21) lit. f) (:8061),
art. 290 alin. (2) (:7484); HG 1/2016 pct. 69 alin. (6) (hg_1_2016_norme_cod_fiscal.txt:2131); Cod fiscal art. 25 alin. (3) lit. a) (:1335) și lit. l) (:1367),
art. 298 alin. (1) (:7708)."""
import os
import uuid
from decimal import Decimal

import pytest

from core import db as _db, migrari_registru

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_p_" + uuid.uuid4().hex
FIRMA = "401002001"


def _m():
    from core import bon_tva_deductibil as m
    return m


# ── verdictul (funcție pură) ────────────────────────────────────────────────────────────────

def test_verdictul_si_precedenta_motivelor():
    m = _m()
    # 1. coloana NULL = bon încărcat înainte de citirea codului: nu se știe, comportamentul de azi rămâne (TVA dedus), cu observație
    assert m.verdict(None, FIRMA, 50, Decimal("5")) == ("de_verificat", "neextras")
    # 2. citit și absent de pe bon (șirul gol sau doar spații): TVA nedeductibil
    assert m.verdict("", FIRMA, 50, Decimal("5")) == ("nu", "fara_cod")
    assert m.verdict("   ", FIRMA, 50, Decimal("5")) == ("nu", "fara_cod")
    # 3. alt cod decât al firmei (forma păstrată: fără spații, fără «RO» în fața cifrelor — core/cui_forma.py: stocare)
    assert m.verdict("RO 14399840", FIRMA, 50, Decimal("5")) == ("nu", "alt_cod")
    # 4. codul firmei, în orice scriere, sub sau la 100 euro (total cu TVA în lei; 100 euro × curs 5 = 500 lei): verde
    assert m.verdict("RO401002001", FIRMA, 500, Decimal("5")) == ("da", "ok")
    assert m.verdict("RO 401 002 001", "401002001", Decimal("499.99"), Decimal("5")) == ("da", "ok")
    assert m.verdict("401002001", "RO401002001", 10, Decimal("5")) == ("da", "ok")
    # 5. peste 100 euro: TVA rămâne dedus, cu observația că art. 319 alin. (13) cere verificare
    assert m.verdict("401002001", FIRMA, Decimal("500.01"), Decimal("5")) == ("de_verificat", "peste_100")
    # 6. fără curs: pragul nu se poate verifica, TVA rămâne dedus, cu observație
    assert m.verdict("401002001", FIRMA, 10, None) == ("de_verificat", "curs_lipsa")
    # 7. firma fără cod în Date firmă: nu se poate compara
    assert m.verdict("401002001", None, 10, Decimal("5")) == ("de_verificat", "firma_fara_cod")
    assert m.verdict("401002001", "", 10, Decimal("5")) == ("de_verificat", "firma_fara_cod")
    # precedența: codul decide înaintea sumei și a cursului
    assert m.verdict("", FIRMA, 9999, None) == ("nu", "fara_cod")
    assert m.verdict("14399840", FIRMA, 9999, None) == ("nu", "alt_cod")
    assert m.verdict(None, FIRMA, 9999, None) == ("de_verificat", "neextras")
    assert m.verdict("401002001", FIRMA, 9999, None) == ("de_verificat", "curs_lipsa")


def test_textele_au_temei_si_nu_au_identificatori_de_cod():
    m = _m()
    t = {k: m.text(k, "14399840", FIRMA) for k in ("ok", "fara_cod", "alt_cod", "neextras", "peste_100", "curs_lipsa", "firma_fara_cod")}
    assert all(isinstance(v, str) and len(v) > 40 for v in t.values())
    assert t["ok"].startswith("TVA deductibil:") and "art. 319 alin. (12) lit. a" in t["ok"]
    assert t["fara_cod"].startswith("TVA nedeductibil: pe bon nu este înscris codul fiscal al firmei cumpărătoare")
    assert "HG 1/2016 pct. 69 alin. (6)" in t["fara_cod"] and "art. 319 alin. (12) și (21)" in t["fara_cod"]
    assert t["alt_cod"].startswith("TVA nedeductibil: codul fiscal de pe bon (14399840) nu este al firmei (401002001)")
    assert "art. 319 alin. (21) lit. f" in t["alt_cod"]
    assert "art. 319 alin. (13)" in t["peste_100"] and "art. 290 alin. (2)" in t["peste_100"]
    assert "art. 319 alin. (12) lit. a" in t["curs_lipsa"]
    for k, v in t.items():
        assert not any(x in v for x in ("cui_cumparator", "core/", "None", "null", "{", "}")), (k, v)
    assert all(v.startswith("TVA nedeductibil:") == (k in ("fara_cod", "alt_cod")) for k, v in t.items() if k != "ok")


def test_notele_de_cont_au_temei_numai_unde_exista_limita():
    m = _m()
    n6022 = m.nota_cont("6022")
    assert n6022 and "art. 25 alin. (3) lit. l" in n6022 and "art. 298 alin. (1)" in n6022 and "50%" in n6022
    n623 = m.nota_cont("623")
    assert n623 and "art. 25 alin. (3) lit. a" in n623 and "2%" in n623 and "salariați" in n623
    assert m.nota_cont("604") is None and m.nota_cont("628") is None and m.nota_cont("") is None and m.nota_cont(None) is None


def test_notele_unui_bon_sunt_unice_si_in_ordinea_conturilor():
    m = _m()
    arts = [{"cont_propus": "6022"}, {"cont_propus": "6022"}, {"cont_propus": "623"}, {"cont_propus": "604"}, {"cont_propus": None}]
    note = m.note_conturi(arts)
    assert note == [m.nota_cont("6022"), m.nota_cont("623")]
    assert m.note_conturi([]) == [] and m.note_conturi(None) == []


# ── migrarea și șablonul ────────────────────────────────────────────────────────────────────

def test_migrarea_e_a_registrului_si_sablonul_are_blocul_ei():
    from core import migrare_bon_cui_cumparator as mig
    sablon = open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    assert mig.bloc_template() in sablon, "tenant_template.sql n-are blocul `migrare_bon_cui_cumparator.bloc_template()`"
    cale = "core/migrare_bon_cui_cumparator.py"
    assert migrari_registru.e_migrare(cale, open(os.path.join(RAD, cale), encoding="utf-8").read())
    assert "ALTER TABLE TENANT_PLACEHOLDER.bonuri ADD COLUMN IF NOT EXISTS cui_cumparator text;" in mig.bloc_template()
    # DDL curat: nicio scriere în datele existente (coloana rămâne NULL pe bonurile vechi), nicio notă contabilă
    import ast
    arbore = ast.parse(open(os.path.join(RAD, cale), encoding="utf-8").read())
    docstringuri = {id(n.body[0].value) for n in ast.walk(arbore) if isinstance(n, (ast.Module, ast.FunctionDef)) and n.body
                    and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant)}
    siruri = [n.value for n in ast.walk(arbore) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstringuri]
    for s in siruri:
        for interzis in ("UPDATE ", "INSERT ", "DELETE ", "inregistrari"):
            assert interzis not in s, "migrarea scrie în date sau în note: %r în %r" % (interzis, s[:80])


def _cere_test():
    _db.init_pool()
    with _db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT current_database()")
        if cur.fetchone() != ("iconta_test",):
            raise RuntimeError("Fixture P: baza nu este iconta_test")


@pytest.fixture
def conn():
    _cere_test()
    from core import tenant_provisioning as _tp
    sablon = open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute(_tp.parametrizeaza_template(sablon, SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


def _coloana(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT data_type, is_nullable, column_default FROM information_schema.columns WHERE table_schema = %s "
                    "AND table_name = 'bonuri' AND column_name = 'cui_cumparator'", (SCHEMA,))
        return cur.fetchone()


def test_firma_noua_are_coloana_nula_fara_implicit_si_migrarea_o_adauga_si_e_idempotenta(conn):
    from core import migrare_bon_cui_cumparator as mig
    assert _coloana(conn) == ("text", "YES", None), "firma nouă (din șablon) trebuie să aibă coloana text, nulabilă, fără valoare implicită"
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE bonuri DROP COLUMN cui_cumparator")        # schema de dinainte de migrare
        cur.execute("INSERT INTO bonuri (comerciant, total, status) VALUES ('Vechi SRL', 10, 'de_verificat')")
    assert _coloana(conn) is None
    mig.aplica(conn, SCHEMA)
    assert mig.verifica(conn, SCHEMA)
    assert _coloana(conn) == ("text", "YES", None)
    with conn.cursor() as cur:
        cur.execute("SELECT cui_cumparator FROM bonuri WHERE comerciant = 'Vechi SRL'")
        assert cur.fetchone() == (None,), "bonul vechi trebuie să rămână cu NULL (necitit), nu «fără cod»"
    mig.aplica(conn, SCHEMA)                                                # idempotentă
    assert mig.verifica(conn, SCHEMA)


def test_raspunsul_ai_da_cele_trei_stari_ale_codului_cumparatorului():
    """Cheia absentă din răspunsul AI = NULL (necitit); cheia prezentă cu null, gol sau fără cifre = șirul gol (citit și absent de pe bon);
    valoarea citită se păstrează în forma cui_forma.stocare (fără spații, fără «RO» în fața cifrelor). Cazurile AI: valori-substitut, codul
    comerciantului pus la cumpărător, poza tăiată (bon_complet false)."""
    from core import uc_portal
    f = uc_portal._cui_cumparator_din_raspuns
    assert f({"tip": "bon"}) is None
    assert f({"cui_cumparator": None}) == ""
    assert f({"cui_cumparator": ""}) == ""
    assert f({"cui_cumparator": "  "}) == ""
    assert f({"cui_cumparator": "RO 401 002 001"}) == "401002001"
    assert f({"cui_cumparator": "401002001"}) == "401002001"
    assert f({"cui_cumparator": 401002001}) == "401002001"                       # număr JSON
    for v in ("-", "—", "N/A", "n/a", "nu", "null", "None", "RO", "lipsa"):      # valori-substitut fără nicio cifră = citit și absent
        assert f({"cui_cumparator": v}) == "", v
    # codul comerciantului pus la cumpărător (promptul interzice, dar nu e verificat): citit și absent
    assert f({"cui": "RO14399840", "cui_cumparator": "14399840"}) == ""
    assert f({"cui": "14 399 840", "cui_cumparator": "RO 14399840"}) == ""
    assert f({"cui": "14399840", "cui_cumparator": "401002001"}) == "401002001"
    # poză tăiată: fără cod citit = necitit (TVA nu se pierde pe o premisă falsă); un cod citit rămâne cod
    assert f({"bon_complet": False}) is None
    assert f({"bon_complet": False, "cui_cumparator": None}) is None
    assert f({"bon_complet": False, "cui_cumparator": ""}) is None
    assert f({"bon_complet": False, "cui_cumparator": "-"}) is None
    assert f({"bon_complet": False, "cui": "14399840", "cui_cumparator": "14399840"}) is None
    assert f({"bon_complet": False, "cui_cumparator": "RO 401 002 001"}) == "401002001"
    assert f({"bon_complet": True, "cui_cumparator": None}) == ""
    assert f({"bon_complet": True}) is None


def test_adauga_bon_pune_fiecare_valoare_pe_coloana_ei(conn):
    """Apelul din core/uc_portal.py (portal_bon) trece pozițional 14 argumente după (cur, schema); parametrii din semnătura lui adauga_bon au nume
    deplasate față de coloane (`status` poartă valoarea coloanei `tip`, `tip` pe `numar_document`, `numar_document` pe `mentiuni`, `mentiuni` pe `orientare`).
    Proba cheamă adauga_bon cu același apel, plus parametrul nou la sfârșit, și citește coloanele: o greșeală la parametrul nou (pus înaintea orientării,
    uitat în apel, scris în altă coloană) lasă coloana NULL sau mută o coloană veche."""
    from core import repo_casa
    for valoare in (None, "", "401002001"):
        with conn.cursor() as cur:
            bid = repo_casa.adauga_bon(cur, SCHEMA, "Magazin P SRL", "14399840", "2026-11-02", 60.5, 0, 10.5, "[]", "[]", 1, True,
                                       "bon", "NR-77", "mentiune P", 90, valoare)[0]
            cur.execute("SELECT cui_cumparator, tip, numar_document, mentiuni, orientare, status, comerciant, cui, total, tva_21 FROM bonuri WHERE id = %s", (bid,))
            rand = cur.fetchone()
            assert rand[0] == valoare, (valoare, rand)
            assert rand[1:6] == ("bon", "NR-77", "mentiune P", 90, "extras"), rand
            assert rand[6:8] == ("Magazin P SRL", "14399840") and float(rand[8]) == 60.5 and float(rand[9]) == 10.5, rand
            # citirile: lista de verificat are coloana la sfârșit, iar cui_cumparator_bon întoarce rândul (valoare,) sau None
            repo_casa.trece_bonul_la_de_verificat(cur, SCHEMA, bid)
            din_lista = [r for r in repo_casa.bonuri_de_verificat(cur, SCHEMA) if r[0] == bid][0]
            assert din_lista[-1] == valoare, (valoare, din_lista)
            citit = repo_casa.cui_cumparator_bon(cur, SCHEMA, bid)
            assert (citit[0] if citit else None) == valoare if valoare is not None else (citit is None or citit[0] is None), (valoare, citit)
    with conn.cursor() as cur:
        assert repo_casa.cui_cumparator_bon(cur, SCHEMA, 987654321) is None


from core.test_portal_bon import env as env_portal  # fixture pytest a rutei existente


@pytest.fixture
def env(request, monkeypatch):
    from core import test_portal_bon
    _cere_test()
    schema = "ztest_p_portal_" + uuid.uuid4().hex
    with _db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regnamespace(%s)", (schema,))
        if cur.fetchone() != (None,):
            raise RuntimeError("Fixture P: schema efemeră există deja")
    monkeypatch.setattr(test_portal_bon, "SCH", schema)
    return request.getfixturevalue("env_portal")


def test_portal_bon_scrie_cui_cumparator_pe_coloana_lui_si_nu_muta_celelalte_coloane(env, monkeypatch):
    """Prin ruta portal_bon (apelul real repo_casa.adauga_bon din uc_portal.py), cu răspunsuri AI simulate: fără cheie = NULL; cheie null = șirul gol;
    cod cu spații și RO = forma stocare; codul comerciantului = șirul gol; poză tăiată fără cod = NULL; tip, numar_document, mentiuni, orientare rămân pe coloanele lor."""
    import json
    from core import ai_client
    from core.test_portal_bon import _client, _H, PNG, SCH as SCH_PB
    cl = _client()

    def _incarca(raspuns):
        monkeypatch.setattr(ai_client, "citeste_imagini", lambda imagini, prompt: json.dumps(raspuns))
        r = cl.post("/portal/bon", files={"fisiere": ("bon.png", PNG, "image/png")}, headers=_H(env))
        assert r.status_code == 200, r.text[:300]
        with env["conn"].cursor() as cur:
            cur.execute('SELECT cui_cumparator, tip, numar_document, mentiuni, orientare, status FROM "%s".bonuri WHERE id = %%s' % SCH_PB, (r.json()["bon_id"],))
            return cur.fetchone()

    baza = {"tip": "bon", "comerciant": "ZT MAGAZIN", "cui": "14399840", "data": "2026-11-02", "total": 121.0, "numar_document": "NR-7",
            "mentiuni": "mentiune", "articole": [], "tva": [{"cota": 21, "valoare": 21.0}], "bon_complet": True, "orientare": 90}
    assert _incarca(dict(baza)) == (None, "bon", "NR-7", "mentiune", 90, "extras")
    assert _incarca(dict(baza, cui_cumparator=None)) == ("", "bon", "NR-7", "mentiune", 90, "extras")
    assert _incarca(dict(baza, cui_cumparator="RO 401 002 001")) == ("401002001", "bon", "NR-7", "mentiune", 90, "extras")
    assert _incarca(dict(baza, cui_cumparator="RO14399840"))[0] == ""          # codul comerciantului
    assert _incarca(dict(baza, cui_cumparator="N/A"))[0] == ""
    assert _incarca(dict(baza, cui_cumparator=None, bon_complet=False))[0] is None


# ── aprobarea bonului (use-case) pe o schemă efemeră din șablon ─────────────────────────────

@pytest.fixture
def uc(conn, monkeypatch):
    """Schema provine din fixture-ul conn. Totul revine prin rollback la ieșire."""
    import contextlib
    from core import auth_api, uc_comun, uc_curs_bnr, uc_tenants
    with conn.cursor() as cur:
        cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                    "VALUES (1, 'ZT Bon SRL', '401002001', true, 'SRL', 200, 'cantitativ_valoric')")

    class FaraCommit:
        def commit(self):
            pass

        def __getattr__(self, nume):
            return getattr(conn, nume)

    proxy = FaraCommit()
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCHEMA)
    monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
    monkeypatch.setattr(uc_curs_bnr, "asigura_cursul", lambda *a, **k: None)
    yield uc_tenants, conn


def _bon(conn, cui_cumparator, total=60.5, tva=10.5, cont="6022"):
    import json
    with conn.cursor() as cur:
        cur.execute("INSERT INTO bonuri (comerciant, cui, data, total, tva_21, status, articole, tva, tip, cui_cumparator) "
                    "VALUES ('Magazin Test SRL', '14399840', '2026-11-02', %s, %s, 'de_verificat', %s, %s, 'bon', %s) RETURNING id",
                    (total, tva, json.dumps([{"denumire": "Articol", "valoare": total, "cota_tva": 21, "cont_propus": cont}]),
                     json.dumps([{"cota": 21, "valoare": tva}]), cui_cumparator))
        return cur.fetchone()[0]


def _aproba(uc, conn, monkeypatch, cui_cumparator, curs, total=60.5, tva=10.5, cont="6022"):
    import types
    from core import bon_tva_deductibil
    monkeypatch.setattr(bon_tva_deductibil, "curs_euro", lambda *a, **k: curs)
    bid = _bon(conn, cui_cumparator, total, tva, cont)
    b = types.SimpleNamespace(data="2026-11-02", comerciant="Magazin Test SRL", total=total, tva=tva,
                              linii=[types.SimpleNamespace(cont=cont, valoare=total)])
    r = uc.bon_aproba(1, bid, b, {"uid": 1})
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY cont_debit", (r["nota_id"],))
        linii = [(d, c, float(s)) for d, c, s in cur.fetchall()]
    return r, linii


def test_bonul_fara_codul_firmei_nu_isi_dedude_tva_si_valoarea_intreaga_intra_in_cheltuiala(uc, monkeypatch):
    mod, conn = uc
    r, linii = _aproba(mod, conn, monkeypatch, "", Decimal("5"))
    assert linii == [("6022", "5311", 60.5)], linii
    assert r["tva_dedus"] == 0 and r["avertisment"].startswith("TVA nedeductibil: pe bon nu este înscris codul fiscal al firmei cumpărătoare")


def test_bonul_cu_alt_cod_nu_isi_dedude_tva(uc, monkeypatch):
    mod, conn = uc
    r, linii = _aproba(mod, conn, monkeypatch, "RO14399840", Decimal("5"))
    assert [l for l in linii if "4426" in l[:2]] == [] and linii == [("6022", "5311", 60.5)], linii
    assert r["avertisment"].startswith("TVA nedeductibil: codul fiscal de pe bon (14399840) nu este al firmei (401002001)")


def test_bonul_cu_codul_firmei_sub_100_euro_isi_dedude_tva_ca_pana_acum_fara_observatie(uc, monkeypatch):
    mod, conn = uc
    r, linii = _aproba(mod, conn, monkeypatch, "401002001", Decimal("5"))
    assert linii == [("4426", "5311", 10.5), ("6022", "5311", 50.0)], linii
    assert r["tva_dedus"] == 10.5 and r["avertisment"] is None


def test_bonul_cu_codul_firmei_peste_100_euro_si_cel_vechi_isi_pastreaza_tva_cu_observatie(uc, monkeypatch):
    mod, conn = uc
    r, linii = _aproba(mod, conn, monkeypatch, "401002001", Decimal("5"), total=600, tva=104.13)
    assert ("4426", "5311", 104.13) in linii and r["tva_dedus"] == 104.13 and isinstance(r["tva_dedus"], float) and "art. 319 alin. (13)" in r["avertisment"], (linii, r)
    r2, linii2 = _aproba(mod, conn, monkeypatch, None, Decimal("5"))
    assert ("4426", "5311", 10.5) in linii2 and r2["avertisment"].startswith("Codul cumpărătorului nu a fost citit de pe acest bon"), (linii2, r2)
    r3, linii3 = _aproba(mod, conn, monkeypatch, "401002001", None)
    assert ("4426", "5311", 10.5) in linii3 and "nu s-a putut verifica" in r3["avertisment"], (linii3, r3)


def test_bonul_fara_tva_nu_cere_verdict_si_nu_citeste_nimic_in_plus(uc, monkeypatch):
    """Garda din test_flux_factura_f1_c.py: apel cu SimpleNamespace(tva=0) și fără atribute noi pe `b`."""
    mod, conn = uc
    r, linii = _aproba(mod, conn, monkeypatch, "", Decimal("5"), total=12.1, tva=0, cont="604")
    assert linii == [("604", "5311", 12.1)] and r["tva_dedus"] == 0 and r["avertisment"] is None, (linii, r)


def test_lista_de_verificat_poarta_codul_verdictul_si_notele(uc, monkeypatch):
    mod, conn = uc
    from core import bon_tva_deductibil
    monkeypatch.setattr(bon_tva_deductibil, "curs_euro", lambda *a, **k: Decimal("5"))
    _bon(conn, "", 60.5, 10.5, "6022")
    r = mod.bonuri_de_verificat(1, {"uid": 1})
    b = r["bonuri"][0]
    assert b["cui_cumparator"] == "" and b["tva_deductibil"] == "nu"
    assert b["avertismente"][0].startswith("TVA nedeductibil: pe bon nu este înscris codul fiscal")
    assert any("art. 298 alin. (1)" in a for a in b["avertismente"])


def test_bonul_fara_tva_in_lista_nu_primeste_verdict_ci_numai_notele_de_cont(uc, monkeypatch):
    """Limita (4): fără TVA nu e nimic de dedus, deci nici «TVA nedeductibil» (text fals) și nici caseta-atenție dată de un verdict inexistent."""
    mod, conn = uc
    from core import bon_tva_deductibil
    monkeypatch.setattr(bon_tva_deductibil, "curs_euro", lambda *a, **k: Decimal("5"))
    b1 = _bon(conn, "", 12.1, 0, "604")
    b2 = _bon(conn, "", 12.1, 0, "6022")
    lista = {b["id"]: b for b in mod.bonuri_de_verificat(1, {"uid": 1})["bonuri"]}
    assert lista[b1]["cui_cumparator"] == "" and lista[b1]["tva_deductibil"] is None and lista[b1]["avertismente"] == [], lista[b1]
    assert lista[b2]["tva_deductibil"] is None and lista[b2]["avertismente"] == [bon_tva_deductibil.nota_cont("6022")], lista[b2]


def test_curs_euro_real_converteste_data_si_ia_cursul_din_tuplul_lui_curs_pentru(monkeypatch):
    """curs_euro nu e înlocuit aici: data poate fi șir ISO (BonAproba.data, bonuri.data), date sau None; curs_pentru întoarce (curs, data_curs, sursa);
    refuzurile BNR dau None. Se înlocuiește curs_pentru ca atribut al modulului core.curs_bnr."""
    from datetime import date
    from core import curs_bnr
    m = _m()
    chemari = []

    def _fals(conn, moneda, data, *a, **k):
        chemari.append((moneda, data))
        return Decimal("4.9"), data, "bnr"

    monkeypatch.setattr(curs_bnr, "curs_pentru", _fals)
    assert m.curs_euro(None, "2026-11-02") == Decimal("4.9") and chemari[-1] == ("EUR", date(2026, 11, 2)), chemari
    assert m.curs_euro(None, date(2026, 11, 2)) == Decimal("4.9")
    n = len(chemari)
    assert m.curs_euro(None, None) is None and m.curs_euro(None, "nu e dată") is None and m.curs_euro(None, "") is None
    assert len(chemari) == n, "cu data lipsă sau nepărsabilă nu se cere niciun curs"
    for exc in (curs_bnr.CursIndisponibil("x"), curs_bnr.MonedaNecotata("EUR"),
                curs_bnr.CursPreaVechi("EUR", date(2026, 9, 1), Decimal("5"), 60, 30)):
        def _refuz(*a, _e=exc, **k):
            raise _e
        monkeypatch.setattr(curs_bnr, "curs_pentru", _refuz)
        assert m.curs_euro(None, "2026-11-02") is None, type(exc).__name__
