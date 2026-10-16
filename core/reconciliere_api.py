# -*- coding: utf-8 -*-
"""Reconciliere bancară — strat API (tipar stat_plata_api: funcții conn+schema).

Motorul de matching e în core/reconciliere.py (pur, testat)."""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
import json
from decimal import Decimal, ROUND_HALF_UP
from psycopg2.extras import RealDictCursor
from core import reconciliere as _m
from core.common import cate as _cate

CONT_CLIENTI, CONT_FURNIZORI = "4111", "401"


def _data_iso(v):
    """z.l.aaaa / zz.ll.aa (cu . / -) -> aaaa-ll-zz; lasă neschimbat ce e deja ISO / date. [16.10.2026, 277] Înainte numai forma de
    exact 10 caractere cu punct: `1.8.2026` ajungea la Postgres așa cum era, care o citea lună-zi (DateStyle MDY) — 8 ianuarie."""
    import re
    m = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{2}|\d{4})", v.strip()) if isinstance(v, str) else None
    if m:
        z, l, a = m.groups()
        return "%s-%02d-%02d" % (a if len(a) == 4 else "20" + a, int(l), int(z))
    return v


def _text_cheie(v):
    """Referința / descrierea în cheia mișcării: fără spațiile în plus, fără deosebire de majuscule."""
    return " ".join(str(v or "").split()).lower()


def cheie_miscare(data, suma, tip, cont, referinta, descriere):
    """[16.10.2026, lotul 6 pct.1a, 277, verbatim în DECIZII] „o linie e duplicat numai dacă aceeași mișcare (dată, sumă, sens,
    referință/descriere, cont) există deja.” Contul necunoscut (extrasele în tabel, liniile de dinainte) rămâne `None` și nu se
    socotește egal cu un cont cunoscut."""
    return (str(data), Decimal(str(suma)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), tip, (cont or "").strip() or None,
            _text_cheie(referinta), _text_cheie(descriere))


def _cont_banca(valuta):
    return "5124" if valuta else "5121"


def facturi_deschise(conn, schema):
    """Facturi cu sold > 0. Sold = total_lei(±total) - sume decontate prin
    inregistrari legate cu factura_id (credit 4111 la emise / debit 401 la primite)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.id, f.tert_cui, f.directie, f.data_emitere,
                   COALESCE(f.total_lei, f.total) AS total,
                   COALESCE((SELECT SUM(l.suma)
                             FROM {schema}.inregistrari i
                             JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                             WHERE i.factura_id = f.id
                               AND ((f.directie='emisa'   AND l.cont_credit=%s)
                                 OR (f.directie='primita' AND l.cont_debit=%s))), 0) AS decontat,
                   COALESCE((SELECT SUM(COALESCE(st.total_lei, st.total))
                             FROM {schema}.facturi st
                             WHERE st.storno_din_id = f.id), 0) AS storno
            FROM {schema}.facturi f
            WHERE f.status NOT IN ('anulata','storno')
              AND f.storno_din_id IS NULL
        """, (CONT_CLIENTI, CONT_FURNIZORI))
        rez = []
        for r in cur.fetchall():
            sold = Decimal(r["total"] or 0) - Decimal(r["decontat"] or 0) + Decimal(r["storno"] or 0)
            if sold > Decimal("0.01"):
                rez.append({"id": r["id"], "tert_cui": r["tert_cui"],
                            "directie": r["directie"],
                            "data_emitere": r["data_emitere"], "sold": sold})
        return rez


