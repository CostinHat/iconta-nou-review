# -*- coding: utf-8 -*-
"""GARD — nota derivată dintr-un document se corectează numai din documentul-sursă (lotul 07.10 B, decizia Costin C9).

„o notă derivată dintr-un document (stat de plată, factură, ieșire din stoc, NIR, amortizare și restul clasei) se corectează numai
din documentul-sursă; recontabilizarea înlocuiește nota respinsă și o retrimite la validare; editarea manuală în jurnal e blocată
pentru notele derivate, cu mesaj care spune unde se corectează.” Constatarea (retest 07.10, F5 09/2026 nota #3): mesajul o trimitea
pe Ana în Registrul-jurnal, iar „Contabilizează statul” reafișa nota respinsă, fără cale de refacere.
"""
import json

from core.test_lot0710_p2 import SCH, _ca, _factura_cu_doua_note, _nota, tx  # noqa: F401 — fixture-ul `tx`


def _respinge(cur, tid, cab, nota_id):
    # fixtura-sintetica-ok: rândul din coada PARTAJATĂ e scris în tranzacția fixturii `tx`, anulată (ROLLBACK) la ieșire
    cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, fel, perioada, stare, payload, hash) "
                "VALUES (%s, %s, 'nota', 'nota', %s, 'respinsa', '{}'::jsonb, 'x')", (cab, tid, "nota-%d" % nota_id))


def test_documentul_sursa_se_recunoaste_dupa_legatura_nu_dupa_sursa(tx):
    from core import note_derivate as nd
    conn, cur, tid, cab, asist, valid = tx
    _fid, n_contare, n_iesire = _factura_cu_doua_note(conn, cur)
    manuala = _nota(conn, "Manuală", 10)
    operatiune = _nota(conn, "Leasing (Operațiuni)", 10)
    cur.execute("UPDATE inregistrari SET sursa='facturi' WHERE id=%s", (operatiune,))      # Operațiuni: sursă, dar fără document
    nir = [_nota(conn, "NIR %d" % k, 5) for k in range(2)]
    cur.execute("INSERT INTO nir (numar, data, inregistrari_ids) VALUES ('7', '2026-10-05', %s)", (json.dumps(nir),))
    stat = _nota(conn, "Salariile lunii 09/2026", 100)
    cur.execute("UPDATE inregistrari SET sursa='salarii', numar='SAL 09/2026' WHERE id=%s", (stat,))
    fel = {k: (nd.documentul_sursa(cur, SCH, k) or (None,))[0] for k in (n_contare, n_iesire, manuala, operatiune, nir[0], stat)}
    assert fel == {n_contare: "factura", n_iesire: "stoc", manuala: None, operatiune: None, nir[0]: "nir", stat: "salarii"}


def test_jurnalul_nu_editeaza_si_nu_sterge_nota_derivata(tx):
    """MUTAȚIE: verificarea `documentul_sursa` scoasă din `jurnal_api.editeaza` -> contarea facturii se editează din jurnal."""
    from core import jurnal_api as j, note_derivate as nd
    conn, cur, tid, cab, asist, valid = tx
    _fid, n_contare, n_iesire = _factura_cu_doua_note(conn, cur)
    r = j.editeaza(conn, SCH, n_contare, descriere="altceva")
    assert (r["cod"], r["document"]) == (nd.COD, "factura")
    assert j.sterge(conn, SCH, n_iesire)["cod"] == nd.COD            # ieșirea din stoc: legătura mișcării ar rămâne în aer
    assert j.sterge(conn, SCH, n_contare) == {"ok": True}            # contarea: legătura stă pe notă, factura redevine necontată
    manuala = _nota(conn, "Manuală", 10)
    assert j.editeaza(conn, SCH, manuala, descriere="corectată") == {"ok": True}


def test_recontabilizarea_facturii_inlocuieste_contarea_respinsa(tx):
    """„Contabilizează” (actul explicit) pe o factură cu contarea RESPINSĂ scrie nota din nou; cea respinsă dispare, iar a doua
    chemare pe o contare care NU e respinsă rămâne fără efect. MUTAȚIE: ramura `respinsa` scoasă -> „deja_contata”."""
    from core import contare_facturi as cf, facturi_api
    conn, cur, tid, cab, asist, valid = tx
    cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, tip_firma, forma_juridica, capital_subscris) "
                "VALUES (1, 'ZT SRL', '14399840', true, 'srl', 'SRL', 200) ON CONFLICT (id) DO NOTHING")
    fid = facturi_api.creeaza_factura(conn, "ZTR1", "2026-10-05", "emisa",
                                      [{"descriere": "Servicii", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}],
                                      tert_nume="Client SRL", tert_cui="RO14399840")
    fid = fid["factura_id"] if isinstance(fid, dict) else fid
    with cf.cursor_dict(conn) as c2:
        vechi = cf.contare_existenta(c2, SCH, fid) or cf.contabilizeaza(c2, SCH, fid, automat=False) and cf.contare_existenta(c2, SCH, fid)
        assert cf.contabilizeaza(c2, SCH, fid, automat=False)["stare"] == "deja_contata"     # nerespinsă: nu se dublează
        _respinge(cur, tid, cab, vechi["id"])
        r = cf.contabilizeaza(c2, SCH, fid, automat=False)
        nou = cf.contare_existenta(c2, SCH, fid)
    assert r.get("stare") != "deja_contata" and nou["id"] != vechi["id"]
    cur.execute("SELECT count(*) FROM inregistrari WHERE id = %s", (vechi["id"],))
    assert cur.fetchone()[0] == 0
