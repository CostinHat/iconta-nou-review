# -*- coding: utf-8 -*-
"""GARD [R81, DECIS 28.08.2026]: denumirea unei firme se scrie în AMÂNDOUĂ locurile sau în niciunul.

DECIZIA lui Costin, în cuvintele lui: *„orice act care redenumește o firmă scrie denumirea în AMBELE
locuri (`public.tenants.nume` și `{schema}.firma_profil.nume`), în aceeași tranzacție, cu aceeași
valoare. Nu se construiește alias."*

DE UNDE VINE. Trei căi redenumeau o firmă, și fiecare atingea **un singur loc din două**:
`PUT /tenants/{id}` și ramura `anaf` scriau numai portofoliul, iar ecranul „Date firmă" scria numai
denumirea fiscală. Consecința probată pe 27.08: alegerea *„Ia denumirea de la ANAF"*, apăsată de un
om, **nu ajungea pe hârtie** — pe D100, D205 și pe bilanț pleca mai departe cealaltă denumire. A
patra cale, pe care măsurătoarea de atunci n-o găsise, a ieșit la lumină de-abia din scanul ăsta:
`precompleteaza_din_anaf(seteaza_nume=True)` scria `firma_profil.nume` singur, la `POST /auth/register`.

CE FACE IMPOSIBIL:
  1. o funcție care scrie `nume` pe una din cele două tabele și nu pe cealaltă;
  2. **o a cincea cale de redenumire care ocolește scriitorul unic** — fiecare cale cunoscută
     trebuie să treacă prin el, verificat pe apel, în AST;
  3. un `commit()` strecurat între cele două scrieri, care ar rupe tranzacția în două;
  4. dispariția porții de unicitate de pe traseul redenumirii;
  5. crearea care ar scrie denumirea într-un singur loc (`provision_tenant`, pe `INSERT`).

CE NU FACE, declarat:
  - **nu verifică VALOAREA.** Că amândouă primesc același șir se probează pe date, în tranzacție
    întoarsă la savepoint (O5), nu se citește din AST.
  - **nu urmărește apelurile în adâncime.** Dacă cineva scrie o funcție-intermediar care cheamă
    doar jumătate din scriitor, gardul n-o vede — dar nici n-ar avea ce, fiindcă scriitorul e o
    singură funcție care le face pe amândouă.
  - **nu acoperă scrierile din afara aplicației** (SQL de mână, semănătoare). Chiar așa au apărut
    cele patru divergențe de fixtură.
"""
import ast
import io
import os
import re

from core import scan_simetrie_denumire as s

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TP = os.path.join(_RAD, "core", "tenant_provisioning.py")

# Scriitorul unic. Nu e o preferință de stil: două perechi de `UPDATE`-uri scrise separat s-ar
# putea despărți la fel de tăcut ca cele trei scrieri singure de la care a pornit R81.
SCRIITORUL = ("core/tenant_provisioning.py", "scrie_denumirea")

# Toate căile prin care denumirea unei firme se poate schimba, cu ruta lor. Lista e o DECLARAȚIE —
# dacă apare a cincea, ea trebuie adăugată aici, iar `test_toate_caile_trec_prin_scriitorul_unic`
# o obligă să treacă prin scriitor.
CAILE = {
    ("core/tenant_provisioning.py", "actualizeaza_tenant"): "PUT /tenants/{id}",
    ("core/tenant_provisioning.py", "alege_denumirea"): "POST /tenants/{id}/nume-ales, ramura anaf",
    ("core/tenant_provisioning.py", "precompleteaza_din_anaf"): "POST /auth/register (firma proprie)",
    ("core/firma_profil_api.py", "salveaza_date"): "POST /tenants/{id}/firma-profil/date",
}


def _arbore(rel):
    return ast.parse(io.open(os.path.join(_RAD, rel), encoding="utf-8").read())


def _functia(rel, nume):
    fn = next((n for n in ast.walk(_arbore(rel))
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nume), None)
    assert fn is not None, "funcția `%s` din `%s` nu mai există" % (nume, rel)
    return fn


def _cheama(fn, tinta):
    for c in ast.walk(fn):
        if not isinstance(c, ast.Call):
            continue
        n = c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", None)
        if n == tinta:
            return True
    return False


