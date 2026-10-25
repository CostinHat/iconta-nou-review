# -*- coding: utf-8 -*-
"""Lotul 5 (Costin 15.10.2026): 258 — „mesajul pentru asistent spune «Nota #24», iar pe card nota e «Nr. crt. 5»; numărul intern nu
se afișează nicăieri.” Nota se numește cum o vede contabilul în Registrul jurnal („nota nr. crt. 5 din 12.03.2026”, `eticheta_nota`
din bază, `core/eticheta_nota.py`). Pe aplicația de probă, pe baza de TEST, pe o firmă sintetică alocată asistentului."""
import datetime
import os
import re
import sys

import pytest

from conftest import _scoate_firmele_e2e, nr_crt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_b import _deschide_rand   # noqa: E402
from e2e_bloc_d import ASISTENT, PATRON, _api, _firma_noua, _jurnal   # noqa: E402
from e2e_ciorne_proprii import _nota, _nume   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core import drepturi as _dr   # noqa: E402


@pytest.fixture(scope="module")
def firma_258():
    f = _firma_noua("D258")          # alocată asistentului (`_atribuie_asistentului`)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_258_motivul_numeste_nota_prin_nr_crt_de_pe_card_nu_prin_id(asistent, firma_258):
    """258. Registru jurnal, ca Ana Asistent, pe ciorna contabilului-șef: motivul numește nota cum o arată cardul ei, iar id-ul intern nu
    apare nicăieri pe rând. [302, 17.10.2026] Ciorna n-are încă număr curent (îl primește la validare): cardul începe cu data, iar
    motivul spune „Nota din ZZ.LL.AAAA e ciorna lui …” — fără „Nr. crt.” și fără id. Ca id-ul să nu poată trece drept număr, o primă
    notă a contabilului-șef se scrie și se șterge (id-ul ei rămâne consumat). Cererea directă de editare primește același text de la
    server (triggerul din bază), cu aceeași etichetă."""
    tid = firma_258["tenant_id"]
    aruncata = _nota(PATRON, tid, "Nota scoasă D258")
    st, r = _api(PATRON, "DELETE", "/tenants/%d/jurnal/%d" % (tid, aruncata))
    assert st == 200, (st, r)
    nid = _nota(PATRON, tid, "Ciorna contabilului-șef D258")
    eticheta = nr_crt(firma_258["schema"], nid)      # citit independent de aplicație; ciorna: „din ZZ.LL.AAAA”
    _jurnal(asistent, firma_258)
    # [lotul 12, 617] tabelul de note: rândul notei are numărul curent în prima celulă („—” la ciorna fără număr) și data în a doua; motivul
    # stă în detaliul notei, deschis cum îl deschide omul (clic pe rând). `tot` = tot ce arată nota, rândul și detaliul deschis.
    _deschide_rand(asistent, ".fereastra:last-of-type tbody.tn-nota[data-nota-id='%d']" % nid)
    rand = asistent.pg.evaluate("""(i) => { const r = document.querySelector(`.fereastra:last-of-type tbody.tn-nota[data-nota-id='${i}']`);
        const m = r && r.querySelector('.jn-a-altuia'), t = r && r.querySelector('tr.tn-rand');
        return r ? {nr: t ? t.cells[0].innerText.trim() : null, data: t ? t.cells[1].innerText.trim() : null, card: t ? t.innerText : null,
                    motiv: m ? m.innerText.trim() : null, tot: r.innerText} : null; }""", nid)
    asistent.captura()
    azi = datetime.date.today().strftime("%d.%m.%Y")
    nume = _nume(PATRON)
    assert eticheta == "din %s" % azi, eticheta
    # cardul începe cu data (ciorna n-are număr curent: „—” în coloana Nr. crt.), fără „Nr. crt.” și fără id
    assert (rand["nr"], rand["data"]) == ("—", azi) and "Nr. crt." not in rand["card"], rand
    assert rand["motiv"] == _dr.MESAJ_CIORNA_ALTUI % (eticheta, nume, nume), rand
    assert re.findall(r"^Nota din (\d\d\.\d\d\.\d{4}) ", rand["motiv"]) == [azi], rand
    assert re.findall(r"#\d+", rand["tot"]) == [], rand            # numărul intern nu se afișează nicăieri pe rând
    st, r = _api(ASISTENT, "PUT", "/tenants/%d/jurnal/%d" % (tid, nid), {"descriere": "schimbată de Ana"})
    assert (st, (r or {}).get("detail")) == (403, rand["motiv"]), (st, r)
