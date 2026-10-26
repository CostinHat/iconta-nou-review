# -*- coding: utf-8 -*-
"""core/centre_cost_api.py — nomenclator centre de cost (F143 Faza 1).

Management accounting intern: centrul de cost e o DIMENSIUNE pe linia de nota
(inregistrari_linii.centru_cost_id), nu contabilitate bugetara publica. CRUD minimal
per firma. Stergerea nu se face (liniile istorice trimit la centru prin FK) - un centru
scos din uz se DEZACTIVEAZA (activ=false): ramane pe notele vechi, nu se mai ofera la note noi.

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from psycopg2.extras import RealDictCursor


def lista(conn, schema, doar_active=False):
    """Centrele firmei: [{id, nume, activ}]. doar_active=True -> doar cele oferibile la note noi."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q = f"SELECT id, nume, activ FROM {schema}.centre_cost"
        if doar_active:
            q += " WHERE activ = true"
        q += " ORDER BY activ DESC, nume"
        cur.execute(q)
        return [dict(r) for r in cur.fetchall()]


def adauga(conn, schema, nume):
    """Adauga un centru nou. Numele e unic (case-insensitive) ca sa nu se dubleze."""
    nume = (nume or "").strip()[:100]
    if not nume:
        return {"eroare": "numele centrului e obligatoriu"}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id FROM {schema}.centre_cost WHERE lower(nume) = lower(%s)", (nume,))
        if cur.fetchone():
            return {"eroare": "există deja un centru cu acest nume"}
        cur.execute(f"INSERT INTO {schema}.centre_cost (nume) VALUES (%s) RETURNING id", (nume,))
        cid = cur.fetchone()["id"]
    return {"ok": True, "id": cid}


def seteaza_activ(conn, schema, centru_id, activ):
    """Dezactiveaza/reactiveaza un centru (nu se sterge - FK de pe liniile istorice)."""
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {schema}.centre_cost SET activ = %s WHERE id = %s",
                    (bool(activ), centru_id))
        n = cur.rowcount
    return {"ok": True} if n else None


def _f(v):
    return round(float(v or 0), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5


def raport_realizat(conn, schema, de, pana):
    """Realizat pe centru de cost, perioada [de, pana], din note VALIDATE (nu ciorne).
    cheltuieli = rulajul net al clasei 6 (debit − credit); venituri = rulajul net al clasei 7 (credit − debit; [C119] debitul 707 = 4427
    al notei Raportului Z se scade) — fără închiderea în 121 (C15).
    Include si centrele fara activitate (0). Liniile fara centru nu intra pe centre, dar se
    raporteaza separat ca 'nealocat' (cat din cheltuieli/venituri nu e atribuit niciunui centru)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT cc.id, cc.nume, cc.activ,
                   (COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '6%%' AND i.id IS NOT NULL AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0) - COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '6%%' AND i.id IS NOT NULL AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0)) AS cheltuieli,
                   (COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '7%%' AND i.id IS NOT NULL AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0) - COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '7%%' AND i.id IS NOT NULL AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0)) AS venituri
            FROM {schema}.centre_cost cc
            LEFT JOIN {schema}.inregistrari_linii l ON l.centru_cost_id = cc.id
            LEFT JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
              AND i.status = 'validata' AND i.data BETWEEN %s AND %s
            GROUP BY cc.id, cc.nume, cc.activ
            ORDER BY cc.nume
        """, (de, pana))
        centre = []
        for r in cur.fetchall():
            ch, ve = _f(r["cheltuieli"]), _f(r["venituri"])
            centre.append({"id": r["id"], "nume": r["nume"], "activ": r["activ"],
                           "cheltuieli": ch, "venituri": ve, "net": round(ve - ch, 2)})  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
        # nealocat: linii de clasa 6/7 din note validate FARA centru (coverage)
        cur.execute(f"""
            SELECT (COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '6%%' AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0) - COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '6%%' AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0)) AS cheltuieli,
                   (COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '7%%' AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0) - COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '7%%' AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0)) AS venituri
            FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE l.centru_cost_id IS NULL AND i.status = 'validata' AND i.data BETWEEN %s AND %s
        """, (de, pana))
        nr = cur.fetchone()
    return {"centre": centre,
            "nealocat": {"cheltuieli": _f(nr["cheltuieli"]), "venituri": _f(nr["venituri"])}}


