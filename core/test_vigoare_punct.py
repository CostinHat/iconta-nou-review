# -*- coding: utf-8 -*-
"""Garda instrumentului de vigoare PE PUNCT (`scripts/vigoare_punct.py`, R2).

Un instrument de măsură se gardează pe CAZUL CUNOSCUT și pe REFUZ, nu pe totaluri: totalul se poate
potrivi din întâmplare, cazul cunoscut nu.

Cele două greșeli pe care le-a făcut instrumentul înainte de a fi bun — amândouă gardate aici:
1. expresia marcajului se oprea la primul „)", care e în „Litera a)", deci rata „Punctul 9." și
   raporta NEMODIFICAT un punct despre care știam că fusese modificat;
2. cunoștea un singur tipar de numerotare, deci pe Normele OMFP 2634 nu vedea NICIUN punct — și
   răspundea totuși la întrebări despre puncte, cu încredere.
"""
import importlib.util
import pathlib

import pytest

_CALE = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "vigoare_punct.py"
_SPEC = importlib.util.spec_from_file_location("vigoare_punct", _CALE)
vp = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(vp)

_RAD = pathlib.Path(__file__).resolve().parents[1] / "anaf_surse"
_REGL = _RAD / "omfp_1802_2014_reglementari_consolidat.txt"
_NORME = _RAD / "omfp_2634_2015_anexa1_norme_generale.txt"


def _text(p):
    if not p.exists():
        pytest.skip("actul nu e în corpus: %s" % p.name)
    return p.read_bytes().decode("utf-8", errors="replace")


def test_cazul_cunoscut_pct9_criteriile_de_marime():
    """CALIBRARE. pct. 9 din Reglementări a fost modificat de ORDIN 4.164/2024, în vigoare 23-08-2024.

    E chiar punctul pe care registrul l-a avut greșit o dimineață (criteriile scrise în EUR, din forma
    inițială 2014). Dacă instrumentul nu-l găsește, nu are voie să fie crezut pe niciun alt punct."""
    d = vp.pe_punct(_text(_REGL))
    assert "9" in d, "instrumentul nu vede modificarea pct. 9 — cazul cunoscut e ratat"
    ultim = d["9"][0]
    assert ultim["data"] == "2024-08-23", "data intrării în vigoare: %s" % ultim["data"]
    assert "4.164" in ultim["act"], "actul modificator: %s" % ultim["act"]


def test_adresa_se_citeste_din_marcaj_nu_din_pozitie():
    """Marcajul își spune singur adresa; parantezele din adresă („Litera a)") nu au voie s-o taie."""
    brut = "(la 23-08-2024, \n Litera a) , Alineatul (2) , Punctul 9. , Sectiunea 1.3 , Capitolul 1 " \
           "a fost modificată de Punctul 2. , Articolul I din ORDINUL nr. 4.164 din 12 august 2024 )"
    m = vp.marcaje(brut)
    assert m and m[0]["punct"] == "9", "adresa s-a pierdut la prima paranteză închisă: %r" % m


def test_punctul_din_actul_modificator_nu_se_confunda_cu_al_actului_de_baza():
    """Marcajul numește DOUĂ puncte: al actului de bază (înainte de «a fost») și al celui modificator
    (după). Confundarea lor ar atribui modificarea altui punct — greșeală tăcută, cifră plauzibilă."""
    brut = "(la 23-08-2024, \n Punctul 9. , Sectiunea 1.3 a fost modificată de Punctul 2. , " \
           "Articolul I din ORDINUL nr. 4.164 din 12 august 2024 )"
    assert vp.marcaje(brut)[0]["punct"] == "9", "s-a luat punctul din actul MODIFICATOR"


def test_tiparele_de_numerotare_acopera_ambele_acte():
    """ANTI-VACUU. Cele două acte numerotează diferit („9. - (1)" vs „45. Registrul-jurnal").
    Un act în care nu se vede niciun punct face orice răspuns despre puncte vid."""
    for cale, minim in ((_REGL, 100), (_NORME, 20)):
        iv = vp.intervale(_text(cale))
        assert len(iv) >= minim, ("în %s s-au găsit doar %d puncte — sub pragul de vacuu %d"
                                  % (cale.name, len(iv), minim))


def test_punctele_pe_care_sta_verdictul_sunt_gasite_ca_puncte():
    """Cele 8 puncte pe care stă verdictul 1d trebuie să EXISTE ca puncte în actele lor.
    «Negăsit» și «neatins de marcaje» sunt răspunsuri diferite; garda ține distincția vie."""
    for cale, puncte in ((_REGL, ["9", "20", "21"]), (_NORME, ["44", "45", "46", "47", "48"])):
        iv = vp.intervale(_text(cale))
        lipsa = [p for p in puncte if p not in iv]
        assert not lipsa, "%s: puncte negăsite ca puncte: %s" % (cale.name, lipsa)


def test_refuzul_pe_act_fara_puncte():
    """Un act în care nu se vede niciun punct nu primește răspuns, ci refuz."""
    assert vp.intervale("text fara nicio numerotare pe puncte") == {}
