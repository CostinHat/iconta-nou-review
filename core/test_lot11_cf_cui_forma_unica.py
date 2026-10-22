# -*- coding: utf-8 -*-
"""[lotul 11, subagentul CF — decizia Costin 10.3 pct.4 + deficiența 459, verbatim în DECIZII „Comanda 10.3”: „CUI-ul se păstrează fără
«RO» și fără spații; «RO» apare doar la afișare, după starea de plătitor de TVA.”] CLASA (CICLUL DE NECONFORMITATE): o normalizare LOCALĂ
a codului fiscal („scoate RO”), paralelă cu forma unică `core/cui_forma.stocare` — fiecare cu dialectul ei: `.replace("RO", "")` (scoate
„RO” de oriunde din text și e sensibil la majuscule), `startswith("RO")` + `[2:]` (fără spațiile din mijloc), `re.sub(r"^RO", …)`, SQL
`replace(tert_cui, 'RO', '')`. Două dialecte dau două răspunsuri la „e același partener?”: factura veche „RO 185 47290” nu se mai potrivea
cu extrasul „18547290”.

1. Comportamentul fiecărui loc reparat = `cui_forma.stocare` (testele `test_*_forma_unica`), pe cazurile care despart dialectele: spațiu
   NBSP în mijloc (copiat dintr-un document), majuscule, codul de TVA al unui partener din alt stat (rămâne cu prefixul lui).
2. GARDA permanentă (`test_garda_nicio_normalizare_locala_a_prefixului_ro`): AST pe tot `core/`, `scripts/`, `main.py` (fără teste) +
   text pe `static/js` — nicio normalizare locală a prefixului „RO” în afara lui `core/cui_forma.py` și a listei `EXCEPTATE`, fiecare cu
   motivul (format de ieșire ANAF / detectarea codului de TVA RO, nu păstrare). O excepție care nu mai apare în cod pică și ea
   (`test_exceptiile_sunt_toate_vii`): lista nu poate rămâne mai largă decât codul.

CUI-urile de test au cifra de control verificată (algoritmul din CLAUDE.md, `_cui_valid` mai jos); „DE123456789” e numai o formă de cod de
TVA străin (prefix + cifre), nu se verifică și nu se scrie în bază.
"""
import ast
import os
import re

import pytest

from core import cui_forma as cf

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CUI = "18547290"                 # cifra de control verificată (test_cui_urile_de_test_sunt_valide)
CNP = "1800101221144"            # cifra de control verificată (același CNP ca în test_384_cote_asociati.py)
NBSP = " "
#: forme scrise ale aceluiași cod + cazurile de margine; fiecare loc reparat trebuie să dea exact `stocare`
CAZURI = ["RO 185" + NBSP + "47290", "ro18547290", " 185 47290 ", "RO18547290", CUI, "DE123456789", "", None, CNP]


def _cui_valid(cui):
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui)
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = (sum(int(corp[i]) * ch[i] for i in range(9)) * 10) % 11
    return (0 if r == 10 else r) == ctrl


def _cnp_valid(cnp):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(cnp[i]) * ch[i] for i in range(12)) % 11
    return str(1 if c == 10 else c) == cnp[12]


def test_cui_urile_de_test_sunt_valide():
    assert _cui_valid(CUI) and _cnp_valid(CNP)


# ══════════════════════════════════════════════════════════════════ 1. LOCURILE REPARATE = FORMA UNICĂ
def test_compensari_cui_partener_forma_unica():
    from core import compensari_api as cz
    # contractul apelanților (`not cui_partener(...)`, cheia JSON „cui”): "" fără cod, nu None
    assert [cz.cui_partener(v) for v in CAZURI] == [cf.stocare(v) or "" for v in CAZURI]