def importa_extras(conn, schema, tranzactii, fisier="", continut=None, cont=None):
    """Persistă liniile NOI ale extrasului + rulează matching-ul pe ele. Întoarce `{"linii": [noi], "deja": [găsite], "rezumat"}`.

    [16.10.2026, lotul 6 pct.1, 277 — PIVOT peste C5 (DECIZII „Lotul 6, comanda 1”)] Duplicatul e MIȘCAREA, nu fișierul:
    `cheie_miscare` (dată, sumă, sens, cont, referință, descriere). O linie e găsită deja numai dacă aceeași mișcare există în
    `extras_linii`, socotită cu multiplicitatea ei: două comisioane identice în același extras rămân două, iar la reimport amândouă
    se găsesc. Înainte, hash-ul fișierului întreg hotăra tot: un fișier cu aceiași octeți ca unul vechi era respins în întregime
    („Extras deja importat: 2 linii”, F1, 16.10 13:18), iar un extras care se suprapunea cu unul vechi îi dubla liniile.
    Importurile pe aceeași firmă se serializează (`pg_advisory_xact_lock`), ca un dublu-clic să nu insereze de două ori.
    `extras_import` rămâne registrul fișierelor (hash, nume, număr de linii), nu mai decide nimic.
    """
    import hashlib
    from collections import Counter
    from core import repo_banca
    linii = [{"suma": Decimal(str(abs(t.get("suma", 0)))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
              "tip": "incasare" if t.get("suma", 0) > 0 else "plata",
              "cui": t.get("cui"), "descriere": t.get("detalii", ""),
              "referinta": (t.get("referinta") or "").strip() or None,
              "data": _data_iso(t.get("data"))} for t in tranzactii]
    rezumat = {"total": len(tranzactii), "noi": 0, "deja": 0, "potrivite": 0, "fara_potrivire": 0}
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", ("extras_import:" + schema,))
        cur.execute(f"SELECT data, suma, tip, cont_extras, referinta, descriere FROM {schema}.extras_linii "
                    f"WHERE data = ANY(%s::date[])", (sorted({str(ln["data"]) for ln in linii}),))
        existente = Counter(cheie_miscare(*r) for r in cur.fetchall())
        noi, deja = [], []
        for t, ln in zip(tranzactii, linii):
            k = cheie_miscare(ln["data"], ln["suma"], ln["tip"], cont, ln["referinta"], ln["descriere"])
            if existente[k] > 0:
                existente[k] -= 1
                deja.append({"data": str(ln["data"]), "suma": str(ln["suma"]), "tip": ln["tip"], "descriere": ln["descriere"]})
            else:
                noi.append((t, ln))
        rezumat["noi"], rezumat["deja"] = len(noi), len(deja)
        if continut is not None:
            h = hashlib.sha256(continut if isinstance(continut, bytes)
                               else str(continut).encode("utf-8")).hexdigest()
            repo_banca.inregistreaza_import(cur, schema, h, fisier, len(tranzactii))
        tranzactii = [t for t, _ln in noi]
        linii = [ln for _t, ln in noi]
        rezultate = _m.potriveste_extras(linii, facturi_deschise(conn, schema)) if linii else []
        out = []
        for t, ln, rez in zip(tranzactii, linii, rezultate):
            # [P8] `rez` E DEJA o afirmatie tipata (potriveste_linie); se duce mai departe intreaga,
            # nu se re-extrage `motiv` - altfel ar exista doua surse ale aceluiasi text.
            aloc = dict(rez, status_match=rez["status"],
                        alocari=[{"factura_id": a["factura_id"], "suma": str(a["suma"])}
                                 for a in rez["alocari"]])
            aloc.pop("status", None)
            # ai_sugestie_v1: linie fara facturi -> sugestie din istoricul invatat. [05.10.2026] Condiția veche cerea „fără
            # notă”, dar `banca.regula_cont` pune mereu una (client/furnizor PRESUPUS din sens) -> ramura nu rula niciodată.
            # Acum rulează când tipul NU s-a recunoscut din descriere; un tip recunoscut (comision, TVA…) rămâne al regulii.
            if rez["status"] == "rosu" and not t.get("tip_detectat"):
                try:
                    from core import ai_incredere as _ai
                    sug = _ai.sugestie(conn, schema, ln.get("descriere") or "")
                    if sug:
                        cont_banca = "5121"
                        if ln["tip"] == "plata":
                            t["nota"] = {"debit": sug["cont"], "credit": cont_banca}
                        else:
                            t["nota"] = {"debit": cont_banca, "credit": sug["cont"]}
                        aloc["incredere"] = sug["incredere"]
                        aloc["motiv"] = aloc["motiv"] + f"; sugestie invatata: {sug['cont']} ({sug['incredere']}, {_cate(sug['validari'], 'validare', 'validări')})"
                except Exception as _e:
                    from core import observare as _obs
                    _obs.esec_secundar("sugestie invatata la importul extrasului", _e)   # înghițit, dar nu tăcut
            status = "potrivit" if rez["status"] in ("verde", "galben") else "nou"
            rezumat["potrivite" if status == "potrivit" else "fara_potrivire"] += 1
            cur.execute(f"""
                INSERT INTO {schema}.extras_linii
                  (data, descriere, suma, valuta, tip, cui_detectat, status,
                   alocari, nota_propusa, fisier_sursa, cont_extras, referinta)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            """, (ln["data"], ln["descriere"], ln["suma"], bool(t.get("valuta")),
                  ln["tip"], ln["cui"], status, json.dumps(aloc),
                  json.dumps(t.get("nota"), default=str) if t.get("nota") else None, fisier,
                  (cont or "").strip() or None, ln["referinta"]))
            out.append({"id": cur.fetchone()[0], "data": str(ln["data"]),
                        "descriere": ln["descriere"], "suma": str(ln["suma"]),
                        "tip": ln["tip"], "cui": ln["cui"], "status": status, **aloc})
    return {"linii": out, "deja": deja, "rezumat": rezumat}


def compara_solduri(conn, schema, sold_initial, sold_final):
    """[16.10.2026, lotul 6 pct.2b, 276] Soldurile din extras (MT940 `:60F:` / `:62F:`) față de contul băncii din contabilitate (5121, la
    valută 5124, cu analiticele) la aceeași zi: soldul de preluare + notele VALIDATE până la acea zi (`bilant_api.sold_la`). Liniile
    extrasului încă necontate apar ca diferență la soldul final — de-aia se arată amândouă. `None` la extrasele fără solduri (tabele).
    Contabilul vede `contabil = None` dacă ziua e dinaintea soldurilor de preluare (aplicația nu știe soldul de atunci)."""
    import datetime
    from psycopg2.extras import RealDictCursor as _RD
    from core import bilant_api as _ba
    if not (sold_initial or sold_final):
        return None
    valuta = (sold_initial or sold_final).get("valuta") or "RON"
    cont = _cont_banca(valuta != "RON")
    out = {"cont": cont, "valuta": valuta}
    with conn.cursor(cursor_factory=_RD) as cur:
        for nume, s in (("initial", sold_initial), ("final", sold_final)):
            if not s:
                out[nume] = None
                continue
            sl = _ba.sold_la(cur, schema, datetime.date.fromisoformat(s["data"]))
            contabil = (None if sl is None else
                        sum((d - c for k, (d, c) in sl.items() if k == cont or k.startswith(cont + ".")), Decimal("0")))
            extras = Decimal(str(s["suma"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            out[nume] = {"data": s["data"], "extras": str(extras), "contabil": None if contabil is None else str(contabil),
                         "diferenta": None if contabil is None else str(extras - contabil)}
    return out


def lista(conn, schema, status=None):
    """Liniile de extras cu detaliile facturilor alocate (pentru UI)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q = f"SELECT * FROM {schema}.extras_linii"
        # [05.10.2026, comanda Costin pct.8] liniile noi ale extrasului apar primele, nu sub cele vechi
        ordine = " ORDER BY creat_la DESC, data DESC, id DESC"
        if status:
            cur.execute(q + " WHERE status=%s" + ordine, (status,))
        else:
            cur.execute(q + ordine)
        linii = cur.fetchall()
        ids = set()
        for l in linii:
            for a in (l.get("alocari") or {}).get("alocari", []):
                ids.add(a["factura_id"])
        facturi = {}
        if ids:
            cur.execute(f"""SELECT id, numar, serie, data_emitere, tert_nume, tert_cui,
                            COALESCE(total_lei, total) AS total
                            FROM {schema}.facturi WHERE id = ANY(%s)""", (list(ids),))
            facturi = {f["id"]: f for f in cur.fetchall()}
        for l in linii:
            l["suma"] = str(l["suma"])
            l["data"] = str(l["data"])
            l["creat_la"] = str(l["creat_la"])
            for a in (l.get("alocari") or {}).get("alocari", []):
                f = facturi.get(a["factura_id"])
                if f:
                    a["factura"] = {"numar": f["numar"], "serie": f["serie"],
                                    "data": str(f["data_emitere"]),
                                    "tert": f["tert_nume"], "total": str(f["total"])}
        return linii


def conteaza(conn, schema, linie_id, alocari=None):
    """Contează o linie: câte o înregistrare per factură alocată.
    incasare: 5121/5124 = 4111; plata: 401 = 5121/5124.
    alocari=None → folosește alocările din matching."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.extras_linii WHERE id=%s", (linie_id,))
        l = cur.fetchone()
        if not l:
            return None
        if l["status"] == "contat":
            return {"eroare": "linia e deja contata"}
        aloc = alocari or (l.get("alocari") or {}).get("alocari", [])
        # [05.10.2026, comanda Costin pct.6] fiecare notă din extras poartă extrasul ca document justificativ
        from core import pdf_util as _pu
        doc = ("Extras bancar %s din %s" % (l["fisier_sursa"], _pu.data_ro(l["data"])) if l.get("fisier_sursa")
               else "Extras bancar din %s" % _pu.data_ro(l["data"]))
        if not aloc:
            np = l.get("nota_propusa") or {}
            if not (np.get("debit") and np.get("credit")):
                return {"eroare": "fără alocări și fără notă propusă; alege facturile"}
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                VALUES (%s,%s,'banca','ciorna',%s) RETURNING id
            """, (l["data"], (l["descriere"] or "")[:200] or "operatiune bancara", doc))
            iid = cur.fetchone()["id"]
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                VALUES (%s,%s,%s,%s)
            """, (iid, np["debit"], np["credit"], Decimal(str(np.get("suma") or l["suma"]))))
            cur.execute(f"UPDATE {schema}.extras_linii SET status='contat', alocari=%s WHERE id=%s",
                        (json.dumps({**(l.get("alocari") or {}), "inregistrari_ids": [iid]}), linie_id))
            # [05.10.2026, comanda Costin pct.8] se OPREȘTE aici. Înainte cădea în ramura alocărilor: fără alocări nu
            # scria nimic, rescria `inregistrari_ids` cu [] (legătura notei pierdută) și răspundea cu nota din tipul
            # liniei („Nota 401=5121 — 0 înregistrări create”) deși se crease 627=5121.
            return {"inregistrari": [iid], "nota": "%s=%s" % (np["debit"], np["credit"])}
        banca = _cont_banca(l["valuta"])
        debit, credit = (banca, CONT_CLIENTI) if l["tip"] == "incasare" else (CONT_FURNIZORI, banca)
        create = []
        for a in aloc:
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, factura_id, descriere, sursa, status, document_ref)
                VALUES (%s,%s,%s,'banca','ciorna',%s) RETURNING id
            """, (l["data"], a["factura_id"],
                  (l["descriere"] or "")[:200] or "operatiune bancara", doc))
            iid = cur.fetchone()["id"]
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                VALUES (%s,%s,%s,%s)
            """, (iid, debit, credit, Decimal(str(a["suma"]))))
            # [tvai_v1] TVA la incasare: exigibilitate la incasare/plata (art.282(3),(8))
            cur.execute(f"SELECT COALESCE(tva_la_incasare, false) AS b FROM {schema}.firma_profil WHERE id = 1")
            if (cur.fetchone() or {}).get("b"):
                from core import tva_incasare as _tv
                cur.execute(f"""SELECT f.directie, (SELECT cota_tva FROM {schema}.factura_linii
                                        WHERE factura_id = f.id LIMIT 1) AS cota
                                FROM {schema}.facturi f WHERE f.id = %s""", (a["factura_id"],))
                _f = cur.fetchone()
                if _f:
                    if _f["cota"] is None:
                        raise ValueError("factura fără cota TVA pe linii - TVA la încasare nu se "
                                         "poate calcula (declara cota pe factura)")
                    _tva = _tv.tva_din_incasare(a["suma"], _f["cota"])
                    if _tva > 0:
                        _deb, _cred = ("4428", "4427") if _f["directie"] == "emisa" else ("4426", "4428")
                        cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                        (inregistrare_id, cont_debit, cont_credit, suma)
                                        VALUES (%s,%s,%s,%s)""", (iid, _deb, _cred, _tva))
            create.append(iid)
        cur.execute(f"UPDATE {schema}.extras_linii SET status='contat', alocari=%s WHERE id=%s",
                    (json.dumps({**(l.get("alocari") or {}),
                                 "alocari": [{"factura_id": a["factura_id"], "suma": str(a["suma"])}
                                             for a in aloc],
                                 "inregistrari_ids": create}), linie_id))
    return {"inregistrari": create, "nota": f"{debit}={credit}"}


def facturi_deschise_detalii(conn, schema):
    """Facturile deschise cu detalii pentru picker-ul din UI."""
    fd = facturi_deschise(conn, schema)
    if not fd:
        return []
    ids = [f["id"] for f in fd]
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, numar, serie, tert_nume FROM {schema}.facturi WHERE id=ANY(%s)", (ids,))
        det = {r["id"]: r for r in cur.fetchall()}
    return [{"id": f["id"], "tert_cui": f["tert_cui"], "directie": f["directie"],
             "data_emitere": str(f["data_emitere"]), "sold": str(f["sold"]),
             "numar": det[f["id"]]["numar"], "serie": det[f["id"]]["serie"],
             "tert_nume": det[f["id"]]["tert_nume"]} for f in fd]
