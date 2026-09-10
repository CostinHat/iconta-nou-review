# -*- coding: utf-8 -*-
"""core/test_blocante_clasificate.py — garda diagnosticului P5.

**CE PĂZEȘTE, în trei straturi:**

1. **DETECTORUL vede ce zice că vede** — corpusul sintetic din `scripts/scan_blocante.py`, cu probă
   pozitivă per detector și controale negative. Un detector care nu se aprinde pe cazul lui, sau
   care se aprinde pe controlul curat, pică aici. `DETECTOR_CALIBRATION_GAPS = 0`.
2. **CLASIFICAREA acoperă tot** — inventarul se REGENEREAZĂ în test (1,4 s), nu se citește dintr-un
   artefact comis. Deci nu poate îmbătrâni în tăcere: o rută nouă cu I/O blocant apare la prima
   rulare a suitei, nu la următoarea regenerare manuală.
3. **MECANISMUL REFUZĂ** — pentru fiecare regulă există un candidat sintetic care o aprinde, ȘI
   dovada că, fără ea, același candidat rămâne NECLASIFICAT și contabilitatea trece pe `FAIL`.
   *Calibrarea pozitivă singură n-ar dovedi decât că regula spune „da" — nu că absența ei se vede*
   (METODA §22, interdicția 76).

**ANTI-VACUUM.** Fiecare strat își asertează premisa: dacă scanarea n-ar găsi nimic, dacă inventarul
ar fi gol, sau dacă o regulă n-ar fi atinsă niciodată, testele de mai jos pică — nu trec verde
despre o lume pe care n-o văd.
"""
import os
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import scan_blocante as SB  # noqa: E402
from core import p5_clasificare as P  # noqa: E402


@pytest.fixture(scope="module")
def inventar():
    """Inventarul BRUT, regenerat acum din cod — nu citit dintr-un artefact."""
    candidati, stat = SB.inventar(rad=RAD)
    return {"candidati": candidati, "stat": stat}


# ═══════════════════════════════════════════════════════════════════════════
#  STRATUL 1 — detectorul
# ═══════════════════════════════════════════════════════════════════════════

def test_calibrarea_detectorului_nu_are_goluri():
    """`DETECTOR_CALIBRATION_GAPS = 0` — fiecare detector are probă pozitivă și control negativ."""
    probe = SB.probe_calibrare()
    assert len(probe) >= 20, "corpusul de calibrare a produs doar %d probe — premisă căzută" % len(
        probe)
    picate = [nume for nume, ok in probe if not ok]
    assert not picate, "goluri de calibrare:\n  " + "\n  ".join(picate)


def test_fiecare_detector_are_proba_pozitiva_proprie():
    """Anti-vacuum pe tabelul de calibrare: niciun detector fără caz al lui."""
    assert set(SB.CALIBRARE) == set(SB.DETECTORI), (
        "detectori fără probă de calibrare: %s" % sorted(set(SB.DETECTORI) - set(SB.CALIBRARE)))


#: detectorii care se aprind pe codul REAL — clichet, nu cerință. Vezi testul de mai jos.
APRINSI_PE_REAL = {"C1", "C2", "C3", "C4", "C5", "C7"}

#: de ce lipsește fiecare detector din mulțimea de mai sus — un gol fără motiv nu poate trece
DE_CE_ZERO = {
    "C6": (
        "ZERO instanțe reale, și e o măsurătoare, nu o scăpare. Toate cele 5 aprinderi din prima "
        "formă erau ACELAȘI loc, numărat de cinci ori: `core/spv_conector.py:455`, "
        "`requests.request(metoda, url, ..., **kw)` din `apel_anaf`. La locul apelului nu scrie "
        "`timeout`, dar toți cei 7 apelanți reali îl trimit prin despachetare "
        "(`efactura_send.py:393,400,407,442` · `etransport_send.py:82,89,97` — `timeout=30/60/120`, "
        "verificat rând cu rând). Detectorul are acum trei stări, iar C6 se aprinde numai pe "
        "absența CERTĂ. RĂMÂNE ADEVĂRAT, și se scrie: `apel_anaf` n-are termen IMPLICIT, deci un "
        "apelant viitor care uită `timeout=` produce chiar defectul, și nimic nu l-ar opri."),
}


