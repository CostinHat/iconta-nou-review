# -*- coding: utf-8 -*-
"""GARDĂ: o interpretare e un OBIECT declarabil, cu variantele obligatorii. (P11, 22.08.2026)

DE CE (ARHITECTURA_NORMATIV, P11 + anexa): între lege și cifră există un pas de interpretare, iar
acel pas nu are voie să fie îngropat într-o condiție din cod. O alegere care poartă marcajul unui
fapt legal devine imposibil de contestat — nimeni nu discută un articol de lege.

CE FACE OBIECTUL. Ce cere Partea III pentru o INTERPRETARE: textul care a lăsat loc (citat), de ce
lasă loc, variantele posibile, ce s-a ales, motivul, cine și când, ce spune arbitrul, și — dacă
arbitrul contrazice — dezacordul marcat ca DESCHIS.

REGULA CARE O DEOSEBEȘTE DE O VALOARE: **o interpretare fără variantele enumerate nu e o
interpretare, e o valoare deghizată.** Dacă nu poți numi cealaltă variantă, legea nu lăsa loc.
Minimul e DOUĂ: cea aleasă și cel puțin o alta.
"""
import pytest

from core.interpretare import (INCERTITUDINI, Interpretare, InterpretareIncompleta,
                               interpretari_deschise)

BAZA = dict(
    cheie="incadrat_la_minim",
    text_citat="persoanele fizice care realizează venituri din salarii ... încadrate cu salariul "
               "de bază minim brut pe țară garantat în plată",
    de_ce_lasa_loc="«încadrat cu» nu spune dacă e egalitate strictă sau prag maxim; un brut cu un "
                   "leu peste minim e sau nu «încadrat cu minimul»?",
    variante=[("egalitate_stricta", "brutul e EXACT salariul minim"),
              ("prag_maxim", "brutul e cel mult salariul minim")],
    ales="egalitate_stricta",
    motiv="formularea «încadrat cu» descrie nivelul de încadrare din contract, nu o limită; iar "
          "alin.(4) prorateaza facilitatea pe fereastra activă, ceea ce presupune un nivel fix",
    forma="termen_nedefinit",
    de_cine="costin",
    la_data="2026-08-22",
)


def test_interpretarea_se_construieste_si_poarta_tot():
    i = Interpretare(**BAZA)
    assert i.cheie == "incadrat_la_minim" and i.ales == "egalitate_stricta"
    assert i.text_citat and i.de_ce_lasa_loc and i.motiv


def test_fara_variante_nu_e_interpretare():
    """Miezul: «o interpretare fără variantele enumerate e o valoare deghizată»."""
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, variante=[]))


def test_o_singura_varianta_nu_e_o_alegere():
    """Dacă nu poți numi CEALALTĂ variantă, legea nu lăsa loc — deci n-ai interpretat, ai citit."""
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, variante=[("egalitate_stricta", "brutul e EXACT minimul")]))


def test_alesul_trebuie_sa_fie_dintre_variante():
    """O alegere din afara listei înseamnă că lista nu descrie spațiul real al alegerii."""
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, ales="a_treia_cale"))


def test_textul_care_a_lasat_loc_e_obligatoriu():
    """Fără textul citat, nu se poate verifica DACĂ legea lăsa loc — iar atunci «interpretare» devine
    un permis de a scrie orice."""
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, text_citat=""))
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, de_ce_lasa_loc=""))


def test_autorul_si_data_sunt_obligatorii():
    """O alegere anonimă nu e o decizie — aceeași regulă ca la asumarea unei contradicții."""
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, de_cine=""))
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, la_data=""))


# ---------------------------------------------------------------- arbitrul

def test_dezacordul_cu_arbitrul_ramane_DESCHIS():
    """P11: «când arbitrul o contrazice, dezacordul rămâne vizibil până la lămurire, nu se stinge
    prin alinierea tăcută a codului»."""
    i = Interpretare(**dict(BAZA, arbitru="DUK regula SP1B4_1", arbitru_confirma=False,
                            arbitru_spune="validatorul calculează 3750"))
    assert i.dezacord_deschis is True
    assert i in interpretari_deschise([i])


def test_arbitrul_care_confirma_nu_lasa_dezacord():
    i = Interpretare(**dict(BAZA, arbitru="DUK regula SP1B4_1", arbitru_confirma=True))
    assert i.dezacord_deschis is False


def test_dezacordul_nu_se_poate_stinge_fara_lamurire():
    """Nu există câmp «rezolvat=True». Un dezacord se stinge doar prin schimbarea alegerii sau prin
    confirmarea arbitrului — nu prin apăsare. Aceeași formă ca la contradicția din statul de plată."""
    i = Interpretare(**dict(BAZA, arbitru="DUK regula SP1B4_1", arbitru_confirma=False,
                            arbitru_spune="validatorul calculeaza 3750"))
    with pytest.raises(AttributeError):
        i.rezolvat = True


def test_arbitrul_care_contrazice_cere_sa_se_spuna_CE_zice():
    """«dezacordul se documentează ca atare, nu se ascunde» (P8). Un `False` fără text nu documentează."""
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, arbitru="DUK regula SP1B4_1", arbitru_confirma=False))


# ---------------------------------------------------------------- nomenclatorul de incertitudini

def test_de_ce_lasa_loc_e_dintr_un_set_INCHIS():
    """Altfel «lasă loc» devine o formulă magică. Formele sunt puține și se pot enumera: termen
    nedefinit, tăcere a textului, două texte care nu se acordă, delegare la o normă care nu există."""
    assert len(INCERTITUDINI) >= 3
    for cod, spec in INCERTITUDINI.items():
        assert spec.get("inseamna"), "forma de incertitudine %r nu spune ce e" % cod
    with pytest.raises(InterpretareIncompleta):
        Interpretare(**dict(BAZA, forma="motiv_inventat_pe_loc"))
