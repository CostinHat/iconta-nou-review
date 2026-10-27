# -*- coding: utf-8 -*-
"""GARD — „până la pilot nu intră funcții noi, doar reparații” (comanda Costin 11.2 pct.5, verbatim în DECIZII „Comanda 11.2”).

Verbatim: *„Regulă permanentă, scrisă în DECIZII: până la pilot nu intră funcții noi, doar reparații. Pilotul pornește când o lună completă
de contabil merge cap-coadă pe o firmă fără deficiențe grave: facturi, bancă, casă, stoc, salarii, închidere, D300, D394, D112, D100,
balanță.”*

CE MĂSOARĂ (un clichet, față de starea de la închiderea lotului 11, scrisă în `scripts/rute_inainte_de_pilot.txt`):
  (1) rutele HTTP ale aplicației: decoratorii `@app.get/post/put/delete/patch/...` din `main.py` (singurul loc cu rute — `APIRouter` nu
      există în aplicație; orice `include_router` / `api_route` / `add_api_route` cu altă țintă decât adresele retrase 410 e refuzat);
  (2) funcționalitățile din `FUNCTIONALITATI.csv`: mulțimea ID-urilor ȘI mulțimea celor „în aplicație” (starea începe cu LIVE / PARTIAL /
      API / INTERN) — o funcționalitate trecută din PLANIFICAT / AMANAT / RESPINS în LIVE e tot o funcție nouă.
O rută / un ID / o trecere în LIVE care nu e în referință pică poarta. EXCEPȚIA (o reparație poate cere o rută): o intrare în
`EXCEPTII` de mai jos, cu numărul deficienței pe care o repară — numărul trebuie să existe în `DEFICIENTE.md`.

Referința e exactă în ambele sensuri: o rută scoasă (reparație care elimină un drum dublu, ex. formularul manual al lui 429) se scoate și
din referință, altfel referința ar acoperi o rută care nu mai există. Amprenta referinței (`AMPRENTA_REFERINTA`) stă aici, în gardă: o
referință rescrisă fără să se schimbe și garda e prinsă; rescrierea ei e un act vizibil în diff (permis o dată, la închiderea lotului
11 — `python core/test_fara_functii_noi.py --scrie-referinta`).

LIMITĂ DECLARATĂ: garda vede o funcție nouă numai prin rută sau prin registru. O funcție nouă strecurată într-o rută existentă (un
parametru nou, un ecran nou peste API-ul vechi) nu se vede mecanic — rămâne disciplina regulii.

CRITERIILE PILOTULUI stau ca date în `PILOT_CRITERII.md` (cele 11 domenii, fiecare cu starea lui); garda de aici le păzește forma.
"""
import ast
import csv
import hashlib
import io
import os
import re
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERINTA = os.path.join(_RAD, "scripts", "rute_inainte_de_pilot.txt")
CRITERII = os.path.join(_RAD, "PILOT_CRITERII.md")
METODE = ("get", "post", "put", "delete", "patch", "head", "options", "api_route", "websocket")
STARI_IN_APLICATIE = ("LIVE", "PARTIAL", "API", "INTERN")
#: [11.2 pct.5] excepția: {"METODĂ /cale" sau "F<id>" sau "LIVE F<id>": "<nr deficiență>"} — reparația care cere ruta / funcționalitatea
EXCEPTII = {
    # [lotul 12] funcții CERUTE explicit de Costin (comanda 12.1 pct.8: „461 lista de parteneri și 477 introducerea manuală a facturilor
    # primite sunt cerute”) și ruta reparației 495 (ciorna facturii pe server, ca să se regăsească pe alt calculator)
    "GET /tenants/{tenant_id}/parteneri-firma": "461",
    "GET /tenants/{tenant_id}/parteneri-firma/fisa": "461",
    "POST /tenants/{tenant_id}/facturi-primite/manual": "477",
    "GET /tenants/{tenant_id}/ciorne-formular/{formular}": "495",
    "PUT /tenants/{tenant_id}/ciorne-formular/{formular}": "495",
    "DELETE /tenants/{tenant_id}/ciorne-formular/{formular}": "495",
    # [lotul 12, C139] raportul Z importat greșit (ciornă) n-avea niciun drum de ștergere: jurnalul trimite nota Z-ului la ecranul Raport Z
    "DELETE /tenants/{tenant_id}/horeca/raport-z/{nota_id}": "C139",
    # [lotul 13, 681] căutarea globală din antet — decizia Costin 25.10.2026 (comanda 13.1): „parte din pilot, excepție de la «fără funcții
    # noi»”
    "GET /eu/cautare": "681",
    # [lotul 13, zona fact] rutele reparațiilor comenzii 13.1: ștergerea fișei de furnizor fără documente (640), completarea notificării
    # e-Transport din factură / NIR (534), emiterea ciornei lunii din șablonul recurent (680)
    "DELETE /tenants/{tenant_id}/furnizori/{furnizor_id}": "640",
    "GET /tenants/{tenant_id}/etransport/din-document": "534",
    "POST /tenants/{tenant_id}/facturi-recurente/{sid}/emite": "680",
    # [lotul 13, reparațiile finale] rutele reparațiilor comenzii 13.1, fiecare cu deficiența ei: lista anunțurilor trimise și retragerea
    # unei trimiteri (646 c), retragerea invitației (646 e), starea pașilor de preluare ai firmei (662 — „Începe / Continuă preluarea”),
    # listele din care formularele Operațiunilor aleg ce aplicația știe deja (511 facturile neîncasate, 524 facturile în valută)
    "GET /admin/anunturi": "646",
    "POST /admin/anunturi/{lot}/retrage": "646",
    "POST /admin/invitatii/{invitatie_id}/retrage": "646",
    "GET /migrare/firma/{tenant_id}": "662",
    "GET /tenants/{tenant_id}/operatiuni-date": "524",
    # [lotul 13, 536] centrul de cost pe salariați, mijloace fixe și (decizia Costin 26.10.2026, varianta (a)) articolele de stoc —
    # comanda 13.1 la 536: „Centrul se poate pune pe liniile facturilor, NIR-urilor, salariilor și pe mijloacele fixe”
    "PUT /tenants/{tenant_id}/centre-cost/alocari": "536",
    # [lotul 13, 681] rândul din registru al căutării funcțiilor (ruta GET /eu/cautare are deja excepția 681)
    "F268": "681",
    "LIVE F268": "681",
}
#: sha256 al conținutului referinței (fără liniile de comentariu); se schimbă numai împreună cu referința (vezi docstring)
#: [26.10.2026, lotul 13] referința s-a schimbat numai prin scoaterea din [live] a celor cinci formulare înlocuite de Declarația unică
#: (660: F214, F215, F221, F222, F227, trecute în RESPINS) — exactă în ambele sensuri; amprenta veche: 4b107c8b…
AMPRENTA_REFERINTA = "5d5b9b7a05749070b18e6d4e37d52cdbc54d90864a8ae7c6a9769e14f18dc228"
DOMENII_PILOT = ("facturi", "bancă", "casă", "stoc", "salarii", "închidere", "D300", "D394", "D112", "D100", "balanță")
STARI_PILOT = ("neprobat", "în probă", "probat")


