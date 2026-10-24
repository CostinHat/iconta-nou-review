# -*- coding: utf-8 -*-
"""GARD — pozițiile pilotului sunt legate de scenariul lunii complete, iar starea scrisă e starea testului (lotul 12, comanda 12.1;
CLAUDE.md §2, verbatim: „Pilotul are un scenariu automat al lunii complete a firmei-pilot, parcurs pe ecran ca un contabil, cu cifrele
exacte așteptate la fiecare pas, până la declarații. Scenariul crește cu fiecare poziție pilot rezolvată și rulează permanent în poartă.
Pilotul e atins când scenariul e verde de la cap la coadă.”).

Scenariul: `frontend_test/e2e/e2e_pilot_luna.py` (rulat de plasa porții ca orice `e2e_*.py`). Registrul: secțiunea „Pozițiile pilotului în
scenariu” din `PILOT_CRITERII.md`, un rând pe poziție: `| <ID> | <funcționalitate> | <pașii> | <stare> |`.

CE VERIFICĂ (fiecare punct pică poarta):
  (a) pozițiile sunt EXACT cele 43 din comanda 12.1 + „Primii pași” (`POZITII_PILOT`, lista fixă, verbatim), fiecare o dată, în tabel;
  (b) funcționalitatea din rând e numele din `FUNCTIONALITATI.csv` (coloana „Functionalitate” a ID-ului) — rândul nu derivă de registru;
  (c) pașii scenariului: `test_pilot_<nn>_<pas>`, numerele strict crescătoare în ordinea din fișier (pytest le rulează în ordinea asta,
      iar fiecare pas se sprijină pe cei dinainte), fiecare marcat cu `@pozitii(...)` numai cu ID-uri din (a);
  (d) legătura e aceeași în ambele sensuri: pașii scriși pe rândul poziției P = pașii al căror `@pozitii` cuprinde P; nicio poziție fără pas;
  (e) starea scrisă = starea testelor, în ordinea pașilor: „verde” pentru un pas fără xfail, „xfail (deficiența <nr>)” pentru unul cu
      `xfail(strict=True, reason="deficiența <nr>: …")`; un xfail fără `strict=True`, sau fără numărul deficienței, pică;
  (f) numărul din xfail e în `DEFICIENTE.md` și NU e „rezolvată” (o deficiență rezolvată nu mai poate ține un pas al pilotului în xfail;
      cu `strict=True`, pasul ar pica oricum ca XPASS);
  (g) niciun pas nu se oprește altfel: fără `skip` / `skipif`, fără `pytest.skip` / `pytest.xfail` în corp, fără `pytestmark`.

LIMITĂ DECLARATĂ: garda vede legătura și starea DECLARATĂ (xfail sau nu), nu rezultatul rulării: dacă un pas „verde” pică, îl prinde plasa
porții (rularea e2e), nu garda. Că pasul reface ce face contabilul se judecă la scrierea lui (docstringul numește pașii) și prin mutație
(`mut_lot12_pilot.json`).
"""
import ast
import csv
import io
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIU = "frontend_test/e2e/e2e_pilot_luna.py"
CRITERII = "PILOT_CRITERII.md"
#: comanda 12.1, verbatim: „Pozițiile pilotului: F018, F023, F025, F045, F046, F070, F126, F131, F172, F017, F003, F252, F254, F043, F176,
#: F179, F089, F139, F011, F012, F073, F015, F078, F080, F087, F122, F134, F019, F054, F061, F118, F022, F081, F162, F169, F026, F028,
#: F031, F034, F035, F084, F085, F183 și fereastra de bun venit („Primii pași”).”
POZITII_PILOT = ("F018", "F023", "F025", "F045", "F046", "F070", "F126", "F131", "F172", "F017", "F003", "F252", "F254", "F043", "F176",
                 "F179", "F089", "F139", "F011", "F012", "F073", "F015", "F078", "F080", "F087", "F122", "F134", "F019", "F054", "F061",
                 "F118", "F022", "F081", "F162", "F169", "F026", "F028", "F031", "F034", "F035", "F084", "F085", "F183", "PRIMII_PASI")
NUME_PRIMII_PASI = "Fereastra de bun venit „Primii pași”"
_RAND = re.compile(r"^\| (F\d{3}|PRIMII_PASI) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|\s*$")
_XFAIL_MOTIV = re.compile(r"^deficiența (\d+|C\d+): \S")


def _citeste(cale, surse=None):
    if surse is not None and cale in surse:
        return surse[cale]
    p = os.path.join(_RAD, cale)
    return io.open(p, encoding="utf-8").read() if os.path.isfile(p) else None


