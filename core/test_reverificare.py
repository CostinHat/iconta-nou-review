# -*- coding: utf-8 -*-
"""GARD [31.08.2026]: categoria de reverificare se CALCULEAZĂ, iar necunoscutul rămâne necunoscut.

Interdicția **55** măsura, pe 23.08: *„53 din 53 fără categorie de reverificare — fiindcă **câmpul nu
există**."* Exista un prag global unic (6 luni) pentru tot. Categoria e acum calculată din două axe
mecanice, iar tabelul 3×3 de praguri e decizia lui Costin din aceeași zi.

**REGULA CARE GUVERNEAZĂ GARDUL** *(Costin, 31.08)*: *„perechile neconfruntabile primesc NECUNOSCUT
declarat. **Orice implicit minte** — STABIL tăcut, VOLATIL zgomotos."* De aceea testul central nu e
că fiecare temei are o clasă, ci că **niciun necunoscut nu primește prag**.

CE FACE IMPOSIBIL:
  1. un prag atribuit unei perechi pe care instrumentul n-a putut-o citi;
  2. un tabel de praguri incomplet sau ne-monoton — mai volatil trebuie să însemne mai des, iar mai
     grav (DEPUS) trebuie să însemne mai des, altfel axa nu mai are sens;
  3. o clasificare care se mută tăcut: distribuția e pinată;
  4. o valoare care ar deveni verificată **mai rar** decât azi, fără ca cineva s-o decidă.

CE NU FACE, declarat:
  - **nu verifică dacă marcajul atinge VALOAREA** — un articol modificat la alin. (9) e clasat
    volatil chiar dacă valoarea stă la alin. (2). Frecvența e **plafon SUPERIOR** al volatilității
    reale, direcție aleasă deliberat: mai des verificat, nu mai rar;
  - **nu poate atribui `INFORMATIV`** — v. antetul modulului. Clasa e declarată **vidă**, iar testul
    de mai jos o cere vidă, ca absența ei să fie o afirmație, nu o tăcere.
"""
import datetime
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import reverificare as R  # noqa: E402

#: Distribuția măsurată pe `846e118`. Pinată: o mutare tăcută a clasificării e o mutare a pragurilor
#: de reverificare, adică a cât de des se uită cineva la o valoare fiscală.
DISTRIBUTIE = {
    ("VOLATIL", "DEPUS"): 9,
    ("STABIL", "DEPUS"): 12,
    ("MISCATOR", "CALCULAT"): 2,
    ("MISCATOR", "NECUNOSCUT"): 1,
    ("NECUNOSCUT", "NECUNOSCUT"): 10,
}

_AZI = datetime.date(2026, 8, 31)


def _d(*perechi):
    return [datetime.date(a, l, 1) for a, l in perechi]


# ── TABELUL ────────────────────────────────────────────────────────────────────────────────────

def test_tabelul_de_praguri_e_COMPLET():
    lipsa = [(f, c) for f in ("VOLATIL", "MISCATOR", "STABIL")
             for c in ("DEPUS", "CALCULAT", "INFORMATIV") if (f, c) not in R.PRAGURI]
    assert not lipsa, "combinații fără prag în tabel: %s" % lipsa
    assert len(R.PRAGURI) == 9, "tabelul are %d căsuțe, nu 9" % len(R.PRAGURI)


def test_tabelul_e_MONOTON_pe_amandoua_axele():
    """Dacă mai volatil nu înseamnă mai des, axa A n-are sens; dacă mai grav nu înseamnă mai des,
    axa B n-are sens. Se cere pe **structura tabelului**, nu pe valorile lui: o rescriere care
    păstrează cifrele dar le încurcă ordinea ar trece un test de egalitate și ar pica aici."""
    for c in ("DEPUS", "CALCULAT", "INFORMATIV"):
        v, m, s = R.PRAGURI[("VOLATIL", c)], R.PRAGURI[("MISCATOR", c)], R.PRAGURI[("STABIL", c)]
        assert v <= m <= s, "axa A ne-monotonă pe %s: VOLATIL %d, MISCATOR %d, STABIL %d" % (c, v, m, s)
    for f in ("VOLATIL", "MISCATOR", "STABIL"):
        d, cc, i = (R.PRAGURI[(f, "DEPUS")], R.PRAGURI[(f, "CALCULAT")],
                    R.PRAGURI[(f, "INFORMATIV")])
        assert d <= cc <= i, "axa B ne-monotonă pe %s: DEPUS %d, CALCULAT %d, INFORMATIV %d" % (f, d, cc, i)


# ── AXA A: frecvența ───────────────────────────────────────────────────────────────────────────

def test_frecventa_CALIBRARE_pe_cele_trei_clase():
    assert R.frecventa([], _AZI) == "STABIL"
    assert R.frecventa(_d((2019, 3), (2018, 5)), _AZI) == "STABIL", "marcaje vechi ies din fereastră"
    assert R.frecventa(_d((2026, 3)), _AZI) == "MISCATOR"
    assert R.frecventa(_d((2026, 3), (2026, 7)), _AZI) == "MISCATOR", "două în același an"
    assert R.frecventa(_d((2024, 3), (2026, 7)), _AZI) == "VOLATIL", "doi ani distincți"


