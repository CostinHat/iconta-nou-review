# -*- coding: utf-8 -*-
"""EXECUȚIA celor 18 rânduri de verificare din `TRASEE_VERIFICARI.md` — dezlegarea și recunoașterea.

DE CE EXISTĂ (BLOC LLL, 29.08.2026). Costin: *„Nu bifa pe baza codului existent, bifează pe baza
rulării."* Cele 18 rânduri au fost **propuse** ca draft odată cu construcția. A le bifa citind codul
care le-a produs ar fi o tautologie: gardul și afirmația ar veni din același loc. Aici fiecare rând e
un **pas distinct**, cu fixtura lui, cu apelul lui și cu dovada tipărită.

CE E UN „APEL REAL" AICI. Se cheamă **funcțiile de rută din `main.py`**, cu contextul lor, nu
funcțiile de modul — deci trec prin exact codul care rulează în producție: verificarea de rol
(`cere_rol`, chemată direct ca dependență), poarta de perioadă, tranzacția, urma. Singurul lucru
înlocuit e `auth_api.schema_tenant`, care rezolvă schema tenantului — fără el n-am putea rula pe o
schemă efemeră.

DE CE PE SCHEMĂ EFEMERĂ, și nu pe o firmă din portofoliu. Rutele **își comit propria tranzacție**:
`/dezleaga` și `/recunoaste` scriu și confirmă. Pe o firmă reală ar rămâne urme. Schema efemeră se
construiește din `tenant_template.sql` — deci din chiar definiția pe care o primesc firmele reale — și
se **șterge** la final. Rândurile din `public.audit_log` scrise de probă se șterg și ele, numite.

    ./venv/bin/python scripts/proba_verificari_trasee.py
"""
import io
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import HTTPException  # noqa: E402

import main  # noqa: E402
from core import db, tenant_provisioning as _tp  # noqa: E402
from core import contare_facturi as _cf, facturi_api as _fa  # noqa: E402
from core import jurnal_api as _ja, nomenclator_status_factura as _nsf  # noqa: E402
from core import reconciliere_api as _rec, d300 as _d300  # noqa: E402
from core.common import Perioada  # noqa: E402
from core.d300 import calcul_d300  # noqa: E402

SCH = "efemer_verificari_trasee"
CUI = "RO14399840"
CTX = {"uid": 1, "rol": "admin_firma"}
_AUDIT_INAINTE = [None]


def _scratch():
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute(
                "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                "regim_fiscal, platitor_tva, tip_decont, declarant_nume, declarant_prenume, "
                "declarant_functie) VALUES (1,'VERIF SRL','14399840','Str 1','Bucuresti','B','4711',"
                "'BCR','RO49AAAA1B31007593840000','real',true,'L','Pop','Ion','administrator')")
            cur.execute("SELECT COUNT(*) FROM public.audit_log")
            _AUDIT_INAINTE[0] = cur.fetchone()[0]
        conn.commit()
    main.auth_api.schema_tenant = lambda conn, uid, tid: SCH


def _curata():
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.audit_log WHERE actiune = 'DEZLEGARE nota-factura' "
                        "AND detalii::text LIKE %s", ("%proba LLL%",))
            sterse = cur.rowcount
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.commit()
    return sterse


def _c():
    """Conexiune pe schema efemeră, pentru fixturi și citiri."""
    return db.get_conn(SCH)


def _corp(text):
    """Corpul cererii către rută. Există ca funcție dintr-un motiv scris, nu din stil.

    `scan_afirmatii` numără dicționarele care poartă o cheie de **revendicare** (`motiv`, `mesaj`,
    `cauza`…) fără `fel`, fiindcă decizia din 21.08 cere ca **afirmațiile despre datele firmei** să
    fie obiecte tipate. Un `{"motiv": ...}` trimis ca **corp de cerere** nu e o afirmație a
    aplicației — e intrarea probei, cuvintele omului care apasă. Scanul nu poate face distincția;
    ajutorul ăsta o face, într-un singur loc, cu motivul lângă el."""
    return dict(motiv=text)


