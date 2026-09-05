# -*- coding: utf-8 -*-
"""Garda R165/R166 — D406 raporteaza perioada pe care o ACOPERA, si o declara asa cum e.

CE APARA, cu instanta fiecare (etapa 2, lotul E, 05.09.2026):

  R165  — fereastra datelor era strict lunara, deci SAF-T-ul unei firme TRIMESTRIALE continea o
          luna din trei, in timp ce D300 si D394 pe acelasi trimestru le contineau pe toate.
          Temei: OPANAF 1783/2021 Anexa 4 pct.2-3 (D406 urmeaza perioada fiscala TVA; S, A si
          neplatitorii depun trimestrial).
  R165c — dupa largirea ferestrei, `SelectionCriteria` a ramas pe luna-ancora: fisierul cu
          iulie-septembrie declara despre sine „luna 9 - luna 9". Temei: `d406_schema_anaf.xlsx`
          5.12 — PeriodStart = „The first accounting period covered by SAF-T", PeriodEnd = „The
          last accounting period covered by the SAF-T".
  R166  — ruta de validare citea perioada din CORPUL cererii, dar D406 se cere pe `trim`; nu
          exista niciun corp care sa treaca si generarea si validarea, deci validarea D406 iesea
          `gri` intotdeauna. Perioada se ia de pe REZULTATUL generatorului.
  R166b — `HeaderComment` era constanta „L". Validatorul oficial, la prima lui rulare reala:
          „Tipul declaratiei L nu corespunde cu perioada declarata: 7.2026 - 9.2026".

ANTI-VACUU: fiecare aserţiune pe XML cere INTAI ca elementul sa existe. Proba care a ratat R165c
cauta `<SelectionStartDate>` — cealalta ramura a lui `<xs:choice>`, pe care fisierul n-o emite —,
n-o gasea, si raporta linistit `null`. Un gard cu domeniul de cautare gresit e verde despre o lume
pe care n-o vede.

STRUCTURA, NU TEXT (METODA §23): antetul se citeste ca ARBORE (`ElementTree`), iar contractul rutei
de validare ca AST — nu prin `"..." in sursa`.
"""
import ast
import os
from datetime import date

import pytest

from core import d406 as m

PROF_L = {"cui": "14399840", "nume": "FIRMA TEST SRL", "adresa": "Str. Test 1",
          "oras": "Bucuresti", "cod_postal": "010101", "baza_contabila": "A",
          "platitor_tva": True, "tip_decont": "L"}


def _prof(**kw):
    p = dict(PROF_L)
    p.update(kw)
    return p


def _fara_ns(eticheta):
    return eticheta.split("}")[-1]


def _antet(res):
    """Antetul ca ARBORE, nu ca text. Pica daca <Header> lipseste — fara el n-am ce masura."""
    import xml.etree.ElementTree as ET
    radacina = ET.fromstring(m.build_xml(res))
    for copil in radacina:
        if _fara_ns(copil.tag) == "Header":
            return copil
    pytest.fail("D406 fara <Header> — garda n-are pe ce aserta (aserţiune anti-vacuu)")


def _text(nod, cale):
    """Textul unui element, cautat pe nume fara namespace. None daca lipseste."""
    curent = nod
    for nume in cale.split("/"):
        gasit = None
        for copil in curent:
            if _fara_ns(copil.tag) == nume:
                gasit = copil
                break
        if gasit is None:
            return None
        curent = gasit
    return curent.text


def _res(prof, an, luna, di=None, ds=None):
    res = m.construieste(prof, an, luna, [], [], [], note=[], facturi_vanzare=[],
                         facturi_cumparare=[], plati=[])
    if di is not None:
        res.data_inceput, res.data_sfarsit = di, ds
    return res


# ── R165: fereastra urmeaza perioada fiscala TVA ───────────────────────────
@pytest.mark.parametrize("prof,asteptat", [
    (_prof(tip_decont="L"), (date(2026, 9, 1), date(2026, 10, 1))),
    (_prof(tip_decont="T"), (date(2026, 7, 1), date(2026, 10, 1))),
    # pct. 2 teza a doua: semestrial si anual depun TRIMESTRIAL
    (_prof(tip_decont="S"), (date(2026, 7, 1), date(2026, 10, 1))),
    (_prof(tip_decont="A"), (date(2026, 7, 1), date(2026, 10, 1))),
    # pct. 3: neplatitorul de TVA depune TRIMESTRIAL
    (_prof(platitor_tva=False, tip_decont="L"), (date(2026, 7, 1), date(2026, 10, 1))),
])
def test_fereastra_urmeaza_perioada_fiscala_tva(prof, asteptat):
    assert m.fereastra_d406(prof, 2026, 9) == asteptat


def test_fereastra_trimestriala_e_de_trei_ori_cea_lunara():
    """Calibrare pe EFECT, nu pe nume: T chiar acopera de trei ori cat L."""
    li, ls = m.fereastra_d406(_prof(tip_decont="L"), 2026, 9)
    ti, ts = m.fereastra_d406(_prof(tip_decont="T"), 2026, 9)
    assert ls == ts and (ls - li).days * 3 < (ts - ti).days + 3
    assert ti < li, "fereastra trimestriala trebuie sa inceapa mai devreme decat cea lunara"


# ── R166b: tipul depunerii se DERIVA din perioada acoperita ────────────────
@pytest.mark.parametrize("di,ds,cod", [
    (date(2026, 9, 1), date(2026, 9, 30), "L"),
    (date(2026, 7, 1), date(2026, 9, 30), "T"),
    (date(2026, 1, 1), date(2026, 12, 31), "A"),
])
def test_header_comment_derivat_din_perioada(di, ds, cod):
    assert m.header_comment(di, ds) == cod


