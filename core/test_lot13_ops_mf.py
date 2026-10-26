# -*- coding: utf-8 -*-
"""[lotul 13, deficiențele 518 / 519 / 522 / 516 / 521, comanda Costin 13.1] Mijloacele fixe: activul schimbat de o notă numai prin
validarea ei, amortizarea înregistrată ținută pe fiecare activ, casarea care refuză lunile lipsă și trece luna casării prin 6811.

Scenariul F2 al lui Costin, refăcut pe o schemă efemeră: MF-001 „Utilaj producție” 12.000 lei, 60 de luni, liniar, PIF 15.01.2025 (rata 200),
soldul preluat 2813 = 2.200 (02–12/2025), notele de amortizare 01–02/2026 validate (400) -> înregistrat 2.600 (522/516: verificarea
reevaluării citea 400). Casare pe 15.10.2026: lipsesc 03–09/2026 (1.400) -> refuz (518: nota debita 2813 cu 4.200 și 1.600 nu treceau
prin 6811). MF-PLUS „Laptop găsit la inventar”, pe același cont, PIF 15.10.2026 — „înregistrat 4.000” la el era amortizarea lui MF-001 (522).

TEMEI: OMFP 1802/2014 pct.238 alin.(2) („Amortizarea imobilizărilor corporale se calculează începând cu luna următoare punerii în funcțiune
și până la recuperarea integrală a valorii lor”), pct.242–243 (scoaterea din evidență la casare, valoarea neamortizată pe cheltuieli);
HG 2139/2004 anexa cap.I pct.4 (durata aleasă în plaja catalogului); Legea 82/1991 art.6 alin.(1) (documentul justificativ).
"""
from decimal import Decimal

import pytest

from core import erori
from core.test_lot13_ops_schema import CTX, linii, nota, schema_ops

D = "2026-10-15"


def _mf001(cur):
    cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor) VALUES ('2131', 12000, 0), ('2813', 0, 2200)")
    cur.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda, activ) "
                "VALUES ('MF-001', 'Utilaj productie', '2131', '2813', 12000, 0, 60, '2025-01-15', 'liniara', true) RETURNING id")
    mid = cur.fetchone()[0]
    for luna in (1, 2):
        nid = nota(cur, "2026-%02d-28" % luna, [("6811", "2813", 200)], descriere="Amortizare %02d/2026" % luna)
        cur.execute("UPDATE inregistrari SET sursa = 'amortizare', numar = %s WHERE id = %s", ("AMORT-2026-%02d" % luna, nid))
    return mid


def _pe_activ(cur, nid, mid):
    """Rândurile notei `nid`, legate de activul `mid` (`mf_linii`)."""
    cur.execute("INSERT INTO mf_linii (linie_id, mijloc_fix_id) SELECT id, %s FROM inregistrari_linii WHERE inregistrare_id = %s", (mid, nid))


def _registru(uc):
    return {m["cod"]: m for m in uc.tenant_mijloace_fixe(1, CTX)["mijloace"]}


def _valideaza(cur, nid):
    cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))


@pytest.fixture
def azi(monkeypatch):
    import datetime
    from core import common, inchidere_luna
    zi = datetime.date(2026, 10, 25)
    monkeypatch.setattr(common, "azi_ro", lambda *a: zi)
    return zi


def test_def_522_516_inregistrat_pe_activ_cu_soldul_preluat(monkeypatch, azi):
    """MUTAȚIE: `mf_note.pe_activ` numără și ciornele (`if data <= pana_la:`) -> înregistrat 2.800 -> pică."""
    from core import migrare_mf_note
    with schema_ops(monkeypatch) as (c, cur, uc):
        mid = _mf001(cur)
        assert migrare_mf_note.backfill(c, "ztest_lot13_ops")["amortizare"] == 2   # notele vechi primesc activul după rată
        cur.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda, activ) "
                    "VALUES ('MF-PLUS', 'Laptop', '2131', '2813', 6000, 0, 36, '2026-10-15', 'liniara', true)")
        # amortizarea lui 03/2026 numai în CIORNĂ, pe activ: nu e „înregistrată” (evidența = notele validate), ci „în ciornă”
        _pe_activ(cur, nota(cur, "2026-03-31", [("6811", "2813", 200)], status="ciorna"), mid)
        r = _registru(uc)
        # 2.200 din soldul preluat (02–12/2025) + 400 (01–02/2026) — pe MF-001; nimic pe MF-PLUS (înainte: 4.000 / −4.000)
        assert (r["MF-001"]["inregistrat"], r["MF-PLUS"]["inregistrat"]) == ("2600.00", "0")
        assert r["MF-001"]["luni_neinregistrate"][:2] == ["04/2026", "05/2026"] and r["MF-001"]["luni_in_ciorna"] == ["03/2026"]
        # 516: reevaluarea citește aceeași cifră (2.600), nu rulajele lui 2813 din 2026 (400)
        from core import mf_registru, repo_mijloace_fixe, repo_contabilitate
        repo_contabilitate.search_path_firma(cur, "ztest_lot13_ops")
        assert mf_registru.inregistrat_pe_activ(cur, "ztest_lot13_ops", repo_mijloace_fixe.toate(cur), mid,
                                                __import__("datetime").date(2026, 9, 30)) == Decimal("2600.00")


