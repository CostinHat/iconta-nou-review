# -*- coding: utf-8 -*-
"""GARDĂ: ce datorează o microentitate la notele explicative — și de ce NU e „nimic".

**Garda de așteptare de dinainte și-a făcut treaba pe 31.08.2026**: a picat în ziua în care a apărut
o firmă cu două exerciții consecutive cu rulaje, exact cum fusese construită. Nu se șterge fără să
lase nimic în urmă — se înlocuiește cu ce s-a aflat atunci, fiindcă partea scumpă n-a fost condiția,
ci **citirea normei**.

**CE S-A AFLAT, și ar fi fost a treia concluzie inversată în trei zile.** Prima citire dă
**pct. 576 alin. (1)**: *„microentitățile nu au obligația elaborării notelor explicative"*. Concluzia
firească: firmele `micro` nu datorează nimic. **Falsă.** Punctul începe cu *«Cu respectarea
prevederilor alin. (2)»*, iar **alin. (2) e elidat în prima apariție a actului din corpus**. A doua
apariție îl are:

> **576. (2)** Microentitățile prezintă informațiile prevăzute la pct. 468 lit. a), d) și e) și
> pct. 491 alin. (2) lit. c).

Deci scutirea e **parțială**, iar garda asta ține minte exact care parte.

**CE NU PĂZEȘTE, declarat:** că aplicația produce notele — nu le produce, iar rândul e DESCHIS în
lista 3. Păzește **conținutul datorat**, ca el să nu se piardă și să nu fie recitit greșit.
"""
import io
import os
import re

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ACT = os.path.join(_RAD, "anaf_surse", "omfp_1802_2014_reglementari_consolidat.txt")

#: Ce datorează o microentitate, ca DATE. Nomenclator ÎNCHIS — dacă norma se schimbă, se schimbă și
#: aici, nu se adaugă tăcut.
DATORAT_DE_MICRO = (
    ("pct. 468 lit. a)", "politicile contabile adoptate, inclusiv bazele de evaluare"),
    ("pct. 468 lit. d)", "angajamente financiare, garanții, active și datorii contingente neincluse în bilanț"),
    ("pct. 468 lit. e)", "avansuri și credite acordate membrilor organelor de administrație, conducere și supraveghere"),
    ("pct. 491 alin. (2) lit. c)", "informații privind achizițiile propriilor acțiuni"),
)


def _text():
    if not os.path.exists(_ACT):
        pytest.skip("OMFP 1802/2014 nu e în corpus")
    return io.open(_ACT, encoding="utf-8", errors="replace").read()


def alineate(text=None, punct=576):
    """[{aparitie, alineate: {nr: text}}] — actul PARSAT pe punct și alineat.

    Aserțiunile se fac pe structura asta, nu pe fraze căutate în text: întrebarea reală e *„punctul
    576 are alineatul 2?"*, iar ea se poate parsa. `aparitie` e indexul, fiindcă actul apare de mai
    multe ori în același fișier, iar diferența dintre apariții e chiar lecția.
    """
    t = text if text is not None else _text()
    out = []
    for m in re.finditer(r"%d\. ?- ?\(1\)" % punct, t):
        seg = t[m.start():m.start() + 1200]
        # se oprește la punctul următor, ca să nu înghită vecinul
        urm = re.search(r"%d\. ?- ?\(?1?\)?" % (punct + 1), seg)
        if urm:
            seg = seg[:urm.start()]
        al = {}
        # `(?<!alin\. )` — o TRIMITERE arată identic cu un MARCAJ de alineat. Prima formă a
        # parserului citea „Cu respectarea prevederilor alin. (2)" din interiorul alin. (1) ca pe un
        # alineat nou, deci vedea (1) și (2) în amândouă aparițiile — inclusiv în cea care chiar
        # elidează alineatul. Ar fi trecut verde despre un act pe care nu-l citea.
        # Textul unui alineat CONȚINE paranteze — «pct. 468 lit. a), d) și e)». O primă formă îl
        # tăia la prima paranteză închisă și pierdea tocmai trimiterile, adică partea utilă.
        # Se citește până la MARCAJUL următor, nu până la primul `)`.
        _MARCAJ = r"(?<!alin\. )(?<!alin\.)\((\d)\)"
        for a in re.finditer(_MARCAJ + r"\s*(.{20,600}?)(?=" + _MARCAJ + r"|$)", seg, re.S):
            al[int(a.group(1))] = " ".join(a.group(2).split())
        out.append({"aparitie": len(out), "alineate": al})
    return out


def test_scutirea_microentitatilor_e_PARTIALA_nu_totala():
    """Miezul. Citit doar alin. (1), răspunsul ar fi «nu datorează nimic» — și ar fi greșit."""
    ap = alineate()
    assert ap, "punctul 576 nu se mai găsește în act — s-a schimbat norma sau s-a rupt corpusul"
    # Pe STRUCTURA: se cere ca vreo apariție a punctului să aibă AMBELE alineate. Prima formă a
    # probei căuta două fraze în text (clichet 50) — iar întrebarea reală e despre numerotarea
    # actului, care se parsează.
    cu_ambele = [a for a in ap if set(a["alineate"]) >= {1, 2}]
    assert cu_ambele, (
        "nicio apariție a pct. 576 n-are alineatul (2). Fără el, scutirea se citește ca TOTALĂ — "
        "exact concluzia inversată de pe 31.08. Alineate găsite pe apariție: %s"
        % [sorted(a["alineate"]) for a in ap])
    trimiteri = set(re.findall(r"pct\. (\d+)", cu_ambele[0]["alineate"][2]))
    assert trimiteri >= {"468", "491"}, (
        "alin. (2) nu mai trimite la pct. 468 și 491 — conținutul datorat s-a schimbat: %s"
        % sorted(trimiteri))


def test_alin_2_e_ELIDAT_la_prima_aparitie_si_intreg_la_a_doua():
    """Lecția, ca probă: actul apare de două ori în același fișier, iar prima apariție elidează
    tocmai partea care schimbă concluzia. Dacă vreodată **ambele** apariții îl au, proba asta cade —
    și e o veste bună care trebuie citită, nu o regresie."""
    ap = alineate()
    assert len(ap) >= 2, "actul nu mai apare de două ori — regula «caută a doua apariție» n-are obiect"
    assert 2 not in ap[0]["alineate"], (
        "prima apariție are acum și alin. (2) — corpusul s-a îmbunătățit; șterge proba asta")
    assert 2 in ap[1]["alineate"], (
        "a doua apariție nu mai are alin. (2) — atunci conținutul datorat nu se mai poate cita")


@pytest.mark.parametrize("temei,ce", DATORAT_DE_MICRO)
def test_fiecare_informatie_datorata_se_poate_CITI_in_act(temei, ce):
    """Anti-vacuu pe conținut: un temei citat fără ca textul lui să fie găsibil în corpus ar fi o
    trimitere la ceva ce nu se poate verifica."""
    t = _text()
    cuvant = ce.split(",")[0].split()[0].lower()
    assert cuvant[:9] in t.lower(), (
        "textul pentru %s nu se mai găsește în act (căutat după %r)" % (temei, cuvant))


def test_lista_datorata_are_exact_patru_pozitii():
    """Norma numește patru trimiteri. O a cincea adăugată tăcut ar fi o extindere fără temei."""
    assert len(DATORAT_DE_MICRO) == 4
    assert all(t.startswith("pct.") for t, _ in DATORAT_DE_MICRO)