def test_frecventa_GAURA_din_tabel_e_astupata_DECLARAT():
    """Trei modificări în ACELAȘI an nu intră în niciunul dintre cele trei rânduri, cum sunt scrise.
    Instrumentul alege **VOLATIL** — direcția care verifică mai des. *Testul există ca alegerea să
    fie o decizie scrisă, nu un efect colateral al ordinii de `if`-uri.*"""
    assert R.frecventa(_d((2026, 1), (2026, 4), (2026, 7)), _AZI) == "VOLATIL"


def test_frecventa_FEREASTRA_chiar_taie():
    """Direcția inversă: dacă fereastra n-ar tăia, orice articol vechi ar părea volatil pe vecie."""
    vechi = _d((2010, 1), (2012, 1), (2015, 1))
    assert R.frecventa(vechi, _AZI) == "STABIL", "fereastra de %d ani nu taie" % R.FEREASTRA_ANI
    assert R.frecventa(vechi + _d((2025, 6), (2026, 6)), _AZI) == "VOLATIL"


# ── NECUNOSCUT NU PRIMEȘTE PRAG ────────────────────────────────────────────────────────────────

def test_niciun_NECUNOSCUT_nu_primeste_prag():
    """Miezul regulii lui Costin. Un implicit aici ar fi invizibil și ar minți în amândouă
    direcțiile: STABIL tăcut (prag lung, valoare nesupravegheată) sau VOLATIL zgomotos."""
    rele = [(x["temei"], x["frecventa"], x["consecinta"], x["prag_luni"])
            for x in R.inventar(_AZI)
            if (x["frecventa"] == "NECUNOSCUT" or x["consecinta"] == "NECUNOSCUT")
            and x["prag_luni"] is not None]
    assert not rele, "perechi NECUNOSCUT cu prag atribuit: %s" % rele


def test_fiecare_NECUNOSCUT_isi_scrie_MOTIVUL():
    """Un necunoscut fără motiv e o tăcere care arată ca un răspuns."""
    fara = [x["temei"] for x in R.inventar(_AZI)
            if (x["frecventa"] == "NECUNOSCUT" or x["consecinta"] == "NECUNOSCUT") and not x["motiv"]]
    assert not fara, "perechi NECUNOSCUT fără motiv scris: %s" % fara


def test_fiecare_pereche_CONFRUNTABILA_are_prag():
    """Direcția inversă: `NECUNOSCUT` nu are voie să devină o scuză confortabilă. Dacă amândouă axele
    se pot citi, pragul e obligatoriu."""
    fara = [x["temei"] for x in R.inventar(_AZI)
            if x["frecventa"] != "NECUNOSCUT" and x["consecinta"] != "NECUNOSCUT"
            and x["prag_luni"] is None]
    assert not fara, "perechi complet clasificate, dar fără prag: %s" % fara


# ── CLASA DECLARATĂ VIDĂ ───────────────────────────────────────────────────────────────────────

def test_INFORMATIV_e_declarat_VID_si_chiar_e():
    """`dependenti_act` vede funcții Python, nu ecrane, deci nu poate deosebi «intră într-o cifră
    arătată omului» de «apare ca informație». Clasa e declarată vidă în antetul modulului; testul o
    cere vidă, ca absența ei să fie **o afirmație**, nu o tăcere. Ziua în care apare o cale de a o
    atribui, testul ăsta cade — și e corect să cadă."""
    inform = [x["temei"] for x in R.inventar(_AZI) if x["consecinta"] == "INFORMATIV"]
    assert not inform, (
        "s-a atribuit INFORMATIV: %s. Dacă e intenționat, scrie CUM se deosebește mecanic de "
        "CALCULAT și schimbă testul — clasa era declarată vidă tocmai fiindcă nu se putea." % inform)


# ── DISTRIBUȚIA NU SE MUTĂ TĂCUT ───────────────────────────────────────────────────────────────

def test_ANTI_VACUU_si_distributia_pinata():
    inv = R.inventar(_AZI)
    assert len(inv) >= 30, "[anti-vacuu] doar %d temeiuri — domeniul s-a rupt" % len(inv)
    clasificate = [x for x in inv if x["prag_luni"] is not None]
    assert len(clasificate) >= 20, (
        "[anti-vacuu] doar %d temeiuri clasificate complet — dacă aproape totul e NECUNOSCUT, "
        "gardul de mai sus trece pe o mulțime goală" % len(clasificate))
    acum = R.pe_clasa(inv)
    assert acum == DISTRIBUTIE, (
        "clasificarea s-a mutat:%s  acum:  %s%s  pinat: %s%s"
        "O mutare aici e o mutare a pragurilor de reverificare — adică a cât de des se uită cineva "
        "la o valoare fiscală. Dacă e intenționată, pinează noua distribuție."
        % (chr(10), dict(sorted(acum.items())), chr(10), dict(sorted(DISTRIBUTIE.items())), chr(10)))


def test_nicio_valoare_nu_devine_verificata_MAI_RAR():
    """Pragul global de azi e 6 luni. Trecerea la praguri per-articol are voie să strângă, nu să
    slăbească — iar dacă vreodată slăbește, e o decizie, nu un efect colateral. *Azi: 9 mai strict,
    0 mai larg.*"""
    d = R.fata_de_pragul_global(azi=_AZI)
    assert d["mai_larg"] == 0, (
        "%d valori ar fi verificate MAI RAR decât azi: asta cere o decizie scrisă, nu un tabel. %s"
        % (d["mai_larg"], d))
    assert d["mai_strict"] > 0, (
        "[anti-vacuu] nicio valoare nu se strânge — tabelul n-ar schimba nimic, deci n-ar fi "
        "reparat interdicția 55: %s" % d)
