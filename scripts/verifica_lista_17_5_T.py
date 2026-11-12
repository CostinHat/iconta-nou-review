# -*- coding: utf-8 -*-
"""scripts/verifica_lista_17_5_T.py — garda aserțiunilor testelor din lista lotului 17.5-T (T.2 d). Poarta compară aserțiunile numai pentru testele din nucleu și din plasa fixă; testele listei sunt în afara lor.
Pentru fiecare test din «lista de lucru» (rândurile cu acțiune T.2, T.3 sau T.4 din docs/dovezi/17_5_T/lista_teste_17_5_T.tsv) compară numărul de aserțiuni de pe baza lotului (merge-base cu main sau --baza)
cu cel din arborele curent (P) și iese cu 1 când:
  - numărul scade (excepție: testul scos, cu marker «scos» în fișier sau cu linie în docs/dovezi/17_5_T/scoase.txt);
  - un test atins (AST-ul funcției, fără docstring, diferă de pe bază, sau lipsește la P) nu are marker valid: «[17.5-T] actualizat la <decizie>» (T.2), «[17.5-T] stabilizat: <cauza>, <ce așteaptă acum>» (T.4)
    în docstring sau în comentariile funcției, sau «[17.5-T] scos: <nume>: <motiv>, <decizie>» în fișier, sau o linie «fișier::test | motiv | decizie» (motiv ≥ 10 caractere) în scoase.txt;
  - un test lipsește la P (sau tot fișierul e șters) fără marker «scos» / fără linie în scoase.txt.
Tipărește tabelul per test: test, grupa, aserțiuni bază, aserțiuni P, marker, și «alte noduri modificate în fișier» (constante și ajutoare de nivel modul, în afara funcțiilor de test, al căror AST diferă).
Uz: verifica_lista_17_5_T.py [--baza SHA] [--lista cale.tsv] [--scoase cale] [--tabel iesire.txt]"""
import argparse
import ast
import copy
import csv
import os
import re
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import poarta_lib as L  # noqa: E402

LISTA = os.path.join("docs", "dovezi", "17_5_T", "lista_teste_17_5_T.tsv")
SCOASE = os.path.join("docs", "dovezi", "17_5_T", "scoase.txt")
MARKERE = (re.compile(r"\[17\.5-T\] actualizat la \S.{5,}"), re.compile(r"\[17\.5-T\] stabilizat: \S.{5,}"))
_SCOS = r"\[17\.5-T\] scos: %s: \S.{9,}"


def _git_show(rad, sha, cale):
    r = subprocess.run(["git", "show", "%s:%s" % (sha, cale)], cwd=rad, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _fara_docstring(nod):
    corp = list(nod.body)
    if corp and isinstance(corp[0], ast.Expr) and isinstance(getattr(corp[0], "value", None), ast.Constant) and isinstance(corp[0].value.value, str):
        corp = corp[1:]
    c = copy.copy(nod)
    c.body = corp
    return ast.dump(c)


def _functii(text):
    """-> ({`[Clasa::]test`: (nod, sursa)}, {nume nod de nivel modul care nu e test: ast.dump}) sau (None, None) dacă textul lipsește sau nu se parsează."""
    if text is None:
        return None, None
    try:
        arbore = ast.parse(text)
    except SyntaxError:
        return None, None
    teste, module = {}, {}
    for i, nod in enumerate(arbore.body):
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)) and nod.name.startswith("test"):
            teste[nod.name] = (nod, ast.get_source_segment(text, nod) or "")
        elif isinstance(nod, ast.ClassDef):
            for f in nod.body:
                if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name.startswith("test"):
                    teste[nod.name + "::" + f.name] = (f, ast.get_source_segment(text, f) or "")
        else:
            nume = getattr(nod, "name", None) or (ast.unparse(nod.targets[0]) if isinstance(nod, ast.Assign) and nod.targets else "%s@%d" % (type(nod).__name__, i))
            if isinstance(nod, (ast.Import, ast.ImportFrom)):
                nume = "import:" + ast.unparse(nod)
            module[nume] = ast.dump(nod)
    return teste, module


def _marker(sursa):
    """Markerul valid din sursa funcției (docstring sau comentarii) sau None."""
    for rx in MARKERE:
        m = rx.search(sursa)
        if m:
            return m.group(0).strip()
    return None


def _scoase(rad, cale):
    """{`fișier::test`: (motiv, decizie)} din scoase.txt: o linie pe test, `fișier::test | motiv | decizie`, motiv de cel puțin 10 caractere."""
    iesire = {}
    try:
        for ln in open(os.path.join(rad, cale), encoding="utf-8"):
            if not ln.strip() or ln.startswith("#"):
                continue
            p = [x.strip() for x in ln.split("|")]
            if len(p) >= 3 and len(p[1]) >= 10 and p[2]:
                iesire[p[0]] = (p[1], p[2])
    except OSError:
        pass
    return iesire


