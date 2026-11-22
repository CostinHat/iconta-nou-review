"""Teste D110 (regularizare/restituire impozit pe venit retinut la sursa).
Structura din validatorul oficial (D110Validator.jar, v0/namespace :v1) + semantica din anaf_surse
(structura_D110_2026_240326 + d110_20260330.xsd). nr_evid: control = suma primelor 21 cifre % 100
(CONFIRMAT empiric pe DUKIntegrator). Proba pe DUKIntegrator -v D110."""
import os
import pytest
from core import d110
from core.common import Perioada

_JAR = "/home/costin/duk/dist/lib/D110Validator.jar"


class _P:
    def cursor(self): return self
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q): pass
    def fetchone(self):
        return ("TEST SRL", "14399840", "Str Exemplu 1", "Bucuresti", "B", "POPESCU", "ION", "ADMIN",
                "021", "t@t.ro", "RO49AAAA1B31007593840000", "Banca Test")


def test_d110_dif_si_total():
    """dif_plata=suma_dat-suma_rest daca >=0 (altfel dif_rest); totalPlata_A=sum(dif_plata+dif_rest)."""
    c = d110.calcul_d110(6, 2025, {"obligatii": [
        {"cod_oblig": "604", "suma_dat": 1000, "suma_rest": 1},        # plata: dif_plata=999
        {"cod_oblig": "605", "suma_dat": 200, "suma_rest": 500}]})     # restituire: dif_rest=300
    o1, o2 = c["obligatii"]
    assert o1["dif_plata"] == 999 and o1["dif_rest"] == 0
    assert o2["dif_plata"] == 0 and o2["dif_rest"] == 300
    assert c["totalPlata_A"] == 999 + 300 and c["sigma_dif_rest"] == 300


def test_d110_nr_evid_control_si_cod_bugetar():
    """nr_evid 23 caractere, control = suma primelor 21 cifre % 100; cod_bugetar 5503XXXXXX (629 -> 20A031800X)."""
    c = d110.calcul_d110(6, 2025, {"obligatii": [{"cod_oblig": "604", "suma_dat": 1000, "suma_rest": 1}]})
    ne = c["obligatii"][0]["nr_evid"]
    assert len(ne) == 23
    assert int(ne[-2:]) == sum(int(x) for x in ne[:21]) % 100
    assert c["obligatii"][0]["cod_bugetar"] == "5503XXXXXX"
    c629 = d110.calcul_d110(6, 2025, {"obligatii": [{"cod_oblig": "629", "suma_dat": 100, "suma_rest": 1}]})
    assert c629["obligatii"][0]["cod_bugetar"] == "20A031800X"


def test_d110_erori():
    prof = {"cui": "14399840", "den": "F", "adresa": "A", "declarant_nume": "N",
            "declarant_prenume": "P", "declarant_functie": "F"}
    # suma_rest <= 0
    c = d110.calcul_d110(6, 2025, {"obligatii": [{"cod_oblig": "604", "suma_dat": 100, "suma_rest": 0}]})
    assert any("suma_rest" in e for e in d110.erori_generare(prof, {"obligatii": [
        {"cod_oblig": "604", "suma_dat": 100, "suma_rest": 0}]}, c))
    # cod_oblig invalid
    c2 = d110.calcul_d110(6, 2025, {"obligatii": [{"cod_oblig": "999", "suma_dat": 100, "suma_rest": 1}]})
    assert any("nomenclator" in e for e in d110.erori_generare(prof, {"obligatii": [
        {"cod_oblig": "999", "suma_dat": 100, "suma_rest": 1}]}, c2))
    # d_temei=1 fara IBAN
    prof_no_iban = dict(prof)
    m = {"d_temei": 1, "obligatii": [{"cod_oblig": "605", "suma_dat": 100, "suma_rest": 500}]}
    c3 = d110.calcul_d110(6, 2025, m)
    assert any("IBAN" in e for e in d110.erori_generare(prof_no_iban, m, c3))


@pytest.mark.skipif(not os.path.exists(_JAR), reason="Validatorul D110 nu e instalat in DUK.")
def test_d110_valid_pe_validatorul_oficial():
    from core import duk
    x0, _ = d110.genereaza(_P(), "s", Perioada(2025, luna=6),
                           {"obligatii": [{"cod_oblig": "604", "suma_dat": 1000, "suma_rest": 1}]})
    assert duk.valideaza(x0, "d110", an=2025, luna=6)["stare"] == "valid"
    x1, _ = d110.genereaza(_P(), "s", Perioada(2025, luna=6),
                           {"d_temei": 1, "obligatii": [{"cod_oblig": "605", "suma_dat": 200, "suma_rest": 500}]})
    rez = duk.valideaza(x1, "d110", an=2025, luna=6)
    assert rez["stare"] == "valid", rez.get("erori")


