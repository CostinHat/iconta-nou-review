# -*- coding: utf-8 -*-
"""scripts/scan_sonde_stare.py — SONDELE CARE MĂSOARĂ FĂRĂ SĂ ȘTIE DACĂ CEREREA A REUȘIT.

**Clasa, în cuvintele defectului care a produs-o.** Pe 10.09.2026, martorul sincron al bancului P5
a măsurat 40 de cereri care cădeau cu `UndefinedTable`. Nimic n-a semnalat: funcția de curbă
înregistra **duratele**, nu și **statusurile**. *O durată există și pe 500.* Sonda își raporta
cifra fără să poată spune despre ce ramură vorbește.

**Criteriul e STRUCTURAL, nu textual** (METODA §23). Nu caut cuvântul „status" în cod — l-aș găsi
și acolo unde e vorba de statusul altcuiva (bancul meu chiar avea `c.erori`, dar erau erorile
canarului, nu ale rutei măsurate; un criteriu pe nume l-ar fi declarat curat). Caut **poziția**:

  1. **SONDA** — o funcție care face o cerere HTTP și pune rezultatul la dispoziția apelantului
     sub forma unui TUPLU în care una din poziții vine din `.status_code`. Poziția aia se reține.
  2. **AGREGATORUL** — o funcție care cheamă sonda și adună o cifră din rezultatul ei.
  3. **DEFECTUL** — agregatorul citește din tuplu alte poziții (durata), dar **poziția stării nu e
     citită niciodată**: nici prin index, nici prin despachetare într-un nume folosit.

**CE NU VEDE, declarat:**
  * sonde care întorc un DICT, nu un tuplu — poziția n-are ce să însemne acolo;
  * sonde din alt modul decât agregatorul (rezolvarea e per fișier, deliberat: altfel ar trebui un
    graf de apeluri, iar clasa asta e despre o pereche care stă la doi pași unul de altul);
  * un agregator care verifică starea **indirect**, chemând o a treia funcție care o asertează;
  * cazul în care starea e citită, dar nu se face nimic cu ea. *Instrumentul măsoară dacă poziția e
    ATINSĂ, nu dacă e judecată* — deci cifra e un **plafon INFERIOR**.

Rulare:  `./venv/bin/python scripts/scan_sonde_stare.py`
         `./venv/bin/python scripts/scan_sonde_stare.py --calibrare`
         `./venv/bin/python scripts/scan_sonde_stare.py --esantion 30`
"""
import ast
import glob
import io
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: DOMENIUL, declarat: fișierele de sondă. Un instrument fără domeniu scris măsoară „ce-am găsit".
TIPARE = ("scripts/masoara_*.py", "scripts/proba_*.py")

#: numele prin care se recunoaște o cerere HTTP
HTTP = {"get", "post", "put", "delete", "patch", "request", "head", "options"}
MODULE_HTTP = {"httpx", "requests", "client", "cl", "sesiune"}

#: numele prin care se recunoaște că se adună o cifră
AGREGARE = {"append", "median", "mean", "quantiles", "fmean", "extend"}


def fisiere(rad=None):
    rad = rad or RAD
    out = []
    for t in TIPARE:
        out += sorted(glob.glob(os.path.join(rad, t)))
    return out


def _e_status(nod):
    """`True` dacă expresia vine din `.status_code` — direct sau printr-un `str(...)` peste el."""
    if isinstance(nod, ast.Attribute) and nod.attr == "status_code":
        return True
    if isinstance(nod, ast.Call):
        return any(_e_status(a) for a in nod.args)
    return False


def _cere_http(nod):
    """`True` dacă nodul e un apel HTTP."""
    if not isinstance(nod, ast.Call):
        return False
    f = nod.func
    if isinstance(f, ast.Attribute) and f.attr in HTTP:
        baza = f.value
        nume = baza.id if isinstance(baza, ast.Name) else (
            baza.attr if isinstance(baza, ast.Attribute) else "")
        return nume in MODULE_HTTP or nume.startswith("cl")
    return False