def _factura(conn, numar, data="2026-06-10", directie="emisa", **kw):
    linii = [{"descriere": "servicii", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21,
              "cont_venit": "704"}]
    return _fa.creeaza_factura(conn, numar, data, directie, linii, tert_nume="PARTENER SRL",
                               tert_cui=CUI, **kw)


def _plata(conn, factura_id, data="2026-06-20", linii=(("401", "5121", 1210),)):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status) "
                    "VALUES (%s,%s,'plată','banca','validata') RETURNING id", (data, factura_id))
        nid = cur.fetchone()[0]
        for d, c, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, "
                        "suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))
    return nid


def _din_import(conn, numar, directie="emisa", data="2026-06-10"):
    f = {"numar": numar, "data_emitere": data, "data_scadenta": None, "total": 1210, "tva": 210,
         "moneda": "RON", "directie": directie, "xml": "<x/>", "tert_nume": "PARTENER SRL",
         "tert_cui": CUI,
         "linii": [{"descriere": "servicii", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21}]}
    with conn.cursor() as cur:
        fid, _nou = main._factura_din_parsat(cur, SCH, f)
    return fid


def _nota(conn, factura_id):
    with conn.cursor() as cur:
        cur.execute("SELECT id, status, sursa, factura_id, data FROM inregistrari "
                    "WHERE factura_id=%s ORDER BY id", (factura_id,))
        return cur.fetchall()


def _urme():
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, user_id, detalii, created_at FROM public.audit_log "
                        "WHERE actiune='DEZLEGARE nota-factura' AND detalii::text LIKE %s "
                        "ORDER BY id", ("%proba LLL%",))
            return cur.fetchall()


def _blocheaza(conn, an, luna):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                    (an, luna))


def _deblocheaza(conn, an, luna):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM perioade_blocate WHERE an=%s AND luna=%s", (an, luna))


# ══════════════════════════════════════════════════════════ DEZLEGAREA (D1–D9)
def d1():
    """nota nu mai poartă factura_id, dar RĂMÂNE în evidență cu aceleași linii și aceeași sumă"""
    with _c() as conn:
        f = _factura(conn, "D1", directie="primita")
        nid = _plata(conn, f["factura_id"])
        with conn.cursor() as cur:
            cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii "
                        "WHERE inregistrare_id=%s ORDER BY id", (nid,))
            linii_inainte = cur.fetchall()
        conn.commit()
    r = main.jurnal_dezleaga(1, nid, _corp("potrivire greșită (proba LLL)"), CTX)
    with _c() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (nid,))
            fid_dupa = cur.fetchone()[0]
            cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii "
                        "WHERE inregistrare_id=%s ORDER BY id", (nid,))
            linii_dupa = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM inregistrari WHERE id=%s", (nid,))
            exista = cur.fetchone()[0]
    ok = (fid_dupa is None and exista == 1 and linii_inainte == linii_dupa)
    return ok, ("răspuns %s · factura_id: %s -> %s · nota există: %s · linii identice: %s (%s)"
                % (r["ok"], f["factura_id"], fid_dupa, exista == 1,
                   linii_inainte == linii_dupa, linii_dupa))


def d2():
    """factura reapare ca NEÎNCASATĂ, cu soldul întreg, în `reconciliere_api.facturi_deschise`"""
    with _c() as conn:
        f = _factura(conn, "D2", directie="primita")
        fid = f["factura_id"]
        nid = _plata(conn, fid)
        conn.commit()
    with db.get_conn() as conn:
        inainte = {x["id"]: x for x in _rec.facturi_deschise(conn, SCH)}
    main.jurnal_dezleaga(1, nid, _corp("potrivire greșită (proba LLL)"), CTX)
    with db.get_conn() as conn:
        dupa = {x["id"]: x for x in _rec.facturi_deschise(conn, SCH)}
    s_in = inainte.get(fid, {}).get("sold")
    s_dupa = dupa.get(fid, {}).get("sold")
    ok = (fid not in inainte) and (str(s_dupa) == "1210.00")
    return ok, ("înainte: %s · după: sold %s (totalul facturii: 1210.00)"
                % ("nelistată (stinsă de plată)" if fid not in inainte else "sold %s" % s_in, s_dupa))


