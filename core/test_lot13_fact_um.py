# -*- coding: utf-8 -*-
"""Lotul 13, zona `fact` — regula UM-ului unei linii noi (decizia sesiunii principale, 26.10.2026, pe întrebarea din raportul fact §14,
verbatim: „UM gol NU devine «buc» pe ascuns — se refuză, lângă câmp, cu o propoziție («Alege unitatea de măsură a liniei.»), în toate
cele patru locuri (linia nouă la emitere, linia facturii primite de mână, articolul nou din borderou, serverul — o singură regulă, server
+ ecran). Excepție: o linie cu articol din nomenclator își ia UM-ul articolului (e vizibil pe linie). Datele existente: neafectate.”).

O singură regulă: `facturi.um_linie` / `facturi.um_lipsa` / `facturi.MESAJ_UM_LIPSA`; serverul emiterii o aplică prin
`facturi_api.um_lipsa_emitere` (UM-ul articolului citit din nomenclator), factura de mână prin `uc_factura_primita.factura_din_formular`,
borderoul prin `uc_tenants` (refuzul `op-um`).

Temei: N/A — regulă de produs (CLAUDE.md §8: datele contabilului duse nealterate; DS cap.6 v2.104, 504: nimic precompletat care induce
în eroare). Schemă efemeră din template, în tranzacție anulată (fixturile lui 417 și R193)."""
import pytest

from core import erori, facturi, facturi_api, uc_factura_primita
from core.test_417_storno_trimitere import _db_ok, conn  # noqa: F401 — fixtura
from core.test_r193_model_fara_conexiune import mediu  # noqa: F401 — fixtura (emiterea pe ruta formularului, schemă efemeră)

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def test_um_gol_nu_devine_buc():
    """Regula pură: UM-ul scris rămâne; gol fără articol -> None (de refuzat), nu „buc”; gol pe linia cu articol -> UM-ul articolului.
    MUTAȚIE: `return None` -> `return "buc"` în `um_linie` -> pică."""
    assert facturi.MESAJ_UM_LIPSA == "Alege unitatea de măsură a liniei."
    assert facturi.um_linie({"um": " kg "}) == "kg"
    assert facturi.um_linie({"um": ""}) is None and facturi.um_linie({}) is None and facturi.um_linie({"um": "  "}) is None
    assert facturi.um_linie({"um": "", "articol_id": 7}, "ml") == "ml"          # articolul din nomenclator: UM-ul lui
    assert facturi.um_linie({"um": "", "articol_id": 7}, None) is None           # articolul fără UM nu inventează unul
    assert facturi.um_linie({"um": "ora", "articol_id": 7}, "ml") == "ora"       # ce a scris omul pe linie rămâne


def test_um_lipsa_numeste_campul_fiecarei_linii_si_completeaza_din_articol():
    linii = [{"descriere": "A", "um": ""}, {"descriere": "B", "um": "", "articol_id": 3}, {"descriere": "C", "um": "mp"}]
    assert facturi.um_lipsa(linii, {3: "kg"}) == [("em-l0-um", facturi.MESAJ_UM_LIPSA)]
    assert [l["um"] for l in linii] == ["", "kg", "mp"]
    assert facturi.um_lipsa([{"um": ""}], prefix="pm-l", de_la=1) == [("pm-l1-um", facturi.MESAJ_UM_LIPSA)]


def test_factura_de_mana_cu_um_gol_e_refuzata_langa_camp():
    """Factura primită introdusă de mână: linia fără UM se refuză pe `pm-l1-um`, cu propoziția regulii (aceeași ca la emitere).
    MUTAȚIE: refuzul UM-ului scos din `factura_din_formular` -> pică."""
    corp = {"tert_tara": "RO", "tert_cui": "14399840", "tert_nume": "DANTE INTERNATIONAL SA", "numar": "UM-1", "data_emitere": "2099-03-10",
            "moneda": "RON", "cont": "628", "linii": [{"descriere": "Servicii", "cantitate": 1, "um": "", "pret_unitar": 100, "cota_tva": 21}]}
    with pytest.raises(erori.DateInvalide) as e:
        uc_factura_primita.factura_din_formular(corp)
    campuri = {c["camp"]: c["mesaj"] for c in e.value.detaliu["erori_campuri"]}
    assert campuri.get("pm-l1-um") == facturi.MESAJ_UM_LIPSA, campuri


@DB
def test_emiterea_ia_um_ul_articolului_si_refuza_linia_fara_um(conn):
    """Serverul emiterii: linia cu articol din nomenclator și UM gol primește UM-ul articolului (citit din `articole`); linia fără articol
    și fără UM se refuză pe `em-l1-um`. MUTAȚIE: citirea UM-ului articolului scoasă din `um_lipsa_emitere` -> pică."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Cablu UM E2E', 'ml') RETURNING id")
        aid = cur.fetchone()[0]
    linii = [{"descriere": "Cablu UM E2E", "um": "", "articol_id": aid}, {"descriere": "Montaj", "um": ""}]
    assert facturi_api.um_lipsa_emitere(conn, linii) == [("em-l1-um", facturi.MESAJ_UM_LIPSA)]
    assert linii[0]["um"] == "ml"


def test_ruta_emiterii_refuza_um_gol_langa_camp_si_nu_scrie_nimic(mediu):
    """Ruta formularului `Emite factură` (`uc_tenants.facturi_emite`): UM-ul trimis gol de ecran se refuză pe `em-l0-um`, cu propoziția
    regulii, iar nicio factură nu se scrie (înainte: pleca „buc”). MUTAȚIE: refuzul din `facturi_emite` scos -> factura se emite -> pică."""
    import main
    from core import uc_tenants
    date = main.EmitereIn(linii=[{"descriere": "Mentenanta platforma web", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "um": ""}],
                          tert_nume="Client R193 SRL", tert_cui="14399840", data_emitere="2026-10-10")
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.facturi_emite(1, date, {"uid": 1})
    assert {c["camp"]: c["mesaj"] for c in e.value.detaliu["erori_campuri"]} == {"em-l0-um": facturi.MESAJ_UM_LIPSA}
    with mediu["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM test_r193_model.facturi")
        assert cur.fetchone()[0] == 0
