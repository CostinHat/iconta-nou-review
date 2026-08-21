# -*- coding: utf-8 -*-
"""GARD (21.08.2026): FAPTUL BATE VECTORUL în selectorul de declarații, iar „lună închisă" nu mai
înseamnă singură completitudine.

DE CE. Tiparul tenant_006: vectorul spunea că firma nu are operațiuni intracomunitare, firma avea
achiziții IC reale. Un selector care blochează pe bifă îl împiedică pe contabil să declare o obligație
pe care firma o ARE. Vectorul e o AFIRMAȚIE, faptul e o OBSERVAȚIE — când se contrazic, faptul câștigă
și vectorul devine ce trebuie corectat (decis de Costin).

ȘI CONTRA-DIRECȚIA, care contează la fel de mult: când faptul LIPSEȘTE și vectorul spune „nu", blocajul
RĂMÂNE — nu devine „nu pot verifica" ca la cele trei D301. Diferența e reală: acolo tăcea un TABEL
(absența unei observații), aici a răspuns un OM. Măsurat 21.08: câmpul e tri-stare cu placeholder gol,
salvarea e refuzată cu mesaj propriu dacă rămâne necompletat, 17/17 firme îl au completat, iar
necompletat produce gri în semafor — nu blocaj.
"""
import datetime

import pytest

from core import control_fiscal_api as cf
from core import d390


def _vec(ic):
    return {"tip_firma": "srl", "platitor_tva": False, "operatiuni_ic": ic}


# ─────────── selectorul: faptul bate vectorul ───────────

def test_faptul_prezent_deblocheaza_desi_vectorul_spune_nu():
    """Cazul 006. Firma declară «fără IC», dar există achiziții intracomunitare reale — selectorul
    NU mai are voie să blocheze D390/D301, altfel contabilul nu poate declara ce datorează."""
    neap = cf.neaplicabile_selector(_vec(False), ic_fapt=lambda: True)
    assert "d390" not in neap and "d301" not in neap, neap


def test_evidenta_incompleta_deblocheaza_la_fel():
    """Dacă există documente neînregistrate, absența operațiunilor NU se poate afirma — deci nu se
    blochează. `None` e «nu pot ști», nu «nu»."""
    neap = cf.neaplicabile_selector(_vec(False), ic_fapt=lambda: None)
    assert "d390" not in neap and "d301" not in neap, neap


def test_faptul_absent_pastreaza_blocajul_pe_DECLARATIE():
    """Contra-direcția. Blocajul rămâne — dar motivul își numește SURSA (cine a declarat) și poartă
    remediul. Nu afirmă despre lume dintr-o bifă."""
    neap = cf.neaplicabile_selector(_vec(False), ic_fapt=lambda: False)
    assert "d390" in neap and "d301" in neap
    for t in ("d390", "d301"):
        assert "Vectorul fiscal declară" in neap[t], neap[t]
        assert "corectează Vectorul fiscal" in neap[t], neap[t]


def test_fara_sonda_comportamentul_ramane_cel_vechi():
    """Compatibilitate: apelanții care nu dau `ic_fapt` (teste, matricea de 64) văd exact ce vedeau."""
    assert cf.neaplicabile_selector(_vec(False)) == cf.neaplicabile_selector(_vec(False), ic_fapt=lambda: False)


def test_vectorul_da_nu_blocheaza_niciodata():
    """Anti-fals-pozitiv: bifa «da» n-a blocat nici înainte; sonda nu se cheamă degeaba."""
    chemat = []
    neap = cf.neaplicabile_selector(_vec(True), ic_fapt=lambda: chemat.append(1) or True)
    assert "d390" not in neap and not chemat, "sonda de fapt s-a chemat inutil"


# ─────────── poarta D390: întărită, nu convertită ───────────

class _Cur:
    """Cursor fals: raspunde pe rand din lista data. Fara DB — testăm decizia, nu Postgres."""

    def __init__(self, raspunsuri):
        self._r = list(raspunsuri)
        self.ultima = None

    def execute(self, q, a=None):
        self.ultima = (q, a)

    def fetchone(self):
        return self._r.pop(0)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Conn:
    def __init__(self, raspunsuri):
        self._c = _Cur(raspunsuri)

    def cursor(self):
        return self._c