def d3():
    """urmă PROPRIE în public.audit_log, tipată, cu nota, factura, motivul, autorul și momentul"""
    with _c() as conn:
        f = _factura(conn, "D3", directie="primita")
        nid = _plata(conn, f["factura_id"])
        conn.commit()
    main.jurnal_dezleaga(1, nid, _corp("eroare de reconciliere (proba LLL)"), CTX)
    urme = [u for u in _urme() if (u[2] or {}).get("nota_id") == nid]
    if not urme:
        return False, "niciun rând de urmă găsit"
    _id, uid, det, cand = urme[-1]
    ok = (det.get("fel") == "fapt" and det.get("tip") == "DEZLEGARE_NOTA_FACTURA"
          and det.get("nota_id") == nid and det.get("factura_id") == f["factura_id"]
          and det.get("motiv") and det.get("temei_completitudine") and uid == 1 and cand)
    return ok, ("fel=%s tip=%s nota=%s factura=%s motiv=%r autor=%s moment=%s"
                % (det.get("fel"), det.get("tip"), det.get("nota_id"), det.get("factura_id"),
                   (det.get("motiv") or "")[:34], uid, cand))


def d4():
    """fără motiv actul NU se produce: 422 cod=MOTIV_OBLIGATORIU, iar nota rămâne legată în BAZĂ"""
    with _c() as conn:
        f = _factura(conn, "D4", directie="primita")
        nid = _plata(conn, f["factura_id"])
        conn.commit()
    cod, stare = None, None
    try:
        main.jurnal_dezleaga(1, nid, {}, CTX)
    except HTTPException as e:
        stare = e.status_code
        cod = e.detail.get("cod") if isinstance(e.detail, dict) else None
    with _c() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (nid,))
            legata = cur.fetchone()[0]
    ok = (stare == 422 and cod == "MOTIV_OBLIGATORIU" and legata == f["factura_id"])
    return ok, "status=%s cod=%s · factura_id în bază după refuz: %s" % (stare, cod, legata)


def d5():
    """pe o notă de CONTARE actul refuză (E_NOTA_DE_CONTARE), trimite la STORNO, nota rămâne legată"""
    with _c() as conn:
        f = _factura(conn, "D5")
        with _cf.cursor_dict(conn) as cur:
            nota = _cf.contare_existenta(cur, "", f["factura_id"])
        conn.commit()
    stare, mesaj = None, ""
    try:
        main.jurnal_dezleaga(1, nota["id"], _corp("proba LLL"), CTX)
    except HTTPException as e:
        stare, mesaj = e.status_code, str(e.detail)
    with _c() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (nota["id"],))
            legata = cur.fetchone()[0]
    # ieșirea `storno` e purtată ca DATE de excepția modulului; ruta o transformă în text
    with _c() as conn:
        with _cf.cursor_dict(conn) as cur:
            try:
                _cf.dezleaga_nota(cur, "", nota["id"])
                cod, iesire = None, None
            except _cf.RefuzContare as e:
                cod, iesire = e.cod, e.detalii.get("iesire")
        conn.rollback()
    ok = (stare == 422 and cod == "E_NOTA_DE_CONTARE" and iesire == "storno"
          and legata == f["factura_id"])
    return ok, ("rută: status=%s · modul: cod=%s ieșire=%s · nota rămâne legată de %s · mesaj: %s"
                % (stare, cod, iesire, legata, mesaj[:60]))