def rute(src):
    """PURĂ. ({"METODĂ /cale"}, [probleme]) — rutele decorate pe `app` + apelurile care ar adăuga rute pe alt drum."""
    out, rele = set(), []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in n.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and isinstance(d.func.value, ast.Name)
                        and d.func.value.id == "app" and d.func.attr in METODE):
                    if d.args and isinstance(d.args[0], ast.Constant) and isinstance(d.args[0].value, str):
                        out.add("%s %s" % (d.func.attr.upper(), d.args[0].value))
                    else:
                        rele.append("ruta funcției %s (linia %d) nu are calea scrisă literal" % (n.name, n.lineno))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            a = n.func.attr
            if a in ("include_router", "add_route", "add_websocket_route"):
                rele.append("linia %d: %s — rutele se declară numai cu decoratori pe `app`" % (n.lineno, a))
            elif a == "add_api_route":
                h = n.args[1] if len(n.args) > 1 else next((k.value for k in n.keywords if k.arg == "endpoint"), None)
                if not (isinstance(h, ast.Name) and h.id == "_adresa_retrasa"):
                    rele.append("linia %d: add_api_route cu altă țintă decât adresele retrase (410)" % n.lineno)
            elif a == "mount" and isinstance(n.func.value, ast.Name) and n.func.value.id == "app":
                if not (n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == "/static"):
                    rele.append("linia %d: app.mount nou" % n.lineno)
    return out, rele


def functionalitati(text):
    """PURĂ. ({ID}, {ID în aplicație}) din textul lui FUNCTIONALITATI.csv."""
    toate, active = set(), set()
    for r in csv.DictReader(io.StringIO(text)):
        i = (r.get("ID") or "").strip()
        if not i:
            continue
        toate.add(i)
        if (r.get("Stare") or "").strip().upper().startswith(STARI_IN_APLICATIE):
            active.add(i)
    return toate, active


