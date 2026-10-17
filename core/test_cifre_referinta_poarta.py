# -*- coding: utf-8 -*-
"""GARD — cifrele de referință ale firmelor F1–F5 opresc publicarea la orice diferență (comanda Costin 10.10.2026 pct.1, verbatim în
DECIZII: „Leagă gardul «orice diferență față de referință oprește publicarea». O schimbare voită se face doar cu aprobarea mea,
consemnată în DECIZII.”). Calculul pe producție îl face poarta (`scripts/githooks/poarta-suita`); aici se păzesc legătura, comparația și
regula schimbării. Fără acces la producție."""
import io
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import cifre_referinta as cr  # noqa: E402


def _citeste(rel):
    return io.open(os.path.join(RAD, rel), encoding="utf-8").read()


def test_poarta_ruleaza_verificarea_si_respinge_la_orice_iesire_nenula():
    """MUTAȚIE: treapta scoasă din poartă -> pică."""
    t = _citeste("scripts/githooks/poarta-suita")
    m = re.search(r'^"\$PY" scripts/cifre_referinta\.py --productie --verifica > \$J/precommit_cifre\.log 2>&1\nRC=\$\?', t, re.M)
    assert m, "poarta nu mai confruntă cifrele cu referința aprobată"
    dupa = t[m.end():m.end() + 900]
    linii_dupa = [x.strip() for x in dupa.splitlines()]   # liniile scriptului, nu un sub-șir oarecare din el
    assert 'if [ "$RC" -ne 0 ]; then' in linii_dupa and "exit 1" in linii_dupa[linii_dupa.index('if [ "$RC" -ne 0 ]; then'):], (
        "o diferență (sau o măsurătoare eșuată) nu oprește poarta")
    assert m.start() < t.find('scripts/e2e_poarta.py'), "cifrele se confruntă înaintea plasei"


def test_referinta_e_cea_aprobata_si_nu_e_goala():
    """Anti-vacuu: cinci firme, patru cu balanța pe cel puțin o lună (F4 n-are date încă); amprenta fișierului e cea consemnată în
    DECIZII."""
    ref = json.load(open(cr.REFERINTA, encoding="utf-8"))
    assert len(ref) == 5 and sum(1 for f in ref.values() if f.get("balanta")) >= 4, sorted(ref)
    assert cr.amprenta_fisier() in _citeste("DECIZII.md"), "referința nu are aprobarea consemnată în DECIZII (cu amprenta ei)"


def test_comparatia_vede_orice_schimbare_si_nimic_in_plus():
    """MUTAȚIE: `diferente` care întoarce mereu [] -> pică."""
    ref = json.load(open(cr.REFERINTA, encoding="utf-8"))
    assert cr.diferente(ref, json.loads(json.dumps(ref))) == []
    alt = json.loads(json.dumps(ref))
    f = sorted(alt)[0]
    luna = sorted(alt[f]["balanta"])[0]
    rand = alt[f]["balanta"][luna][0]
    rand["sf_d"] = float(rand.get("sf_d") or 0) + 0.01                    # un ban pe un sold
    alt[f]["D112"] = {}                                                   # o declarație care dispare
    d = [c for c, _a, _b in cr.diferente(ref, alt)]
    assert any("/balanta/" in c for c in d) and any("/D112/" in c or c.endswith("/D112") for c in d), d


def test_amprenta_ignora_numai_data_generarii():
    """Amprenta XML-ului nu depinde de ziua generării (`AuditFileDateCreated`, `DateCreated`), dar depinde de orice cifră.
    MUTAȚIE: `AuditFileDateCreated` scos din `_VOLATIL` -> pică."""
    x = "<H><AuditFileDateCreated>%s</AuditFileDateCreated></H><T><TotalDebit>%s</TotalDebit></T>"
    assert cr._amprenta(x % ("2026-10-09", "100.00")) == cr._amprenta(x % ("2026-10-10", "100.00"))
    assert cr._amprenta(x % ("2026-10-09", "100.00")) != cr._amprenta(x % ("2026-10-09", "100.01"))


