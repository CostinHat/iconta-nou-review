# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul „start”: prima intrare („Înainte de a începe”) și
cardurile „Primii pași”.

561: „Portal client, «Înainte de a începe»: «Salvează numărul» nu salvează niciun număr, deci clientul nu poate intra în portal; pagina nu
derulează.” 596: „Aceeași pagină, la cabinet nou: iese din ecran; motivul lui «NU s-a salvat» e scris mărunt, sub ecran; cardurile «Primii
pași» au prea mult text (cardul 1 e tăiat).”

Ce se păzește aici (proba de capăt la capăt, în browser, e `frontend_test/e2e/e2e_lot12_start.py`):
  1. drumul serverului al clientului din portal: numărul se salvează, alegerile se salvează, prima intrare e completă, cardul lui e făcut —
     pe rutele aplicației (`PUT /eu/telefon`, `PUT /eu/notificari`, `GET /eu/notificari`, `GET /eu/inceput`), cu sesiunea clientului;
  2. prima intrare e o FEREASTRĂ (încape pe ecran, corpul derulează el însuși) cu „Continuă în aplicație” și rândul „ce mai lipsește” în
     `.bara-fixa` (DS cap.6 v2.92), deschisă de aplicație (garda 325);
  3. pașii și nota fiecărui card „Primii pași” stau pliați în „Cum se face”, închis (DS cap.6 v2.95) — textul aprobat la 319 rămâne întreg;
  4. CLASA („pagina / fereastra nu derulează, iese din ecran”): sub `html, body { overflow-y: hidden }` (DS cap.22 §7) fiecare ecran pus
     direct în `#app` și fiecare strat fix pe tot ecranul trebuie să încapă / să deruleze el însuși.