def test_reconciliere_factura_veche_cu_spatii_se_potriveste_cu_extrasul():
    """Factura scrisă înainte de normalizare („RO 185<NBSP>47290”, documentele nu se rescriu — `migrare_cui_fara_ro`) și linia de extras
    cu „18547290” sunt același partener. Înainte (`_norm_cui`, `.replace("RO", "")`): spațiul din mijloc rămânea -> factura lipsea."""
    from core import reconciliere as rec
    f = {"id": 7, "tert_cui": "RO 185" + NBSP + "47290", "directie": "emisa", "data_emitere": "2026-01-05", "sold": "100.00"}
    assert [x["id"] for x in rec.facturi_partener([f], CUI, "incasare")] == [7]
    rez = rec.potriveste_linie({"suma": "100.00", "tip": "incasare", "cui": "ro" + CUI, "descriere": "", "data": "2026-01-10"}, [f])
    assert rez["status"] == "verde" and [a["factura_id"] for a in rez["alocari"]] == [7], rez


def test_asociati_ecran_identificatorul_forma_unica():
    from core import asociati_api as aa
    r = aa.randuri_din_corp([{"nume": "X", "cnp": v, "cota": "10"} for v in CAZURI])
    assert [x["cnp"] for x in r] == [cf.stocare(v) or "" for v in CAZURI]
    assert r[CAZURI.index(CNP)]["cnp"] == CNP   # un CNP n-are „RO”: rămâne neatins


def test_asociati_import_identificatorul_forma_unica():
    from core import asociati_import_api as ai
    r = ai.extrage(("Nume;CNP;Cota\nFirma Asociat SRL;RO 185%s47290;40\nPop Ion;%s;60\n" % (NBSP, CNP)).encode(), "asociati.csv")
    assert [(x["cnp"], x["tip"], x["cnp_valid"]) for x in r] == [(CUI, "juridica", True), (CNP, "fizica", True)], r


def test_solduri_parteneri_import_cui_forma_unica():
    from core import solduri_parteneri_api as sp
    r = sp.extrage(("Cont;Cod fiscal;Denumire;Sold debitor;Sold creditor\n4111;RO 185%s47290;A;10;0\n" % NBSP).encode(), "p.csv")
    assert [x["cui"] for x in r] == [CUI], r


def test_bon_facturi_candidate_potrivire_cui_forma_unica(monkeypatch):
    """Bonul scris înainte de normalizare („RO 185<NBSP>47290”) și factura „18547290” = același furnizor (`potrivire_cui`), iar
    căutarea primește codul în forma păstrată."""
    import contextlib
    from core import uc_tenants as ut
    primit = {}
    monkeypatch.setattr(ut.db, "get_conn", lambda *a, **k: contextlib.nullcontext(type("C", (), {
        "cursor": lambda self, *a, **k: contextlib.nullcontext(None)})()))
    monkeypatch.setattr(ut.auth_api, "schema_tenant", lambda conn, uid, tid: "tenant_x")
    monkeypatch.setattr(ut.repo_casa, "cui_si_total_bon", lambda cur, s, bid: ("RO 185" + NBSP + "47290", 119))

    def _candidate(cur, s, cui, suma):
        primit["cui"] = cui
        return [(1, "12", "F", None, 119, "Furnizor", CUI), (2, "13", "F", None, 119, "Altul", "DE123456789")]
    monkeypatch.setattr(ut.repo_facturi, "candidate_pentru_bon", _candidate)
    rez = ut.bon_facturi_candidate(1, 5, {"uid": 1})
    assert primit["cui"] == CUI
    assert [x["potrivire_cui"] for x in rez["facturi"]] == [True, False], rez


def test_anaf_tva_check_intreaba_anaf_cu_forma_pastrata(monkeypatch):
    from core import uc_comun as uc
    cerute = []
    monkeypatch.setattr(uc.anaf_api, "valideaza_cui", lambda lista: cerute.append(list(lista)) or [{"gasit": False}])
    for v in ("ro" + CUI, "RO 185" + NBSP + "47290", "  ", None):
        uc._anaf_tva_check(v, None)
    assert cerute == [[CUI], [CUI]]   # golul nu ajunge la ANAF