def sonde(arbore):
    """`{nume: pozitia_starii}` — funcțiile care fac o cerere și oferă starea pe o poziție."""
    out = {}
    for n in ast.walk(arbore):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(_cere_http(c) for c in ast.walk(n)):
            continue
        # numele locale legate de `.status_code`
        din_status = set()
        for a in ast.walk(n):
            if isinstance(a, ast.Assign) and _e_status(a.value):
                for t in a.targets:
                    if isinstance(t, ast.Name):
                        din_status.add(t.id)
            if isinstance(a, ast.Assign) and isinstance(a.value, ast.Attribute):
                if a.value.attr == "status_code":
                    for t in a.targets:
                        if isinstance(t, ast.Name):
                            din_status.add(t.id)
                    if any(isinstance(t, ast.Subscript) for t in a.targets):
                        pass                   # forma cu dict se prinde mai jos
        # DICT: `d["status"] = r.status_code`, iar `d` ajunge la apelant
        for a in ast.walk(n):
            if not (isinstance(a, ast.Assign) and _e_status(a.value)):
                continue
            for t in a.targets:
                if (isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant)
                        and isinstance(t.slice.value, str)):
                    out[n.name] = t.slice.value
                    break
        # tuplul oferit apelantului: `return (...)` sau `rezultat[i] = (...)`
        for a in ast.walk(n):
            tup = None
            if isinstance(a, ast.Return) and isinstance(a.value, ast.Tuple):
                tup = a.value
            elif isinstance(a, ast.Assign) and isinstance(a.value, ast.Tuple):
                if any(isinstance(t, ast.Subscript) for t in a.targets):
                    tup = a.value
            if tup is None:
                continue
            for i, el in enumerate(tup.elts):
                if _e_status(el) or (isinstance(el, ast.Name) and el.id in din_status):
                    out[n.name] = i
                    break
    return out


def _nume_din_apel(nod):
    if isinstance(nod, ast.Call):
        if isinstance(nod.func, ast.Name):
            return nod.func.id
        if isinstance(nod.func, ast.Attribute):
            return nod.func.attr
    return None


def _pozitii_citite(fn, prin_param, direct):
    """Indicii CITIȚI din tuplul sondei, plus numele legate prin despachetare.

    **Cele două niveluri de indexare nu se adună, și asta a fost un bug al instrumentului**, prins
    de calibrare înainte de prima cifră. La tiparul cu parametru de ieșire, `rez[slot][poz]`,
    indicele dinăuntru alege SLOTUL din lista pe care scrie sonda, iar cel din afară e poziția în
    tuplu. Prima formă le lua pe amândouă, deci orice `rez[0][...]` părea să citească poziția 0 —
    chiar starea — și toți agregatorii ieșeau curați, inclusiv cei construiți să nu fie.
    """
    indici, despachetate = set(), []
    for a in ast.walk(fn):
        if isinstance(a, ast.Subscript) and isinstance(a.slice, ast.Constant):
            baza = a.value
            # `X[slot][poz]` — purtător prin parametru de ieșire: contează indicele DIN AFARĂ
            if (isinstance(baza, ast.Subscript) and isinstance(baza.value, ast.Name)
                    and baza.value.id in prin_param):
                indici.add(a.slice.value)
            # `X[poz]` — purtător direct: singurul indice E poziția
            elif isinstance(baza, ast.Name) and baza.id in direct:
                indici.add(a.slice.value)
        # `a, b, c = X[slot]`  ·  `a, b, c = X`  ·  `a, b, c = f(...)`
        if isinstance(a, ast.Assign) and len(a.targets) == 1:
            t = a.targets[0]
            if isinstance(t, (ast.Tuple, ast.List)):
                v, purtator = a.value, False
                if isinstance(v, ast.Subscript) and isinstance(v.value, ast.Name):
                    purtator = v.value.id in prin_param
                elif isinstance(v, ast.Name):
                    purtator = v.id in direct
                if purtator:
                    despachetate.append([e.id if isinstance(e, ast.Name) else None
                                         for e in t.elts])
    return indici, despachetate


