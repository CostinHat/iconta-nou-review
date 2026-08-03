# -*- coding: utf-8 -*-
"""
core/d301_operatiuni_api.py — introducerea operatiunilor pentru D301 (Decont special TVA).

Geaman cu d390_clasificare_api: grila lunara + adaugare + stergere, delegate din rute cu
cere_cabinet. D301 se introduce manual (achizitii intracomunitare / taxare inversa la
neinregistrati normal) — nu exista factura sau nomenclator de produse in spate.

FISCAL:
  - baza = val_valuta x curs  (calc_baza din d301; ROTUNJITA la leu, formula oficiala).
    baza NU se stocheaza (nici tabela n-are coloana) — generatorul o recalculeaza.
  - tva  = rotund(baza x cota / 100).  tva SE STOCHEAZA: d301.calcul_d301 il CITESTE din DB,
    nu il recalculeaza (doar baza). Fara stocare -> tva=0 -> declaratie valida dar substantial
    gresita (falsul-verde). De aceea cota se alege la introducere si tva se persista.
  - Cota vine din common.cota('tva_standard', <data perioadei>) — PERIOD-AWARE (Legea 141/2025:
    21% din 01.08.2025, 19% inainte), nu constanta literala. Redusa (11%) si scutit (0%) sunt
    optiunile suplimentare; daca redusa capata valabilitate parametrizata, intra in common.COTE.
"""
import re
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

_DATA_DOC = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")   # ZZ.LL.AAAA (structura ANAF, poz.35 C(10) DA)
from core import common as _c
from core.d301 import TIPURI_OP, VALUTE, calc_baza

# Etichetele oficiale ale celor 5 tipuri (OPANAF 592/2016, formularul 301) — sursa UNICA,
# EXACT ca in formular; frontend-ul le randeaza, nu le rescrie.
TIPURI_ETICHETE = {
    1: "Achiziții intracomunitare de bunuri taxabile (altele decât mijloace de transport noi și produse accizabile)",
    2: "Achiziții intracomunitare de mijloace de transport NOI",
    3: "Achiziții intracomunitare de produse accizabile",
    4: "Operațiuni prevăzute la art. 307 alin. (2), (3), (5) și (6) Cod fiscal",
    5: "Achiziții de SERVICII intracomunitare, taxare inversă art. 307 alin. (2) — secțiunea 4.1",
}