def pasi(text):
    """PURĂ. [{nume, nr, pozitii, xfail: (strict, motiv) | None, opriri: [...]}] — pașii scenariului, în ordinea din fișier."""
    out = []
    for n in ast.parse(text).body:
        if not isinstance(n, ast.FunctionDef) or not n.name.startswith("test_"):
            continue
        p = {"nume": n.name, "nr": None, "pozitii": None, "xfail": None, "opriri": []}
        m = re.match(r"^test_pilot_(\d{2})_[a-z0-9_]+$", n.name)
        p["nr"] = int(m.group(1)) if m else None
        for d in n.decorator_list:
            f = d.func if isinstance(d, ast.Call) else d
            nume = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if nume == "pozitii" and isinstance(d, ast.Call):
                p["pozitii"] = tuple(a.value for a in d.args if isinstance(a, ast.Constant))
            elif nume == "xfail":
                kw = {k.arg: k.value for k in getattr(d, "keywords", [])}
                strict = isinstance(kw.get("strict"), ast.Constant) and kw["strict"].value is True
                motiv = kw.get("reason")
                p["xfail"] = (strict, motiv.value if isinstance(motiv, ast.Constant) else None)
            elif nume in ("skip", "skipif"):
                p["opriri"].append("decoratorul %s" % nume)
        for c in ast.walk(n):
            if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr in ("skip", "xfail", "importorskip")
                    and isinstance(c.func.value, ast.Name) and c.func.value.id == "pytest"):
                p["opriri"].append("pytest.%s în corp (linia %d)" % (c.func.attr, c.lineno))
        out.append(p)
    return out


def _pytestmark(text):
    return [n.lineno for n in ast.parse(text).body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in n.targets)]


def stare_pas(p):
    """„verde” / „xfail (deficiența <nr>)” — starea declarată a pasului."""
    if not p["xfail"]:
        return "verde"
    m = _XFAIL_MOTIV.match(p["xfail"][1] or "")
    return "xfail (deficiența %s)" % (m.group(1) if m else "?")


def randuri(text):
    """PURĂ. {poziție: (funcționalitate, [pași], stare)} din secțiunea pozițiilor a lui PILOT_CRITERII.md (+ dublurile, ca listă)."""
    out, dubluri = {}, []
    for ln in text.splitlines():
        m = _RAND.match(ln)
        if not m:
            continue
        poz = m.group(1)
        if poz in out:
            dubluri.append(poz)
        out[poz] = (m.group(2).strip(), re.findall(r"`(test_pilot_\d{2}_[a-z0-9_]+)`", m.group(3)), m.group(4).strip())
    return out, dubluri


def nume_functionalitati(text_csv):
    return {(r.get("ID") or "").strip(): (r.get("Functionalitate") or "").strip() for r in csv.DictReader(io.StringIO(text_csv))}


def probleme(surse=None, numere=None, pozitii_pilot=POZITII_PILOT):
    """Toate abaterile (listă goală = scenariul și registrul sunt legate și la zi)."""
    rele = []
    text = _citeste(SCENARIU, surse)
    if text is None:
        return ["scenariul %s lipsește" % SCENARIU]
    ps = pasi(text)
    if not ps:
        rele.append("scenariul n-are niciun pas")
    for ln in _pytestmark(text):
        rele.append("scenariul are `pytestmark` (linia %d): pașii nu se opresc la nivelul modulului" % ln)
    nr_ant = -1
    for p in ps:
        if p["nr"] is None:
            rele.append("%s: un pas se numește `test_pilot_<nn>_<pas>`" % p["nume"])
            continue
        if p["nr"] <= nr_ant:
            rele.append("%s: numărul %02d nu crește față de pasul de dinainte (%02d)" % (p["nume"], p["nr"], nr_ant))
        nr_ant = p["nr"]
        if not p["pozitii"]:
            rele.append("%s: fără `@pozitii(...)`" % p["nume"])
        for x in p["pozitii"] or ():
            if x not in pozitii_pilot:
                rele.append("%s: poziția %r nu e a pilotului" % (p["nume"], x))
        rele += ["%s: %s" % (p["nume"], o) for o in p["opriri"]]
        if p["xfail"]:
            strict, motiv = p["xfail"]
            if not strict:
                rele.append("%s: xfail fără strict=True (un pas reparat ar trece neobservat)" % p["nume"])
            m = _XFAIL_MOTIV.match(motiv or "")
            if not m:
                rele.append("%s: motivul xfail începe cu „deficiența <nr>: …” (%r)" % (p["nume"], motiv))
            elif numere is not None:
                nr = m.group(1)
                if nr not in numere:
                    rele.append("%s: deficiența %s nu e în DEFICIENTE.md" % (p["nume"], nr))
                elif numere[nr] == "rezolvată":
                    rele.append("%s: deficiența %s e „rezolvată” în DEFICIENTE.md, deci pasul nu mai e xfail" % (p["nume"], nr))
    tabel, dubluri = randuri(_citeste(CRITERII, surse) or "")
    rele += ["%s: rândul apare de două ori în %s" % (d, CRITERII) for d in dubluri]
    lipsa = [x for x in pozitii_pilot if x not in tabel]
    if lipsa:
        rele.append("pozițiile pilotului lipsesc din %s: %s" % (CRITERII, lipsa))
    rele += ["%s: nu e o poziție a pilotului (comanda 12.1), dar e în %s" % (x, CRITERII) for x in tabel if x not in pozitii_pilot]
    nume = nume_functionalitati(_citeste("FUNCTIONALITATI.csv", surse) or "")
    dupa_nume = {p["nume"]: p for p in ps}
    for poz in pozitii_pilot:
        if poz not in tabel:
            continue
        functionalitate, scrise, stare = tabel[poz]
        corect = NUME_PRIMII_PASI if poz == "PRIMII_PASI" else nume.get(poz)
        if functionalitate != corect:
            rele.append("%s: funcționalitatea %r, în FUNCTIONALITATI.csv %r" % (poz, functionalitate, corect))
        reali = [p["nume"] for p in ps if poz in (p["pozitii"] or ())]
        if not reali:
            rele.append("%s: niciun pas al scenariului nu o acoperă" % poz)
        if scrise != reali:
            rele.append("%s: pașii scriși %s, pașii marcați în scenariu %s" % (poz, scrise, reali))
        asteptat = "; ".join(stare_pas(dupa_nume[x]) for x in reali)
        if stare != asteptat:
            rele.append("%s: starea scrisă %r, starea pașilor %r" % (poz, stare, asteptat))
    return rele