Pe baza de TEST, într-o singură tranzacție anulată la final (`commit` = no-op). Temei: N/A — reguli de produs (CLAUDE.md §9).
"""
import contextlib
import html.parser
import io
import json
import os
import re
import subprocess

import pytest

from core import arbore_js as _aj
from core import db as _db

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCEPUT = os.path.join(RAD, "static", "js", "ecrane", "inceput.js")
CSS = os.path.join(RAD, "static", "stil.css")


def _citeste(cale):
    return io.open(cale, encoding="utf-8").read()


# Gărzile ecranelor asertează pe NOD (`core/arbore_js.py`): elementul HTML cu părintele, copiii și atributele lui, apelul cu argumentele
# lui — nu „șirul apare undeva în sursă”, care trece și dintr-un comentariu (`core/test_garzi_pe_text.py`).
_GOALE = {"br", "hr", "img", "input", "meta", "link", "source", "wbr", "col", "area", "base", "embed", "param", "track"}


class _Dom(html.parser.HTMLParser):
    """Arborele elementelor: {tag, at, copii, text}; rădăcina e un nod fără tag."""

    def __init__(self):
        super().__init__()
        self.rad = {"tag": None, "at": {}, "copii": [], "text": ""}
        self.stiva = [self.rad]

    def handle_starttag(self, tag, attrs):
        n = {"tag": tag, "at": dict(attrs), "copii": [], "text": ""}
        self.stiva[-1]["copii"].append(n)
        if tag not in _GOALE:
            self.stiva.append(n)

    def handle_endtag(self, tag):
        assert self.stiva[-1]["tag"] == tag, ("șablon dezechilibrat", tag, self.stiva[-1]["tag"])
        self.stiva.pop()

    def handle_data(self, data):
        self.stiva[-1]["text"] += data


def _desfasurat(t):
    """Textul unui șablon `…` cu fiecare `${…}` înlocuit de șabloanele imbricate din el (toate ramurile, alăturate); restul expresiei -> ""."""
    out = []
    for i, q in enumerate(t["quasis"]):
        out.append(q["value"]["cooked"] or "")
        if i < len(t["expressions"]):
            out += [_desfasurat(x) for x in _sabloane_de_varf(t["expressions"][i])]
    return "".join(out)


def _sabloane_de_varf(n):
    """Șabloanele `…` de sub `n` care nu stau în alt șablon de sub `n`, în ordinea din sursă."""
    out, stiva = [], [n]
    while stiva:
        x = stiva.pop()
        if isinstance(x, dict):
            if x.get("type") == "TemplateLiteral":
                out.append(x)
                continue
            stiva.extend(x.values())
        elif isinstance(x, list):
            stiva.extend(x)
    return sorted(out, key=lambda x: x["start"])


def _dom(sablon):
    p = _Dom()
    p.feed(_desfasurat(sablon))
    p.close()
    assert p.stiva == [p.rad], "șablon neînchis: %s" % [x["tag"] for x in p.stiva[1:]]
    return p.rad


def _elemente(n):
    """Elementele de sub `n` (fără `n`), în ordinea din sursă."""
    out = []
    for c in n["copii"]:
        out += [c] + _elemente(c)
    return out


def _clase(n):
    return {k for e in _elemente(n) for k in e["at"].get("class", "").split()}


def _unic(n, **at):
    """Singurul element de sub `n` cu atributele date (`clasa=` = una din clasele lui)."""
    clasa = at.pop("clasa", None)
    g = [e for e in _elemente(n) if all(e["at"].get(k) == v for k, v in at.items())
         and (clasa is None or clasa in e["at"].get("class", "").split())]
    assert len(g) == 1, ("se aștepta exact un element", clasa, at, len(g))
    return g[0]


def _sablonul_innerhtml(fn, cod, tinta):
    """Șablonul atribuit lui `tinta.innerHTML` în funcția `fn`; exact unul."""
    s = [a["right"] for a in _aj.noduri(fn, "AssignmentExpression")
         if cod(a["left"]) == tinta + ".innerHTML" and a["right"]["type"] == "TemplateLiteral"]
    assert len(s) == 1, (tinta, len(s))
    return s[0]


def _ruleaza_js(cale, fn, apeluri):
    """Rezultatele (JSON) ale apelurilor `apeluri` pe funcția PURĂ `fn` din `cale`, rulată în `node` cu sursa ei exactă."""
    u16 = _citeste(cale).encode("utf-16-le")
    sursa = u16[2 * fn["start"]:2 * fn["end"]].decode("utf-16-le")
    prog = "%s\nprocess.stdout.write(JSON.stringify([%s]));" % (sursa, ", ".join(apeluri))
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-500:]
    return json.loads(r.stdout)


# ── 1. clientul din portal: numărul și alegerile se salvează, prima intrare e completă (561) ───────────────────────────────────────────
class _ConnProxy:
    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        pass


@pytest.fixture
def client_portal(monkeypatch):
    """Un cabinet, o firmă și contul ei de client din portal, nou (fără telefon, fără alegeri salvate) — într-o tranzacție anulată."""
    from core import auth_api
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST LOT12 START') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email, password_hash, nume, rol, accounting_firm_id, activ) VALUES "
                        "('ztest_lot12_start_client@invalid', 'x', 'Client Probă', 'client', %s, true) RETURNING id", (firm,))
            uid = cur.fetchone()[0]
        tok = auth_api.sesiune_pentru_user(conn, uid)
        assert tok["ok"], tok

        @contextlib.contextmanager
        def _fake(schema=None):
            yield _ConnProxy(conn)
        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"conn": conn, "uid": uid, "firm": firm, "antet": {"Authorization": "Bearer " + tok["token"]}}
    finally:
        conn.rollback()
        p.putconn(conn)


def test_561_clientul_din_portal_isi_salveaza_numarul_si_trece_de_prima_intrare(client_portal):
    """561. Pașii clientului, pe rutele ecranului „Înainte de a începe”, cu sesiunea lui: prima intrare nu e făcută -> „Salvează numărul”
    cu 0700 000 123 -> numărul e în bază, în forma +40700000123 -> alegerile (email, bifele lui) -> prima intrare e completă, iar cardul
    lui de început („Cum afli noutățile de la cabinet”) e făcut.
    MUTAȚIE: `repo_cont_notificari.seteaza_telefonul` scrie NULL în locul numărului -> numărul nu se salvează -> pică."""
    import main
    from fastapi.testclient import TestClient
    c = TestClient(main.app, raise_server_exceptions=True)
    h = client_portal["antet"]
    st = c.get("/eu/notificari", headers=h)
    assert st.status_code == 200 and st.json()["complet"] is False, st.text
    r = c.put("/eu/telefon", json={"telefon": "0700 000 123"}, headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["telefon"] == "+40700000123", r.json()
    with client_portal["conn"].cursor() as cur:
        cur.execute("SELECT telefon FROM public.users WHERE id = %s", (client_portal["uid"],))
        assert cur.fetchone()[0] == "+40700000123"
    tipuri = {t["cheie"]: True for g in r.json()["grupuri"] for t in g["tipuri"]}
    assert set(tipuri) == {"pachet_lunar", "mesaj_cabinet"}, tipuri          # tipurile clientului (320)
    r = c.put("/eu/notificari", json={"canal": "email", "tipuri": tipuri}, headers=h)
    assert r.status_code == 200 and r.json()["complet"] is True, r.text
    inc = c.get("/eu/inceput", headers=h).json()
    assert [x["cheie"] for x in inc["carduri"]] == ["client"] and inc["toate_facute"] is True, inc


def test_561_numarul_gresit_e_refuzat_langa_camp_cu_motivul(client_portal):
    """561 / 596: un număr care nu e de telefon („722”) e refuzat NUMIT, cu câmpul lui (`not-telefon`) — ecranul îl pune lângă câmp și în
    caseta „NU s-a salvat.” de lângă buton (DS cap.6 v2.93 / v2.99); nimic nu se scrie.
    MUTAȚIE: `erori_campuri` scos din `_refuz_camp` -> refuzul fără câmp -> pică."""
    import main
    from fastapi.testclient import TestClient
    from core import uc_cont_notificari as U
    r = TestClient(main.app).put("/eu/telefon", json={"telefon": "722"}, headers=client_portal["antet"])
    assert r.status_code == 400, r.text
    d = r.json()["detail"]
    assert d["mesaj"] == U.MESAJ_TELEFON_INVALID and d["erori_campuri"] == [{"camp": "not-telefon", "mesaj": U.MESAJ_TELEFON_INVALID}], d
    with client_portal["conn"].cursor() as cur:
        cur.execute("SELECT telefon FROM public.users WHERE id = %s", (client_portal["uid"],))
        assert cur.fetchone()[0] is None


# ── 2. prima intrare: fereastră, acțiunea și rândul „ce mai lipsește” în bara fixă (561 + 596) ────────────────────────────────────────
def test_596_prima_intrare_e_o_fereastra_cu_continua_in_bara_fixa():
    """596: „iese din ecran”; 561: „pagina nu derulează”. Șablonul ecranului „Înainte de a începe”: stratul ferestrei (deschis de aplicație,
    `data-deschidere="aplicatie"`) -> `.fereastra` (#prima-intrare, dialog) -> antetul cu titlul -> `.fereastra-corp` (derulează el
    însuși), iar ULTIMUL lui copil e `.bara-fixa` cu rândul „ce mai lipsește” (#pi-motiv) și „Continuă în aplicație” (#pi-continua).
    MUTAȚIE: `<div class="bara-fixa">` -> `<div class="pi-bara">` -> pică (și e2e `test_def_596_*`: „Continuă” iese din ecran)."""
    arb, cod = _aj.arbore_js(INCEPUT)
    rad = _dom(_sablonul_innerhtml(_aj.functia(arb, "ecranPrimaIntrare"), cod, "radacina"))
    # stratul e singurul lucru pus în rădăcină, iar fereastra e singurul lui copil
    assert [(e["tag"], e["at"]) for e in rad["copii"]] == [("div", {"class": "fereastra-overlay", "data-deschidere": "aplicatie"})], rad
    strat = rad["copii"][0]
    assert len(strat["copii"]) == 1, strat["copii"]
    fereastra = strat["copii"][0]
    assert (fereastra["tag"], fereastra["at"].get("class"), fereastra["at"].get("id"), fereastra["at"].get("role"),
            fereastra["at"].get("aria-modal")) == ("div", "fereastra", "prima-intrare", "dialog", "true"), fereastra["at"]
    # corpul ferestrei (care derulează) e ultimul ei copil; ultimul copil al corpului e `.bara-fixa` (DS cap.6 v2.92)
    corp = fereastra["copii"][-1]
    assert (corp["tag"], corp["at"].get("class")) == ("div", "fereastra-corp"), "corpul ferestrei (care derulează) lipsește"
    bara = corp["copii"][-1]
    assert (bara["tag"], bara["at"]) == ("div", {"class": "bara-fixa"}), "„Continuă” și rândul de jos nu stau în `.bara-fixa` (DS cap.6 v2.92)"
    assert _unic(bara, id="pi-motiv")["tag"] == "p"
    continua = _unic(bara, id="pi-continua")
    # „Continuă” e ultimul element al barei: după el se închid numai bara, corpul, fereastra și stratul
    assert _elemente(bara)[-1] is continua and continua["tag"] == "button", _elemente(bara)[-1]
    # pagina veche, direct în #app (`class="prima-intrare"`), nu mai există: `prima-intrare` e numai id-ul ferestrei
    assert [e["at"].get("id") for e in _elemente(rad) if e["at"].get("id") == "prima-intrare"] == ["prima-intrare"]
    assert "prima-intrare" not in _clase(rad)
    # „Continuă” nu scrie nimic: nu e un buton de salvare (caseta „NU s-a salvat.” nu i se pune — api.js `refuzSalvare`)
    assert continua["at"].get("data-fara-actiune"), continua["at"]


def _butoane(mesaj):
    """Butoanele numite în mesaj, între ghilimelele românești."""
    return set(re.findall(r"„([^”]+)”", mesaj))


def test_561_randul_spune_ce_mai_lipseste_si_se_reface_dupa_orice_salvare():
    """561: „Salvează numărul” se făcea, dar „Continuă” rămânea blocat cu textul „se deblochează după ce salvezi numărul de telefon și
    alegerile de mai sus” — omul nu știa că mai are un „Salvează”, la capătul listei. Acum rândul din bară spune pasul care lipsește
    (fără număr / numărul salvat, alegerile nu / gata) și se reface după ORICE salvare reușită (`iconta:schimbare` + `dupaSalvare`).
    MUTAȚIE: ascultătorul `iconta:schimbare` scos -> pică."""
    arb, cod = _aj.arbore_js(INCEPUT)
    # rândul, pe cele trei stări, din funcția însăși (rulată): butoanele pe care le numește și locul lui „Salvează”
    gata, fara_numar, cu_numar = _ruleaza_js(INCEPUT, _aj.functia(arb, "ceMaiLipseste"), [
        'ceMaiLipseste({complet: true})', "ceMaiLipseste(null)", 'ceMaiLipseste({telefon: "0722000561"})'])
    assert _butoane(gata) == {"Continuă în aplicație"}, gata
    assert _butoane(fara_numar) == {"Continuă", "Salvează numărul", "Salvează"}, fara_numar
    assert _butoane(cu_numar) == {"Salvează", "Continuă"}, cu_numar
    assert {"0722000561"} <= set(cu_numar.split()), cu_numar   # numărul salvat e spus
    for m in (fara_numar, cu_numar):
        bucati = [b.strip(" .") for b in re.split(r"[;,]", m)]
        # „Salvează” e cel „la capătul listei” (al doilea buton, pe care omul nu-l vedea)
        assert _butoane(bucati[bucati.index("la capătul listei") - 1]) == {"Salvează"}, bucati
    e = _aj.functia(arb, "ecranPrimaIntrare")
    assert _aj.apeluri(e, cod, "window.addEventListener") == [('"iconta:schimbare"', "laSchimbare")]
    assert [a[1] for a in _aj.apeluri(e, cod, "panouNotificari")] == ["{ dupaSalvare: verifica }"]
    init = {d["id"]["name"]: d["init"] for d in _aj.noduri(e, "VariableDeclarator") if d["id"].get("type") == "Identifier"}
    assert _aj.apeluri(init["verifica"], cod, "ceMaiLipseste") == [("st",)]
    assert _aj.apeluri(init["laSchimbare"], cod, "verifica") == [("await stareaNotificarilor()",)]


# ── 3. cardurile „Primii pași”: pașii pliați în „Cum se face” (596) ─────────────────────────────────────────────────────────────────
def test_596_pasii_si_nota_cardului_stau_pliati_in_cum_se_face():
    """596: „cardurile «Primii pași» au prea mult text (cardul 1 e tăiat)”. În `htmlCard` (aceeași pe pagina principală și în „?”), lista
    pașilor (`inceput-pasi`) și nota (`inceput-nota`) stau într-un `<details class="dec-xml"><summary>Cum se face</summary>`, închis
    (fără `open`) — DS cap.6 v2.95; la vedere: titlul, „Ce faci aici”, „Cardul devine verde când …”, butoanele.
    MUTAȚIE: `<details class="dec-xml">` -> `<details class="dec-xml" open>` -> pică (și e2e: cardul 1 nu mai încape)."""
    arb, _cod = _aj.arbore_js(INCEPUT)
    ret = [r["argument"] for r in _aj.noduri(_aj.functia(arb, "htmlCard"), "ReturnStatement")
           if r["argument"] and r["argument"]["type"] == "TemplateLiteral"]
    card = _dom(ret[0])
    assert [e["tag"] for e in card["copii"]] == ["article"], card["copii"]
    det = [e for e in _elemente(card) if e["tag"] == "details"]
    assert [d["at"] for d in det] == [{"class": "dec-xml"}], [d["at"] for d in det]   # unul singur, închis (fără `open`)
    assert det[0]["copii"][0]["tag"] == "summary" and det[0]["copii"][0]["text"].strip() == "Cum se face", det[0]["copii"][0]
    assert _clase(det[0]) >= {"inceput-pasi", "inceput-nota"}, _clase(det[0])
    afara = {k for e in _elemente(card) if e not in [det[0]] + _elemente(det[0]) for k in e["at"].get("class", "").split()}
    assert not afara & {"inceput-pasi", "inceput-nota"}, afara
    assert afara >= {"inceput-ce", "inceput-verde", "inceput-butoane"}, afara


# ── 4. CLASA: ecranele din #app și straturile pe tot ecranul încap / derulează singure ──────────────────────────────────────────────
#: straturile fixe pe tot ecranul (`position: fixed; inset: 0` în stil.css) și panoul lor: cum încape conținutul pe ecran. Un strat nou
#: intră aici, clasificat, altfel testul pică. `None` = stratul însuși derulează (`overflow: auto`) sau nu ține text (lupa: o imagine).
STRATURI = {
    ".fereastra-overlay": ".fereastra-corp",      # .fereastra are max-height = ecranul, corpul derulează
    ".pacm-overlay": ".pacm-preview",             # povestea lunii: înălțimea ecranului, previzualizarea derulează
    ".rec-overlay": ".rec-modal-corp",            # Recomandă: max-height = ecranul, corpul derulează
    ".acces-overlay": ".acces-modal",             # intrarea în cont și „Înregistrează cabinetul tău”
    ".lupa-overlay": None,                        # poza mărită (o imagine, cu rotița pentru zoom)
    ".bun-venit-overlay": None,                   # stratul derulează (`overflow: auto`)
    ".reaut-overlay": ".reaut",                   # parola cerută peste ecran
}


def _reguli(css):
    return [(m.group(1).strip().split("\n")[-1].strip(), m.group(2)) for m in re.finditer(r"([^{}]+)\{([^}]*)\}", css)]


def _declaratii(css, selector):
    """Toate declarațiile regulilor al căror selector e exact `selector` (în afara @media)."""
    return " ".join(b for s, b in _reguli(css) if s == selector)


def test_clasa_straturile_pe_tot_ecranul_incap_si_deruleaza():
    """Clasa lui 561 / 596 („pagina nu derulează”, „iese din ecran”), pe straturile fixe: cu `html, body { overflow-y: hidden }`, un strat
    fix pe tot ecranul al cărui panou e mai înalt decât ecranul se taie sus și jos, fără derulare. Fiecare strat are aici panoul lui, iar
    panoul fie derulează el însuși (`max-height` + `overflow-y: auto`), fie stă într-o casetă cu `max-height` și derulează un copil al lui
    (fereastra, povestea, Recomandă). Un strat nou neclasificat pică.
    ROȘU ACUM pe `.acces-modal` (intrarea în cont / „Înregistrează cabinetul tău”, fără `max-height`: formularul de înregistrare — 10
    câmpuri + verificarea anti-roboți — iese din ecran la 1366×768) și pe `.reaut` (parola cerută peste ecran, fără `max-height`) —
    cerute în raport (stil.css, sesiunea principală)."""
    css = _citeste(CSS)
    gasite = set()
    for s, b in _reguli(css):
        if re.search(r"position:\s*fixed", b) and re.search(r"inset:\s*0", b) and s.startswith("."):
            gasite.add(s)
    assert gasite == set(STRATURI), ("straturi pe tot ecranul neclasificate / dispărute", gasite ^ set(STRATURI))
    rele = []
    for strat, panou in STRATURI.items():
        if panou is None:
            continue
        d = _declaratii(css, panou)
        parinte = {".fereastra-corp": ".fereastra", ".pacm-preview": ".pacm", ".rec-modal-corp": ".rec-modal"}.get(panou)
        if parinte:
            if not (re.search(r"max-height\s*:", _declaratii(css, parinte)) and re.search(r"overflow-y\s*:\s*auto", d)):
                rele.append((strat, parinte, panou))
        elif not (re.search(r"max-height\s*:", d) and re.search(r"overflow-y\s*:\s*auto", d)):
            rele.append((strat, panou))
    assert not rele, "straturi al căror conținut nu încape și nu derulează: %s" % rele


def test_clasa_ecranele_puse_direct_in_app_deruleaza():
    """Clasa lui 561 / 596 pe ecranele puse DIRECT în `#app` (nu în desktopul care derulează, `.desktop`, și nici într-un strat): pagina de
    intrare (login.js: `.pagina-bara` + `.pagina-corp`), „Activare cont” / „Parolă nouă” (app.js: `.pagina-login`), prima intrare (acum
    fereastră). Cu `html, body { overflow-y: hidden }`, ce trece sub ecran nu se mai ajunge. Regula: fiecare ecran pus în `#app` e un shell
    care derulează (`.desktop`) sau un strat (clasificat mai sus) — ori `#app` însuși derulează (`height: 100dvh; overflow-y: auto`), și
    atunci toate sunt acoperite.
    ROȘU ACUM: pagina de intrare și „Activare cont” / „Parolă nouă” — cerut în raport (`#app`, stil.css, sesiunea principală)."""
    css = _citeste(CSS)
    app = _declaratii(css, "#app")
    if re.search(r"(?<![-\w])height\s*:\s*100dvh", app) and re.search(r"overflow-y\s*:\s*auto", app):
        return
    rele = []
    for rad, _dirs, fis in os.walk(os.path.join(RAD, "static", "js")):
        for n in fis:
            if not n.endswith(".js"):
                continue
            cale = os.path.join(rad, n)
            s = _citeste(cale)
            if "radacina" not in s:
                continue
            for m in re.finditer(r"radacina\.innerHTML\s*=\s*`\s*<(\w+)[^>]*class=\"([^\"]+)\"", s):
                if m.group(2).split()[0] not in ("desktop",) + tuple(x[1:] for x in STRATURI):
                    rele.append((os.path.relpath(cale, RAD), m.group(2)))
            for m in re.finditer(r"radacina\.appendChild\((\w+)\)", s):
                c = re.search(r"%s\.className\s*=\s*\"([^\"]+)\"" % m.group(1), s)
                cls = c.group(1).split()[0] if c else "?"
                if cls not in ("desktop",) + tuple(x[1:] for x in STRATURI):
                    rele.append((os.path.relpath(cale, RAD), cls))
    assert not rele, "ecrane puse direct în #app, care nu derulează: %s" % sorted(set(rele))