def test_detectorii_aprinsi_pe_codul_real_sunt_cei_pinati(inventar):
    """Clichet în AMBELE direcții pe ce vede detectorul în casă.

    Prima formă cerea ca FIECARE detector să se aprindă pe cod real. Cerința aia e prea tare: un
    detector poate avea zero instanțe fiindcă **așa e casa**, nu fiindcă e mort. Dar „zero" nu poate
    fi tăcut — altfel un detector care se strică arată identic cu unul care n-are ce găsi. Deci se
    pinează mulțimea, iar fiecare absență își scrie motivul. *Un detector viu care începe să se
    aprindă e la fel de important ca unul care se stinge: amândouă mișcă mulțimea, amândouă pică.*
    """
    aprinsi = set()
    for x in inventar["candidati"]:
        aprinsi |= set(x["detectori"])
    assert aprinsi == APRINSI_PE_REAL, (
        "mulțimea detectorilor aprinși pe cod real s-a mutat: %s\n"
        "  apărut: %s\n  dispărut: %s\n"
        "Nu e o eroare de la sine — e o schimbare care trebuie citită și rescrisă."
        % (sorted(aprinsi), sorted(aprinsi - APRINSI_PE_REAL), sorted(APRINSI_PE_REAL - aprinsi)))
    tacuti = sorted(set(SB.DETECTORI) - APRINSI_PE_REAL - set(DE_CE_ZERO))
    assert not tacuti, "detectori cu zero instanțe și fără motiv scris: %s" % tacuti


def test_detectorul_fara_instante_reale_e_totusi_viu():
    """Cealaltă direcție a aceleiași întrebări: zero pe casă ≠ mort.

    Un detector cu zero instanțe reale ar putea fi rupt fără ca nimic să spună. Proba că e viu vine
    din corpusul sintetic, unde are cazul lui și mulțimea pinată.
    """
    gasit, _d = SB.corpus_sintetic()
    for cod in sorted(set(SB.DETECTORI) - APRINSI_PE_REAL):
        ruta, astept = SB.CALIBRARE[cod]
        x = gasit.get(ruta)
        assert x is not None, "%s n-are caz sintetic — nu se poate ști dacă e viu" % cod
        assert set(x["detectori"]) == astept, (
            "%s nu se aprinde nici pe cazul lui: %s" % (cod, sorted(x["detectori"]) if x else None))


# ═══════════════════════════════════════════════════════════════════════════
#  STRATUL 2 — clasificarea acoperă tot
# ═══════════════════════════════════════════════════════════════════════════

def test_inventarul_nu_e_gol(inventar):
    """Premisa tuturor celorlalte: scanarea CHIAR a văzut aplicația."""
    st = inventar["stat"]
    assert st["intrari"] > 300, "prea puține puncte de intrare (%d) — scanarea n-a văzut app" % (
        st["intrari"],)
    assert st["middleware"] >= 1, "niciun middleware văzut — fals-negativ pe cea mai fierbinte cale"
    assert len(inventar["candidati"]) > 10, "prea puțini candidați — filtru prea strâns"


def test_fiecare_candidat_brut_are_verdict(inventar):
    """`RAW_CANDIDATES == CLASSIFIED_CANDIDATES`, `UNCLASSIFIED_RAW_CANDIDATES = 0`."""
    n = P.numaratori(inventar["candidati"])
    assert n["UNCLASSIFIED_RAW_CANDIDATES"] == 0, (
        "candidați fără verdict: %s" % n["neclasificate"][:20])
    assert n["RAW_CANDIDATES"] == n["CLASSIFIED_CANDIDATES"]


def test_contabilitatea_claselor_se_inchide(inventar):
    """`ACTION_REQUIRED + ACCEPTABLE_BY_DESIGN + FALSE_POSITIVE == RAW_CANDIDATES`."""
    n = P.numaratori(inventar["candidati"])
    assert n["RAW_CLASS_SUM"] == n["RAW_CANDIDATES"], (
        "%d + %d + %d = %d ≠ %d" % (n["ACTION_REQUIRED"], n["ACCEPTABLE_BY_DESIGN"],
                                    n["FALSE_POSITIVES"], n["RAW_CLASS_SUM"], n["RAW_CANDIDATES"]))
    assert n["RAW_CLASS_ACCOUNTING"] == "PASS"


