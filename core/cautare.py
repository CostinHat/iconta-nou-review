# -*- coding: utf-8 -*-
"""core/cautare.py — căutarea globală din antet (lotul 13, deficiența 681).

Decizia Costin, 25.10.2026 (comanda 13.1, verbatim): „Căsuță de căutare în antet, mereu vizibilă; scrii o funcție, o declarație sau un nume
(«diurnă», «tichet», «D112», un salariat) și te duce în fereastra potrivită, pentru firma în lucru. Proba: «Decont deplasare / diurnă» nu se
găsește azi fără să știi că e în Operațiuni → Personal și deconturi.” Parte din pilot, excepție de la „fără funcții noi”.

PRECIZAREA din 26.10.2026 (Costin, verbatim): „căutarea este a funcțiilor aplicației (scrii «D300», «stat de plată», «NIR» și te duce în
fereastra respectivă), nu căutare de documente sau date. Căsuța trebuie să fie accesibilă din fiecare fereastră de lucru (pe bara de sus a
ferestrei, lângă traseu), nu doar în antetul paginii, care e acoperit de ferestre; plus scurtătura Ctrl+K de oriunde.” SUPERSEDEAZĂ „un nume /
un salariat” din decizia veche: numele unui salariat e DATĂ a firmei, nu funcție — nu se mai caută și nu se mai citește din firmă.

DE UNDE VIN REZULTATELE — fiecare dintr-o sursă care există deja, nicio listă scrisă a doua oară:
  · cardurile ferestrei firmei: lista `optiuni` din `meniuFirma` (`static/js/ecrane/firme.js`) — cheia, regimul, grupul, titlul, descrierea;
  · operațiunile speciale: registrul `REGISTRU` din `static/js/ecrane/operatiuni_ecran.js` — titlul, categoria, ruta și etichetele
    câmpurilor („Diurna acordată pe zi” găsește decontul și când omul nu știe numele operației);
  · declarațiile firmei: `declaratii_api.tipuri()` cu filtrul formei firmei (ca `uc_declaratii.declaratii_tipuri`), denumirea oficială din
    `core/dNNN.DENUMIRE_OFICIALA` (sursa listei publice, `scripts/genereaza_declaratii_lista.py`).
Din firma în lucru se citește numai forma ei (tipul de firmă: ce funcții are); nicio dată a firmei (nume, sume, documente) nu intră în căutare.
Sursele JS se citesc o dată și se recitesc numai când fișierul s-a schimbat (data modificării). Căutarea ignoră diacriticele și majusculele;
fiecare cuvânt scris trebuie să apară. `SINONIME` leagă cuvintele contabilului de fereastra în care lucrează („tichet” -> Salariați: tichetele
se pun pe rândul salariatului), nu o listă de funcții.

DREPTURI: firma se citește numai dacă utilizatorul are acces la ea (`_schema_sau_404`, același drum ca rutele firmei); ruta fiecărei
operațiuni pleacă în rezultat, ecranul îi compune acțiunea (`actiuneOp`) și o ascunde celui căruia serverul i-o refuză (`drepturi.permis`).
Gard: `core/test_lot13_ds_cautare.py`.
"""
import json
import os
import re
import unicodedata

from core.cache_declarat import Declaratie as _Dec

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSA_CARDURI = os.path.join(_RAD, "static", "js", "ecrane", "firme.js")
SURSA_OPERATIUNI = os.path.join(_RAD, "static", "js", "ecrane", "operatiuni_ecran.js")

#: cuvântul contabilului -> cardul ferestrei firmei unde se face lucrul (nu e un titlu de card)
SINONIME = {
    "tichet": "salariati", "tichete": "salariati", "masa": "salariati", "vacanta": "salariati", "cadou": "salariati",
    "cresa": "salariati", "pontaj": "salariati", "fluturas": "salariati", "stat de plata": "salariati", "concediu": "salariati",
    "salariu": "salariati", "angajat": "salariati", "nir": "stocuri", "gestiune": "stocuri", "inventar": "stocuri",
    "amortizare": "mijloace", "casare": "mijloace", "extras": "banca", "nota contabila": "jurnal", "note contabile": "jurnal",
    "chitanta": "casa", "dispozitie": "casa", "factura": "facturi", "facturi": "facturi", "spv": "facturi", "efactura": "facturi",
    "balanta": "balanta", "fisa de cont": "fisacont", "sold initial": "import", "preluare": "import", "solduri": "import",
}

