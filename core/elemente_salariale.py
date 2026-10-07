# -*- coding: utf-8 -*-
"""core/elemente_salariale.py — elementele VARIABILE ale salariului, pe salariat și pe lună (retest Costin 07.10 seara, S1).

Comanda, verbatim: „Adaugă prime, sporuri și ore suplimentare, pe salariat și pe lună. Intră în brut și în bazele CAS / CASS /
impozit și apar distinct în fluturaș și în compoziția netului. Valori introduse de contabil, fără preselecție.”

Temei: CF art.76 alin.(1) — „Sunt considerate venituri din salarii toate veniturile în bani și/sau în natură obținute … în baza
unui contract individual de muncă … indiferent de perioada la care se referă, de denumirea veniturilor ori de forma sub care ele
se acordă” -> prima, sporul și plata orelor suplimentare sunt venit din salarii: intră în brut și în bazele CAS (CF art.139),
CASS (CF art.157) și impozit (CF art.78), ca salariul de bază. Facilitatea de la salariul minim: OUG 89/2025 art.III alin.(1)
lit.b — „venitul brut realizat din salarii … astfel cum este definit la art. 76 alin. (1)-(3) … nu depășește nivelul de 4.300 lei
inclusiv” (4.600 din 1 iulie 2026) -> elementele variabile intră în venitul REALIZAT (`salarizare.calcul_salariu`).

Nimic nu e presupus: tipul se alege (fără implicit), suma și denumirea se scriu; la orele suplimentare se scriu și orele, iar
suma o calculează contabilul (sporul minim e în Codul muncii art.123 alin.(2) — „cel puțin 75%”; aplicația nu-l aplică în locul
lui). Luna cu D112 depusă nu se mai modifică (rectificativă), ca pontajul (`pontaj.seteaza`).
"""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from psycopg2.extras import RealDictCursor

TIPURI = {"prima": "Primă", "spor": "Spor", "ore_suplimentare": "Ore suplimentare"}


def _p(schema):
    return ('"%s".' % str(schema).strip('"')) if schema else ""


def _suma(v, nume):
    try:
        d = Decimal(str(v))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("%s: scrie o sumă în lei." % nume)
    if d <= 0:
        raise ValueError("%s: trebuie să fie mai mare ca 0." % nume)
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)   # aritmetic (CLAUDE.md „Rotunjire fiscală”)


def valideaza(corp):
    """Elementul cerut, verificat câmp cu câmp: întoarce (date, erori_campuri)."""
    er, d = [], {}
    tip = corp.get("tip")
    if tip not in TIPURI:
        er.append({"camp": "tip", "mesaj": "Alege tipul: primă, spor sau ore suplimentare."})
    d["tip"] = tip
    den = " ".join(str(corp.get("denumire") or "").split())
    if not den:
        er.append({"camp": "denumire", "mesaj": "Scrie ce este (ex.: prima de performanță) — apare așa pe fluturaș."})
    d["denumire"] = den[:120]
    try:
        d["suma"] = _suma(corp.get("suma"), "Suma")
    except ValueError as e:
        er.append({"camp": "suma", "mesaj": str(e)})
    d["ore"] = None
    if tip == "ore_suplimentare":
        try:
            d["ore"] = _suma(corp.get("ore"), "Orele suplimentare")
        except ValueError as e:
            er.append({"camp": "ore", "mesaj": str(e)})
    elif corp.get("ore") not in (None, ""):
        er.append({"camp": "ore", "mesaj": "Orele se scriu numai la orele suplimentare."})
    return d, er


def _d112_depusa(cur, tenant_id, an, luna):
    if tenant_id is None:
        return False
    cur.execute("SELECT 1 FROM public.declaratii_depuse WHERE tenant_id = %s AND an = %s AND luna = %s AND tip = 'd112' LIMIT 1",
                (tenant_id, an, luna))
    return cur.fetchone() is not None


COD_D112_DEPUSA = "D112_DEPUSA"
MESAJ_D112_DEPUSA = ("Elementele de salariu ale lunii %02d.%04d nu se mai modifică: D112 e deja depusă la ANAF. Corectează prin "
                     "rectificativă.")


def adauga(conn, schema, salariat_id, an, luna, corp, tenant_id=None):
    d, er = valideaza(corp)
    if er:
        return {"ok": False, "erori_campuri": er, "mesaj": "; ".join(x["mesaj"] for x in er)}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT 1 FROM {_p(schema)}salariati WHERE id = %s", (int(salariat_id),))
        if not cur.fetchone():
            return {"ok": False, "cod": "INEXISTENT", "mesaj": "Salariatul nu există."}
        if _d112_depusa(cur, tenant_id, an, luna):
            return {"ok": False, "cod": COD_D112_DEPUSA, "mesaj": MESAJ_D112_DEPUSA % (luna, an)}
        cur.execute(f"""INSERT INTO {_p(schema)}elemente_salariale (salariat_id, an, luna, tip, denumire, ore, suma)
                        VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (int(salariat_id), int(an), int(luna), d["tip"], d["denumire"], d["ore"], d["suma"]))
        return {"ok": True, "id": cur.fetchone()["id"]}


def sterge(conn, schema, salariat_id, element_id, tenant_id=None):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT an, luna FROM {_p(schema)}elemente_salariale WHERE id = %s AND salariat_id = %s",
                    (int(element_id), int(salariat_id)))
        r = cur.fetchone()
        if not r:
            return {"ok": False, "cod": "INEXISTENT", "mesaj": "Elementul de salariu nu există."}
        if _d112_depusa(cur, tenant_id, r["an"], r["luna"]):
            return {"ok": False, "cod": COD_D112_DEPUSA, "mesaj": MESAJ_D112_DEPUSA % (r["luna"], r["an"])}
        cur.execute(f"DELETE FROM {_p(schema)}elemente_salariale WHERE id = %s", (int(element_id),))
    return {"ok": True}


def luna_elementului(conn, schema, element_id):
    """(an, luna) ale elementului, sau None."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT an, luna FROM {_p(schema)}elemente_salariale WHERE id = %s", (int(element_id),))
        r = cur.fetchone()
    return (r[0], r[1]) if r else None


def lista_luna(conn, schema, an, luna, salariat_id=None):
    """{salariat_id: [{id, tip, eticheta_tip, denumire, ore, suma}]} — o singură citire (statul, D112, nota, fluturașul)."""
    cond, val = "an = %s AND luna = %s", [int(an), int(luna)]
    if salariat_id is not None:
        cond += " AND salariat_id = %s"
        val.append(int(salariat_id))
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, salariat_id, tip, denumire, ore, suma FROM {_p(schema)}elemente_salariale WHERE {cond} "
                    "ORDER BY salariat_id, id", val)
        out = {}
        for r in cur.fetchall():
            out.setdefault(r["salariat_id"], []).append({
                "id": r["id"], "tip": r["tip"], "eticheta_tip": TIPURI.get(r["tip"], r["tip"]), "denumire": r["denumire"],
                "ore": str(r["ore"]) if r["ore"] is not None else None, "suma": str(r["suma"])})
    return out


def total(elemente):
    """Suma elementelor unui salariat (lista din `lista_luna`), ca Decimal."""
    return sum((Decimal(e["suma"]) for e in elemente or []), Decimal("0"))
