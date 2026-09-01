# -*- coding: utf-8 -*-
"""GARD [01.09.2026, interdicția 3]: un calcul fiscal nu citește data curentă în tăcere.

Interdicția era **NEÎNCEPUTĂ** — fără instrument, deci fără cifră. `core/scan_data_curenta.py` o
măsoară acum, iar aici se păzește ce s-a măsurat.

**De ce e clasa care produce o cifră validă și falsă:** registrul de cote e cheiat pe dată tocmai ca
o valoare să fie citită *la perioada ei*. Un apelant care omite data desface asta **la locul
apelului**: primește „azi", iar numărul iese valid și fals pentru perioada calculată.

**CALIBRAREA E SCRISĂ PE MODUL MEU DE EȘEC, nu pe cel al codului.** Am măsurat clasa greșit de trei
ori într-o singură alegere, toate în aceeași direcție — numărând **forma**, nu **efectul**:

  | greșeala | ce a produs | proba care o prinde |
  |---|---|---|
  | numai apeluri pe **nume**, nu pe atribut | „1 apel de `cota`" | `test_un_apel_pe_ATRIBUT_se_vede` |
  | numai argumente cu **cuvânt-cheie** | „68 de omisiuni" în loc de 4 | `test_o_data_data_POZITIONAL_conteaza_ca_data` |
  | tipar de nume prea larg | o funcție de **email** clasată ca fiscală | `EXCEPTII`, cu motivul, + `test_fiecare_exceptie_are_inca_obiect` |
"""
import ast
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import scan_data_curenta as S  # noqa: E402

#: MĂSURAT 01.09.2026. Fiecare e un generator LATENT: orice apelant viitor care uită data primește
#: tăcut „azi". Clichetul nu poate crește — o funcție fiscală nouă cu implicit pe azi e o intrare în
#: clasă, nu o comoditate.
CLICHET_FUNCTII_CARE_CAD = 26

#: Omisiuni reale rămase, după reparație. **1**: `intrastat.analiza_flux`, ținută separat fiindcă
#: repararea ei schimbă ce AFIȘEAZĂ ecranul (pentru un an fără prag cunoscut, răspunsul onest e
#: „nu se poate ști" — v. R112), deci cere poartă vizuală și tură proprie.
CLICHET_OMISIUNI = 1


def test_ANTI_VACUU_instrumentul_chiar_vede_ceva():
    c = S.cifre()
    assert c["functii_care_cad_pe_azi"] >= 20, (
        "[anti-vacuu] doar %d funcții — domeniul s-a rupt și toate clichetele de mai jos ar fi verzi "
        "despre o mulțime goală" % c["functii_care_cad_pe_azi"])
    assert c["apeluri_care_dau_data"] >= 50, (
        "[anti-vacuu] doar %d apeluri care dau data — sonda nu mai vede apelurile"
        % c["apeluri_care_dau_data"])


def test_functiile_care_cad_pe_data_curenta_nu_CRESC():
    n = S.cifre()["functii_care_cad_pe_azi"]
    assert n <= CLICHET_FUNCTII_CARE_CAD, (
        "%d funcții fiscale cad pe data curentă (clichet %d). O funcție nouă cu `la_data or "
        "today()` e un generator latent de cifră validă și falsă: primul apelant care uită data o "
        "declanșează. Dă data explicit, sau cere-o." % (n, CLICHET_FUNCTII_CARE_CAD))


def test_niciun_apel_nou_nu_OMITE_data():
    """MIEZUL. Clasa care produce cifra falsă **azi**, nu latent."""
    om = S.omisiuni()
    assert len(om) <= CLICHET_OMISIUNI, (
        "apeluri de producție care omit data: %d > clichet %d%s  %s%s"
        "Fiecare primește «azi» pentru o perioadă care poate fi alta. Dă data, sau declar-o în "
        "`EXCEPTII` cu motivul — o excepție tăcută e cea pe care o știe un singur raport."
        % (len(om), CLICHET_OMISIUNI, chr(10),
           (chr(10) + "  ").join("%s:%d → %s()" % o for o in om), chr(10)))


