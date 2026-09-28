# -*- coding: utf-8 -*-
"""GARD [P13c, 28.09.2026, interdictiile 27+31]: verdictul din stare are UN SINGUR punct in frontend.

Instanta reala: `static/js/ecrane/portal.js` initializa "pa-verde"/"Totul e la zi" din OFICIU si-l
suprascria doar pe rosu/galben/gri; `uc_portal.portal_acasa` trimite `stare=rez.get("stare")`, care poate
fi None -> patronul vedea VERDE fara temei. Fiecare tura anterioara (P13a/P13b) a ratat urmatoarea forma;
de aceea inchiderea e STRUCTURALA, nu forma-cu-forma:

  `static/js/ecrane/verdict.js` e PUNCTUL UNIC. Verde EXPLICIT -> text pozitiv (VERDICT_POZITIV). Gri,
  ABSENT (null/undefined) sau NECUNOSCUT -> gri, "nu se poate verifica". Rosu/galben raman la apelant.

Textele de verdict pozitiv traiesc DOAR in verdict.js; oriunde altundeva in static/js sunt interzise (gard
mecanic mai jos). NU e in domeniu verdictul din flag boolean `ok` (firme.js reconciliere) — acela e o stare
EXPLICITA, nu absenta/necunoscut (calibrat GOOD si in P13b).
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js")
PUNCT = os.path.join(JS, "ecrane", "verdict.js")


def _sursa(cale):
    return io.open(cale, encoding="utf-8").read()


def _fraze_pozitive():
    """Valorile din VERDICT_POZITIV, citite din punctul unic."""
    src = _sursa(PUNCT)
    m = re.search(r"VERDICT_POZITIV\s*=\s*\{([^}]*)\}", src)
    assert m, "verdict.js: VERDICT_POZITIV n-a fost gasit — punctul unic a disparut sau s-a redenumit"
    return re.findall(r':\s*"([^"]+)"', m.group(1))


def _fisiere_js():
    for root, _, fs in os.walk(JS):
        for f in fs:
            if f.endswith(".js"):
                yield os.path.join(root, f)


def test_ANTI_VACUU_punctul_unic_are_frazele():
    fraze = _fraze_pozitive()
    assert len(fraze) >= 4, "verdict.js: sub 4 fraze de verdict — parserul s-a rupt, gardul ar trece in gol: %r" % fraze


def test_frazele_verdict_traiesc_DOAR_in_punctul_unic():
    """Fiecare text de verdict pozitiv apare ca literal DOAR in verdict.js. Un text mutat afara -> rosu."""
    fraze = _fraze_pozitive()
    vinovati = []
    for cale in _fisiere_js():
        if os.path.abspath(cale) == os.path.abspath(PUNCT):
            continue
        src = _sursa(cale)
        rel = os.path.relpath(cale, RAD)
        for fr in fraze:
            if fr in src:
                vinovati.append("%s: %r" % (rel, fr))
    assert not vinovati, ("text de verdict pozitiv in afara punctului unic (verdict.js) — 27+31:\n"
                          + "\n".join("  " + v for v in vinovati))


def test_verdictDinStare_NU_da_verde_pe_necunoscut():
    """Structural: pozitivul apare DOAR sub `stare === \"verde\"`; caderea (gri/absent/necunoscut) da gri.
    Mutatie: o stare necunoscuta tratata ca verde (fallthrough pozitiv) -> rosu."""
    src = _sursa(PUNCT)
    assert re.search(r'if \(stare === "verde"\) return \{ pozitiv: true', src), \
        "verdict.js: ramura pozitiva nu mai e gardata pe stare === verde"
    n = src.count("pozitiv: true")
    assert n == 1, "verdict.js: `pozitiv: true` apare de %d ori — verdele nu mai e UNIC pe verde explicit" % n
    assert re.search(r'return \{ pozitiv: false, gri: true, titlu: VERDICT_GRI \}', src), \
        "verdict.js: caderea (gri/absent/necunoscut) nu mai intoarce gri VERDICT_GRI"
