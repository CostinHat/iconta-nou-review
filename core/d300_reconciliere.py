"""
core/d300_reconciliere.py — A DOUA CALE D300 (gard de continut, 05.08.2026).

DE CE EXISTA: DUK valideaza STRUCTURA, nu semantica. O declaratie cu total GRESIT
dar structural valid trece azi. Golden din exemplu oficial ANAF nu se poate (nu
exista nicio declaratie ANAF completata cu cifre - verificat 05.08). Deci gardul
de continut = recalcul INDEPENDENT al totalurilor, confruntat cu generatorul.

CE FACE: isi trage SINGUR liniile brute de factura (SQL propriu), le agrega SINGUR
pe cote (Sigma(baza)xcota, rotunjire aritmetica ROUND_HALF_UP) si confrunta cu
randurile AUTOMATE ale generatorului (`res.R`): colectat R9/R10/R11 (21/11/9),
deductibil R22/R23 (21/11). O divergenta = EROARE VIZIBILA care numeste AMBELE
valori. Gardul NU alege singur cine are dreptate si NU repara tacit (cerinta Costin
05.08) - blocheaza generarea si cere verificare.

NON-TAUTOLOGIE (probata prin cod - vezi test_d300_reconciliere.test_non_tautologie_*):
acest modul NU importa si NU cheama `calcul_d300`, `_segmente`, `pull` sau `_int`
din `core.d300`. Importa doar Decimal + psycopg2. Cele doua cai NU impart codul de
agregare, deci un bug in agregarea generatorului (factura scapata din suma, cota
pusa in bucketul gresit, semn inversat) apare ca divergenta.

CE PRINDE:  factura pierduta din agregare/pull; cota mutata in bucketul gresit;
            semn inversat; dublare - orice face totalul generatorului sa difere de
            recalculul independent din liniile brute.
CE NU PRINDE (limita declarata, GARZI cat.4 "Iesire catre autoritati"):
  1. Randurile MANUALE (intracom, taxare inversa, ajustari) + orice rand atins prin
     `manual=` -> NEACOPERIT (sarit, nu alarma falsa).
  2. pro_rata si lantul R33->R42 (aritmetica determinista pe care DUK o verifica
     formula cu formula) - doar bazele+TVA pe cote intra aici.
  3. `tva_la_incasare`: exigibilitate pe DECONTARI, nu pe emitere -> NEACOPERIT
     explicit (recalculul pe emitere nu se aplica; nu produce divergenta falsa).
  4. Eroare de INTRARE partajata (ambele cai citesc aceeasi linie gresita a
     contabilului) - raspunderea contabilului (CLAUDE.md §8).
  5. Cota unei facturi FARA linii e dedusa (total/tva) identic de ambele cai -> o
     clasificare gresita acolo nu se prinde.

PRECONDITIE: conn e pozitionat pe schema tenantului (acelasi contract ca
`d300.pull` in calea non-tva_la_incasare, care nu seteaza search_path).
"""

from decimal import Decimal, ROUND_HALF_UP

# Randurile AUTOMATE derivate din facturi (aceleasi cote ca generatorul, dar
# maparea e re-declarata aici - nu se importa _LIVRARE_RAND/_ACHIZ_RAND din d300,
# ca sa nu existe cod comun cu calea 1).
_COLECTAT = {21: "R9", 11: "R10", 9: "R11"}     # livrari taxabile
_DEDUCTIBIL = {21: "R22", 11: "R23"}            # achizitii deductibile (9% e respins de DUK -> negardat aici)


class ReconciliereD300(ValueError):
    """Cele doua cai nu se reconciliaza. Poarta ambele valori si randul divergent."""


