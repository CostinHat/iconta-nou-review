# -*- coding: utf-8 -*-
"""[lotul 12, C135] Reparația 443 (numărul facturii cu seria separat) acoperă și notele de CASĂ ale facturii.

Găsit pe copia F2 (nota 79, validată): „Încasare de la client — chitanța F2C-1 — factura F2T2 din 22.10.2026 — …”. `note_cu_serie_lipita`
citea numai contarea facturii, nota de stoc și compensarea; nota încasării / plății din Casă rămânea cu numărul lipit pe ecran.
Fixtura și emiterea sunt cele ale testului 443 (`core/test_lot11_n_443_existente.py`): schema efemeră din `tenant_template.sql`, ROLLBACK.
"""
from core.test_lot11_n_443_existente import SCH, _emite, conn  # noqa: F401  (fixtura `conn`)


def _nota_casa(conn, fid, text, status="ciorna"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, factura_id, document_ref) "
                    "VALUES ('2099-10-10', %s, 'casa', 'ciorna', %s, 'Chitanța CH-1') RETURNING id", (text, fid))
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5311', '4111', 121)",
                    (nid,))
        if status != "ciorna":
            cur.execute("UPDATE inregistrari SET status = %s WHERE id = %s", (status, nid))
    return nid


def test_def_c135_nota_de_casa_a_facturii_se_arata_cu_seria_separat(conn):
    """MUTAȚIE: ramura `i.sursa = 'casa'` scoasă din `note_cu_serie_lipita` -> pică (nota nu mai e găsită)."""
    from core import jurnal_api as _j
    fid = _emite(conn)   # factura F6 nr. 1 („F61” în forma veche, lipită)
    inc = _nota_casa(conn, fid, "Încasare de la client — chitanța CH-1 — factura F61 din 10.10.2099 — Client N SRL")
    plata = _nota_casa(conn, fid, "Plată către furnizor — factura F61 din 10.10.2099 — Furnizor N SRL", status="validata")
    omul = _nota_casa(conn, fid, "Am încasat F61 de la client")   # textul omului nu se atinge
    with conn.cursor() as cur:
        afisat = _j.note_fara_serie_lipita(cur, SCH, [inc, plata, omul])
    assert afisat == {
        inc: {"descriere": "Încasare de la client — chitanța CH-1 — factura F6 nr. 1 din 10.10.2099 — Client N SRL"},
        plata: {"descriere": "Plată către furnizor — factura F6 nr. 1 din 10.10.2099 — Furnizor N SRL"},
    }, afisat
