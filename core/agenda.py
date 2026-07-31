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

# Suita pentru STARE TEHNICA: rulata din _RAD, FARA filtru de cale, ca sa numere EXACT ce
# numara `pytest -q` de la radacina (core/ + testele de la radacina), nu doar core/. Un scope
# mai ingust face STARE TEHNICA sa afiseze un numar fals (bug 30.07.2026: core/ 759 vs 1082).
# Pazit de core/test_agenda.py::test_stare_tehnica_numara_toata_suita.
PYTEST_ARGS = ["-q", "-p", "no:cacheprovider"]


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


def inventar_verificat_raw(text):
    """{cluster: celula 'Verificat la sursă' bruta} din Inventarul A al unui text TESTE.md
    (orice versiune, inclusiv din `git show`). Bruta = cu tot ce urmeaza dupa data √ (motivul
    de bump). Sursa unica de parsare a coloanei bifei; folosita si de garda de bump din test_agenda."""
    out = {}
    for cel in _randuri_tabel(text, "## Inventarul de acoperit în A"):
        if len(cel) > 3 and cel[0] and not cel[0].lower().startswith("cluster"):
            out[cel[0]] = cel[3]
    return out


def stare_sesiune_a():
    """{rows, fiscal:(verif,total), structura:(verif,total)} - per CLUSTER (30.07), cu risc.
    Rand: {cluster, modul, fisiere, verificat, risc, temeiuri}."""
    r = _randuri_tabel(_text(_TESTE), "## Inventarul de acoperit în A")
    if not r:
        return None
    rows = []
    for cel in r[1:]:
        if len(cel) < 5:
            continue
        data = None
        if _VERIF in cel[3]:
            m = re.search(r"\d{1,2}\.\d{1,2}", cel[3])
            data = m.group(0) if m else "?"
        rows.append({"cluster": cel[0], "modul": cel[1],
                     "fisiere": re.findall(r"test_\w+\.py", cel[2]),
                     "verificat": data, "risc": cel[4].strip().upper(),
                     "temeiuri": cel[5] if len(cel) > 5 else "",
                     "functie": re.findall(r"test_\w+", cel[6]) if len(cel) > 6 else []})
    fisc = [x for x in rows if x["risc"].startswith("FISC")]
    stru = [x for x in rows if x["risc"].startswith("STRUC")]
    return {"rows": rows,
            "fiscal": (sum(1 for x in fisc if x["verificat"]), len(fisc)),
            "structura": (sum(1 for x in stru if x["verificat"]), len(stru))}


def stare_sesiune_b():
    txt = _text(_TESTE)
    faze = _randuri_tabel(txt, "## Starea sesiunii B")
    if not faze:
        return None
    faze = faze[1:]
    faza = "necunoscut"
    stare_faza = ""
    for cel in faze:
        if len(cel) >= 2 and "închis" not in cel[1].lower() and "gata" not in cel[1].lower():
            faza = cel[0].split("—")[0].strip()
            stare_faza = cel[1].strip()
            break
    dupa = txt[txt.index("## Starea sesiunii B"):] if (txt and "## Starea sesiunii B" in txt) else ""
    et = _randuri_tabel(dupa, "| Etapă | Stare |")  # ancora = antetul, deci randurile sunt deja datele
    facute = sum(1 for c in et if len(c) > 1 and _VERIF in c[1])
    return {"faza": faza, "stare": stare_faza, "etape_facute": facute, "etape_total": len(et)}


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
    """DERIVAT din categoriile GARZI marcate cu bullet-uri `- LIPSĂ:` (sursa unica; NU o lista de
    mana care se desincronizeaza). Fiecare categorie -> {categorie, risc (Esec), lipsuri:[...]}.
    Riscul e ce lasa deschis gardul absent - ca cine citeste agenda sa stie ce e in joc."""
    r = _text(_GARZI)
    if not r:
        return None
    out, cat, esec, lipsuri, in_esec = [], None, [], [], False

    def _flush():
        if cat and lipsuri:
            out.append({"categorie": cat, "risc": " ".join(esec).strip(), "lipsuri": list(lipsuri)})

    for ln in r.splitlines():
        s = ln.strip()
        m = re.match(r"###\s+\d+\.\s+(.+)", s)
        if m:
            _flush()
            cat, esec, lipsuri, in_esec = m.group(1).strip(), [], [], False
            continue
        if cat is None:
            continue
        me = re.match(r"\*\*E[sș]ec:\*\*\s*(.*)", s)
        if me:
            in_esec, esec = True, [me.group(1).strip()]
            continue
        if in_esec:
            if s == "" or s.startswith("**") or s.startswith("- ") or s.startswith("#"):
                in_esec = False
            else:
                esec.append(s)
        if re.match(r"- LIPS[ĂA]:", s):
            lipsuri.append(re.sub(r"^- LIPS[ĂA]:\s*", "", s))
    _flush()
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
        r = subprocess.run([py, "-m", "pytest", *PYTEST_ARGS],
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
    if a:
        fv, ft = a["fiscal"]
        sv, st = a["structura"]
        _sa = "%d/%d clustere FISCALE (risc invizibil) \u00b7 %d/%d structura verificate la sursa" % (fv, ft, sv, st)
    else:
        _sa = "necunoscut (Inventar lipseste)"
    L.append("  Sesiunea A (aliniere la legislatie):  %s" % _sa)
    b = stare_sesiune_b()
    L.append("  Sesiunea B (testare pe flux):         %s" %
             ("%s (%s), etape %d/%d" % (b["faza"], b["stare"], b["etape_facute"], b["etape_total"]) if b else "necunoscut"))
    L.append("  Ultimul commit: %s" % ultim_commit())
    L += ["", "URMATORUL PAS", "  %s" % urmatorul_pas(), "", "DESCHIS ACUM (datoria mecanica)"]
    d = datorii_deschise()
    if d is None:
        L.append("  necunoscut (test_datorie.py necitibil)")
    elif not d:
        L.append("  (nicio datorie xfail)")
    else:
        L += ["  · %s - %s" % (n, mo) for n, mo in d]
    L += ["", "GARDURI LIPSA (derivat din categoriile GARZI marcate LIPSĂ)"]
    g = garduri_lipsa()
    if g is None:
        L.append("  necunoscut")
    elif not g:
        L.append("  (nicio categorie cu LIPSĂ)")
    else:
        for c in g:
            risc = (" — risc: " + c["risc"][:110]) if c["risc"] else ""
            L.append("  · %s%s" % (c["categorie"], risc))
            for lp in c["lipsuri"]:
                L.append("      - %s" % lp[:110])
    L += ["", "STARE TEHNICA"]
    if tehnic:
        ps, vs, ss = stare_tehnica()
        L.append("  teste: %s | verificator: %s | site: HTTP %s" % (ps, vs, ss))
    else:
        L.append("  (ruleaza: python -m core.agenda)")
    return "\n".join(L)


if __name__ == "__main__":
    print(raport(tehnic=True))
