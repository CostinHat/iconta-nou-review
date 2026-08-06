# -*- coding: utf-8 -*-
"""NECONFORMITATE ACTIVA reparata (04.08): operatiunile de achizitie (achizitie_ic, achizitie_taxare_inversa)
emit un rand `facturi` (directie=primita) + contabilizeaza cu factura_id legat, ca sa ajunga in D390/D394.
Probe end-to-end pe schema scratch din template (gated DB): handler real -> facturi + factura_id -> declaratie
-> operatiunea E ACOLO -> DUK valid. + GARD anti-regresie de CLASA: nicio inregistrare de achizitie fara factura_id."""
import pytest


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
_SCH = "efemer_achizitii_factura"


def _scratch(cur):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
    sql = open("tenant_template.sql", encoding="utf-8").read().replace("TENANT_PLACEHOLDER", _SCH)
    cur.execute(sql)   # template isi creeaza schema + tabelele, calificate cu _SCH
    cur.execute("SET search_path TO %s" % _SCH)
    cur.execute("""INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, email, telefon, caen,
                   declarant_nume, declarant_prenume, declarant_functie, platitor_tva, operatiuni_ic, tip_decont)
                   VALUES (1,'TEST SRL','RO14399840','Str 1','Buc','B','e@x.ro','0722','4690',
                           'P','I','ADMIN', true, true, 'L')""")


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_achizitie_ic_emite_factura_ajunge_in_d390_duk_valid(monkeypatch):
    import main
    from core import db, d390, duk
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _scratch(cur)
            conn.commit()
        monkeypatch.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: _SCH)
        # handler REAL
        r = main.achizitie_ic(1, {"data": "2026-06-20", "valoare": 1000, "cont_destinatie": "371",
                                   "tip": "bunuri", "cota": 21, "cod_tva_furnizor": "DE811569869",
                                   "numar": "F-DE-77", "furnizor_nume": "LIEFERANT GMBH"},
                              {"uid": 1})
        assert r.get("factura_id"), r
        # rand facturi (primita, furnizor UE) + inregistrare LEGATA (factura_id)
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SET search_path TO %s" % _SCH)
            cur.execute("SELECT directie, tert_cui, total, tva FROM facturi WHERE id=%s", (r["factura_id"],))
            f = cur.fetchone()
            assert f == ("primita", "DE811569869", 1000, 0), f
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (r["inregistrare_id"],))
            assert cur.fetchone()[0] == r["factura_id"], "inregistrare ORFANA (fara factura_id)"
        # D390: operatiunea E ACOLO + DUK valid
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO %s" % _SCH)
            prof, facturi = d390.pull(conn, _SCH, 2026, 6)
        assert any((x.get("cui") or "").startswith("DE") for x in facturi), \
            "achizitia IC NU e in facturi citite de D390: %r" % facturi
        res = d390.calcul_d390(prof, 2026, 6, facturi)
        assert res.total_baza >= 1000, res.total_baza
        if duk.poate_valida("d390"):
            xml = d390.build_xml(res)
            verdict = duk.valideaza(xml, "d390", an=2026, luna=6)
            assert verdict["stare"] == "valid", "DUK a respins D390: %s" % verdict.get("erori")
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            conn.commit()


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_achizitie_taxare_inversa_emite_factura_ajunge_in_d394_duk_valid(monkeypatch):
    import main
    from core import db, d394, duk
    from core.common import Perioada
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _scratch(cur)
            conn.commit()
        monkeypatch.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: _SCH)
        r = main.achizitie_taxare_inversa(1, {"data": "2026-06-15", "categorie": "deseuri", "valoare": 5000,
                                              "cont_destinatie": "371", "cota": 21, "furnizor_platitor_tva": True,
                                              "furnizor_cui": "RO14399840", "furnizor_nume": "FURNIZOR RO",
                                              "numar": "F-RO-1"}, {"uid": 1})
        assert r.get("factura_id"), r
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SET search_path TO %s" % _SCH)
            cur.execute("SELECT directie, tert_cui, taxare_inversa, categorie_331 FROM facturi WHERE id=%s",
                        (r["factura_id"],))
            assert cur.fetchone() == ("primita", "RO14399840", True, "deseuri")
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (r["inregistrare_id"],))
            assert cur.fetchone()[0] == r["factura_id"], "inregistrare ORFANA (fara factura_id)"
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO %s" % _SCH)
            xml, res = d394.genereaza(conn, _SCH, Perioada(2026, luna=6))
        assert 'codPR="22"' in xml, "taxare inversa (deseuri->codPR 22) NU e in D394: op11 lipsa"
        if duk.poate_valida("d394"):
            verdict = duk.valideaza(xml, "d394", an=2026, luna=6)
            assert verdict["stare"] == "valid", "DUK a respins D394: %s" % verdict.get("erori")
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            conn.commit()


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_achizitie_neinregistrat_N_ajunge_in_d394_duk_valid(monkeypatch):
    import main
    from core import db, d394, duk
    from core.common import Perioada
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _scratch(cur)
            conn.commit()
        monkeypatch.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: _SCH)
        r = main.achizitie_neinregistrat(1, {"data": "2026-06-18", "furnizor_nume": "ION POPESCU",
                                             "valoare": 2000, "cont_cheltuiala": "301", "categorie": "deseuri",
                                             "numar": "BON-1"}, {"uid": 1})
        assert r.get("factura_id") and r.get("in_d394") is True, r
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SET search_path TO %s" % _SCH)
            cur.execute("SELECT directie, COALESCE(tert_cui,''), tert_nume, categorie_331 FROM facturi WHERE id=%s",
                        (r["factura_id"],))
            assert cur.fetchone() == ("primita", "", "ION POPESCU", "deseuri")
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (r["inregistrare_id"],))
            assert cur.fetchone()[0] == r["factura_id"], "inregistrare ORFANA"
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO %s" % _SCH)
            xml, res = d394.genereaza(conn, _SCH, Perioada(2026, luna=6))
        assert 'tip="N"' in xml, "operatiunea N NU e in D394 (desi are categorie): %s" % xml[:400]
        if duk.poate_valida("d394"):
            verdict = duk.valideaza(xml, "d394", an=2026, luna=6)
            assert verdict["stare"] == "valid", "DUK a respins D394 cu N: %s" % verdict.get("erori")
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            conn.commit()


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_achizitie_necorporala_emite_factura_in_d394_si_mijloc_fix(monkeypatch):
    import main
    from core import db, d394, duk
    from core.common import Perioada
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _scratch(cur)
            conn.commit()
        monkeypatch.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: _SCH)
        r = main.achizitie_necorporala(1, {"data": "2026-06-10", "denumire": "Licenta X", "valoare": 5000,
                                           "tip": "software", "cota": 21, "furnizor_cui": "RO14399840",
                                           "furnizor_nume": "SOFT SRL", "numar": "F-SOFT-1"}, {"uid": 1})
        assert r.get("factura_id") and r.get("mijloc_fix_id"), r  # factura SI mijloc fix (efect MF/amortizare)
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SET search_path TO %s" % _SCH)
            cur.execute("SELECT directie, tert_cui FROM facturi WHERE id=%s", (r["factura_id"],))
            assert cur.fetchone() == ("primita", "RO14399840")
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (r["inregistrare_id"],))
            assert cur.fetchone()[0] == r["factura_id"], "inregistrare ORFANA"
            cur.execute("SELECT count(*) FROM mijloace_fixe WHERE id=%s", (r["mijloc_fix_id"],))
            assert cur.fetchone()[0] == 1, "mijlocul fix (amortizare) nu s-a creat"
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO %s" % _SCH)
            xml, res = d394.genereaza(conn, _SCH, Perioada(2026, luna=6))
        if duk.poate_valida("d394"):
            verdict = duk.valideaza(xml, "d394", an=2026, luna=6)
            assert verdict["stare"] == "valid", "DUK a respins D394 necorporala: %s" % verdict.get("erori")
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            conn.commit()


