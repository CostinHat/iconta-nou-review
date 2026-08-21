# -*- coding: utf-8 -*-
"""GARD (P3, 21.08.2026): o afirmație despre datele firmei își declară FELUL și poartă câmpurile
cerute de el. `core/afirmatii.py`.

R2′ (decis 20.08): payload-ul DECLARĂ felul; garda nu-l deduce din prezența câmpurilor. O deducție ar
face ca un câmp uitat să schimbe TĂCUT înțelesul afirmației.

CE PĂZEȘTE, dincolo de formă: `fapt` nu poate exista fără `temei_completitudine`, iar
`absenta_observatie` nu poate exista fără `surse_consultate`. Alea două nu sunt câmpuri decorative —
sunt exact diferența dintre „știu" și „n-am găsit", pe care am confundat-o de patru ori în două zile.
"""
import pytest

from core.afirmatii import FELURI, AfirmatieIncompleta, afirmatie, domeniu_text


def test_felul_e_declarat_nu_dedus():
    """Un `fel` din afara nomenclatorului nu trece tăcut — nomenclator ÎNCHIS, tiparul VC_RANDATE."""
    with pytest.raises(AfirmatieIncompleta) as e:
        afirmatie("cam_asa_ceva", "d300", "ceva")
    assert "nomenclatorul e închis" in str(e.value)


def test_faptul_nu_poate_exista_fara_temeiul_completitudinii():
    """Miezul. Un fapt negativ («nicio operațiune IC în lună») e o afirmație despre lume; ea se
    sprijină pe ce ne face să credem că am văzut tot. Fără asta, «fapt» e o absență bine îmbrăcată —
    exact eroarea din poarta D390, unde «lună închisă» însemna doar «luna calendaristică s-a terminat»."""
    with pytest.raises(AfirmatieIncompleta) as e:
        afirmatie("fapt", "d390", "nicio operațiune intracomunitară în lună", an=2026, luna=7)
    assert "temei_completitudine" in str(e.value)


def test_absenta_nu_poate_exista_fara_sursele_consultate():
    """A doua jumătate a aceleiași lecții: dacă spui «n-am găsit», trebuie să spui UNDE ai căutat."""
    with pytest.raises(AfirmatieIncompleta) as e:
        afirmatie("absenta_observatie", "d205", "niciun rulaj pe 457")
    assert "surse_consultate" in str(e.value)


def test_cheia_prezenta_cu_None_e_un_RASPUNS_nu_o_scapare():
    """Distincția care contează: cheia lipsă = afirmație incompletă; cheia prezentă cu None =
    necunoaștere DECLARATĂ. Intervalul deschis la dreapta e o afirmație validă despre lume."""
    a = afirmatie("necunoastere", "d300", "nu pot demonstra de când e înregistrată în scopuri de TVA",
                  domeniu_de="2025-01", domeniu_pana=None)
    assert a["domeniu_pana"] is None
    with pytest.raises(AfirmatieIncompleta):
        afirmatie("necunoastere", "d300", "motiv", domeniu_de="2025-01")   # cheia LIPSEȘTE


def test_campurile_care_nu_pot_fi_goale_chiar_nu_pot():
    with pytest.raises(AfirmatieIncompleta) as e:
        afirmatie("absenta_observatie", "d301", "n-am înregistrări", surse_consultate=None)
    assert "goale" in str(e.value)


def test_o_afirmatie_valida_ramane_un_dict_simplu():
    """Payload-ul rămâne JSON: obiectul e un contract, nu un tip de transport."""
    a = afirmatie("statut", "d301", "firma e plătitoare de TVA",
                  statut="platitor_tva", statut_din=None)
    assert isinstance(a, dict) and a["fel"] == "statut" and a["tip"] == "d301"


