# -*- coding: utf-8 -*-
"""Teste gardian pentru D112 - reparat 16.07.2026 dupa testul agregat pe toate 9
declaratii (secțiunea angajatorA lipsea complet - "sectiunea Creante este
obligatorie pt cif <> cif AJPIS").

Trei bug-uri, toate confirmate prin validatorul oficial + structura oficiala
(structura_D112_0126_030226.pdf):

1. <angajatorA> lipsea complet din XML - exista deja add_oblig() care o
   calcula, dar nimic n-o scria in H (lista de linii XML).

2. Rotunjire: round() Python (bancar, half-to-even) aplicat INAINTE de
   _d112int() facea ca 112.5 sa devina 112 in loc de 113 - contrazicea regula
   explicita din structura oficiala ("Contributiile se rotunjesc aritmetic").
   4 locuri afectate: cas, cass, imp, d17 (media CM).

3. Pozitia <angajatorA>: trebuie sa fie PRIMA in <angajator>, inaintea lui
   angajatorB/C1/C2/C4 - confirmat din lista completa de elemente din
   structura oficiala (linia 391 vine inaintea liniei 919 = angajatorB).
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
    """Regresie: mutata gresit dupa C4 prima data - structura oficiala o are
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