# ─────────────────────────────────────────────── verdictul, pe arborele real
def test_nicio_scriere_asimetrica():
    rele = s.asimetrii()
    assert not rele, (
        "funcții care scriu denumirea într-un singur loc din două (%d):\n  %s\n"
        "R81 e decisă: simetrie de scriere. Trece scrierea prin "
        "`tenant_provisioning.scrie_denumirea`, care le face pe amândouă în aceeași tranzacție."
        % (len(rele), "\n  ".join("%s::%s scrie %s, lipsește `%s` (l.%d)" % r for r in rele)))


def test_exact_o_functie_scrie_denumirea():
    """Anti-vacuu **și** regulă: dacă lista se golește, gardul de mai sus devine adevărat despre o
    lume în care nimeni nu mai scrie denumirea; dacă are doi membri, simetria are două
    implementări care se pot despărți în tăcere (instanța: R62)."""
    assert s.simetrice() == [SCRIITORUL], (
        "scriitorul denumirii nu mai e unul singur: %s" % (s.simetrice(),))


def test_niciun_SET_compus_nou_pe_cele_doua_tabele():
    """Clasa despre care instrumentul nu poate afirma nimic singur. Azi e goală; dacă apare una,
    se citește cu ochii și se declară — nu se lasă să treacă drept «nu scrie denumirea»."""
    assert s.compuse() == [], (
        "`UPDATE`-uri cu `SET` asamblat la rulare, care POT scrie denumirea: %s" % (s.compuse(),))


def test_toate_caile_trec_prin_scriitorul_unic():
    """[2] Ce nu poate spune scanul de simetrie: că nu există o cale care scrie *altfel*. Aici se
    cere explicit ca fiecare cale cunoscută să cheme scriitorul."""
    fara = [(rel, fn, ruta) for (rel, fn), ruta in sorted(CAILE.items())
            if not _cheama(_functia(rel, fn), "scrie_denumirea")]
    assert not fara, (
        "căi care schimbă denumirea fără să treacă prin scriitorul unic:\n  %s"
        % "\n  ".join("%s::%s (%s)" % x for x in fara))


def test_cele_doua_scrieri_sunt_in_ACEEASI_tranzactie():
    """[3] Simetria **este** o proprietate a tranzacției: două scrieri corecte separate de un
    `commit()` lasă o fereastră în care cele două denumiri diferă, iar o cădere în fereastra aia
    produce exact divergența pe care regula o interzice."""
    fn = _functia(*SCRIITORUL)
    interzise = [c for c in ast.walk(fn)
                 if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                 and c.func.attr in ("commit", "rollback")]
    assert not interzise, (
        "`scrie_denumirea` face `commit`/`rollback` (%d apeluri) — tranzacția e a apelantului, "
        "altfel cele două scrieri se pot despărți" % len(interzise))


def test_poarta_de_unicitate_e_pe_traseul_redenumirii():
    """[4] O regulă care se poate ocoli printr-o redenumire nu e o regulă (lecția din 27.08)."""
    assert _cheama(_functia(*SCRIITORUL), "cere_nume_unic"), (
        "scriitorul unic nu mai trece prin `cere_nume_unic` — atunci o redenumire poate produce "
        "două firme cu același nume în același cabinet, ceea ce crearea refuză")


def test_crearea_scrie_denumirea_in_AMANDOUA_locurile():
    """[5] `provision_tenant` scrie prin `INSERT`, deci scanul de `UPDATE` n-o vede. Fără asta,
    divergența s-ar putea naște chiar la creare — și nimic n-ar spune-o."""
    fn = _functia("core/tenant_provisioning.py", "provision_tenant")
    re_insert = re.compile(
        # prefixul de schema poate fi si o interpolare (`f"… {schema}.firma_profil …"`), care
        # ajunge aici ca marcaj — deci se accepta orice pana la punct, nu doar identificatori.
        r'^INSERT INTO\s+(?:[^\s(]+\.)?"?(tenants|firma_profil)"?\s*\(([^)]*)\)', re.I)
    tinte = set()
    for nod, sql in s._executari(fn):
        m = re_insert.match(sql)
        if not m:
            continue
        coloane = {c.strip().lower() for c in m.group(2).split(",")}
        if not coloane >= {"nume"}:
            continue
        nume_arg = {x.id for x in ast.walk(nod) if isinstance(x, ast.Name)}
        tinte.add((m.group(1).lower(), nume_arg >= {"nume"}))
    assert tinte == {("tenants", True), ("firma_profil", True)}, (
        "crearea nu mai scrie ACEEAȘI variabilă `nume` în amândouă locurile: %s" % sorted(tinte))