def test_fiecare_exceptie_are_inca_obiect():
    """O excepție care nu mai corespunde niciunui apel e o urmă de intenție (R23). Și invers: o
    excepție fără motiv scris e un clichet deghizat."""
    vazute = {(f, n) for f, _l, n in S.scutite()}
    orfane = sorted(set(S.EXCEPTII) - vazute)
    assert not orfane, (
        "excepții care nu mai corespund niciunui apel — apelul a dispărut sau a primit data; "
        "scoate-le: %s" % orfane)
    fara_motiv = [k for k, v in S.EXCEPTII.items() if len((v or "").strip()) < 40]
    assert not fara_motiv, "excepții fără motiv scris: %s" % fara_motiv


# ── CALIBRAREA, pe cele trei greșeli ale mele ──────────────────────────────────────────────────

def _apel(cod):
    return next(n for n in ast.walk(ast.parse(cod)) if isinstance(n, ast.Call))


def test_un_apel_pe_ATRIBUT_se_vede():
    """Greșeala 1. `_common.cota(...)` e același apel ca `cota(...)`. Prima sondă căuta numai
    `ast.Name` și a raportat **un** apel de `cota` în tot `core/`."""
    fn = S.cade_pe_azi()
    assert fn.get("cota") is not None, (
        "[calibrare] `cota` nu mai e în populația A — proba și-a pierdut obiectul")
    # `d100.py` cheamă EXCLUSIV `_common.cota(...)` — deci apare aici doar dacă atributul se vede.
    # *Prima formă a probei număra toate apelurile de `cota` și trecea și cu sonda oarbă la atribut:
    # `cota(...)` pe nume există în destule alte fișiere. O calibrare care nu izolează proprietatea
    # nu o testează.*
    surse = {f for f, _l, nume, _da, _t in S.apeluri(fn) if nume == "cota"}
    assert {"d100.py"} <= surse, (
        "[calibrare] apelurile pe ATRIBUT nu se mai văd: `d100.py` cheamă numai `_common.cota(...)` "
        "și a dispărut din inventar. Fișiere văzute: %s" % sorted(surse)[:8])


def test_o_data_data_POZITIONAL_conteaza_ca_data():
    """Greșeala 2, cea care a umflat clasa de la 4 la 68. `cota("impozit_micro", d)` **dă** data."""
    fn = S.cade_pe_azi()
    _f, indici, de_data = fn["cota"]
    assert S._da_data(_apel('cota("impozit_micro", d)'), indici, de_data) is True, (
        "un al doilea argument pozițional nu mai e recunoscut ca dată — clasa se umflă din nou")
    assert S._da_data(_apel('cota("impozit_micro", la_data=d)'), indici, de_data) is True
    assert S._da_data(_apel('cota("impozit_micro")'), indici, de_data) is False, (
        "un apel FĂRĂ dată e socotit ca având-o — direcția opusă, și ar goli clasa")


def test_directia_INVERSA_un_apel_care_omite_chiar_se_vede():
    """Fără asta, un `_da_data` care ar întoarce mereu `True` ar face toate testele verzi pe o clasă
    goală. Se cere pe instanța reală care rămâne de reparat."""
    om = S.omisiuni()
    assert om, ("[anti-vacuu] zero omisiuni — dacă e adevărat, coboară `CLICHET_OMISIUNI` la 0 și "
                "mută proba pe caz sintetic (METODA §29)")
    assert ("intrastat.py", 45, "prag_intrastat") in [(f, l, n) for f, l, n in om] or \
           any(n == "prag_intrastat" for _f, _l, n in om), (
        "instanța pinată a dispărut din omisiuni: %s. Dacă a fost reparată, coboară clichetul." % om)


def test_o_functie_fara_parametru_de_data_NU_intra_in_clasa():
    """Direcția care ar umfla populația A: nu orice funcție care citește `today()` e un calcul care
    ar TREBUI să primească o dată. Cele fără niciun parametru de dată nu au ce alege."""
    fn = S.cade_pe_azi()
    fara = [n for n, (_f, _i, de_data) in fn.items() if not de_data]
    assert not fara, "funcții fără parametru de dată intrate în clasă: %s" % fara
