# -*- coding: utf-8 -*-
"""[lotul 13, comanda 13.1 pct.5 + deficiența 656] PROBA AUTOMATĂ PE TOATE DECLARAȚIILE RARE: fiecare se generează pe date minime complete,
trece prin verificarea proprie a cifrelor (`core.verificare_bun_simt`) și prin validatorul oficial ANAF (DUK, judecătorul structurii).

Comanda, verbatim: „Fă probă automată pe toate declarațiile rare cu validatorul ANAF, plus verificarea de bun-simț a cifrelor cerută la
656.” Iar 656: „D207 cu impozit reținut 160 lei pe bază 1 leu a fost generată și validată (DUKIntegrator verifică doar structura).
Lipsește verificarea proprie: impozit ≤ bază și cota conformă tipului de venit și actului normativ.”

RARE = declarațiile dispecerului (`declaratii_api.DECLARATII`) în afara celor nouă periodice generice (D100, D101, D112, D205, D300, D301,
D390, D394, D406). Garda de acoperire: o declarație rară nouă fără caz aici face testul roșu, iar una fără verificare proprie trebuie să
fie numită, cu motivul, în `verificare_bun_simt.FARA_CIFRE`. Datele minime sunt cele probate deja pe DUK de testele fiecărei declarații —
se refolosesc (o singură sursă), nu se rescriu.

Temeiurile cotelor (textul în `core/verificare_bun_simt.py`): CF art.224 alin.(4) lit.b-d; OUG 156/2024 art.LXIV pct.15; CF art.230
alin.(1); CF art.500^2 lit.a; HG 1/2016 pct.73 alin.(13)-(14)."""
import pytest

from core import declaratii_api, duk, verificare_bun_simt as V
from core.common import Perioada

GENERICE = {"d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406"}
RARE = sorted(set(declaratii_api.DECLARATII) - GENERICE)


def _din_loturi():
    """{tip: (generează, an, luna, corpul cererii)} din cazurile loturilor de declarații (probate DUK la construcție)."""
    from core import test_declaratii_lot2_duk as L2, test_declaratii_lot3_duk as L3, test_declaratii_lot4_duk as L4, \
        test_declaratii_lot5_duk as L5
    out = {}
    for tip, mod, per, manual in L2.CAZURI + L4.CAZURI:
        out[tip] = (lambda mod=mod, per=per, manual=manual: mod.genereaza(None, None, per, manual), per.an, per.luna, manual)
    for tip, mod, conn, per in L3.CAZURI:
        m = L3._MANUAL[tip]
        out[tip] = (lambda mod=mod, conn=conn, per=per, m=m: mod.genereaza(conn, "tenant_013", per, m), per.an, per.luna, m)
    for c in L5.CAZURI:
        tip, mod, per, manual = c[0], c[1], c[2], c[3]
        out[tip] = (lambda mod=mod, per=per, manual=manual: mod.genereaza(None, None, per, manual), per.an, per.luna, manual)
    return out


