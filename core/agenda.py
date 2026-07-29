# -*- coding: utf-8 -*-
"""core/agenda.py - starea REALA a campaniei, derivata din surse PAZITE MECANIC.

Nu tine stare proprie: citeste TESTE.md (Inventar A, Starea sesiunii B, In lucru), test_datorie.py
(datoriile xfail), GARZI.md (Ce lipseste), git log si (optional) pytest/verificator/site. Daca o
informatie nu se poate DERIVA dintr-o sursa, spune "necunoscut" - nu ghiceste, nu tine copie (lectia
DE_FACUT.md). Pazit de core/test_agenda.py: docul care ramane in urma codului pica suita.

  python -m core.agenda        # raport complet (cu starea tehnica: pytest/verificator/site)
"""
import re
import subprocess
import datetime
import pathlib

_RAD = pathlib.Path(__file__).resolve().parent.parent
_TESTE = _RAD / "TESTE.md"
_GARZI = _RAD / "GARZI.md"
_DATORIE = _RAD / "core" / "test_datorie.py"
_VERIF = "√"   # √


def _text(f):
    try:
        return f.read_text(encoding="utf-8")
    except Exception:
        return None


def _randuri_tabel(text, titlu):
    """Randurile (liste de celule) ale PRIMULUI tabel de dupa `titlu`. [] daca lipseste."""
    if not text or titlu not in text:
        return []
    dupa = text[text.index(titlu) + len(titlu):]
    randuri = []
    for ln in dupa.splitlines():
        t = ln.strip()
        if t.startswith("|"):
            cel = [c.strip() for c in t.strip("|").split("|")]
            if set("".join(cel)) <= set("-: "):   # linia separator
                continue
            randuri.append(cel)
        elif randuri:
            break
    return randuri


def stare_sesiune_a():
    """(verificate, total, randuri). Rand: {modul, fisiere, verificat, temeiuri}."""
    r = _randuri_tabel(_text(_TESTE), "## Inventarul de acoperit în A")
    if not r:
        return None
    r = r[1:]
    out = []
    for cel in r:
        if len(cel) < 3:
            continue
        data = None
        if _VERIF in cel[2]:
            m = re.search(r"\d{1,2}\.\d{1,2}", cel[2])
            data = m.group(0) if m else "?"
        out.append({"modul": cel[0], "fisiere": re.findall(r"test_\w+\.py", cel[1]),
                    "verificat": data, "temeiuri": cel[3] if len(cel) > 3 else ""})
    return sum(1 for x in out if x["verificat"]), len(out), out


def stare_sesiune_b():
    txt = _text(_TESTE)
    faze = _randuri_tabel(txt, "## Starea sesiunii B")
    if not faze:
        return None
    faze = faze[1:]
    faza = "necunoscut"
    for cel in faze:
        if len(cel) >= 2 and "închis" not in cel[1].lower() and "gata" not in cel[1].lower():
            faza = cel[0].split("—")[0].strip()
            break
    dupa = txt[txt.index("## Starea sesiunii B"):] if (txt and "## Starea sesiunii B" in txt) else ""
    et = _randuri_tabel(dupa, "| Etapă | Stare |")  # ancora = antetul, deci randurile sunt deja datele
    facute = sum(1 for c in et if len(c) > 1 and _VERIF in c[1])
    return {"faza": faza, "etape_facute": facute, "etape_total": len(et)}


def urmatorul_pas():
    txt = _text(_TESTE) or ""
    m = re.search(r"^- urmator:\s*(.+)$", txt, re.MULTILINE)
    if m:
        return m.group(1).strip()
    a = stare_sesiune_a()
    if a:
        neverif = [x["modul"] for x in a[2] if not x["verificat"]]
        if neverif:
            return "Sesiunea A: verifica la sursa modulul %s (primul neverificat)" % neverif[0]
        return "Sesiunea A completa - incepe Sesiunea B (Faza 1, firmele F1-F7)"
    return "necunoscut"


