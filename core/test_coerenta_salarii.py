# -*- coding: utf-8 -*-
"""GARD [R33, decizia lui Costin 25.08.2026]: semnalul de coerență notă-vs-D112 apare LA PROPUNERE,
arată AMBELE cifre, și NU blochează.

Decizia, în cuvintele lui: *„LOCUL: la propunere. E singurul moment în care omul poate face ceva cu
informația — la închiderea lunii e prea târziu, iar pe suprafața de control fiscal e o constatare
despre trecut. COMPORTAMENTUL: semnalează, cu cifra divergenței și cu ce diferă. Nu blochează.
Motivul: aplicația compară o propunere cu o declarație generată din alte date. Când cele două
diferă, nu se știe care greșește."*

Ce s-a găsit legând-o, și e mai mare decât spunea R33: modulul era nelegat **în întregime**.
`note_lunare` — contabilizarea statului de plată — n-avea niciun apelant, deci salariile nu deveneau
niciodată notă contabilă. R33 număra funcții publice fără importatori; ce nu spunea e că lipsea
chiar **actul**, nu doar verificarea lui.

Iar docstringul modulului promitea o garanție inexistentă: *„nota se scrie DOAR dacă totalul ei
coincide … refuzăm să scriem"*. Nimic nu scria și nimic nu refuza. A doua instanță a lui R16 în
același fișier — prima fiind comentariul din `salarizare.py:296`.
"""
import ast
import io
import pathlib

import pytest

RAD = pathlib.Path(__file__).resolve().parent.parent
_MAIN = ast.parse(io.open(RAD / "main.py", encoding="utf-8").read())

_CAMPURI = {"eticheta", "cont", "nota", "declaratie", "diferenta", "toleranta"}


def _ruta(nume):
    for n in ast.walk(_MAIN):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == nume:
            return n
    return None


# ── forma semnalului ─────────────────────────────────────────────────────────

def _cu_d112(monkeypatch, declarat, brut_nota):
    """Construieste cazul in loc sa-l astepte: D112 declara `declarat` pe impozit, nota propune
    `brut_nota`. Se inlocuiesc FUNCTIILE (`core.d112.genereaza` s.a.), nu intrarile din
    `sys.modules`: `from core import d112` citeste atributul de pe pachet, nu sys.modules - prima
    forma a probei masura functia reala pe o baza inexistenta si intorcea zero."""
    from decimal import Decimal

    from core import control_incrucisat as _ci
    from core import d112 as _d112
    from core import salarii_contare as _sc
    monkeypatch.setattr(_d112, "genereaza", lambda *a, **k: ('<angajatorB B_sal="3"/>', []))
    monkeypatch.setattr(_ci, "totaluri_d112_din_xml", lambda x: {"602": declarat})
    monkeypatch.setattr(_ci, "toleranta_d112", lambda n: 0)
    return _sc.control_coerenta([("641", "444", Decimal(str(brut_nota)))], None, "x", 2026, 6)


def test_o_divergenta_e_OBIECT_cu_ambele_cifre(monkeypatch):
    """*„Ce trebuie sa arate semnalul: ce spune nota, ce spune declaratia, si care e diferenta. Nu
    «exista o divergenta» - cifrele amandoua."*

    Forma veche intorcea proza. Cifrele nu se pot compune inapoi dintr-o fraza, iar o afirmatie
    despre datele firmei e un obiect cu atribute, nu un sir (decizia 21.08)."""
    div = _cu_d112(monkeypatch, 204.00, 161.12)
    assert div, "cazul construit TREBUIE sa divearga - altfel testul de dedesubt trece vid"
    d = div[0]
    assert set(d) == _CAMPURI, "campurile unei divergente s-au schimbat: %s" % sorted(d)
    assert d["nota"] == 161.12, "cifra NOTEI nu e cea propusa"
    assert d["declaratie"] == 204.00, "cifra DECLARATIEI nu e cea din XML"
    assert d["diferenta"] == round(d["declaratie"] - d["nota"], 2), (
        "diferenta nu e declaratie - nota; semnul ei spune in ce parte e lipsa")


def test_CALIBRARE_cand_cifrele_COINCID_nu_se_afirma_nimic(monkeypatch):
    """Cealalta directie (METODA §22): o functie care raporteaza mereu divergenta ar trece testul
    de sus si ar transforma semnalul in zgomot permanent."""
    assert _cu_d112(monkeypatch, 161.12, 161.12) == []


# ── locul: la propunere ──────────────────────────────────────────────────────

def test_propunerea_intoarce_SI_nota_SI_semnalul():
    """Cele două stau într-un singur răspuns fiindcă decizia le leagă: semnalul apare *la
    propunere*, adică în același moment în care omul vede ce s-ar scrie."""
    src = io.open(RAD / "core" / "salarii_contare.py", encoding="utf-8").read()
    fn = next((n for n in ast.parse(src).body
               if isinstance(n, ast.FunctionDef) and n.name == "propunere"), None)
    assert fn is not None, "salarii_contare.propunere a dispărut"
    chei = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Dict):
            chei.update(k.value for k in n.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str))
    assert {"note", "divergente"} <= chei, (
        "propunerea nu întoarce și nota, și divergențele: %s" % sorted(chei))