def _scapa(fn, apelate, prin_param, direct):
    """`True` dacă rezultatul sondei supraviețuiește apelului — prin `return` sau printr-un container.

    E deosebirea dintre «a aruncat starea» și «n-a judecat-o». Un dicționar pus într-un `out` care
    se întoarce ajunge în artefact, deci se poate confrunta oricând mai târziu; o durată extrasă
    dintr-un tuplu care moare la sfârșitul buclei nu se mai poate confrunta niciodată.
    """
    def e_intregul(nod):
        """`True` doar dacă nodul E rezultatul sondei — nu o bucată extrasă din el.

        `sonda(...)` da · `v` (purtător) da · `sonda(...)["ms"]` **nu** · `rez[0][1]` **nu**.
        Deosebirea asta e tot criteriul: ce se adaugă într-o listă de numere n-a supraviețuit.
        """
        if _nume_din_apel(nod) in apelate:
            return True
        if isinstance(nod, ast.Name) and nod.id in (set(prin_param) | set(direct)):
            return True
        if isinstance(nod, (ast.Dict, ast.DictComp)):      # `{r: sonda(...) for r in ...}`
            valori = nod.values if isinstance(nod, ast.Dict) else [nod.value]
            return any(e_intregul(v) for v in valori)
        if isinstance(nod, (ast.List, ast.ListComp, ast.Tuple)):
            elts = nod.elts if hasattr(nod, "elts") else [nod.elt]
            return any(e_intregul(v) for v in elts)
        return False

    containere = set()
    for a in ast.walk(fn):
        # `out[n] = sonda(...)` sau `out[n] = {r: sonda(...) ...}` — `out` devine container
        if isinstance(a, ast.Assign) and e_intregul(a.value):
            for t in a.targets:
                baza = t
                while isinstance(baza, ast.Subscript):
                    baza = baza.value
                if isinstance(baza, ast.Name):
                    containere.add(baza.id)
        # `toate.append(sonda(...))` — dar NU `durate.append(sonda(...)["ms"])`
        if (isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute)
                and a.func.attr in ("append", "extend") and a.args
                and e_intregul(a.args[0]) and isinstance(a.func.value, ast.Name)):
            containere.add(a.func.value.id)

    for a in ast.walk(fn):
        if not (isinstance(a, (ast.Return, ast.Yield)) and a.value is not None):
            continue
        if e_intregul(a.value):
            return True
        # un purtător care apare DOAR ca bază de subscript nu scapă: se întoarce o bucată din el
        baze = set()
        for x in ast.walk(a.value):
            if isinstance(x, ast.Subscript):
                b = x.value
                while isinstance(b, ast.Subscript):
                    b = b.value
                if isinstance(b, ast.Name):
                    baze.add(b.id)
        for x in ast.walk(a.value):
            if isinstance(x, ast.Name) and x.id in containere and x.id not in baze:
                return True
    return False


def _nume_folosit(fn, nume):
    """`True` dacă numele e CITIT undeva (nu doar legat)."""
    if not nume or nume == "_":
        return False
    for a in ast.walk(fn):
        if isinstance(a, ast.Name) and a.id == nume and isinstance(a.ctx, ast.Load):
            return True
    return False


def analizeaza(cale, sursa=None, rad=None):
    """`[(fisier, agregator, sonda, pozitie, duce_starea)]` pentru un fișier."""
    sursa = sursa if sursa is not None else io.open(cale, encoding="utf-8").read()
    arbore = ast.parse(sursa)
    s = sonde(arbore)
    if not s:
        return []
    out = []
    for n in ast.walk(arbore):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if n.name in s:
            continue                                   # sonda nu se judecă pe sine
        apelate = {}
        prin_param, direct = set(), set()
        for a in ast.walk(n):
            nume = _nume_din_apel(a)
            if nume in s:
                apelate[nume] = s[nume]
                for arg in a.args:            # parametru de ieșire: sonda scrie în el
                    if isinstance(arg, ast.Name):
                        prin_param.add(arg.id)
        if not apelate:
            continue
        for a in ast.walk(n):                 # purtător direct: `v = sonda(...)`
            if isinstance(a, ast.Assign) and _nume_din_apel(a.value) in apelate:
                for t in a.targets:
                    if isinstance(t, ast.Name):
                        direct.add(t.id)
                    elif isinstance(t, (ast.Tuple, ast.List)):
                        pass                  # despachetarea directă se prinde mai jos
        agrega = any(_nume_din_apel(c) in AGREGARE for c in ast.walk(n))
        indici, despachetate = _pozitii_citite(n, prin_param, direct)
        # POZIȚIE-CHEIE (sondă care întoarce un dict): se caută cheia oriunde în agregator —
        # ca subscript sau ca `.get("...")`. *Limita se scrie: nu se verifică pe CE obiect se
        # citește cheia, deci un agregator care citește `"status"` de pe altceva ar trece drept
        # curat. Cifra e, și pe latura asta, un plafon INFERIOR.*
        chei = set()
        for a in ast.walk(n):
            if isinstance(a, ast.Subscript) and isinstance(a.slice, ast.Constant):
                if isinstance(a.slice.value, str):
                    chei.add(a.slice.value)
            if (isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute)
                    and a.func.attr == "get" and a.args
                    and isinstance(a.args[0], ast.Constant)
                    and isinstance(a.args[0].value, str)):
                chei.add(a.args[0].value)
        for a in ast.walk(n):                 # `st, dt = sonda(...)` — despachetare directă
            if (isinstance(a, ast.Assign) and len(a.targets) == 1
                    and isinstance(a.targets[0], (ast.Tuple, ast.List))
                    and _nume_din_apel(a.value) in apelate):
                despachetate.append([e.id if isinstance(e, ast.Name) else None
                                     for e in a.targets[0].elts])
        # Rezultatul SUPRAVIEȚUIEȘTE apelului? Asta desparte «aruncat» de «nejudecat».
        scapa = _scapa(n, apelate, prin_param, direct)
        for sonda_nume, poz in sorted(apelate.items(), key=lambda kv: str(kv[0])):
            if isinstance(poz, str):
                duce = poz in chei
            else:
                duce = poz in indici
                for grup in despachetate:
                    if poz < len(grup) and _nume_folosit(n, grup[poz]):
                        duce = True
            if duce:
                clasa = "DUCE"
            elif scapa:
                clasa = "NEJUDECATA"     # rezultatul iese din funcție: starea trăiește, nejudecată
            else:
                clasa = "PIERDUTA"       # a extras alte poziții, iar restul moare aici
            out.append((os.path.relpath(cale, rad or RAD), n.name, sonda_nume, poz, clasa,
                        agrega))
    return out


