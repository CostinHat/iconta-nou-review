# -*- coding: utf-8 -*-
"""GARD DE PROPRIETATE (P2, 21.08.2026): un ECRAN nu scrie în COAJĂ. DESIGN_SYSTEM cap.25.

CONTRACTUL: proprietarul nu interpretează ce spune chiriașul; chiriașul nu se atinge de spațiu care nu
e al lui. Până azi, `cabinet.js` își lipea indicatorul și mesajul educativ direct în bara de stare, cu
`document.querySelector(".subbara").appendChild(...)`. Două consecințe, amândouă trăite:

  1. **Bara de stare nu-și mai controla propriul conținut.** Ăsta e mecanismul „indicatorului mincinos"
     (20.08): subbara spunea „Validarea în doi ✓" în timp ce un card de pe ACELAȘI ecran spunea altceva
     — un fapt, două randări, surse diferite.
  2. **Coaja nu se putea schimba** fără să cauți prin toate ecranele cine mai scrie în ea.

Chiriașii cer acum loc prin `static/js/coaja.js` (`cereLoc` / `pune` / `scoate`). Locul poate lipsi —
la rolul `client` nu există bară de stare — și chiriașul trebuie să suporte asta.

CE NU PĂZEȘTE: nu verifică sensul, doar accesul. Un ecran care primește un nod din coajă prin altă cale
(pasat ca argument) nu e prins — și nici n-ar trebui: contractul interzice să ȚI-L IEI, nu să-l
primești.
"""
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ECRANE = os.path.join(_RAD, "static", "js", "ecrane")

# Accesul la coajă, nu simpla pomenire a unei clase. `el.className = "subbara-edu"` e al chiriașului
# (își numește propriul nod); `document.querySelector(".subbara")` e coaja altcuiva.
_ACCES = re.compile(
    r"""document\s*\.\s*(?:querySelector|querySelectorAll)\s*\(\s*["'][^"']*\.(?:bara|subbara|bara3|bara-antet)\b"""
    r"""|document\s*\.\s*getElementById\s*\(\s*["'](?:nav-|clopot)""")

# Excepții MOTIVATE, ca `# upsert-ok:`. Goală azi — și e bine să rămână așa.
_EXCEPTII = {}


def _fara_comentarii(s):
    """Comentariile se scot ÎNAINTE de căutare. Prima versiune a gardului s-a aprins pe propriul
    comentariu explicativ («Înainte: querySelector(".subbara")») — aceeași greșeală ca gardul de ieri
    care nu deosebea afirmația de negația ei. Se repară gardul, nu se rescrie proza."""
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"(^|[^:])//[^\n]*", r"\1", s)


def _fisiere():
    return sorted(f for f in os.listdir(_ECRANE) if f.endswith(".js"))


def test_niciun_ecran_nu_scrie_in_coaja():
    """Miezul. Un ecran care ia singur spațiu din coajă rupe contractul din DS cap.25."""
    rele = []
    for f in _fisiere():
        src = _fara_comentarii(open(os.path.join(_ECRANE, f), encoding="utf-8").read())
        for m in _ACCES.finditer(src):
            if f in _EXCEPTII:
                continue
            ln = src[:m.start()].count("\n") + 1
            rele.append("  %s:%d  %s" % (f, ln, m.group(0)[:70]))
    assert not rele, (
        "ecrane care scriu direct în coajă:\n" + "\n".join(rele)
        + "\n\nChiriașul CERE loc, nu și-l ia: `coaja.pune(LOCURI.BARA_DE_STARE, \"id\", nod)`. "
        "Dacă accesul direct e chiar decizia corectă, adaugă fișierul în `_EXCEPTII` cu motivul scris.")


def test_contractul_chiar_e_folosit():
    """Anti-vacuu pe reparație: dacă nimeni nu mai cheamă `coaja`, gardul de mai sus trece pe gol —
    ar păzi absența accesului direct într-o lume în care nimeni nu mai pune nimic în bara de stare."""
    folosesc = [f for f in _fisiere()
                if "coaja.js" in open(os.path.join(_ECRANE, f), encoding="utf-8").read()]
    assert folosesc, "niciun ecran nu mai cere loc prin coaja.js — contractul e scris, dar nefolosit"


def test_proprietarul_isi_declara_locul():
    """Cealaltă jumătate: dacă navigatorul nu mai înregistrează locul, `cereLoc` întoarce mereu null
    și chiriașii dispar TĂCUT de pe ecran. Un contract are nevoie de ambele semnături."""
    nav = open(os.path.join(_RAD, "static", "js", "navigator.js"), encoding="utf-8").read()
    assert "inregistreazaLoc" in nav, "navigatorul nu mai declară niciun loc închiriabil"
    assert "BARA_DE_STARE" in nav, "bara de stare nu mai e declarată ca loc"


def test_gardul_chiar_vede_ecranele():
    """Anti-vacuu pe domeniu: dacă directorul se mută sau se golește, testul de mai sus trece pe gol."""
    fis = _fisiere()
    assert len(fis) >= 20, "prea puține ecrane văzute (%d) — verifică domeniul gardului" % len(fis)
    assert "cabinet.js" in fis


def test_exceptiile_nu_imbatranesc():
    """Anti-vacuu pe exceptare, ca la `PROZA_RESPINSA`: o excepție pentru un fișier care nu mai are
    acces direct e o notă despre o lume dispărută."""
    moarte = []
    for f in _EXCEPTII:
        p = os.path.join(_ECRANE, f)
        if not os.path.exists(p):
            moarte.append(f + " (fișier inexistent)")
            continue
        if not _ACCES.search(_fara_comentarii(open(p, encoding="utf-8").read())):
            moarte.append(f + " (nu mai are acces direct)")
    assert not moarte, "excepții care nu mai corespund — scoate-le: %s" % moarte


def test_comentariile_nu_declanseaza_gardul():
    """Legat, fiindcă s-a întâmplat: gardul trebuie să deosebească un ACCES de o POMENIRE. Altfel
    documentația care explică regula devine o încălcare a ei."""
    fals = '// Înainte: document.querySelector(".subbara") — explicație, nu acces\nconst a = 1;'
    assert not _ACCES.search(_fara_comentarii(fals))
    adevarat = 'const b = document.querySelector(".subbara");'
    assert _ACCES.search(_fara_comentarii(adevarat)), "gardul nu mai vede accesul real"


@pytest.mark.parametrize("clasa", ["subbara-edu", "bara-veriga", "subbara-firma"])
def test_numele_propriei_clase_nu_e_incalcare(clasa):
    """Contra-direcția: un chiriaș care își numește propriul nod `subbara-edu` NU atinge coaja.
    Fără asta, gardul ar cere redenumiri fără sens și s-ar dezactiva singur."""
    assert not _ACCES.search(_fara_comentarii('el.className = "%s";' % clasa))