def test_nicio_excludere_nemotivata(inventar):
    """`UNEXPLAINED_EXCLUSIONS = 0` — peste TOȚI candidații care nu cer acțiune, nu doar unii."""
    n = P.numaratori(inventar["candidati"])
    assert n["EXCLUSIONS_TOTAL"] == (n["ACCEPTABLE_BY_DESIGN"] + n["FALSE_POSITIVES"]), (
        "universul excluderilor nu e cel al ne-acțiunii")
    assert n["UNEXPLAINED_EXCLUSIONS"] == 0, "excluderi fără motiv scris: %s" % n["nemotivate"][:20]


def test_fiecare_actiune_are_val_si_fel_de_dovada(inventar):
    """Un `ACTION_REQUIRED` fără val de remediere și fără felul dovezii n-ar fi acționabil."""
    fara = []
    for x in inventar["candidati"]:
        v = P.verdict(x)
        if v["clasa"] == P.ACTIUNE and (not v.get("val") or v["dovada"] == "-"):
            fara.append(x["intrare"])
    assert not fara, "acțiuni fără val sau fără fel de dovadă: %s" % fara[:20]


def test_felurile_de_dovada_nu_se_amesteca(inventar):
    """Cele trei feluri sunt DECLARATE, nu inventate rând cu rând."""
    permise = {P.MASURAT, P.NEMARGINIT, P.MARGINIT_RAR, "THREADPOOL", "FARA_BUCLA", "PORNIRE",
               "OARBIRE", "TIPAR_BUN"}
    vazute = {P.verdict(x)["dovada"] for x in inventar["candidati"]}
    assert vazute <= permise, "feluri de dovadă nedeclarate: %s" % sorted(vazute - permise)


def test_randurile_individuale_nu_sunt_moarte(inventar):
    """Un rând scris de mână pentru o cale care nu mai există ar minți despre acoperire."""
    intrari = {x["intrare"] for x in inventar["candidati"]}
    absente = set(P.randuri_fara_cale())
    moarte = sorted(k for k in P.CLASIFICARE if k not in intrari and k not in absente)
    assert not moarte, ("rânduri individuale fără cale în inventar: %s — ori calea a dispărut, "
                        "ori rândul trebuie marcat `cale_absenta`" % moarte)


def test_randurile_declarate_absente_chiar_lipsesc(inventar):
    """Cealaltă direcție: `cale_absenta` nu poate acoperi o cale care E în inventar."""
    intrari = {x["intrare"] for x in inventar["candidati"]}
    gresite = sorted(k for k in P.randuri_fara_cale() if k in intrari)
    assert not gresite, "marcate absente, dar prezente în inventar: %s" % gresite


# ═══════════════════════════════════════════════════════════════════════════
#  STRATUL 3 — mecanismul REFUZĂ (calibrare în ambele direcții)
# ═══════════════════════════════════════════════════════════════════════════

def _sintetic(intrare, fel="ruta", detectori=(), primitive=None, **fapte):
    f = {"primitive_total": 1, "pe_bucla": 0, "in_domeniu_db": 0, "feluri": ["DB"],
         "retea_fara_timeout": 0, "numai_omonim": False}
    f.update(fapte)
    return {"id": "SINT", "fel": fel, "intrare": intrare, "functie": "f_sintetic",
            "fisier": "sintetic.py", "async": fel == "ruta" and "C1" in detectori,
            "e_ruta": fel == "ruta", "detectori": {c: "sintetic" for c in detectori}, "fapte": f,
            "primitive": primitive or [{"fel": f["feluri"][0], "detaliu": "x",
                                        "loc": "sintetic.py:1", "pe_bucla": False,
                                        "in_domeniu_db": False, "via": "f", "omonim": False}]}