@pytest.mark.parametrize("fel", sorted(FELURI))
def test_fiecare_fel_din_nomenclator_e_construibil(fel):
    """Anti-vacuu: un fel declarat dar imposibil de construit e o intrare moartă în nomenclator."""
    valori = {"domeniu_de": "2025-01", "domeniu_pana": None, "an": 2026, "luna": 7,
              "temei_completitudine": "lună închisă, fără documente în așteptare",
              "surse_consultate": "registrul de note validate", "statut": "pfa", "statut_din": None,
              "sursele": "profilul firmei; facturile intracomunitare din iunie",
              "eroare": "TypeError: unsupported operand type(s)",
              "unde": "rândul 7", "regula": "cnp_invalid"}
    a = afirmatie(fel, "d999", "motiv de probă",
                  **{c: valori[c] for c in FELURI[fel] if c not in ("fel", "tip", "motiv")})
    assert a["fel"] == fel


def test_domeniul_se_scrie_dar_nu_se_inventeaza():
    """`statut` n-are domeniu prin natura lui — funcția întoarce None, nu o perioadă ticluită."""
    f = afirmatie("fapt", "d390", "nicio operațiune IC", an=2026, luna=7,
                  temei_completitudine="lună închisă")
    assert domeniu_text(f) == "07.2026"
    n = afirmatie("necunoastere", "d300", "m", domeniu_de="2025-01", domeniu_pana="2026-06")
    assert domeniu_text(n) == "2025-01 – 2026-06"
    s = afirmatie("statut", "d301", "m", statut="platitor", statut_din=None)
    assert domeniu_text(s) is None


def test_nomenclatorul_e_acelasi_cu_asteptarea_din_harta():
    """CONFRUNTAREA celor două instrumente, ca la scan↔verificator: harta casetelor poartă aceeași
    listă de feluri, ca ASTEPTARE. Dacă cele două se despart, una minte și nimeni nu află."""
    import os
    import sys
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(rad, "frontend_test", "vizual"))
    import harta_casete as h
    assert set(h.FELURI) == set(FELURI), (
        "nomenclatorul de feluri diferă între cod (core/afirmatii.py) și hartă: %s"
        % (set(h.FELURI) ^ set(FELURI)))
    for fel, spec in h.FELURI.items():
        assert tuple(spec["campuri_ceruti"]) == FELURI[fel], (
            "câmpurile cerute pentru `%s` diferă între hartă și cod" % fel)


# ---------------------------------------------------------------- al șaselea fel (21.08.2026)

def test_verificarea_rupta_e_un_fel_propriu():
    """`_c_rupt` din control_incrucisat exista ÎNAINTE de nomenclator și nu încăpea în niciunul din
    cele cinci feluri. Nu e necunoaștere — asta ar ascunde-o ca verdict permanent gri, exact ce
    refuză docstringul lui („lecția D300 mort"). Nu e contradicție — nimeni nu contrazice pe nimeni.
    E instrumentul care s-a rupt, iar asta se spune tare."""
    a = afirmatie("verificare_rupta", tip="d300", motiv="reconcilierea s-a oprit cu o eroare",
                  eroare="TypeError: unsupported operand")
    assert a["fel"] == "verificare_rupta"


def test_verificarea_rupta_cere_eroarea():
    """Fără eroarea concretă, „verificarea s-a rupt" e o vorbă: nimeni nu poate începe s-o repare."""
    with pytest.raises(AfirmatieIncompleta):
        afirmatie("verificare_rupta", tip="d300", motiv="s-a rupt ceva")


def test_neconformitatea_e_un_fel_propriu():
    """Cele 46 de validări de rând la import („rândul 7: CNP invalid") nu încap în cele cinci: nu e
    necunoaștere (știm foarte bine), nu e absență (valoarea E acolo, dar nu ține), nu e statut. E o
    valoare care nu satisface o regulă — iar regula trebuie NUMITĂ, altfel respingerea e arbitrară."""
    a = afirmatie("neconformitate", tip="salariat", motiv="CNP invalid (cifra de control)",
                  unde="rândul 7", regula="cnp_invalid")
    assert a["fel"] == "neconformitate"


def test_neconformitatea_cere_unde_si_regula():
    """`unde` = pe ce anume; `regula` = de ce nu ține. Fără ele, contabilul are un repros fără adresă."""
    with pytest.raises(AfirmatieIncompleta):
        afirmatie("neconformitate", tip="salariat", motiv="CNP invalid", unde="rândul 7")
    with pytest.raises(AfirmatieIncompleta):
        afirmatie("neconformitate", tip="salariat", motiv="CNP invalid", regula="cnp_invalid")
