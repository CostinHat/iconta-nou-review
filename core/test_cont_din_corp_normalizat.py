# -*- coding: utf-8 -*-
"""core/test_cont_din_corp_normalizat.py — un cont luat din CORPUL CERERII trece prin strip().

DE UNDE VINE (masurat 26.08.2026, pe AST): tiparul
    str(corp.get("cont_x") or "<implicit>")
arata ca o garda si e o MASCA. `or` transforma None si "" in implicit, dar lasa "   " sa treaca
VERBATIM in `inregistrari_linii`. Consecinta, probata pe schema efemera:
  - `NOT NULL` nu-l opreste (spatiile nu sunt NULL);
  - un `CHECK (cont <> '')` nu l-ar fi oprit (spatiile nu sunt sirul gol);
  - si pana la reparatia din aceeasi zi NICIUNA din cele doua verificari de echilibru nu-l vedea,
    fiindca `if l.get("cont_debit")` e ADEVARAT pe "   ".
Clasa avea 19 situri (main.py, core/inventariere.py, core/stocuri_cv_api.py), toate reparate cu
tiparul deja corect din acelasi cod: `(str(corp.get("x") or "").strip() or "<implicit>")`.

ASERTEAZA PE STRUCTURA, nu pe text (clichet 50): se cauta in AST daca nodul care citeste contul
are un stramos `.strip()` care il CONTINE — nu daca sirul ".strip()" apare pe aceeasi linie.

MODURILE DE ESEC ALE GARDULUI, scrise INAINTE (interdictia 76):
  H1 corpul cererii sub alt nume decat corp/date/body/payload -> NEVAZUT. Domeniul e declarat.
  H2 normalizarea intr-o functie chemata (`_cont(corp, "x")`) -> ar aparea ca neacoperit, adica
     FALS POZITIV, nu fals negativ. Directia sigura.
  H3 cheie care nu incepe cu "cont" (ex. "debit") -> NEVAZUT; masurat: nu exista azi.
  H4 fisiere de test -> excluse deliberat (fixturile au voie sa construiasca date rupte).
"""
import ast
import io
import os

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPURI = {"corp", "date", "body", "payload"}

# Situri care au voie sa NU fie normalizate, fiecare cu motivul. Gol = nimic tolerat.
PIN = {}


def _fisiere():
    out = [os.path.join(RAD, "main.py")]
    cd = os.path.join(RAD, "core")
    for f in sorted(os.listdir(cd)):
        if f.endswith(".py") and not f.startswith("test_") and not f.startswith("scan_"):
            out.append(os.path.join(cd, f))
    return out


def _e_cont(cheie):
    """Cheia numeste un CONT contabil, nu orice incepe cu «cont».

    Calibrare negativa gasita de gard pe el insusi, la prima rulare: `corp.get("continut")` --
    continutul unui mesaj -- trecea drept cont si producea un fals pozitiv. Prefixul brut "cont"
    e prea larg; forma reala e `cont` exact, sau `cont_<ceva>`."""
    return bool(cheie) and (cheie == "cont" or cheie.startswith("cont_"))


def _parinti(arb):
    p = {}
    for n in ast.walk(arb):
        for c in ast.iter_child_nodes(n):
            p[c] = n
    return p


def _sub_strip(nod, par):
    """Nodul e NORMALIZAT? Structural, nu textual — se cauta un STRAMOS care il curata.

    Doua forme trec, si a doua o subsumeaza pe prima:
      - `.strip()` direct pe expresie (forma din 26.08, dimineata);
      - un apel `cont_valid.cere_cont(...)`, care normalizeaza SI confrunta cu planul firmei
        (forma de dupa decizia lui Costin). A cere `.strip()` in plus ar fi doua verificari
        suprapuse — exact ce nu vrem intr-un singur loc de adevar (P1)."""
    cur = nod
    while cur in par:
        cur = par[cur]
        if isinstance(cur, ast.Call) and isinstance(cur.func, ast.Attribute):
            if cur.func.attr in ("strip", "cere_cont"):
                return True
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            return False
    return False


def _citiri_de_cont():
    """[(fisier:linie, expresie, normalizat)] pentru fiecare citire de cont din corpul cererii."""
    gasite = []
    for cale in _fisiere():
        rel = os.path.relpath(cale, RAD)
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        par = _parinti(arb)
        for n in ast.walk(arb):
            cheie = baza = None
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
                    and n.args and isinstance(n.args[0], ast.Constant)
                    and isinstance(n.args[0].value, str)):
                cheie, baza = n.args[0].value, n.func.value
            elif (isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                  and isinstance(n.slice.value, str)):
                cheie, baza = n.slice.value, n.value
            if not _e_cont(cheie):
                continue
            if not (isinstance(baza, ast.Name) and baza.id in CORPURI):
                continue
            gasite.append(("%s:%d" % (rel, n.lineno), ast.unparse(n), _sub_strip(n, par)))
    return gasite


