# -*- coding: utf-8 -*-
"""Teste gardian pentru D112 - reparat 16.07.2026 dupa testul agregat pe toate 9
declaratii (secțiunea angajatorA lipsea complet - "sectiunea Creante este
obligatorie pt cif <> cif AJPIS").

Trei bug-uri, toate confirmate prin validatorul oficial + ANAF structura D112 0126_030226
(structura_D112_0126_030226.pdf):

1. <angajatorA> lipsea complet din XML - exista deja add_oblig() care o
   calcula, dar nimic n-o scria in H (lista de linii XML).

2. Rotunjire: round() Python (bancar, half-to-even) aplicat INAINTE de
   _d112int() facea ca 112.5 sa devina 112 in loc de 113 - contrazicea regula
   explicita din ANAF structura D112 0126_030226 ("Contributiile se rotunjesc aritmetic").
   4 locuri afectate: cas, cass, imp, d17 (media CM).

3. Pozitia <angajatorA>: trebuie sa fie PRIMA in <angajator>, inaintea lui
   angajatorB/C1/C2/C4 - confirmat din lista completa de elemente din
   ANAF structura D112 0126_030226 (linia 391 vine inaintea liniei 919 = angajatorB).
"""
from core.d112 import _d112int, _d112_genereaza


def cnp_valid(baza12):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    s = sum(int(baza12[i]) * ch[i] for i in range(12))
    c = s % 11
    return baza12 + str(1 if c == 10 else c)


def _prof():
    return {"nume": "FIRMA TEST SRL", "cui": "14399840", "caen": "4711",
            "judet": "B", "declarant_nume": "POPESCU",
            "declarant_prenume": "Ion", "declarant_functie": "ADMINISTRATOR"}


def _sal(brut=5000):
    cas = round(brut * 0.25)
    cass = round(brut * 0.10)
    impozit = round((brut - cas - cass) * 0.10)
    return [{"nume": "IONESCU", "prenume": "Maria", "cnp": cnp_valid("290010145001"),
             "brut": brut, "cas": cas, "cass": cass, "impozit": impozit,
             "part_time": False, "ore_zi": 8, "persoane_intretinere": 0,
             "judet_casa": "B", "cor": "263501", "data_angajare": "2024-01-15",
             "activ": True}]


def test_rotunjire_aritmetica_nu_bancara():
    """112.5 -> 113 (aritmetic), nu 112 (bancar/half-to-even) - dovedit pe
    validator: 'C4_ct (112) = C4_ct calculat cf. regulii (113)'."""
    assert _d112int(112.5) == 113
    assert _d112int(112.4) == 112
    assert _d112int(112.6) == 113


def test_angajatorA_apare_in_xml():
    """Regresie: add_oblig() calcula A, dar H.extend(A) lipsea complet din
    build - XML-ul nu avea deloc sectiunea, indiferent de sume."""
    xml, av = _d112_genereaza(_prof(), _sal(), 2026, 6)
    assert "<angajatorA " in xml
    assert xml.count("<angajatorA ") == 4  # impozit, CAS, CASS, CAM


def test_angajatorA_e_prima_in_angajator():
    """Regresie: mutata gresit dupa C4 prima data - ANAF structura D112 0126_030226 o are
    PRIMA (linia 391 din document, inaintea lui angajatorB la linia 919)."""
    xml, av = _d112_genereaza(_prof(), _sal(), 2026, 6)
    poz_A = xml.index("<angajatorA ")
    poz_B = xml.index("<angajatorB ")
    assert poz_A < poz_B


def test_codurile_de_obligatie_corecte():
    xml, av = _d112_genereaza(_prof(), _sal(), 2026, 6)
    assert 'A_codOblig="602"' in xml  # impozit
    assert 'A_codOblig="412"' in xml  # CAS
    assert 'A_codOblig="432"' in xml  # CASS
    assert 'A_codOblig="480"' in xml  # CAM


# ============================================================
#  SUPRATAXARE part-time: campurile ANAF asigExc / motivExc (art. 146 alin.(5^6)-(5^7) CF).
#  Sesiunea A (29.07.2026): cod verificat CORECT la sursa; se adauga testele care lipseau.
# ============================================================
def _sal_ex(brut=5000, **extra):
    """_sal() cu chei suprascrise (scutit / motiv_exceptare / pt_aplica) pentru cazurile de suprataxare."""
    s = _sal(brut)[0].copy()
    s.update(extra)
    return [s]


def test_scutit_motiv_valid_emite_asigexc1_si_motivexc():
    xml, _ = _d112_genereaza(_prof(), _sal_ex(scutit=True, motiv_exceptare=1), 2026, 6)
    assert 'asigExc="1"' in xml    # art. 146 alin.(5^7) lit.a) CF - elev/student <26 ani: exceptat de la suprataxare
    assert 'motivExc="1"' in xml   # structura D112 (ANAF): motivExc (1-5 = literele a-e) se declara DOAR cand asigExc=1


