# -*- coding: utf-8 -*-
"""Registru-jurnal de încasări și plăți (OMFP 170/2015) + Fișa calcul D212.
Convenție: funcții (conn, schema, ...). Tot ce e generat automat = ciorna."""
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import d212_engine as _e

CATEGORII_INCASARE = {"activitate", "aport", "credit", "subventie", "alte_incasari"}
CATEGORII_PLATA = {"cheltuiala_deductibila", "cheltuiala_limitata",
                   "cheltuiala_nedeductibila", "aport_retragere", "rambursare_credit"}


def _fara_decimal(x):
    if isinstance(x, list):
        return [_fara_decimal(i) for i in x]
    if isinstance(x, dict):
        return {k: _fara_decimal(v) for k, v in x.items()}
    return str(x) if isinstance(x, Decimal) or hasattr(x, "isoformat") else x


def _valideaza(op):
    tip, cat = op.get("tip"), op.get("categorie")
    if tip not in ("incasare", "plata"):
        return "tip invalid"
    if op.get("metoda") not in ("numerar", "banca"):
        return "metoda invalida (numerar/banca)"
    if Decimal(str(op.get("suma", 0))) <= 0:
        return "suma trebuie să fie > 0"
    if not (op.get("data_operatiune") or "").strip():
        return "data operatiunii este obligatorie"
    if not (op.get("explicatie") or "").strip():
        return "explicatia este obligatorie (OMFP 170/2015)"
    cats = CATEGORII_INCASARE if tip == "incasare" else CATEGORII_PLATA
    if cat not in cats:
        return f"categorie invalida pentru {tip}"
    if tip == "plata" and cat.startswith("cheltuiala") and not op.get("deductibilitate"):
        return "deductibilitate obligatorie pentru cheltuieli"
    if op.get("valuta", "RON") != "RON" and (not op.get("suma_valuta") or not op.get("curs_valutar")):
        return "pentru valuta != RON: suma_valuta si curs_valutar obligatorii"
    return None


def lista(conn, schema, an, luna=None, status=None):
    where, params = ["EXTRACT(YEAR FROM data_operatiune)=%s"], [an]
    if luna:
        where.append("EXTRACT(MONTH FROM data_operatiune)=%s"); params.append(luna)
    if status:
        where.append("status=%s"); params.append(status)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT * FROM {schema}.rip_operatiuni
                        WHERE {' AND '.join(where)} ORDER BY data_operatiune, id""", params)
        rows = cur.fetchall()
    ti = sum(Decimal(str(r["suma"])) for r in rows if r["tip"] == "incasare")
    tp = sum(Decimal(str(r["suma"])) for r in rows if r["tip"] == "plata")
    return {"operatiuni": _fara_decimal(rows), "total_incasari": str(ti),
            "total_plati": str(tp), "sold": str(ti - tp)}


def adauga(conn, schema, op, user_id=None):
    err = _valideaza(op)
    if err:
        return {"eroare": err}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""INSERT INTO {schema}.rip_operatiuni
            (data_operatiune, tip, document_tip, document_numar, document_data, explicatie,
             suma, valuta, suma_valuta, curs_valutar, metoda, categorie, deductibilitate,
             status, creat_de)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'ciorna',%s) RETURNING id""",
            (op["data_operatiune"], op["tip"], op.get("document_tip"), op.get("document_numar"),
             op.get("document_data"), op["explicatie"].strip(), op["suma"],
             op.get("valuta", "RON"), op.get("suma_valuta"), op.get("curs_valutar"),
             op["metoda"], op["categorie"], op.get("deductibilitate"), user_id))
        rid = cur.fetchone()["id"]
    conn.commit()
    return {"id": rid, "status": "ciorna"}


def valideaza(conn, schema, op_id, user_id=None):
    with conn.cursor() as cur:
        cur.execute(f"""UPDATE {schema}.rip_operatiuni
                        SET status='validata', validat_de=%s, updated_at=now()
                        WHERE id=%s AND status='ciorna' RETURNING id""", (user_id, op_id))
        if not cur.fetchone():
            return {"eroare": "operațiune inexistentă sau deja validată"}
    conn.commit()
    return {"id": op_id, "status": "validata"}


