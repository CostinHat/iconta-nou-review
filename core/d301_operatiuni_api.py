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
    # Cotele reduse VALABILE la data, din registru (period-aware). Post 01.08.2025: una singura
    # comasata (tva_redusa=11%). Pre: 9% (art.291 alin.2) SI 5% (art.291 alin.3) coexistente. Se
    # interogheaza toate cheile reduse si se deduplica pe valoare (dupa comasare toate dau 11%).
    vazute = set()
    for cheie in ("tva_redusa", "tva_redusa_9", "tva_redusa_5"):
        try:
            red, _tr = _c.cota(cheie, la)
        except (_c.PerioadaIndisponibila, ValueError):
            continue  # cota neconfigurata / in afara valabilitatii pt perioada -> nu se ofera fals
        red_p = int(red * 100)
        if red_p not in vazute:
            vazute.add(red_p)
            optiuni.append({"val": red_p, "eticheta": "%d%% (redusă)" % red_p})
    optiuni.append({"val": 0, "eticheta": "0% / scutit"})
    return optiuni


def _tva_din(val_valuta, curs, cota):
    baza = calc_baza(val_valuta, curs)
    return baza, _r0(Decimal(str(baza)) * Decimal(str(int(cota))) / Decimal(100))


def lista(conn, schema, an, luna):
    """Operatiunile lunii (cu baza si tva) + nomenclatoarele pt formular (o singura sursa)."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        # [confirmare per-furnizor 18.08.2026] Un furnizor (tara+cod) confirmat "local" pe ORICE operatiune
        # (orice luna) => viitoarele operatiuni de la el nu mai primesc indiciul de mis-clasificare - nu
        # re-confirmi lunar acelasi furnizor de gaz/energie. Derivat din confirmarile per-operatiune existente,
        # fara tabel separat. Se interogheaza INAINTE de SELECT-ul principal (acelasi cursor).
        cur.execute(f"SELECT DISTINCT partener_tara, partener_cod FROM {schema}.d301_operatiuni "
                    f"WHERE d390_confirmat_local = true AND coalesce(partener_cod, '') <> ''")
        # .get() defensiv: robust daca un rand nu poarta cheile (ex. cursor mock din teste); WHERE filtreaza real.
        _furnizori_conf = {(r.get("partener_tara") or "", r.get("partener_cod") or "")
                           for r in cur.fetchall() if (r.get("partener_cod") or "").strip()}
        cur.execute(f"SELECT id, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva, "
                    f"partener_tara, partener_cod, partener_den, d390_confirmat_local "
                    f"FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        ops = []
        for r in cur.fetchall():
            baza = calc_baza(r["val_valuta"] or 0, r["curs"])
            _codD = {1: "A", 3: "A", 5: "S"}.get(r["tip"])
            ops.append({"id": r["id"], "tip": r["tip"],
                        "eticheta": TIPURI_ETICHETE.get(r["tip"], "Tip %s" % r["tip"]),
                        "nr_doc": r["nr_doc"] or "", "data_doc": r["data_doc"] or "",
                        "val_valuta": float(r["val_valuta"] or 0), "tip_valuta": r["tip_valuta"] or "",
                        "curs": float(r["curs"]), "baza": baza, "tva": _r0(r["tva"] or 0),
                        "partener_tara": r["partener_tara"] or "", "partener_cod": r["partener_cod"] or "",
                        "partener_den": r["partener_den"] or "",
                        # semnal UI: operatiune care ar apărea in D390 (cod A/S) dar nu are tara furnizor
                        "d390_cod": _codD, "d390_lipsa_furnizor": bool(_codD and not (r["partener_tara"] or "")),
                        # [mis-clasificare 18.08.2026] tip 4 cu COD TVA furnizor completat = suspect: codul
                        # exclude alin.(6) (furnizori neinregistrati) -> ramane gaz/energie (alin 3/5) SAU un
                        # SERVICIU IC (alin 2) gresit pus ca tip 4 (ar trebui tip 5 -> cod S in D390). Indiciu
                        # soft (nu certitudine: gazul poate avea si el furnizor inregistrat). Fals-pozitivul
                        # benign (gaz/energie legitim): contabilul confirma (d390_confirmat_local) -> se stinge.
                        "d390_confirmat_local": bool(r["d390_confirmat_local"]),
                        # furnizorul (tara+cod) a fost confirmat local pe alta operatiune -> mostenit
                        "d390_furnizor_confirmat": bool((r["partener_cod"] or "").strip()
                            and (r["partener_tara"] or "", r["partener_cod"] or "") in _furnizori_conf
                            and not r["d390_confirmat_local"]),
                        # indiciul apare doar daca NICI operatiunea, NICI furnizorul nu sunt confirmate
                        "d390_posibil_serviciu": bool(r["tip"] == 4 and (r["partener_cod"] or "").strip()
                            and not r["d390_confirmat_local"]
                            and (r["partener_tara"] or "", r["partener_cod"] or "") not in _furnizori_conf)})
    return {
        "operatiuni": ops,
        "tipuri": [{"val": t, "eticheta": TIPURI_ETICHETE[t]} for t in TIPURI_OP],
        "valute": sorted(VALUTE),
        "cote": cote_perioada(an, luna),
    }


def adauga(conn, schema, an, luna, d):
    """Valideaza si insereaza o operatiune. Calculeaza+stocheaza tva; NU stocheaza baza."""
    # [G10 rule2/4] colecteaza TOATE erorile de camp (nu fail-fast), field-keyed pt erori_campuri.
    erori = []
    try:
        tip = int(d.get("tip"))
    except (TypeError, ValueError):
        tip = None
    if tip is None:
        erori.append(("tip", "Tip lipsă sau invalid."))
    elif tip not in TIPURI_OP:
        erori.append(("tip", "Tip %r invalid (permise 1..5)." % tip))
    tip_valuta = (d.get("tip_valuta") or "").strip().upper()
    if tip_valuta not in VALUTE:
        erori.append(("valuta", "Valuta %r neacceptată (nomenclator ANAF)." % tip_valuta))
    val_valuta = curs = cota = None
    try:
        val_valuta = Decimal(str(d.get("val_valuta")))
        curs = Decimal(str(d.get("curs")))
        cota = int(d.get("cota"))
    except (TypeError, ValueError, ArithmeticError):
        erori.append(("val", "Valoare, curs sau cotă invalide."))
    if val_valuta is not None and val_valuta <= 0:
        erori.append(("val", "Valoarea în valută trebuie să fie > 0."))
    if curs is not None and curs <= 0:
        erori.append(("curs", "Cursul trebuie să fie > 0."))
    if cota is not None and cota not in {x["val"] for x in cote_perioada(an, luna)}:
        erori.append(("cota", "Cota %r%% nepermisă pentru perioadă." % cota))
    nr_doc = (d.get("nr_doc") or "").strip()
    if not nr_doc:
        erori.append(("nrdoc", "Numărul documentului e obligatoriu."))
    data_doc = (d.get("data_doc") or "").strip()
    if not _DATA_DOC.match(data_doc):
        erori.append(("datadoc", "Data documentului e obligatorie în format ZZ.LL.AAAA (ex. 15.06.2026)."))
    else:
        try:
            zz, ll, aaaa = (int(x) for x in data_doc.split("."))
            date(aaaa, ll, zz)
        except (ValueError, TypeError):
            erori.append(("datadoc", "Data documentului %r nu e o dată calendaristică validă." % data_doc))
    # [auto-derivare d301->D390, decizia Costin 18.08.2026] Furnizorul UE - OPTIONAL pe D301 (D301 nu-l cere),
    # dar necesar ca operatiunea sa apara AUTOMAT in D390 (cod A/S). tara: 2 litere ISO; cod: codul de TVA al
    # furnizorului fara prefix tara (poate lipsi = NOTA 1). Fara tara -> operatiunea nu intra in D390 (avertisment
    # la generare). Validam usor aici; checksum-ul VIES al codului il face D390 (checksum_vies) la generare.
    partener_tara = (d.get("partener_tara") or "").strip().upper()
    partener_cod = (d.get("partener_cod") or "").strip().upper()
    partener_den = (d.get("partener_den") or "").strip()
    if partener_tara and not re.match(r"^[A-Z]{2}$", partener_tara):
        erori.append(("partener_tara", "Țara furnizorului trebuie să fie codul din 2 litere (ex. DE, FR, IT)."))
    if partener_cod and not partener_tara:
        erori.append(("partener_tara", "Ai completat codul de TVA al furnizorului — completează și țara (2 litere)."))
    if len(partener_cod) > 20:
        erori.append(("partener_cod", "Codul de TVA al furnizorului e prea lung (max 20 caractere)."))
    if erori:
        return {"eroare": "; ".join(m for _c, m in erori),
                "erori_campuri": [{"camp": c, "mesaj": m} for c, m in erori]}
    baza, tva = _tva_din(val_valuta, curs, cota)
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.d301_operatiuni
                        (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva,
                         partener_tara, partener_cod, partener_den)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva,
                     partener_tara, partener_cod, partener_den))
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


def confirma_local(conn, schema, an, luna, op_id, valoare=True):
    """[mis-clasificare, fals-pozitiv benign 18.08.2026] Marcheaza o operatiune tip 4 ca CONFIRMATA
    legitima locala (NU serviciu IC) -> stinge indiciul 'poate e serviciu -> tip 5' pentru ea. Reversibil
    (valoare=False readuce indiciul). Doar tip 4 conteaza (indiciul apare doar acolo), dar setarea e permisa
    pe orice rand al perioadei (idempotent). Contabilul o foloseste pentru gaz/energie de la furnizor
    inregistrat (alin.3/5), care legitim nu intra in D390 desi are cod TVA."""
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {schema}.d301_operatiuni SET d390_confirmat_local=%s "
                    f"WHERE id=%s AND an=%s AND luna=%s", (bool(valoare), op_id, an, luna))
        ok = cur.rowcount > 0
    conn.commit()
    return {"ok": ok, "d390_confirmat_local": bool(valoare)}