def _din_teste_pe_tip():
    from core import d104, d107, d110, d177, d207, d212, d230, d307, d311
    from core import test_d104 as T104, test_d107 as T107, test_d110 as T110, test_d177 as T177, test_d207 as T207, \
        test_d230 as T230, test_d307 as T307, test_d311 as T311, test_d710 as T710
    from core.d710 import build_xml as _b710
    m110 = {"obligatii": [{"cod_oblig": "604", "suma_dat": 1000, "suma_rest": 1}]}
    m311 = T311._manual()
    m212 = {"cif": "1800101221144", "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}
    m207 = T207._manual()
    m207["beneficiari"][0]["imp"] = 1000   # dividende 2025: 10% din 10.000 (CF art.224 alin.(4) lit.b, OUG 156/2024)
    m207["beneficiari"][1]["imp"] = 800    # dobânzi: 16% din 5.000 (CF art.224 alin.(4) lit.d)
    return {
        "d104": (lambda: d104.genereaza(T104._P(), "s", Perioada(2024, trim=4), T104._manual()), 2024, 12, T104._manual()),
        "d107": (lambda: d107.genereaza(T107._P(), "s", Perioada(2024, luna=12), T107._manual()), 2024, 12, T107._manual()),
        "d110": (lambda: d110.genereaza(T110._P(), "s", Perioada(2025, luna=6), m110), 2025, 6, m110),
        "d177": (lambda: d177.genereaza(T177._P(), "s", Perioada(2025, luna=12), T177._manual()), 2025, 12, T177._manual()),
        # [656] datele testului D207 aveau 8% la dividende în 2025 și 5% la dobânzi cu actul „Cod fiscal” — cifre pe care Codul fiscal nu le
        # dă (CF art.224 alin.(4): 10% dividendele în 2025, 16% / 10% dobânzile); proba folosește cotele legii
        "d207": (lambda: d207.genereaza(T207._P(), "s", Perioada(2025, luna=12), m207), 2025, 12, m207),
        "d212": (lambda: d212.genereaza(None, None, Perioada(an=2025), m212), 2025, 12, m212),
        "d230": (lambda: (d230.build_xml(T230._prof(), 2025, 12, T230._manual()), None), 2025, 12, T230._manual()),
        "d307": (lambda: d307.genereaza(T307._P(), "s", Perioada(2026, luna=7), T307._manual()), 2026, 7, T307._manual()),
        "d311": (lambda: (d311.build_xml(T311._prof(), 2026, 6, m311, *d311.calcul_d311(m311)), None), 2026, 6, m311),
        "d710": (lambda: (_b710(T710.calcul_d710(T710._prof(), 2025, 3, T710._obl())), None), 2025, 3, {"obligatii": T710._obl()}),
    }


def _cazuri():
    c = _din_loturi()
    c.update(_din_teste_pe_tip())
    return c


CAZURI = _cazuri()


def test_fiecare_declaratie_rara_are_proba_si_e_clasificata():
    """Acoperirea: fiecare declarație rară are cazul ei aici, iar verificarea proprie ori o are (`VERIFICARI`), ori spune de ce nu
    (`FARA_CIFRE`). MUTAȚIE: un tip scos din `FARA_CIFRE` -> ROȘU."""
    assert sorted(set(RARE) - set(CAZURI)) == [], "declarații rare fără probă automată"
    neclasificate = [t for t in RARE if t not in V.VERIFICARI and t not in V.FARA_CIFRE]
    assert neclasificate == [], neclasificate
    assert all(len(V.FARA_CIFRE[t]) > 20 for t in V.FARA_CIFRE), "motivul se scrie, nu se lasă gol"


@pytest.mark.parametrize("tip", RARE)
def test_declaratia_rara_trece_verificarea_proprie_si_validatorul_anaf(tip):
    """Date minime complete -> verificarea proprie nu găsește nimic, iar DUK spune „valid”."""
    gen, an, luna, manual = CAZURI[tip]
    er, _av = V.verifica(tip, {"an": an, "luna": luna, "manual": manual})
    assert er == [], er
    xml, _res = gen()
    v = duk.valideaza(xml, tip, an=an, luna=luna, timeout=120)
    if v.get("stare") == "gri":
        pytest.skip("validatorul %s nu e instalat: %s" % (tip, v.get("temei")))
    assert v.get("stare") == "valid", "%s: %s" % (tip, v)


def _d207(**ben):
    b = {"tip_venit": "01", "den": "KUNDE GMBH", "stat": "DE", "cif_strain": "DE123", "act_n": "1", "baza": 10000, "imp": 1600,
         "imp_suportat": 0}
    b.update(ben)
    return {"an": 2026, "luna": 12, "manual": {"beneficiari": [b]}}


def test_656_d207_impozit_160_pe_baza_1_se_opreste_inaintea_validatorului():
    """Cazul din 656: impozit 160 pe bază 1 leu. Validatorul ANAF îl primește (structura e bună); verificarea proprie îl oprește.
    CF art.224 alin.(4): impozitul „se calculează prin aplicarea următoarelor cote asupra veniturilor brute”."""
    er, _ = V.verifica("d207", _d207(baza=1, imp=160))
    assert len(er) == 1 and "impozitul (160 lei) e mai mare decât baza (1 lei)" in er[0], er
    with pytest.raises(ValueError, match="verificarea cifrelor"):
        V.poarta("d207", _d207(baza=1, imp=160), None)


def test_656_d207_cota_dividendelor_dupa_anul_distribuirii():
    """CF art.224 alin.(4) lit.b): 16% de la 01.01.2026 (Legea 141/2025); 10% în 2025 (OUG 156/2024 art.LXIV pct.15)."""
    assert V.verifica("d207", _d207())[0] == []                                          # 16% din 10.000
    assert V.verifica("d207", dict(_d207(imp=1000), an=2025))[0] == []                    # 10% în 2025
    er = V.verifica("d207", _d207(imp=1000))[0]                                           # 10% în 2026 cu Codul fiscal -> nu
    assert er and "16%" in er[0] and "1.600 lei" in er[0], er


def test_656_d207_alte_venituri_cotele_codului_fiscal_si_conventia():
    """Dobânzi (02): 16% (lit.d) sau 10% (lit.c^1) cu Codul fiscal; cu convenția (art.230 alin.(1)) cel mult cota Codului."""
    assert V.verifica("d207", _d207(tip_venit="02", imp=1600))[0] == []
    assert V.verifica("d207", _d207(tip_venit="02", imp=1000))[0] == []
    assert V.verifica("d207", _d207(tip_venit="02", imp=700))[0]                          # 7%: nici o cotă a Codului
    assert V.verifica("d207", _d207(tip_venit="02", imp=500, act_n="2"))[0] == []        # convenția: 5%
    assert V.verifica("d207", _d207(tip_venit="02", imp=2000, act_n="2"))[0]             # convenția peste 16%
    assert V.verifica("d207", _d207(tip_venit="23", imp=500, act_n="1"))[0]              # „cf. convenției” cu actul Cod fiscal
    assert V.verifica("d207", _d207(tip_venit="14", imp=0))[0] == []                     # scutit


def test_656_impozit_peste_baza_la_celelalte_declaratii_cu_baza():
    """D104, D205 (completat de mână), D208, D311: impozitul / TVA-ul nu depășește baza."""
    assert V.verifica("d104", {"manual": {"asociati": [{"den": "A", "venit": 100, "imp_datorat": 500}]}})[0]
    assert V.verifica("d205", {"manual": {"beneficiari": [{"nume": "A", "baza": 100, "imp": 500}]}})[0]
    ben = {"nume": "A", "cotaImpozit": 3, "baza_calcul": 300000, "impozit": 9000}
    assert V.verifica("d208", {"manual": {"imobile": [{"beneficiari": [ben]}]}})[0] == []
    assert V.verifica("d208", {"manual": {"imobile": [{"beneficiari": [dict(ben, impozit=900)]}]}})[0]
    assert V.verifica("d311", {"an": 2026, "luna": 6, "manual": {"OB_11": 100, "OB_12": 210}})[0]


def test_656_d216_cota_legii_pe_anul_declarat():
    """CF art.500^2 lit.a: 0,9% în 2026 (`common.cota("impozit_special_valoare_mare")`); 0,3% scris pe 2026 se oprește."""
    m = {"imobile": [{"cota": 0.3, "valoare_impozabila_imobil": 3000000, "plafon_imobil": 2500000}]}
    assert V.verifica("d216", {"an": 2026, "manual": m})[0]
    assert V.verifica("d216", {"an": 2025, "manual": m})[0] == []


def test_638_d318_pragul_minim_al_cererii_de_rambursare():
    """HG 1/2016 pct.73 alin.(13): perioadă mai scurtă de un an -> cel puțin 400 euro; alin.(14): anul (sau restul lui) -> 50 euro.
    Calcul pur, în euro (moneda EUR; altă monedă cere cursurile BNR, deci conexiunea — proba aceea e la e2e)."""
    def m(ded, li, ls):
        return {"manual": {"an": 2026, "luna_inceput": li, "luna_sfarsit": ls, "currency": "EUR",
                           "achizitii": [{"taxable_amount": 1000, "vat_amount": ded, "deductible_vat": ded}]}}
    assert V.verifica("d318", m(80, 7, 9))[0]                    # T3, 80 euro < 400
    assert V.verifica("d318", m(450, 7, 9))[0] == []
    assert V.verifica("d318", m(60, 7, 12))[0] == []             # restul anului: pragul 50
    assert V.verifica("d318", m(40, 1, 12))[0]
    er, av = V.verifica("d318", dict(m(80, 7, 9), manual=dict(m(80, 7, 9)["manual"], currency="HUF")))
    assert er == [] and av and "nu s-a putut verifica" in av[0]   # fără curs (fără conexiune): avertisment, nu tăcere