#: `(regula, candidat sintetic care o aprinde, clasa așteptată)`
CAZURI = [
    ("OMONIM", _sintetic("SINTETIC numai omonim", detectori=("C2",), numai_omonim=True), P.FALS),
    ("FUNDAL", _sintetic("SINTETIC lucrător", fel="fundal", detectori=("C2", "C6")), P.ACCEPTABIL),
    ("C1-CERERE", _sintetic("SINTETIC numai C1", detectori=("C1",), pe_bucla=2), P.ACTIUNE),
    ("C6-FARA-TIMEOUT", _sintetic("SINTETIC numai C6", detectori=("C6",), retea_fara_timeout=1,
                                  feluri=["RETEA"]), P.ACTIUNE),
    ("C5-EXTERN-CU-CONEXIUNE", _sintetic("SINTETIC numai C5", detectori=("C5",), in_domeniu_db=1,
                                         feluri=["DB", "RETEA"]), P.ACTIUNE),
    ("SINCRON-MARGINIT", _sintetic("SINTETIC sincron", detectori=("C7",), feluri=["FS"]),
     P.ACCEPTABIL),
]


@pytest.mark.parametrize("cod,candidat,clasa", CAZURI, ids=[c[0] for c in CAZURI])
def test_regula_se_aprinde_pe_cazul_ei(cod, candidat, clasa):
    """DIRECȚIA POZITIVĂ: regula spune «da» exact pe candidatul construit pentru ea."""
    v = P.verdict(candidat)
    assert v is not None, "candidatul sintetic pentru %s n-a primit verdict" % cod
    assert v["regula"] == cod, "%s a fost prins de %s, nu de %s" % (candidat["intrare"],
                                                                   v["regula"], cod)
    assert v["clasa"] == clasa


@pytest.mark.parametrize("cod,candidat,clasa", CAZURI, ids=[c[0] for c in CAZURI])
def test_fara_regula_mecanismul_refuza(cod, candidat, clasa):
    """DIRECȚIA NEGATIVĂ, cea care chiar dovedește ceva.

    Se scot TOATE regulile (inclusiv coada care prinde orice) și se cere ca același candidat să
    rămână NECLASIFICAT, iar contabilitatea să treacă pe `FAIL`. *Fără proba asta, «toți cei 94 au
    verdict» ar putea însemna doar că ultima regulă înghite orice.*
    """
    n = P.numaratori([candidat], clasificare={}, reguli=[])
    assert n["UNCLASSIFIED_RAW_CANDIDATES"] == 1, (
        "candidatul %s a primit verdict deși nicio regulă nu-l acoperă" % cod)
    assert n["RAW_CLASS_ACCOUNTING"] == "FAIL", (
        "contabilitatea a rămas PASS cu un candidat neclasificat — mecanismul NU refuză")


def test_coada_nu_ascunde_lipsa_unei_reguli():
    """Cazul viclean: regula lipsește, dar coada o acoperă tăcut.

    Se scoate DOAR `C1-CERERE`. Candidatul care aprinde numai C1 cade atunci în coadă și primește
    `ACCEPTABLE_BY_DESIGN` — adică exact verdictul GREȘIT, în tăcere. Testul pinează purtarea asta
    ca fiind CUNOSCUTĂ: coada e o afirmație despre restul, nu o plasă de siguranță. De-aia proba de
    refuz de mai sus se face cu lista goală, nu cu lista ciuntită.
    """
    _, candidat, _ = CAZURI[2]
    fara_c1 = [r for r in P.REGULI if r["cod"] != "C1-CERERE"]
    v = P.verdict(candidat, clasificare={}, reguli=fara_c1)
    assert v["regula"] == "SINCRON-MARGINIT" and v["clasa"] == P.ACCEPTABIL


def test_fiecare_regula_e_atinsa_de_ceva(inventar):
    """Nicio regulă decorativă: fiecare e atinsă de cod real SAU are caz sintetic propriu."""
    reale = {P.verdict(x)["regula"] for x in inventar["candidati"]}
    sintetice = {c[0] for c in CAZURI}
    neatinse = sorted(r["cod"] for r in P.REGULI if r["cod"] not in reale | sintetice)
    assert not neatinse, "reguli pe care nimic nu le atinge: %s" % neatinse


