# -*- coding: utf-8 -*-
"""CALIBRAREA instrumentului JS — scrisă ÎNAINTE de prima măsurătoare, nu după.

Interdicția 76 (*un instrument pe care stau măsurători, fără calibrare pe propriul mod de eșec*) are
patru instanțe în proiect și **toate au fost prinse târziu**. Cerința lui Costin, 23.08.2026: *„asta e
prima ocazie de a o aplica înainte, nu după."*

Cele șase moduri pe care un scan care citește JavaScript poate greși sunt enumerate în antetul lui
`core/scan_js_texte.py`. Aici fiecare are un caz. **Trei sunt ACOPERITE și probate; două sunt
NEACOPERITE și probate ca atare** — un mod de eșec declarat și demonstrat e o limită; unul declarat
și nedemonstrat e o speranță.
"""
import os

import pytest

from core import scan_js_texte as sc


def _scan(src):
    """Frazele văzute într-o sursă construită anume."""
    return [sc.normalizeaza(t) for t, _l in sc._siruri(sc._fara_comentarii(src))
            if sc.e_fraza_de_om(t)]


# ─────────────────────────────────────────── M1: template literals
def test_M1_backtick_e_vazut():
    """`Text ${x}` nu e prins de un regex pe ghilimele. Iar `${...}` trebuie normalizat, altfel
    aceeași frază cu variabile diferite apare ca două fraze."""
    a = _scan("const a = `Nu s-a putut salva ${nume} acum`;\n")
    b = _scan("const b = `Nu s-a putut salva ${alt} acum`;\n")
    assert a == b == ["Nu s-a putut salva · acum"], (a, b)


# ─────────────────────────────────────────── M2: comentarii
def test_M2_fraza_din_comentariu_NU_se_numara():
    """O frază dintr-un comentariu nu ajunge la om."""
    assert _scan("// Nu s-a putut salva firma acum\nlet x = 1;\n") == []
    assert _scan("/* Nu s-a putut salva firma acum */\nlet x = 1;\n") == []


def test_M2_slash_slash_DINTR_UN_SIR_nu_incepe_un_comentariu():
    """Cazul pe care un regex simplu îl greșește pe ORICE url: `https://`. Dacă `//` din șir ar
    începe un comentariu, restul fișierului ar dispărea din măsurătoare — tăcere, nu eroare."""
    src = 'const u = "https://exemplu.ro/x";\nconst m = "Nu s-a putut salva firma acum";\n'
    assert "Nu s-a putut salva firma acum" in _scan(src)


def test_M2_ghilimele_DINTR_UN_COMENTARIU_nu_deschid_un_sir():
    """Direcția inversă: dacă `"` dintr-un comentariu ar deschide un șir, tot ce urmează s-ar citi
    greșit."""
    src = '// aici era un "text" vechi\nconst m = "Nu s-a putut salva firma acum";\n'
    assert _scan(src) == ["Nu s-a putut salva firma acum"]


# ─────────────────────────────────────────── M3: zgomot
@pytest.mark.parametrize("zgomot", [
    '"#lista-firme"', '".ecran-nota"', '"https://anaf.ro/x"', '"firma_id"', '"click"',
    '"em-cui-stare em-cui-rau"', '"<div class=\\"x\\">"',
])
def test_M3_zgomotul_nu_intra(zgomot):
    """Selectoare, clase, chei, URL-uri, fragmente de markup — masa șirurilor. Dacă intră, îneacă
    semnalul; prima formă a euristicii le lăsa să treacă, măsurat înainte de a raporta cifra."""
    assert _scan("const x = %s;\n" % zgomot) == []


def test_M3_LIMITA_o_eticheta_de_un_cuvant_NU_e_vazuta():
    """Fals negativ DECLARAT, nu ascuns: euristica cere un spațiu. «Salvează» nu se vede."""
    assert _scan('const x = "Salvează";\n') == []


def test_M3_dar_o_fraza_scurta_cu_diacritice_E_vazuta():
    """Contra-direcția: pragul nu e atât de sus încât să taie frazele reale."""
    assert _scan('const x = "Cotă TVA %";\n') == ["Cotă TVA %"]


# ─────────────────────────────────────────── M4: concatenare (NEACOPERIT)
def test_M4_concatenarea_NU_e_vazuta_si_asta_se_demonstreaza():
    """Modul de eșec declarat în antet, probat: fraza există pentru om, nu pentru scan. De-aia cifra
    e un plafon inferior — și de-aia limita e scrisă, nu presupusă."""
    vazute = _scan('const m = "Nu s-a putut " + verb + " firma";\n')
    assert "Nu s-a putut · firma" not in vazute
    assert vazute == ["Nu s-a putut"], (
        "scanul vede doar BUCATA literală, nu fraza — exact ce declară M4: %r" % vazute)


# ─────────────────────────────────────────── M5: alt fișier (NEACOPERIT)
def test_M5_domeniul_e_DOAR_js_si_se_spune():
    """O frază care trăiește și în `.html` poate fi raportată drept «loc unic». Se probează pe
    domeniul real: scanul citește doar `.js`."""
    assert sc.RAD.endswith("static/js")
    fisiere = [f for _d, _s, fs in os.walk(sc.RAD) for f in fs]
    assert fisiere, "domeniul e gol"
    assert all(not f.endswith(".html") for f in fisiere), \
        "au apărut fișiere .html în domeniu — limita M5 s-a schimbat, actualizează antetul"


# ─────────────────────────────────────────── M6: anti-vacuu
def test_M6_scanul_chiar_vede_ceva():
    """Dacă mașina de stări sau filtrul de fișiere se rup, listele se golesc și scanul ar raporta
    «nicio duplicare» — verde din vacuitate, exact clasa interdicției 19."""
    inv = sc.inventar()
    assert len(inv) >= 800, "prea puține fraze văzute (%d) — scanul s-a rupt" % len(inv)
    fisiere = {loc[0] for locuri in inv.values() for loc in locuri}
    assert len(fisiere) >= 20, "prea puține fișiere văzute: %d" % len(fisiere)


def test_M6_duplicarea_chiar_se_detecteaza():
    """Anti-vacuu pe funcția care produce cifra: dacă gruparea s-ar rupe, `duplicate()` ar întoarce
    gol și ar raporta pace."""
    dup = sc.duplicate()
    assert len(dup) >= 50, "prea puține duplicări (%d) — gruparea s-a rupt?" % len(dup)
    assert any(len(loc) >= 10 for loc in dup.values()), \
        "nicio frază în 10+ locuri — normalizarea nu mai unește variantele"
