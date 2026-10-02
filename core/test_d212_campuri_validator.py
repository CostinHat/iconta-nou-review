# -*- coding: utf-8 -*-
"""GARD — atributele pe care `d212.py` le poate emite sunt NUMELE XML ale validatorului instalat (02.10.2026).

Clasa: `d212._CAMPURI` (setul de atribute permise pe capitol) fusese scris din numele CÂMPURILOR INTERNE ale claselor din
D212Validator.jar (`_cass_ret_plat_alin6_ai`), nu din numele atributelor XML pe care validatorul le citește
(`cass_retinut_platitor_alin6_ai`). Pe 7 atribute `oblig_realizat` și pe `reg` (cap11) numele erau greșite; s-a văzut abia
când Etapa 4 a emis prima oară `oblig_realizat`: DUK „atribut necunoscut ('real_cas_deduc_ai')”. Un capitol neexercitat de
teste ar fi purtat greșeala până la primul contribuabil.

Gardul citește jar-ul instalat (ultima versiune `vN` a pachetului `d212validator`) și cere ca fiecare set din `_CAMPURI` să
fie inclus în numele de atribute XML ale clasei capitolului. Fără jar (altă mașină) -> skip.
LIMITĂ: numele XML se recunosc ca șiruri `[a-z][a-zA-Z0-9_]+` din constant pool, minus numele de metode cunoscute; un nume
de metodă nou al validatorului ar putea trece drept atribut (direcția sigură: setul nostru tot trebuie să fie inclus).
"""
import os
import re
import zipfile

import pytest

from core import d212

_JAR = os.path.expanduser("~/duk/dist/lib/D212Validator.jar")
_CLASE = {"cap11": "Cap11", "cap12": "Cap12", "cap14": "Cap14", "oblig_realizat": "Oblig_realizat",
          "oblig_estimat": "Oblig_estimat", "coasigurat": "Coasigurat"}


def _nume_xml(z, cale):
    brut = z.read(cale)
    # delimitat: un nume intern `_cass_ret_plat_alin6_ai` NU are voie să producă subșirul `cass_ret_plat_alin6_ai`
    return set(re.findall(rb"(?<![A-Za-z0-9_])[a-z][a-zA-Z0-9_]{2,}(?![A-Za-z0-9_])", brut))


def _ultima_versiune(z):
    vs = {int(m.group(1)) for n in z.namelist() if (m := re.match(r"d212validator/v(\d+)/", n))}
    return max(vs)


@pytest.mark.skipif(not os.path.exists(_JAR), reason="D212Validator.jar indisponibil")
@pytest.mark.parametrize("capitol", sorted(_CLASE))
def test_atributele_emise_sunt_nume_xml_ale_validatorului(capitol):
    with zipfile.ZipFile(_JAR) as z:
        v = _ultima_versiune(z)
        nume = {x.decode() for x in _nume_xml(z, "d212validator/v%d/%s.class" % (v, _CLASE[capitol]))}
    straine = sorted(d212._CAMPURI[capitol] - nume)
    assert straine == [], "atribute pe care validatorul v%d nu le cunoaște în <%s>: %s" % (v, capitol, straine)


@pytest.mark.skipif(not os.path.exists(_JAR), reason="D212Validator.jar indisponibil")
def test_CALIBRARE_numele_interne_nu_trec_drept_atribute():
    # `_cass_ret_plat_alin6_ai` e câmp intern (începe cu `_`): extragerea delimitată nu-l confundă cu un atribut XML
    with zipfile.ZipFile(_JAR) as z:
        nume = {x.decode() for x in _nume_xml(z, "d212validator/v%d/Oblig_realizat.class" % _ultima_versiune(z))}
    assert {"cass_retinut_platitor_alin6_ai", "real_cas_deductibila_ai"} <= nume
    assert not {"cass_ret_plat_alin6_ai", "real_cas_deduc_ai"} & nume
