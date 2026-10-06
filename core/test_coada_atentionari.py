# -*- coding: utf-8 -*-
"""GARD — „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului. O eroare DUK oprește.”
(comanda Costin 07.10.2026, C3)

Instanța: D112 Panificatie 09/2026 (B4_5P 4.125, corect după OUG 89/2025 art.III alin.(5) lit.b) semnalat de un validator vechi cu
atenționarea SP1B4_1 -> coada îl refuza ca „erori”, deși ecranul spunea „nu blochează depunerea”. Iar `motiv_trecere` trecea peste
ORICE verdict, inclusiv peste erori.
CE FACE IMPOSIBIL: (1) o eroare DUK în coadă, aprobată sau depusă — cu sau fără motiv; (2) o atenționare trecută fără confirmare
scrisă; (3) o confirmare care rămâne valabilă după ce XML-ul s-a regenerat. LIMITA: severitatea o dă `duk.severitate` (linii
A: / E:, fail-safe spre eroare) — un format DUK nou, neclasificat, e tratat ca eroare.
"""
import json

import pytest

from core import coada_api
from core import db as _db

XML = "<D112><x>1</x></D112>"
ATENT = "A: asigurat (4) [idAsig = 4] sectiune asiguratB4 (1)\n atentionare regula: SP1B4_1: B4_5P(4125) diferit de suma calculata 3750"
EROARE = "E: angajator sectiune A (1)\n eroare regula: A21.1"


def _v(verdict, erori, conf=None, xml=XML):
    amp = coada_api.amprenta_xml(xml)
    return coada_api.verdict_din_rand(verdict, erori, amp, None, "J27", xml, conf)


def test_atentionarea_neconfirmata_nu_e_gata_de_depus():
    v = _v("erori", ATENT)
    assert (v["severitate"], v["atentionari_confirmate"], coada_api.gata_de_depus(v)) == ("atentionare", False, False)


def test_atentionarea_confirmata_pe_acelasi_xml_e_gata_de_depus():
    """MUTAȚIE: ramura atenționării scoasă din `gata_de_depus` -> pică."""
    conf = {"text": "salariul part-time 4.125 e corect (OUG 89/2025 art.III alin.(5) lit.b)", "de_id": 1, "la": "x",
            "amprenta": coada_api.amprenta_xml(XML)}
    assert coada_api.gata_de_depus(_v("erori", ATENT, conf)) is True


def test_confirmarea_nu_tine_dupa_regenerare():
    """MUTAȚIE: comparația cu amprenta scoasă -> pică."""
    conf = {"text": "m", "de_id": 1, "la": "x", "amprenta": coada_api.amprenta_xml("<D112>ALT</D112>")}
    assert coada_api.gata_de_depus(_v("erori", ATENT, conf)) is False


def test_eroarea_nu_e_niciodata_gata_de_depus():
    conf = {"text": "m", "de_id": 1, "la": "x", "amprenta": coada_api.amprenta_xml(XML)}
    assert coada_api.gata_de_depus(_v("erori", EROARE, conf)) is False
    assert coada_api.gata_de_depus(_v("erori", ATENT + "\n" + EROARE, conf)) is False   # amestec: eroare


@pytest.fixture()
def element():
    try:
        _db.init_pool()
    except Exception:                                         # noqa: BLE001
        pytest.skip("DB indisponibil")
    conn = _db.pool().getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume, patru_ochi_activ) VALUES ('ZTEST ATENT', false) RETURNING id")
            fid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email, password_hash, nume, rol, accounting_firm_id, activ, poate_valida, poate_depune) "
                        "VALUES ('ztest_atent@invalid','x','ZTest','angajat',%s,true,true,true) RETURNING id", (fid,))
            uid = cur.fetchone()[0]
            # fixtura-sintetica-ok: tenant_id NEGATIV + perioadă 2099 + rollback
            cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, perioada, stare, payload, creat_de, creat_de_id) "
                        "VALUES (%s,-43,'d112','2099-01','la_senior',%s,%s,%s) RETURNING id",
                        (fid, json.dumps({"xml": XML, "_an": 2099, "_luna": 1}), str(uid), uid))
            cid = cur.fetchone()[0]
        yield conn, cid, uid
    finally:
        conn.rollback()
        _db.pool().putconn(conn)


def test_poarta_refuza_eroarea_chiar_cu_motiv(element):
    """MUTAȚIE: ramura ERORI_DUK scoasă din `_poarta_verdict` (motivul trece din nou peste erori) -> pică."""
    conn, cid, uid = element
    coada_api.scrie_verdict(conn, cid, {"stare": "erori", "erori": EROARE}, "J27", XML)
    r = coada_api._poarta_verdict(conn, cid, "depune", "trec peste, urgent", uid)
    assert (r or {}).get("cod") == "ERORI_DUK"


def test_poarta_cere_confirmarea_atentionarii_si_o_pastreaza(element):
    """MUTAȚIE: confirmarea nescrisă în payload -> a doua întrebare a porții pică."""
    conn, cid, uid = element
    coada_api.scrie_verdict(conn, cid, {"stare": "erori", "erori": ATENT}, "J27", XML)
    assert coada_api._poarta_verdict(conn, cid, "aproba", None, uid)["cod"] == "ATENTIONARI_NECONFIRMATE"
    assert coada_api._poarta_verdict(conn, cid, "aproba", "4.125 e pragul din OUG 89/2025 art.III alin.(5) lit.b", uid) is None
    st = coada_api.verdict_stare(conn, cid)
    assert (st["atentionari_confirmate"], st["confirmare"]["de_id"], st["confirmare"]["text"]) == (
        True, uid, "4.125 e pragul din OUG 89/2025 art.III alin.(5) lit.b")
    assert len(st["confirmare"]["la"] or "") == 19                    # momentul confirmării (ISO, secunde) — cine, ce, CÂND
    assert coada_api._poarta_verdict(conn, cid, "depune", None, uid) is None      # depunerea recunoaște confirmarea


def test_ecranul_cabinetului_nu_ofera_trecere_peste_eroare():
    """MUTAȚIE: ramura `!vi.faraTrecere` scoasă (butonul „Depune totuși…” și la erori) -> pică."""
    import os
    import re
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static/js/ecrane/validat.js"),
               encoding="utf-8").read()
    assert re.search(r'faraTrecere: v\.verdict === "erori"', src)
    assert re.search(r'\} else if \(!vi\.faraTrecere\) \{\s*actiuni \+= `<button class="val-btn val-trece" data-act="trece"[^`]*>Depune totuși…', src)
    assert re.search(r'if \(vi\.atentionari\) \{\s*actiuni \+= `<button class="val-btn val-trece"[^`]*>Confirmă atenționările și depune…', src)