# 17.5-Q. Amprente pe cod, din tabelele D100/D112 ale documentului D110
# ANAF din 24.03.2026. Notele editoriale sunt excluse.
AMPRENTE_D110 = {
    "602": "6300eb800ccf029023f178e4e9b31e1e0ee1408289c66ce82927e95ce1635614",
    "604": "99d2cfa078846e73db7d3846ec0cd948a24efa7cdfb82cff1995bb6689a74108",
    "605": "50b3a41a90cd7daa5e7a19cdaed0db8e39f632e64c99173b6b8a361aa6df7b82",
    "606": "f13794296609974f689387713ae8eaa51f26b6f2741433435b5f5c4133bb44b7",
    "607": "a8dd908deaabb3dd85b58629c448c1805219167041b9b13a0ef6dac13d3a1090",
    "608": "ea99111949a416752fd865515921366aeef016c93694242521238348e7ad91a9",
    "611": "b9b28a1d2dcc2a97bde4c3d2d55b597ae013a323e5bac821eeec6761792d80bb",
    "619": "5e03657e45a0268673ac27cab16812da226d39ab513e4a6169cbe2b49aff4438",
    "621": "0f9b850773d430287b8e8ccf133bf7e1f79b644505ef6509cbad8fad1f94d546",
    "622": "19508603adc2b8aa307dcc17d35c8ea0dbad2ac76159cd745f2f0af5416b151e",
    "623": "c1a974f6296452b7dc7a3ade8814b53694e075282e89bb3f8bca3492fedcb3ce",
    "625": "729864137edd8f476bf296ee5302603f0479f0a88fad51a70dd0ad4a5e517fd3",
    "626": "71750939c98ca16c2c0415f90aa338fea53e4657a2be95d9a15fea09c7943f14",
    "627": "edcc403ef021af335712ee1b437a8d0dfda9a8356a5c1410fde87d8f36ecadf0",
    "628": "b11eba3f72e238ad68441803e7e144e8115e94ec02bbca9ced4ff35fb26a1d70",
    "629": "c7bb9a4f7b721974b0f64da521d2b232c60cd68a35006a6ad48f81b764fbff62",
    "631": "f6c954165d42e432fa753e3bab631ff261831131f9a518ef16b6694eba05624a",
    "632": "4cf6d916425126a5e9e187185996cb725aba8938f1b9669fc0d967e899ba63f7",
    "633": "118fad60dbb8187e71a8fc97c3ac9e1d90fd741682537c3888a6109a8ea7927b",
    "634": "131ceda854593974223a15103d505c5316a29b5db296bdffd045aaec5ab163e3",
    "635": "87770242f0c4c8af60566cbcf96909b478369505dc68ae9a2d831ad9dcf0163c",
    "636": "887e85726c44756d21e4e901407cbf9556297c13db331c22494f81bab0a06c47",
    "637": "b440490c2fcf69fc860b5ccaf036bc96c01b189a085c4eab1d33d5f114db2535",
    "638": "55b671f66ab23f28ce2503c3bec783589d7a9b9dca1874a2be60b971879bd959",
    "639": "285f3d6c38f5fbbb25abb3b28822ae66c3f07f2a055a0b98d327ece02c2d17da",
    "640": "877a8efb74c9a190f7cf10b84a48f4077847f7bf43f82867744ae67e9ed4bf11",
    "641": "6851ca88dee96cfef724d69b038578353a0287f0874cb3ab6050cf99cf6efd85",
    "642": "00abc0ae762cd9e5fba4b6599be21c128d036b1395044a47e46de2bb61b1d977",
    "690": "51e3135815388c68c274be5bed9957adccd79ab01ac6ed4d2c65489c969d0c5a",
}

def test_q_d110_denumirile_fiecarui_cod():
    import hashlib
    import re
    import unicodedata

    coduri = d110.COD_OBLIG_DENUMIRI
    assert set(coduri) == set(d110._COD_OBLIG_VALIDE) == set(AMPRENTE_D110)
    for cod, denumire in coduri.items():
        if cod == "626":
            assert denumire == "Plăți anticipate ale impozitului pentru unele venituri din activități independente, precum și pentru venituri din alte surse prevăzute la art. 114 alin. (2) lit. k¹)"
            assert hashlib.sha256(denumire.encode("utf-8")).hexdigest() == AMPRENTE_D110[cod]
            continue
        simplu = unicodedata.normalize("NFD", denumire.casefold()).encode("ascii", "ignore").decode()
        cuvinte = " ".join(re.findall("[a-z0-9]+", simplu))
        assert hashlib.sha256(cuvinte.encode()).hexdigest() == AMPRENTE_D110[cod], cod


def test_q_d110_codurile_si_ordinea_api():
    from core.uc_declaratii import _obligatii_d110

    asteptate = [{"cod": c, "denumire": d110.COD_OBLIG_DENUMIRI[c]} for c in AMPRENTE_D110]
    assert _obligatii_d110() == asteptate
