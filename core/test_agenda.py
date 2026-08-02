# -*- coding: utf-8 -*-
"""Garda anti-stale a agendei: pica daca TESTE.md a ramas in urma codului. Diferenta fata de DE_FACUT.md
(care a murit necitit): agenda e scrisa de mana DAR pazita mecanic - docul in urma codului pica suita."""
import os
import re
import ast
import subprocess
import datetime
import pathlib

from core import agenda

_RAD = pathlib.Path(__file__).resolve().parent.parent


def _git_at(cale):
    """Timestamp Unix al ultimului commit care a atins `cale` (NU mtime - se schimba la checkout)."""
    r = subprocess.run(["git", "-C", str(_RAD), "log", "-1", "--format=%at", "--", str(cale)],
                       capture_output=True, text=True)
    t = r.stdout.strip()
    return int(t) if t else None


def _ast_functie(src, nume):
    """ast.dump al functiei `nume` cu docstring-ul scos. Comentariile nu-s in AST (ignorate automat);
    formatarea e ignorata de ast.dump. None daca src nu se parseaza; '<ABSENT>' daca functia nu exista
    (redenumita/stearsa -> tratat ca schimbat)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == nume:
            b = node.body
            if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) \
               and isinstance(b[0].value.value, str):
                node.body = b[1:]
            return ast.dump(node)
    return "<ABSENT>"


def _functie_schimbata(relpath, func, data_verif):
    """(schimbat: bool, nota_fallback: str|None). Compara AST-ul functiei `func` (fara docstring) intre
    commitul de la data_verif (ultimul <= data) si HEAD. Fallback VIZIBIL daca o versiune nu se parseaza."""
    iso = data_verif.isoformat()
    oc = subprocess.run(["git", "-C", str(_RAD), "log", "--until=%s 23:59:59" % iso, "-1", "--format=%H",
                         "--", relpath], capture_output=True, text=True).stdout.strip()
    if not oc:
        return True, None
    old = subprocess.run(["git", "-C", str(_RAD), "show", "%s:%s" % (oc, relpath)],
                         capture_output=True, text=True).stdout
    new = subprocess.run(["git", "-C", str(_RAD), "show", "HEAD:%s" % relpath],
                         capture_output=True, text=True).stdout
    ao, an = _ast_functie(old, func), _ast_functie(new, func)
    if ao is None or an is None:
        return True, "versiunea nu se parseaza; fallback pe fisier pentru %s::%s" % (relpath, func)
    return (ao != an), None


def test_fiecare_modul_A_are_fisier_de_test():
    a = agenda.stare_sesiune_a()
    assert a is not None, "Inventarul sesiunii A lipseste din TESTE.md"
    lipsa = []
    for rand in a["rows"]:
        if not rand["fisiere"]:
            lipsa.append(rand["modul"] + " (niciun fisier numit)")
            continue
        for f in rand["fisiere"]:
            if not (_RAD / "core" / f).exists():
                lipsa.append("%s -> %s (inexistent)" % (rand["modul"], f))
    assert not lipsa, "module A fara fisier de test in repo (contopeste sau adauga fisierul): %s" % lipsa


def test_verificarile_A_nu_sunt_in_urma_codului():
    """Un cluster √ DD.MM e STALE daca FUNCTIA lui de test s-a schimbat substantial dupa acea data
    (nivel de FUNCTIE, nu de fisier - 30.07: verificarea unui cluster nou NU mai reseteaza clusterele
    co-locate in acelasi fisier). Docstring/comentariu/format NU reseteaza (varianta c la nivel de
    functie). Co-locatie (clustere ce impart o functie de test): se reseteaza IMPREUNA, mesajul o spune.
    Ruleaza pe starea COMISA (git HEAD): commit INTAI, apoi poarta."""
    import collections
    a = agenda.stare_sesiune_a()
    assert a is not None
    azi = datetime.date.today()
    folos = collections.defaultdict(list)   # (relpath, functie) -> [(cluster, data_verif)]
    for rand in a["rows"]:
        if not rand["verificat"] or "." not in rand["verificat"]:
            continue
        if not rand["fisiere"] or not rand.get("functie"):
            continue
        zi, luna = rand["verificat"].split(".")[:2]
        dv = datetime.date(azi.year, int(luna), int(zi))
        relpath = "core/" + rand["fisiere"][0]
        for fn in rand["functie"]:
            folos[(relpath, fn)].append((rand["cluster"], dv))
    stale = []
    for (relpath, fn), cl in sorted(folos.items()):
        dv = min(d for _, d in cl)   # cea mai veche data (conservator)
        schimbat, nota = _functie_schimbata(relpath, fn, dv)
        nume = [c for c, _ in cl]
        if nota:
            stale.append("%s::%s: %s (clustere: %s)" % (relpath, fn, nota, ", ".join(nume)))
        elif schimbat:
            co = "  [CO-LOCATIE - clustere resetate impreuna]" if len(nume) > 1 else ""
            stale.append("functia de test %s::%s s-a schimbat substantial -> reverifica la sursa: %s%s"
                         % (relpath, fn, ", ".join(nume), co))
    assert not stale, "AGENDA STALE (functie de test in urma docului):\n" + "\n".join(stale)


def test_fiecare_xfail_apare_in_raport():
    d = agenda.datorii_deschise()
    assert d, "nicio datorie xfail citita din test_datorie.py"
    rap = agenda.raport(tehnic=False)
    lipsa = [n for n, _ in d if n not in rap]
    assert not lipsa, "datorii care nu apar in raportul agendei: %s" % lipsa


def test_agenda_ruleaza_fara_eroare():
    rap = agenda.raport(tehnic=False)
    assert "AGENDA iConta" in rap and "URMATORUL PAS" in rap and "DESCHIS ACUM" in rap


def test_stare_tehnica_numara_toata_suita():
    """STARE TEHNICA trebuie sa numere suita de la RADACINA (core/ + radacina), nu un subset.
    Bug 30.07.2026: agenda rula `pytest core/` (colecta doar un subset), dar suita reala e cea
    de la radacina -> STARE TEHNICA afisa un numar mai mic decat realitatea. Compara SCOPE-ul
    colectat (--collect-only), nu ruleaza suita de doua ori. (Fara literal cu numar+passed in
    text, ca traceback-ul la esec sa nu otraveasca regexul din stare_tehnica.)"""
    py = str(_RAD / "venv" / "bin" / "python3")
    if not os.path.exists(py):
        py = "python3"

    def _colectate(scope):
        # UN singur -q: dublu -q schimba formatul --collect-only si dispare 'N tests collected'
        args = ["--collect-only", "-q"] + [x for x in scope if x != "-q"]
        r = subprocess.run([py, "-m", "pytest"] + args,
                           cwd=str(_RAD), capture_output=True, text=True, timeout=120)
        m = re.search(r"(\d+) tests? collected", r.stdout)
        return int(m.group(1)) if m else None

    n_agenda = _colectate(agenda.PYTEST_ARGS)   # scope-ul REAL folosit de stare_tehnica
    n_radacina = _colectate([])                 # radacina, fara niciun filtru
    assert n_agenda is not None and n_radacina is not None, \
        "nu s-a putut parsa 'N tests collected' din pytest --collect-only"
    assert n_agenda == n_radacina, \
        "STARE TEHNICA numara %d, radacina are %d -> agenda ar afisa un numar fals" % (n_agenda, n_radacina)


def test_garda_functie_distinge_functia_clusterului():
    """Mutatie pe garda de FUNCTIE, ambele sensuri (Costin, 30.07):
    - schimbare in ASSERT-ul functiei clusterului -> AST difera (reseteaza);
    - schimbare in ALTA functie din acelasi fisier -> functia clusterului NEatinsa (NU reseteaza) -
      cazul care dovedeste upgrade-ul de la fisier la functie;
    - schimbare DOAR de docstring in functia clusterului -> NU reseteaza (varianta c la nivel functie);
    - functie absenta -> tratata ca schimbata."""
    vechi = ('def test_cluster():\n    "doc"\n    assert calc(2) == 4\n\n'
             'def test_alta():\n    assert alt(1) == 1\n')
    assert_schimbat = ('def test_cluster():\n    "doc"\n    assert calc(2) == 5\n\n'
                       'def test_alta():\n    assert alt(1) == 1\n')
    alta_schimbata = ('def test_cluster():\n    "doc"\n    assert calc(2) == 4\n\n'
                      'def test_alta():\n    assert alt(1) == 999\n')
    doar_docstring = ('def test_cluster():\n    "doc NOU, reformulat"\n    assert calc(2) == 4  # comentariu\n\n'
                      'def test_alta():\n    assert alt(1) == 1\n')
    assert _ast_functie(vechi, "test_cluster") != _ast_functie(assert_schimbat, "test_cluster"), \
        "schimbarea de assert NU reseteaza"
    assert _ast_functie(vechi, "test_cluster") == _ast_functie(alta_schimbata, "test_cluster"), \
        "schimbarea in ALTA functie reseteaza clusterul (upgrade-ul fisier->functie nu tine)"
    assert _ast_functie(vechi, "test_cluster") == _ast_functie(doar_docstring, "test_cluster"), \
        "schimbarea de docstring reseteaza (varianta c cazuta la nivel de functie)"
    assert _ast_functie("def x():\n    pass\n", "test_cluster") == "<ABSENT>", "functia absenta nedetectata"


def _fisiere_din_garzi_acoperit(text):
    """Fisierele numite in bullet-urile ACOPERIT din GARZI (bulletul + continuarile lui indentate).
    NU si cele din LIPSA/PARTIAL - acolo un fisier poate lipsi legitim (e chiar gardul care lipseste)."""
    fisiere = []
    inside = False
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith("- "):
            inside = s.startswith("- ACOPERIT") or (s.startswith("- **") and "ACOPERIT" in s)
        elif s.startswith("#"):
            inside = False
        if inside:
            fisiere += re.findall(r"core/[\w/]+\.py", line)
            fisiere += re.findall(r"\btest_\w+\.py", line)
    return fisiere


def test_garzi_acoperit_are_fisierele_numite():
    """Un gard marcat ACOPERIT trebuie sa aiba fisierul pe care il numeste - altfel registrul minte
    in sens invers (spune acoperit ce nu exista). Simetric cu Inventarul A."""
    g = (_RAD / "GARZI.md").read_text(encoding="utf-8")
    lipsa = []
    for tok in _fisiere_din_garzi_acoperit(g):
        ok = (_RAD / tok).exists() if tok.startswith("core/") else \
            ((_RAD / "core" / tok).exists() or (_RAD / tok).exists())
        if not ok:
            lipsa.append(tok)
    assert not lipsa, "GARZI ACOPERIT numeste fisiere inexistente: %s" % sorted(set(lipsa))


def _titluri_h2(text):
    return [ln.strip() for ln in text.splitlines() if ln.startswith("## ")]


def _h2_duplicate(titluri):
    return sorted({t for t in titluri if titluri.count(t) > 1})


def test_teste_md_fara_titluri_duplicate():
    """Doua sectiuni cu acelasi titlu = drift: agenda citeste PRIMA, a doua ramane stale invizibil.
    Exact bug-ul din 30.07 (doua '## Starea sesiunii B')."""
    dubluri = _h2_duplicate(_titluri_h2((_RAD / "TESTE.md").read_text(encoding="utf-8")))
    assert not dubluri, "titluri ## duplicate in TESTE.md (agenda citeste doar primul): %s" % dubluri


def test_garzi_si_duplicat_prind_defectul():
    """Mutatie pe cele doua garzi noi: fabricam defectul, garda il prinde; pe curat, tace."""
    fals = ("- ACOPERIT: `core/exista_ac.py` — foo\n"
            "  test_exista_ac.py bar\n"
            "- LIPSA: **Y** — core/planificat_lipsa.py\n")
    toks = _fisiere_din_garzi_acoperit(fals)
    assert "core/exista_ac.py" in toks and "test_exista_ac.py" in toks, "nu extrage fisierele din ACOPERIT"
    assert "core/planificat_lipsa.py" not in toks, "scaneaza gresit fisiere din LIPSA (pot lipsi legitim)"
    assert _h2_duplicate(["## A", "## B", "## A"]) == ["## A"], "nu prinde titlul duplicat"
    assert _h2_duplicate(["## A", "## B"]) == [], "fals-pozitiv pe titluri unice"



def test_fiecare_fisier_test_are_cel_putin_un_test():
    """GARZI cat.9 (onestitatea testelor): un fisier test_*.py (exclus venv) cu 0 functii 'def test_'
    pare acoperire care NU exista - pytest nu-l colecteaza, dar numele sugereaza suita. Un script
    functional nu trebuie sa poarte prefixul test_. Prinde scripturile deghizate; verde cand nu exista."""
    goale = []
    for f in sorted(_RAD.rglob("test_*.py")):
        if "venv" in f.parts:
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^\s*(async\s+)?def test_", src, re.MULTILINE):
            goale.append(str(f.relative_to(_RAD)))
    assert not goale, ("fisiere test_*.py cu 0 functii 'def test_' (redenumeste-le fara prefixul test_ "
                       "- sunt scripturi, nu suita): %s" % goale)


def _data_ddmm(cell):
    """(luna, zi) din prima data DD.MM a unei celule Verificat. None daca nu are bifa-data."""
    m = re.search(r"\d{1,2}\.\d{1,2}", cell or "")
    if not m:
        return None
    zi, luna = m.group(0).split(".")[:2]
    return (int(luna), int(zi))


def test_bifa_bumpuita_are_motiv():
    """O bifa mutata INAINTE (data crescuta fata de prima ei aparitie in istoricul comis al TESTE.md)
    TREBUIE sa poarte motivul mutarii ('bump: ...') in coloana Verificat. Altfel garda anti-stale
    devine ornament: functia de test se schimba -> garda pica -> cineva bumpeaza data -> verde, fara
    reverificare la sursa (reset semnalat -> bump -> verde). Ancora canonica, imutabila in istoric:
    facilitate a fost mutata 29.07->31.07 la FIX3 (net-ul derivat s-a mutat in
    test_minim_4325_are_facilitate_sem2). Ruleaza pe starea COMISA a istoricului (git log/show)."""
    cur = agenda.inventar_verificat_raw((_RAD / "TESTE.md").read_text(encoding="utf-8"))
    hist = subprocess.run(["git", "-C", str(_RAD), "log", "--format=%H", "--", "TESTE.md"],
                          capture_output=True, text=True).stdout.split()
    earliest = {}   # cluster -> cea mai veche (luna, zi) bifa vazuta in istoric
    for h in hist:
        txt = subprocess.run(["git", "-C", str(_RAD), "show", "%s:TESTE.md" % h],
                             capture_output=True, text=True).stdout
        for cl, cell in agenda.inventar_verificat_raw(txt).items():
            d = _data_ddmm(cell)
            if d and (cl not in earliest or d < earliest[cl]):
                earliest[cl] = d
    # anti-vacuu (GARZI cat.9): daca parserul/istoricul se rup, earliest se goleste si testul ar
    # trece degeaba. Ancoram pe bump-ul real cunoscut: facilitate a pornit la 29.07.
    assert earliest.get("facilitate salariu minim") == (7, 29), \
        "istoricul TESTE.md nu mai arata bifa 29.07 initiala la facilitate - parser/istoric rupt, garda ar trece vacuu"
    lipsa = []
    for cl, cell in cur.items():
        d = _data_ddmm(cell)
        e = earliest.get(cl)
        if d and e and d > e and not re.search(r"bump:\s*\S", cell, re.IGNORECASE):
            lipsa.append("%s: bifa mutata %02d.%02d->%02d.%02d fara 'bump: <motiv>'"
                         % (cl, e[1], e[0], d[1], d[0]))
    assert not lipsa, ("bifa mutata inainte fara motiv inregistrat (garda anti-stale devine ornament):\n"
                       + "\n".join(lipsa))


# ============================================================
#  V3 (02.08.2026) — RESETAREA PROPAGATA pe dependentele din graf
#  Garda anti-stale de FUNCTIE vede doar codul testelor; ASTA vede COTELE de care depinde clusterul.
#  Inchide esecul de temut: o bifa care sta pe o baza (cota) schimbata dupa √, fara ca nimic sa semnaleze.
# ============================================================
def _cota_schimbata(nume, data_verif):
    """Intrarea COTE[nume] (DOAR valori, fara temei) s-a schimbat in core/common.py intre commitul de la
    data_verif si HEAD? Analog _functie_schimbata, dar pentru o cota."""
    relpath = "core/common.py"
    iso = data_verif.isoformat()
    oc = subprocess.run(["git", "-C", str(_RAD), "log", "--until=%s 23:59:59" % iso, "-1", "--format=%H",
                         "--", relpath], capture_output=True, text=True).stdout.strip()
    if not oc:
        return False
    old = subprocess.run(["git", "-C", str(_RAD), "show", "%s:%s" % (oc, relpath)], capture_output=True, text=True).stdout
    new = subprocess.run(["git", "-C", str(_RAD), "show", "HEAD:%s" % relpath], capture_output=True, text=True).stdout
    vo, vn = agenda.cota_valori(old, nume), agenda.cota_valori(new, nume)
    if vo is None or vn is None:
        return True
    return vo != vn


def test_cota_valori_distinge_schimbarea_de_baza():
    """cota_valori vede o schimbare de VALOARE/data, dar IGNORA metadata temeiului (verificat_la, nivel_sursa)
    - analog garzii de functie care ignora docstring-ul. Fara asta, restructurarea temeiului ar reseta FALS."""
    vechi = ('from datetime import date\n'
             'COTE = {"salariu_minim": [(date(2025,1,1), 3700, Temei("HG",1006,2024,verificat_la="2026-07-29"))],'
             ' "cas": [(date(2018,1,1), 0.25, None)]}\n')
    valoare = vechi.replace("3700", "4050")
    doar_meta = vechi.replace('verificat_la="2026-07-29"', 'verificat_la="2026-07-31", nivel_sursa="REDARE"')
    alta_cota = vechi.replace("0.25", "0.30")
    assert agenda.cota_valori(vechi, "salariu_minim") != agenda.cota_valori(valoare, "salariu_minim"), \
        "schimbarea VALORII nu se vede -> baza schimbata trece tacut"
    assert agenda.cota_valori(vechi, "salariu_minim") == agenda.cota_valori(doar_meta, "salariu_minim"), \
        "reformatarea temeiului reseteaza FALS (ar trebui ignorata, ca docstring-ul)"
    assert agenda.cota_valori(vechi, "salariu_minim") == agenda.cota_valori(alta_cota, "salariu_minim"), \
        "schimbarea ALTEI cote reseteaza gresit clusterul"
    assert agenda.cota_valori("COTE = {}", "salariu_minim") == "<ABSENT>"


def test_cote_cluster_leaga_deducere_de_salariu_minim():
    """Maparea cluster -> cote (via test -> sursa -> graf): clusterul deducere depinde de salariu_minim."""
    a = agenda.stare_sesiune_a()
    ded = next((r for r in a["rows"] if r["cluster"] == "deducere personala"), None)
    assert ded and "salariu_minim" in agenda.cote_cluster(ded), \
        "graful nu leaga clusterul deducere de salariu_minim (V3 s-ar rupe)"


# RATCHET V3: bife care stau pe o cota schimbata dupa √. Baseline = restantele masurate 02.08.2026:
# 3 bife din 29.07 (suprataxare part-time, proratare angajare/incetare, suprataxare prag) stau pe
# salariu_minim a carui VALOARE 2025 a fost corectata 3700->4050 (FIX5, cf31ddb) DUPA verificarea lor.
# Sunt STALE real - de REVERIFICAT la sursa (decizie Costin; nu reset automat - ramificatie: nu resetez singur).
# Baseline coboara pe masura ce se reverifica; la 0 devine PRAG (orice bifa pe baza schimbata BLOCHEAZA).
STALE_BAZA_BASELINE = 3


def test_bifele_nu_stau_pe_o_baza_schimbata():
    """V3 - resetarea propagata pe dependentele din graf. Ratchet la baseline; o bifa NOUA pe o cota schimbata
    dupa √ ridica numarul peste baseline -> BLOCHEAZA (esecul de temut prevenit)."""
    azi = datetime.date.today()
    a = agenda.stare_sesiune_a()
    stale = []
    for rand in a["rows"]:
        if not rand["verificat"] or "." not in rand["verificat"]:
            continue
        zi, luna = rand["verificat"].split(".")[:2]
        dv = datetime.date(azi.year, int(luna), int(zi))
        for cota in sorted(agenda.cote_cluster(rand)):
            if _cota_schimbata(cota, dv):
                stale.append("'%s' (√ %s) sta pe '%s' schimbata in COTE dupa √ -> reverifica la sursa"
                             % (rand["cluster"], rand["verificat"], cota))
    assert len(stale) <= STALE_BAZA_BASELINE, \
        "BAZA SCHIMBATA SUB O BIFA (peste baseline %d):\n%s" % (STALE_BAZA_BASELINE, "\n".join(stale))
