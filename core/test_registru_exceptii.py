# -*- coding: utf-8 -*-
"""GARDĂ peste REGISTRUL DE EXCEPȚII al clichetului de afirmații. (P8, 22.08.2026)

DE CE EXISTĂ REGISTRUL (decis de Costin): un plafon care nu poate ajunge la zero își pierde funcția.
Câteva locuri poartă cheia `mesaj` fără să fie afirmații despre datele firmei — răspunsul ANAF
verbatim, triajul AI al unei sesizări de suport. Ele nu se pot converti, fiindcă n-au ce tipa.

DE CE E PERICULOS (întrebarea lui Costin): ce împiedică o intrare nouă să fie ADĂUGATĂ acolo în loc
să fie REPARATĂ? Trei zăvoare, și doar al treilea e cel real:

  1. MECANIC — registrul nu poate CREȘTE. Dimensiunea lui e ea însăși clichet.
  2. MECANIC — fiecare intrare trebuie să fie VIE: situl pe care-l numește trebuie să existe ȘI să
     fie încă netipat. Cine convertește un sit trebuie să scoată intrarea, altfel roșu. Ăsta e
     echivalentul „excepția trebuie să fie chiar folosită" de la blocul de perimetru.
  3. AL RAȚIUNII — motivul se alege dintr-un set ÎNCHIS de patru. Fără el, primele două zăvoare ar
     păzi o listă în care se poate scrie orice. „Rezultat de operație" NU e printre ele, deliberat:
     e o FORMĂ, nu o natură, și s-ar umple pe măsură ce clichetul strânge — exact ce a suspectat
     Costin când a întrebat dacă cele cinci sunt de aceeași natură. (Nu erau: măsurate, erau ~11, de
     patru naturi.)
"""
import pytest

from core import registru_exceptii as reg
from core import scan_afirmatii as s

# Instalat 22.08.2026 pe cifra MĂSURATĂ. Coborât la 5 în aceeași zi, când cheia a trecut de pe
# LINIE pe FUNCȚIE și cele trei ramuri ale lui `raportari_ai.triaj` s-au dovedit a fi o singură
# intrare (aceeași funcție, aceeași natură). NU se ridică.
MARIME_MAXIMA = 5


@pytest.fixture(scope="module")
def inv():
    return {(x[0], x[1]) for x in s.netipate_in_scop()}      # (fisier, functie)


def test_registrul_nu_creste():
    """ZĂVORUL 1. Dacă ar putea crește, ar fi o portiță cu proces-verbal."""
    assert len(reg.EXCEPTII) <= MARIME_MAXIMA, (
        "registrul de excepții a crescut la %d (max %d). O afirmație netipată se REPARĂ; se declară "
        "excepție doar dacă nu e o afirmație despre datele firmei."
        % (len(reg.EXCEPTII), MARIME_MAXIMA))


def test_fiecare_exceptie_e_VIE(inv):
    """ZĂVORUL 2, cel care ține registrul onest. O intrare care nu mai corespunde unui sit real e o
    excepție acordată unei lumi care nu există — și ascunde faptul că altceva a luat locul."""
    moarte = ["  %s::%s (%s)" % (e["fisier"], e["functie"], e["motiv"])
              for e in reg.EXCEPTII if (e["fisier"], e["functie"]) not in inv]
    assert not moarte, (
        "excepții MOARTE — situl nu mai există sau a fost convertit; scoate intrarea:\n"
        + "\n".join(moarte))


def test_motivele_sunt_dintr_un_set_inchis():
    """ZĂVORUL 3. Fără el, celelalte două păzesc o listă în care se poate scrie orice."""
    for e in reg.EXCEPTII:
        assert e["motiv"] in reg.RATIUNI, (
            "motiv din afara setului închis: %r. Cele patru sunt: %s. Dacă ai nevoie de altul, e "
            "semn că situl trebuie REPARAT, nu declarat."
            % (e["motiv"], ", ".join(sorted(reg.RATIUNI))))
        assert e.get("de_ce"), (
            "excepția %s::%s n-are explicație proprie — rațiunea din nomenclator e categoria, nu "
            "argumentul" % (e["fisier"], e["functie"]))


