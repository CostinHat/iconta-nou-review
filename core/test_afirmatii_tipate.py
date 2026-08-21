# -*- coding: utf-8 -*-
"""CLICHET: afirmațiile despre datele firmei nu mai pot fi proză. (P8, 21.08.2026)

DECIZIA (Costin, 21.08): afirmațiile despre datele firmei sunt OBIECTE cu toate atributele, nu
șiruri — și se aplică în TOATĂ aplicația, inclusiv validărilor de rând la import.

Până azi, decizia trăia pe UN ecran: `core/afirmatii.py` avea exact un consumator de producție,
`control_fiscal_api`. Restul aplicației producea proză în dicționare. O regulă scrisă și nepăzită
e o intenție.

CLICHET, nu xfail: numărul netipatelor din fiecare fișier poate SCĂDEA, niciodată crește. Un fișier
convertit dispare din baseline și nu se mai poate întoarce. Un fișier NOU care produce afirmații
netipate pică din prima — n-are intrare în baseline.

CE NU PĂZEȘTE. Că textul e bun. Că `fel`-ul ales e cel potrivit. Că domeniul e corect completat.
Alea sunt gărzile de conținut (`test_afirmatii.py` verifică nomenclatorul și câmpurile cerute).
Gardul de aici păzește un singur lucru: că afirmația E un obiect.
"""
import pytest

from core import scan_afirmatii as s

# Măsurat 21.08.2026: 120 afirmații netipate în clasele A (verdict) și C (import), în 30 de fișiere.
# Fiecare linie e o DATORIE, nu o normă. Se coboară; nu se ridică.
BASELINE = {
    "core/control_incrucisat.py": 27,
    "main.py": 13,
    "core/salariati_import_api.py": 8,
    "core/d390.py": 7,
    "core/istoric_declaratii_import_api.py": 7,
    "core/reconciliere.py": 6,
    "core/rip_migrare_api.py": 6,
    "core/mijloace_fixe_import_api.py": 5,
    "core/articole_import_api.py": 3,
    "core/control_fiscal_api.py": 3,
    "core/d100_reconciliere.py": 3,
    "core/firma_profil_api.py": 3,
    "core/raportari_ai.py": 3,
    "core/asociati_import_api.py": 2,
    "core/d112_reconciliere.py": 2,
    "core/d205_reconciliere.py": 2,
    "core/d300_reconciliere.py": 2,
    "core/d301_reconciliere.py": 2,
    "core/d390_reconciliere.py": 2,
    "core/d394_reconciliere.py": 2,
    "core/retete_import_api.py": 2,
    "core/solduri_parteneri_api.py": 2,
    "core/audit_preluare.py": 1,
    "core/cote_tva.py": 1,
    "core/etransport_send.py": 1,
    "core/gdpr_sterge.py": 1,
    "core/intrastat.py": 1,
    "core/reconciliere_api.py": 1,
    "core/stocuri_api.py": 1,
    "core/tipare_api.py": 1,
}


@pytest.fixture(scope="module")
def acum():
    from collections import Counter
    return Counter(x[0] for x in s.netipate_in_scop())


def test_niciun_fisier_nu_creste(acum):
    """Miezul clichetului."""
    rele = ["  %-42s %d > %d" % (f, n, BASELINE[f]) for f, n in sorted(acum.items())
            if f in BASELINE and n > BASELINE[f]]
    assert not rele, (
        "afirmații netipate ÎN CREȘTERE (scrie-le ca obiecte, nu ridica baseline-ul):\n"
        + "\n".join(rele))


def test_niciun_fisier_nou(acum):
    """Un fișier care începe azi să producă afirmații netipate n-are voie să intre tăcut."""
    noi = ["  %-42s %d" % (f, n) for f, n in sorted(acum.items()) if f not in BASELINE]
    assert not noi, (
        "fișiere NOI cu afirmații netipate — decizia din 21.08 cere obiecte cu `fel`, nu proză în "
        "dicționar. Folosește `core/afirmatii.afirmatie()`:\n" + "\n".join(noi))


def test_baseline_nu_e_stale(acum):
    """DOC↔COD: un fișier convertit trebuie SCOS din baseline, altfel tabelul minte despre datorie
    și clichetul păstrează un plafon care nu mai corespunde nimănui."""
    stale = ["  %-42s baseline %d, acum %d" % (f, n, acum.get(f, 0))
             for f, n in sorted(BASELINE.items()) if acum.get(f, 0) < n]
    assert not stale, (
        "baseline peste realitate — coboară-l (sau scoate linia dacă a ajuns la 0):\n"
        + "\n".join(stale))


def test_scanul_vede_producatorul_tipat():
    """ANTI-VACUU. Prima formă a acestui scan căuta LISTE numite `constatari`/`probleme` și era
    ORBĂ pe `control_fiscal_api` — exact modulul care produce afirmații tipate. Un scan care nu-și
    vede lumea raportează verde despre ea. Aici se probează că le VEDE."""
    tipate = [x for x in s.inventar() if x[3] == "tipata"]
    assert len(tipate) >= 20, "doar %d afirmații tipate văzute — scanul a orbit" % len(tipate)
    assert any("control_fiscal_api" in x[0] for x in tipate), (
        "scanul nu vede afirmațiile tipate din control_fiscal_api — producătorul de referință")


def test_clasificarea_chiar_discrimineaza():
    """ANTI-VACUU pe clasificare: dacă `clasa()` ar întoarce mereu același lucru, clichetul ar
    număra tot sau nimic. Se probează pe cele patru forme, cu exemple din calibrare."""
    assert s.clasa("core/x.py", "verifica", "eticheta,mesaj,remediu,stare,temei") == "A_verdict"
    assert s.clasa("core/x_import_api.py", "verifica_randuri", "mesaj,motiv,rand") == "C_import"
    assert s.clasa("core/x.py", "salveaza", "cod,mesaj,ok") == "B_operatie"
    assert s.clasa("core/x.py", "adauga", "camp,mesaj") == "D_formular"


def test_granita_lui_costin_e_respectata():
    """B (rezultat de operație) și D (validare de formular) NU intră în decizie — nu spun nimic
    despre datele firmei. Dacă ar intra, clichetul ar crește cu 66 și campania ar vâna text de
    interfață, exact ce a exclus Costin."""
    scop = {x[4] for x in s.netipate_in_scop()}
    assert scop <= {"A_verdict", "C_import"}, "clichetul a înghițit clase excluse: %s" % scop
    inv = s.inventar()
    assert any(x[4] == "D_formular" for x in inv), (
        "nicio validare de formular văzută — clasa nu mai e exercitată, deci nu se știe dacă ar mai "
        "fi ținută afară")