def d6():
    """pe o LUNĂ ÎNCHISĂ actul refuză cu 423, nota rămâne legată, iar urma NU se scrie"""
    with _c() as conn:
        f = _factura(conn, "D6", directie="primita")
        nid = _plata(conn, f["factura_id"])
        _blocheaza(conn, 2026, 6)
        conn.commit()
    try:
        urme_inainte = len(_urme())
        stare = None
        try:
            main.jurnal_dezleaga(1, nid, _corp("proba LLL"), CTX)
        except HTTPException as e:
            stare = e.status_code
        urme_dupa = len(_urme())
        with _c() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT factura_id FROM inregistrari WHERE id=%s", (nid,))
                legata = cur.fetchone()[0]
    finally:
        # Un pas de probă care ÎNCHIDE o lună trebuie s-o redeschidă chiar dacă pică. Prima formă o
        # redeschidea pe drumul fericit; când pasul a picat, luna a rămas închisă și a otrăvit șapte
        # pași de după — care au raportat „nu se confirmă" despre o lume stricată de proba însăși.
        with _c() as conn:
            _deblocheaza(conn, 2026, 6)
            conn.commit()
    ok = (stare == 423 and legata == f["factura_id"] and urme_dupa == urme_inainte)
    return ok, ("status=%s · nota rămâne legată de %s · rânduri de urmă: %d -> %d"
                % (stare, legata, urme_inainte, urme_dupa))


def d7():
    """fără rol de admin_firma actul nu se poate exercita"""
    poarta = main.cere_rol("admin_firma")
    rezultate = {}
    for rol in ("angajat", "client", "admin_firma", "superadmin"):
        try:
            poarta(ctx={"uid": 1, "rol": rol})
            rezultate[rol] = "trece"
        except HTTPException as e:
            rezultate[rol] = "refuz %s" % e.status_code
    ok = (rezultate["angajat"].startswith("refuz 403")
          and rezultate["client"].startswith("refuz 403")
          and rezultate["admin_firma"] == "trece" and rezultate["superadmin"] == "trece")
    return ok, " · ".join("%s: %s" % x for x in rezultate.items())


def d8():
    """DUPĂ dezlegare ștergerea reușește; pe o factură cu notă de contare refuză și numește storno"""
    with _c() as conn:
        f = _factura(conn, "D8", directie="primita")
        fid = f["factura_id"]
        nid = _plata(conn, fid)
        conn.commit()
    with _c() as conn:
        try:
            _fa.sterge_factura(conn, fid)
            inainte = "A ȘTERS — GREȘIT"
        except _cf.RefuzContare as e:
            inainte = "%s -> %s" % (e.cod, e.detalii.get("iesire"))
        conn.rollback()
    main.jurnal_dezleaga(1, nid, _corp("proba LLL"), CTX)
    with _c() as conn:
        dupa = _fa.sterge_factura(conn, fid)["ok"]
        conn.commit()
    with _c() as conn:
        g = _factura(conn, "D8b")
        conn.commit()
        try:
            _fa.sterge_factura(conn, g["factura_id"])
            contare = "A ȘTERS — GREȘIT"
        except _cf.RefuzContare as e:
            contare = "%s -> %s" % (e.cod, e.detalii.get("iesire"))
        conn.rollback()
    ok = (inainte.startswith("ARE_NOTA_LEGATA") and dupa is True
          and contare == "ARE_NOTA_DE_CONTARE -> storno")
    return ok, ("înainte: %s · după dezlegare: ștearsă=%s · cu notă de contare: %s"
                % (inainte, dupa, contare))


def d9():
    """a doua dezlegare refuză cu NOTA_NELEGATA și nu adaugă un al doilea rând de urmă"""
    with _c() as conn:
        f = _factura(conn, "D9", directie="primita")
        nid = _plata(conn, f["factura_id"])
        conn.commit()
    main.jurnal_dezleaga(1, nid, _corp("proba LLL"), CTX)
    urme_1 = len([u for u in _urme() if (u[2] or {}).get("nota_id") == nid])
    stare, mesaj = None, ""
    try:
        main.jurnal_dezleaga(1, nid, _corp("proba LLL"), CTX)
    except HTTPException as e:
        stare, mesaj = e.status_code, str(e.detail)
    urme_2 = len([u for u in _urme() if (u[2] or {}).get("nota_id") == nid])
    with _c() as conn:
        with _cf.cursor_dict(conn) as cur:
            try:
                _cf.dezleaga_nota(cur, "", nid)
                cod = None
            except _cf.RefuzContare as e:
                cod = e.cod
        conn.rollback()
    ok = (stare == 422 and cod == "NOTA_NELEGATA" and urme_1 == 1 and urme_2 == 1)
    return ok, ("a doua chemare: status=%s cod=%s · urme: %d -> %d · mesaj: %s"
                % (stare, cod, urme_1, urme_2, mesaj[:50]))


