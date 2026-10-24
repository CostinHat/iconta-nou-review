# -*- coding: utf-8 -*-
"""[lotul 12, C115] Datele existente: borderoul de achiziție pe cont de stoc scris înainte de reparație, cu un articol ales din
nomenclator (în kg), are linia pe „buc”; `core/migrare_um_borderou.py` îi pune unitatea articolului. Nu atinge borderoul pe
cheltuială, linia cu altă unitate pusă de om, nici o factură obișnuită. MUTAȚIE: `aplica` fără `SET um = a.um` -> pică."""
import pytest

from core.test_417_storno_trimitere import _SCHEMA, _db_ok, conn  # noqa: F401 — fixtura (schemă efemeră, ROLLBACK)

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _borderou(cur, numar, tip, um_linie, articol_id=None, denumire="Grau"):
    cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_nume, tert_cui, status, tip) VALUES "
                "(%s, '2099-05-01', 'primita', 100, 0, 'Ion Vanzator', '', 'importata', %s) RETURNING id", (numar, tip))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, um) VALUES (%s, %s, 50, 2, 0, %s)",
                (fid, denumire, um_linie))
    if articol_id:
        cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, factura_id) VALUES "
                    "(%s, '2099-05-01', 'intrare', 50, 2, 100, %s, %s)", (articol_id, numar, fid))
    return fid


@DB
def test_def_c115_migrarea_pune_unitatea_articolului_pe_borderourile_vechi(conn):
    from core import migrare_um_borderou as mig
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES ('Grau', 'kg', '371', '607') RETURNING id")
        aid = cur.fetchone()[0]
        vechi = _borderou(cur, "BA-2", "borderou", "buc", aid)            # înainte de reparație: articol în kg, linia pe „buc”
        pus_de_om = _borderou(cur, "BA-3", "borderou", "t", aid)          # unitate scrisă de om: rămâne
        cheltuiala = _borderou(cur, "BA-4", "borderou", "buc", None, "Achizitie de la neinregistrat - Ion")   # fără intrare în stoc
        factura = _borderou(cur, "F-9", "factura", "buc", aid)            # o factură obișnuită nu e a migrării
    r = mig.aplica(conn, _SCHEMA)
    assert r == {"linii": 1, "borderouri": ["BA-2"]}, r
    with conn.cursor() as cur:
        cur.execute("SELECT factura_id, um FROM factura_linii WHERE factura_id = ANY(%s) ORDER BY factura_id",
                    ([vechi, pus_de_om, cheltuiala, factura],))
        assert dict(cur.fetchall()) == {vechi: "kg", pus_de_om: "t", cheltuiala: "buc", factura: "buc"}
    assert mig.aplica(conn, _SCHEMA)["linii"] == 0   # idempotentă