def test_documente_in_asteptare_impiedica_afirmarea_absentei():
    """Trei e-Facturi descărcate și neînregistrate pe iulie → nu pot spune «nu s-a datorat pe iulie»."""
    m = d390.evidenta_incompleta(_Conn([("t",), (3,)]), "tenant_x", 2026, 7)
    assert m and "3 e-Facturi" in m and "07.2026" in m, m
    assert "nu pot confirma" in m


def test_fara_documente_in_asteptare_poarta_ramane_deschisa():
    """Contra-direcția, și cea care apără decizia lui Costin: fără semnal concret, luna închisă rămâne
    un FAPT. Altfel gri-ul ar acoperi și «nu știm nimic» și «știm, dar poarta e slabă»."""
    assert d390.evidenta_incompleta(_Conn([("t",), (0,)]), "tenant_x", 2026, 7) is None


def test_fara_conexiune_sau_tabel_nu_inventeaza_incertitudine():
    assert d390.evidenta_incompleta(None, None, 2026, 7) is None
    assert d390.evidenta_incompleta(_Conn([(None,)]), "tenant_x", 2026, 7) is None


def test_semaforul_pune_gri_nu_neaplicabil_cand_evidenta_e_incompleta():
    """Capătul celălalt: motivul ajunge în `neclar`, nu în `neaplicabile`. Fără asta, funcția ar fi
    corectă și complet nefolosită."""
    azi = datetime.date(2026, 8, 20)
    vector = {"tip_firma": "srl", "platitor_tva": True, "tip_decont": "lunar", "regim_fiscal": "micro",
              "operatiuni_ic": True, "inreg_art317": False}
    r = cf.obligatii_datorate(vector, False, azi,
                              d390_fapt=lambda a, l: False,
                              d390_incomplet=lambda a, l: "două documente în așteptare pe %02d" % l)
    tipuri_neclar = [n for n in r["neclar"] if n["tip"] == "d390"]
    assert tipuri_neclar, "D390 n-a ajuns în «nu pot verifica»: %s" % r["neclar"]
    assert "așteptare" in (tipuri_neclar[0].get("cauza") or tipuri_neclar[0].get("motiv") or "")
    assert not [n for n in r["neaplicabile"] if n["tip"] == "d390"], \
        "a rămas și în «nu se datorează» — cele două nu pot fi amândouă"


def test_fara_callback_semaforul_afirma_ca_inainte():
    """Anti-regresie: fără sondă, comportamentul vechi (neaplicabil pe ultima lună închisă) rămâne."""
    azi = datetime.date(2026, 8, 20)
    vector = {"tip_firma": "srl", "platitor_tva": True, "tip_decont": "lunar", "regim_fiscal": "micro",
              "operatiuni_ic": True, "inreg_art317": False}
    r = cf.obligatii_datorate(vector, False, azi, d390_fapt=lambda a, l: False)
    assert [n for n in r["neaplicabile"] if n["tip"] == "d390"], \
        "comportamentul vechi s-a schimbat pentru apelanții fără sondă"


# ─────────── anti-vacuu ───────────

def test_toate_cele_trei_raspunsuri_ale_sondei_sunt_exercitate():
    """Un gard care exercită o singură ramură lasă celelalte două să moară tăcut."""
    rezultate = {r: ("d390" in cf.neaplicabile_selector(_vec(False), ic_fapt=lambda: r))
                 for r in (True, False, None)}
    assert rezultate == {True: False, False: True, None: False}, rezultate


def test_sonda_de_db_exista_si_e_citita_de_ruta():
    """Funcția pură poate fi corectă și nefolosită. Ruta selectorului trebuie s-o cheme."""
    import inspect
    import os
    assert callable(cf.ic_fapt_din_db)
    rad = os.path.dirname(os.path.dirname(os.path.abspath(cf.__file__)))
    src = open(os.path.join(rad, "main.py"), encoding="utf-8").read()
    assert "ic_fapt=(lambda: control_fiscal_api.ic_fapt_din_db(" in src, \
        "ruta /declaratii/tipuri nu mai cheamă sonda de fapt — selectorul ar bloca iar pe bifă"
    assert "SELECT" in inspect.getsource(cf.ic_fapt_din_db).upper()