def test_def_518_casarea_refuza_lunile_lipsa(monkeypatch, azi):
    from core import migrare_mf_note
    with schema_ops(monkeypatch) as (c, cur, uc):
        mid = _mf001(cur)
        migrare_mf_note.backfill(c, "ztest_lot13_ops")
        with pytest.raises(erori.DateInvalide) as e:
            uc.nota_inventariere(1, {"data": D, "operatie": "casare", "mijloc_fix_id": mid}, CTX)
        m = e.value.detaliu if isinstance(e.value.detaliu, str) else e.value.detaliu["mesaj"]
        # până la 30.09.2026: calculat 4.000 (20 de luni), înregistrat 2.600 -> lipsesc 1.400 (03–09/2026)
        assert "amortizarea calculată e 4.000,00 lei" in m and "înregistrați 2.600,00 lei" in m and "lipsesc 1.400,00 lei" in m, m
        assert "03–09/2026" in m and "6811" in m, m


def test_def_518_519_casarea_cu_luna_ei_iese_din_registru_la_validare(monkeypatch, azi):
    from core import migrare_mf_note
    with schema_ops(monkeypatch) as (c, cur, uc):
        mid = _mf001(cur)
        for luna in range(3, 10):   # lunile 03–09/2026, înregistrate pe activ
            nid = nota(cur, "2026-%02d-28" % luna, [("6811", "2813", 200)])
            _pe_activ(cur, nid, mid)
        migrare_mf_note.backfill(c, "ztest_lot13_ops")
        r = uc.nota_inventariere(1, {"data": D, "operatie": "casare", "mijloc_fix_id": mid}, CTX)
        # luna casării (10/2026, 200) trece prin 6811; 2813 = 2131 cu toată amortizarea (2.200 + 1.800 + 200 = 4.200); restul pe 6583
        assert [x[:3] for x in linii(cur, r["inregistrare_id"])] == [("6811", "2813", "200.00"), ("2813", "2131", "4200.00"),
                                                                    ("6583", "2131", "7800.00")]
        cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
        assert cur.fetchone()[0].startswith("Proces-verbal de casare nr ")
        assert _registru(uc)["MF-001"]["stare"] == "casare_in_asteptare"           # ciorna nu scoate activul
        with pytest.raises(erori.DateInvalide):                                     # a doua casare a aceluiași activ
            uc.nota_inventariere(1, {"data": D, "operatie": "casare", "mijloc_fix_id": mid}, CTX)
        _valideaza(cur, r["inregistrare_id"])
        assert _registru(uc)["MF-001"]["stare"] == "casat"                         # la validare iese


