# -*- coding: utf-8 -*-
"""GARD — ecranul nu anunță rezultatul unei scrieri după o cheie pe care ruta n-o întoarce (comanda Costin 07.10.2026, C5).

Instanța: Operațiuni › „Chirii / comodat” — ruta `nota-chirie` scrie ciorna și întoarce `{inregistrari: [31]}`, iar ecranul
căuta `r.inregistrare_id` -> „Calcul (nu s-a generat nicio notă): inregistrari: 31”. Clasa, măsurată pe toate cele 81 de
scrieri cu răspunsul citit (rutele dinamice ale Operațiunilor desfăcute pe cele 34): încă un defect — REGES › Răspunsuri
spunea „niciun răspuns nou” după ce mesajul fusese CONSUMAT din coada REGES și scris (citea `mesaje`/`raspunsuri`) — și două
citiri moarte (`r.referinta`, `r.id`/`r.mesaj`). DS cap.27: un act se încheie cu o confirmare care spune ce s-a întâmplat.

CUM CITEȘTE: în `static/js`, fiecare `const X = await api.post|put|patch|delete(`…`)`; cheile `X.cheie` citite până la
`catch`, cu ALTERNATIVELE (`X.a || X.b`, `X.a ?? X.b` = un grup: ajunge ca ruta să producă una); ruta din `main.py` (segmentele `${…}` = parametri de cale; cele DINAMICE se desfac din `DINAMICE`); use-case-ul
`_uc_*.f`, apoi — urmând apelurile în modulele `core/` — TOATE cheile pe care le poate produce (chei de dict literal, argumente
numite, `x["cheie"] = …`). Cheia citită și neprodusă nicăieri pe drum = roșu.
LIMITA, declarată: (1) supra-aproximează producătorul (o cheie produsă oriunde pe drum trece, chiar pe altă ramură); (2) nu
vede cheile venite din rânduri SQL (de-aceea citirile GET NU sunt în perimetru — măsurat: 5 fals-pozitive din 53, toate rânduri
de bază de date); (3) vede numai răspunsurile puse într-o variabilă `const X = await api…`.
"""
import ast
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: segmente dinamice ale căii -> de unde se citesc valorile lor (o rută dinamică nedesfăcută = roșu, nu sărită)
DINAMICE = {
    "${opCurenta.ruta}": ("static/js/ecrane/operatiuni_ecran.js", r'ruta: *"([^"]+)"'),
    "${tip()}": ("static/js/ecrane/firme.js", r'<option value="(s100[35])">'),
}
#: (fișier, cheie) citite deliberat fără să fie produse, cu motivul — goală: fiecare citire are producătorul ei
EXCEPTII = {}
_FARA = {"length", "map", "join", "forEach", "filter", "slice", "some", "find"}


def _citeste(p):
    return io.open(os.path.join(RAD, p), encoding="utf-8").read()


def _rute_main():
    s = _citeste("main.py")
    out = {}
    for n in ast.parse(s).body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in n.decorator_list:
                if isinstance(d, ast.Call) and getattr(d.func, "attr", "") in ("post", "put", "patch", "delete") and d.args \
                        and isinstance(d.args[0], ast.Constant) and isinstance(d.args[0].value, str):
                    out[(d.func.attr, re.sub(r"\{[^}]+\}", "{}", d.args[0].value))] = n
    return out


_MOD = {}


def _modul(nume):
    """(funcții, alias-uri de import) ale unui modul — `main` = main.py, altfel core/<nume>.py."""
    if nume not in _MOD:
        cale = os.path.join(RAD, "main.py" if nume == "main" else "core/%s.py" % nume)
        if not os.path.exists(cale):
            _MOD[nume] = None
        else:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
            fns = {n.name: n for n in arb.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            _MOD[nume] = (fns, _aliasuri(arb.body))
    return _MOD[nume]


def _aliasuri(noduri):
    al = {}
    for n in noduri:
        for x in ast.walk(n) if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) else []:
            _alias(x, al)
    return al


