# -*- coding: utf-8 -*-
"""core/agenda.py - starea REALA a campaniei, derivata din surse PAZITE MECANIC.

Nu tine stare proprie: citeste TESTE.md (Inventar A, Starea sesiunii B, In lucru), test_datorie.py
(datoriile xfail), GARZI.md (Ce lipseste), git log si (optional) pytest/verificator/site. Daca o
informatie nu se poate DERIVA dintr-o sursa, spune "necunoscut" - nu ghiceste, nu tine copie (lectia
DE_FACUT.md). Pazit de core/test_agenda.py: docul care ramane in urma codului pica suita.

  python -m core.agenda        # raport complet (cu starea tehnica: pytest/verificator/site)
"""
import ast
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
                     "verificat": data, "verificat_raw": cel[3], "risc": cel[4].strip().upper(),
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


def _cote_transitive(nume, graf, _vazut=None):
    """Cotele (chei COTE) de care depinde `nume` DIRECT sau prin apeluri (inchidere pe graf)."""
    if _vazut is None:
        _vazut = set()
    if nume in _vazut or nume not in graf:
        return set()
    _vazut.add(nume)
    c = set(graf[nume]["cote"])
    for ap in graf[nume]["apeleaza"]:
        c |= _cote_transitive(ap, graf, _vazut)
    return c


