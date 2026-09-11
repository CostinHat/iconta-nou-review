# -*- coding: utf-8 -*-
"""core/test_brevo_pe_fir_propriu.py — familia `_trimite_brevo` nu mai tine o conexiune din pool.

**Ce s-a reparat, si de ce in DOUA feluri.** Apelul la Brevo are termen de 10 s, si se facea din
interiorul unui `with db.get_conn()`. Zece secunde dintr-un pool de zece conexiuni, pentru un
e-mail care n-are nicio legatura cu tranzactia. Dar cele doua feluri de e-mail nu se repara la fel,
iar deosebirea era deja scrisa in verdictul P4 al lui `_trimite_brevo`: *«e un efect, dar unul care
VORBESTE DESPRE un esec, nu unul care consemneaza un act»*.

  (a) ALERTA despre un esec secundar pleaca pe un FIR PROPRIU. NU se amana dupa commit — verdictul
      P4 spune explicit ca ar fi gresit: o alerta amanata s-ar pierde exact cand actul cade.
  (b) E-MAILUL cererii GDPR consemneaza un act, deci i se aplica litera doctrinei P4: efectul
      ireversibil vine ULTIMUL, dupa ce tranzactia a reusit sigur.

**Fiecare proba are perechea ei.** O proba care arata ca ceva «nu mai blocheaza» trece si daca
nimic nu se mai intampla deloc. Deci se probeaza si ca mesajul CHIAR pleaca, si ca varianta
sincrona CHIAR asteapta — altfel n-am masurat o reparatie, am masurat o functie goala.
"""
from __future__ import annotations

import ast
import io
import os
import threading
import time

import pytest

from core import gdpr_cerere as gc
from core import observare

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ============================================================
#  unelte
# ============================================================
class _Cursor:
    def __init__(self, raspunsuri):
        self._r = list(raspunsuri)
        self.executate = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, p=None):
        self.executate.append((" ".join(sql.split()), p))

    def fetchone(self):
        return self._r.pop(0)


class _Conn:
    """Conexiune de proba. NU atinge nicio baza — familia asta se probeaza pe contract, nu pe date."""

    def __init__(self, raspunsuri):
        self._c = _Cursor(raspunsuri)
        self.comis = 0

    def cursor(self):
        return self._c

    def commit(self):
        self.comis += 1


class _Spion:
    """Inlocuitor pentru `_trimite_brevo`: retine apelurile, poate intarzia, poate ridica."""

    def __init__(self, intarziere=0.0, ridica=None, raspuns=True):
        self.apeluri = []
        self.intarziere = intarziere
        self.ridica = ridica
        self.raspuns = raspuns
        self._lacat = threading.Lock()

    def __call__(self, subiect, mesaj):
        if self.intarziere:
            time.sleep(self.intarziere)
        with self._lacat:
            self.apeluri.append((subiect, mesaj))
        if self.ridica:
            raise self.ridica
        return self.raspuns


def _fire_de_alerta():
    return [t for t in threading.enumerate() if t.name == "alerta-brevo"]


def _asteapta_firele(termen=5.0):
    t0 = time.monotonic()
    for t in _fire_de_alerta():
        t.join(max(0.0, termen - (time.monotonic() - t0)))


# ============================================================
#  (a) ALERTA — pe fir propriu
# ============================================================
def test_alerta_in_fundal_nu_asteapta_apelul_la_brevo(monkeypatch):
    """Miezul reparatiei: apelantul se intoarce INAINTE ca Brevo sa raspunda."""
    spion = _Spion(intarziere=0.40)
    monkeypatch.setattr(observare, "_trimite_brevo", spion)
    t0 = time.monotonic()
    pornit = observare.alerteaza_in_fundal("p_fundal_1", "s", "m")
    scurs = time.monotonic() - t0
    assert pornit is True
    assert scurs < 0.20, ("apelantul a asteptat %.2f s — trimiterea n-a plecat pe alt fir" % scurs)
    _asteapta_firele()
    assert spion.apeluri == [("s", "m")], "mesajul n-a ajuns niciodata la Brevo"


def test_perechea_sincrona_CHIAR_asteapta(monkeypatch):
    """ANTI-VACUUM pentru proba de mai sus. Fara ea, `alerteaza_in_fundal` ar putea fi rapida
    fiindca intarzierea de proba nu exista, nu fiindca a plecat pe alt fir."""
    spion = _Spion(intarziere=0.40)
    monkeypatch.setattr(observare, "_trimite_brevo", spion)
    t0 = time.monotonic()
    observare.alerteaza("p_sinc_1", "s", "m")
    scurs = time.monotonic() - t0
    assert scurs >= 0.35, ("varianta sincrona s-a intors in %.2f s — intarzierea de proba nu "
                           "exista, deci proba cealalta n-a masurat nimic" % scurs)


