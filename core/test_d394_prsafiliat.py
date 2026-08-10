"""GARD: prsAfiliat (poz.6.a) trebuie sa fie SURSAT din profil, nu hardcodat "0".

SPEC OFICIAL anaf_surse/d394_struct_anaf.txt poz.6.a:
  prsAfiliat "Au fost efectuate operatiuni cu persoane afiliate in perioada de
  raportare", N(1), OBLIGATORIU: =0 NU, =1 Da.

Pe HEAD 6cd0054 valoarea era hardcodata prsAfiliat="0" in build_xml -> ramanea 0
chiar si cand profilul ar declara operatiuni cu persoane afiliate. iConta NU are inca
un model de persoana afiliata (nicio coloana in firma_profil/clienti/furnizori), deci
fixul onest = a citi un flag EXPLICIT de pe profil (are_operatiuni_afiliate); pana la
adaugarea coloanei, implicit "0" = DECLARAT fara operatiuni afiliate. Testul cazului
flag=True PICA pe HEAD (mereu "0") si TRECE dupa fix.
"""
import re
from core.common import Perioada
from core import d394

_PROF = {"cui": "RO12345678", "caen": "4690", "nume": "TEST SRL",
         "adresa": "str X", "telefon": "0700", "tip_decont": "L"}
_PER = Perioada(2026, luna=8)


def _xml(prof):
    res = d394.calcul_d394(prof, _PER, {"facturi": [], "serii": {}}, {})
    return d394.build_xml(res)


def _prs(xml):
    return re.search(r'prsAfiliat="(\d)"', xml).group(1)


def test_prsafiliat_implicit_zero_cand_lipseste_flag():
    assert _prs(_xml(dict(_PROF))) == "0"


def test_prsafiliat_unu_cand_profil_declara_afiliate():
    prof = dict(_PROF); prof["are_operatiuni_afiliate"] = True
    assert _prs(_xml(prof)) == "1", "prsAfiliat hardcodat 0 - nu urmeaza flagul din profil"


def test_prsafiliat_zero_cand_flag_fals():
    prof = dict(_PROF); prof["are_operatiuni_afiliate"] = False
    assert _prs(_xml(prof)) == "0"


if __name__ == "__main__":
    test_prsafiliat_implicit_zero_cand_lipseste_flag()
    test_prsafiliat_unu_cand_profil_declara_afiliate()
    test_prsafiliat_zero_cand_flag_fals()
    print("OK")