def _functii_apelate_de_test(relpath, func, cunoscute, radacina=None):
    """Numele functiilor-sursa (din `cunoscute`) apelate de functia de test `func` din `relpath`."""
    rad = pathlib.Path(radacina) if radacina else _RAD
    try:
        tree = ast.parse((rad / relpath).read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    # R17: cheile sunt CALIFICATE ("fisier.py::nume"), iar apelul se rezolva prin importurile
    # fisierului de test, nu pe nume simplu. Altfel un test care cheama `salarizare.calcul_salariu`
    # ajungea la orice functie din core/ care se numea la fel.
    from core import graf_temei as _gt
    del tree
    return _gt.apeluri_din(relpath, func, radacina) & cunoscute


def cote_cluster(rand, radacina=None):
    """Cotele (chei COTE) de care depinde un CLUSTER: functiile lui de test -> functiile-sursa apelate ->
    inchiderea pe graf -> cote. Baza resetarii propagate (V3): daca o cota de aici s-a schimbat in COTE dupa
    data √, verificarea clusterului e stale. LIMITA (V2): vede doar dependentele rutate prin cota() - un
    literal hardcodat ramane invizibil (se inchide cu gardul GRI). set() daca nu se poate deriva."""
    from core import graf_temei as _gt
    graf = _gt.construieste_graf(radacina)
    if not rand.get("fisiere") or not rand.get("functie"):
        return set()
    relpath = "core/" + rand["fisiere"][0]
    cunoscute = set(graf)
    cote = set()
    for fn in rand["functie"]:
        for sf in _functii_apelate_de_test(relpath, fn, cunoscute, radacina):
            cote |= _cote_transitive(sf, graf)
    return cote


def cota_valori(src, nume):
    """[(data_in, valoare) dump] pentru COTE[nume] dintr-un text common.py, IGNORAND temeiul (metadata:
    verificat_la/nivel_sursa/url - reformatarea lor NU e o schimbare de baza). '<ABSENT>' daca lipseste,
    None daca src nu se parseaza. Analog _ast_functie (fara docstring), dar pentru o intrare COTE."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "COTE" for t in node.targets) \
           and isinstance(node.value, ast.Dict):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == nume and isinstance(v, ast.List):
                    return [ast.dump(el.elts[0]) + "|" + ast.dump(el.elts[1])
                            for el in v.elts if isinstance(el, ast.Tuple) and len(el.elts) >= 2]
    return "<ABSENT>"


def functii_per_cluster(graf, rows):
    """{cluster: set(functii-sursa atinse de testele lui)}. Extras din `graf_clustere` ca gardul
    proprietatii (`test_graf_clustere_proprietar`) sa masoare ACEEASI multime, nu una paralela."""
    cunoscute = set(graf)
    cf = {}
    for r in rows:
        s = set()
        if r.get("fisiere") and r.get("functie"):
            rel = "core/" + r["fisiere"][0]
            for tf in r["functie"]:
                s |= _functii_apelate_de_test(rel, tf, cunoscute)
        cf[r["cluster"]] = s
    return cf


def proprietari_unici(cf):
    """{functie: {cluster}} pastrand DOAR functiile cu proprietar UNIC (R19, 23.08.2026).

    Docstringul lui `graf_clustere` spunea de la inceput "functie partajata = CO-LOCATIE, nu
    dependenta", dar filtrul aplicat era `if f in own: continue` - adica excludea partajarea CU SINE,
    nu partajarea INTRE ALTII. Un utilitar chemat de testele a cinci clustere era "detinut" de toate
    cinci, iar orice al saselea cluster care il atingea tranzitiv capata cinci muchii.

    MASURAT 23.08.2026: din 154 de functii detinute, 70 erau detinute de 2+ clustere
    (`duk.py::valideaza` de 21). Cu regula asta raman 84 de functii cu proprietar, iar muchiile scad
    de la 960 la 111 - adica noua din zece muchii erau co-locatie, nu dependenta.

    O functie partajata NU primeste un alt proprietar: nu primeste NICIUNUL. Faptul ca testele a doua
    clustere o cheama nu e o dovada ca vreunul dintre ele o detine."""
    owner = {}
    for cl, fns in cf.items():
        for f in fns:
            owner.setdefault(f, set()).add(cl)
    return dict((f, v) for f, v in owner.items() if len(v) == 1)


def graf_clustere():
    """{cluster: set(clustere de care depinde)}. Edge A->B: o functie a lui A (testele -> functii-sursa ->
    inchidere pe graf_temei) atinge o functie DETINUTA de B (verificata de testele lui B), fara ca A s-o
    detina (functie partajata = CO-LOCATIE, nu dependenta). Cele mai multe clustere = radacini (structura/
    declaratii ce depind doar de cote de baza). LIMITA (V2): vede doar prin cota()/apeluri; un literal ascuns
    ramane invizibil."""
    from core import graf_temei as _gt
    graf = _gt.construieste_graf()
    rows = stare_sesiune_a()["rows"]
    cf = functii_per_cluster(graf, rows)

    def _clo(fns):
        seen, st = set(), list(fns)
        while st:
            f = st.pop()
            if f in seen or f not in graf:
                continue
            seen.add(f)
            st += list(graf[f]["apeleaza"])
        return seen

    owner = proprietari_unici(cf)
    edges = {}
    for r in rows:
        A = r["cluster"]
        own = cf[A]
        d = set()
        for f in _clo(own):
            if f in own:
                continue
            for B in owner.get(f, ()):
                if B != A:
                    d.add(B)
        edges[A] = d
    return edges


def _e_blocat(rand):
    """Un cluster e BLOCAT (imposibil de verificat acum: sursa indisponibila, structura neverificata) daca
    poarta marcajul 'BLOCAT:' in coloana Verificat la sursa. Scos din secventa pana se deblocheaza."""
    return "BLOCAT:" in (rand.get("verificat_raw") or "") or "BLOCAT" in str(rand.get("verificat") or "")


def secventa_calculata():
    """Secventa DETERMINISTA de verificare a clusterelor NEBIFATE si NEBLOCATE (1..N), sortare topologica pe
    graf_clustere (un cluster vine dupa dependentele lui) cu departajare FIXA cand mai multe sunt libere:
    (a) FISCAL inainte de STRUCTURA (eroarea ajunge INVIZIBIL la ANAF); (b) cate clustere deblocheaza (desc);
    (c) ordinea din inventar. Intoarce (secventa, neordonabile) - neordonabile = prinse intr-un ciclu (se
    raporteaza, NU se ordoneaza fortat)."""
    edges = graf_clustere()                            # muchii pe NUME (doar familia salarizare are muchii)
    rows = stare_sesiune_a()["rows"]
    # IDENTITATE = (cluster, modul): nume de cluster se repeta intre module (taxare inversa d300/d394,
    # rotunjire aritmetica d112/d300/d390) - cheia pe nume le-ar colapsa si ar pierde din secventa.
    def _id(r):
        return (r["cluster"], r["modul"])
    by = {_id(r): r for r in rows}
    inv = {_id(r): i for i, r in enumerate(rows)}
    deb = {}
    for A, deps in edges.items():
        for B in deps:
            deb[B] = deb.get(B, 0) + 1                  # deblocari pe NUME (destul: doar salarizare are)
    done = {r["cluster"] for r in rows if r["verificat"]}   # dependentele satisfacute, pe NUME
    ramase = [_id(r) for r in rows if not r["verificat"] and not _e_blocat(r)]
    seq = []
    while ramase:
        liber = [k for k in ramase if edges.get(k[0], set()) <= done]
        if not liber:
            break                                       # ce ramane e prins intr-un ciclu
        liber.sort(key=lambda k: (0 if by[k]["risc"].startswith("FISC") else 1, -deb.get(k[0], 0), inv[k]))
        pick = liber[0]
        seq.append(pick)                                # (cluster, modul)
        done.add(pick[0])
        ramase.remove(pick)
    return seq, ramase


def secventa_persistata():
    """Secventa scrisa in TESTE.md (## Secventa de verificare) - [(pozitie, cluster)]. Sursa unica intre
    sesiuni: pozitia 7 de azi = pozitia 7 de maine. [] daca sectiunea lipseste."""
    txt = _text(_TESTE) or ""
    m = re.search(r"## Secven\w+ de verificare[^\n]*\n(.*?)(?=\n## |\Z)", txt, re.DOTALL)
    if not m:
        return []
    out = []
    for ln in m.group(1).splitlines():
        mm = re.match(r"\s*(\d+)\.\s+(.+?)\s*\|\s*(\S.*?)\s*$", ln)
        if mm:
            out.append((int(mm.group(1)), mm.group(2).strip(), mm.group(3).strip()))
    return out


def _violari_topologice(seq_ids, edges):
    """Violari intr-o secventa: un cluster apare INAINTEA unei dependente care e si ea in secventa.
    seq_ids = [(cluster, modul)]; edges = {nume_cluster: set(nume_dependente)}. [] = ordine valida."""
    poz = {}
    for i, (cl, _mod) in enumerate(seq_ids):
        poz.setdefault(cl, i)                          # prima pozitie a numelui
    viol = []
    for i, (cl, _mod) in enumerate(seq_ids):
        for dep in edges.get(cl, set()):
            if dep in poz and poz[dep] > i:
                viol.append("%s (poz %d) inaintea dependentei %s (poz %d)" % (cl, i + 1, dep, poz[dep] + 1))
    return viol


def urmator_cluster():
    """(urmator, ramase, blocate): primul cluster din secventa persistata inca NEBIFAT, cate au ramas de
    verificat, cate sunt BLOCATE. Se recalculeaza dupa fiecare cluster inchis (bifat -> iese din numar)."""
    rows = stare_sesiune_a()["rows"]
    bifat = {(r["cluster"], r["modul"]) for r in rows if r["verificat"]}
    blocate = sum(1 for r in rows if _e_blocat(r))
    urm, ramase = None, 0
    for _p, cl, mod in secventa_persistata():
        if (cl, mod) not in bifat:
            ramase += 1
            if urm is None:
                urm = (cl, mod)
    return urm, ramase, blocate


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
    L += ["", "URMATORUL PAS", "  %s" % urmatorul_pas()]
    try:
        _urm, _ram, _bl = urmator_cluster()
        if _urm:
            L.append("  URMATORUL CLUSTER (din secventa): %s | %s  (raman %d nebifate, %d blocate)"
                     % (_urm[0], _urm[1], _ram, _bl))
    except Exception:
        pass
    L += ["", "DESCHIS ACUM (datoria mecanica)"]
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