def test_header_comment_nu_ghiceste_pe_o_intindere_necunoscuta():
    """FARA DEFAULT FISCAL TACIT: 2 luni n-au cod in nomenclator — se opreste, nu cade pe „L".

    Se asertaza pe CAMPURILE refuzului, nu pe propozitia lui: `IntinderNerecunoscuta` poarta
    ce a gasit (`luni`, `di`, `ds`), ce tipuri exista (`coduri`) si pe ce se sprijina
    (`temei`). O garda care ar cauta „2 luni" in text ar pazi formularea, nu faptul.
    """
    with pytest.raises(m.IntinderNerecunoscuta) as e:
        m.header_comment(date(2026, 8, 1), date(2026, 9, 30))
    refuz = e.value
    assert refuz.luni == 2
    assert (refuz.di, refuz.ds) == (date(2026, 8, 1), date(2026, 9, 30))
    assert set(refuz.coduri) == set(m.HEADER_COMMENT_PER.values())
    assert refuz.temei, "un refuz dintr-un modul care citeaza legea poarta temeiul"


# ── R165c: antetul declara perioada ACOPERITA, nu luna-ancora ──────────────
def test_antetul_declara_trimestrul_cand_fisierul_poarta_trimestrul():
    antet = _antet(_res(_prof(tip_decont="T"), 2026, 9,
                        date(2026, 7, 1), date(2026, 9, 30)))
    assert _text(antet, "SelectionCriteria/PeriodStart") == "7"
    assert _text(antet, "SelectionCriteria/PeriodStartYear") == "2026"
    assert _text(antet, "SelectionCriteria/PeriodEnd") == "9"
    assert _text(antet, "SelectionCriteria/PeriodEndYear") == "2026"
    assert _text(antet, "HeaderComment") == "T"


def test_antetul_lunar_ramane_neschimbat():
    """Cealalta directie a calibrarii: reparatia nu misca ce era corect."""
    antet = _antet(_res(_prof(tip_decont="L"), 2026, 9,
                        date(2026, 9, 1), date(2026, 9, 30)))
    assert _text(antet, "SelectionCriteria/PeriodStart") == "9"
    assert _text(antet, "SelectionCriteria/PeriodEnd") == "9"
    assert _text(antet, "HeaderComment") == "L"


def test_antetul_fara_fereastra_cade_pe_luna_ancora():
    """`d406_active`/`d406_stocuri` cheama `_header` fara fereastra — comportamentul de dinainte."""
    antet = _antet(_res(_prof(tip_decont="L"), 2026, 9))
    assert _text(antet, "SelectionCriteria/PeriodStart") == "9"
    assert _text(antet, "HeaderComment") == "L"


def test_perioada_declarata_si_tipul_depunerii_nu_pot_diverge():
    """Chiar regula pe care a numit-o validatorul ANAF, aserţiuata la noi in casa.

    Nu compara doua constante: recalculeaza tipul din perioada CITITA DIN XML si il confrunta cu
    cel scris in XML. Daca cineva scoate una din cele doua din aceeasi sursa, testul cade.
    """
    for tip, di, ds in (("L", date(2026, 9, 1), date(2026, 9, 30)),
                        ("T", date(2026, 7, 1), date(2026, 9, 30))):
        antet = _antet(_res(_prof(tip_decont=tip), 2026, 9, di, ds))
        ps = int(_text(antet, "SelectionCriteria/PeriodStart"))
        psy = int(_text(antet, "SelectionCriteria/PeriodStartYear"))
        pe = int(_text(antet, "SelectionCriteria/PeriodEnd"))
        pey = int(_text(antet, "SelectionCriteria/PeriodEndYear"))
        din_perioada = m.header_comment(date(psy, ps, 1), date(pey, pe, 28))
        assert _text(antet, "HeaderComment") == din_perioada


# ── R166: ruta de validare ia perioada de la GENERATOR, nu din corpul cererii ──
def test_ruta_de_validare_ia_perioada_de_pe_rezultat():
    """Pe AST, nu pe text: apelul `_duk.valideaza` primeste an/luna derivate din `res`.

    Instanta: cat timp le lua din `body`, D406 nu se putea valida NICIODATA din aplicatie —
    generarea cere `trim`, iar `luna` nu ajungea niciodata in corp.
    """
    cale = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
    arbore = ast.parse(open(cale, encoding="utf-8").read())
    fn = next((n for n in ast.walk(arbore)
               if isinstance(n, ast.FunctionDef) and n.name == "declaratie_valideaza"), None)
    assert fn is not None, "ruta `declaratie_valideaza` a disparut din main.py — garda ar fi vida"

    apel = None
    for n in ast.walk(fn):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "valideaza"):
            apel = n
            break
    assert apel is not None, "apelul catre validator nu mai e in ruta"

    chei = {k.arg: k.value for k in apel.keywords}
    assert {"an", "luna"} <= set(chei), "validatorul SAF-T cere an si luna: " + str(sorted(chei))

    # Valoarea trimisa validatorului trebuie sa fie legata de `res`. Se cauta NODUL `res` in
    # subarbore — nu sirul „res" in `ast.dump`: aia ar fi o aserţiune pe reprezentarea unei
    # structuri, adica exact forma pe care o interzice METODA §23.
    asignari = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            asignari[n.targets[0].id] = n.value
    for cheie in ("an", "luna"):
        v = chei[cheie]
        sursa = asignari.get(v.id, v) if isinstance(v, ast.Name) else v
        referinte = {n.id for n in ast.walk(sursa) if isinstance(n, ast.Name)}
        assert "res" in referinte, (
            "`%s` ajunge la validator fara sa treaca prin rezultatul generatorului; "
            "asa a stat D406 nevalidat (R166). Nume gasite: %s" % (cheie, sorted(referinte)))
