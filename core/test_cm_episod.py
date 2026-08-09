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


def test_art_xi_granita_pre_post_141():
    """art.XI L141/2025: forma art.17(1) dupa data certificatului INITIAL al episodului. Pana la
    1 august 2025 = 75% uniform (pre-141); de la 1 august 2025 = 55/65/75 progresiv (post-141)."""
    d1, d2 = date(2025, 7, 31), date(2025, 8, 1)
    assert procent_cm("01", 5, la_data=d1) == Decimal("0.75"), "pre-141: 5 zile = 75% uniform"
    assert procent_cm("01", 20, la_data=d1) == Decimal("0.75"), "pre-141: 20 zile = 75% uniform"
    assert procent_cm("01", 5, la_data=d2) == Decimal("0.55"), "post-141: 5 zile = 55%"
    assert procent_cm("01", 20, la_data=d2) == Decimal("0.75"), "post-141: 20 zile = 75%"
    assert procent_cm("01", 5, la_data=d1) != procent_cm("01", 5, la_data=d2), "granita 31 iul / 1 aug 2025 schimba regimul"


def test_coduri_speciale_neatinse_de_l141():
    """L141/2025 a modificat DOAR art.17(1) cod 01. alin.(2) 100% (infectocontagioase grupa A=05,
    carantina=07, TBC/neoplazii/SIDA=12) si maternitatea (08=85%) raman IDENTICE in ambele regimuri."""
    for d in (date(2025, 7, 31), date(2025, 8, 1)):
        assert procent_cm("05", 10, la_data=d) == Decimal("1.00")
        assert procent_cm("07", 10, la_data=d) == Decimal("1.00")
        assert procent_cm("12", 10, la_data=d) == Decimal("1.00")
        assert procent_cm("08", 10, la_data=d) == Decimal("0.85")


# ---------------------------------------------------------------------------
# OUG 91/2025 + Legea 64/2026 + Ordin 506/1030/2026 - verbatim (aduse in corpus 09.08.2026:
# anaf_surse/oug_91_2025.html, lege_64_2026.html, ordin_506_1030_2026_norme_oug158.html)
# ---------------------------------------------------------------------------

def test_diminuare_o_zi_lucratoare_exemplul_ordin_506():
    """Ordin 506/1030/2026 art.I pct.3 -> Norme art.78^4 alin.(4) VERBATIM:
    Ci = Mzbci x ....% x (NZLCM - 1), unde 'NZLCM - 1 = numarul de zile lucratoare din concediul
    medical minus prima zi lucratoare'. Exemplul din norma: 5 zile lucratoare, media 200,82 lei, 55%
    -> 200,82 x 55%% x 4 = 441,80 -> 442 lei. Se scade O ZI LUCRATOARE (nu calendaristica)."""
    r = calcul_cm(24300, 121, 5, cod="01", zile_episod=5, prima_zi_din_episod=True, la_data=date(2026, 7, 1))
    assert r["zile_platite"] == 4, "NZLCM-1 = 5 minus prima zi lucratoare = 4"
    assert r["procent"] == Decimal("55.00"), "episod 5 zile (<=7) -> 55%%"
    assert r["media_zilnica"] == Decimal("200.83") or r["media_zilnica"] == Decimal("200.82"), r["media_zilnica"]
    assert r["brut"] == Decimal("442"), "exemplul Ordin 506: 200,82 x 55%% x 4 = 442 lei (rotunjit la leu)"


def test_diminuare_fereastra_certificat_01022026_31122027():
    """OUG 91/2025 art.II(1) VERBATIM: 'Pentru certificatele de concediu medical eliberate in perioada
    1 februarie 2026-31 decembrie 2027 ... se calculeaza si se platesc prin diminuarea cu o zi'.
    In afara ferestrei: fara diminuare."""
    B0 = dict(cod="01", zile_episod=7, prima_zi_din_episod=True)
    assert calcul_cm(25200, 126, 7, la_data=date(2026, 1, 31), **B0)["diminuare"] == 0, "< 01.02.2026 fara diminuare"
    assert calcul_cm(25200, 126, 7, la_data=date(2026, 2, 1),  **B0)["diminuare"] == 1, "01.02.2026 diminuare"
    assert calcul_cm(25200, 126, 7, la_data=date(2027, 12, 31),**B0)["diminuare"] == 1, "31.12.2027 diminuare"
    assert calcul_cm(25200, 126, 7, la_data=date(2028, 1, 1),  **B0)["diminuare"] == 0, ">= 2028 fara diminuare"


def test_diminuare_exceptii_verbatim_art2_lit_c_d1_e():
    """Legea 64/2026 pct.3 -> OUG 91 art.II alin.(4) + Ordin 506 art.78^4 alin.(2^1) VERBATIM:
    diminuarea NU se aplica la CM prevazute la art.2 alin.(1) lit. c), d^1) si e) din OUG 158/2005.
    art.2(1) OUG 158 (oug_158_2005_consolidat.html): c)=maternitate(08), d^1)=oncologic(17), e)=risc
    maternal(15). lit d)=ingrijire copil bolnav(09) NU e in lista -> se diminueaza."""
    LA0 = date(2026, 7, 1)
    for cod in ("08", "15", "17"):
        r = calcul_cm(25200, 126, 7, cod=cod, zile_episod=7, prima_zi_din_episod=True, la_data=LA0)
        assert r["diminuare"] == 0, "cod %s (art.2(1) lit c/d^1/e) NU se diminueaza" % cod
    for cod in ("01", "09"):
        r = calcul_cm(25200, 126, 7, cod=cod, zile_episod=7, prima_zi_din_episod=True, la_data=LA0)
        assert r["diminuare"] == 1, "cod %s (NU e in lista de exceptii) se diminueaza" % cod


