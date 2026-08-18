# -*- coding: utf-8 -*-
"""core/test_a11y_contrast_tokens.py — GARD: token-urile de culoare trec contrastul WCAG AA (4.5:1).

Audit a11y tenant_005 (17.08.2026): axe-core a gasit 5 perechi text/fundal sub 4.5:1 (alb pe --albastru
#3d8fd6 = 3.44; card verde #16a34a pe #e6f6ec = 2.94; card teal #0a807b pe #dff4f2 = 4.18; .camp-ajutor
albastru pe #e9edf3 = 2.93; edu #1d7a4d pe #dfe4ea = 4.16). Reparate la SURSA (stil.css --albastru +
.camp-ajutor; api.js CULORI_CARD; cabinet.js po-indicator). Gardul recalculeaza contrastul din sursa -
browser-free, ratchet pe token: daca cineva readuce o culoare sub 4.5:1, pica.
"""
import re
import glob
import pytest

_RAD = None


def _lum(hx):
    hx = hx.lstrip("#")
    if len(hx) == 3:
        hx = "".join(c * 2 for c in hx)
    r, g, b = [int(hx[i:i+2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    R, G, B = f(r), f(g), f(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _css():
    import os
    return open("static/stil.css", encoding="utf-8").read() if os.path.exists("static/stil.css") else ""


def _apijs():
    import os
    return open("static/js/api.js", encoding="utf-8").read() if os.path.exists("static/js/api.js") else ""


def _val(pattern, text):
    m = re.search(pattern, text)
    return m.group(1) if m else None


def test_token_albastru_alb_pe_el():
    css = _css()
    if not css:
        pytest.skip("stil.css absent")
    alb = _val(r"--albastru:\s*(#[0-9a-fA-F]{6})", css)
    assert alb, "--albastru negasit"
    r = _ratio("#ffffff", alb)
    assert r >= 4.5, "alb pe --albastru (%s) = %.2f < 4.5 (butoane/bara)" % (alb, r)


def test_token_camp_ajutor_pe_fundal_deschis():
    css = _css()
    if not css:
        pytest.skip("stil.css absent")
    # .camp-ajutor color, pe fundalul ferestrei #e9edf3 (cel mai deschis fundal pe care apare)
    m = re.search(r"\.camp-ajutor\s*\{[^}]*?color:\s*(#[0-9a-fA-F]{6})", css, re.S)
    assert m, ".camp-ajutor color negasit (nu mai e literal? verifica)"
    r = _ratio(m.group(1), "#e9edf3")
    assert r >= 4.5, ".camp-ajutor (%s) pe #e9edf3 = %.2f < 4.5" % (m.group(1), r)


def test_culori_card_fg_pe_bg():
    js = _apijs()
    if not js:
        pytest.skip("api.js absent")
    rele = []
    for m in re.finditer(r'\{\s*bg:\s*"(#[0-9a-fA-F]{6})",\s*fg:\s*"(#[0-9a-fA-F]{6})"\s*\}', js):
        bg, fg = m.group(1), m.group(2)
        r = _ratio(fg, bg)
        if r < 4.5:
            rele.append("CULORI_CARD fg %s pe bg %s = %.2f < 4.5" % (fg, bg, r))
    assert not rele, "\n".join(rele)


# [a11y contrast Control fiscal 18.08.2026 - audit tenant_006] Ecranul Control fiscal (panou #e9edf3) avea
# 17 perechi color-contrast sub 4.5 (axe): codurile declaratiilor (--albastru #347ab8 = 3.87) + sub-textul
# verdictelor (--gri-semafor #9aa3b2 = 2.16). Reparate SCOPED (token global neatins). Gardul recalculeaza
# din sursa contrastul culorilor scoped pe fundalul panoului.
_PANOU_CF = "#e9edf3"


def test_cf_incr_temei_contrast_pe_panou():
    css = _css()
    if not css:
        pytest.skip("stil.css absent")
    col = _val(r"\.cf-incr-temei\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})", css)
    assert col, ".cf-incr-temei color negasit"
    r = _ratio(col, _PANOU_CF)
    assert r >= 4.5, ".cf-incr-temei (%s) pe panoul Control fiscal %s = %.2f < 4.5 (sub-text verdicte)" % (col, _PANOU_CF, r)


def test_cf_coduri_declaratii_contrast_pe_panou():
    css = _css()
    if not css:
        pytest.skip("stil.css absent")
    col = _val(r"\.cf-incr-cap \.mig-sold-cont\s*\{\s*color:\s*(#[0-9a-fA-F]{6})", css)
    assert col, "culoarea codurilor declaratiilor (control fiscal) negasita"
    r = _ratio(col, _PANOU_CF)
    assert r >= 4.5, "codurile declaratiilor Control fiscal (%s) pe panoul %s = %.2f < 4.5" % (col, _PANOU_CF, r)


# [a11y contrast btn-link + summary 18.08.2026 - axe pe grila D301] .btn-link folosea #3d8fd6 (3.44 pe alb,
# 2.93 pe panoul #e9edf3) si .dec-xml summary --albastru #347ab8 (3.86 pe #e9edf3) - sub AA. -> #2f6fa6.
def test_btn_link_contrast_pe_alb_si_panou():
    css = _css()
    if not css:
        pytest.skip("stil.css absent")
    col = _val(r"\.btn-link\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})", css)
    assert col, ".btn-link color negasit"
    for bg in ("#ffffff", "#e9edf3"):
        r = _ratio(col, bg)
        assert r >= 4.5, ".btn-link (%s) pe %s = %.2f < 4.5 (butoane-link sterge/confirma/anuleaza)" % (col, bg, r)


def test_dec_xml_summary_contrast_pe_panou():
    css = _css()
    if not css:
        pytest.skip("stil.css absent")
    col = _val(r"\.dec-xml summary\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})", css)
    assert col, ".dec-xml summary color negasit"
    r = _ratio(col, "#e9edf3")
    assert r >= 4.5, ".dec-xml summary (%s) pe panoul #e9edf3 = %.2f < 4.5" % (col, r)


# [a11y contrast P3 18.08.2026 - audit tenant_006 strat solduri_parteneri] codul de cont (.mig-sold-cont)
# apare si in preview-urile de migrare (solduri/parteneri/plan) pe panoul #e9edf3, NU doar pe alb. Fix-ul
# Control fiscal a asumat "migrare = pe alb" si a lasat baza --albastru #347ab8 (3.86 pe #e9edf3). axe a
# gasit 5121/101 la 3.86 in preview-ul de parteneri -> baza dusa la #2f6fa6 (4.53 pe panou).
def test_mig_sold_cont_baza_contrast_pe_panou():
    css = _css()
    if not css:
        pytest.skip("stil.css absent")
    col = _val(r"(?m)^\.mig-sold-cont\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})", css)
    assert col, "culoarea de baza .mig-sold-cont nu e un hex literal (revenit la var(--albastru)? = 3.86 pe panou)"
    r = _ratio(col, _PANOU_CF)
    assert r >= 4.5, ".mig-sold-cont baza (%s) pe panoul de preview %s = %.2f < 4.5 (coduri de cont in migrare)" % (col, _PANOU_CF, r)