def test_def_519_stergerea_ciornei_de_casare_lasa_activul_activ(monkeypatch, azi):
    with schema_ops(monkeypatch) as (c, cur, uc):
        mid = _mf001(cur)
        cur.execute("INSERT INTO mf_linii (linie_id, mijloc_fix_id) SELECT id, %s FROM inregistrari_linii", (mid,))
        for luna in range(3, 10):
            nid = nota(cur, "2026-%02d-28" % luna, [("6811", "2813", 200)])
            _pe_activ(cur, nid, mid)
        r = uc.nota_inventariere(1, {"data": D, "operatie": "casare", "mijloc_fix_id": mid}, CTX)
        cur.execute("DELETE FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
        assert _registru(uc)["MF-001"]["stare"] == "activ"


def test_def_519_521_plusul_de_mijloc_fix_intra_la_validare_si_dispare_la_stergere(monkeypatch, azi):
    with schema_ops(monkeypatch) as (c, cur, uc):
        corp = {"data": D, "operatie": "plus_mf", "valoare": 6000, "denumire": "Laptop găsit la inventar", "cont_imobilizare": "2131",
                "cod_catalog": "2.2.9", "dnf_luni": 36, "data_pif": D, "metoda": "liniara", "destinatie_cd": "false"}
        with pytest.raises(erori.DateInvalide) as e:   # 521: durata în afara plajei catalogului (2.2.9: 3–5 ani)
            uc.nota_inventariere(1, dict(corp, dnf_luni=12), CTX)
        assert e.value.detaliu["erori_campuri"][0]["camp"] == "op-dnf_luni"
        r = uc.nota_inventariere(1, corp, CTX)
        assert r["numar_inventar"] == "MF-001"                                      # 521: număr de inventar, nu „MF-PLUS”
        reg = _registru(uc)["MF-001"]
        assert (reg["stare"], reg["cont_amortizare"], reg["activ"]) == ("intrare_in_asteptare", "2813", False)   # 519, 504
        assert linii(cur, r["inregistrare_id"])[0][:3] == ("2131", "4754", "6000.00")
        cur.execute("DELETE FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
        assert "MF-001" not in _registru(uc)                                         # 519: ciorna ștearsă, activul dispare
        r = uc.nota_inventariere(1, corp, CTX)
        _valideaza(cur, r["inregistrare_id"])
        assert _registru(uc)["MF-001"]["stare"] == "activ"


def test_def_519_migrarea_reface_F2(monkeypatch, azi):
    """Datele existente: MF-001 „casat” fără nicio notă de casare (ciorna ștearsă) redevine activ; MF-PLUS fără nota lui dispare."""
    from core import migrare_mf_note
    with schema_ops(monkeypatch) as (c, cur, uc):
        mid = _mf001(cur)
        cur.execute("UPDATE mijloace_fixe SET activ = false WHERE id = %s", (mid,))
        cur.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda, activ) "
                    "VALUES ('MF-PLUS', 'Laptop', '2131', '2813', 6000, 0, 36, '2026-10-15', 'liniara', true)")
        n = migrare_mf_note.backfill(c, "ztest_lot13_ops")
        assert (n["reactivate"], n["scoase"]) == (1, 1)
        assert {k: v["stare"] for k, v in _registru(uc).items()} == {"MF-001": "activ"}
        assert not any(migrare_mf_note.backfill(c, "ztest_lot13_ops").values())    # idempotentă


def test_nou_ops_1_reevaluarea_validata_din_coada_urca_registrul(monkeypatch, azi):
    """[NOU-ops-1, găsită la 511] Reevaluarea validată din coada „De validat” (`coada_api.aproba` -> `valideaza_documentul`) lăsa nota validată
    cu registrul neurcat: numai `jurnal_valideaza` chema `_aplica_reevaluarea`. Acum drumul comun al validării o aplică (peticul
    `l13_petice/ops_coada.json`). OMFP 1802/2014 pct.111 alin.(1): „Dacă rezultatul reevaluării este o creștere față de valoarea contabilă
    netă, atunci aceasta se tratează ca o creștere a rezervei din reevaluare” — valoarea reevaluată e noua valoare a activului.
    MUTAȚIE: bucla `_aplica_reevaluarea` scoasă din peticul cozii -> valoarea rămâne 6.000 -> pică."""
    from core import coada_api
    with schema_ops(monkeypatch) as (c, cur, uc):
        cur.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda, activ) "
                    "VALUES ('MF-R', 'Hala', '212', '2812', 6000, 0, 120, '2026-10-01', 'liniara', true) RETURNING id")
        mid = cur.fetchone()[0]
        r = uc.reevaluare_imobilizare(1, {"data": D, "operatie": "reevaluare", "mijloc_fix_id": mid, "valoare_justa": "7500"}, CTX)
        nid = r["inregistrare_id"]
        cur.execute("SELECT valoare FROM mijloace_fixe WHERE id = %s", (mid,))
        assert cur.fetchone()[0] == Decimal("6000.00")            # ciorna nu schimbă registrul
        v = coada_api.valideaza_documentul(c, "ztest_lot13_ops", nid)
        assert v and v.get("ok"), v
        cur.execute("SELECT valoare FROM mijloace_fixe WHERE id = %s", (mid,))
        assert cur.fetchone()[0] == Decimal("7500.00")            # validată pe drumul cozii -> registrul urcat
        assert uc._aplica_reevaluarea(c, "ztest_lot13_ops", nid) is False   # a doua aplicare: nimic (idempotent prin date)