def test_nicio_achizitie_creeaza_inregistrare_orfana_de_factura():
    """CLASA (nu instanta): orice handler achizitie_* din main.py care INSEREAZA in `inregistrari` (jurnal
    invoice-backed, sursa='facturi') TREBUIE sa lege factura_id - altfel operatiunea e invizibila pentru
    D390/D394 (NECONFORMITATE 04.08). Scan AST pe sursa. EXCEPTIE NUMITA (motiv scris in GARZI + DECIZII 04.08):
    achizitie_agricultor - regim special art.315^1, tratamentul D394 al achizitiei de la agricultor forfetar
    NEconfirmabil la sursa. Orice ALT handler achizitie_* orfan pica; o exceptie noua cere motiv in registru."""
    import ast, re
    EXCEPTATE = {"achizitie_agricultor"}
    src = open("main.py", encoding="utf-8").read()
    tree = ast.parse(src)
    rele = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("achizitie_"):
            seg = ast.get_source_segment(src, node) or ""
            for mm in re.finditer(r"INSERT INTO\s+\S*inregistrari\s*\(([^)]*)\)", seg):
                if "factura_id" not in mm.group(1) and node.name not in EXCEPTATE:
                    rele.append("%s: INSERT inregistrari fara factura_id (orfan, invizibil D390/D394)" % node.name)
    assert not rele, "achizitie orfana de factura (invizibila declaratiei):\n" + "\n".join(rele)
    # anti-vacuu: exceptarea e reala (agricultor chiar e orfan azi) - altfel exceptia e moarta/inutila
    assert "def achizitie_agricultor" in src


# ============ B: clasifica_partener pe flag real (INGHETAT), nu pe forma CUI ============

