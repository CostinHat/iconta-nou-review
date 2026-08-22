# -*- coding: utf-8 -*-
"""GARDĂ: amprentele corpusului se verifică, nu doar se scriu. (22.08.2026)

DE CE. Interdicția 52 — *„un act din corpus al cărui text s-a modificat după aducere"* — avea până
acum un artefact (`<nume>.sha256`) și **niciun mecanism care să-l compare cu fișierul**. Amprenta era
o declarație, nu o probă. S-a văzut în ziua în care `legea_82_1991_consolidat.html` a apărut modificat
față de commit, cu 1629 de linii, **fără ca vreun script din tură să-l scrie**: nimic nu s-ar fi
aprins dacă nu mă uitam din întâmplare la `git status`.

CE FACE IMPOSIBIL: un fișier din corpus care s-a schimbat după ce i s-a luat amprenta · o amprentă
scrisă pentru un fișier care nu mai există · un `.sha256` gol sau cu altceva decât un hash.

CE NU FACE, declarat: nu spune că textul de pe SURSĂ s-a schimbat — pentru asta ar trebui
re-descărcat, iar pagina portalului nu e reproductibilă octet cu octet (URL-uri de CSS/JS versionate,
motiv pentru care actele aduse poartă și o amprentă pe TEXT, nu doar pe pagină). Răspunde la
întrebarea dinăuntru: *„fișierul din corpus e cel căruia i-am luat amprenta?"* Cine l-a schimbat, nu
spune — spune doar CĂ s-a schimbat, ceea ce e exact ce lipsea.
"""
import hashlib
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSE = os.path.join(RAD, "anaf_surse")


def _perechi():
    """[(fisier_amprenta, fisier_de_verificat)] pentru toate `<x>.sha256` din corpus."""
    out = []
    for f in sorted(os.listdir(SURSE)):
        if f.endswith(".sha256"):
            out.append((f, f[:-len(".sha256")]))
    return out


def test_gardul_chiar_vede_amprente():
    """ANTI-VACUU. Fără proba asta, un director redenumit ar face testele de mai jos să treacă pe
    zero perechi — interdicția 19, pe corpus în loc de cod."""
    p = _perechi()
    assert len(p) >= 100, (
        "doar %d amprente găsite în %s — ori s-a mutat corpusul, ori s-a rupt căutarea. "
        "Un gard care nu găsește nimic TRECE." % (len(p), SURSE))
    assert any(a.startswith("cod_fiscal") for a, _b in p)


def test_amprentele_au_forma_de_amprenta():
    rele = []
    for amp, _baza in _perechi():
        v = io.open(os.path.join(SURSE, amp), encoding="utf-8").read().strip()
        if not re.fullmatch(r"[0-9a-f]{64}", v.split()[0] if v.split() else ""):
            rele.append("  %s: %r nu e un sha256" % (amp, v[:40]))
    assert not rele, "amprente nevalide:\n" + "\n".join(rele)


def test_nicio_amprenta_orfana():
    """O amprentă pentru un fișier care nu mai există apără o lume care a plecat."""
    orfane = [a for a, b in _perechi() if not os.path.exists(os.path.join(SURSE, b))]
    assert not orfane, "amprente fără fișier pe disc: %s" % orfane


def test_corpusul_nu_s_a_schimbat_sub_amprenta():
    """INTERDICȚIA 52, prima dată cu mecanism. Compară, nu presupune."""
    rele = []
    for amp, baza in _perechi():
        cale = os.path.join(SURSE, baza)
        if not os.path.exists(cale):
            continue
        scris = io.open(os.path.join(SURSE, amp), encoding="utf-8").read().strip().split()[0]
        real = hashlib.sha256(io.open(cale, "rb").read()).hexdigest()
        if scris != real:
            rele.append("  %s: amprenta %s… ≠ conținutul %s…" % (baza, scris[:12], real[:12]))
    assert not rele, (
        "fișiere din corpus schimbate după ce li s-a luat amprenta (%d):\n%s\n"
        "Nu se repară rescriind amprenta. Întâi se află CE s-a schimbat: `git diff` pe fișier, și "
        "dacă textul e identic iar diferența e în chrome-ul paginii, se restaurează din commit."
        % (len(rele), "\n".join(rele)))
