# -*- coding: utf-8 -*-
"""core/test_394_migrare_cum_se_face.py — deficiența 394, partea „Migrare cabinet” (decizia Costin 19.10.2026, verbatim în DECIZII
„Închiderea lotului 9”: „**394** (Migrare cabinet): «Instrucțiunile pliate» — pașii rămân în aceeași ordine; instrucțiunile devin
«Cum se face», pliate.”).

Ce fac imposibil:
- instrucțiunile de sub butoanele aplicațiilor (`TEXT_FARA_BUTON`, textul 270 b) deschise din nou pe ecran: ele stau într-un
  `<details class="dec-xml">` (toggle-ul secundar al aplicației, DS v2.54 / v2.83) cu titlul „Cum se face”, ÎNCHIS la randare;
- pașii (cei 12, `STRATURI`) mutați: ordinea și numerele 1..12 rămân cele dinaintea deciziei, iar meniul pașilor nu intră în pliere.
Temei: N/A — ecran (tooling). Proba în browser: `frontend_test/e2e/e2e_lot93d.py::test_def_394_*`.
"""
import os
import re
from html.parser import HTMLParser

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js", "ecrane", "migrare.js")

#: pașii Migrare cabinet, în ordinea de dinaintea deciziei 394 (aceeași listă ca `frontend_test/e2e/e2e_lot5_migrare.py::PASI`)
PASI = ["Firme", "Vector fiscal", "Solduri inițiale", "Solduri parteneri", "Salariați", "Asociați", "Mijloace fixe", "Istoric declarații",
        "Plan de conturi", "Import RIP (PFA)", "Articole și stoc inițial", "Rețete (HoReCa)"]


def _js():
    with open(JS, encoding="utf-8") as f:
        return f.read()


def _text_fara_buton():
    m = re.search(r"const TEXT_FARA_BUTON = `(.*?)`;", _js(), re.S)
    assert m, "TEXT_FARA_BUTON lipsește din migrare.js"
    return m.group(1)


