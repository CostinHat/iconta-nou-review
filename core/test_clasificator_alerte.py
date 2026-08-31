# -*- coding: utf-8 -*-
"""CLICHET: eticheta unei alerte e o PREDICȚIE confruntabilă, iar greșelile ei nu mai pot crește.

*Costin, 31.08.2026: «A greșit pe 2 din 2 acte, în direcții opuse — asta nu e o constatare, e rata
lui de eroare pe tot eșantionul existent. E pâlnia de intrare: tot ce vine de la ANAF se
prioritizează pe el. Ce trebuie să fie adevărat după: eticheta e o predicție confruntabilă cu
impactul măsurat, nu un verdict. Azi am aflat că minte doar fiindcă am măsurat de mână.»*

**CE ERA GRESIT, și nu e „modelul a greșit".** Clasificatorul întorcea `relevanta: mare|medie` — o
judecată de ansamblu **fără motive**. O judecată fără motive **nu se poate contrazice**: când
impactul iese altfel, n-ai ce compara cu ce. De-aia a putut minți fără să se aprindă nimic.

**CE S-A SCHIMBAT.** Nu se cere o judecată mai bună; se cer **două fapte verificabile** — încotro
merge documentul, și ce declarații atinge — iar relevanța se **derivă** din ele, în cod. Amândouă
faptele se pot confrunta cu măsurătoarea, fiindcă măsurătoarea răspunde la aceleași două întrebări.

**Proba că schimbarea nu e cosmetică:** din cele două fapte, **amândouă actele ies corect**, fără
nicio judecată de ansamblu — vezi `test_cele_doua_acte_ar_fi_iesit_corect_din_fapte`.

**CE NU PĂZEȘTE, declarat:** că faptele extrase sunt adevărate. Un model care spune „catre_anaf"
despre o decizie de impunere va produce în continuare o etichetă greșită — dar acum **greșeala are
un loc unde se vede**, fiindcă e o afirmație despre lume, nu un verdict.
"""
import pytest

from core import clasificator_alerte as ca

#: Măsurat 31.08.2026, pe commit `76ae256`. Instanța fondatoare: **2 din 2 greșite**, în direcții
#: OPUSE. Se coboară; nu se ridică. `masurate` nu poate SCĂDEA — altfel rata s-ar putea „îmbunătăți"
#: ștergând proba, ceea ce e chiar felul de îmbunătățire pe care clichetul există s-o interzică.
BASELINE_GRESITE = 2
BASELINE_MASURATE = 2


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    from core import db
    db.init_pool()
    with db.get_conn() as c:
        yield c


# ── PARTEA PURĂ — se probează fără bază și fără AI ───────────────────────────────────────────

def test_relevanta_se_DERIVA_din_cele_doua_fapte():
    """Miezul reparației: relevanța nu mai e o intrare, e o ieșire."""
    assert ca.relevanta_din("catre_contribuabil", []) == "zero"
    assert ca.relevanta_din("catre_anaf", ["D100"]) == "mare"
    assert ca.relevanta_din("catre_anaf", []) == "medie"


def test_cele_doua_acte_ar_fi_iesit_corect_din_fapte():
    """CALIBRAREA POZITIVĂ, pe cazul cunoscut — și e cazul care a cerut reparația.

    Ancorată pe **faptele** celor două acte, nu pe rândurile lor din bază: dacă ar fi ancorată pe
    rânduri, s-ar autodistruge la prima ștergere a lor (METODA §29). Faptele rămân adevărate despre
    acte oricâte rânduri s-ar șterge.
    """
    # 603/2026: ANAF emite Referat/Decizie CĂTRE contribuabil; nu schimbă nicio declarație de-a noastră
    assert ca.relevanta_din("catre_contribuabil", []) == "zero", "603/2026 ar ieși iar greșit"
    # 602/2026: schimbă nomenclatorul de obligații al D100
    assert ca.relevanta_din("catre_anaf", ["D100"]) == "mare", "602/2026 ar ieși iar greșit"


def test_necunoscutul_NU_se_rotunjeste_la_zero():
    """O direcție pe care predicția n-a putut-o stabili e o necunoaștere, nu o absență de impact.
    Rotunjită la `zero`, ar scoate actul din atenție exact când se știe cel mai puțin despre el."""
    assert ca.relevanta_din("necunoscut", []) == "medie"


def test_nomenclatoarele_sunt_INCHISE():
    """`zero` lipsea din vechiul nomenclator — deci un act care nu ne atinge deloc TREBUIA botezat
    `medie`. Minciuna era cerută de nomenclator, nu produsă de model."""
    assert set(ca.DIRECTII) == {"catre_contribuabil", "catre_anaf", "necunoscut"}
    assert set(ca.RELEVANTE) >= {"zero"}
    with pytest.raises(ValueError):
        ca.relevanta_din("altceva", [])