def test_schimbarea_referintei_cere_amprenta_in_decizii():
    """MUTAȚIE: regula scoasă din `verifica-mesaj` -> pică."""
    linii = {x.strip() for x in _citeste("scripts/githooks/verifica-mesaj").splitlines()}   # liniile scriptului, ca mulțime
    assert 'REF_CIFRE="scripts/cifre_referinta_aprobate.json"' in linii
    regula = r'git diff --cached -U0 -- DECIZII.md | grep -E ' + r"'^\+'" + r' | grep -q "$AMPR"'
    assert any(regula in x and x.startswith("if ") for x in linii), "regula aprobării lipsește (condiția unui `if` din script)"


def test_lunile_cu_date_vin_numai_din_notele_validate():
    """[14.10.2026, decizia Costin, varianta (c), verbatim în DECIZII] „Unealta de cifre alege lunile numai din notele validate (R36).”
    Pe o schemă din `tenant_template.sql` (baza de TEST, anulată): o notă validată în 01/2099 și o ciornă în 12/2099 -> numai 01/2099
    (cazul din 13.10: ciornele de închidere la 31.12.2026 pe F2 adăugau o lună goală). MUTAȚIE: filtrul `status = 'validata'` scos din
    `_luni_cu_date` -> pică."""
    from core import db as _db
    from core import tenant_provisioning as _tp
    schema = "ztest_cifre_r36"
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
                cur.execute(_tp.parametrizeaza_template(_citeste("tenant_template.sql"), schema))
                for data, stare in (("2099-01-15", "validata"), ("2099-12-31", "ciorna")):
                    cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status) VALUES (%%s, 'proba R36', 'manual', %%s)"
                                % schema, (data, stare))
                assert cr._luni_cu_date(cur, schema) == [(2099, 1)]
        finally:
            conn.rollback()


#: DSN-uri SINTETICE (parola `p` / `p@r@la`), declarate în lista închisă a gărzii de secrete (`core/test_fara_secrete_in_git.py`)
_PROD = "postgresql://u:p@h:5432/iconta_v2"
_COPIE = _PROD.replace("/iconta_v2", "/iconta_cifre_copie")


def test_dsn_copiei_si_acreditarea_din_dsn():
    """Funcțiile PURE ale copiei: baza schimbată, restul DSN-ului neatins; parola (cu `@` în ea) tăiată de la dreapta."""
    url = "postgresql://ion:p%40r@la@db.local:6432/iconta_v2?sslmode=require"
    assert cr.dsn_cu_baza(url, "iconta_cifre_copie") == url.replace("/iconta_v2?", "/iconta_cifre_copie?")
    assert cr.env_din_dsn(url) == {"DB_HOST": "db.local", "DB_PORT": "6432", "DB_NAME": "iconta_v2", "DB_USER": "ion",
                                   "DB_PASSWORD": "p@r@la"}


def test_cu_migrari_nerulate_cifrele_se_masoara_pe_copia_migrata(monkeypatch):
    """[17.10.2026, lotul 6, poarta 1 ROȘIE] Poarta rulează înaintea migrărilor publicării: o coloană nouă citită de generatoare nu există
    încă pe producție. Cu migrări nerulate, măsurătoarea merge pe copia migrată (DATABASE_URL al copiei), iar la ieșire DSN-ul producției
    revine. MUTAȚIE: `if not lipsa:` -> `if True:` (măsurat direct, ca înainte) -> pică."""
    import contextlib
    vazut = {}
    monkeypatch.setenv("DATABASE_URL", _PROD)
    monkeypatch.setattr(cr, "migrari_nerulate", lambda: ["core/migrare_x.py"])

    @contextlib.contextmanager
    def copie(dsn, migrari):
        vazut["copie"] = (dsn, migrari)
        yield _COPIE
    monkeypatch.setattr(cr, "copie_migrata", copie)
    with cr.baza_masurata() as unde:
        vazut["masurat_pe"] = os.environ["DATABASE_URL"]
    assert vazut == {"copie": (_PROD, ["core/migrare_x.py"]), "masurat_pe": _COPIE}, vazut
    assert unde == "măsurat pe o copie a bazei, după migrările nerulate încă pe producție (1): core/migrare_x.py", unde
    assert os.environ["DATABASE_URL"] == _PROD