def lista_de_lucru(rad, cale=LISTA):
    """[(fișier, test fără parametri, grupa)] pentru rândurile cu acțiune T.2, T.3 sau T.4, fără duplicate (testele parametrizate pe rezoluție dau o singură intrare)."""
    iesire, vazut = [], set()
    for r in list(csv.reader(open(os.path.join(rad, cale), encoding="utf-8"), delimiter="\t"))[1:]:
        if not r or not re.match(r"T\.[234]\b", r[4]):
            continue
        fis, _, test = r[0].partition("::")
        test = test.split("[")[0]
        grupa = r[3].split()[1] if r[3].startswith("grupa ") else ("T.4" if r[4].startswith("T.4") else "T.3")
        if (fis, test) not in vazut:
            vazut.add((fis, test))
            iesire.append((fis, test, grupa))
    return iesire


def verifica(rad, baza, lista=LISTA, scoase=SCOASE):
    """-> (rânduri, erori). rând = dict(test, grupa, baza, p, marker, alte)."""
    lucru = lista_de_lucru(rad, lista)
    sc = _scoase(rad, scoase)
    randuri, erori = [], []
    cache = {}

    def incarca(fis):
        if fis not in cache:
            tb, mb = _functii(_git_show(rad, baza, fis))
            cale = os.path.join(rad, fis)
            tp, mp = _functii(open(cale, encoding="utf-8").read() if os.path.exists(cale) else None)
            text_p = open(cale, encoding="utf-8").read() if os.path.exists(cale) else ""
            alte = sorted(n for n in set(mb or {}) | set(mp or {}) if (mb or {}).get(n) != (mp or {}).get(n))
            cache[fis] = (tb, tp, text_p, alte)
        return cache[fis]

    for fis, test, grupa in lucru:
        nume = "%s::%s" % (fis, test)
        tb, tp, text_p, alte = incarca(fis)
        nb = L._numara(tb[test][0]) if tb and test in tb else None
        np_ = L._numara(tp[test][0]) if tp and test in tp else None
        marker, motiv = None, ""
        scos_fisier = bool(re.search(_SCOS % re.escape(test), text_p)) if text_p else False
        if tp is None or test not in tp:                                    # lipsește la P
            if nb is None:
                motiv = ""                                                    # nu era nici pe bază: nimic de judecat
            elif nume in sc:
                marker = "scos (scoase.txt): " + sc[nume][0]
            elif scos_fisier:
                marker = "scos (în fișier)"
            else:
                erori.append("%s: lipsește la P fără marker «scos» în fișier și fără linie în scoase.txt" % nume)
        else:
            atins = nb is None or _fara_docstring(tb[test][0]) != _fara_docstring(tp[test][0])
            marker = _marker(tp[test][1])
            if atins and not marker:
                erori.append("%s: test atins fără marker «[17.5-T] actualizat la … / stabilizat: …»" % nume)
            if nb is not None and np_ < nb:
                erori.append("%s: aserțiunile au scăzut: %d → %d" % (nume, nb, np_))
        randuri.append({"test": nume, "grupa": grupa, "baza": nb, "p": np_, "marker": marker or "-", "alte": ", ".join(alte) or "-"})
    return randuri, erori


def tabel(randuri):
    antet = "test\tgrupa\taserțiuni bază\taserțiuni P\tmarker\talte noduri modificate în fișier"
    return "\n".join([antet] + ["%s\t%s\t%s\t%s\t%s\t%s" % (r["test"], r["grupa"], "-" if r["baza"] is None else r["baza"], "-" if r["p"] is None else r["p"], r["marker"], r["alte"]) for r in randuri])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--baza")
    ap.add_argument("--rad", default=RAD)
    ap.add_argument("--lista", default=LISTA)
    ap.add_argument("--scoase", default=SCOASE)
    ap.add_argument("--tabel")
    a = ap.parse_args(argv)
    baza = a.baza or subprocess.run(["git", "merge-base", "HEAD", "main"], cwd=a.rad, capture_output=True, text=True).stdout.strip()
    randuri, erori = verifica(a.rad, baza, a.lista, a.scoase)
    t = tabel(randuri)
    print(t)
    if a.tabel:
        open(a.tabel, "w", encoding="utf-8").write(t + "\n")
    for e in erori:
        print("[verifica_lista] EROARE: " + e)
    print("[verifica_lista] %d teste în lista de lucru, %d erori, baza %s" % (len(randuri), len(erori), baza[:8]))
    return 1 if erori else 0


if __name__ == "__main__":
    sys.exit(main())