# ---------------------------------------------------------------------------
# Deciziile Costin 09.08.2026 (tura 5): izolare se diminueaza; exceptii de la 01.06.2026;
# cod 02 ramane nediminuat; gating pe data eliberarii.
# ---------------------------------------------------------------------------

def test_izolare_51_se_diminueaza():
    """Decizie Costin: izolarea (cod 51) SE DIMINUEAZA. Ordin 506 alin.(2^1)/(2^2) NU listeaza izolarea
    printre exceptii; norma de calcul prevaleaza asupra formatului D112 (care o excepta)."""
    r = calcul_cm(25200, 126, 7, cod="51", zile_episod=7, prima_zi_din_episod=True, la_data=date(2026, 7, 1))
    assert r["diminuare"] == 1, "izolare 51 se diminueaza (nu mai e exceptata)"


def test_exceptii_de_la_01062026_nu_de_la_01022026():
    """Legea 64/2026 art.VI(4): exceptiile alin.(4)/(5) (08/15/17 + spitalizare + programe nationale) se
    aplica DE LA 01.06.2026. Certificat eliberat inainte (02-05.2026): exceptia NU se aplica -> se diminueaza."""
    B0 = dict(zile_episod=7, prima_zi_din_episod=True)
    # maternitate 08: eliberat 03.2026 -> diminuat; eliberat 07.2026 -> exceptat
    assert calcul_cm(25200, 126, 7, cod="08", data_eliberare=date(2026, 3, 1), **B0)["diminuare"] == 1
    assert calcul_cm(25200, 126, 7, cod="08", data_eliberare=date(2026, 7, 1), **B0)["diminuare"] == 0
    # spitalizare: la fel (flag), fazat 01.06.2026
    assert calcul_cm(25200, 126, 7, cod="01", spitalizare=True, data_eliberare=date(2026, 3, 1), **B0)["diminuare"] == 1
    assert calcul_cm(25200, 126, 7, cod="01", spitalizare=True, data_eliberare=date(2026, 7, 1), **B0)["diminuare"] == 0


def test_cod_02_03_04_se_diminueaza():
    """Decizie Costin (09.08 tura 8, propunere aplicata): codurile accident 02/03/04 ('neconfirmat de casa de
    pensii', Nomenclator 9 = G1/OUG 158 cat timp neconfirmate) SE DIMINUEAZA ca orice cod G1. Legea 319/2006
    art.5 lit.g) (accident de munca, include traseu) + Legea 346/2002 = FAAMBP abia DUPA confirmare (ies din CM)."""
    for cod in ("02", "03", "04"):
        for elib in (date(2026, 3, 1), date(2026, 7, 1)):
            r = calcul_cm(25200, 126, 7, cod=cod, zile_episod=7, prima_zi_din_episod=True, data_eliberare=elib)
            assert r["diminuare"] == 1, "cod %s se diminueaza G1/OUG 158 (elib %s)" % (cod, elib)


def test_gating_pe_data_eliberarii_nu_pe_data_inceput():
    """OUG 91/2025 art.II(1): fereastra pe 'certificatele ELIBERATE in perioada'. Dispecerul foloseste
    data_eliberare (data acordarii), nu data_inceput (la_data). Certificat cu inceput in fereastra dar
    ELIBERAT inainte de 01.02.2026: NU se diminueaza."""
    B0 = dict(cod="01", zile_episod=7, prima_zi_din_episod=True, la_data=date(2026, 3, 1))  # inceput in fereastra
    assert calcul_cm(25200, 126, 7, data_eliberare=date(2026, 1, 20), **B0)["diminuare"] == 0, "eliberat < 01.02.2026"
    assert calcul_cm(25200, 126, 7, data_eliberare=date(2026, 3, 1),  **B0)["diminuare"] == 1, "eliberat in fereastra"


def test_program_national_exceptat_de_la_diminuare():
    """D_9a: pacient inclus in program national de sanatate -> exceptat de la diminuare (Ordin 506/1030/2026
    art.78^4 alin.(2^1)), fazat de la 01.06.2026 (Legea 64 art.VI(4)). Inainte de 06.2026 inca se diminueaza."""
    B0 = dict(cod="01", zile_episod=7, prima_zi_din_episod=True)
    assert calcul_cm(25200, 126, 7, program_national=True,  data_eliberare=date(2026, 7, 1), **B0)["diminuare"] == 0
    assert calcul_cm(25200, 126, 7, program_national=True,  data_eliberare=date(2026, 3, 1), **B0)["diminuare"] == 1
    assert calcul_cm(25200, 126, 7, program_national=False, data_eliberare=date(2026, 7, 1), **B0)["diminuare"] == 1