@pytest.fixture(scope="module")
def citiri():
    g = _citiri_de_cont()
    # ANTI-VACUU: un gard care nu gaseste nimic raporteaza verde despre o lume pe care n-o vede.
    assert len(g) >= 15, (
        "sonda a gasit doar %d citiri de cont din corpul cererii — clasa masurata pe 26.08.2026 "
        "avea 19 situri reparate plus cele deja corecte. Sub prag inseamna ca sonda s-a rupt "
        "(redenumire de variabila, alt tipar), nu ca s-a curatat codul." % len(g))
    return g


def test_orice_cont_din_corpul_cererii_trece_prin_strip(citiri):
    rele = [(u, e) for (u, e, ok) in citiri if not ok and u not in PIN]
    assert not rele, (
        "%d citire(i) de cont din corpul cererii NU trec prin strip() — un cont format din spatii "
        "ajunge verbatim in evidenta, iar acolo nu-l opreste nici NOT NULL, nici un CHECK pe sirul "
        "gol:\n%s" % (len(rele), "\n".join("  %s   ->  %s" % (u, e[:110]) for u, e in rele)))


def test_sonda_chiar_vede_un_sit_nenormalizat():
    """CALIBRARE POZITIVA pe propriul mod de esec: daca sonda n-ar deosebi normalizat de
    nenormalizat, testul de mai sus ar fi verde pe orice cod."""
    arb = ast.parse('x = str(corp.get("cont_venit") or "707")\n'
                    'y = (str(corp.get("cont_stoc") or "").strip() or "371")\n')
    par = _parinti(arb)
    stari = {}
    for n in ast.walk(arb):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
                and n.args and isinstance(n.args[0], ast.Constant)):
            stari[n.args[0].value] = _sub_strip(n, par)
    assert stari == {"cont_venit": False, "cont_stoc": True}, stari


def test_pinul_e_gol_sau_motivat():
    """Un sit tolerat fara motiv scris ar face din clichet o lista de ignorat."""
    for unde, motiv in PIN.items():
        assert isinstance(motiv, str) and len(motiv) > 40, \
            "%s e in PIN fara motiv scris" % unde

# ============================================================================
#  PARTEA A DOUA (26.08.2026) — confruntarea cu PLANUL, nu doar curatarea
# ============================================================================
# DECIZIA lui Costin: *„o intrare din afara unui nomenclator de registru se REFUZA, nu se
# semnaleaza."* Normalizarea de mai sus opreste contul ALB; nu opreste contul GRESIT — `7O7`
# cu litera O, sau `9999` care nu exista in planul firmei. Confruntarea traieste intr-un
# singur loc: `core/cont_valid.cere_cont`.
#
# CE PAZESTE CLICHETUL: multimea citirilor de cont care NU trec inca prin `cere_cont` nu
# poate CRESTE. Fiecare intrare poarta motivul pentru care n-a fost legata inca — o lista
# fara motive ar fi o lista de tolerat.