# ─────────────────────────────────────────────── calibrare, ambele direcții
_SIMETRIC = '''
def f(conn, tid, nume):
    with conn.cursor() as cur:
        cur.execute("UPDATE public.tenants SET nume = %s WHERE id = %s", (nume, tid))
        cur.execute('UPDATE "%s".firma_profil SET nume = %%s WHERE id = 1' % schema, (nume,))
'''


def test_CALIBRARE_forma_corecta_NU_e_raportata():
    an = s.analizeaza_sursa("x.py", _SIMETRIC)
    assert sorted((t, fel) for _r, _f, t, fel, _l in an) == [
        ("firma_profil", "nume"), ("tenants", "nume")]


def test_CALIBRARE_o_scriere_pe_una_singura_E_PRINSA():
    """Modul de eșec pe care regula îl interzice, în forma lui exactă: chiar codul de ieri."""
    sursa = _SIMETRIC.split("cur.execute('UPDATE")[0]
    an = s.analizeaza_sursa("x.py", sursa)
    assert [(t, fel) for _r, _f, t, fel, _l in an] == [("tenants", "nume")]


def test_CALIBRARE_nume_ales_si_nume_anaf_NU_trec_drept_denumire():
    """Prima formă de eșec a instrumentului: potrivirea pe subșir ar fi luat `nume_ales=` drept
    denumirea firmei, iar `_consemneaza_alegerea` ar fi apărut ca scriere asimetrică — un roșu
    fals, pe o funcție corectă."""
    sursa = ('def g(conn):\n'
             '    with conn.cursor() as cur:\n'
             '        cur.execute("UPDATE public.tenants SET nume_ales=%s, nume_ales_la=now()", (a,))\n'
             '        cur.execute("UPDATE public.tenants SET nume_anaf=%s WHERE id=%s", (a, b))\n')
    assert [fel for _r, _f, _t, fel, _l in s.analizeaza_sursa("x.py", sursa)] == ["alt", "alt"]


def test_CALIBRARE_un_SET_compus_cu_fragment_nume_E_PRINS():
    """A doua formă, și e cea care a scăpat o dată deja (R77): `SET`-ul se asamblează la rulare,
    deci niciun literal dat lui `execute` nu conține cuvântul `nume`. Un detector care s-ar uita
    numai la argumentul apelului ar raporta **zero** și ar părea complet."""
    sursa = ('def h(conn, nume):\n'
             '    seturi = []\n'
             '    if nume:\n'
             '        seturi.append("nume = %s")\n'
             '    with conn.cursor() as cur:\n'
             '        cur.execute("UPDATE public.tenants SET " + ", ".join(seturi), val)\n')
    an = s.analizeaza_sursa("x.py", sursa)
    assert [(t, fel) for _r, _f, t, fel, _l in an] == [("tenants", "compus")]


def test_CALIBRARE_un_UPDATE_care_nu_ajunge_la_execute_nu_conteaza():
    """Direcția «raportează ce nu e»: gardul citește **argumentul unui apel**, nu text. Un exemplu
    de SQL scris într-un docstring sau într-o variabilă de documentație ar fi trecut la orice
    căutare pe fișier."""
    sursa = ('def d():\n'
             '    """Exemplu: UPDATE public.tenants SET nume = %s WHERE id = %s"""\n'
             '    ajutor = "UPDATE public.tenants SET nume = 1"\n'
             '    return ajutor\n')
    assert s.analizeaza_sursa("x.py", sursa) == []


def test_ANTI_VACUU_scanul_chiar_vede_codul():
    an = s.analizeaza()
    assert len(an) >= 10, "scanul vede doar %d instrucțiuni — s-a rupt calea" % len(an)
    assert len(s.fisiere_productie()) >= 20