class _Arbore(HTMLParser):
    """Strămoșii fiecărui element: (tag, atribute) -> lista strămoșilor, ca să știm ce stă în `<details>`."""
    GOALE = {"br", "img", "input", "hr", "meta", "link"}

    def __init__(self):
        super().__init__()
        self.stiva, self.elemente, self.text_summary = [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.elemente.append((tag, a, list(self.stiva)))
        if tag not in self.GOALE:
            self.stiva.append((tag, a))

    def handle_endtag(self, tag):
        while self.stiva:
            t, _ = self.stiva.pop()
            if t == tag:
                break

    def handle_data(self, data):
        if self.stiva and self.stiva[-1][0] == "summary":
            self.text_summary.append(data)


def test_instructiunile_stau_pliate_sub_cum_se_face():
    """Textul 270 b stă într-un `<details class="dec-xml">` închis, cu titlul „Cum se face”; nimic din el nu rămâne afară.
    MUTAȚIA: `<details class="dec-xml" id="mig-apl-cum">` -> `<details class="dec-xml" id="mig-apl-cum" open>` -> ROȘU (pliere deschisă)."""
    p = _Arbore()
    p.feed(_text_fara_buton())
    details = [(t, a) for t, a, _ in p.elemente if t == "details"]
    assert len(details) == 1, details
    t, a = details[0]
    assert (a.get("class") or "").split().count("dec-xml") == 1, a   # toggle-ul secundar (DS v2.54 / v2.83), zero clase noi
    assert "open" not in a, "„Cum se face” trebuie să fie pliat la randare: %s" % a
    assert "".join(p.text_summary).strip() == "Cum se face", p.text_summary
    # tot textul instrucțiunilor (paragrafele și lista) e în <details>; în afara lui nu rămâne niciun element
    afara = [(tg, at) for tg, at, stramosi in p.elemente if tg != "details" and not any(s[0] == "details" for s in stramosi)]
    assert not afara, "elemente din instrucțiuni în afara „Cum se face”: %s" % afara
    assert any(tg == "div" and at.get("id") == "mig-apl-text" for tg, at, _ in p.elemente)   # id-ul folosit de e2e 270 rămâne


def test_pasii_raman_in_aceeasi_ordine_si_nu_se_pliaza():
    """Decizia pliază NUMAI instrucțiunile: pașii au aceleași numere (1..12) și aceeași ordine, iar meniul lor (`#mig-meniu`) nu stă
    în pliere. MUTAȚIA: `nr:9, titlu:"Plan de conturi"` -> `nr:13, titlu:"Plan de conturi"` -> ROȘU."""
    js = _js()
    bloc = re.search(r"export const STRATURI = \[(.*?)\n\];", js, re.S).group(1)
    pasi = re.findall(r'nr:(\d+), titlu:"([^"]+)"', bloc)
    assert [t for _, t in pasi] == PASI, pasi
    assert [int(n) for n, _ in pasi] == list(range(1, len(PASI) + 1)), pasi
    corp = re.search(r'corp\.innerHTML = `\s*<div id="mig-aplicatii"></div>(.*?)`;', js, re.S).group(1)
    p = _Arbore()
    p.feed(corp)
    assert [(t, a.get("id")) for t, a, _ in p.elemente] == [("div", "mig-meniu")], corp   # meniul pașilor, fără pliere


# ── „Rânduri mai compacte” (a doua decizie 394) ──────────────────────────────────────────────────────────────────────────────────
CSS = os.path.join(RAD, "static", "stil.css")
#: bugetul ferestrei Migrare cabinet pe 1366×768 (măsurat în 9.1: 661 px), minus ce stă deasupra pașilor, numărat cu înălțimea de
#: rând cea mai mare a fontului (15 px × 1,36): corpul 24+24, butoanele aplicațiilor 40+6, nota celor inactive pe două rânduri 41+10,
#: „Cum se face” pliat 20+8 => 661 − 173 = 488 px pentru cei 12 pași. Proba în browser e `e2e_lot93d.py::test_def_394_*`.
BUGET_PASI = 488
RAND_TEXT = 21      # un rând de text de 15 px, rotunjit în sus (înălțimea „normal” cea mai mare dintre fonturile probabile)


def _px(bloc, selector, prop):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", bloc)
    assert m, "lipsește regula %s" % selector
    v = re.search(r"(?:^|;)\s*" + re.escape(prop) + r"\s*:\s*([^;]+)", m.group(1))
    assert v, "%s fără %s" % (selector, prop)
    return [float(x) for x in re.findall(r"([\d.]+)px", v.group(1))]


def _media_lat():
    css = open(CSS, encoding="utf-8").read()
    m = re.search(r"@media \(min-width: 761px\) \{\n(.*?)\n\}", css, re.S)
    assert m, "lipsește blocul ecranului lat pentru `.mig-op` (@media (min-width: 761px))"
    assert re.search(r"^\s*\.mig-op\s*\{", m.group(1), re.M), m.group(1)
    return css, m.group(1)


def test_pasii_compacti_incap_in_fereastra_laptopului():
    """Pe ecranul lat, cei 12 pași, fiecare pe un singur rând (titlul și descrierea alături, nowrap), încap în bugetul ferestrei de
    1366×768. MUTAȚIA: `  .mig-op { padding: 3px 12px; gap: 10px; }` -> `  .mig-op { padding: 13px 15px; gap: 10px; }` -> ROȘU."""
    _, b = _media_lat()
    pad = _px(b, ".mig-op", "padding")[0]
    gap = _px(b, ".mig-meniu", "gap")[0]
    nr = _px(b, ".mig-op-nr", "height")[0]
    icon = _px(b, ".mig-op-icon", "height")[0]
    badge = RAND_TEXT + 2 * _px(b, ".mig-badge", "padding")[0]
    assert re.search(r"\.mig-op-text\s*\{[^}]*flex-direction:\s*row", b), "titlul și descrierea nu mai stau pe același rând"
    assert re.search(r"\.mig-op-sub\s*\{[^}]*white-space:\s*nowrap", b) and re.search(r"\.mig-op-titlu\s*\{[^}]*white-space:\s*nowrap", b)
    rand = max(nr, icon, badge, RAND_TEXT) + 2 * pad + 1        # + bordura de 0,5 px sus și jos
    total = 12 * rand + 11 * gap
    assert total <= BUGET_PASI, "12 pași × %.1f px + 11 × %.0f px = %.1f px > %d px" % (rand, gap, total, BUGET_PASI)


def test_pe_telefon_randul_ramane_inalt():
    """Compactarea e numai în blocul ecranului lat: regula de bază a lui `.mig-op` (telefonul) păstrează rândul înalt — padding 13 px și
    iconița de 34 px (≥ 44 px cu cele două rânduri de text), ținta de atingere nu scade. MUTAȚIA: `@media (min-width: 761px) {` (al lui
    `.mig-meniu { gap: 2px; }`) scos, regulile compacte rămânând globale -> ROȘU."""
    css, b = _media_lat()
    baza = css.replace(b, "")
    assert _px(baza, ".mig-op", "padding")[0] >= 13 and _px(baza, ".mig-op-icon", "height")[0] >= 34
    assert re.search(r"\.mig-op-text\s*\{[^}]*flex-direction:\s*column", baza)