def test_ordinea_regulilor_pune_omonimia_prima():
    """Ordinea NU e cosmetică — e direcția prudenței, și se pinează.

    La P4 `OMONIM` stătea ultima, fiindcă rezolvarea pe omonimie ADAUGĂ evenimente, iar acolo
    verdictul sigur era «non-critic». Aici verdictul sigur e «acceptabil», deci aceleași evenimente
    în plus ar produce o ACȚIUNE falsă. *Aceeași proprietate a instrumentului cere ordini opuse.*
    """
    coduri = [r["cod"] for r in P.REGULI]
    assert coduri[0] == "OMONIM", "omonimia trebuie judecată înaintea regulilor de acțiune"
    assert coduri[-1] == "SINCRON-MARGINIT", "coada trebuie să fie ultima"
    x = _sintetic("SINTETIC omonim si C1", detectori=("C1",), pe_bucla=2, numai_omonim=True)
    assert P.verdict(x)["clasa"] == P.FALS, (
        "un candidat sprijinit numai pe omonimie a primit ACȚIUNE — ordinea nu ține")


# ═══════════════════════════════════════════════════════════════════════════
#  Cifrele citate — recalculabile, nu ținute minte
# ═══════════════════════════════════════════════════════════════════════════

def test_cifrele_din_motive_vin_din_banc():
    """Nicio cifră din motive nu are voie să fie scrisă de mână.

    Prima formă le avea bătute în text. O re-rulare a bancului le-a schimbat pe toate, iar textul
    ar fi rămas în urmă fără ca nimic să pice: *o cifră care nu se poate recalcula nu e o
    măsurătoare, e o amintire.* Acum se citesc din artefact, iar testul cere artefactul.
    """
    m = P.masuratori(reincarca=True)
    assert m, "lipsește masuratori/p5/P5_MASURATORI.json — motivele n-ar avea de unde cita"
    obligatorii = ("canar_baza_p95", "canar_varf_p95", "canar_varf_max", "ruta_varf_p50",
                   "canar_sync_p95", "N_varf", "k_max", "conexiuni_max", "capacitate_pool")
    lipsa = [k for k in obligatorii if m.get(k) is None]
    assert not lipsa, "cifre absente din banc: %s" % lipsa


def test_niciun_motiv_nu_ramane_fara_masuratoare(inventar):
    """Semnul de lipsă e vizibil — deci trebuie să nu apară nicăieri."""
    fara = [x["intrare"] for x in inventar["candidati"]
            if "«fără măsurătoare»" in P.verdict(x)["de_ce"]]
    assert not fara, "motive care citează o cifră inexistentă: %s" % fara[:10]


def test_martorul_sincron_chiar_a_reusit():
    """Premisa martorului, asertată — nu presupusă.

    Martorul a măsurat o vreme o cale de EROARE 500 (`UndefinedTable`), fiindcă firma sintetică
    avea schemă goală, iar `curba_sync` nu înregistra statusurile. *O durată există și pe 500.*
    Testul cere ca artefactul să arate numai 200 și niciun status neașteptat.
    """
    import io as _io
    import json as _json
    cale = os.path.join(RAD, "masuratori", "p5", "P5_MASURATORI.json")
    assert os.path.exists(cale), "lipsește artefactul de măsurători"
    d = _json.load(_io.open(cale, encoding="utf-8"))
    assert d.get("statusuri_neasteptate") == {}, (
        "măsurători pe altă ramură decât cea numită: %s" % d.get("statusuri_neasteptate"))
    assert set(d["martor_sync"]["statusuri"]) == {"200"}, (
        "martorul sincron n-a ieșit 200: %s" % d["martor_sync"]["statusuri"])
    assert d["jurnal_server"]["URME_EXCEPTIE"] == 0, (
        "%d urme de excepție în jurnalul serverului — măsurătoarea a lovit o cale de eroare"
        % d["jurnal_server"]["URME_EXCEPTIE"])
    assert d["amprenta"]["PRODUCTION_DATA_AFFECTED"] == "NO"


# ═══════════════════════════════════════════════════════════════════════════
#  Contractul fazei: diagnostic, nu implementare
# ═══════════════════════════════════════════════════════════════════════════

def test_diagnosticul_nu_atinge_codul_de_productie():
    """Instrumentele P5 nu au voie să scrie în calea de cerere.

    Nu e o promisiune, e o verificare: fișierele scrise pentru faza asta trăiesc în `scripts/` și
    `core/p5_*`, iar niciunul nu e importat de `main.py`.
    """
    import io
    m = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    for nume in ("scan_blocante", "masoara_p5", "p5_clasificare"):
        assert nume not in m, "%s e importat în calea de cerere — diagnosticul a devenit cod viu" % (
            nume,)