def seteaza_buget(conn, schema, centru_id, an, buget_cheltuieli, buget_venituri):
    """Upsert bugetul anual al unui centru (per clasa: cheltuieli + venituri). Un rand per
    (centru, an) - re-setarea inlocuieste. Sume >= 0."""
    from decimal import Decimal
    try:
        ch = Decimal(str(buget_cheltuieli or 0))
        ve = Decimal(str(buget_venituri or 0))
    except Exception:
        return {"eroare": "sume invalide"}
    if ch < 0 or ve < 0:
        return {"eroare": "bugetul nu poate fi negativ"}
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM {schema}.centre_cost WHERE id = %s", (centru_id,))
        if not cur.fetchone():
            return None
        # upsert-ok: editare buget centru de cost pe (centru,an) - re-scriere intentionata
        cur.execute(f"""INSERT INTO {schema}.bugete
                        (centru_cost_id, an, buget_cheltuieli, buget_venituri)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (centru_cost_id, an) DO UPDATE
                        SET buget_cheltuieli = EXCLUDED.buget_cheltuieli,
                            buget_venituri = EXCLUDED.buget_venituri""",
                    (centru_id, an, ch, ve))
    return {"ok": True}


def raport_varianta(conn, schema, an):
    """Buget vs realizat pe an, per centru. Realizat = note VALIDATE pe tot anul (clasele 6/7).
    Include toate centrele (buget 0 daca nesetat). Abaterea o interpreteaza UI (la cheltuieli
    depasirea e rea, la venituri e buna)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT cc.id, cc.nume, cc.activ,
                   COALESCE(b.buget_cheltuieli, 0) AS buget_cheltuieli,
                   COALESCE(b.buget_venituri, 0) AS buget_venituri,
                   (COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '6%%' AND i.id IS NOT NULL AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0) - COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '6%%' AND i.id IS NOT NULL AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0)) AS realizat_cheltuieli,
                   (COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '7%%' AND i.id IS NOT NULL AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0) - COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '7%%' AND i.id IS NOT NULL AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'), 0)) AS realizat_venituri
            FROM {schema}.centre_cost cc
            LEFT JOIN {schema}.bugete b ON b.centru_cost_id = cc.id AND b.an = %s
            LEFT JOIN {schema}.inregistrari_linii l ON l.centru_cost_id = cc.id
            LEFT JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
              AND i.status = 'validata' AND i.data BETWEEN %s AND %s
            GROUP BY cc.id, cc.nume, cc.activ, b.buget_cheltuieli, b.buget_venituri
            ORDER BY cc.nume
        """, (an, f"{an}-01-01", f"{an}-12-31"))
        centre = []
        for r in cur.fetchall():
            bch, bve = _f(r["buget_cheltuieli"]), _f(r["buget_venituri"])
            rch, rve = _f(r["realizat_cheltuieli"]), _f(r["realizat_venituri"])
            centre.append({
                "id": r["id"], "nume": r["nume"], "activ": r["activ"],
                "buget_cheltuieli": bch, "realizat_cheltuieli": rch,
                "buget_venituri": bve, "realizat_venituri": rve,
                "net_buget": round(bve - bch, 2), "net_realizat": round(rve - rch, 2),  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            })
    return {"an": an, "centre": centre}


# ============================================================
#  [lotul 13, deficiența 536] Centrul pe documentele contate automat
# ============================================================
# Comanda Costin 13.1, 536, verbatim: „Centrul se pune doar pe notele manuale; tot ce se contează automat (facturi, NIR, salarii, amortizare)
# iese «nealocat» […] Centrul se poate pune pe liniile facturilor, NIR-urilor, salariilor și pe mijloacele fixe (amortizarea moștenește
# centrul activului).” Centrul e o dimensiune a rândului de VENIT / CHELTUIALĂ (clasele 6 / 7 — raportul le citește numai pe ele): pe
# rândurile de TVA, terți sau stoc nu are ce căuta, iar închiderea în 121 nu e rulaj (C15).

MESAJ_CENTRU_INEXISTENT = ("Centrul de cost ales nu există sau a fost dezactivat. Alege un centru activ din listă, sau lasă rândul fără "
                           "centru.")


def e_rand_de_centru(debit, credit):
    """True dacă rândul de notă (debit = credit) e unul de venit / cheltuială pe care centrul îl poartă: o latură în clasa 6 sau 7, niciuna
    în 121 (închiderea nu e rulaj, C15)."""
    d, c = str(debit or ""), str(credit or "")
    return (d[:1] in ("6", "7") or c[:1] in ("6", "7")) and not (d.startswith("121") or c.startswith("121"))


def _id_centru(v):
    """Valoarea trimisă de ecran -> id-ul centrului sau None (gol / 0 = fără centru); altceva decât un întreg pozitiv -> ValueError."""
    if v in (None, "", 0, "0"):
        return None
    n = int(v)
    if n <= 0:
        raise ValueError(v)
    return n


def centre_gresite(cur, schema, valori):
    """{valoarea trimisă} care nu e un centru ACTIV al firmei (inexistent, dezactivat, sau nu e un număr). Golul nu e greșit."""
    ids, rele = set(), set()
    for v in valori:
        try:
            n = _id_centru(v)
        except (TypeError, ValueError):
            rele.add(v)
            continue
        if n is not None:
            ids.add(n)
    if ids:
        cur.execute(f"SELECT id FROM {schema}.centre_cost WHERE activ = true AND id = ANY(%s)", (sorted(ids),))
        bune = {(r["id"] if isinstance(r, dict) else r[0]) for r in cur.fetchall()}
        rele |= ids - bune
    return rele