@pytest.mark.parametrize("nume", ["salarii_contare_propunere", "salarii_contare_scrie"])
def test_rutele_exista_si_sunt_POST(nume):
    n = _ruta(nume)
    assert n is not None, "ruta %s a dispărut" % nume
    metode = {d.func.attr for d in n.decorator_list
              if isinstance(d, ast.Call) and hasattr(d.func, "attr")}
    assert metode == {"post"}, (
        "%s nu mai e POST (%s). Propunerea calculează fără să scrie, dar rămâne POST: un GET n-are "
        "voie să scrie, iar `scrie` chiar scrie." % (nume, sorted(metode)))


def test_PROPUNEREA_nu_scrie_nimic():
    """Interdicția 6 în oglindă: ruta e POST tocmai ca să nu depindă de promisiunea că nu scrie —
    dar promisiunea se verifică oricum, fiindcă ecranul o cheamă la fiecare deschidere."""
    n = _ruta("salarii_contare_propunere")
    sql = " ".join(x.value.lower() for x in ast.walk(n)
                   if isinstance(x, ast.Constant) and isinstance(x.value, str))
    for verb in ("insert into", "update ", "delete from"):
        assert verb not in sql, "propunerea scrie (%s) — trebuia să doar calculeze" % verb
    assert not [1 for x in ast.walk(n)
                if isinstance(x, ast.Call) and getattr(x.func, "attr", "") == "commit"], (
        "propunerea face commit")


# ── comportamentul: semnalează, nu blochează ─────────────────────────────────

def test_semnalul_NU_blocheaza_scrierea():
    """Inima deciziei. Ruta care scrie nota nu are voie să refuze din cauza divergențelor:
    *„un blocaj ar presupune că declarația are dreptate."*

    Se citește STRUCTURA: niciun `raise` nu poate fi condiționat de `divergente`."""
    n = _ruta("salarii_contare_scrie")
    for x in ast.walk(n):
        if not isinstance(x, ast.If):
            continue
        # SETUL numelor din condiție, nu textul ei: `"divergente" in cond` ar trece și pe o
        # variabilă botezată `fara_divergente`, și n-ar spune nimic pe o condiție goală.
        nume = {y.id for y in ast.walk(x.test) if isinstance(y, ast.Name)}
        nume |= {y.value for y in ast.walk(x.test)
                 if isinstance(y, ast.Constant) and isinstance(y.value, str)}
        arunca = any(isinstance(y, ast.Raise) for y in ast.walk(x))
        assert not (arunca and {"divergente"} & nume), (
            "scrierea notei se blochează pe divergență (`if %s`) — decizia spune că semnalează"
            % ast.unparse(x.test))


def test_scrierea_e_CIORNA_nu_validata():
    """Patru-ochi rămâne: nota propusă mecanic intră ca ciornă, validarea o face un om."""
    n = _ruta("salarii_contare_scrie")
    # Statusul e parametru cu nume, deci se citește ca STRUCTURĂ: numele constantei folosite în
    # INSERT. Prima formă căuta `'ciorna'` în SQL — ar fi trecut și dacă șirul apărea într-un
    # comentariu, și n-ar fi văzut o schimbare a valorii constantei.
    nume = {y.id for x2 in ast.walk(n) if isinstance(x2, ast.Call)
            for y in ast.walk(x2) if isinstance(y, ast.Name)}
    assert {"STARE_CIORNA"} <= nume, (
        "nota statului de plată nu mai intră ca STARE_CIORNA — patru-ochi se pierde")
    import main as _m
    assert _m.STARE_CIORNA == "ciorna", "STARE_CIORNA nu mai e ciornă, ci %r" % _m.STARE_CIORNA


def test_divergenta_se_intoarce_SI_dupa_contare():
    """*„Divergența nesoluționată rămâne vizibilă, nu se stinge prin ignorare."*

    Ruta care scrie întoarce propunerea recalculată, inclusiv pe ramura «există deja» — deci
    semnalul reapare la fiecare deschidere, nu doar înainte de apăsare."""
    n = _ruta("salarii_contare_scrie")
    retururi = [x for x in ast.walk(n) if isinstance(x, ast.Return) and x.value is not None]
    assert len(retururi) >= 2, "ruta are o singură ieșire — ramura «deja contată» s-a pierdut"
    for r in retururi:
        assert "**p" in ast.unparse(r.value), (
            "o ieșire nu mai poartă propunerea recalculată: %s" % ast.unparse(r.value)[:80])


def test_luna_inchisa_opreste_SCRIEREA_dar_nu_propunerea():
    """[R42 (a)] Nota poartă data lunii declarate. Într-o lună închisă nu se scrie — dar propunerea
    se poate vedea oricând: a privi nu e a modifica."""
    scrie = _ruta("salarii_contare_scrie")
    prop = _ruta("salarii_contare_propunere")
    chemat = {getattr(x.func, "id", "") for x in ast.walk(scrie) if isinstance(x, ast.Call)}
    assert {"_cere_luna_deschisa"} <= chemat, "scrierea notei nu verifică dacă luna e închisă"
    chemat_prop = {getattr(x.func, "id", "") for x in ast.walk(prop) if isinstance(x, ast.Call)}
    assert not {"_cere_luna_deschisa"} & chemat_prop, (
        "propunerea refuză pe lună închisă — dar ea nu scrie nimic, deci n-are ce să încalce")