def test_nemasurat_NU_se_numara_ca_greseala():
    """Absența probei nu e probă. Altfel rata ar crește cu fiecare alertă nouă, nemăsurată."""
    assert ca.gresita("mare", None) is False
    assert ca.gresita("mare", "nemasurat") is False
    assert ca.gresita("mare", "zero") is True
    assert ca.gresita("zero", "zero") is False


# ── PARTEA PE DATE REALE ─────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_greselile_nu_cresc(conn):
    """Miezul clichetului. O predicție nouă care se dovedește greșită aprinde poarta."""
    r = ca.rata(conn)
    assert r["gresite"] <= BASELINE_GRESITE, (
        "predicții greșite ÎN CREȘTERE: %d > %d. Clasificatorul e pâlnia de intrare — tot ce vine "
        "de la ANAF se prioritizează pe el. Confruntă predicția cu ce s-a măsurat și repară "
        "extragerea faptelor, nu eticheta." % (r["gresite"], BASELINE_GRESITE))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_proba_nu_poate_fi_STEARSA_ca_sa_scada_rata(conn):
    """Direcția cealaltă de eludare, și e cea ieftină: rata se „îmbunătățește" ștergând măsurătorile.

    Perechea regulii de migrare de la interdicția 77 — acolo datoria se muta în umbră, aici proba
    dispare. Amândouă fac o cifră să scadă fără ca nimic să se fi reparat.
    """
    r = ca.rata(conn)
    assert r["masurate"] >= BASELINE_MASURATE, (
        "măsurători DISPĂRUTE: %d < %d. O rată care scade fiindcă s-a șters proba nu e o "
        "îmbunătățire." % (r["masurate"], BASELINE_MASURATE))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fiecare_masuratoare_isi_poarta_motivul_si_commitul(conn):
    """O măsurătoare fără motiv scris nu se poate reconstitui — devine o amintire, nu o cifră."""
    from psycopg2.extras import RealDictCursor
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, titlu, motiv_masurat, masurat_la, masurat_pe FROM public.alerte_fiscale "
                    "WHERE impact_masurat IS NOT NULL AND impact_masurat <> 'nemasurat'")
        rele = [r["id"] for r in cur.fetchall()
                if not (r["motiv_masurat"] and r["masurat_la"] and r["masurat_pe"])]
    assert not rele, (
        "măsurători fără motiv scris, dată sau commit: %s. O cifră care nu se poate recalcula nu e "
        "o măsurătoare, e o amintire." % rele)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_impactul_masurat_e_din_nomenclator(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT impact_masurat FROM public.alerte_fiscale "
                    "WHERE impact_masurat IS NOT NULL")
        val = {r[0] for r in cur.fetchall()}
    assert val <= set(ca.MASURATORI), (
        "valori de impact în afara nomenclatorului: %s" % sorted(val - set(ca.MASURATORI)))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_anti_vacuu_confruntarea_chiar_are_ce_compara(conn):
    """O rată `0 din 0` ar fi verde și n-ar spune nimic."""
    assert ca.rata(conn)["masurate"] > 0, "nicio alertă măsurată — confruntarea n-are obiect"


# ── PROMPT-UL NU MAI CERE UN VERDICT ─────────────────────────────────────────────────────────

def test_promptul_cere_FAPTE_nu_relevanta():
    """Dacă prompt-ul ar cere iar `relevanta`, verdictul s-ar strecura înapoi, iar derivarea din cod
    ar deveni decor. Se citește din sursă, pe STRUCTURA cererii JSON, nu după cuvinte în proză."""
    # Prompt-ul NU mai e un literal — se COMPUNE din `CAMPURI_CERUTE`, tocmai ca să nu existe două
    # adevăruri despre ce cere. Deci se citește rezultatul compunerii, nu nodul din AST: prima formă
    # a acestei probe citea `n.value.value` și a crăpat cu `BinOp has no attribute value` exact în
    # tura în care compunerea a fost introdusă.
    from core import monitor_fiscal
    prompt = monitor_fiscal.PROMPT
    assert prompt, "PROMPT nu se mai găsește în monitor_fiscal"
    # Pe STRUCTURA: prompt-ul se COMPUNE din `CAMPURI_CERUTE`, deci se confruntă mulțimea cerută
    # cu cea declarată — nu se caută șiruri în proza lui (clichet 50).
    ceruta = set(ca.CAMPURI_CERUTE)
    assert ceruta >= {"directie", "declaratii_atinse"}, "prompt-ul nu mai cere cele două fapte"
    assert ca.CAMP_INTERZIS not in ceruta, (
        "prompt-ul cere iar `%s` — verdictul s-a întors, iar derivarea din cod e decor"
        % ca.CAMP_INTERZIS)
    import re as _re
    numite = set(_re.findall(r'"(\w+)"', prompt.split("EXACT campurile:")[-1].split(chr(10))[0]))
    assert numite == ceruta, (
        "prompt-ul numește alte câmpuri decât cele declarate: %s vs %s — două adevăruri despre ce "
        "cere" % (sorted(numite), sorted(ceruta)))