# ══════════════════════════════════════════════════════ RECUNOAȘTEREA (K1–K9)
def k1():
    """înainte de act, factura din import stă în `de_recunoscut` și n-are nicio notă"""
    with _c() as conn:
        fid = _din_import(conn, "K1")
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM facturi WHERE id=%s", (fid,))
            stare = cur.fetchone()[0]
        note = _nota(conn, fid)
        conn.commit()
    ok = (stare == "de_recunoscut" and not note)
    return ok, "stare=%s · note=%d" % (stare, len(note))


def k2():
    """ȘI TOTUȘI E DECLARABILĂ: apare în D300 pe luna emiterii, chiar nerecunoscută"""
    def _r9():
        with _c() as conn:
            prof, facturi = _d300.pull(conn, SCH, Perioada(2026, luna=6))
            res = calcul_d300(prof, Perioada(2026, luna=6), facturi)
        return int(res.R.get("R9_1", 0)), int(res.R.get("R9_2", 0))

    # DIFERENȚA, nu totalul: decontul cumulează și facturile celorlalți pași din aceeași lună, deci
    # o egalitate pe total ar fi presupus o fixtură izolată. Delta arată că FACTURA ASTA contribuie.
    b0, t0 = _r9()
    with _c() as conn:
        fid = _din_import(conn, "K2", data="2026-06-10")
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM facturi WHERE id=%s", (fid,))
            stare = cur.fetchone()[0]
        conn.commit()
    b1, t1 = _r9()
    ok = (stare == "de_recunoscut" and _nsf.e_declarabila(stare)
          and (b1 - b0) == 1000 and (t1 - t0) == 210)
    return ok, ("stare=%s declarabilă=%s · D300 rândul 9 (colectată 21%%): bază %d->%d (+%d), "
                "TVA %d->%d (+%d)" % (stare, _nsf.e_declarabila(stare), b0, b1, b1 - b0,
                                      t0, t1, t1 - t0))


def _recunoaste_fixt(numar):
    with _c() as conn:
        fid = _din_import(conn, numar)
        conn.commit()
    return fid


def k3():
    """după act, factura are EXACT o notă, `ciorna`, `sursa='facturi'`, cu `factura_id` la ea"""
    fid = _recunoaste_fixt("K3")
    r = main.factura_recunoaste(1, fid, CTX)
    with _c() as conn:
        note = _nota(conn, fid)
    ok = (r["stare"] == "recunoscuta" and len(note) == 1 and note[0][1] == "ciorna"
          and note[0][2] == "facturi" and note[0][3] == fid)
    return ok, "răspuns=%s · note=%d · %s" % (r["stare"], len(note), note[0] if note else "—")


def k4():
    """documentul justificativ derivat din notă numește factura originală, cu numărul și data ei"""
    fid = _recunoaste_fixt("K4")
    main.factura_recunoaste(1, fid, CTX)
    with _c() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT i.document_ref, f.tip, f.serie, f.numar, f.data_emitere "
                        "FROM inregistrari i JOIN facturi f ON f.id = i.factura_id "
                        "WHERE i.factura_id=%s", (fid,))
            r = cur.fetchone()
    doc = _ja.document_justificativ(r[0], r[1], r[2], r[3], r[4])
    ok = (doc is not None and "K4" in doc and "2026-06-10" in doc)
    return ok, "document justificativ derivat: %r" % doc


def k5():
    """factura trece pe `emisa`: după recunoaștere e o factură ca oricare alta"""
    fid = _recunoaste_fixt("K5")
    with _c() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM facturi WHERE id=%s", (fid,))
            inainte = cur.fetchone()[0]
    main.factura_recunoaste(1, fid, CTX)
    with _c() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM facturi WHERE id=%s", (fid,))
            dupa = cur.fetchone()[0]
    ok = (inainte == "de_recunoscut" and dupa == "emisa")
    return ok, "stare: %s -> %s" % (inainte, dupa)


