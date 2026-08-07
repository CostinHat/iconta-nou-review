# -*- coding: utf-8 -*-
"""GARD CM-episod: indemnizatia CM se calculeaza pe EPISOD, nu pe certificat izolat (OUG 158/2005
art.17(1) "raportat la fiecare episod"). Doua defecte reparate + gardate:
  1. procentul (55/65/75) pe zile_episod (suma episodului), NU pe zilele certificatului curent;
  2. diminuarea de 1 zi + portia angajator (zilele 2-6) O SINGURA DATA pe episod (pe certificatul initial).
Al treilea (art.XI L141/2025 - forma dupa data certificatului INITIAL) e PLUMBAT (data_episod_initial),
inert pana intra forma pre-141 in _VARIANTE_PROCENT_CM (blocat pe sursa, xfail #16)."""
import io
import re
from datetime import date
from decimal import Decimal

from core.salarizare import calcul_cm, procent_cm

LA = date(2026, 7, 1)
B = dict(cod="01", la_data=LA)


def _read(p):
    return io.open(p, encoding="utf-8").read()


def test_procent_pe_zile_episod_nu_pe_certificat():
    """Un certificat de 7 zile dintr-un episod de 20 -> 75%, NU 55%. Daca procentul iese pe zilele
    certificatului curent (7 -> 55%) in loc de zile_episod (20 -> 75%), testul PICA."""
    # certificat izolat de 7 zile = 55%
    assert procent_cm("01", 7, la_data=LA) == Decimal("0.55")
    # acelasi certificat ca parte dintr-un episod de 20 de zile = 75%
    c = calcul_cm(25200, 126, 7, zile_episod=20, prima_zi_din_episod=True, **B)
    assert c["procent"] == Decimal("75.00"), "procentul trebuie pe zile_episod (20 -> 75%), nu pe zilele certificatului (7)"


def test_diminuare_si_angajator_o_data_pe_episod():
    """Diminuarea de 1 zi si portia angajator (zilele 2-6) se aplica O DATA pe episod = pe certificatul
    INITIAL; certificatele de continuare: diminuare=0, zile_ang=0."""
    ini = calcul_cm(25200, 126, 7, zile_episod=20, prima_zi_din_episod=True, **B)
    cont = calcul_cm(25200, 126, 13, zile_episod=20, prima_zi_din_episod=False, **B)
    assert ini["diminuare"] == 1 and ini["zile_ang"] == 5, "initialul: diminuare 1 + primele 5 zile angajator"
    assert cont["diminuare"] == 0 and cont["zile_ang"] == 0, "continuarea: fara diminuare, fara portie angajator (deja pe initial)"
    # diminuare totala pe episod = 1 (nu 2)
    assert ini["diminuare"] + cont["diminuare"] == 1, "diminuarea NU se aplica de mai multe ori intr-un episod"


def test_episod_20_zile_brut_2850_la_baza_200():
    """Episod 7+13 = 20 zile, baza 200 lei/zi (ven6=25200/zile6=126=200): brut total = 2850 (75% pe 19
    zile platite, 1 zi diminuata pe initial). Per-certificat gresit ar da 660+1560=2220 (55%+65%)."""
    ini = calcul_cm(25200, 126, 7, zile_episod=20, prima_zi_din_episod=True, **B)
    cont = calcul_cm(25200, 126, 13, zile_episod=20, prima_zi_din_episod=False, **B)
    assert ini["brut"] + cont["brut"] == Decimal("2850.00")


def test_art_xi_plumbing_data_episod_initial():
    """art.XI L141/2025 plumbat: procentul se ia pe forma valabila la data certificatului INITIAL
    (data_episod_initial), nu la data certificatului curent. Azi o singura varianta (post-141) -> inert,
    dar plumbing-ul trebuie sa existe in cod pentru cand intra forma pre-141 (xfail #16)."""
    src = _read("core/salarizare.py")
    assert "data_episod_initial" in src, "parametrul data_episod_initial (art.XI) lipseste"
    assert re.search(r"procent_cm\([^\n]*la_data=data_episod_initial or la_data", src), \
        "procentul nu foloseste data certificatului INITIAL (art.XI)"


def test_gard_salveaza_paseaza_zile_episod():
    """GARD anti-regresie: salveaza_concediu calculeaza zile_episod (suma pe episod) si il paseaza la
    calcul_cm. Daca cineva revine la calcul pe certificatul izolat, testul PICA."""
    src = _read("core/salariati_api.py")
    assert re.search(r"zile_episod = sum\(", src), "salveaza_concediu nu mai insumeaza zilele pe episod"
    assert "zile_episod=zile_episod" in src, "salveaza_concediu nu mai paseaza zile_episod la calcul_cm"
    assert "prima_zi_din_episod=prima_zi" in src, "prima_zi_din_episod (diminuare/angajator o data) nu mai e pasat"
    # lock-ul perioadei confirmate cu instructiune (art.17(1) + lei)
    assert "art.17(1)" in src and "rectificativa" in src, "mesajul de refuz pe perioada confirmata nu mai e instructiune"