@pytest.fixture(autouse=True)
def _stub_anaf(monkeypatch):
    """Handlerele ingheata tert_platitor_tva best-effort din ANAF F004; in teste stub-uim valideaza_cui sa
    RIDICE -> freeze cade pe fallback (declaratia/semantica), FARA HTTP live la ANAF (determinist, nu depinde de retea)."""
    import main
    monkeypatch.setattr(main.anaf_api if hasattr(main, "anaf_api") else __import__("core.anaf_api", fromlist=["x"]),
                        "valideaza_cui", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("ANAF stub")))


def test_clasifica_partener_consulta_flag_nu_forma():
    from core.d394 import clasifica_partener, P_TVA_RO, P_NEINREG, P_UE
    CUI = "RO14399840"   # RO CUI VALID (forma OK)
    # PJ NEplatitor cu CUI valid -> tip 2 (N pe achizitie). AZI (fara flag/None) ar fi fost tip 1.
    assert clasifica_partener(CUI, False)[0] == P_NEINREG
    # platitor cu CUI valid -> tip 1
    assert clasifica_partener(CUI, True)[0] == P_TVA_RO
    # legacy (None) -> euristica de forma: CUI valid presupus platitor -> tip 1 (comportament de dinainte)
    assert clasifica_partener(CUI, None)[0] == P_TVA_RO
    # UE: flag N/A, clasificat pe prefix indiferent de flag
    assert clasifica_partener("DE811569869", False)[0] == P_UE


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_flag_inghetat_da_raspunsuri_diferite_pe_facturi_ale_aceluiasi_cui(monkeypatch):
    """ISTORIC: furnizor RO inregistrat 2020-2023 apoi radiat. Factura 2022 (flag inghetat True) -> tip 1;
    factura 2025 (flag inghetat False) -> tip 2 -> N. ACELASI CUI, doua facturi, doua clasificari - din flag,
    nu din forma. Freeze-la-creare = fapt imutabil pe factura."""
    import main
    from core import db, d394, facturi_api
    from core.common import Perioada
    CUI = "RO14399840"
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _scratch(cur)
            conn.commit()
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO %s" % _SCH)
            L = [{"descriere": "marfa", "cantitate": 1, "pret_unitar": "1000", "cota_tva": 0}]
            facturi_api.creeaza_factura(conn, numar="F2022", data_emitere="2022-06-10", directie="primita",
                                        linii=L, tert_nume="FURNIZOR SRL", tert_cui=CUI,
                                        categorie_331="deseuri", tert_platitor_tva=True, status="importata")
            facturi_api.creeaza_factura(conn, numar="F2025", data_emitere="2025-06-10", directie="primita",
                                        linii=L, tert_nume="FURNIZOR SRL", tert_cui=CUI,
                                        categorie_331="deseuri", tert_platitor_tva=False, status="importata")
            conn.commit()
        # 2022: acelasi CUI, flag True -> tip 1 (P_TVA_RO); 2025: flag False -> tip 2 (P_NEINREG)
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO %s" % _SCH)
            _p22, f22 = d394.pull(conn, _SCH, Perioada(2022, luna=6))
            _p25, f25 = d394.pull(conn, _SCH, Perioada(2025, luna=6))
        l22, l25 = f22["facturi"], f25["facturi"]
        assert l22 and d394.clasifica_partener(l22[0]["cui"], l22[0]["platitor_tva"])[0] == d394.P_TVA_RO, l22
        assert l25 and d394.clasifica_partener(l25[0]["cui"], l25[0]["platitor_tva"])[0] == d394.P_NEINREG, l25
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            conn.commit()


@pytest.mark.skipif(not _DB, reason="DB indisponibil")
def test_handlerele_ingheata_flagul_la_creare(monkeypatch):
    """Handlerele ingheata tert_platitor_tva pe factura la creare (ANAF stub -> fallback): N->False (PF),
    taxare inversa->True (furnizor platitor declarat)."""
    import main
    from core import db
    db.init_pool()
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                _scratch(cur)
            conn.commit()
        monkeypatch.setattr(main.auth_api, "schema_tenant", lambda conn, uid, tid: _SCH)
        rn = main.achizitie_neinregistrat(1, {"data": "2026-06-18", "furnizor_nume": "ION", "valoare": 2000,
                                             "cont_cheltuiala": "301", "categorie": "deseuri"}, {"uid": 1})
        rt = main.achizitie_taxare_inversa(1, {"data": "2026-06-15", "categorie": "deseuri", "valoare": 5000,
                                              "cont_destinatie": "371", "cota": 21, "furnizor_platitor_tva": True,
                                              "furnizor_cui": "RO14399840", "furnizor_nume": "FRZ", "numar": "F1"},
                                           {"uid": 1})
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("SET search_path TO %s" % _SCH)
            cur.execute("SELECT tert_platitor_tva FROM facturi WHERE id=%s", (rn["factura_id"],))
            assert cur.fetchone()[0] is False, "N nu a inghetat False"
            cur.execute("SELECT tert_platitor_tva FROM facturi WHERE id=%s", (rt["factura_id"],))
            assert cur.fetchone()[0] is True, "taxare inversa nu a inghetat True (fallback din declaratie)"
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            conn.commit()