_SIR = r'"((?:[^"\\]|\\.)*)"'
_RE_CARD = re.compile(r"\{\s*cheie:\s*" + _SIR + r",\s*regim:\s*" + _SIR + r",\s*grup:\s*" + _SIR + r",\s*titlu:\s*" + _SIR
                      + r",\s*desc:\s*" + _SIR)
_RE_GRUP = re.compile(r"\[\s*" + _SIR + r"\s*,\s*" + _SIR + r"\s*\]")
_RE_OP = re.compile(r"\{\s*cat:\s*" + _SIR + r",\s*cheie:\s*" + _SIR + r",\s*titlu:\s*" + _SIR + r",\s*ruta:\s*" + _SIR)
_RE_CAMP = re.compile(r"\b(?:C|DN)\(\s*" + _SIR + r"\s*,\s*" + _SIR)
_cache = {}
_cache_DECLARATIE = _Dec(
    rol="sursele JS ale căutării din antet (cardurile din `firme.js`, registrul operațiunilor din `operatiuni_ecran.js`), ca o căutare să nu "
        "recitească fișierele la fiecare literă scrisă",
    sursa="fișierele `static/js/ecrane/firme.js` și `static/js/ecrane/operatiuni_ecran.js` (versionate); aplicația nu le scrie",
    motiv="citirea a două fișiere sursă mari pe calea fiecărei cereri de căutare",
    invalidare="la schimbarea datei modificării fișierului (`_citeste` compară `getmtime` la fiecare citire); plus repornirea procesului, "
               "pe care publicarea o face la orice commit",
    dovada="core/test_cache_declarat.py::test_cautare_se_reconstruieste_identic",
)


def normalizeaza(text):
    """Text de comparat: litere mici, fără diacritice (ș/ş, ț/ţ, ă, â, î), spațiile strânse."""
    t = unicodedata.normalize("NFKD", str(text or "").lower())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", t).strip()


def _sir_js(s):
    """Un șir JS scris între ghilimele duble (cu `\\u0103`) -> textul lui."""
    try:
        return json.loads('"' + s + '"')
    except ValueError:
        return s


def _citeste(cale):
    """(conținutul, data modificării) — recitit numai când fișierul s-a schimbat."""
    m = os.path.getmtime(cale)
    v = _cache.get(cale)
    if not v or v[0] != m:
        with open(cale, encoding="utf-8") as h:
            v = (m, h.read())
        _cache[cale] = v
    return v[1]


def carduri_firma():
    """Cardurile ferestrei firmei: [{cheie, regim, grup, grup_titlu, titlu, desc}] (`firme.js`, `meniuFirma` + `GRUPURI_FIRMA`)."""
    t = _citeste(SURSA_CARDURI)
    i = t.find("export const GRUPURI_FIRMA = [")
    grupuri = dict((_sir_js(a), _sir_js(b)) for a, b in _RE_GRUP.findall(t[i:t.find("];", i)])) if i >= 0 else {}
    inceput = t.find("function meniuFirma(")
    corp = t[inceput:t.find("\n}\n", inceput)] if inceput >= 0 else ""
    return [{"cheie": _sir_js(c), "regim": _sir_js(r), "grup": _sir_js(g), "grup_titlu": grupuri.get(_sir_js(g), ""),
             "titlu": _sir_js(ti), "desc": _sir_js(d)} for c, r, g, ti, d in _RE_CARD.findall(corp)]


def operatiuni():
    """Operațiunile speciale: [{cheie, cat, titlu, ruta, campuri}] (`operatiuni_ecran.js`, `REGISTRU`)."""
    t = _citeste(SURSA_OPERATIUNI)
    i = t.find("const REGISTRU = [")
    corp = t[i:t.find("\nconst CATEGORII", i)] if i >= 0 else ""
    poz = [(m.start(), m) for m in _RE_OP.finditer(corp)]
    out = []
    for k, (p, m) in enumerate(poz):
        bucata = corp[p:poz[k + 1][0] if k + 1 < len(poz) else len(corp)]
        out.append({"cat": _sir_js(m.group(1)), "cheie": _sir_js(m.group(2)), "titlu": _sir_js(m.group(3)), "ruta": _sir_js(m.group(4)),
                    "campuri": sorted({_sir_js(e) for _n, e in _RE_CAMP.findall(bucata)})})
    return out


