# -*- coding: utf-8 -*-
"""Lotul 13, zona `fact` — regula UM pe șablonul facturii recurente (decizia sesiunii principale, 26.10.2026, verbatim: „Șablonul recurent —
DA: linia șablonului poartă UM, cu aceeași regulă (`um_linie`: scris de om / al articolului / refuz lângă câmp la salvarea șablonului);
șabloanele vechi fără UM: la emiterea lunii, linia fără UM și fără articol nu se emite pe ascuns cu «buc» — șablonul se oprește cu refuzul
în clopoțel (mecanismul C109 existent), ca să fie completat o dată. Datele existente: migrare care pune UM-ul articolului unde linia are
articol; restul rămân de completat (le numește refuzul).”).

Regula unică: `facturi.um_linie` / `MESAJ_UM_LIPSA`, aplicată în `facturi_recurente.verificari_drum` (salvarea și cronul); textul refuzului
cronului: `facturi_recurente.motiv_drum`; datele existente: `core/migrare_sablon_um_articol.py`.

Temei: N/A — regulă de produs (CLAUDE.md §8; DS cap.6 v2.104, 504). Fixtura C109 (`core/test_lot12_fe3_recurente.py`): schemă efemeră din
template, tranzacție anulată, cronul pe aceeași conexiune, emailul notificărilor prins."""
from core import facturi, facturi_recurente as fr
from core import migrare_sablon_um_articol as mg
from core.test_lot12_fe3_recurente import AZI, LINIE, SCH, _adauga, _db_ok, _pe_campuri, _sql, _stare, mediu  # noqa: F401 — fixtura

import pytest

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
MOTIV_UM = "Linia 1 — " + facturi.MESAJ_UM_LIPSA


def test_linia_sablonului_fara_um_e_refuzata_pe_campul_ei():
    """`verificari_drum` (salvarea și cronul): linia fără UM -> `fr-l0-um`, cu propoziția regulii; cu UM -> nimic.
    MUTAȚIE: verificarea UM-ului scoasă din `verificari_drum` -> pică."""
    s = {"tert_nume": "Client", "tert_cui": "14399840", "linii": [dict(LINIE, um="")]}
    assert ("fr-l0-um", facturi.MESAJ_UM_LIPSA) in fr.verificari_drum(s)
    assert [c for c, _m in fr.verificari_drum(dict(s, linii=[dict(LINIE, um="luna")]))] == []
    assert fr.motiv_drum([("fr-l0-um", facturi.MESAJ_UM_LIPSA)]) == MOTIV_UM
    assert fr.motiv_drum([("fr-nume", "X.")]) == "X."


def test_migrarea_pune_um_ul_articolului_numai_pe_liniile_cu_articol_fara_um():
    linii = [{"descriere": "A", "articol_id": 3}, {"descriere": "B", "articol_id": 3, "um": "t"}, {"descriere": "C"}]
    noi, n = mg.linii_cu_um(linii, {3: "kg"})
    assert n == 1 and [l.get("um") for l in noi] == ["kg", "t", None]


@DB
def test_salvarea_sablonului_fara_um_e_refuzata_langa_camp(mediu):
    r = _adauga(mediu, linii=[dict(LINIE, um="")])
    assert ("fr-l0-um", facturi.MESAJ_UM_LIPSA) in _pe_campuri(r), r
    assert _sql(mediu, "SELECT count(*) FROM facturi_recurente")[0][0] == 0


@DB
def test_sablonul_vechi_fara_um_se_opreste_cu_refuzul_in_clopotel_nu_cu_buc(mediu):
    """Datele existente: șablonul salvat înainte de regulă, cu linia fără UM și fără articol. Cronul NU emite factura cu „buc”: refuzul
    („Linia 1 — Alege unitatea de măsură a liniei.”) e pe șablon și în clopoțel (C109), nicio factură. Cu UM-ul completat, factura lunii
    iese în unitatea scrisă. MUTAȚIE: verificarea UM-ului scoasă din `verificari_drum` -> factura iese cu „buc” -> pică."""
    r = _adauga(mediu, linii=[dict(LINIE, um="luna")])
    sid = r["id"]
    _sql(mediu, "UPDATE facturi_recurente SET linii = %s WHERE id = %s", ('[{"descriere": "Abonament mentenanta lunara", "cantitate": 1, '
                                                                       '"pret_unitar": 100, "cota_tva": 21, "cont_venit": "704"}]', sid))
    e = fr.emite_scadente(SCH, AZI)
    assert [(x["sablon"], x.get("eroare")) for x in e if x.get("sablon")] == [(sid, MOTIV_UM)], e
    ultima, motiv, _la = _stare(mediu, sid)
    assert (ultima, motiv) == (None, MOTIV_UM)
    assert _sql(mediu, "SELECT count(*) FROM facturi")[0][0] == 0
    assert any(t == fr.TIP_REFUZ and MOTIV_UM in txt for t, txt, _d in _sql(mediu, "SELECT tip, text, de_livrat FROM public.notificari "
                                                                              "WHERE user_id = %s", (mediu["uid"],)))
    _sql(mediu, "UPDATE facturi_recurente SET linii = %s WHERE id = %s", ('[{"descriere": "Abonament mentenanta lunara", "cantitate": 1, '
                                                                       '"um": "luna", "pret_unitar": 100, "cota_tva": 21, "cont_venit": "704"}]', sid))
    e = fr.emite_scadente(SCH, AZI)
    assert [x.get("eroare") for x in e if x.get("sablon")] == [None], e
    assert _sql(mediu, "SELECT um FROM factura_linii")[0][0] == "luna"


@DB
def test_migrarea_pe_schema_si_idempotenta(mediu):
    """Linia cu articol și fără UM primește UM-ul articolului; a doua rulare nu mai atinge nimic (verifica = True)."""
    aid = _sql(mediu, "INSERT INTO articole (denumire, um) VALUES ('Cablu UM sablon', 'ml') RETURNING id")[0][0]
    _sql(mediu, "INSERT INTO facturi_recurente (tert_nume, linii, zi_emitere, moneda) VALUES ('Client', %s, 5, 'RON')",
         ('[{"descriere": "Cablu UM sablon", "articol_id": %d, "cantitate": 1, "pret_unitar": 10}, {"descriere": "Montaj"}]' % aid,))
    assert mg.aplica(mediu["c"], SCH)["linii"] == 1
    linii = _sql(mediu, "SELECT linii FROM facturi_recurente")[0][0]
    assert [l.get("um") for l in linii] == ["ml", None]
    assert mg.aplica(mediu["c"], SCH)["linii"] == 0
