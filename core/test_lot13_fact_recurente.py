# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1, zona `fact` — 680: „Facturi recurente, Șablon nou [...] lipsesc seria, scadența, perioada de valabilitate și, mai
ales, dacă factura se emite singură sau ca ciornă și dacă pleacă singură în SPV. Șablonul folosește aceleași controale ca Emite factură.”
Briefing: „întrebate explicit, nimic implicit”.

Temei: N/A — regulă de produs (CLAUDE.md §9: „Nimic precompletat sau afișat care poate induce în eroare contabilul”); scadența facturii:
Legea 72/2013 nu fixează termenul pe șablon (îl alege contabilul). Fixtura cronului: `test_lot12_fe3_recurente.mediu` (schemă efemeră,
tranzacție anulată, perioade 2099)."""
import datetime

from core import facturi_recurente as fr
from core.erori import ErorileFormularului
from core.test_lot12_fe3_recurente import AZI, LINIE, SCH, _adauga, _notificari, _sql, mediu  # noqa: F401 — `mediu` e fixture


def _campuri(corp):
    er = ErorileFormularului("x")
    fr.cere_emiterea(corp, er)
    return [c["camp"] for c in er.detaliu()["erori_campuri"]]


def test_def_680_intrebarile_emiterii_se_cer_toate_deodata():
    """Fără scadență, început, „până când”, mod -> patru erori, fiecare lângă câmpul ei; emiterea automată fără răspunsul SPV -> și „SPV”;
    ciorna nu întreabă SPV-ul (o trimite contabilul după emitere). MUTAȚIE: modul emiterii nefiind cerut -> pică."""
    assert _campuri({}) == ["fr-scadenta", "fr-inceput", "fr-pana", "fr-mod"]
    assert _campuri({"scadenta_zile": 15, "data_inceput": "2026-11-01", "valabil_pana": "oprire", "mod_emitere": "automata"}) == ["fr-spv"]
    assert _campuri({"scadenta_zile": 0, "data_inceput": "2026-11-01", "valabil_pana": "data", "mod_emitere": "ciorna"}) == ["fr-sfarsit"]
    assert _campuri({"scadenta_zile": 0, "data_inceput": "2026-11-01", "valabil_pana": "data", "data_sfarsit": "2026-10-01",
                     "mod_emitere": "ciorna"}) == ["fr-sfarsit"]


def test_def_680_valabilitatea_si_scadenta_sunt_pure():
    d = datetime.date(2099, 3, 10)
    assert fr.in_valabilitate({"data_inceput": "2099-03-01", "data_sfarsit": None}, d)
    assert not fr.in_valabilitate({"data_inceput": "2099-04-01"}, d)
    assert not fr.in_valabilitate({"data_inceput": "2099-01-01", "data_sfarsit": "2099-02-28"}, d)
    assert fr.in_valabilitate({}, d)                                         # șablonul de dinainte de 680: oricând
    assert fr.scadenta({"scadenta_zile": 15}, d) == "2099-03-25" and fr.scadenta({}, d) is None


def test_def_680_cronul_emite_cu_scadenta_iar_ciorna_numai_o_anunta(mediu):
    """Două șabloane scadente pe 10.03.2099: cel „automat”, cu termenul de 15 zile -> factura emisă, scadentă pe 25.03.2099; cel „ciornă” ->
    nicio factură, un anunț în clopoțel („pregătită ca ciornă”), o singură dată în lună. MUTAȚIE: `de_emis` fără filtrul modului -> ciorna se
    emite -> pică."""
    a = _adauga(mediu, scadenta_zile=15)["id"]
    c = _adauga(mediu, tert_nume="Client Ciorna SRL", mod_emitere="ciorna")["id"]
    e = fr.emite_scadente(SCH, AZI)
    assert [x["sablon"] for x in e if x.get("factura")] == [a], e
    assert _sql(mediu, "SELECT data_scadenta::text FROM facturi") == [("2099-03-25",)]
    asteptat = fr.text_ciorna("Firma FE3 SRL", {"tert_nume": "Client Ciorna SRL"}, AZI)
    assert [t for _tip, t, _d in _notificari(mediu)].count(asteptat) == 1, _notificari(mediu)
    fr.emite_scadente(SCH, AZI + datetime.timedelta(days=1))
    assert [t for _tip, t, _d in _notificari(mediu)].count(asteptat) == 1   # o dată pe lună
    assert _sql(mediu, "SELECT ultima_pregatire::text FROM facturi_recurente WHERE id = %s", (c,)) == [("2099-03-10",)]


def test_def_680_emite_factura_lunii_pe_ciorna(mediu):
    """„Emite factura lunii” pe ciorna pregătită -> factura emisă pe drumul cronului; a doua apăsare în aceeași lună -> refuzul numit."""
    c = _adauga(mediu, mod_emitere="ciorna", scadenta_zile=30)["id"]
    r = fr.emite_unul(SCH, c, AZI)
    assert r.get("factura"), r
    assert _sql(mediu, "SELECT data_scadenta::text FROM facturi") == [("2099-04-09",)]
    assert fr.emite_unul(SCH, c, AZI) == {"eroare": fr.MESAJ_NU_E_DE_EMIS}