def test_sub_minim_nescutit_emite_asigexc2_fara_motivexc():
    xml, _ = _d112_genereaza(_prof(), _sal_ex(brut=2000, pt_aplica=True), 2026, 6)
    assert 'asigExc="2"' in xml    # art. 146 alin.(5^6) CF - venit sub minim, NEexceptat: contributia minima e datorata
    assert 'motivExc' not in xml   # structura D112: motivExc NU se declara la asigExc=2, doar la asigExc=1 (exceptat)


def test_scutit_motiv_invalid_nu_emite_asigexc1():
    for motiv in (0, 6, None):
        xml, _ = _d112_genereaza(_prof(), _sal_ex(scutit=True, motiv_exceptare=motiv), 2026, 6)
        assert 'asigExc="1"' not in xml, motiv   # art. 146 (5^7): motivExc valid e 1-5 (lit. a-e); motiv in afara NU e exceptare, altfel ANAF respinge declaratia
        assert 'motivExc' not in xml, motiv      # fara asigExc=1 nu se declara motivExc


def test_peste_minim_asigexc_zero():
    xml, _ = _d112_genereaza(_prof(), _sal(6000), 2026, 6)
    assert 'asigExc="0"' in xml     # art. 146 alin.(5^6) CF - venit >= salariul minim: suprataxarea nu se aplica (asigExc=0)
    assert 'asigExc="1"' not in xml and 'asigExc="2"' not in xml   # nici exceptat, nici suprataxat
    assert 'motivExc' not in xml    # asigExc=0 -> fara motivExc


# ============================================================
#  Baze contributii D112 - cotele salariale PERIOD-AWARE din COTE (nu literale).
#  Verificat verbatim la sursa (anaf_surse/cod_fiscal_227_2015_consolidat.html):
#    CAS 25%  - CF art.138 lit.a (contributia de asigurari sociale, cota generala)
#    CASS 10% - CF art.156 (contributia de asigurari sociale de sanatate)
#    impozit  10% - CF art.78 alin.(2) (cota de impozit pe venitul din salarii)
#    CAM 2.25% - CF art.220^3 alin.(1) (contributia asiguratorie pentru munca)
# ============================================================
def test_cotele_contributii_din_cote_cu_temei():
    from decimal import Decimal
    from datetime import date
    from core.common import cota
    ref = date(2026, 8, 1)
    assert cota("cas", ref)[0] == Decimal("0.25")            # CF art.138 lit.a
    assert cota("cass", ref)[0] == Decimal("0.10")           # CF art.156
    assert cota("impozit_venit", ref)[0] == Decimal("0.10")  # CF art.78 alin.(2)
    assert cota("cam", ref)[0] == Decimal("0.0225")          # CF art.220^3 alin.(1)
    # fiecare cota vine cu temei documentat in COTE (nu literal fara sursa)
    for nume in ("cas", "cass", "impozit_venit", "cam"):
        temei = cota(nume, ref)[1]
        assert temei and str(temei).strip(), nume


def test_d112_ruteaza_cotele_prin_cote_nu_literale():
    # GARD anti-hardcode: _d112_genereaza si pull NU mai contin literalele 0.25/0.10/0.0225
    # pentru cotele de contributii - trebuie sa citeasca din cota(). Daca cineva rescrie
    # literalul, testul pica si trimite inapoi la COTE (sursa unica period-aware).
    import inspect, re
    from core import d112
    src = inspect.getsource(d112._d112_genereaza)
    assert "bazac * 0.25" not in src   # CAS: routat prin _cota_cas
    assert "bazac * 0.10" not in src   # CASS: routat prin _cota_cass
    assert "bimp * 0.10" not in src    # impozit: routat prin _cota_imp
    assert "sum_bazac * 0.0225" not in src  # CAM: routat prin _cota_cam
    assert "_cota_cas" in src and "_cota_cass" in src and "_cota_imp" in src and "_cota_cam" in src
    psrc = inspect.getsource(d112.pull)
    assert "prag_zile * 0.25" not in psrc and "prag_zile * 0.10" not in psrc
    assert 'cota("cas"' in psrc and 'cota("cass"' in psrc


def test_d112_cas_cass_valori_neschimbate_dupa_rutare():
    # Proba pe date reale: rutarea prin cota() e VALUE-PRESERVING (cota == literalul vechi).
    # Generarea D112 pt un brut real trebuie sa ramana identica cu cota din COTE (golden D112
    # o pinneaza integral); aici verificam invariantul aritmetic al rutarii: cota() = literalul.
    from decimal import Decimal
    from datetime import date
    from core.common import cota
    ref = date(2026, 6, 1)
    assert float(cota("cas", ref)[0]) == 0.25 and float(cota("cass", ref)[0]) == 0.10
    assert float(cota("cam", ref)[0]) == 0.0225 and float(cota("impozit_venit", ref)[0]) == 0.10
    # generarea reala nu arunca dupa rutare (brut 6000, full-time)
    xml, _ = _d112_genereaza(_prof(), _sal(6000), 2026, 6)
    assert xml and "<asigurat" in xml