def _citeste(cale):
    return io.open(cale, encoding="utf-8").read()


def masoara():
    """Starea de acum: {"rute": {...}, "functionalitati": {...}, "live": {...}}, plus problemele de drum."""
    r, rele = rute(_citeste(os.path.join(_RAD, "main.py")))
    f, a = functionalitati(_citeste(os.path.join(_RAD, "FUNCTIONALITATI.csv")))
    return {"rute": r, "functionalitati": f, "live": a}, rele


def citeste_referinta(text):
    """PURĂ. {secțiune: {linii}} + amprenta conținutului (fără comentarii)."""
    sec, cur, util = {}, None, []
    for ln in text.splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        util.append(ln)
        m = re.match(r"^\[(\w+)\]$", ln)
        if m:
            cur = sec.setdefault(m.group(1), set())
        elif cur is not None:
            cur.add(ln.strip())
    return sec, hashlib.sha256("\n".join(util).encode("utf-8")).hexdigest()


def text_referinta(stare):
    cap = ("# Referința gărzii core/test_fara_functii_noi.py (comanda Costin 11.2 pct.5: „până la pilot nu intră funcții noi, doar reparații”).\n"
           "# Starea de la închiderea lotului 11: rutele din main.py, ID-urile din FUNCTIONALITATI.csv și cele „în aplicație” (LIVE / PARTIAL /\n"
           "# API / INTERN). Nu se editează de mână: o rută nouă intră numai prin EXCEPTII (cu numărul deficienței), în gardă.\n"
           "# %d rute, %d funcționalități, %d în aplicație.\n" % (len(stare["rute"]), len(stare["functionalitati"]), len(stare["live"])))
    corp = []
    for s in ("rute", "functionalitati", "live"):
        corp.append("[%s]" % s)
        corp.extend(sorted(stare[s]))
    return cap + "\n".join(corp) + "\n"


def abateri(stare, ref, exceptii, numere):
    """PURĂ. Lista abaterilor stării de acum față de referință, cu excepțiile (care trebuie să numească o deficiență din registru)."""
    rele = []
    for k, nr in exceptii.items():
        if str(nr) not in numere:
            rele.append("excepția %s numește deficiența %s, care nu e în DEFICIENTE.md" % (k, nr))
    for s, ce, cheie in (("rute", "rută nouă", "%s"), ("functionalitati", "funcționalitate nouă", "%s"),
                         ("live", "funcționalitate trecută în aplicație", "LIVE %s")):
        acum, inainte = stare[s], ref.get(s, set())
        for x in sorted(acum - inainte):
            if (cheie % x) not in exceptii:
                rele.append("%s: %s — până la pilot nu intră funcții noi, doar reparații (comanda 11.2 pct.5); dacă repară o deficiență, "
                            "adaug-o în EXCEPTII din core/test_fara_functii_noi.py cu numărul ei" % (ce, x))
        for x in sorted(inainte - acum):
            rele.append("%s: %s nu mai există — scoate-o și din scripts/rute_inainte_de_pilot.txt (referința e exactă)" % (s, x))
        for k in exceptii:
            x = k[5:] if k.startswith("LIVE ") else k
            if s == ("live" if k.startswith("LIVE ") else ("rute" if " /" in k else "functionalitati")):
                if x in inainte:
                    rele.append("excepția %s e deja în referință — scoate-o din EXCEPTII" % k)
                elif x not in acum:
                    rele.append("excepția %s nu mai corespunde nimic în aplicație — scoate-o din EXCEPTII" % k)
    return rele


def _numere_deficiente():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test_deficiente import randuri
    return {r["nr"] for r in randuri()}


def test_nicio_functie_noua_pana_la_pilot():
    """Comanda 11.2 pct.5. MUTAȚIE: o rută nouă în main.py fără deficiență în EXCEPTII -> pică."""
    stare, drum = masoara()
    ref, amp = citeste_referinta(_citeste(REFERINTA))
    assert amp == AMPRENTA_REFERINTA, ("scripts/rute_inainte_de_pilot.txt a fost rescrisă (amprenta %s, garda știe %s): referința se "
                                       "schimbă numai odată cu garda" % (amp, AMPRENTA_REFERINTA))
    rele = drum + abateri(stare, ref, EXCEPTII, _numere_deficiente())
    assert not rele, "\n".join(rele)


