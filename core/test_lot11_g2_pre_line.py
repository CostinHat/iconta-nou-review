# -*- coding: utf-8 -*-
"""[lotul 11, 22.10.2026, subagentul g2 — clasa găsită de W5 la `.dec-eroare`] O casetă care afișează TEXTUL SERVERULUI (`e.mesaj`,
`detaliu.mesaj`, …) păstrează rândurile lui.

DE CE. Campania 440 („toate erorile apar deodată, fiecare cu textul ei”) face ca refuzul serverului să vină rând cu rând: colectorul unic
(`core.erori.ErorileFormularului.detaliu`: „Formularul nu s-a salvat:\\n— …\\n— …”), `d212._motive`, `facturi_api.FacturaRefuzata`. DS
cap.6 v2.89: *„Un mesaj cu mai multe elemente vine cu rândurile despărțite (`\\n`), iar zonele de mesaj … le păstrează (`white-space:
pre-line`)”*. O casetă fără `pre-line` pune toate motivele într-un singur paragraf — W5 a văzut-o la `.dec-eroare` (refuzul D212).

CE PĂZEȘTE, structural, pe tot `static/js`: fiecare loc care scrie textul unui refuz într-un element — șablon
(`class="…">${esc(x.mesaj…` ) sau `el.textContent = x.mesaj` / `(x && x.mesaj)` — scrie într-un element care are, prin una din clasele
lui, o regulă CSS cu `white-space: pre-line` (sau `pre-wrap` / `pre`). Clasele de PROZĂ (`.ecran-nota`, `.ca-mesaj`, `.tip-desc`,
`.em-cui-stare`, …) nu primesc `pre-line` pe clasă: în sursă au paragrafe scrise pe mai multe rânduri (25 de locuri la 22.10.2026),
care s-ar rupe; acolo caseta refuzului primește și clasa `.pe-randuri` (DS cap.6).

CE NU VEDE, declarat: un text de refuz trecut printr-o variabilă intermediară (`const m = e.mesaj; el.textContent = m`), sau scris
într-un element al cărui `className` / `id` nu se poate rezolva static în același fișier (se raportează ca NEREZOLVAT, nu trece tăcut).
"""
import functools
import glob
import http.server
import io
import os
import re
import socketserver
import threading

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: textul serverului: `x.mesaj`, `(x && x.mesaj)`, `x.mesaj_lipsuri` (orice identificator — `e`, `err`, `det`, `detaliu`, `dep` …)
_MESAJ = r"\(?\s*[A-Za-z_$][\w$]*(?:\.|\s*&&\s*[A-Za-z_$][\w$]*\.)mesaj\w*"
_SABLON = re.compile(r'class="([^"]+)"[^<>]*>\$\{esc\(' + _MESAJ)
_TEXT = re.compile(r"(?m)^(.*?)\b([A-Za-z_$][\w$]*)\.textContent\s*=\s*" + _MESAJ)


def _css():
    return io.open(os.path.join(RAD, "static", "stil.css"), encoding="utf-8").read()


def clase_care_pastreaza(css=None):
    """Clasele care, SINGURE pe ultimul element al unui selector, au `white-space: pre-line | pre-wrap | pre` (`.a .b` -> b)."""
    css = re.sub(r"/\*.*?\*/", "", css if css is not None else _css(), flags=re.S)
    out = set()
    for sel, corp in re.findall(r"([^{}@]+)\{([^{}]*)\}", css):
        if not re.search(r"white-space\s*:\s*pre(-line|-wrap)?\s*(;|$)", corp.strip()):
            continue
        for s in sel.split(","):
            ultim = s.strip().split()[-1] if s.strip() else ""
            m = re.fullmatch(r"(?:[a-z0-9]*)((?:\.[\w-]+)+)", ultim)
            if m:
                out |= set(m.group(1).lstrip(".").split("."))
    return out


def _fisiere_js():
    return sorted(glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True))