# ============================================================
#  A91b pt minimul PART-TIME: sumele fiscale (baza + CAS/CASS pe prag) se rotunjesc
#  ARITMETIC (half-up), nu bancar. Descoperit la clusterul rotunjire aritmetica (A91b) | d112:
#  prag_zile/cas_min_pt/cass_min_pt foloseau round() Python (bancar/half-to-even), iar _d112int
#  ulterior era NO-OP (valoarea era deja intreaga) -> divergenta ajungea in B4_*P declarat.
#  Regula: ANAF structura D112 "Contributiile se rotunjesc aritmetic" (validator DUK regula A91b).
# ============================================================
def test_partime_minim_rotunjeste_aritmetic_nu_bancar():
    from core.d112 import _d112int
    # PROBA pe valori reale de prag: bancar (round) da o suma GRESITA la granita .5, aritmetic o corecteaza.
    # prag_zile=1226: CAS = 1226 x 0.25 = 306.5 -> bancar 306 (impar->par), ANAF cere 307.
    assert round(1226 * 0.25) == 306        # comportamentul BANCAR (gresit pt ANAF)
    assert _d112int(1226 * 0.25) == 307     # aritmetic (half-up) = valoarea CERUTA
    # prag_zile=1225: CASS = 1225 x 0.10 = 122.5 -> bancar 122, ANAF cere 123.
    assert round(1225 * 0.10) == 122        # BANCAR (gresit)
    assert _d112int(1225 * 0.10) == 123     # aritmetic = corect


def test_partime_minim_foloseste_d112int_nu_round_bancar():
    # GARD anti-regresie pe SURSA functiei pull: minimul part-time (prag_zile, cas_min_pt,
    # cass_min_pt) NU mai foloseste round() bancar - trebuie _d112int (half-up). Daca cineva
    # rescrie cu round(), pica aici si trimite la A91b.
    import inspect
    from core import d112
    src = inspect.getsource(d112.pull)
    assert "prag_zile = round(" not in src
    assert 's["cas_min_pt"] = round(' not in src
    assert 's["cass_min_pt"] = round(' not in src
    assert "prag_zile = _d112int(" in src
    assert 's["cas_min_pt"] = _d112int(' in src
    assert 's["cass_min_pt"] = _d112int(' in src



def test_limita_75_asigurat_si_functie_declar_50():
    """GARD (neconformitate 03.08.2026, cluster limita text 75 | d112): campurile text D112 respecta
    limita din structura ANAF (structura_D112_0126_030226) SI acolo unde nu e 75:
      - numeAsig/prenAsig (nume/prenume salariat, C(75)) erau doar escapate, NEtrunchiate -> un nume
        > 75 caractere era respins de ANAF ("sir mai lung de 75 caractere");
      - functie_declar are C(50), nu C(75) -> se trunchia gresit la 74 in loc de 50."""
    import re
    prof = _prof(); prof["declarant_functie"] = "D" * 60          # > 50
    sal = _sal(); sal[0]["nume"] = "N" * 90; sal[0]["prenume"] = "P" * 80   # > 75
    xml, _av = _d112_genereaza(prof, sal, 2026, 6)
    mf = re.search(r'functie_declar="([^"]*)"', xml)
    assert mf and len(mf.group(1)) <= 50, "functie_declar = %d car (structura C50)" % (len(mf.group(1)) if mf else -1)
    for attr in ("numeAsig", "prenAsig"):
        m = re.search(r'%s="([^"]*)"' % attr, xml)
        assert m, "%s lipseste din XML" % attr
        assert len(m.group(1)) <= 74, "%s = %d car (structura C75, marja 74)" % (attr, len(m.group(1)))



def test_cod_oblig_pereche_cu_cod_bugetar_corect():
    """GARD (verificare nomenclator 03.08.2026, cluster nomenclator cod_oblig | d112): fiecare cod_oblig
    D112 poarta codul bugetar CORECT din nomenclatorul oficial ANAF (structura D112, Nomenclator 3 -
    Obligatii de plata la BS si BASFS). Esential: 480 (CAM) are cod bugetar 20470300XX, DIFERIT de
    5503XXXXXX al celorlalte (602 impozit salarii, 412 CAS, 432 CASS). Testul vechi verifica doar
    codOblig ca substring -> o inversare a codului bugetar (ex. 480 cu 5503XXXXXX) trecea nedetectata."""
    import re
    xml, _av = _d112_genereaza(_prof(), _sal(), 2026, 6)
    perechi = dict(re.findall(r'<angajatorA A_codOblig="(\d+)" A_codBugetar="([^"]+)"', xml))
    assert perechi.get("602") == "5503XXXXXX", "602 (impozit) cod bugetar gresit: %r" % perechi.get("602")
    assert perechi.get("412") == "5503XXXXXX", "412 (CAS) cod bugetar gresit: %r" % perechi.get("412")
    assert perechi.get("432") == "5503XXXXXX", "432 (CASS) cod bugetar gresit: %r" % perechi.get("432")
    assert perechi.get("480") == "20470300XX", "480 (CAM) trebuie 20470300XX, nu %r" % perechi.get("480")
