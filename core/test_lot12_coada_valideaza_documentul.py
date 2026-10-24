# -*- coding: utf-8 -*-
"""Lotul 12, clasa deficienței 80 (Costin, retestul 07.10.2026, verbatim în DECIZII: „Coada, F1A3: contarea și ieșirea din stoc apar
ca două elemente separate, fiecare cu Validează/Respinge; validarea contării NU a validat ieșirea din stoc.”).

În coadă documentul se validează o dată, cu toate notele lui (`coada_api.aproba`, lotul 07.10 pct.9). Drumul rămas era Registrul
jurnal: „Validează” pe o notă a documentului (contarea facturii, o notă a NIR-ului) valida numai nota aceea, iar celelalte rămâneau
ciornă. `coada_api.valideaza_documentul` aplică aceeași regulă pe drumul jurnalului: toate ciornele documentului (cheia `_GRUP_DOC`),
ori niciuna — la refuzul unei note, refuzul o numește. Temei: N/A — regulă de produs (CLAUDE.md §9: situații identice, soluții identice).

Testele rulează într-o singură tranzacție anulată la final (schemă efemeră din `tenant_template.sql`)."""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_lot12_valideaza_doc"


@pytest.fixture()
def tx():
    try:
        _db.init_pool()
    except Exception:  # noqa: BLE001 — deja inițializat
        pass
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    try:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
        cur.execute('SET LOCAL search_path TO "%s", public' % SCH)
        cur.execute("UPDATE firma_profil SET metoda_stoc = 'global_valoric'")
        if cur.rowcount == 0:   # șablonul nu are rândul profilului: firma nouă îl primește la primul „Date firmă”
            cur.execute("INSERT INTO firma_profil (nume, cui, metoda_stoc) VALUES ('ZT Lot 12 Validare Document', '14399840', 'global_valoric')")
        yield conn, cur
    finally:
        conn.rollback()   # `SET LOCAL` piere odată cu tranzacția: conexiunea se întoarce în pool fără schema firmei
        p.putconn(conn)


def _nir(conn, numar):
    from core import stocuri_api
    r = stocuri_api.adauga_nir(conn, SCH, {"numar": numar, "data": "2026-10-05", "furnizor": "Furnizor Lot12 SRL", "transport": 0,
                                           "taxe": 0, "linii": [{"denumire": "Marfa Lot12", "cantitate": 10, "pret_achizitie": 5,
                                                                 "pret_vanzare": 9.68, "cota_tva": 21}]})
    assert "eroare" not in r, r
    cur = conn.cursor()
    cur.execute("SELECT inregistrari_ids FROM nir WHERE numar = %s", (numar,))
    ids = sorted(int(i) for i in cur.fetchone()[0])
    assert len(ids) > 1, ids          # NIR-ul global-valoric fără factură are mai multe note (documentul cu mai multe note)
    return ids


def _stari(cur, ids):
    cur.execute("SELECT id, status FROM inregistrari WHERE id = ANY(%s) ORDER BY id", (ids,))
    return dict(cur.fetchall())


def test_validarea_unei_note_a_nir_ului_valideaza_toate_notele_lui(tx):
    """MUTAȚIE: `notele_documentului` întoarce numai nota cerută -> celelalte note ale NIR-ului rămân ciornă -> pică."""
    from core import coada_api as c
    conn, cur = tx
    ids = _nir(conn, "L12-1")
    assert c.notele_documentului(cur, SCH, ids[1]) == [ids[1]] + [i for i in ids if i != ids[1]]
    r = c.valideaza_documentul(conn, SCH, ids[1])
    assert r.get("ok") and sorted(r["validate"]) == ids, r
    # documentul se validează o dată, cu toate notele lui (ca în coadă, `aproba`)
    assert set(_stari(cur, ids).values()) == {"validata"}, _stari(cur, ids)


def test_nota_care_nu_e_a_unui_document_cu_mai_multe_note_se_valideaza_singura(tx):
    from core import coada_api as c, jurnal_api as j
    conn, cur = tx
    ids = _nir(conn, "L12-2")
    n = j.creeaza(conn, SCH, "Chirie lot 12", "2026-10-05", [{"debit": "612", "credit": "401", "suma": 100,
                                                               "partener_nume": "PARTENER PROBA SRL"}], document_ref="Factura CH12")["id"]
    assert c.notele_documentului(cur, SCH, n) == [n]
    assert c.valideaza_documentul(conn, SCH, n)["validate"] == [n]
    assert set(_stari(cur, ids).values()) == {"ciorna"}        # NIR-ul nu e atins de validarea altei note


def test_refuzul_unei_note_a_documentului_o_numeste_si_nu_valideaza_restul(tx):
    """O notă a documentului care nu se poate valida (aici: fără linii) oprește validarea documentului; refuzul o numește. Apelantul
    (ruta) anulează tranzacția la refuz — aici, punctul de salvare ține locul ei."""
    from core import coada_api as c
    conn, cur = tx
    ids = _nir(conn, "L12-3")
    cur.execute("DELETE FROM inregistrari_linii WHERE inregistrare_id = %s", (ids[-1],))
    cur.execute("SAVEPOINT doc")
    r = c.valideaza_documentul(conn, SCH, ids[0])
    cur.execute("ROLLBACK TO SAVEPOINT doc")
    assert r.get("eroare", "").startswith("Nota ") and "a aceluiași document nu se poate valida" in r["eroare"], r
    assert "nota nu are linii" in r["eroare"], r
    assert set(_stari(cur, ids).values()) == {"ciorna"}