def test_seed_d406_repara_cui_in_forma_pastrata():
    """`scripts/seed_alfa_d406.py` scrie CUI-ul reparat în forma păstrată (fără „RO”). Scriptul atinge baza la import, deci funcțiile
    se citesc din AST și se rulează izolat."""
    cale = os.path.join(RADACINA, "scripts", "seed_alfa_d406.py")
    arb = ast.parse(open(cale, encoding="utf-8").read())
    fn = [n for n in arb.body if isinstance(n, ast.FunctionDef) and n.name in ("cif_check", "cif_valid", "repara_cui")]
    ns = {"_forma_cui": cf}
    exec(compile(ast.Module(body=fn, type_ignores=[]), cale, "exec"), ns)
    nou = ns["repara_cui"]("RO12345678")
    assert nou == cf.stocare(nou) and nou.isdigit() and _cui_valid(nou) and ns["cif_valid"](nou), nou
    assert ns["cif_valid"]("ro " + CUI) and not ns["cif_valid"]("DE123456789")


# ══════════════════════════════════════════════════════════════════ 1b. PARITATEA PYTHON – SQL A FORMEI UNICE
#: fiecare spațiu Unicode (`str.isspace`, deci `\s` din Python), pus în mijlocul și în fața unui cod
SPATII = [chr(i) for i in range(0x110000) if chr(i).isspace()]
MOSTRE_SPATII = [("RO%s185%s47290" % (s, s)) for s in SPATII] + ["RO١٢٣", "RO" + CUI, "DE 123456789", "ROMANIA", ""]


def _conn_test():
    try:
        from core import db
        db.init_pool()
        return db
    except Exception:  # noqa: BLE001 — fără bază de test: testul de paritate se sare (cel pe Python rămâne)
        return None


@pytest.mark.skipif(_conn_test() is None, reason="DB indisponibil")
@pytest.mark.parametrize("expresie", ["cui_forma.SQL", "migrare_cui_fara_ro.EXPR"])
def test_paritatea_spatiilor_python_sql(expresie):
    """`cui_forma.SQL` (comparațiile pe coloane) și expresia triggerului `trg_cui_fara_ro` (`migrare_cui_fara_ro.EXPR`) dau exact
    `stocare` pe FIECARE spațiu Unicode. Înainte: `'\\s'` din PostgreSQL nu vedea U+00A0 / U+202F / U+2007 / U+0085 / U+001C–U+001F,
    deci „RO<NBSP>18547290” rămânea cu „RO” în bază și în comparațiile SQL, iar Python îl dădea „18547290”."""
    from core import db, migrare_cui_fara_ro as m
    sql = cf.SQL.format(c="v") if expresie == "cui_forma.SQL" else m.EXPR
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT v, %s FROM unnest(%%s::text[]) WITH ORDINALITY t(v, i) ORDER BY i" % sql, (MOSTRE_SPATII,))
            rez = cur.fetchall()
        c.rollback()
    diferite = [("U+%04X" % ord(v[2]) if len(v) > 2 else v, s) for v, s in rez if (s or None) != cf.stocare(v)]
    assert not diferite, "%s diferă de `cui_forma.stocare` pe: %s" % (expresie, diferite)