def _declaratii_firmei(tip_firma):
    """Tipurile oferite firmei, cu denumirea oficială — același filtru ca `uc_declaratii.declaratii_tipuri` (forma firmei)."""
    import importlib
    from core import control_fiscal_api, declaratii_api
    forma = control_fiscal_api.neaplicabile_forma(tip_firma)
    tipuri = [t for t in declaratii_api.tipuri() if t not in control_fiscal_api._NEAP_PERSOANA_JURIDICA or t not in forma]
    out = []
    for tp in tipuri:
        try:
            den = (getattr(importlib.import_module("core." + tp), "DENUMIRE_OFICIALA", "") or "").strip()
        except ImportError:
            den = ""
        out.append({"tip": tp, "denumire": den})
    return out


def _potriveste(cuvinte, *texte):
    """Scorul potrivirii (0 = nu se potrivește): fiecare cuvânt căutat apare în texte; titlul (primul text) cântărește mai mult."""
    tot = normalizeaza(" ".join(x for x in texte if x))
    # fiecare cuvânt la începutul unui cuvânt din text („casa” găsește „Casă”, nu „încasare”)
    la_inceput = lambda c, t: re.search(r"(?:^|[^a-z0-9])" + re.escape(c), t) is not None   # noqa: E731
    if not all(la_inceput(c, tot) for c in cuvinte):
        return 0
    titlu = normalizeaza(texte[0] if texte else "")
    scor = 1
    if all(la_inceput(c, titlu) for c in cuvinte):
        scor += 4
    if titlu.startswith(cuvinte[0]):
        scor += 2
    return scor


def cauta(q, firma=None):
    """Rezultatele pentru textul `q`. `firma` = {"tenant_id", "tip_firma"} (citită de apelant, cu dreptul verificat),
    sau None (fără firmă în lucru: rezultatele de firmă cer întâi firma). [{fel, titlu, unde, …, actiune}], cel mult 12."""
    qn = normalizeaza(q)
    if len(qn) < 2:
        return []
    cuvinte = qn.split(" ")
    from core.migrare_api import regim_contabil
    regim = regim_contabil(firma.get("tip_firma")) if firma else None
    rez = []
    sinonim = SINONIME.get(qn)
    for c in carduri_firma():
        if regim and c["regim"] not in ("ambele", regim):
            continue
        s = _potriveste(cuvinte, c["titlu"], c["desc"], c["grup_titlu"]) + (6 if sinonim == c["cheie"] else 0)
        if s:
            rez.append((s, {"fel": "card", "cheie": c["cheie"], "titlu": c["titlu"], "unde": "Fereastra firmei › %s" % c["grup_titlu"],
                            "desc": c["desc"], "actiune": None}))
    if regim in (None, "dubla"):   # operațiunile speciale sunt ale partidei duble (cardul `operatiuni`, regim „dubla”)
        for o in operatiuni():
            s = _potriveste(cuvinte, o["titlu"], o["cat"], " ".join(o["campuri"]))
            if s:
                # ruta operației, nu acțiunea: acțiunea o compune ecranul cu `actiuneOp` (operatiuni_ecran.js), aceeași formă ca la butoane
                rez.append((s + 1, {"fel": "operatiune", "cheie": o["cheie"], "titlu": o["titlu"],
                                    "unde": "Operațiuni speciale › %s" % o["cat"], "ruta": o["ruta"], "actiune": None}))
    if firma:
        for d in _declaratii_firmei(firma.get("tip_firma")):
            s = _potriveste(cuvinte, d["tip"], d["denumire"])
            if s:
                rez.append((s + (3 if normalizeaza(d["tip"]) == qn else 0),
                            {"fel": "declaratie", "tip": d["tip"], "titlu": "%s — %s" % (d["tip"].upper(), d["denumire"]) if d["denumire"]
                             else d["tip"].upper(), "unde": "Declarații", "actiune": None}))
    rez.sort(key=lambda x: (-x[0], normalizeaza(x[1]["titlu"])))
    return [r for _s, r in rez][:12]   # cât încape în lista de sub căsuță fără derulare (nu e o valoare fiscală)


def cauta_pentru(q, tenant_id, ctx):
    """Corpul rutei `GET /cautare`: firma în lucru citită numai cu dreptul utilizatorului asupra ei (`_schema_sau_404`)."""
    firma = None
    if tenant_id is not None:
        from core import db, repo_firma_profil
        from core.uc_comun import _schema_sau_404
        schema = _schema_sau_404(ctx, tenant_id)
        with db.get_conn(schema) as conn:
            with conn.cursor() as cur:
                row = repo_firma_profil.profil_fiscal(cur)
        firma = {"tenant_id": tenant_id, "tip_firma": row[0] if row else None}
    return {"rezultate": cauta(q, firma), "firma": tenant_id}
