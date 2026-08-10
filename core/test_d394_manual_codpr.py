"""GARD neconformitate: operatiune MANUALA C/V (art.331) trebuie sa emita op11(codPR).

SPEC OFICIAL anaf_surse/d394_struct_anaf.txt poz.233:
  <op11> "Pt ((tip in (V,C) si tip_partener=1) sau (tip=N si (lung(cuiP)=13 sau
  cuiP=null))) sectiunea este OBLIGATORIE". DUKIntegrator R233.5.

Pe HEAD 6cd0054 calea manuala (calcul_d394, bucla `ops`) NU pasa categorie_331 la
_adauga pentru tipurile non-N -> `categorii` ramanea gol -> op11 nu se construia ->
op1 se emitea FARA op11 pentru C/V manual la tip_partener=1 -> declaratie invalida.
Acest test PICA pe HEAD (op11 gol) si TRECE dupa fix.
"""
from core.common import Perioada
from core import d394

_PROF = {"cui": "RO12345678", "caen": "4690", "nume": "TEST SRL",
         "adresa": "str X", "telefon": "0700", "tip_decont": "L"}
_PER = Perioada(2026, luna=8)


def _calc(manual):
    return d394.calcul_d394(_PROF, _PER, {"facturi": [], "serii": {}}, manual)


def test_manual_C_art331_emite_op11_codPR():
    # achizitie art.331 (C) de la partener TVA RO, categoria "deseuri" (codPR 22)
    manual = {"operatiuni": [{"tip": "C", "tip_partener": 1, "cota": 19,
                              "cuiP": "RO999", "denP": "FURN SRL", "nrFact": 1,
                              "baza": 1000, "tva": 190, "categorie_331": "deseuri"}]}
    res = _calc(manual)
    k = ("C", 1, 19, "RO999", "FURN SRL")
    assert k in res.op11, "op11 lipseste pentru C manual art.331 (R233.5)"
    assert res.op11[k]["codPR"] == "22"
    assert res.op11[k]["tvaPR"] == 190          # C: tvaPR completat
    xml = d394.build_xml(res)
    assert "<op11" in xml, "XML fara <op11> pentru C manual -> DUK-invalid"


def test_manual_V_cereale_subcod_emite_op11_codPR():
    # livrare taxare inversa (V), cereale cu subcodul NC direct (1005 porumb)
    manual = {"operatiuni": [{"tip": "V", "tip_partener": 1, "cota": 19,
                              "cuiP": "RO888", "denP": "CLIENT SRL", "nrFact": 1,
                              "baza": 2000, "tva": 380, "categorie_331": "1005"}]}
    res = _calc(manual)
    k = ("V", 1, 0, "RO888", "CLIENT SRL")     # V -> cota fortata la 0 (R217.2)
    assert k in res.op11, "op11 lipseste pentru V manual art.331 (R233.5)"
    assert res.op11[k]["codPR"] == "1005"       # subcod NC, nu centralizatorul 21
    assert res.op11[k]["bun"] == "21"           # detaliu.bun = categoria cereale
    assert res.op11[k]["tvaPR"] is None         # R237: tvaPR=null pt tip_partener=1 si V
    xml = d394.build_xml(res)
    assert "<op11" in xml


if __name__ == "__main__":
    test_manual_C_art331_emite_op11_codPR()
    test_manual_V_cereale_subcod_emite_op11_codPR()
    print("OK")