def test_garda_functiilor_noi_nu_e_vida():
    """Anti-vacuu: pică pe un fragment sintetic rău (rută nouă, ID nou, trecere în LIVE, drum ocolit), trece pe unul bun."""
    src = ('@app.get("/a")\ndef a(): pass\n@app.post("/tenants/{t}/b")\ndef b(): pass\n'
           'for c in ADRESE_RETRASE:\n    app.add_api_route(c, _adresa_retrasa, methods=["GET"])\n')
    r, drum = rute(src)
    assert r == {"GET /a", "POST /tenants/{t}/b"} and drum == []
    csvt = "Functionalitate,ID,Stare\nx,F001,LIVE\ny,F002,PLANIFICAT\n"
    f, a = functionalitati(csvt)
    assert (f, a) == ({"F001", "F002"}, {"F001"})
    ref = {"rute": set(r), "functionalitati": set(f), "live": set(a)}
    numere = {"451"}
    assert abateri({"rute": r, "functionalitati": f, "live": a}, ref, {}, numere) == []
    rau = rute(src + '@app.delete("/c")\ndef c(): pass\n')[0]
    assert abateri({"rute": rau, "functionalitati": f, "live": a}, ref, {}, numere), "rută nouă trecută"
    assert abateri({"rute": rau, "functionalitati": f, "live": a}, ref, {"DELETE /c": "451"}, numere) == [], "excepția cu deficiență"
    assert abateri({"rute": rau, "functionalitati": f, "live": a}, ref, {"DELETE /c": "999"}, numere), "excepție fără deficiență"
    assert abateri({"rute": r, "functionalitati": f | {"F003"}, "live": a}, ref, {}, numere), "ID nou trecut"
    assert abateri({"rute": r, "functionalitati": f, "live": a | {"F002"}}, ref, {}, numere), "trecere în LIVE trecută"
    assert abateri({"rute": r - {"GET /a"}, "functionalitati": f, "live": a}, ref, {}, numere), "rută scoasă, referință stale"
    for ocol in ('app.include_router(r)\n', 'app.add_api_route("/x", f)\n', 'app.mount("/y", z)\n',
                 'P = "/z"\n@app.get(P)\ndef z(): pass\n'):
        assert rute(src + ocol)[1], "drum ocolit trecut: %r" % ocol
    t = text_referinta(ref)
    assert citeste_referinta(t)[0] == ref


def criterii_pilot(text):
    """PURĂ. [(domeniu, stare, rest)] din tabelul lui PILOT_CRITERII.md."""
    out = []
    for ln in text.splitlines():
        m = re.match(r"^\| (\d+) \| ([^|]+?) \| ([^|]+?) \|(.*)\|\s*$", ln)
        if m:
            out.append((m.group(2).strip(), m.group(3).strip(), m.group(4).strip()))
    return out


def test_criteriile_pilotului_sunt_cele_11_domenii_cu_stare():
    """Comanda 11.2 pct.5: cele 11 domenii, în ordinea comenzii, fiecare cu starea din mulțimea închisă; „probat” cere firma, luna și
    dovada. MUTAȚIE: un domeniu șters / o stare inventată / „probat” fără dovadă -> pică."""
    rele = []
    c = criterii_pilot(_citeste(CRITERII))
    if [d for d, _, _ in c] != list(DOMENII_PILOT):
        rele.append("domeniile pilotului trebuie să fie exact %s, în ordine: %s" % (DOMENII_PILOT, [d for d, _, _ in c]))
    for d, s, rest in c:
        if s not in STARI_PILOT:
            rele.append("%s: stare %r (permise: %s)" % (d, s, STARI_PILOT))
        elif s == "probat" and not all(k in rest for k in ("firma:", "luna:", "dovadă:")):
            rele.append("%s: „probat” fără „firma:”, „luna:” și „dovadă:”" % d)
    assert not rele, "\n".join(rele)
    assert criterii_pilot("| 1 | facturi | neprobat | |\n") == [("facturi", "neprobat", "")], "anti-vacuu: cititorul tabelului"


if __name__ == "__main__":
    if sys.argv[1:] == ["--scrie-referinta"]:
        st, dr = masoara()
        assert not dr, dr
        t = text_referinta(st)
        io.open(REFERINTA, "w", encoding="utf-8").write(t)
        print("scris %s: %d rute, %d funcționalități, %d în aplicație; AMPRENTA_REFERINTA = %r"
              % (os.path.relpath(REFERINTA, _RAD), len(st["rute"]), len(st["functionalitati"]), len(st["live"]), citeste_referinta(t)[1]))
    else:
        print("folosire: python core/test_fara_functii_noi.py --scrie-referinta   (o dată, la închiderea lotului 11)")