def _r0(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def cote_perioada(an, luna):
    """Cotele TVA valabile in perioada, PERIOD-AWARE — standard SI redusa din common.cota,
    nu literal. CF art.291: standard alin.(1), redusa alin.(2); alin.(8) leaga cota achizitiei
    intracomunitare de cota livrarii interne a aceluiasi bun, deci redusa se aplica si in D301.
    Redusa era hardcodata 11 -> gresita pentru perioade dinainte de 01.08.2025 (atunci reducerile
    erau 9% si 5%; Legea 141/2025 le-a comasat in 11% de la 01.08.2025). Daca redusa nu e
    configurata pentru perioada, se OMITE optiunea — nu se ofera un 11% fals (care ar persista un
    tva eronat, fals-verde). Cele doua cote reduse istorice coexistente (9%/5%) cer remodelare
    COTE = decizie de produs, nerezolvata aici."""
    la = date(int(an), int(luna), 1)
    std, _temei = _c.cota("tva_standard", la)
    optiuni = [{"val": int(std * 100), "eticheta": "%d%% (standard)" % int(std * 100)}]
    try:
        red, _tr = _c.cota("tva_redusa", la)
        red_p = int(red * 100)
        optiuni.append({"val": red_p, "eticheta": "%d%% (redusă)" % red_p})
    except _c.PerioadaIndisponibila:
        pass  # redusa neconfigurata pentru perioada -> nu se ofera un 11% fals
    optiuni.append({"val": 0, "eticheta": "0% / scutit"})
    return optiuni


def _tva_din(val_valuta, curs, cota):
    baza = calc_baza(val_valuta, curs)
    return baza, _r0(Decimal(str(baza)) * Decimal(str(int(cota))) / Decimal(100))


def lista(conn, schema, an, luna):
    """Operatiunile lunii (cu baza si tva) + nomenclatoarele pt formular (o singura sursa)."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(f"SELECT id, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva "
                    f"FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        ops = []
        for r in cur.fetchall():
            baza = calc_baza(r["val_valuta"] or 0, r["curs"])
            ops.append({"id": r["id"], "tip": r["tip"],
                        "eticheta": TIPURI_ETICHETE.get(r["tip"], "Tip %s" % r["tip"]),
                        "nr_doc": r["nr_doc"] or "", "data_doc": r["data_doc"] or "",
                        "val_valuta": float(r["val_valuta"] or 0), "tip_valuta": r["tip_valuta"] or "",
                        "curs": float(r["curs"]), "baza": baza, "tva": _r0(r["tva"] or 0)})
    return {
        "operatiuni": ops,
        "tipuri": [{"val": t, "eticheta": TIPURI_ETICHETE[t]} for t in TIPURI_OP],
        "valute": sorted(VALUTE),
        "cote": cote_perioada(an, luna),
    }


def adauga(conn, schema, an, luna, d):
    """Valideaza si insereaza o operatiune. Calculeaza+stocheaza tva; NU stocheaza baza."""
    try:
        tip = int(d.get("tip"))
    except (TypeError, ValueError):
        return {"eroare": "tip lipsă sau invalid"}
    if tip not in TIPURI_OP:
        return {"eroare": "tip %r invalid (permise 1..5)" % tip}
    tip_valuta = (d.get("tip_valuta") or "").strip().upper()
    if tip_valuta not in VALUTE:
        return {"eroare": "valuta %r neacceptată (nomenclator ANAF)" % tip_valuta}
    try:
        val_valuta = Decimal(str(d.get("val_valuta")))
        curs = Decimal(str(d.get("curs")))
        cota = int(d.get("cota"))
    except (TypeError, ValueError, ArithmeticError):
        return {"eroare": "valoare, curs sau cotă invalide"}
    if val_valuta <= 0:
        return {"eroare": "valoarea în valută trebuie să fie > 0"}
    if curs <= 0:
        return {"eroare": "cursul trebuie să fie > 0"}
    if cota not in {x["val"] for x in cote_perioada(an, luna)}:
        return {"eroare": "cota %r%% nepermisă pentru perioadă" % cota}
    nr_doc = (d.get("nr_doc") or "").strip()
    if not nr_doc:
        return {"eroare": "numărul documentului e obligatoriu"}
    # data_doc: obligatorie, format ANAF ZZ.LL.AAAA + dată calendaristică reală (structura poz.35).
    # DUKIntegrator respinge orice altceva ("data calendaristica eronata"): o validăm la sursă,
    # nu lăsăm formatul greșit să treacă și să producă un D301 respins.
    data_doc = (d.get("data_doc") or "").strip()
    if not _DATA_DOC.match(data_doc):
        return {"eroare": "data documentului e obligatorie în format ZZ.LL.AAAA (ex. 15.06.2026)"}
    try:
        zz, ll, aaaa = (int(x) for x in data_doc.split("."))
        date(aaaa, ll, zz)
    except (ValueError, TypeError):
        return {"eroare": "data documentului %r nu e o dată calendaristică validă" % data_doc}
    baza, tva = _tva_din(val_valuta, curs, cota)
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.d301_operatiuni
                        (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva))
        oid = cur.fetchone()[0]
    conn.commit()
    return {"ok": True, "id": oid, "baza": baza, "tva": tva}


def sterge(conn, schema, an, luna, op_id):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.d301_operatiuni WHERE id=%s AND an=%s AND luna=%s",
                    (op_id, an, luna))
        ok = cur.rowcount > 0
    conn.commit()
    return {"ok": ok}