def test_copia_se_sterge_si_cand_migrarea_pica(monkeypatch, tmp_path):
    """Copia (o bază cu toate datele producției) nu rămâne în urmă: o migrare picată pe copie oprește măsurătoarea (fail-closed), iar
    baza și dump-ul se șterg. MUTAȚIE: `pr._sterge(BAZA_COPIE)` scos din `finally` -> pică."""
    import subprocess
    import proba_restaurare as pr
    pasi = []
    monkeypatch.setattr(pr, "DIR_DUMP", str(tmp_path))
    monkeypatch.setattr(pr, "_pg_dump", lambda env, a: (open(a[-1], "w").write("x"), pasi.append(("dump", env["DB_NAME"])),
                                                         subprocess.CompletedProcess(a, 0))[-1])
    monkeypatch.setattr(pr, "_restaureaza", lambda dump, env, baza: pasi.append(("restaurat", baza)))
    monkeypatch.setattr(pr, "_sterge", lambda baza: pasi.append(("sters", baza)))
    monkeypatch.setattr(cr.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "UndefinedTable: t"))
    try:
        with cr.copie_migrata(_PROD, ["core/migrare_x.py"]):
            raise AssertionError("măsurătoarea n-are voie să pornească pe o copie nemigrată")
    except RuntimeError as e:
        assert e.args == ("migrarea core/migrare_x.py a picat pe copie (cod 1): UndefinedTable: t",), e.args
    assert pasi == [("dump", "iconta_v2"), ("restaurat", "iconta_cifre_copie"), ("sters", "iconta_cifre_copie")], pasi
    assert list(tmp_path.iterdir()) == [], "dump-ul copiei a rămas pe disc"


def test_main_masoara_numai_prin_baza_masurata():
    """Legătura: `main` cheamă execuția numai în `baza_masurata()` (altfel copia ar exista și n-ar fi folosită).
    MUTAȚIE: `with baza_masurata() as unde:` scos din `main` -> pică."""
    import ast
    arb = ast.parse(_citeste("scripts/cifre_referinta.py"))
    main = next(n for n in arb.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    withuri = [w for w in ast.walk(main) if isinstance(w, ast.With)
               and any(ast.unparse(i.context_expr) == "baza_masurata()" for i in w.items)]
    assert withuri and any(isinstance(n, ast.Call) and ast.unparse(n.func) == "_executa" for n in ast.walk(withuri[0])), (
        "main nu măsoară prin baza_masurata()")


def test_referinta_e_numai_pe_f1_f5():
    """[17.10.2026, decizia Costin] „FISCALOS ICONTA S.R.L. rămâne în cabinetul de test, dar iese din referință; referința rămâne pe
    F1–F5.” MUTAȚIE: filtrul `in_referinta` scos din `culege` -> FISCALOS intră și `test_referinta_e_cea_aprobata` (5 firme) pică la
    următoarea scriere; aici: regula însăși."""
    assert [n for n in ("F1 Comert Stoc SRL", "F5 Salarii SRL", "FISCALOS ICONTA S.R.L.", "F6 Ceva SRL", "F10 X") if cr.in_referinta(n)] == [
        "F1 Comert Stoc SRL", "F5 Salarii SRL"]
    import ast
    culege = next(n for n in ast.parse(_citeste("scripts/cifre_referinta.py")).body if isinstance(n, ast.FunctionDef) and n.name == "culege")
    assert any(isinstance(n, ast.Call) and ast.unparse(n.func) == "in_referinta" for n in ast.walk(culege)), "culege nu filtrează pe F1–F5"