# ─────────────────────────────────────────────────────────────────────────────
# [LOTUL 11, 04.09.2026] CE POATE FI O DENUMIRE, si ce se intampla cand nu e.
#
# Doua defecte gasite APASAND, pe ecranul «Date firma», cu formularul umplut cu semne:
#   1. `PUT /tenants/{id}` a acceptat `«»@#$%` si a scris-o in amandoua locurile. De acolo pleaca
#      pe `den` din D394 si pe antetul facturii.
#   2. TOATE refuzurile rutei ieseau **500 Internal Server Error**: portile puse pe 27.08 (cifra de
#      control a CUI-ului, unicitatea) ridica `ValueError`, iar ruta nu-l prindea. Mesajele scrise
#      cu grija n-au ajuns niciodata la un contabil.
# Al doilea il face pe primul invizibil: o poarta al carei refuz arata ca o cadere nu invata pe
# nimeni nimic despre date.
from core.tenant_provisioning import cere_denumire_scriibila  # noqa: E402
import pytest  # noqa: E402


@pytest.mark.parametrize("nume", [
    "Comert Micro TVA SRL", "Distributie Profit IC SRL", "Ana & Co S.R.L.",
    "Întreprindere Individuală Popescu", "A1 Serv", "  Firma Test  ",
])
def test_o_denumire_ADEVARATA_trece(nume):
    """Directia «refuza pe nedrept». Ampersand, puncte, cifre, diacritice — toate sunt denumiri
    reale de firma si niciuna nu are voie sa fie oprita."""
    assert cere_denumire_scriibila(nume) == nume.strip()


@pytest.mark.parametrize("nume", ["«»@#$%", "", "   ", None, "---", "123", "!!!", "  .  "])
def test_ce_NU_e_o_denumire_e_refuzat(nume):
    """Directia «lasa sa treaca». `123` e refuzat deliberat: un cod nu e o denumire, iar `den`
    din D394 nu e un camp numeric."""
    with pytest.raises(ValueError):
        cere_denumire_scriibila(nume)


def test_scriitorul_unic_TRECE_prin_verificare():
    """STRUCTURAL, nu pe text: `scrie_denumirea` chiar cheama functia, deci poarta nu se poate
    ocoli prin scriitorul unic. Daca apelul dispare, testul cade."""
    arb = ast.parse(io.open(os.path.join(_RAD, "core", "tenant_provisioning.py"),
                            encoding="utf-8").read())
    fn = [n for n in ast.walk(arb)
          if isinstance(n, ast.FunctionDef) and n.name == "scrie_denumirea"]
    assert len(fn) == 1, "scrie_denumirea nu mai e o singura functie"
    apeluri = [n.func.id for n in ast.walk(fn[0])
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert apeluri.count("cere_denumire_scriibila") == 1, (
        "scriitorul unic nu mai trece prin verificarea denumirii: %s" % apeluri)


def _prinde_valueerror(h):
    """`except ValueError` sau `except (ValueError, ...)`, citit din ARBORE."""
    ty = h.type
    tipuri = ty.elts if isinstance(ty, ast.Tuple) else ([ty] if ty is not None else [])
    return any(isinstance(x, ast.Name) and x.id == "ValueError" for x in tipuri)


def test_ruta_PUT_tenants_PRINDE_refuzul_si_nu_da_500():
    """STRUCTURAL: in corpul rutei `tenant_actualizeaza`, apelul catre `actualizeaza_tenant` std
    intr-un `try` al carui `except` prinde `ValueError`. Masurat inainte de reparatie:
    `PUT /tenants/4838 {"cui": "123"}` -> **500**. Mutatia care face gardul rosu: scoate `try`-ul."""
    arb = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    fn = [n for n in ast.walk(arb)
          if isinstance(n, ast.FunctionDef) and n.name == "tenant_actualizeaza"]
    assert len(fn) == 1, "ruta PUT /tenants/{id} nu mai e o singura functie"
    incercari = [n for n in ast.walk(fn[0]) if isinstance(n, ast.Try)]
    bune = 0
    for tr in incercari:
        cheama = any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                     and c.func.attr == "actualizeaza_tenant" for c in ast.walk(tr))
        # Pe NODUL de tip, nu pe textul lui `ast.dump`: un tipar pe text ar trece si peste un
        # `except SomeValueErrorish` si peste un comentariu (METODA_VERIFICARE §23).
        prinde = any(_prinde_valueerror(h) for h in tr.handlers)
        if cheama and prinde:
            bune += 1
    assert bune == 1, (
        "refuzurile lui `actualizeaza_tenant` nu mai sunt prinse in ruta — ies 500, iar mesajele "
        "scrise nu ajung la om (%d blocuri `try` potrivite)" % bune)