# Citiri de cont care inca nu trec prin `cere_cont`, cu motivul fiecareia.
NELEGATE = {
    "main.py::factura_primita_valideaza::corp.get('cont')":
        "citirea e INAINTE de `with db.get_conn()`, deci nu exista nici conn, nici schema in acel "
        "punct, si nu e intr-un `try` care prinde ValueError — un refuz de acolo ar iesi 500. "
        "Se leaga mutand citirea in interiorul blocului, ca la /export-extracomunitar",
    "core/firma_profil_api.py::salveaza_date::date.get('cont_venit_implicit')":
        "e o PREFERINTA de profil, nu un cont dintr-o nota, iar `salveaza_date(conn, date)` n-are "
        "`schema` in semnatura. Confruntarea are sens la FOLOSIRE, acolo unde preferinta ajunge "
        "intr-o linie de inregistrare — altfel s-ar refuza salvarea unei preferinte inca nefolosite",
    "core/inventariere.py::pregateste_mf_plus::corp.get('cont_imobilizare')":
        "`pregateste_mf_plus(corp)` e PUR — verificat la sursa: nu primeste nici conn, nici schema. "
        "Ridica deja ValueError, deci refuzul ar iesi corect; ce lipseste e planul firmei, care cere "
        "schimbarea semnaturii. Se schimba odata cu sora ei de mai jos, nu separat",
    "core/inventariere.py::pregateste_mf_plus::corp.get('cont_amortizare')":
        "acelasi modul pur si aceeasi schimbare de semnatura ca mai sus; legate separat ar lasa "
        "jumatate din mijlocul fix confruntat cu planul si jumatate nu",
    "core/stocuri_cv_api.py::intrare::corp.get('cont_stoc')":
        "are conn+schema — deci SE POATE lega; nu s-a facut fiindca acolo contul intra in `articole` "
        "ca implicit al articolului, nu intr-o linie de inregistrare. Ajunge in evidenta abia prin "
        "miscarea de stoc, iar confruntarea la ambele capete ar fi doua locuri. Consemnat, nu facut",
    "core/stocuri_cv_api.py::intrare::corp.get('cont_cheltuiala')":
        "acelasi INSERT in `articole` ca mai sus, aceeasi conditie: se leaga acolo unde contul "
        "articolului devine linie de inregistrare, nu la definirea articolului",
    "core/stocuri_cv_api.py::reclasificare::corp.get('cont_stoc_nou')":
        "are conn+schema, dar functia isi intoarce refuzurile ca dict `{eroare: ...}`, nu le ridica. "
        "Un `cere_cont` care ridica ValueError ar iesi din contractul rutei; legarea cere intai "
        "alegerea unui singur fel de refuz pentru modul",
    "core/stocuri_cv_api.py::reclasificare::corp.get('cont_cheltuiala_nou')":
        "acelasi contract de refuz prin dict ca mai sus; se schimba amandoua odata sau niciuna, "
        "altfel acelasi apel ar refuza in doua feluri",
}


def _fn_care_contine(nod, par):
    """Functia care contine nodul. Cheia clichetului sta pe NUME, nu pe linie: liniile se muta
    la orice editare, deci un clichet ancorat pe ele ar pica din alt motiv decat cel pazit."""
    cur = nod
    while cur in par:
        cur = par[cur]
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur.name
    return "(modul)"


def _sub_cere_cont(nod, par):
    """Nodul e CONFRUNTAT cu planul firmei? Structural: are un strămoș `…cere_cont(…)` care îl
    conține.

    Prima formă a acestei funcții căuta șirul `"cere_cont("` într-o fereastră de linii — adică
    exact aserțiunea pe text pe care clichetul 50 o interzice, scrisă chiar în gardul care
    păzește altceva. A prins-o scanul, nu eu. Forma pe AST n-are nici fereastră, nici prag de
    proximitate: sau apelul conține nodul, sau nu."""
    cur = nod
    while cur in par:
        cur = par[cur]
        if isinstance(cur, ast.Call):
            f = cur.func
            if getattr(f, "attr", None) == "cere_cont" or getattr(f, "id", None) == "cere_cont":
                return True
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            return False
    return False


def _citiri_cu_context():
    out = []
    for cale in _fisiere():
        rel = os.path.relpath(cale, RAD)
        try:
            src = io.open(cale, encoding="utf-8").read()
            arb = ast.parse(src)
        except SyntaxError:
            continue
        par = _parinti(arb)
        for n in ast.walk(arb):
            cheie = baza = None
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
                    and n.args and isinstance(n.args[0], ast.Constant)
                    and isinstance(n.args[0].value, str)):
                cheie, baza = n.args[0].value, n.func.value
            elif (isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                  and isinstance(n.slice.value, str)):
                cheie, baza = n.slice.value, n.value
            if not _e_cont(cheie) or not (isinstance(baza, ast.Name) and baza.id in CORPURI):
                continue
            fn = _fn_care_contine(n, par)
            out.append(("%s::%s::%s" % (rel, fn, ast.unparse(n)),
                        "%s:%d" % (rel, n.lineno),
                        _sub_cere_cont(n, par)))
    return out


def test_clichetul_celor_neconfruntate_nu_creste():
    """Un cont din corpul cererii care NU trece prin `cere_cont` e o intrare din afara
    nomenclatorului care se poate scrie. Multimea lor nu are voie sa creasca."""
    citiri = _citiri_cu_context()
    assert len(citiri) >= 15, "sonda a gasit doar %d citiri — s-a rupt, nu s-a curatat codul" % len(citiri)
    nelegate = sorted({cheie for cheie, _unde, legat in citiri if not legat})
    noi = [x for x in nelegate if x not in NELEGATE]
    assert not noi, (
        "citiri de cont care nu se confrunta cu planul firmei si nu sunt in clichet (%d):\n%s\n"
        "Ori se leaga prin `cont_valid.cere_cont`, ori intra in NELEGATE cu motivul scris."
        % (len(noi), "\n".join("  " + x for x in noi)))


