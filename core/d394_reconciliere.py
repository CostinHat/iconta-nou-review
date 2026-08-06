"""
core/d394_reconciliere.py — A DOUA CALE D394 (gard de continut, 05.08.2026).

CAMPANIA GARDUL DE CONTINUT, pas 2/6. Acelasi TIPAR ca D300 (core/d300_reconciliere.py):
recalcul INDEPENDENT al totalurilor pe cota din liniile brute, confruntat cu generatorul;
divergenta = HARD-BLOCK (ridica exceptie) care numeste AMBELE valori, NU repara tacit
(DECIZII 05.08, tipar pentru toate cele 6 declaratii).

DE CE NU "reconciliere incrucisata D394<->D300": doua motive descoperite la sursa (05.08):
  1. TAUTOLOGIE: gardul existent test_d300_d394_paritate confrunta calcul_d300 vs calcul_d394,
     dar AMBELE citesc aceleasi factura_linii si deduc cota la fel — propriul lui docstring o
     spune ("sursa e comuna (liniile)"). Nu e cale incrucisata, e aceeasi cale de doua ori;
     prinde doar DRIFTUL intre generatoare, nu un bug comun de agregare.
  2. NU E EGALITATE: D300 colectat >= D394 livrari L pe cota (D300 e TVA TOTALA, D394 e
     subsetul raportabil), deci o confruntare pe egalitate ar da divergenta falsa. Reziduul
     structural o face inegalitate, nu egalitate — gard slab.
Deci calea 2 = recalcul propriu al rezumat2 D394 din liniile brute, self-contained, exact ca
la D300, care NU are niciuna din cele doua probleme.

CE CONFRUNTA: rezumat2 pe cota — colectat livrari (bazaL/tvaL) + achizitii (bazaA/tvaA, unde
achizitia cu taxare inversa C se pliaza pe A, ca in generator REZ2_MAPARE). Acestea sunt
TOTALURILE cu TVA ale D394. Poarta in d394.genereaza inainte de build_xml.

NON-TAUTOLOGIE (probata pe AST — test_d394_reconciliere): acest modul NU importa/foloseste
calcul_d394 / d394.pull / cota_standard / _int din core.d394. Isi trage singur facturile (SQL
propriu) si isi face singura clasificarea (emisa->L, primita RO->A, primita RO taxare-inversa
->C pliat pe A, intracom EXCLUS, cota 0 / N / V EXCLUSE) si agregarea. Un bug in agregarea/
clasificarea generatorului (factura scapata, livrare pusa la achizitii, semn inversat) apare ca
divergenta, fiindca cele doua cai nu impart codul.

LIMITA DECLARATA (GARZI cat.4):
  1. Acopera doar TOTALURILE CU TVA raportabile (L, A, C->A) din FACTURI. Tipurile cota-0 fara
     TVA (V livrare taxare inversa, N persoane fizice, LS/AS regim special) sunt prezenta/
     clasificare — DUK le pazeste structural, nu sunt sume de reconciliat.
  2. Operatiunile MANUALE (manual["operatiuni"]: bonuri, borderouri, AI/AS/LS) -> NEACOPERIT.
     AZI D394 nu are UI/tabela care sa le alimenteze (doar body-ul cererii b["manual"]); tot
     traficul real vine din facturi si e acoperit. Daca `manual` e nevid, reconcilierea se
     declara NEACOPERIT (nu alarma falsa).
  3. Eroare de INTRARE partajata (ambele cai citesc aceeasi linie gresita a contabilului) NU se
     prinde — raspunderea contabilului (CLAUDE.md §8).
  4. Cota unei facturi FARA linii e dedusa (total/tva, ori standardul perioadei la taxare
     inversa primita) identic de ambele cai -> o clasificare gresita acolo nu se prinde.

PRECONDITIE: conn pozitionat pe schema tenantului (acelasi contract ca d394.pull).
"""

import re
from decimal import Decimal, ROUND_HALF_UP

_NEDIGIT = re.compile(r"\D")


