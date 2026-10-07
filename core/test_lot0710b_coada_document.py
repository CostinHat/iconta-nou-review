# -*- coding: utf-8 -*-
"""GARD — coada grupează notele aceluiași DOCUMENT, și pentru elementele existente (lotul 07.10 B, comanda Costin C8).

Comanda: „Coada, F1A3: contarea și ieșirea din stoc apar ca două elemente separate … Stabilește dacă e doar pe elemente create
înainte de reparație. Oricum ar fi: coada grupează notele aceluiași document și pentru elementele existente (migrare) … Aceeași
grupare pentru cele 4 note ale unui NIR.” Măsurat pe producție (citire): elementele 11385/11386 (F1A3) au fost create pe 06.10
la 12:54, fără `payload.grup` — înaintea grupării; NIR 1 (note 110–113) — patru chei separate. Regula unică: `coada_api._GRUP_DOC`.
"""
import json

from core.test_lot0710_p2 import SCH, _ca, _factura_cu_doua_note, _nota, tx  # noqa: F401 — fixture-ul `tx`


def _nir_cu_patru_note(conn, cur):
    ids = [_nota(conn, "NIR ZT %d" % k, 100 + k, doc="NIR nr 1 din 05.10.2026") for k in range(4)]
    cur.execute("UPDATE inregistrari SET sursa='stocuri' WHERE id = ANY(%s)", (ids,))
    cur.execute("INSERT INTO nir (numar, data, inregistrari_ids) VALUES ('1', '2026-10-05', %s) RETURNING id", (json.dumps(ids),))
    return cur.fetchone()[0], ids


def test_cele_patru_note_ale_nir_sunt_un_singur_element(tx):
    """MUTAȚIE: ramura `nir-` scoasă din `_GRUP_DOC` -> patru elemente -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    nid, ids = _nir_cu_patru_note(conn, cur)
    assert len(c.pune_notele_in_coada(conn, cab, tid, asist)) == 1
    el = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert len(el) == 1 and len(el[0]["membri_ids"]) == 4
    _ca(cur, valid)
    assert len(c.aproba(conn, el[0]["id"], str(valid), valid, cabinet_id_apelant=cab, schema_nota=SCH)["membri"]) == 4


def test_plata_legata_de_factura_e_alt_document(tx):
    """O încasare (bancă) cu `factura_id` e documentul extrasului, nu al facturii: nu se validează odată cu contarea."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    fid, n1, n2 = _factura_cu_doua_note(conn, cur)
    plata = _nota(conn, "Încasare ZT1", 121, doc="Extras 1")
    cur.execute("UPDATE inregistrari SET sursa='banca', factura_id=%s WHERE id=%s", (fid, plata))
    assert len(c.pune_notele_in_coada(conn, cab, tid, asist)) == 2           # factura (2 note) + plata


def test_migrarea_leaga_elementele_vechi_de_document(tx):
    """Elementele create înaintea grupării (fără `payload.grup`, ca 11385/11386 pe producție) se leagă de document; starea nu se
    schimbă. MUTAȚIE: `aplica` care sare rândurile fără grup -> pică."""
    from core import coada_api as c, migrare_grup_coada as m
    conn, cur, tid, cab, asist, valid = tx
    _ca(cur, asist)
    _fid, n1, n2 = _factura_cu_doua_note(conn, cur)
    nid, ids = _nir_cu_patru_note(conn, cur)
    c.pune_notele_in_coada(conn, cab, tid, asist)
    cur.execute("UPDATE public.declaratii_coada SET payload = payload - 'grup' WHERE tenant_id = %s", (tid,))   # forma veche
    assert len([x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]) == 6
    schimbate = m.aplica(conn, tid)
    assert sorted(n for _i, _v, n in schimbate) == sorted(["factura-%d" % _fid] * 2 + ["nir-%d" % nid] * 4)
    el = [x for x in c.lista_coada(conn, cab, "la_senior") if x["tenant_id"] == tid]
    assert sorted(len(x["membri_ids"]) for x in el) == [2, 4]
    assert m.aplica(conn, tid) == []                                         # idempotentă