# ══════════════════════════════════════════════════════════════════ 2. GARDA
#: (fișier, funcție, tip) -> motivul pentru care locul NU e o normalizare de păstrare (rămâne, prin natura lui)
EXCEPTATE = {
    ("core/anaf_api.py", "statut_furnizori", "startswith_RO"):
        "detectare, nu normalizare: codul „RO…” din XML-ul e-Factura (BT-31) e codul de TVA, deci furnizorul e înregistrat în scopuri "
        "de TVA (CF art.318 alin.(1)) — se citește starea, codul nu se rescrie",
    ("core/d318.py", "erori_generare", "startswith_RO"):
        "nu e un cod fiscal: `reference_number` al cererii de rambursare (DUK regula R9.2: începe cu „RO”)",
    ("core/d394.py", "cui_ro", "startswith_RO"):
        "format de ieșire: `cuiP` din D394 = numai cifre (XSD); `_NEDIGIT` scoate oricum prefixul — nu e forma păstrată în bază",
    ("core/d394_reconciliere.py", "_partener", "slice_RO"):
        "reconcilierea D394 e o oglindă INDEPENDENTĂ a lui `d394.clasifica_partener` (nu-l importă, prin construcție): cifrele codului, "
        "pentru clasificare, nu forma păstrată",
    ("core/efactura_send.py", "genereaza_xml", "slice_RO"):
        "format de ieșire: BT-47 (identificatorul legal, RO_CIUS BR-RO-120) = cifrele CUI-ului; `[2:]` scoate „RO” pus chiar de `_vatid`",
    ("core/factura_pdf.py", "cod_fiscal_pe_factura", "startswith_RO"):
        "afișare (CF art.318 alin.(1)): pe un cod scris înainte de normalizare, cu starea necunoscută, prefixul e chiar informația de TVA "
        "arătată pe factură — se citește, nu se păstrează",
    ("core/facturi_api.py", "spv_obligatorie", "startswith_RO"):
        "detectare (OUG 120/2021 art.10 alin.(1^1)): un cod de TVA „RO…” = înregistrat în scopuri de TVA în România — nu rescrie codul",
}
#: fișierele care SUNT forma unică (sursa și oglinda ei SQL, paritatea păzită de core/test_lot11_p_cui.py)
SURSE = {"core/cui_forma.py", "core/migrare_cui_fara_ro.py"}

_SQL_RO = re.compile(r"replace\s*\([^;]*?'RO'\s*,\s*''\s*\)|regexp_replace\s*\([^;]*?'\^RO", re.I)
_JS_RO = re.compile(r"""\.replace\(\s*(?:/\^?\(?RO|["']RO["'])|\.startsWith\(\s*["']RO["']\s*\)""", re.I)


def _e_ro(v):
    return isinstance(v, str) and v.upper() == "RO"


def _felie_2(n):
    return isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Slice) and n.slice.upper is None and \
        isinstance(n.slice.lower, ast.Constant) and n.slice.lower.value == 2


def _tip(n):
    """Tipul normalizării locale a prefixului „RO” din nodul `n`, sau None."""
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.args:
        a0, at = n.args[0], n.func.attr
        v = a0.value if isinstance(a0, ast.Constant) else None
        if at == "replace" and _e_ro(v):
            return "replace_RO"
        if at in ("lstrip", "strip", "removeprefix") and isinstance(v, str) and {"R", "O"} <= set(v.upper()):
            return "strip_RO"
        if at == "startswith" and (_e_ro(v) or (isinstance(a0, ast.Tuple) and any(
                isinstance(e, ast.Constant) and _e_ro(e.value) for e in a0.elts))):
            return "startswith_RO"
        if at == "sub" and isinstance(v, str) and v.upper().lstrip("(?I)").startswith("^RO"):
            return "re_sub_RO"
    if isinstance(n, (ast.If, ast.IfExp)) and isinstance(n.test, ast.Compare) and any(
            isinstance(c, ast.Constant) and _e_ro(c.value) for c in [n.test.left] + list(n.test.comparators)):
        corp = n.body if isinstance(n.body, list) else [n.body]
        if any(_felie_2(x) for b in corp for x in ast.walk(b)):
            return "slice_RO"
    if isinstance(n, ast.Constant) and isinstance(n.value, str) and _SQL_RO.search(n.value):
        return "sql_RO"
    return None


def _fisiere_py(radacina):
    out = [os.path.join(radacina, "main.py")]
    for d in ("core", "scripts"):
        for rad, dirs, fs in os.walk(os.path.join(radacina, d)):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            out += [os.path.join(rad, f) for f in fs if f.endswith(".py") and not f.startswith("test_")]
    return sorted(out)


