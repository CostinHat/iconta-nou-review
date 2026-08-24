# -*- coding: utf-8 -*-
"""GARD — D112 ȘI D300 se confruntă cu ce s-a DEPUS, când s-a păstrat; altfel o spun.

**Interdicția 32, la nivelul pe care ea îl numește.** Cele două măsurători de dinainte (22.08, 24.08)
au fost un nivel mai jos — pe *înregistrare*. Aici se pornește din **poziția depusă**.

**Ce s-a găsit, măsurat 24.08.2026 pe date reale:**
- `public.declaratii_depuse` are coloanele `xml` și `randuri`, dar **0 din 54** de depuneri le au
  populate — fiindcă toate cele 54 vin din **importul istoric**, care consemnează *că* s-a depus, nu
  *ce* s-a depus. Calea de coadă (`coada_api.py:300`) **le persistă**; ea n-a fost încă folosită.
- Din patru verificări încrucișate, **una singură citea ce s-a depus** (`verifica_d390`, prin
  `_d300_depus_randuri`). Celelalte trei **regenerau** declarația din datele de azi.

**De ce contează.** O verificare care regenerează compară *evidența de azi* cu *declarația care s-ar
genera azi*. Divergența care contează — între ce ține ANAF și ce spun registrele — **nu poate apărea**
în ea. Iar o poziție de declarație nu se poate desface până la document dacă nici declarația nu se
păstrează: lanțul n-are capăt de pornire.

**CE FACE IMPOSIBIL:** ca D112 să prefere tăcut regenerarea când există declarația depusă, și ca
regenerarea să fie prezentată fără să-și spună limita.

**CE NU VERIFICĂ, declarat:** dacă valorile coincid pe o firmă anume — aia cere baza de date, e o
probă, nu un gard. Și nu repară celelalte două verificări care regenerează (`verifica_tva`), fiindcă
acolo fereastra TVA are reguli proprii — rămâne în **R40**.

**Disciplina celor trei valori nu e inventată aici**: `compara_d390_vs_d300` o are deja — `randuri is
None` -> GRI, *„absența datelor nu e divergență"*. Reparația asta o **aplică**, nu o introduce.
"""
import ast
import io
import os

from core.control_incrucisat import compara_d112

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DECL = {"602": 100, "412": 250, "432": 100, "480": 22}
RULAJ = {c: {"debit": 0, "credit": 0} for c in ("421", "4315", "4316", "436")}


def _constatari(**kw):
    r = compara_d112(DECL, RULAJ, **kw)
    assert r, "compara_d112 n-a produs nicio constatare — gardul ar trece pe gol"
    return r


# ── DIN CE s-a comparat e un CÂMP, nu un cuvânt în proză ─────────────────────
def test_sursa_declaratului_e_camp_in_constatare():
    """Structura, nu textul: un consumator întreabă câmpul, nu caută un cuvânt în temei."""
    assert {c["sursa_declarat"] for c in _constatari(sursa_declarat="depus")} == {"depus"}
    assert {c["sursa_declarat"] for c in _constatari(sursa_declarat="regenerat")} == {"regenerat"}


def test_implicitul_e_REGENERAT_nu_depus():
    """Dacă apelantul uită să spună, se presupune varianta mai slabă, nu cea mai tare.
    Un implicit optimist ar afirma despre depunere fără s-o fi citit — interdicția 10."""
    assert {c["sursa_declarat"] for c in _constatari()} == {"regenerat"}


def test_regenerarea_isi_declara_limita_SI_IN_TEXTUL_CITIT_DE_OM():
    """PE TEXT, ȘI DE CE — singura aserțiune textuală din fișier, cu motivul scris.

    Câmpul `sursa_declarat` e pentru mașini. Temeiul e ce **citește contabilul**, iar cerința aici e
    tocmai că fraza destinată lui **spune limita** — nu că există un câmp. Nu există structură sub
    o propoziție: subiectul aserțiunii ESTE proza. Perechea ei structurală e testul de mai sus.

    Nu e într-o buclă, ca să nu poată trece pe listă goală (suprapunerea 18/19, METODA §23)."""
    t = _constatari(sursa_declarat="regenerat")[0]["temei"]
    assert "nu s-a păstrat ce s-a depus" in t, (
        "limita nu e scrisă în temei — cititorul crede că s-a comparat cu depunerea:\n  %s" % t)


def test_CALIBRARE_cele_doua_surse_dau_temeiuri_DIFERITE():
    """Anti-vacuu: dacă ambele ar da același text, testul de mai sus ar trece degeaba."""
    a = _constatari(sursa_declarat="depus")[0]["temei"]
    b = _constatari(sursa_declarat="regenerat")[0]["temei"]
    assert a != b, "sursa declaratului nu schimbă temeiul — parametrul e decorativ"


def _functia(nume):
    arb = ast.parse(io.open(os.path.join(RAD, "core", "control_incrucisat.py"),
                            encoding="utf-8").read())
    for n in ast.walk(arb):
        if isinstance(n, ast.FunctionDef) and n.name == nume:
            return n
    raise AssertionError("nu mai găsesc `%s` — gardul măsoară ce nu vede" % nume)


def test_verificarea_chiar_intreaba_de_ce_s_a_depus():
    apeluri = {getattr(n.func, "attr", None) or getattr(n.func, "id", None)
               for n in ast.walk(_functia("verifica_d112")) if isinstance(n, ast.Call)}
    assert apeluri >= {"_d112_depus_xml"}, (
        "`verifica_d112` nu mai consultă declarația depusă — compară iar azi cu azi")