def sterge(conn, schema, op_id):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.rip_operatiuni WHERE id=%s AND status='ciorna' RETURNING id", (op_id,))
        if not cur.fetchone():
            return {"eroare": "doar ciornele se pot șterge"}
    conn.commit()
    return {"sters": op_id}


def import_banca(conn, schema, an, luna, user_id=None):
    """Ciorne din extras_linii. sens: 'credit'=incasare, 'debit'=plata (core/banca.py).
    Idempotent pe banca_linie_id."""
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.rip_operatiuni
            (data_operatiune, tip, document_tip, explicatie, suma, metoda, categorie,
             deductibilitate, status, creat_de, banca_linie_id)
            SELECT el.data,
                   CASE WHEN el.tip='incasare' THEN 'incasare' ELSE 'plata' END,
                   'extras cont', COALESCE(NULLIF(el.descriere,''), 'operatiune bancara'),
                   ABS(el.suma), 'banca',
                   CASE WHEN el.tip='incasare' THEN 'activitate' ELSE 'cheltuiala_deductibila' END,
                   CASE WHEN el.tip='incasare' THEN NULL ELSE 'integral' END,
                   'ciorna', %s, el.id
            FROM {schema}.extras_linii el
            WHERE EXTRACT(YEAR FROM el.data)=%s AND EXTRACT(MONTH FROM el.data)=%s
              AND NOT EXISTS (SELECT 1 FROM {schema}.rip_operatiuni r WHERE r.banca_linie_id=el.id)
            RETURNING id""", (user_id, an, luna))
        n = len(cur.fetchall())
    conn.commit()
    return {"importate": n, "status": "ciorna",
            "nota": "categoriile/deductibilitatea propuse - de verificat de contabil"}


def import_casa(conn, schema, an, luna, user_id=None):
    """Ciorne din casa_operatiuni (coloane: data,tip,categorie,document,partener,suma).
    Idempotent pe casa_operatiune_id."""
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.rip_operatiuni
            (data_operatiune, tip, document_tip, document_numar, explicatie, suma,
             metoda, categorie, deductibilitate, status, creat_de, casa_operatiune_id)
            SELECT co.data, co.tip, 'document casa', co.document,
                   COALESCE(NULLIF(co.partener,''), REPLACE(co.categorie,'_',' ')),
                   co.suma, 'numerar',
                   CASE WHEN co.tip='incasare' THEN 'activitate' ELSE 'cheltuiala_deductibila' END,
                   CASE WHEN co.tip='incasare' THEN NULL ELSE 'integral' END,
                   'ciorna', %s, co.id
            FROM {schema}.casa_operatiuni co
            WHERE EXTRACT(YEAR FROM co.data)=%s AND EXTRACT(MONTH FROM co.data)=%s
              AND NOT EXISTS (SELECT 1 FROM {schema}.rip_operatiuni r WHERE r.casa_operatiune_id=co.id)
            RETURNING id""", (user_id, an, luna))
        n = len(cur.fetchall())
    conn.commit()
    return {"importate": n, "status": "ciorna"}


