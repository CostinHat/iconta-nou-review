"""
core/d406_reconciliere.py — A DOUA CALE D406/SAF-T (gard de continut, 05.08.2026, pas 4/6).

Acelasi TIPAR ca D300/D394/D112. D406 e o declaratie de EVIDENTA (GeneralLedgerEntries =
notele contabile). Calea 2 construieste o BALANTA DE RULAJE per cont INDEPENDENTA din
inregistrari_linii (SQL propriu) si o leaga de totalurile per-cont din SAF-T-ul emis (res.note),
plus invariantul dublei partide Σdebit == Σcredit. Divergenta = HARD-BLOCK care numeste contul
si AMBELE valori; NU repara tacit (tipar DECIZII 05.08).

CE PRINDE: emisie care pierde/dubleaza o nota sau o linie (ex. bug-ul ISTORIC 16.07 -
<GeneralLedgerEntries> ramanea GOL pentru orice firma printr-un except:pass tacit -> calea 2 ar
fi gasit notele in DB si ar fi strigat); linie mapata pe contul gresit; dezechilibru la emisie.

NON-TAUTOLOGIE (probata pe AST): NU importa/foloseste d406.pull / construieste / _generalledger.
Isi trage singura liniile brute (inregistrari_linii, SQL propriu) si isi face singura balanta;
res.note se citeste ca DATE de verificat (ce a emis generatorul), nu ca sursa de calcul.

LIMITA DECLARATA (GARZI cat.4):
  - Acopera GeneralLedgerEntries (dubla partida a NOTELOR): Σdebit=Σcredit + balanta de rulaje per
    cont legata de inregistrari_linii. NU acopera sub-sectiunile SalesInvoices / PurchaseInvoices /
    Payments / Assets / MovementOfGoods - alt gard (reconcilierea linii-antet D406 exista deja
    partial pentru facturi, GARZI cat.4).
  - Σdebit=Σcredit e in mare parte STRUCTURAL (fiecare inregistrari_linii = debit+credit egale prin
    constructie); valoarea reala e legarea per-cont la rulajul independent (prinde drop/dubla/mapare
    gresita la EMISIE), plus confirmarea ca emisia nu a dezechilibrat.
  - Eroare de INTRARE partajata (ambele cai citesc aceeasi linie gresita) NU se prinde - §8.

PRECONDITIE: conn pozitionat pe schema tenantului (contractul d406.pull).
"""

from decimal import Decimal


class ReconciliereD406(ValueError):
    """SAF-T nu se leaga de balanta de rulaje independenta, sau dubla partida e dezechilibrata."""


def _q2(x):
    return Decimal(x).quantize(Decimal("0.01"))


def _rulaje_independente(conn, schema, an, luna):
    """Balanta de RULAJE per cont din inregistrari_linii — SQL PROPRIU (independent de d406.pull).
    Fereastra si filtrul = contractul d406 (note VALIDATE, `i.data` in FEREASTRA RAPORTARII).
    Fiecare linie (cont_debit, cont_credit, suma): debit pe cont_debit, credit pe cont_credit.

    [R165, 05.09.2026] Fereastra nu mai e luna-ancora, ci PERIOADA FISCALA TVA — ca in D406.
    Se ia din `common`, unde e definita o singura data, si NU din `d406`: garda
    `test_non_tautologie` interzice celei de-a doua cai sa importe generatorul, si are
    dreptate — o cale care isi ia codul din cea pe care o verifica nu mai verifica nimic. Dar
    nici o a doua definitie a ferestrei nu se poate scrie: divergenta lor tacuta E defectul
    R165. De-aia regula sta intr-un al treilea loc, neutru. SQL-ul ramane al ei — independenta
    celei de-a doua cai e in CALCUL, nu in perioada."""
    from core.common import fereastra_d406 as _fd
    with conn.cursor() as _c:
        _c.execute("SELECT platitor_tva, tip_decont FROM firma_profil WHERE id = 1")
        _r = _c.fetchone()
    _prof = {"platitor_tva": _r[0], "tip_decont": _r[1]} if _r else {}
    _di, _ds = _fd(_prof, an, luna)
    di, ds = _di.isoformat(), _ds.isoformat()
    q = ("SELECT l.cont_debit AS cd, l.cont_credit AS cc, l.suma AS suma "
         "FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
         "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s")
    deb, cred = {}, {}
    with conn.cursor() as cur:
        cur.execute(q, (di, ds))
        for cd, cc, suma in cur.fetchall():
            s = Decimal(str(suma or 0))
            if cd:
                deb[cd] = deb.get(cd, Decimal(0)) + s
            if cc:
                cred[cc] = cred.get(cc, Decimal(0)) + s
    return deb, cred


def _rulaje_saft(res):
    """Balanta de rulaje per cont din SAF-T EMIS (res.note - GeneralLedgerEntries)."""
    deb, cred = {}, {}
    for n in res.note:
        for l in n.linii:
            if not l.cont:
                continue
            if l.debit:
                deb[l.cont] = deb.get(l.cont, Decimal(0)) + Decimal(l.debit)
            if l.credit:
                cred[l.cont] = cred.get(l.cont, Decimal(0)) + Decimal(l.credit)
    return deb, cred


def reconciliaza(conn, schema, an, luna, res):
    """NU ridica. {"divergente":[...], "dezechilibru": {...}|None}."""
    d_ind, c_ind = _rulaje_independente(conn, schema, an, luna)
    d_saft, c_saft = _rulaje_saft(res)
    divergente = []
    for latura, ind, saft in (("debit", d_ind, d_saft), ("credit", c_ind, c_saft)):
        for cont in sorted(set(ind) | set(saft)):
            gi, gs = _q2(ind.get(cont, 0)), _q2(saft.get(cont, 0))
            if gi != gs:
                divergente.append({"cont": cont, "latura": latura,
                                   "saft": gs, "cale2": gi, "diferenta": gs - gi})
    sdeb = _q2(sum(d_saft.values(), Decimal(0)))
    scred = _q2(sum(c_saft.values(), Decimal(0)))
    dezechilibru = None
    if sdeb != scred:
        dezechilibru = {"debit": sdeb, "credit": scred, "diferenta": sdeb - scred}
    return {"divergente": divergente, "dezechilibru": dezechilibru}


def verifica_reconciliere(conn, schema, an, luna, res):
    """POARTA (hard-block): ridica ReconciliereD406 daca SAF-T nu se leaga de rulajul independent
    SAU daca dubla partida e dezechilibrata. Numeste contul si AMBELE valori. NU repara tacit."""
    rap = reconciliaza(conn, schema, an, luna, res)
    parti = []
    if rap["dezechilibru"]:
        d = rap["dezechilibru"]
        parti.append("DEZECHILIBRU dubla partida in SAF-T: Sdebit=%s vs Scredit=%s (dif %s)"
                     % (d["debit"], d["credit"], d["diferenta"]))
    if rap["divergente"]:
        det = "; ".join("cont %s %s: saft=%s vs cale2=%s (dif %s)" %
                        (x["cont"], x["latura"], x["saft"], x["cale2"], x["diferenta"])
                        for x in rap["divergente"][:20])
        supl = "" if len(rap["divergente"]) <= 20 else " (+%d)" % (len(rap["divergente"]) - 20)
        parti.append("BALANTA per cont (SAF-T vs rulaje independente din inregistrari_linii): " + det + supl)
    if parti:
        raise ReconciliereD406(
            "D406 A DOUA CALE: %s. Declaratia NU se genereaza - gardul nu alege singur cine are "
            "dreptate; verifica emisia GeneralLedgerEntries si notele." % " | ".join(parti))
    return rap