def _clasa_variabilei(text, linia, var, rand):
    """Clasele elementului `var` din jurul liniei `linia`: `var.className = "…"` pe același rând, în următoarele 2 sau în cele 40 de dinainte, sau
    `var = ….querySelector("#id")` / `getElementById("id")` + `id="id"` cu `class="…"` în fișier."""
    m = re.search(r"\b%s\.className\s*=\s*[\"'`]([^\"'`]+)" % re.escape(var), rand)
    if m:
        return m.group(1).split()
    randuri = text.split("\n")
    for r in randuri[linia:linia + 2]:   # `el.className = …` pus imediat după text (calea erorii)
        m = re.search(r"\b%s\.className\s*=\s*[\"'`]([^\"'`]+)" % re.escape(var), r)
        if m:
            return m.group(1).split()
    for r in reversed(randuri[max(0, linia - 41):linia - 1]):
        m = re.search(r"\b%s\.className\s*=\s*[\"'`]([^\"'`]+)" % re.escape(var), r)
        if m:
            return m.group(1).split()
        m = re.search(r"\b%s\s*=\s*[\w.]*(?:querySelector\([\"'`]#|getElementById\([\"'`])([\w-]+)" % re.escape(var), r)
        if m:
            e = re.search(r'<\w+[^<>]*\bclass="([^"]+)"[^<>]*\bid="%s"|<\w+[^<>]*\bid="%s"[^<>]*\bclass="([^"]+)"'
                          % (re.escape(m.group(1)), re.escape(m.group(1))), text)
            if e:
                return (e.group(1) or e.group(2)).split()
            return None
    return None


def locuri():
    """[(fisier:linie, clasele elementului | None dacă nu se rezolvă)] — fiecare loc care scrie textul unui refuz al serverului."""
    out = []
    for f in _fisiere_js():
        text = io.open(f, encoding="utf-8").read()
        rel = os.path.relpath(f, RAD)
        for m in _SABLON.finditer(text):
            out.append(("%s:%d" % (rel, text[:m.start()].count("\n") + 1), m.group(1).split()))
        for m in _TEXT.finditer(text):
            linia = text[:m.start()].count("\n") + 1
            rand = text.split("\n")[linia - 1]
            out.append(("%s:%d" % (rel, linia), _clasa_variabilei(text, linia, m.group(2), rand)))
    return out


def test_fiecare_caseta_a_textului_serverului_pastreaza_randurile():
    pastreaza = clase_care_pastreaza()
    rele = ["  %-46s class=%r" % (loc, " ".join(cl or ["?"])) for loc, cl in locuri() if cl is None or not set(cl) & pastreaza]
    assert not rele, (
        "casete care afișează textul unui refuz al serverului FĂRĂ `white-space: pre-line` — un refuz cu mai multe motive (440: unul pe "
        "rând, `\\n`) s-ar citi într-un singur paragraf (DS cap.6 v2.89):\n" + "\n".join(rele)
        + "\n\nPune caseta pe o clasă de mesaj (`.msg-eroare` …) sau adaugă clasa `pe-randuri` (`static/stil.css`); o clasă de proză "
          "(`.ecran-nota`, `.ca-mesaj`, `.tip-desc`) nu primește `pre-line` pe clasă — are paragrafe scrise pe mai multe rânduri.")


def test_anti_vacuu_gardul_chiar_gaseste_casetele():
    """Un gard verde pe o listă goală nu păzește nimic: la 22.10.2026 erau peste 50 de locuri (șablon + `textContent`)."""
    toate = locuri()
    assert len(toate) > 40, "doar %d locuri găsite — expresiile au orbit" % len(toate)
    assert any(cl is not None and {"dec-eroare"} <= set(cl) for _l, cl in toate), "caseta lui W5 (.dec-eroare) nu mai e găsită"
    assert {"msg-eroare", "dec-eroare", "pe-randuri"} <= clase_care_pastreaza(), sorted(clase_care_pastreaza())