def datorii_deschise():
    """[(nume_test, motiv)] din xfail-urile din test_datorie.py. Motivele folosesc ghilimele duble."""
    txt = _text(_DATORIE)
    if txt is None:
        return None
    out = []
    for m in re.finditer(r'@pytest\.mark\.xfail\(.*?reason=\(?\s*"([^"]+)"', txt, re.DOTALL):
        motiv = re.sub(r"\s+", " ", m.group(1)).strip()
        dm = re.search(r"def (test_\w+)\(", txt[m.end():])
        nume = dm.group(1) if dm else "?"
        out.append((nume, motiv[:110] + ("…" if len(motiv) > 110 else "")))
    return out


def garduri_lipsa():
    r = _text(_GARZI)
    if not r or "## Ce lipsește" not in r:
        return None
    dupa = r[r.index("## Ce lipsește"):]
    out = []
    for ln in dupa.splitlines()[1:]:
        t = ln.strip()
        if t.startswith("## "):
            break
        m = re.match(r"\d+\.\s+\*\*(.+?)\*\*", t)
        if m:
            out.append(m.group(1).strip())
    return out


def ultim_commit():
    try:
        return subprocess.run(["git", "-C", str(_RAD), "log", "--oneline", "-1"],
                              capture_output=True, text=True, timeout=10).stdout.strip() or "necunoscut"
    except Exception:
        return "necunoscut"


def stare_tehnica():
    """(pytest, verificator, site) - HEAVY. Doar CLI."""
    import os
    venv = str(_RAD / "venv" / "bin" / "python3")
    py = venv if os.path.exists(venv) else "python3"
    ps = vs = ss = "necunoscut"
    try:
        r = subprocess.run([py, "-m", "pytest", "core/", "-q", "-p", "no:cacheprovider"],
                           cwd=str(_RAD), capture_output=True, text=True, timeout=180)
        m = re.search(r"(\d+ passed[^\n]*)", r.stdout)
        ps = m.group(1) if m else "necunoscut"
    except Exception:
        pass
    try:
        r = subprocess.run([py, "verificator_conformitate.py"], cwd=str(_RAD),
                           capture_output=True, text=True, timeout=60)
        m = re.search(r"TOTAL:\s*(\d+)", r.stdout)
        vs = m.group(1) if m else "necunoscut"
    except Exception:
        pass
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                            "http://127.0.0.1:8010/"], capture_output=True, text=True, timeout=10)
        ss = r.stdout.strip() or "necunoscut"
    except Exception:
        pass
    return ps, vs, ss


def raport(tehnic=True):
    L = ["═══ AGENDA iConta ═══  (%s)" % datetime.date.today().isoformat(), ""]
    L.append("UNDE SUNTEM")
    a = stare_sesiune_a()
    L.append("  Sesiunea A (aliniere la legislatie):  %s" %
             ("%d din %d module verificate la sursa" % (a[0], a[1]) if a else "necunoscut (Inventar lipseste)"))
    b = stare_sesiune_b()
    L.append("  Sesiunea B (testare pe flux):         %s" %
             ("%s, etape %d/%d" % (b["faza"], b["etape_facute"], b["etape_total"]) if b else "necunoscut"))
    L.append("  Ultimul commit: %s" % ultim_commit())
    L += ["", "URMATORUL PAS", "  %s" % urmatorul_pas(), "", "DESCHIS ACUM (datoria mecanica)"]
    d = datorii_deschise()
    if d is None:
        L.append("  necunoscut (test_datorie.py necitibil)")
    elif not d:
        L.append("  (nicio datorie xfail)")
    else:
        L += ["  · %s - %s" % (n, mo) for n, mo in d]
    L += ["", "GARDURI LIPSA"]
    g = garduri_lipsa()
    L += (["  necunoscut"] if g is None else ["  · %s" % x for x in g])
    L += ["", "STARE TEHNICA"]
    if tehnic:
        ps, vs, ss = stare_tehnica()
        L.append("  teste: %s | verificator: %s | site: HTTP %s" % (ps, vs, ss))
    else:
        L.append("  (ruleaza: python -m core.agenda)")
    return "\n".join(L)


if __name__ == "__main__":
    print(raport(tehnic=True))
