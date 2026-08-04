# -*- coding: utf-8 -*-
"""Teste gardian pentru D390 — modulul n-avea niciunul.

Doua buguri gasite prin audit pe date reale (16.07.2026):
1. <rezumat> lipsea ca element separat (fix anterior gresit il pusese inline pe
   radacina, pe baza unui `strings` care n-a gasit clasa/tag "rezumat" - concluzie
   gresita: absenta dintr-un extras nu inseamna absenta).
2. pull() citea CUI-ul partenerului DOAR din clienti.cui (via client_id). Facturile
   fara fisa de client si TOATE facturile PRIMITE (care n-au niciodata client_id)
   aveau cui="" -> respinse tacit -> D390 genera mereu "0 operatiuni".
"""
import datetime
import pytest
from core import d390
from core.d390 import calcul_d390, build_xml, valideaza, operatiuni_auto


def test_d390_are_operatiuni_luna_deschisa_none_fara_db():
    """Poarta perioadei DESCHISE: luna curenta/viitoare -> None INAINTE de orice interogare (conn nefolosit).
    D390 nu e obligatie lunara fixa; luna deschisa nu se poate decide inca (exigibilitatea nu s-a nascut)."""
    AZI = datetime.date(2026, 7, 23)
    assert d390.d390_are_operatiuni(None, "x", 2026, 7, azi=AZI) is None    # luna curenta, inca deschisa
    assert d390.d390_are_operatiuni(None, "x", 2026, 12, azi=AZI) is None   # viitoare
    assert d390.d390_are_operatiuni(None, "x", 2099, 1, azi=AZI) is None    # mult in viitor


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA",
            "adresa": "Bd. Timisoara 26Z", "telefon": "0212345678"}