def scaneaza(rad=None):
    rez = []
    for f in fisiere(rad):
        rez += analizeaza(f, rad=rad)
    return rez


# ============================================================================
#  CALIBRARE — în ambele direcții, pe corpus sintetic
# ============================================================================

CORPUS = '''
import httpx, statistics


def _sonda(baza, ruta, rezultat, idx):
    r = httpx.get(baza + ruta)
    st = r.status_code
    rezultat[idx] = (st, 0.1, r.text)


def agregator_care_PIERDE_starea(baza):
    durate = []
    for _ in range(10):
        rez = [None]
        _sonda(baza, "/x", rez, 0)
        durate.append(rez[0][1])
    return {"p50": statistics.median(durate)}


def agregator_care_DUCE_starea_prin_index(baza):
    durate, statusuri = [], {}
    for _ in range(10):
        rez = [None]
        _sonda(baza, "/x", rez, 0)
        durate.append(rez[0][1])
        statusuri[rez[0][0]] = 1
    return {"p50": statistics.median(durate), "statusuri": statusuri}


def agregator_care_DUCE_starea_prin_despachetare(baza):
    durate = []
    for _ in range(10):
        rez = [None]
        _sonda(baza, "/x", rez, 0)
        st, dt, corp = rez[0]
        if st != 200:
            raise AssertionError(st)
        durate.append(dt)
    return durate


def agregator_care_ARUNCA_starea_in_liniuta(baza):
    durate = []
    for _ in range(10):
        rez = [None]
        _sonda(baza, "/x", rez, 0)
        _, dt, _corp = rez[0]
        durate.append(dt)
    return durate


def _sonda_dict(baza, ruta):
    r = httpx.get(baza + ruta)
    d = {"ms": 0.1}
    d["status"] = r.status_code
    return d


def agregator_dict_care_PIERDE_starea(baza):
    durate = []
    for _ in range(10):
        durate.append(_sonda_dict(baza, "/x")["ms"])
    return statistics.median(durate)


def agregator_dict_care_DUCE_starea(baza):
    durate, rele = [], 0
    for _ in range(10):
        d = _sonda_dict(baza, "/x")
        if d["status"] != 200:
            rele += 1
        durate.append(d["ms"])
    return statistics.median(durate), rele


def pastreaza_intreg(baza):
    """Ține dicționarele întregi ȘI le întoarce: starea supraviețuiește. NEJUDECATA."""
    toate = []
    for _ in range(10):
        toate.append(_sonda_dict(baza, "/x"))
    return toate


def citeste_chei_dar_INTOARCE_intregul(baza):
    """Citește `ms` ca să tipărească, dar întoarce dicționarele întregi. NEJUDECATA, nu PIERDUTA.

    E chiar tiparul lui `masoara_p3.curba`, pus în corpus ca proba să nu depindă de codul casei.
    """
    out = {}
    for i in range(10):
        out[i] = _sonda_dict(baza, "/x")
        print("%.3f" % out[i]["ms"])
    return out


def NU_e_agregator(baza):
    rez = [None]
    _sonda(baza, "/x", rez, 0)
    return rez[0][1]


def fara_sonda(x):
    durate = []
    durate.append(x)
    return statistics.median(durate)
'''