def test_clichetul_scade_sau_ramane():
    """Cealalta directie: o intrare care S-A legat nu are voie sa ramana in clichet — altfel
    lista devine o amintire despre o lume care s-a schimbat (aceeasi clasa cu PIN-ul din
    test_module_nelegate)."""
    citiri = _citiri_cu_context()
    nelegate = {cheie for cheie, _u, legat in citiri if not legat}
    ramase = [x for x in NELEGATE if x not in nelegate]
    assert not ramase, (
        "intrari in NELEGATE care s-au legat intre timp (%d): %s — se scot din clichet"
        % (len(ramase), ", ".join(ramase)))


def test_fiecare_nelegata_poarta_motivul():
    for cheie, motiv in NELEGATE.items():
        assert isinstance(motiv, str) and len(motiv) > 60, "%s e in clichet fara motiv scris" % cheie


def test_refuzul_e_o_STRUCTURA_cu_contul_campul_si_locul():
    """Cerinta lui Costin: *„sa spuna CE cont nu exista si UNDE se creeaza."*

    Se aserteaza pe `e.detalii`, nu pe fraza. Motivul e clichetul 50: o garda ancorata pe
    formulare pica la orice rescriere a mesajului si trece la orice pierdere de continut —
    exact pe dos decat trebuie."""
    from core import cont_valid as cv
    with pytest.raises(cv.ContNecunoscut) as ex:
        cv._refuz("7O7", "cont_venit", [("707", "Venituri din vanzarea marfurilor")])
    d = ex.value.detalii
    assert d["fel"] == "necunoscut"
    assert d["cont"] == "7O7", "refuzul nu poarta CONTUL: %r" % d
    assert d["camp"] == "cont_venit", "refuzul nu poarta CAMPUL: %r" % d
    assert d["unde"] == cv.UNDE_SE_CREEAZA, "refuzul nu poarta LOCUL unde se creeaza: %r" % d
    assert d["apropiate"] == [("707", "Venituri din vanzarea marfurilor")]


def test_refuzul_pe_absenta_e_alt_FEL_nu_acelasi_mesaj():
    """Absenta si inexistenta sunt doua lucruri diferite, si omul trebuie sa le poata deosebi:
    la prima completeaza, la a doua creeaza contul."""
    from core import cont_valid as cv
    # `_fara_cont` CONSTRUIESTE refuzul, nu-l ridica — de aceea se ridica aici.
    with pytest.raises(cv.ContNecunoscut) as ex:
        raise cv._fara_cont("cont_stoc")
    assert ex.value.detalii["fel"] == "lipsa"
    assert ex.value.detalii["cont"] is None
    assert ex.value.detalii["camp"] == "cont_stoc"


def test_randarea_foloseste_TOATE_campurile_structurii():
    """Anti-pierdere: o structura completa a carei randare nu o arata e la fel de inutila ca
    absenta ei. Se verifica prin MUTATIE pe date: se schimba fiecare camp si se cere ca fraza
    sa se schimbe — fara sa se asertea ce fraza anume."""
    from core import cont_valid as cv
    baza = {"fel": "necunoscut", "cont": "9999", "camp": "cont_stoc",
            "unde": cv.UNDE_SE_CREEAZA, "apropiate": []}
    referinta = cv.randeaza(baza)
    for camp, alta in (("cont", "8888"), ("camp", "cont_venit"), ("unde", "Alt loc"),
                       ("apropiate", [("999", "Ceva")])):
        variat = dict(baza, **{camp: alta})
        assert cv.randeaza(variat) != referinta, (
            "randarea nu foloseste campul %r — structura il poarta, dar omul nu-l vede" % camp)


def test_normalizarea_si_confruntarea_sunt_acelasi_loc():
    """P1: un singur loc pentru «ce e un cont valabil». Daca `normalizeaza` s-ar dubla, cele
    doua jumatati ale lui R54 ar putea diverge."""
    from core import cont_valid as cv
    assert cv.normalizeaza("  707 ") == "707"
    assert cv.normalizeaza(None) == ""
    assert cv.normalizeaza("   ") == ""