def test_preferinta_ajunge_in_temei():
    """Apelul ar putea exista și rezultatul lui ignorat. Se cere ca `sursa_declarat` să fie
    **transmis** mai departe, ca argument cu nume, la `compara_d112`."""
    fn = _functia("verifica_d112")
    trimis = any(
        isinstance(n, ast.Call)
        and (getattr(n.func, "attr", None) or getattr(n.func, "id", None)) == "compara_d112"
        and any(k.arg == "sursa_declarat" for k in n.keywords)
        for n in ast.walk(fn))
    assert trimis, "`sursa_declarat` nu mai ajunge la `compara_d112` — preferința rămâne fără efect"


def test_cititorul_depusului_are_cale_de_NECUNOSCUT():
    """Trei valori, nu două: `None` = nu se poate ști ce s-a depus."""
    fn = _functia("_d112_depus_xml")
    assert any(isinstance(n, ast.Return) and isinstance(n.value, ast.Constant)
               and n.value.value is None for n in ast.walk(fn)), (
        "`_d112_depus_xml` n-are ieșire cu `None` — necunoscutul nu mai poate fi declarat")


def test_citeste_depunerea_CURENTA_nu_orice_depunere():
    """O firmă poate depune de mai multe ori aceeași perioadă (rectificative). Comparația trebuie să
    stea pe cea în vigoare, altfel apără o cifră înlocuită."""
    sql = "\n".join(n.value for n in ast.walk(_functia("_d112_depus_xml"))
                    if isinstance(n, ast.Constant) and isinstance(n.value, str))
    assert "declaratii_depuse_curente" in sql, (
        "nu se citește din `declaratii_depuse_curente` — o rectificativă n-ar fi luată în seamă")


# ═══ D300: aceeași disciplină, plus cheia ferestrei TVA ══════════════════════
from core.control_incrucisat import compara_tva  # noqa: E402

R_TVA = {"R17_2": 100, "R27_2": 50}
RULAJ_TVA = {"4427": {"credit": 100, "debit": 0}, "4426": {"debit": 50, "credit": 0}}


def _constatari_tva(**kw):
    r = compara_tva(R_TVA, RULAJ_TVA, 2026, 6, **kw)
    assert r, "compara_tva n-a produs nicio constatare — gardul ar trece pe gol"
    return r


def test_D300_sursa_declaratului_e_camp():
    assert {c["sursa_declarat"] for c in _constatari_tva(sursa_declarat="depus")} == {"depus"}
    assert {c["sursa_declarat"] for c in _constatari_tva(sursa_declarat="regenerat")} == {"regenerat"}


def test_D300_implicitul_e_REGENERAT():
    assert {c["sursa_declarat"] for c in _constatari_tva()} == {"regenerat"}


def test_D300_verificarea_intreaba_de_ce_s_a_depus():
    apeluri = {getattr(n.func, "attr", None) or getattr(n.func, "id", None)
               for n in ast.walk(_functia("verifica_tva")) if isinstance(n, ast.Call)}
    assert apeluri >= {"_d300_depus_randuri"}, (
        "`verifica_tva` nu mai consultă decontul depus — compară iar azi cu azi")


def test_D300_preferinta_ajunge_la_comparatie():
    trimis = any(
        isinstance(n, ast.Call)
        and (getattr(n.func, "attr", None) or getattr(n.func, "id", None)) == "compara_tva"
        and any(k.arg == "sursa_declarat" for k in n.keywords)
        for n in ast.walk(_functia("verifica_tva")))
    assert trimis, "`sursa_declarat` nu mai ajunge la `compara_tva`"


def test_D300_cauta_pe_ULTIMA_LUNA_A_FERESTREI_nu_pe_luna_curenta():
    """Partea subtilă, și singura care ar regresa TĂCUT.

    Coada scrie depunerea cu **eticheta decontului** — pentru trimestriali luna 3/6/9/12, nu luna
    calendaristică. O căutare pe `luna` ar nimeri doar firmele lunare și ar rata sistematic
    trimestrialii, fără să spună nimic: ar cădea liniștit înapoi pe regenerare, adică exact
    comportamentul de dinainte, dar cu un temei care pretinde că s-a căutat.

    Structural: argumentele apelului trebuie să fie `.year`/`.month` ale unei date derivate din
    fereastră — nu numele `an`/`luna` primite de funcție."""
    apel = [n for n in ast.walk(_functia("verifica_tva"))
            if isinstance(n, ast.Call)
            and (getattr(n.func, "attr", None) or getattr(n.func, "id", None)) == "_d300_depus_randuri"]
    assert len(apel) == 1, "aștept exact un apel de căutare a depunerii, am găsit %d" % len(apel)
    argumente = apel[0].args[-2:]
    assert all(isinstance(a, ast.Attribute) for a in argumente), (
        "căutarea depunerii nu folosește o dată derivată din fereastra TVA: %r"
        % [ast.dump(a)[:60] for a in argumente])
    assert [a.attr for a in argumente] == ["year", "month"], (
        "argumentele nu sunt (an, lună) ale unei date — %r" % [a.attr for a in argumente])
    nume = {getattr(a.value, "id", None) for a in argumente}
    assert nume == {"_ult"}, (
        "data folosită nu e ultima lună a ferestrei (`_ult`), ci %r — trimestrialii ar fi ratați "
        "tăcut" % nume)


def test_CALIBRARE_D300_cele_doua_surse_dau_temeiuri_DIFERITE():
    a = _constatari_tva(sursa_declarat="depus")[0]["temei"]
    b = _constatari_tva(sursa_declarat="regenerat")[0]["temei"]
    assert a != b, "sursa declaratului nu schimbă temeiul la D300 — parametrul e decorativ"