class ReconciliereD394(ValueError):
    """Cele doua cai nu se reconciliaza. Poarta ambele valori si campul divergent."""


def _q(d):
    """Rotunjire fiscala ARITMETICA la intreg (ROUND_HALF_UP). Autonoma fata de calea 1."""
    return int(Decimal(d).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _partener(cui_brut, platitor_tva):
    """Clasificare independenta (mirror pe clasifica_partener, fara a-l importa):
    'RO_TVA' | 'NEINREG' | 'STRAIN'. platitor_tva=False (RO cu CUI dar neplatitor) -> NEINREG."""
    raw = (cui_brut or "").strip().upper().replace(" ", "")
    if not raw:
        return "NEINREG"
    pref = raw[:2]
    if pref.isalpha() and pref != "RO":
        return "STRAIN"
    cif = _NEDIGIT.sub("", raw[2:] if pref == "RO" else raw)
    if not cif:
        return "NEINREG"
    if platitor_tva is False:
        return "NEINREG"
    return "RO_TVA"


def _cota_standard(an, luna):
    """Cota standard a perioadei din common.cota (infra partajata de citire a ratei la data,
    NU functia de agregare a generatorului). Pentru taxare inversa primita fara linii."""
    from core import common as _c
    from datetime import date as _dt
    v, _t = _c.cota("tva_standard", _dt(an, luna, 1))
    return int((Decimal(str(v)) * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _agrega_independent(conn, perioada, inceput, sfarsit):
    """Pull SQL PROPRIU al facturilor PERIOADEI [inceput, sfarsit) + clasificare + agregare proprie.
    Intoarce {cota: {'bazaL','tvaL','bazaA','tvaA'}} (intregi), doar cote > 0.
    [06.08.2026] Fereastra primita din reconciliaza (aliniata la perioada fiscala TVA), nu pe luna."""
    import psycopg2.extras as _E
    an, luna = perioada.an, perioada.luna
    q = ("SELECT f.id AS fid, f.directie AS directie, f.total AS total, f.tva AS tva, "
         "f.taxare_inversa AS ti, f.tert_cui AS tert_cui, f.tert_platitor_tva AS tert_ptva, "
         "c.cui AS c_cui, "
         "COALESCE(json_agg(json_build_object('cota', l.cota_tva, "
         "  'baza', ROUND(l.cantitate * l.pret_unitar, 2)) ORDER BY l.id) "
         "  FILTER (WHERE l.id IS NOT NULL), '[]') AS linii "
         "FROM facturi f "
         "LEFT JOIN clienti c ON c.id = f.client_id "
         "LEFT JOIN factura_linii l ON l.factura_id = f.id "
         "WHERE f.data_emitere >= %s AND f.data_emitere < %s "
         "  AND COALESCE(f.tip, 'factura') = 'factura' "
         "GROUP BY f.id, c.cui ORDER BY f.id")
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(q, (inceput.isoformat(), sfarsit.isoformat()))
        rows = cur.fetchall()

    acc = {}  # cota -> {'bazaL','tvaL','bazaA','tvaA'} in Decimal

    def add(bucket, cota, baza, tva):
        if cota <= 0:
            return
        r = acc.setdefault(cota, {"bazaL": Decimal(0), "tvaL": Decimal(0),
                                  "bazaA": Decimal(0), "tvaA": Decimal(0)})
        r["baza" + bucket] += Decimal(baza)
        r["tva" + bucket] += Decimal(tva)

    for r in rows:
        emisa = (r["directie"] == "emisa")
        ti = bool(r["ti"])
        cui = (r["c_cui"] if emisa else r["tert_cui"]) or r["c_cui"] or r["tert_cui"] or ""
        p = _partener(cui, r["tert_ptva"])
        # rutare pe bucketul rezumat2 (mirror tip_operatiune + REZ2_MAPARE, independent):
        if emisa:
            if ti:
                continue                 # V (livrare taxare inversa) - cota 0, nu e in rezumat2
            bucket = "L"                 # livrare taxabila catre oricine
        else:
            if p in ("NEINREG", "STRAIN"):
                continue                 # N (persoane fizice, cota 0) / intracom (D390) - excluse
            bucket = "A"                 # achizitie RO (A) sau taxare inversa RO (C) -> pliate pe A
        linii = r["linii"] or []
        pe_cota = {}
        for l in linii:
            if l.get("cota") is None or l.get("baza") is None:
                continue
            c = int(Decimal(str(l["cota"])))
            pe_cota[c] = pe_cota.get(c, Decimal(0)) + Decimal(str(l["baza"]))
        if pe_cota:
            for cota, baza in pe_cota.items():
                add(bucket, cota, baza, baza * Decimal(cota) / Decimal(100))
        else:
            total = Decimal(str(r["total"] or 0)); tva = Decimal(str(r["tva"] or 0))
            baza = total - tva
            if tva and baza:
                cota = int((tva / baza * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
                add(bucket, cota, baza, tva)   # non-TI fara linii: tva = cel stocat
            elif ti and not emisa:
                cota = _cota_standard(an, luna)   # taxare inversa primita fara linii: cota standard
                add(bucket, cota, total, total * Decimal(cota) / Decimal(100))
            # altfel: cota 0 -> nu intra in rezumat2

    return {cota: {k: _q(v) for k, v in r.items()} for cota, r in acc.items()}


def _confrunta(rezumat2, cale2):
    """Confrunta rezumat2 al generatorului cu recalculul. Intoarce lista divergentelor."""
    div = []
    cote = set(rezumat2) | set(cale2)
    for cota in sorted(cote):
        gen = rezumat2.get(cota, {})
        c2 = cale2.get(cota, {})
        for camp, eticheta in (("bazaL", "livrari baza"), ("tvaL", "livrari TVA"),
                               ("bazaA", "achizitii baza"), ("tvaA", "achizitii TVA")):
            g = int(gen.get(camp, 0) or 0)
            v = int(c2.get(camp, 0) or 0)
            if g != v:
                div.append({"cota": cota, "camp": camp, "eticheta": eticheta,
                            "generator": g, "cale2": v, "diferenta": g - v})
    return div


def reconciliaza(conn, perioada, res, manual=None):
    """Recalculeaza independent si confrunta. NU ridica - intoarce raportul.
    {"acoperit": bool, "motiv": str|None, "divergente": [...]}"""
    ops = (manual or {}).get("operatiuni") or []
    if ops:
        return {"acoperit": False, "divergente": [],
                "motiv": "manual['operatiuni'] nevid (%d op) - operatiuni ne-deductibile din facturi "
                         "(bonuri/borderouri/AI/AS/LS); calea 2 reconstruieste doar din facturi "
                         "(limita 2, GARZI cat.4)." % len(ops)}
    from core import common as _c  # [fix trim 06.08.2026]
    _inc, _sf = _c.fereastra_tva(perioada, _c.perioada_tva_tip(res.prof))
    cale2 = _agrega_independent(conn, perioada, _inc, _sf)
    div = _confrunta(res.rezumat2, cale2)
    return {"acoperit": True, "motiv": None, "divergente": div}


def verifica_reconciliere(conn, perioada, res, manual=None):
    """POARTA (hard-block): ridica ReconciliereD394 daca cele doua cai diverg. Numeste AMBELE
    valori. NU repara tacit nici o cale (tipar DECIZII 05.08)."""
    rap = reconciliaza(conn, perioada, res, manual)
    if rap["divergente"]:
        linii = "; ".join(
            "cota %d%% %s (%s): generator=%d vs cale2=%d (dif %d)" %
            (d["cota"], d["camp"], d["eticheta"], d["generator"], d["cale2"], d["diferenta"])
            for d in rap["divergente"])
        raise ReconciliereD394(
            "D394 A DOUA CALE: totalurile rezumat2 ale generatorului NU se reconciliaza cu "
            "recalculul independent din liniile brute. Divergente: %s. Declaratia NU se genereaza "
            "- gardul nu alege singur cine are dreptate; verifica agregarea si datele." % linii)
    return rap