def _alias(x, al):
    if isinstance(x, ast.ImportFrom) and (x.module or "").startswith("core"):
        for a in x.names:
            al[a.asname or a.name] = ("mod", a.name) if x.module == "core" else ("fn", x.module.split(".")[-1], a.name)
    elif isinstance(x, ast.Import):
        for a in x.names:
            if a.name.startswith("core."):
                al[a.asname or a.name.split(".")[-1]] = ("mod", a.name.split(".")[-1])


def _chei_locale(fn):
    k = set()
    for x in ast.walk(fn):
        if isinstance(x, ast.Dict):
            k |= {c.value for c in x.keys if isinstance(c, ast.Constant) and isinstance(c.value, str)}
        elif isinstance(x, ast.Call):
            k |= {kw.arg for kw in x.keywords if kw.arg}
        elif isinstance(x, ast.Subscript) and isinstance(x.ctx, ast.Store) and isinstance(x.slice, ast.Constant) \
                and isinstance(x.slice.value, str):
            k.add(x.slice.value)
    return k


def chei_produse(modul, fn, adanc=0, vazut=None):
    """Cheile pe care `fn` le poate pune într-un răspuns, urmând apelurile în modulele `core/` (adâncime 5)."""
    vazut = set() if vazut is None else vazut
    if (modul, fn.name) in vazut or adanc > 5:
        return set()
    vazut.add((modul, fn.name))
    k = _chei_locale(fn)
    m = _modul(modul)
    if not m:
        return k
    fns, al = m
    al = dict(al)
    for x in ast.walk(fn):           # importurile LOCALE ale funcției au întâietate (același alias, module diferite)
        _alias(x, al)
    for x in ast.walk(fn):
        if not isinstance(x, ast.Call):
            continue
        t = None
        if isinstance(x.func, ast.Name) and x.func.id in fns:
            t = (modul, fns[x.func.id])
        elif isinstance(x.func, ast.Name) and al.get(x.func.id, ("",))[0] == "fn":
            mm = _modul(al[x.func.id][1])
            t = (al[x.func.id][1], mm[0].get(al[x.func.id][2])) if mm else None
        elif isinstance(x.func, ast.Attribute) and isinstance(x.func.value, ast.Name) \
                and al.get(x.func.value.id, ("",))[0] == "mod":
            mm = _modul(al[x.func.value.id][1])
            t = (al[x.func.value.id][1], mm[0].get(x.func.attr)) if mm else None
        if t and t[1] is not None:
            k |= chei_produse(t[0], t[1], adanc + 1, vazut)
    return k


def _tinta_uc(nmain):
    for x in ast.walk(nmain):
        if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and isinstance(x.func.value, ast.Name) \
                and x.func.value.id.startswith("_uc"):
            return x.func.value.id.lstrip("_"), x.func.attr
    return None


def grupuri(var, bloc):
    """Cheile citite din răspuns, ca GRUPURI de alternative: `r.a || r.b` / `r.a ?? (r.b …)` -> {a, b} (ajunge una);
    o citire singură -> {a}. Un cititor comun mai multor rute (Operațiunile) citește legitim forma fiecăreia."""
    v = re.escape(var)
    chei = set(re.findall(r"\b%s\.(\w+)" % v, bloc)) - _FARA
    parinte = {k: k for k in chei}

    def rad(k):
        while parinte[k] != k:
            k = parinte[k]
        return k
    for a, b in re.findall(r"\b%s\.(\w+)\s*(?:\|\||\?\?)\s*\(?\s*%s\.(\w+)" % (v, v), bloc):
        if a in parinte and b in parinte:
            parinte[rad(a)] = rad(b)
    g = {}
    for k in chei:
        g.setdefault(rad(k), set()).add(k)
    return [frozenset(x) for x in g.values()]