def fisa_d212(conn, schema, an, optiune_cas=False, optiune_cass=False):
    """Fisa calcul D212 din operatiunile VALIDATE, pe anul de venit `an`.

    [an_derivat 24.08.2026 — PRAG 1] Inainte: `if an != 2025: eroare`, iar plafoanele veneau din
    constanta `PLAFOANE_VENIT_2025`. Efectul pe o instalare din august 2026: butonul «Fisa D212» nu
    putea produce DECAT fisa anului trecut, pentru orice PFA — iar `PLAFOANE_VENIT_2026`, construit si
    VERIFICAT LA SURSA pe 03.08.2026 (Legea 239/2025 art.XII pct.19, CASS 72 sm in loc de 60), nu era
    chemat de nimeni. Capabilitate verificata si NELEGATA: aceeasi clasa cu R33.

    Refuzul RAMANE, dar pe motivul lui real — anii pentru care plafoanele sunt verificate la sursa
    (`d212_engine.ANI_VERIFICATI`). Nu se largeste dincolo de dovada: 2027 se refuza in continuare.
    """
    if an not in _e.ANI_VERIFICATI:
        return {"eroare": "plafoane verificate doar pentru venituri %s; "
                          "pentru alt an verifică întâi sursele oficiale"
                          % "/".join(str(a) for a in _e.ANI_VERIFICATI)}
    with conn.cursor() as cur:
        cur.execute(f"""SELECT
              COALESCE(SUM(suma) FILTER (WHERE tip='incasare' AND categorie='activitate'),0),
              COALESCE(SUM(suma) FILTER (WHERE tip='plata' AND categorie='cheltuiala_deductibila'),0),
              COALESCE(SUM(suma) FILTER (WHERE tip='plata' AND categorie='cheltuiala_limitata'),0)
            FROM {schema}.rip_operatiuni
            WHERE EXTRACT(YEAR FROM data_operatiune)=%s AND status='validata'""", (an,))
        vb, cd, cl = cur.fetchone()
        cur.execute(f"""SELECT COUNT(*) FROM {schema}.rip_operatiuni
                        WHERE EXTRACT(YEAR FROM data_operatiune)=%s AND status='ciorna'""", (an,))
        ciorne = cur.fetchone()[0]
    p = _e.plafoane_an(an)
    r = _e.calculeaza_d212(float(vb), float(cd), p, optiune_cas, optiune_cass)
    # anul si reperul PLEACA de la server: ecranul nu are de unde sa le stie (P3).
    r["an"] = an
    r["salariu_minim"] = p.salariu_minim
    r["cheltuieli_limitate_de_analizat"] = float(cl)
    r["ciorne_nevalidate"] = ciorne
    if cl or ciorne:
        r["avertisment"] = ("Cheltuielile limitate NU sunt in calcul - contabilul stabileste "
                            f"partea deductibila. {ciorne} ciorne neincluse.")
    return r


def registru_inventar(conn, schema, an):
    """Registrul-inventar (14-1-2/b): elemente de activ la 31.12.an.
    MF la valoare ramasa (liniar), disponibilitati = sold RIP validat cumulat pana la 31.12."""
    from datetime import date as _d
    ref = _d(an, 12, 31)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT id, cod, denumire, valoare, rezidual, dnf_luni, data_pif
                        FROM {schema}.mijloace_fixe WHERE activ AND data_pif <= %s""", (ref,))
        mf = []
        for r in cur.fetchall():
            luni = (ref.year - r["data_pif"].year) * 12 + (ref.month - r["data_pif"].month)
            luni = max(0, min(luni, r["dnf_luni"]))
            amortizabil = float(r["valoare"]) - float(r["rezidual"] or 0)
            amort = round(amortizabil * luni / r["dnf_luni"], 2) if r["dnf_luni"] else 0.0
            mf.append({"denumire": r["denumire"], "cod": r["cod"],
                       "valoare_intrare": float(r["valoare"]), "amortizare_cumulata": amort,
                       "valoare_ramasa": round(float(r["valoare"]) - amort, 2)})
        cur.execute(f"""SELECT
              COALESCE(SUM(suma) FILTER (WHERE tip='incasare'),0)
            - COALESCE(SUM(suma) FILTER (WHERE tip='plata'),0) AS sold
            FROM {schema}.rip_operatiuni
            WHERE status='validata' AND data_operatiune <= %s""", (ref,))
        disponibil = float(cur.fetchone()["sold"])
    total_mf = round(sum(m["valoare_ramasa"] for m in mf), 2)
    return {"an": an, "data_referinta": str(ref), "mijloace_fixe": mf,
            "total_mijloace_fixe": total_mf, "disponibilitati": round(disponibil, 2),
            "total_activ": round(total_mf + disponibil, 2)}