def _numere_deficiente():
    from core.test_deficiente import randuri as randuri_def
    return {r["nr"]: r["stare"] for r in randuri_def()}


def test_pozitiile_pilotului_sunt_legate_de_scenariu_si_starea_e_a_testelor():
    """(a)–(g). MUTAȚII (autoprobele de mai jos): o poziție scoasă din tabel / un pas fără `@pozitii` / o stare „verde” pe un pas xfail /
    un xfail fără strict / pași în altă ordine -> ROȘU."""
    rele = probleme(numere=_numere_deficiente())
    assert not rele, "\n".join(rele)
    assert len(pasi(_citeste(SCENARIU))) >= len(POZITII_PILOT) // 2, "anti-vacuu: scenariul are prea puțini pași"


# ── autoprobele gărzii (mutațiile ei, permanente) ────────────────────────────────────────────────────────────────────────────────
_CSV = "Functionalitate,Descriere,ID,Stare\nParteneri,x,F018,LIVE\nCote,x,F023,LIVE\n"
_SCEN = ('@pozitii("F018")\ndef test_pilot_01_a(patron):\n    pass\n\n\n'
         '@pozitii("F023", "F018")\n@pytest.mark.xfail(strict=True, reason="deficiența 461: lipsește lista")\ndef test_pilot_02_b(patron):\n'
         '    pass\n')
_TAB = ("| F018 | Parteneri | `test_pilot_01_a`, `test_pilot_02_b` | verde; xfail (deficiența 461) |\n"
        "| F023 | Cote | `test_pilot_02_b` | xfail (deficiența 461) |\n")


def _sursa(scen=_SCEN, tab=_TAB):
    return {SCENARIU: scen, CRITERII: tab, "FUNCTIONALITATI.csv": _CSV}


def test_garda_trece_pe_un_scenariu_legat():
    assert probleme(_sursa(), {"461": "neverificat"}, ("F018", "F023")) == []


def test_garda_prinde_legatura_rupta():
    poz, num = ("F018", "F023"), {"461": "neverificat"}
    cazuri = {
        "poziție scoasă din tabel": _sursa(tab=_TAB.splitlines()[0] + "\n"),
        "pas fără @pozitii": _sursa(scen=_SCEN.replace('@pozitii("F018")\n', "", 1)),
        "stare verde pe un pas xfail": _sursa(tab=_TAB.replace("| xfail (deficiența 461) |", "| verde |")),
        "xfail fără strict": _sursa(scen=_SCEN.replace("strict=True, ", "")),
        "xfail fără numărul deficienței": _sursa(scen=_SCEN.replace("deficiența 461: lipsește lista", "lipsește lista")),
        "pași în altă ordine": _sursa(scen=_SCEN.replace("test_pilot_02_b", "test_pilot_00_b")),
        "pas scris în tabel, nemarcat": _sursa(tab=_TAB.replace("| `test_pilot_02_b` |", "| `test_pilot_01_a`, `test_pilot_02_b` |")),
        "funcționalitate greșită": _sursa(tab=_TAB.replace("| Cote |", "| Cotele TVA |")),
        "pytest.skip în corp": _sursa(scen=_SCEN.replace("def test_pilot_01_a(patron):\n    pass", "def test_pilot_01_a(patron):\n"
                                                         "    pytest.skip('x')")),
        "poziție străină pe pas": _sursa(scen=_SCEN.replace('@pozitii("F018")', '@pozitii("F999")')),
    }
    for caz, s in cazuri.items():
        assert probleme(s, num, poz), "garda n-a prins: %s" % caz
    assert probleme(_sursa(), {"461": "rezolvată"}, poz) == [
        "test_pilot_02_b: deficiența 461 e „rezolvată” în DEFICIENTE.md, deci pasul nu mai e xfail"]
    assert probleme(_sursa(), {}, poz) == ["test_pilot_02_b: deficiența 461 nu e în DEFICIENTE.md"]