def test_ratiunea_care_s_ar_umple_nu_exista():
    """Costin a întrebat dacă cele cinci sunt de aceeași natură. Măsurate, erau ~11, de patru naturi,
    iar „rezultat de operație" era o FORMĂ care s-ar fi umplut. Nu e în set, și testul o ține afară."""
    for interzis in ("rezultat_operatie", "rezultat_de_operatie", "altele", "diverse", "temporar"):
        assert interzis not in reg.RATIUNI, (
            "rațiunea %r a intrat în set — e o formă, nu o natură, și se va umple" % interzis)


def test_fiecare_ratiune_e_folosita():
    """ANTI-VACUU pe nomenclator: o rațiune declarată și nefolosită e o categorie disponibilă pentru
    orice, adică exact portița pe care setul închis o închide."""
    folosite = {e["motiv"] for e in reg.EXCEPTII}
    nefolosite = sorted(set(reg.RATIUNI) - folosite)
    assert not nefolosite, (
        "rațiuni declarate și nefolosite: %s — scoate-le, altfel sunt sertare goale în care încape "
        "orice" % nefolosite)


def test_exceptiile_nu_acopera_tot(inv):
    """Un registru care acoperă TOATE netipatele ar face clichetul verde fără nicio reparație."""
    assert len(reg.EXCEPTII) < len(inv), (
        "registrul acoperă %d din %d netipate — clichetul ar fi verde prin declarație, nu prin muncă"
        % (len(reg.EXCEPTII), len(inv)))


def test_datoria_reala_e_in_ACEEASI_unitate_ca_clichetul():
    """Cifra care contează e cea care POATE ajunge la zero: netipate MINUS excepții declarate.

    ȘI trebuie să fie în ACEEAȘI UNITATE ca baseline-ul clichetului — INTRĂRI, nu poziții. Pe 22.08
    n-a fost: `datorie_reala` număra poziții (fișier, linie) distincte și dădea 17 acolo unde
    clichetul număra 18, fiindcă `control_fiscal_api:960` are DOUĂ dicționare pe aceeași linie. Două
    cifre în două unități, raportate ca aceeași măsură."""
    from core.test_afirmatii_tipate import BASELINE
    lst = s.netipate_in_scop()
    assert sum(BASELINE.values()) == len(lst), (
        "baseline-ul (%d) și inventarul (%d) nu mai sunt în aceeași unitate"
        % (sum(BASELINE.values()), len(lst)))
    # O excepție e cheiată pe (fișier, FUNCȚIE), deci poate acoperi mai multe intrări — `raportari_ai
    # .triaj` acoperă trei ramuri. Aritmetica simplă „inventar minus numărul de excepții" NU mai ține,
    # și a fost înlocuită cu numărarea intrărilor NEACOPERITE. Prima formă ar fi dat 13 în loc de 15.
    ex = {(e["fisier"], e["functie"]) for e in reg.EXCEPTII}
    neacoperite = len([x for x in lst if (x[0], x[1]) not in ex])
    assert reg.datorie_reala() == neacoperite, (
        "datorie_reala (%d) nu numără intrările neacoperite de excepții (%d)"
        % (reg.datorie_reala(), neacoperite))


def test_unitatea_e_INTRAREA_nu_pozitia():
    """ANTI-VACUU pe unitate, SINTETIC. Dacă numărătoarea ar deduplica pe (fișier, linie), două
    afirmații scrise pe același rând ar conta ca una — și una dintre ele ar putea rămâne netipată
    pentru totdeauna fără ca vreo cifră să se miște. Asta s-a și întâmplat pe 22.08:
    `control_fiscal_api:960` avea două dicționare, iar `datorie_reala` dădea 17 unde clichetul dădea 18.

    Cazul nu mai există în cod (situl a fost convertit), deci se probează pe un inventar CONSTRUIT —
    altfel testul ar trece pe gol și n-ar mai apăra nimic."""
    fals = [("core/x.py", "f", 10, "netipata", "A_verdict", "mesaj"),
            ("core/x.py", "f", 10, "netipata", "A_verdict", "cauza"),
            ("core/y.py", "g", 20, "netipata", "A_verdict", "mesaj")]
    assert reg.datorie_reala(fals) == 3, (
        "două afirmații pe același rând s-au numărat ca una — unitatea a alunecat de la INTRARE la "
        "poziție, iar una dintre ele ar putea rămâne netipată fără ca vreo cifră să se miște")