def _q(d):
    """Rotunjire fiscala ARITMETICA la intreg (ROUND_HALF_UP), ca in CLAUDE.md 'Rotunjire
    fiscala'. NU se importa din d300/numere - calea 2 e autonoma inclusiv pe rotunjire."""
    return int(Decimal(d).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _agrega_independent(conn, inceput, sfarsit):
    """Pull SQL PROPRIU + agregare proprie. Intoarce (col, ded) cu {cota: (baza_int, tva_int)}.
    Fereastra pe data_emitere [inceput, sfarsit) - contractul non-tva_la_incasare al D300."""
    import psycopg2.extras as _E
    q = ("SELECT f.id AS fid, f.directie AS directie, f.total AS total, f.tva AS tva, "
         "l.cantitate AS cant, l.pret_unitar AS pret, l.cota_tva AS cota "
         "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
         # [B1] fereastra pe EXIGIBILITATE (COALESCE(data_faptului_generator, data_emitere); avans->emitere), ca generatorul
         "WHERE (CASE WHEN f.tip_operatiune = 'avans' THEN f.data_emitere "
         "       ELSE COALESCE(f.data_faptului_generator, f.data_emitere) END) >= %s "
         "AND (CASE WHEN f.tip_operatiune = 'avans' THEN f.data_emitere "
         "     ELSE COALESCE(f.data_faptului_generator, f.data_emitere) END) < %s "
         "AND COALESCE(f.taxare_inversa, false) = false "  # [06.08.2026] taxare inversa -> rd.13 auto (nu col/ded), exclusa din cale2 ca in calcul_d300
         "AND COALESCE(f.tert_tara, 'RO') = 'RO' "  # [B1/F125] IC/export -> randuri proprii (rd.1/5/14/18 bunuri; rd.3/rd.7+rd.20 servicii reclasificate P/S in D390), in afara reconcilierii pe cote 21/11/9 (limita) - filtrul pe tert_tara le exclude coerent, ca la IC bunuri
         "AND COALESCE(f.status, 'emisa') NOT IN ('ciorna', 'de_preluat', 'descarcata', 'anulata', 'stornata') "  # [B1] doar facturi contabilizabile
         "AND NOT (f.directie = 'primita' AND COALESCE(f.furnizor_tva_incasare, false) = true) "  # [B1] deducere amanata la plata, in afara reconcilierii pe emitere (limita)
         "ORDER BY f.id")
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(q, (inceput.isoformat(), sfarsit.isoformat()))
        rows = cur.fetchall()

    # regrupez randurile SQL pe factura (LEFT JOIN -> N randuri/factura, sau 1 cu cant/cota NULL)
    inv = {}
    for r in rows:
        f = inv.setdefault(r["fid"], {"directie": r["directie"],
                                      "total": r["total"] if r["total"] is not None else 0,
                                      "tva": r["tva"] if r["tva"] is not None else 0,
                                      "linii": []})
        if r["cant"] is not None and r["pret"] is not None and r["cota"] is not None:
            f["linii"].append((r["cant"], r["pret"], r["cota"]))

    colb = {21: Decimal(0), 11: Decimal(0), 9: Decimal(0)}
    dedb = {21: Decimal(0), 11: Decimal(0)}
    for f in inv.values():
        emisa = (f["directie"] == "emisa")
        segmente = []  # (cota_int, baza_Decimal)
        if f["linii"]:
            for (cant, pret, cota) in f["linii"]:
                ci = int(round(float(cota)))  # ROTUNJIRE PE COTA (procent intreg RO 21/11/9/5/0): bancar==aritmetic, nu pe lei
                segmente.append((ci, Decimal(str(cant)) * Decimal(str(pret))))
        else:
            # factura fara linii: baza=total-tva, cota dedusa din raport (limita 5)
            baza = Decimal(str(f["total"])) - Decimal(str(f["tva"]))
            tva = Decimal(str(f["tva"]))
            ci = int(round(float(tva) / float(baza) * 100)) if (baza and tva) else None  # ROTUNJIRE PE COTA (procent dedus, nu lei): bancar==aritmetic
            if ci is not None:
                segmente.append((ci, baza))
        tinta = colb if emisa else dedb
        for (ci, baza) in segmente:
            if ci in tinta:
                tinta[ci] += baza

    col = {c: (_q(colb[c]), _q(colb[c] * Decimal(c) / Decimal(100))) for c in colb}
    ded = {c: (_q(dedb[c]), _q(dedb[c] * Decimal(c) / Decimal(100))) for c in dedb}
    return col, ded


def _confrunta(R, col, ded, manual_keys):
    """Confrunta randurile automate din res.R cu recalculul independent.
    Sare randurile atinse prin `manual=` (limita 1). Intoarce (divergente, sarite)."""
    divergente, sarite = [], []

    def cmp(rand, gen, cale2, eticheta):
        if rand in manual_keys:
            sarite.append(rand)
            return
        if gen != cale2:
            divergente.append({"rand": rand, "eticheta": eticheta,
                               "generator": gen, "cale2": cale2, "diferenta": gen - cale2})

    for cota, pre in _COLECTAT.items():
        cmp("%s_1" % pre, R.get("%s_1" % pre, 0), col[cota][0], "colectat %d%% baza" % cota)
        cmp("%s_2" % pre, R.get("%s_2" % pre, 0), col[cota][1], "colectat %d%% TVA" % cota)
    for cota, pre in _DEDUCTIBIL.items():
        cmp("%s_1" % pre, R.get("%s_1" % pre, 0), ded[cota][0], "deductibil %d%% baza" % cota)
        cmp("%s_2" % pre, R.get("%s_2" % pre, 0), ded[cota][1], "deductibil %d%% TVA" % cota)
    return divergente, sarite


def _deferred_activ(conn, inceput, sfarsit):
    """[B1] True daca exista deducere amanata (furnizor la incasare) cu PLATA (cont 401) validata in
    perioada - generatorul o include pe calea de plata; recon pe emitere n-o acopera (limita extinsa)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
            "JOIN facturi f ON f.id = i.factura_id "
            "WHERE i.status = 'validata' AND f.directie = 'primita' "
            "AND COALESCE(f.furnizor_tva_incasare, false) = true AND l.cont_debit = '401' "
            "AND i.data >= %s AND i.data < %s LIMIT 1", (inceput.isoformat(), sfarsit.isoformat()))
        return cur.fetchone() is not None


def reconciliaza(conn, perioada, res, manual=None):
    """Recalculeaza independent si confrunta. NU ridica - intoarce raportul.
    {"acoperit": bool, "motiv": str|None, "divergente": [...], "sarite": [...]}"""
    manual_keys = set((manual or {}).keys())
    if res.prof.get("tva_la_incasare"):
        return {"acoperit": False, "divergente": [], "sarite": [],
                "motiv": "tva_la_incasare: exigibilitate pe decontari, nu pe emitere - "
                         "reconcilierea pe emitere nu se aplica (limita 3, GARZI cat.4)."}
    from core import common as _c  # [fix trim 06.08.2026]
    inceput, sfarsit = _c.fereastra_tva(perioada, _c.perioada_tva_tip(res.prof))  # fereastra pe perioada TVA (trimestrial -> tot trimestrul), ca generatorul
    col, ded = _agrega_independent(conn, inceput, sfarsit)
    # [B1] deducere amanata (furnizor la incasare) cu PLATA in perioada: generatorul include deducerea pe
    # calea de PLATA (rd.24/rd.25), recon pe emitere nu o poate verifica -> sare randurile deductibile.
    skip = set(manual_keys)
    if _deferred_activ(conn, inceput, sfarsit):
        skip |= {"R22_1", "R22_2", "R23_1", "R23_2"}
    divergente, sarite = _confrunta(res.R, col, ded, skip)
    return {"acoperit": True, "motiv": None, "divergente": divergente, "sarite": sorted(set(sarite))}


def verifica_reconciliere(conn, perioada, res, manual=None):
    """POARTA: ridica ReconciliereD300 daca cele doua cai diverg. Numeste AMBELE valori.
    NU repara tacit nici una din cai. Intoarce raportul cand e curat/neacoperit."""
    rap = reconciliaza(conn, perioada, res, manual)
    if rap["divergente"]:
        linii = "; ".join(
            "%s (%s): generator=%d vs cale2=%d (dif %d)" %
            (d["rand"], d["eticheta"], d["generator"], d["cale2"], d["diferenta"])
            for d in rap["divergente"])
        raise ReconciliereD300(
            "D300 A DOUA CALE: totalurile generatorului NU se reconciliaza cu recalculul "
            "independent din liniile brute. Divergente: %s. Declaratia NU se genereaza - "
            "gardul nu alege singur cine are dreptate; verifica agregarea si datele." % linii)
    return rap