#: `(functie, se_aprinde)` — pozitiv ȘI negativ, ca §22 să nu fie o vorbă
CALIBRARE = (
    ("agregator_care_PIERDE_starea", True),
    ("agregator_care_ARUNCA_starea_in_liniuta", True),
    ("agregator_dict_care_PIERDE_starea", True),
    ("agregator_care_DUCE_starea_prin_index", False),
    ("agregator_care_DUCE_starea_prin_despachetare", False),
    ("agregator_dict_care_DUCE_starea", False),
    # PIERDE starea, deși nu agregă nimic: după ce agregarea a încetat să fie condiție de
    # intrare, așteptarea veche («nu se aprinde») a devenit falsă. S-a schimbat AȘTEPTAREA,
    # fiindcă instrumentul avea dreptate — nu invers.
    ("NU_e_agregator", True),
    ("fara_sonda", False),
)


def probe_calibrare():
    rez = analizeaza("sintetic.py", sursa=CORPUS, rad=os.path.dirname("sintetic.py") or ".")
    pierd = {a for _f, a, _s, _p, cls, _g in rez if cls == "PIERDUTA"}
    vazute = {a for _f, a, _s, _p, _c, _g in rez}
    _s = sonde(ast.parse(CORPUS))
    probe = [("sonda cu tuplu e recunoscută, cu poziția 0", _s.get("_sonda") == 0),
             ("sonda cu dict e recunoscută, cu cheia «status»",
              _s.get("_sonda_dict") == "status")]
    for nume, astept in CALIBRARE:
        probe.append(("%s %s" % (nume, "SE aprinde" if astept else "NU se aprinde"),
                      (nume in pierd) == astept))
    probe.append(("cele două care duc starea sunt VĂZUTE, dar nu aprinse",
                  {"agregator_care_DUCE_starea_prin_index",
                   "agregator_care_DUCE_starea_prin_despachetare"} <= vazute))
    nejudecate = {a for _f, a, _s, _p, cls, _g in rez if cls == "NEJUDECATA"}
    probe.append(("cine păstrează rezultatul ÎNTREG intră la NEJUDECATA, nu la PIERDUTA",
                  "pastreaza_intreg" in nejudecate and "pastreaza_intreg" not in pierd))
    probe.append(("cine citește chei DAR întoarce întregul e NEJUDECATA, nu PIERDUTA",
                  "citeste_chei_dar_INTOARCE_intregul" in nejudecate
                  and "citeste_chei_dar_INTOARCE_intregul" not in pierd))
    return probe


def calibreaza(verbose=True):
    probe = probe_calibrare()
    ok = all(r for _n, r in probe)
    if verbose:
        print("CALIBRARE scan_sonde_stare — pozitiv + negativ (METODA §22):")
        for nume, rez in probe:
            print("  %-62s %s" % (nume[:62], "OK" if rez else "PICAT"))
        print("  VERDICT:", "OK" if ok else "PICAT")
    return ok


def main():
    if "--calibrare" in sys.argv:
        return 0 if calibreaza() else 2
    rez = scaneaza()
    pe_clasa = {"PIERDUTA": [], "NEJUDECATA": [], "DUCE": []}
    for r in rez:
        pe_clasa[r[4]].append(r)
    print("DOMENIU: %s" % ", ".join(TIPARE))
    print("fișiere scanate: %d" % len(fisiere()))
    print("locuri de apel sondă↔apelant: %d" % len(rez))
    print()
    print("  PIERDUTA   %d   <-- CIFRA INTERDICȚIEI (a extras alte poziții, starea a rămas afară)"
          % len(pe_clasa["PIERDUTA"]))
    print("  NEJUDECATA %d   <-- se NUMĂRĂ, nu se plafonează (ține rezultatul întreg, nu-l judecă)"
          % len(pe_clasa["NEJUDECATA"]))
    print("  DUCE       %d" % len(pe_clasa["DUCE"]))
    for clasa in ("PIERDUTA", "NEJUDECATA", "DUCE"):
        if not pe_clasa[clasa]:
            continue
        print()
        print("  --- %s ---" % clasa)
        for f, a, sn, p, _c, g in sorted(pe_clasa[clasa], key=lambda r: (r[0], r[1])):
            print("  %-32s %-28s <- %-18s poziția %-8s %s"
                  % (f, a + "()", sn + "()", repr(p), "agregă" if g else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