def apeluri(fisiere_js):
    """[(fișier, linie, cale, metodă, {chei citite})] — rutele dinamice desfăcute; o cale dinamică nedeclarată rămâne cu `${`."""
    out = []
    for f, s in fisiere_js:
        for m in re.finditer(r"const (\w+) = await api\.(post|put|patch|delete)\(`([^`]+)`", s):
            var, met, url = m.groups()
            rest = s[m.end():]
            stop = re.search(r"\n\s*\}\s*catch|\bconst %s = await" % re.escape(var), rest)
            citite = grupuri(var, rest[:stop.start() if stop else 1500])
            if not citite:
                continue
            urluri = [url]
            for seg, (sursa, rx) in DINAMICE.items():
                if seg in url:
                    urluri = [u.replace(seg, v) for u in urluri for v in re.findall(rx, _citeste(sursa))]
            for u in urluri:
                cale = re.sub(r"\$\{[^}]+\}", "{}", re.sub(r"^/tenants/\$\{[^}]+\}", "/tenants/{}", u.split("?")[0]))
                out.append((f, s[:m.start()].count("\n") + 1, cale, met, citite))
    return out


def nepotriviri(fisiere_js):
    rute = _rute_main()
    rele, nerezolvate, n = [], [], 0
    for f, linie, cale, met, citite in apeluri(fisiere_js):
        n += 1
        nm = rute.get((met, cale))
        if nm is None:
            nerezolvate.append((f, linie, met.upper(), cale))
            continue
        t = _tinta_uc(nm)
        uc = _modul(t[0])[0].get(t[1]) if t and _modul(t[0]) else None
        produse = chei_produse(t[0], uc) if uc is not None else chei_produse("main", nm)
        for g in sorted(citite, key=sorted):
            if not (g & produse) and not any((os.path.basename(f), k) in EXCEPTII for k in g):
                rele.append((f, linie, met.upper(), cale, g))
    return rele, nerezolvate, n


def _js_reale():
    out = []
    for d, _s, fs in os.walk(os.path.join(RAD, "static/js")):
        if {"vendor"} & set(d.split(os.sep)):
            continue
        for f in sorted(fs):
            if f.endswith(".js"):
                p = os.path.relpath(os.path.join(d, f), RAD)
                out.append((p, _citeste(p)))
    return out


def test_ecranul_citeste_din_raspunsul_scrierii_numai_ce_ruta_intoarce():
    rele, nerezolvate, n = nepotriviri(_js_reale())
    assert n >= 80, "premisă: scrierile cu răspuns citit chiar se găsesc (%d)" % n
    assert nerezolvate == [], "scrieri a căror rută nu se găsește în main.py (o cale dinamică nouă se declară în DINAMICE):\n  " \
        + "\n  ".join("%s:%d %s %s" % x for x in nerezolvate)
    assert rele == [], "\n  ".join("%s:%d %s %s citește `%s`, pe care ruta n-o întoarce" % (f, l, m, c, "` / `".join(sorted(g)))
                                   for f, l, m, c, g in rele)


def test_CALIBRARE_prinde_instanta_C5():
    """Codul de dinainte (815619dd) al ecranului Operațiuni, pe universul real al rutelor: nota-chirie e prinsă."""
    vechi = '''
        const r = await api.post(`/tenants/${t.id}/${opCurenta.ruta}`, corpReq);
        zona.innerHTML = r && r.inregistrare_id ? "nota" : "calcul";
      } catch (e) {}
    '''
    js = _citeste("static/js/ecrane/operatiuni_ecran.js") + vechi
    rele, _n, _c = nepotriviri([("static/js/ecrane/operatiuni_ecran.js", js)])
    assert [(c, g) for _f, _l, _m, c, g in rele] == [("/tenants/{}/nota-chirie", frozenset({"inregistrare_id"}))], rele


def test_CALIBRARE_prinde_REGES_si_ruta_dinamica_nedeclarata():
    reges = '''
        const r = await api.post(`/tenants/${t.id}/reges-poll`, {});
        const msgs = (r && (r.mesaje || r.raspunsuri)) || [];
      } catch (e) {}
        const q = await api.post(`/tenants/${t.id}/${altceva()}-valideaza`, {});
        q.ok;
      } catch (e) {}
    '''
    rele, nerezolvate, _n = nepotriviri([("x.js", reges)])
    assert [g for *_x, g in rele] == [frozenset({"mesaje", "raspunsuri"})], rele
    assert [c for *_x, c in nerezolvate] == ["/tenants/{}/{}-valideaza"], nerezolvate