def aparitii(radacina=RADACINA):
    """[(fișier, funcție, tip, linie)] — toate normalizările locale ale prefixului „RO”, în afara SURSELOR."""
    out = []
    for cale in _fisiere_py(radacina):
        rel = os.path.relpath(cale, radacina)
        if rel in SURSE:
            continue
        arb = ast.parse(open(cale, encoding="utf-8").read(), cale)
        par = {c: n for n in ast.walk(arb) for c in ast.iter_child_nodes(n)}
        for n in ast.walk(arb):
            t = _tip(n)
            if not t:
                continue
            lant, p = [], n
            while p in par:
                p = par[p]
                if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    lant.append(p.name)
            out.append((rel, ".".join(reversed(lant)) or "<modul>", t, n.lineno))
    for rad, dirs, fs in os.walk(os.path.join(radacina, "static", "js")):
        for f in fs:
            if f.endswith(".js") and not f.endswith(".min.js"):
                cale = os.path.join(rad, f)
                for i, ln in enumerate(open(cale, encoding="utf-8"), 1):
                    if _JS_RO.search(ln):
                        out.append((os.path.relpath(cale, radacina), "<js>", "js_RO", i))
    return out


def test_garda_nicio_normalizare_locala_a_prefixului_ro():
    noi = ["%s:%d %s (%s)" % (f, ln, fn, t) for f, fn, t, ln in aparitii() if (f, fn, t) not in EXCEPTATE]
    assert not noi, ("Normalizare LOCALĂ a prefixului „RO” al codului fiscal în afara formei unice. Folosește `core.cui_forma.stocare` "
                     "(Python) / `cui_forma.SQL` (SQL), comparând forma păstrată pe ambele părți — decizia Costin 10.3 pct.4. Dacă locul "
                     "e un FORMAT de ieșire sau o detectare a codului de TVA, adaugă-l în EXCEPTATE cu motivul:\n  " + "\n  ".join(noi))


def test_exceptiile_sunt_toate_vii():
    vii = {(f, fn, t) for f, fn, t, _ln in aparitii()}
    moarte = sorted(k for k in EXCEPTATE if k not in vii)
    assert not moarte, "excepții care nu mai apar în cod — scoate-le din EXCEPTATE: %s" % moarte


@pytest.mark.parametrize("bucata,tip", [
    ('def f(c):\n    return c.upper().replace("RO", "")\n', "replace_RO"),
    ('def f(c):\n    return c.lstrip("RO")\n', "strip_RO"),
    ('def f(c):\n    return c.removeprefix("RO")\n', "strip_RO"),
    ('def f(c):\n    return c[2:] if c.startswith("RO") else c\n', "startswith_RO"),
    ('import re\ndef f(c):\n    return re.sub(r"^RO", "", c)\n', "re_sub_RO"),
    ('def f(c, p):\n    return c[2:] if p == "RO" else c\n', "slice_RO"),
    ('Q = "SELECT 1 FROM t WHERE upper(replace(COALESCE(tert_cui,\'\'),\'RO\',\'\')) = %s"\n', "sql_RO"),
])
def test_CALIBRARE_garda_vede_fiecare_dialect(bucata, tip):
    """Fiecare formă a clasei e văzută (calibrarea gărzii: altfel „zero apariții” n-ar dovedi nimic)."""
    assert [_tip(n) for n in ast.walk(ast.parse(bucata)) if _tip(n)] == [tip]


def test_CALIBRARE_garda_nu_vede_ce_nu_e_clasa():
    """IBAN-ul („^RO\\d{2}…”, validare), țara „RO” și cifrele codului (`_NEDIGIT`) nu sunt normalizarea prefixului."""
    for bucata in ('import re\nX = re.compile(r"^RO\\d{2}[A-Z0-9]{20}$")\n', 'def f(t):\n    return t == "RO"\n',
                   'def f(c):\n    return "".join(x for x in c if x.isdigit())\n'):
        assert not [n for n in ast.walk(ast.parse(bucata)) if _tip(n)], bucata
    assert not _JS_RO.search('if (/^(RO)?\\d{2,10}$/.test(c)) return "RO";')
    assert _JS_RO.search('const c = cui.replace(/^RO/i, "");')