def campuri_centru_gresit(cur, schema, centre, camp):
    """[(camp(i), mesaj)] pentru fiecare linie al cărei centru nu e un centru activ (`camp` = i -> id-ul câmpului de pe ecran)."""
    rele = centre_gresite(cur, schema, centre or [])
    return [(camp(i), MESAJ_CENTRU_INEXISTENT) for i, v in enumerate(centre or []) if _str_in(v, rele)]


def _str_in(v, rele):
    return any(str(v) == str(r) for r in rele)


def centru_valoare(v):
    """Centrul de scris în bază: id-ul, sau None (după ce `centre_gresite` a respins ce nu e bun)."""
    return _id_centru(v)


def alocari(conn, schema):
    """Ce poartă azi un centru, pentru ecranul Centre de cost: salariații în serviciu și mijloacele fixe active, fiecare cu centrul lui."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, trim(coalesce(nume, '') || ' ' || coalesce(prenume, '')) AS nume, centru_cost_id FROM {schema}.salariati "
                    "WHERE data_incetare IS NULL OR data_incetare >= current_date ORDER BY nume, prenume, id")
        sal = [dict(r) for r in cur.fetchall()]
        cur.execute(f"SELECT id, cod, denumire, centru_cost_id FROM {schema}.mijloace_fixe WHERE activ IS NOT false ORDER BY cod, denumire, id")
        mf = [dict(r) for r in cur.fetchall()]
        # [536 / NIR, decizia Costin (a)] articolele de stoc: ieșirea lor din gestiune (607 = 371 …) moștenește centrul articolului
        cur.execute(f"SELECT id, denumire, um, cont_stoc, centru_cost_id FROM {schema}.articole ORDER BY denumire, id")
        art = [dict(r) for r in cur.fetchall()]
    return {"salariati": sal, "mijloace": mf, "articole": art}


def seteaza_alocari(conn, schema, salariati=None, mijloace=None, articole=None):
    """Pune centrul pe salariați, pe mijloacele fixe și pe articolele de stoc: {id: centru | None}. Un centru inactiv / inexistent se
    refuză lângă rândul lui (`cc-sal-<id>` / `cc-mf-<id>` / `cc-art-<id>`), nimic scris. Notele deja scrise rămân cum sunt; centrul se vede
    pe notele generate de acum."""
    grupe = (("salariati", "sal", dict(salariati or {})), ("mijloace_fixe", "mf", dict(mijloace or {})),
             ("articole", "art", dict(articole or {})))
    with conn.cursor() as cur:
        rele = centre_gresite(cur, schema, [v for _t, _p, alese in grupe for v in alese.values()])
        erori = [{"camp": "cc-%s-%s" % (pre, k), "mesaj": MESAJ_CENTRU_INEXISTENT}
                 for _t, pre, alese in grupe for k, v in alese.items() if _str_in(v, rele)]
        if erori:
            return {"eroare": "Alocarea nu s-a salvat: " + MESAJ_CENTRU_INEXISTENT, "erori_campuri": erori}
        for tabel, _pre, alese in grupe:
            for k, v in alese.items():
                cur.execute(f"UPDATE {schema}.{tabel} SET centru_cost_id = %s WHERE id = %s", (_id_centru(v), int(k)))
    return {"ok": True, **{tabel if tabel != "mijloace_fixe" else "mijloace": len(alese) for tabel, _p, alese in grupe}}


def centrul_articolului(cur, schema, articol_id, debit, credit):
    """[536 / NIR, decizia Costin (a)] Centrul de pus pe rândul (debit = credit) al unei note de stoc: centrul articolului, numai pe un rând
    de venit / cheltuială (clasele 6 / 7) — pe 371 / 4426 / 401 nu. `schema` None = schema conexiunii."""
    if not articol_id or not e_rand_de_centru(debit, credit):
        return None
    cur.execute("SELECT centru_cost_id FROM %sarticole WHERE id = %%s" % (("%s." % schema) if schema else ""), (articol_id,))
    r = cur.fetchone()
    return (r["centru_cost_id"] if isinstance(r, dict) else r[0]) if r else None


def centrele_salariatilor(cur, schema):
    """{salariat_id: centru_cost_id} (numai cei cu centru)."""
    cur.execute(f"SELECT id, centru_cost_id FROM {schema}.salariati WHERE centru_cost_id IS NOT NULL")
    return {(r["id"] if isinstance(r, dict) else r[0]): (r["centru_cost_id"] if isinstance(r, dict) else r[1]) for r in cur.fetchall()}
