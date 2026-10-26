# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1, zona `fact` — C171 (găsită de Code la 628, lotul 12): „Migrarea `migrare_um_borderou` (C115) nu acoperă liniile
borderourilor de stornare („STORNO: grau” copiat cu „buc”).”

Datele: borderoul BA-2 de dinainte de C115 (linia „Grau” pe „buc”, articolul în kg) și stornarea lui (linia „STORNO: Grau” pe „buc”, intrarea
stornată din stoc legată de stornare). Migrarea pune „kg” pe amândouă; o linie de stornare cu altă unitate (pusă de om) nu se rescrie.
Temei: N/A — documentul se citește (cantitatea, prețul, nota, fișa și declarațiile nu se ating). Schemă efemeră, ROLLBACK (fixtura lui 417)."""
import pytest

from core.test_417_storno_trimitere import _SCHEMA, _db_ok, conn  # noqa: F401 — fixtura (schemă efemeră, ROLLBACK)
from core.test_lot12_c115_um_borderou import _borderou

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@DB
def test_def_c171_migrarea_pune_unitatea_si_pe_borderoul_de_stornare(conn):
    """MUTAȚIE: potrivirea fără „STORNO: ” -> linia stornării rămâne pe „buc” -> pică."""
    from core import migrare_um_borderou as mig
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES ('Grau', 'kg', '371', '607') RETURNING id")
        aid = cur.fetchone()[0]
        orig = _borderou(cur, "BA-2", "borderou", "buc", aid)
        storno = _borderou(cur, "BA-5", "borderou", "buc", aid, denumire="STORNO: Grau")
        orig2 = _borderou(cur, "BA-3", "borderou", "t", aid)
        pus_de_om = _borderou(cur, "BA-6", "borderou", "t", aid, denumire="STORNO: Grau")
        cur.execute("UPDATE facturi SET storno_din_id = %s WHERE id = %s", (orig, storno))
        cur.execute("UPDATE facturi SET storno_din_id = %s WHERE id = %s", (orig2, pus_de_om))
    r = mig.aplica(conn, _SCHEMA)
    assert r == {"linii": 2, "borderouri": ["BA-2", "BA-5"]}, r
    with conn.cursor() as cur:
        cur.execute("SELECT factura_id, um FROM factura_linii WHERE factura_id = ANY(%s)", ([orig, storno, orig2, pus_de_om],))
        assert dict(cur.fetchall()) == {orig: "kg", storno: "kg", orig2: "t", pus_de_om: "t"}
    assert mig.aplica(conn, _SCHEMA)["linii"] == 0   # idempotentă
