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

Nimic nu e presupus: tipul se alege (fără implicit), suma și denumirea se scriu. Luna cu D112 depusă nu se mai modifică
(rectificativă), ca pontajul (`pontaj.seteaza`).

[lotul 13, deficiența 679, comanda Costin 13.1: „la orele suplimentare suma se calculează din ore × tarif orar × spor (cum s-a
calculat rândul existent, 497,16) și se arată, nu se cere”] La orele suplimentare contabilul scrie orele și sporul din contract;
suma o calculează aplicația: ore × tariful orar al salariului de bază × (100% + spor), la ban, aritmetic. Tariful orar = salariul de
bază al lunii / orele normei lunii (zilele lucrătoare × orele pe zi) — `tarif_orar`, același pe care îl arată statul. Temei (`anaf_surse/legea_53_2003_codul_muncii.txt`):
Codul muncii art.123 alin.(1) — „munca suplimentară va fi plătită salariatului prin adăugarea unui spor la salariu corespunzător duratei
acesteia”; alin.(2) — sporul „se stabilește prin negociere […] și nu poate fi mai mic de 75% din salariul de bază”; sub 75% aplicația
avertizează, nu refuză (sporul îl stabilește contractul). Exemplul din comandă: 5.000 lei / (22 × 8) = 28,409 lei/oră × 10 ore × 175% = 497,16 lei.
"""
import calendar
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from psycopg2.extras import RealDictCursor

TIPURI = {"prima": "Primă", "spor": "Spor", "ore_suplimentare": "Ore suplimentare"}
SPOR_MINIM = Decimal("75")   # Codul muncii art.123 alin.(2): sporul „nu poate fi mai mic de 75% din salariul de bază”
_BAN = Decimal("0.01")


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


def tarif_orar(cur, schema, salariat_id, an, luna):
    """Decimal (neprotunjit) sau None: salariul de bază al lunii / orele normei lunii (zile lucrătoare × ore pe zi). Sursa unică —
    statul de plată îl arată, iar suma orelor suplimentare se calculează din el."""
    from core import salariu_istoric as _si, scadente as _scad
    ultima = date(int(an), int(luna), calendar.monthrange(int(an), int(luna))[1])
    brut = _si.salariu_la(cur, schema or None, int(salariat_id), ultima)
    cur.execute(f"SELECT ore_zi FROM {_p(schema)}salariati WHERE id = %s", (int(salariat_id),))
    r = cur.fetchone()
    ore_zi = (r["ore_zi"] if isinstance(r, dict) else r[0]) if r else None
    zile = _scad.zile_lucratoare_luna(int(an), int(luna))
    if brut is None or Decimal(str(brut)) <= 0 or not zile:
        return None
    return Decimal(str(brut)) / (Decimal(zile) * Decimal(str(ore_zi or 8)))


def suma_ore_suplimentare(tarif, ore, spor_procent):
    """PURĂ. ore × tarif × (100% + spor), la ban, aritmetic (ROUND_HALF_UP, fără rotunjire intermediară a tarifului)."""
    return (Decimal(str(tarif)) * Decimal(str(ore)) * (Decimal(100) + Decimal(str(spor_procent))) / Decimal(100)).quantize(
        _BAN, rounding=ROUND_HALF_UP)


def spor_din_suma(tarif, ore, suma):
    """PURĂ. Sporul care rezultă dintr-o sumă scrisă de mână (rândurile de dinainte de 679, fără spor salvat): (suma / (tarif ×
    ore) − 1) × 100, la două zecimale. None dacă nu se poate (fără tarif sau ore)."""
    if not tarif or not ore or Decimal(str(ore)) <= 0:
        return None
    return ((Decimal(str(suma)) / (Decimal(str(tarif)) * Decimal(str(ore))) - 1) * 100).quantize(_BAN, rounding=ROUND_HALF_UP)


def valideaza(corp):
    """Elementul cerut, verificat câmp cu câmp: întoarce (date, erori_campuri). La orele suplimentare suma nu se cere: o calculează
    `adauga` din ore și spor (679)."""
    er, d = [], {}
    tip = corp.get("tip")
    if tip not in TIPURI:
        er.append({"camp": "tip", "mesaj": "Alege tipul: primă, spor sau ore suplimentare."})
    d["tip"] = tip
    den = " ".join(str(corp.get("denumire") or "").split())
    if not den:
        er.append({"camp": "denumire", "mesaj": "Scrie ce este (ex.: prima de performanță) — apare așa pe fluturaș."})
    d["denumire"] = den[:120]
    d["ore"] = d["spor_procent"] = d["suma"] = None
    if tip == "ore_suplimentare":
        try:
            d["ore"] = _suma(corp.get("ore"), "Orele suplimentare")
        except ValueError as e:
            er.append({"camp": "ore", "mesaj": str(e)})
        try:
            sp = Decimal(str(corp.get("spor_procent") if corp.get("spor_procent") not in (None, "") else "x"))
            if sp < 0:
                raise InvalidOperation
            d["spor_procent"] = sp.quantize(_BAN, rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError, TypeError):
            er.append({"camp": "spor", "mesaj": "Scrie sporul orelor suplimentare din contract, în procente (cel puțin 75%, Codul "
                                                "muncii art.123 alin.(2))."})
    else:
        try:
            d["suma"] = _suma(corp.get("suma"), "Suma")
        except ValueError as e:
            er.append({"camp": "suma", "mesaj": str(e)})
        if corp.get("ore") not in (None, ""):
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
        tarif = None
        if d["tip"] == "ore_suplimentare":   # [679] suma se calculează, nu se cere
            tarif = tarif_orar(cur, schema, salariat_id, an, luna)
            if tarif is None:
                return {"ok": False, "erori_campuri": [{"camp": "ore", "mesaj": "Salariatul nu are salariul de bază al lunii: "
                                                        "tariful orar nu se poate calcula (completează-l cu „Salariu”)."}],
                        "mesaj": "Salariatul nu are salariul de bază al lunii: tariful orar nu se poate calcula."}
            d["suma"] = suma_ore_suplimentare(tarif, d["ore"], d["spor_procent"])
        cur.execute(f"""INSERT INTO {_p(schema)}elemente_salariale (salariat_id, an, luna, tip, denumire, ore, suma, spor_procent)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (int(salariat_id), int(an), int(luna), d["tip"], d["denumire"], d["ore"], d["suma"], d["spor_procent"]))
        out = {"ok": True, "id": cur.fetchone()["id"], "suma": str(d["suma"])}
        if tarif is not None:
            out["tarif_orar"] = str(tarif.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
            if d["spor_procent"] < SPOR_MINIM:
                out["avertisment"] = ("Sporul de %s%% e sub 75%% din salariul de bază: Codul muncii art.123 alin.(2) nu permite mai "
                                      "puțin." % str(d["spor_procent"]).rstrip("0").rstrip("."))
        return out


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
        cur.execute(f"SELECT id, salariat_id, tip, denumire, ore, suma, spor_procent FROM {_p(schema)}elemente_salariale "
                    f"WHERE {cond} ORDER BY salariat_id, id", val)
        out = {}
        for r in cur.fetchall():
            out.setdefault(r["salariat_id"], []).append({
                "id": r["id"], "tip": r["tip"], "eticheta_tip": TIPURI.get(r["tip"], r["tip"]), "denumire": r["denumire"],
                "ore": str(r["ore"]) if r["ore"] is not None else None, "suma": str(r["suma"]),
                "spor_procent": str(r["spor_procent"]) if r["spor_procent"] is not None else None})
    return out


def cu_calculul(elemente, tarif):
    """[679] Rândurile de ore suplimentare primesc calculul afișat: tariful orar și sporul — cel salvat, sau, pe rândurile scrise înainte
    de 679 (fără spor salvat), cel care rezultă din suma scrisă (`spor_dedus`). Celelalte rânduri rămân neschimbate."""
    out = []
    for e in elemente or ():
        e = dict(e)
        if e.get("tip") == "ore_suplimentare" and tarif:
            e["tarif_orar"] = str(Decimal(str(tarif)).quantize(_BAN, rounding=ROUND_HALF_UP))
            if e.get("spor_procent") is None:
                sp = spor_din_suma(tarif, e.get("ore"), e.get("suma"))
                e["spor_procent"], e["spor_dedus"] = (str(sp) if sp is not None else None), True
        out.append(e)
    return out


def total(elemente):
    """Suma elementelor unui salariat (lista din `lista_luna`), ca Decimal."""
    return sum((Decimal(e["suma"]) for e in elemente or []), Decimal("0"))