def test_operatiune_emisa_UE_intra_in_calcul():
    facturi = [{"cui": "IT00905811006", "nume": "AUCHAN ITALIA SPA",
                "directie": "emisa", "total": 5000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 6, facturi)
    assert res.nr_opi == 1
    assert res.rezumat["L"] == 5000


def test_operatiune_primita_UE_intra_in_calcul():
    """Regresie: facturile primite n-aveau niciodata client_id, deci CUI-ul lipsea."""
    facturi = [{"cui": "DE136695976", "nume": "BAUHAUS GMBH",
                "directie": "primita", "total": 2000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 6, facturi)
    assert res.nr_opi == 1
    assert res.rezumat["A"] == 2000


def test_rezumat_e_element_separat_in_xml():
    """<rezumat> exista ca element propriu, nu atribute pe radacina (dovedit pe
    ANAF structura D390 2020_180320, structura_D390_2020_180320.pdf: '<rezumat> 1 aparitie')."""
    res = calcul_d390(_prof(), 2026, 6, [
        {"cui": "IT00905811006", "nume": "X", "directie": "emisa", "total": 100, "tva": 0}])
    xml = build_xml(res)
    assert "<rezumat " in xml
    assert 'nrOPI="' not in xml.split("<rezumat")[0]  # nu e pe radacina


def test_factura_fara_cui_ue_valid_e_ignorata():
    facturi = [{"cui": "RO14399840", "nume": "FIRMA INTERNA",
                "directie": "emisa", "total": 1000, "tva": 210}]
    res = calcul_d390(_prof(), 2026, 6, facturi)
    assert res.nr_opi == 0
    assert "excluse" in " ".join(res.avertismente)


# ---------- F125: clasificare manuala (reclasificare + adaugare) ----------
_FACT_IC = [{"cui": "IT00905811006", "nume": "AUCHAN ITALIA SPA", "directie": "emisa", "total": 5000, "tva": 0}]


def test_reclasificare_muta_tipul_fara_dubla_numarare():
    """Auto pune emisa->L (bunuri). Reclasificat L->P (serviciu prestat) -> valoarea trece
    din L in P, NU se adauga (fara dubla numarare). nr_opi ramane 1."""
    recl = {("emisa", "IT", "00905811006"): "P"}
    res = calcul_d390(_prof(), 2026, 6, _FACT_IC, reclasificari=recl)
    assert res.rezumat["L"] == 0
    assert res.rezumat["P"] == 5000
    assert res.nr_opi == 1


def test_reclasificare_tip_invalid_ridica_nu_revine_tacit():
    """Un tip care nu e legal (aici 'Z', nici in nomenclator) NU revine tacit la default -
    ar fi MISCLASIFICARE tacuta. Ridica eroare vizibila, ACELASI principiu ca la liniile manuale
    (tip introdus de contabil, invalid -> eroare, nu disparitie/schimbare tacuta)."""
    with pytest.raises(ValueError) as e:
        calcul_d390(_prof(), 2026, 6, _FACT_IC, reclasificari={("emisa", "IT", "00905811006"): "Z"})
    m = str(e.value)
    assert "reclasificare" in m.lower() and "Z" in m, m


def test_reclasificare_directie_gresita_ridica():
    """'A' (achizitie) e in nomenclator DAR ilegal pe o operatiune EMISA (livrare): achizitia nu
    poate deveni livrare si invers (DECIZII 21.07). Read-side valideaza direciția ca write-side
    (salveaza_reclasificare), nu accepta tacit un tip valid-dar-nepotrivit-directiei."""
    with pytest.raises(ValueError) as e:
        calcul_d390(_prof(), 2026, 6, _FACT_IC, reclasificari={("emisa", "IT", "00905811006"): "A"})
    assert "direc" in str(e.value).lower(), str(e.value)


def test_linie_manuala_se_adauga():
    man = [{"tip": "S", "tara": "DE", "cod": "136695976", "den": "SERVICE", "baza": 1000}]
    res = calcul_d390(_prof(), 2026, 6, [], manual=man)
    assert res.rezumat["S"] == 1000
    assert res.nr_opi == 1


def test_operatiuni_auto_arata_tipul_curent():
    """Pt UI: operatiunea auto arata tip_default si tip_curent (reclasificat)."""
    recl = {("emisa", "IT", "00905811006"): "P"}
    ops = operatiuni_auto(_FACT_IC, recl)
    assert len(ops) == 1
    assert ops[0]["tip_default"] == "L" and ops[0]["tip_curent"] == "P"
    assert ops[0]["baza"] == 5000


def test_d390_manual_tip_necunoscut_ridica_nu_dispare():
    # [GARD CLASA] operatiune manuala a contabilului cu tip gresit -> eroare vizibila, nu skip tacit.
    with pytest.raises(ValueError) as e:
        calcul_d390(_prof(), 2026, 6, [], [{"tip": "ZZZ", "tara": "DE", "cod": "X", "den": "y", "baza": 100}])
    assert "tip necunoscut" in str(e.value)



def test_tipuri_operatiune_sunt_exact_nomenclatorul_oficial_opanaf_705_2020():
    """Pin anti-drift: cele 6 simboluri de tip operatiune D390 = nomenclatorul OFICIAL
    (OPANAF 705/2020, anaf_surse/d390_struct_anaf.txt, restrictia campului <operatie> tip:
    tip in (L,T,A,P,S,R)). Semnificatii: L=livrari IC bunuri, T=livrari triunghiulare,
    A=achizitii IC bunuri, P=prestari IC servicii, S=achizitii IC servicii, R=livrari IC
    regim special agricultori. Daca cineva adauga/scoate/schimba un simbol, testul cade si
    cere reverificarea la sursa - nomenclatorul spre ANAF nu se schimba tacit."""
    from core import d390
    assert d390.TIPURI == ("L", "T", "A", "P", "S", "R"), d390.TIPURI



def test_d390_rotunjeste_aritmetic_nu_bancar_A91b():
    """Sumele fiscale D390 se rotunjesc ARITMETIC (ROUND_HALF_UP), nu bancar. Referinta:
    DUK regula A91b (ANAF cere half-up; Python round() e half-to-even). Proba pe valorile unde
    difera - .5 urca MEREU, nu la parul cel mai apropiat. d390 e deja si in gardul de identitate
    cross-generator (test_rotunjirea_e_identica_intre_generatoare) si in scanul anti-round() bancar
    (test_toate_generatoarele_rotunjesc_aritmetic); asta fixeaza VALOAREA aritmetica, nu doar
    egalitatea intre generatoare (daca toate ar fi bancare, identitatea ar trece fals)."""
    from core.d390 import _int
    assert _int(0.5) == 1      # bancar (round) ar da 0
    assert _int(2.5) == 3      # bancar ar da 2
    assert _int(112.5) == 113  # cazul canonic A91b (CAM 112 -> 113)
    assert _int(1.4) == 1 and _int(1.6) == 2


def _oib_valid(base10="1234567890"):
    """OIB croat valid (ISO 7064 MOD 11,10) - pt. un partener HR care trece verificarea codO."""
    x = 10
    for ch in base10:
        x = (x + int(ch)) % 10
        if x == 0:
            x = 10
        x = (x * 2) % 11
    return base10 + str((11 - x) % 10)


def test_croatia_emite_HR_nu_CR():
    """NECONFORMITATE (probata DUK boundary): Croatia se emite cu tara="HR" (prefixul TVA = codul ISO),
    NU "CR". Maparea HR->CR (crezuta corecta) era GRESITA: DUK respinge "CR" ('nu se afla in lista' -
    nomenclatorul de tari ANAF nu are CR) si accepta "HR". Un partener croat real facea D390 respins."""
    facturi = [{"cui": "HR" + _oib_valid(), "nume": "ZAGREB DOO", "directie": "emisa", "total": 5000, "tva": 0}]
    xml = build_xml(calcul_d390(_prof(), 2026, 6, facturi))
    assert 'tara="HR"' in xml, "Croatia trebuie emisa HR"
    assert 'tara="CR"' not in xml, "CR nu e in nomenclatorul ANAF (respins de DUK)"


def test_croatia_HR_trece_duk():
    """Proba pana la validator: D390 cu partener croat (tara=HR) trece DUKIntegrator."""
    from core import duk
    if not duk.poate_valida("d390"):
        import pytest
        pytest.skip("DUK d390 indisponibil")
    facturi = [{"cui": "HR" + _oib_valid(), "nume": "ZAGREB DOO", "directie": "emisa", "total": 5000, "tva": 0}]
    xml = build_xml(calcul_d390(_prof(), 2026, 6, facturi))
    rez = duk.valideaza(xml, "d390", an=2026, luna=6)
    assert rez["stare"] == "valid", "DUK a respins D390 cu Croatia: %s" % rez.get("erori")


# ── Reimprospatare surse invechite (04.08.2026): TARI_UE + TIPURI ancorate pe validatorul instalat ──
def test_nomenclatoare_d390_ancorate_pe_validator_nu_pe_pdf_2020():
    """TARI_UE si TIPURI ancorate pe VALIDATORUL INSTALAT (D390_11), nu pe pdf-ul de structura din 2020
    (INVECHIT). Ambele seturi confirmate prin proba DUK boundary 04.08.2026 pe D390Validator.jar:
    - TARI_UE (28) = EXACT setul de tari recunoscut de validator: fiecare aplica algoritmul specific tarii (DUK regula R24.1,
      mesajul 'algoritmul specific X'); niciun cod mort (tiparul ASI NU apare). GB (post-Brexit) si XI recunoscute
      pentru 2026. Grecia = EL (GR respins 'nu se afla in lista'), Croatia = HR (CR respins). Niciun candidat
      exterior acceptat (GR/CR + microstate MC/SM/AD/LI/VA + Crown IM/JE/GG toate respinse) -> fara gap.
    - TIPURI (6) = EXACT tipurile acceptate: L/T/P/R (emisa) + A/S (primita) toate VALID; fake (Z/X/ASI) respinse.
    Spre deosebire de d301 (unde validatorul avea HRK in plus), d390 NU diverge de validatorul curent."""
    from core.d390 import TARI_UE, TIPURI
    # Seturile confirmate pe validatorul INSTALAT prin proba DUK 04.08.2026 (NU din pdf-ul 2020).
    VALIDATOR_TARI = {"AT", "BE", "BG", "CZ", "CY", "HR", "DK", "EE", "DE", "EL", "FI", "FR", "IE", "IT", "LV",
                      "LU", "LT", "MT", "GB", "NL", "PL", "PT", "SI", "SK", "ES", "SE", "HU", "XI"}
    VALIDATOR_TIPURI = {"L", "T", "A", "P", "S", "R"}
    assert set(TARI_UE) == VALIDATOR_TARI, "TARI_UE difera de setul validatorului (reprobeaza DUK): lipsa %s / in plus %s" % (
        sorted(VALIDATOR_TARI - set(TARI_UE)), sorted(set(TARI_UE) - VALIDATOR_TARI))
    assert set(TIPURI) == VALIDATOR_TIPURI, "TIPURI difera de setul validatorului: %s" % sorted(set(TIPURI) ^ VALIDATOR_TIPURI)
    # invarianti-cheie (VIES / nomenclator ANAF): Grecia EL nu GR; Croatia HR nu CR
    assert "EL" in TARI_UE and "GR" not in TARI_UE
    assert "HR" in TARI_UE and "CR" not in TARI_UE


def test_d390_snapshot_validator_confirmat_pe_duk():
    """Dinti pe snapshot: proba DUK vie confirma ca setul validatorului reflecta jar-ul instalat -
    GB recunoscut (algoritm R24.1 'GB'), o tara exterioara (CR) respinsa 'nu se afla in lista'. Gated."""
    import pytest
    from core import duk
    if not duk.poate_valida("d390"):
        pytest.skip("DUK d390 indisponibil")
    from core import d390
    prof = {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA", "adresa": "Bd. Timisoara 26Z", "telefon": "0212345678"}
    orig = set(d390.TARI_UE)
    def erori_pt(tara):
        d390.TARI_UE = orig | {tara}
        try:
            fac = [{"cui": tara + "123456789", "nume": "X SRL", "directie": "emisa", "total": 1000, "tva": 0}]
            return duk.valideaza(d390.build_xml(d390.calcul_d390(prof, 2026, 6, fac)), "d390", an=2026, luna=6)["erori"]
        finally:
            d390.TARI_UE = orig
    assert "algoritmul specific 'GB'" in erori_pt("GB"), "validatorul ar trebui sa recunoasca GB (R24.1)"
    assert "nu se afla in lista" in erori_pt("CR"), "validatorul ar trebui sa respinga CR"
