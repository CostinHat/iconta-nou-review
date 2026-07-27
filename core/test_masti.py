# -*- coding: utf-8 -*-
"""Garda: nicio masca TACUTA peste un query.

DE CE: cauza radacina a majoritatii defectelor gasite in iulie 2026. Un `except` cu corp
mut peste un `cur.execute` face ca un query rupt sa produca zero randuri - iar generatorul
scoate o declaratie VALIDA STRUCTURAL si GOALA. DUKIntegrator nu poate prinde asta: un D101
cu activitate zero e corect structural. Cazuri reale: d406 GeneralLedgerEntries mereu gol
pentru ORICE firma (coloane gresite, mascate); d406 SourceDocuments fara facturi desi
existau 5 reale.

CE CERE: inghitirea e permisa - o operatie secundara esuata nu trebuie sa opreasca operatia
principala. TACEREA nu e. Handlerul trebuie sa spuna ce a esuat: `observare.esec_secundar(...)`,
un log propriu, sau macar marcajul `# MASCA MOTIVATA:` cu explicatia.

LIMITA DECLARATA: acopera doar mastile peste QUERY (execute/fetch). Mastile peste conversii
numerice au fost tratate separat (core/numere.numar_fiscal). Nu verifica daca eticheta e
corecta, doar ca exista.
"""
import ast
import pathlib

MARCAJ = "# MASCA MOTIVATA:"
_SEMNE_QUERY = ("execute", "fetchall", "fetchone", "fetchmany")


def _radacina():
    return pathlib.Path(__file__).resolve().parent.parent


def _fisiere(rad=None):
    rad = rad or _radacina()
    for f in sorted(rad.rglob("*.py")):
        s = str(f)
        if "/venv/" in s or "/.git/" in s or "/__pycache__/" in s:
            continue
        if f.name.startswith("test_") or f.name == "conftest.py":
            continue
        yield f


def _corp_mut(h):
    """Corp care inghite fara sa spuna nimic: pass / continue / return gol-echivalent."""
    for x in h.body:
        if isinstance(x, (ast.Pass, ast.Continue)):
            continue
        if isinstance(x, ast.Return):
            v = x.value
            if v is None:
                continue
            if isinstance(v, ast.Constant) and v.value in (0, None, "", False):
                continue
            if isinstance(v, (ast.List, ast.Dict, ast.Tuple)) and not (
                    getattr(v, "elts", None) or getattr(v, "keys", None)):
                continue
        return False
    return True


def masti_tacute(rad=None):
    """[(fisier, linie)] pentru fiecare handler mut peste un query, fara marcaj."""
    gasite = []
    for f in _fisiere(rad):
        src = f.read_text(encoding="utf-8")
        try:
            t = ast.parse(src)
        except SyntaxError:
            continue
        linii = src.split("\n")
        for n in ast.walk(t):
            if not isinstance(n, ast.Try):
                continue
            corp = " ".join(ast.get_source_segment(src, b) or "" for b in n.body)
            if not any(k in corp for k in _SEMNE_QUERY):
                continue
            for h in n.handlers:
                if not _corp_mut(h):
                    continue
                sursa_h = "\n".join(linii[h.lineno - 1: h.end_lineno])
                if MARCAJ in sursa_h:
                    continue
                gasite.append((str(f.relative_to(rad or _radacina())), h.lineno))
    return gasite


def test_scanarea_nu_e_inerta():
    """Daca nu mai gaseste niciun try peste query, scanarea s-a rupt - nu e o veste buna."""
    total = 0
    rad = _radacina()
    for f in _fisiere():
        src = f.read_text(encoding="utf-8")
        try:
            t = ast.parse(src)
        except SyntaxError:
            continue
        for n in ast.walk(t):
            if isinstance(n, ast.Try):
                corp = " ".join(ast.get_source_segment(src, b) or "" for b in n.body)
                if any(k in corp for k in _SEMNE_QUERY):
                    total += 1
    assert total > 10, "doar %d try-uri peste query gasite - scanarea s-a rupt" % total


def test_nicio_masca_tacuta_peste_query():
    m = masti_tacute()
    assert not m, (
        "masti TACUTE peste query (un query rupt -> zero randuri -> rezultat gol, valid):\n" +
        "\n".join("  %s:%d" % x for x in m) +
        "\n-> fa handlerul sa SPUNA: observare.esec_secundar(eticheta, e), sau marcheaza-l\n"
        "   cu '%s <motivul>' daca tacerea e chiar decizia corecta." % MARCAJ)


def test_garda_prinde_o_masca_noua(tmp_path):
    """Mutatie: o masca tacuta noua peste query trebuie sa apara, cu fisier si linie."""
    import textwrap
    (tmp_path / "modul_nou.py").write_text(textwrap.dedent('''
        def citeste(cur):
            try:
                cur.execute("SELECT 1")
                return cur.fetchall()
            except Exception:
                return []
    ''').strip(), encoding="utf-8")
    g = masti_tacute(tmp_path)
    assert ("modul_nou.py", 5) in g, "garda nu vede masca noua: %s" % g


def test_marcajul_scuteste_dar_logul_e_de_preferat(tmp_path):
    """Masca marcata explicit nu pica - decizia scrisa e acceptata."""
    import textwrap
    (tmp_path / "modul_nou.py").write_text(textwrap.dedent('''
        def citeste(cur):
            try:
                cur.execute("SELECT 1")
                return cur.fetchall()
            except Exception:
                # MASCA MOTIVATA: tabela e optionala pe tenantii vechi
                return []
    ''').strip(), encoding="utf-8")
    assert masti_tacute(tmp_path) == []


def test_handler_care_logheaza_nu_e_masca(tmp_path):
    """Un handler care SPUNE ce s-a intamplat nu e mut - fara marcaj, trece."""
    import textwrap
    (tmp_path / "modul_nou.py").write_text(textwrap.dedent('''
        def citeste(cur):
            try:
                cur.execute("SELECT 1")
                return cur.fetchall()
            except Exception as e:
                _obs.esec_secundar("citire", e)
                return []
    ''').strip(), encoding="utf-8")
    assert masti_tacute(tmp_path) == []