def test_alerta_in_fundal_respecta_throttlingul(monkeypatch):
    """Al doilea apel pe aceeasi cheie nu pleaca — si NU porneste niciun fir degeaba."""
    spion = _Spion()
    monkeypatch.setattr(observare, "_trimite_brevo", spion)
    assert observare.alerteaza_in_fundal("p_throttle", "s", "m") is True
    _asteapta_firele()
    inainte = len(spion.apeluri)
    assert observare.alerteaza_in_fundal("p_throttle", "s", "m") is False
    _asteapta_firele()
    assert len(spion.apeluri) == inainte, "throttlingul n-a oprit al doilea mesaj"


def test_firul_NU_e_daemon(monkeypatch):
    """O alerta ridicata cu o clipa inainte de restart trebuie sa plece. Un fir `daemon` ar fi
    taiat de interpretor la oprire — adica exact tacerea pe care functia asta o inlatura."""
    vazute = []
    real = threading.Thread

    class _Fir(real):
        def __init__(self, *a, **k):
            vazute.append(k.get("daemon"))
            real.__init__(self, *a, **k)

    monkeypatch.setattr(observare, "_trimite_brevo", _Spion())
    monkeypatch.setattr(threading, "Thread", _Fir)
    observare.alerteaza_in_fundal("p_daemon", "s", "m")
    _asteapta_firele()
    assert vazute == [False], "firul de alerta a fost pornit ca daemon: %r" % vazute


def test_alerteaza_ramane_sincrona_si_intoarce_daca_a_plecat(monkeypatch):
    """`expirare_cote` numara pe raspunsul ei. Daca ar deveni asincrona, «cate au plecat» ar
    deveni tacut «cate au fost pornite» — alt lucru numarat, aceeasi cifra afisata."""
    monkeypatch.setattr(observare, "_trimite_brevo", _Spion(raspuns=True))
    assert observare.alerteaza("p_sinc_2", "s", "m") is True
    monkeypatch.setattr(observare, "_trimite_brevo", _Spion(raspuns=False))
    assert observare.alerteaza("p_sinc_3", "s", "m") is False


def test_esec_secundar_cheama_varianta_de_fundal():
    """STRUCTURAL, pe AST: `esec_secundar` trebuie sa cheme varianta de fundal, nu pe cea sincrona."""
    arbore = ast.parse(io.open(os.path.join(RADACINA, "core", "observare.py"),
                               encoding="utf-8").read())
    fn = next(n for n in ast.walk(arbore)
              if isinstance(n, ast.FunctionDef) and n.name == "esec_secundar")
    # EGALITATE pe lista, nu `in` pe container: un `in` se ancoreaza pe un nume care apare
    # oricum, iar lista spune in plus ca exista EXACT un apel de alerta, si care anume.
    de_alerta = [x.func.id for x in ast.walk(fn) if isinstance(x, ast.Call)
                 and isinstance(x.func, ast.Name) and x.func.id.startswith("alerteaza")]
    assert de_alerta == ["alerteaza_in_fundal"], (
        "esec_secundar cheama %r — varianta sincrona tine o conexiune peste apelul la Brevo"
        % de_alerta)
    # ANTI-VACUUM: numele sincron EXISTA in modul, deci absenta lui de mai sus e o alegere
    assert any(isinstance(n, ast.FunctionDef) and n.name == "alerteaza"
               for n in ast.walk(arbore)), "numele `alerteaza` nu exista — proba de mai sus e vida"


# ============================================================
#  (b) GDPR — efectul ireversibil, ultimul
# ============================================================
def _cerere(monkeypatch, spion=None):
    monkeypatch.setattr(observare, "_trimite_brevo", spion or _Spion())
    conn = _Conn([("Cabinet Alfa",), (7, "2026-09-11 10:00:00+03")])
    r = gc.depune_cerere(conn, 42, 9, "Cabinet Alfa", motiv="nu mai folosesc")
    return conn, r


def test_depunerea_nu_mai_trimite_niciun_email(monkeypatch):
    """Calea reusita: cererea se inregistreaza, dar NIMIC nu pleaca inca."""
    spion = _Spion()
    conn, r = _cerere(monkeypatch, spion)
    assert r["ok"] is True and r["cerere_id"] == 7
    assert spion.apeluri == [], "e-mailul pleaca inca din interiorul tranzactiei"
    assert conn.comis == 0, "depunerea comite singura — ruta trebuie sa decida asta"


