# -*- coding: utf-8 -*-
"""Gard: pasul de restart din ritualul de publicare (scripts/githooks/post-commit) e NECONDITIONAT de continut.

DE CE (11.08.2026): publicarea decidea singura daca restarteaza dupa TIPUL commitului -> un commit de DOCS a
lasat procesul viu pe commitul anterior => RUNNING != HEAD (divergenta prinsa: RUNNING b0ccc40 vs HEAD f504f00).
CLAUDE.md §2.3 pct.10 cere ca dupa ORICE publicare din lant procesul viu sa preia HEAD - fara exceptii, fara
liste de tipuri. Rescrierea PREDARE descria comportamentul, nu-l schimba; clasa ramanea deschisa. Acest gard
CADE daca:
  (a) dispare restartul lui iconta-nou din hook (procesul viu n-ar mai prelua HEAD), SAU
  (b) reapare orice inspectie a CONTINUTULUI commitului in hook (git diff / --name-only / extensii de fisier),
      adica orice mecanism care ar putea conditiona publicarea/restartul pe tipul a ceea ce s-a schimbat.

PIVOT (09.10.2026, comanda Costin pct.2, verbatim in DECIZII): „Daca un commit contine o migrare nerulata pe productie, aplicatia
nu reporneste.” SINGURA conditie admisa e `core.migrari_registru verifica` — pe STAREA productiei (registrul migrarilor, schemele
firmelor fata de sablon), nu pe tipul commitului. Gardul cere acum si ca ea sa existe, inaintea restartului, si sa fie singura.
"""
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(_RAD, "scripts", "githooks", "post-commit")


def _text():
    with open(HOOK, encoding="utf-8") as f:
        return f.read()


def test_hook_publicare_exista():
    assert os.path.exists(HOOK), "scripts/githooks/post-commit lipseste (ritualul de publicare)"


def test_restartul_exista_si_tinteste_iconta_nou():
    t = _text()
    assert re.search(r"systemctl\s+restart\s+iconta-nou\b", t), (
        "post-commit nu restarteaza iconta-nou: procesul viu nu preia HEAD dupa publicare (§2.3 pct.10)")


def test_restartul_e_neconditionat_de_tipul_continutului():
    """Niciun tipar care ar INSPECTA ce s-a schimbat, ca sa decida publicarea/restartul. Se prind mecanismele
    reale de conditionare pe continut, NU simpla mentionare a unui nume de fisier intr-un comentariu:
      - liste de fisiere schimbate: git diff/show --name-only/--stat, diff-tree/diff-index;
      - comparatie cu commitul anterior: HEAD~ / HEAD^;
      - potrivire pe extensie: glob (*.py) sau regex ancorat (\\.py$).
    Reaparitia oricaruia = clasa veche revenita (restart pe tipul commitului)."""
    t = _text()
    INTERZIS = [
        r"--name-only", r"--stat",
        r"\bgit\s+diff\b", r"\bgit\s+show\b", r"diff-tree", r"diff-index",
        r"HEAD~", r"HEAD\^",
        r"\*\.[A-Za-z]",           # glob de extensie: *.py, *.md, *.csv
        r"\\\.[A-Za-z]{2,4}\$",    # regex de extensie ancorat: \.py$ , \.md$
    ]
    gasite = [p for p in INTERZIS if re.search(p, t)]
    assert not gasite, (
        "post-commit inspecteaza tipul continutului ca sa decida publicarea/restartul "
        "(conditionare interzisa pe tip de commit, §2.3 pct.10): %s" % gasite)


def test_singura_conditie_a_restartului_e_verificarea_migrarilor():
    """[09.10.2026] Restartul sta SUB `core.migrari_registru verifica` (altfel codul ar porni peste o migrare nerulata — pățit cu
    d0abd48f: ecranul Casă căzut), iar aceasta e singura conditie: niciun alt `if` nu inconjoara restartul.
    MUTAȚIE: verificarea scoasa din hook -> pica; un al doilea `if` pe restart -> pica."""
    t = _text()
    m = re.search(r'^if .*-m core\.migrari_registru verifica "\$HEAD_SHA".*; then$', t, re.M)   # linia executată, nu comentariul
    i_ver = m.start() if m else -1
    i_rs = t.find("systemctl restart iconta-nou >")
    assert i_ver != -1, "post-commit nu mai verifica migrarile inaintea restartului (comanda Costin 09.10 pct.2)"
    assert i_ver < i_rs, "verificarea migrarilor trebuie sa vina INAINTEA restartului"
    bloc = t[i_ver:i_rs]
    conditii = re.findall(r"^\s*(?:if|elif)\b", bloc, re.M)
    assert re.search(r"^\s*if sudo -n systemctl restart iconta-nou > /tmp/restart_iconta\.log 2>&1; then$", t, re.M), (
        "linia restartului s-a schimbat: o conditie lipita de `sudo` ar conditiona restartul pe altceva decat migrarile")
    assert len(conditii) == 2, ("restartul trebuie sa fie conditionat NUMAI de verificarea migrarilor (+ reusita lui sudo): %s"
                                % conditii)


def test_statica_se_publica_numai_odata_cu_restartul():
    """[10.10.2026, lotul „Retestul plasei”] Cu restartul oprit de o migrare nerulată, post-commit publica totuși statica: JS-ul
    commitului nou ajungea în browser peste backendul vechi (445f9932 servit de procesul pe 60c716d1). Statica se publică NUMAI pe
    ramura în care procesul viu preia același commit — sub verificarea migrărilor, înaintea restartului —, iar rulatorul migrărilor
    o publică înaintea restartului lui. MUTAȚIE: apelul mutat înaintea verificării -> pică; publicarea scoasă din rulator -> pică."""
    t = _text()
    m = re.search(r'^if .*-m core\.migrari_registru verifica "\$HEAD_SHA".*; then$', t, re.M)
    i_rs = t.find("systemctl restart iconta-nou >")
    apeluri = [x.start() for x in re.finditer(r"^\s*publica_statica\b(?!\(\))", t, re.M)]
    assert len(apeluri) == 1 and m and m.start() < apeluri[0] < i_rs, (
        "statica trebuie publicată o singură dată, între verificarea migrărilor și restart: %s" % apeluri)
    directe = [x.start() for x in re.finditer(r"scripts/publica_static\.py >", t)]
    f = t.find("publica_statica() {")
    assert len(directe) == 1 and f < directe[0] < t.find("\n}", f), "publica_static.py chemat în afara funcției publica_statica"
    import inspect
    from core import migrari_registru as mr
    src = inspect.getsource(mr._reporneste_daca_e_cazul)
    apel = re.search(r'subprocess\.run\(\[sys\.executable, os\.path\.join\(RAD, "scripts", "publica_static\.py"\)\]', src)
    assert apel and apel.start() < src.find('"systemctl", "restart"'), (
        "rulatorul migrărilor trebuie să publice statica ÎNAINTEA restartului")