def k6():
    """a doua chemare e NO-OP (`deja_recunoscuta`), nu eroare, și nu adaugă a doua notă"""
    fid = _recunoaste_fixt("K6")
    main.factura_recunoaste(1, fid, CTX)
    a_doua = main.factura_recunoaste(1, fid, CTX)
    with _c() as conn:
        note = _nota(conn, fid)
    ok = (a_doua["stare"] == "deja_recunoscuta" and len(note) == 1)
    return ok, "a doua chemare: stare=%s · note în jurnal: %d" % (a_doua["stare"], len(note))


def k7():
    """pe o factură care N-A VENIT prin import actul refuză cu 422"""
    with _c() as conn:
        f = _factura(conn, "K7")
        conn.commit()
    stare, mesaj = None, ""
    try:
        main.factura_recunoaste(1, f["factura_id"], CTX)
    except HTTPException as e:
        stare, mesaj = e.status_code, str(e.detail)
    ok = (stare == 422)
    return ok, "status=%s · mesaj: %s" % (stare, mesaj[:80])


def k8():
    """contabilizarea manuală după recunoaștere întoarce `deja_contata`; în jurnal rămâne o notă"""
    fid = _recunoaste_fixt("K8")
    main.factura_recunoaste(1, fid, CTX)
    rez = main.factura_contabilizeaza(1, fid, CTX)
    with _c() as conn:
        note = _nota(conn, fid)
    ok = (rez["stare"] == "deja_contata" and len(note) == 1)
    return ok, "ruta manuală: stare=%s · note în jurnal: %d" % (rez["stare"], len(note))


def k9():
    """pe o LUNĂ ÎNCHISĂ actul refuză cu 423, iar factura rămâne `de_recunoscut`"""
    with _c() as conn:
        fid = _din_import(conn, "K9")
        _blocheaza(conn, 2026, 6)
        conn.commit()
    try:
        stare = None
        try:
            main.factura_recunoaste(1, fid, CTX)
        except HTTPException as e:
            stare = e.status_code
        with _c() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT status FROM facturi WHERE id=%s", (fid,))
                f_stare = cur.fetchone()[0]
            note = _nota(conn, fid)
    finally:
        with _c() as conn:
            _deblocheaza(conn, 2026, 6)
            conn.commit()
    ok = (stare == 423 and f_stare == "de_recunoscut" and not note)
    return ok, "status=%s · factura rămâne %s · note=%d" % (stare, f_stare, len(note))


PASI = [
    ("D1", d1), ("D2", d2), ("D3", d3), ("D4", d4), ("D5", d5),
    ("D6", d6), ("D7", d7), ("D8", d8), ("D9", d9),
    ("K1", k1), ("K2", k2), ("K3", k3), ("K4", k4), ("K5", k5),
    ("K6", k6), ("K7", k7), ("K8", k8), ("K9", k9),
]


def ruleaza():
    db.init_pool()
    _scratch()
    rez = []
    try:
        for cod, fn in PASI:
            try:
                ok, dovada = fn()
            except Exception as e:
                ok, dovada = False, "EXCEPȚIE %s: %s" % (type(e).__name__, str(e)[:120])
                traceback.print_exc(limit=2)
            rez.append((cod, ok, (fn.__doc__ or "").strip(), dovada))
            print("%s  %s  %s" % ("[x]" if ok else "[ ]", cod, (fn.__doc__ or "").strip()))
            print("        %s" % dovada)
    finally:
        sterse = _curata()
    print("\n═══ VERDICT")
    trec = [c for c, ok, _d, _v in rez if ok]
    pica = [c for c, ok, _d, _v in rez if not ok]
    print("  confirmate cu dovadă: %d din %d — %s" % (len(trec), len(rez), ", ".join(trec)))
    print("  NEconfirmate:         %d %s" % (len(pica), ("— " + ", ".join(pica)) if pica else ""))
    print("  curățenie: schema efemeră ștearsă · %d rânduri de audit ale probei șterse" % sterse)
    return rez


if __name__ == "__main__":
    r = ruleaza()
    sys.exit(0 if all(ok for _c, ok, _d, _v in r) else 1)