def test_anuntul_e_TUPLU_nu_dictionar(monkeypatch):
    """Un dict cu chei ca `motiv` e citit de gardul afirmatiilor tipate drept afirmatie despre
    datele firmei. Nu e — e continutul unui e-mail."""
    _conn, r = _cerere(monkeypatch)
    anunt = r["anunt"]
    assert isinstance(anunt, tuple) and len(anunt) == 2, type(anunt)
    subiect, corp = anunt
    assert isinstance(subiect, str) and isinstance(corp, str)
    # pe EGALITATE, nu cautand subsiruri: continutul are acum un nume (`corp_anunt`), deci se
    # compara intreg. Un `in` pe text ar fi trecut si daca jumatate din anunt ar fi disparut.
    assert subiect == gc.SUBIECT_ANUNT
    assert corp == gc.corp_anunt(42, "Cabinet Alfa", 7, 9, "2026-09-11 10:00:00+03",
                                 "nu mai folosesc")


def test_anunta_echipa_trimite_si_intoarce_rezultatul(monkeypatch):
    spion = _Spion(raspuns=True)
    _conn, r = _cerere(monkeypatch, spion)
    assert gc.anunta_echipa(r["anunt"]) is True
    assert len(spion.apeluri) == 1
    assert spion.apeluri[0][0] == r["anunt"][0]


def test_anunta_echipa_fara_anunt_nu_trimite(monkeypatch):
    """Configuratie lipsa: `None` nu e un e-mail gol, e nimic de trimis."""
    spion = _Spion()
    monkeypatch.setattr(observare, "_trimite_brevo", spion)
    assert gc.anunta_echipa(None) is False
    assert spion.apeluri == []


def test_esecul_emailului_nu_ridica_dar_NU_dispare(monkeypatch):
    """Calea de eroare. Cererea e deja comisa, deci esecul nu mai poate intoarce nimic — dar se
    consemneaza. `except Exception: pass` de dinainte il facea invizibil."""
    consemnate = []
    monkeypatch.setattr(observare, "_trimite_brevo",
                        _Spion(ridica=RuntimeError("Brevo 500")))
    monkeypatch.setattr(observare, "esec_secundar",
                        lambda eticheta, eroare, alerta=False: consemnate.append(
                            (eticheta, type(eroare).__name__, alerta)))
    assert gc.anunta_echipa(("s", "m")) is False
    assert consemnate and consemnate[0][1] == "RuntimeError", consemnate
    assert consemnate[0][2] is True, "esecul s-a consemnat fara alerta"


def test_ruta_cheama_anuntul_DUPA_commit_si_IN_AFARA_blocului():
    """STRUCTURAL, pe AST, fiindcă asta e chiar ce cere doctrina P4 — efectul ireversibil vine ultimul.

    Nu se cauta un sir in `main.py`: se compara POZITIILE din arbore. Un `anunta_echipa` mutat
    inapoi in bloc ar trece orice proba pe text."""
    arbore = ast.parse(io.open(os.path.join(RADACINA, "main.py"), encoding="utf-8").read())
    fn = next(n for n in ast.walk(arbore)
              if isinstance(n, ast.FunctionDef) and n.name == "gdpr_cerere_stergere")
    blocuri = [n for n in ast.walk(fn) if isinstance(n, ast.With)]
    assert blocuri, "ruta n-are niciun `with` — s-a schimbat forma, reciteste proba"
    bloc = blocuri[0]
    apel = next((n for n in ast.walk(fn) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == "anunta_echipa"), None)
    assert apel is not None, "ruta nu mai anunta echipa deloc"
    assert apel.lineno > bloc.end_lineno, (
        "anuntul se trimite INAUNTRUL blocului de conexiune (linia %d, blocul se inchide la %d) — "
        "adica tine o conexiune din pool peste apelul la Brevo"
        % (apel.lineno, bloc.end_lineno))
    comit = [n for n in ast.walk(bloc) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "commit"]
    assert comit, "nu se mai comite nimic inainte de anunt"
    assert apel.lineno > comit[0].lineno


@pytest.mark.parametrize("nume", ["depune_cerere", "anunta_echipa"])
def test_docstringul_spune_ce_face_functia(nume):
    """doc <-> cod: `depune_cerere` si-a schimbat contractul (intoarce si `anunt`), deci si proza."""
    fn = getattr(gc, nume)
    assert fn.__doc__ and len(fn.__doc__.strip()) > 40, nume