def test_calibrare_detectorul_vede_ambele_forme():
    css = ".a { color: red; }\n.b, .x .c { white-space: pre-line; }\n.d:has(> .e) { white-space: normal; }\n"
    assert clase_care_pastreaza(css) == {"b", "c"}
    assert _SABLON.search('<p class="ecran-nota">${esc((e && e.mesaj) || "x")}</p>')
    assert _SABLON.search('<div class="ca-mesaj">${esc(det.mesaj || "")}</div>')
    assert _TEXT.search("  st.textContent = (e && e.mesaj) || 'x';")
    assert not _SABLON.search('<p class="ecran-nota">${esc(x.nume)}</p>')


def test_clasele_de_proza_NU_primesc_pre_line_pe_clasa():
    """Perechea inversă: o regulă `pre-line` pe `.ecran-nota` / `.ca-mesaj` / `.tip-desc` ar rupe paragrafele scrise în sursă pe mai
    multe rânduri (supervizor.js, firme.js 4426, setari.js 168 …) — de aceea refuzul primește `.pe-randuri`, nu clasa întreagă."""
    assert not {"ecran-nota", "ca-mesaj", "tip-desc", "em-cui-stare"} & clase_care_pastreaza()


# ── PROBA în Chromium, pe `stil.css` REAL: un refuz cu `\n` în fiecare casetă ──────────────────────────────────────────────────────

class _Tacut(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(_Tacut, directory=RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop()
        srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    try:
        yield b, srv.server_address[1]
    finally:
        b.close()
        pw.stop()
        srv.shutdown()


#: refuzul colectorului unic (`ErorileFormularului.detaliu`), trei motive
REFUZ = "Formularul nu s-a salvat:\n— Data dispoziției lipsește.\n— Suma trebuie să fie pozitivă.\n— Categoria nu e în listă."

#: casetele, cu marcajul din JS-ul real (după reparație)
CASETE = [
    '<div class="dec-eroare"><b>x</b></div><div class="dec-avert-cap">%s</div>',
    '<div class="pacm-mail">%s</div>',
    '<div class="caseta-poarta"><div class="cp-mesaj">%s</div></div>',
    '<div class="val-lipsa val-depasita">%s</div>',
    '<div class="refuz-nevazut"><div class="rn-mesaj">%s</div></div>',
    '<div class="mig-eroare">%s</div>',
    '<p class="ecran-nota pe-randuri">%s</p>',
    '<div class="caseta-atentie"><div class="ca-mesaj pe-randuri">%s</div></div>',
    '<span class="tip-desc pe-randuri">%s</span>',
    '<div class="em-cui-stare em-cui-rau pe-randuri">%s</div>',
]


def test_proba_chromium_refuzul_vine_rand_cu_rand(browser):
    b, port = browser
    import html as _h
    corp = "".join('<div class="t" style="width:600px">%s</div>' % (c % _h.escape(REFUZ)) for c in CASETE)
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    try:
        pg.goto("http://127.0.0.1:%d/static/stil.css" % port)   # aceeași origine, ca `<link>` să încarce fișierul real
        pg.set_content('<!doctype html><html lang="ro"><head><meta charset="utf-8"><link rel="stylesheet" href="http://127.0.0.1:%d/'
                       'static/stil.css"></head><body>%s</body></html>' % (port, corp), wait_until="load")
        rez = pg.evaluate("""() => [...document.querySelectorAll('.t')].map((t) => {
            const el = t.lastElementChild.lastElementChild || t.lastElementChild;
            const r = document.createRange(); r.selectNodeContents(el);
            const linii = new Set([...r.getClientRects()].map((x) => Math.round(x.top)));
            return {cls: el.className, ws: getComputedStyle(el).whiteSpace, linii: linii.size, text: el.innerText}; })""")
    finally:
        pg.close()
    print("\nPROBA pre-line (Chromium, stil.css real):")
    for r in rez:
        print("  %-36s white-space=%-8s rânduri=%d" % (r["cls"], r["ws"], r["linii"]))
    rele = [r for r in rez if r["linii"] < 4 or r["ws"] not in ("pre-line", "pre-wrap")]
    assert not rele, "casete în care refuzul cu 4 rânduri NU vine rând cu rând: %s" % rele
