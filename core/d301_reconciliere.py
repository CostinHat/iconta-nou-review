"""
core/d301_reconciliere.py — A DOUA CALE D301 (gard de continut, 10.08.2026).

DE CE EXISTA: DUK valideaza STRUCTURA (nomenclatoare, formule de checksum intern,
totalPlata_A ca INT(sum)), NU corectitudinea SEMANTICA a bazei. O declaratie D301
cu baza SUPRAEVALUATA dar structural coerenta trece azi la DUK: regula
totalPlata_A = INT(baza1..5 + tva1..5) e o suma de control, se verifica pe ea
insasi (tautologie fata de generator). Golden ANAF cu cifre nu exista
(anaf_surse fara declaratii completate). Deci gardul de continut = recalcul
INDEPENDENT al bazelor+TVA din operatiunile brute, confruntat cu generatorul.

CE FACE: isi trage SINGUR operatiunile brute din d301_operatiuni (SQL propriu),
recalculeaza SINGUR baza pe operatiune cu REGULA CORECTA
    baza = round(val_valuta x curs), curs=1 pentru RON, curs stocat pentru valuta
si le agrega pe sectiuni (tip 1..5, cu rollup S4.1->S4 ca in structura ANAF),
apoi confrunta cu totalurile generatorului (res.totaluri[tip]) si cu
res.total_plata_a. O divergenta = EROARE VIZIBILA care numeste AMBELE valori.
Gardul NU alege cine are dreptate si NU repara tacit (cerinta Costin 05.08) -
blocheaza generarea si cere verificare.

CE PRINDE (inchide GAP-urile din CATALOG_INVALIDITATE.md "### D301"):
  - pierdere la agregare: o operatiune scapata din suma pe sectiune, o sectiune
    pusa in bucketul gresit, un rollup S4.1->S4 ratat -> totalul generatorului
    difera de recalculul independent.
  - SEMANTIC T7 "RON cu curs!=1 -> baza supraevaluata": generatorul (calc_baza)
    inmulteste val_valuta x curs STOCAT indiferent de valuta; daca pe o operatiune
    in RON s-a stocat curs!=1 (ex. 5), baza iese de 5x. Calea 2 aplica regula
    CORECTA (RON => curs 1) si prinde supraevaluarea. Aceasta e divergenta pe care
    DUK NU o vede: totalPlata_A ramane coerent cu bazele umflate.

NON-TAUTOLOGIE (probata prin cod - test_non_tautologie_*): acest modul NU importa
si NU cheama calcul_d301 / _r0 / calc_baza / pull din core.d301. Importa doar
Decimal + psycopg2. Cele doua cai NU impart codul de agregare/rotunjire, deci un
bug in calea generatorului apare ca divergenta.

CE NU PRINDE (limite declarate, GARZI cat.4 "Iesire catre autoritati"):
  1. TVA per operatiune: e valoare PASSTHROUGH din sursa (coloana tva), citita
     IDENTIC de ambele cai. Un tva gresit stocat de contabil (nedeductibil din
     baza x cota - la D301 TVA e adus, nu recalculat) NU produce divergenta =
     raspunderea contabilului (CLAUDE.md sec.8). Calea 2 confirma DOAR ca suma pe
     sectiune a generatorului = suma independenta a acelorasi valori tva.
  2. Cursul pentru VALUTA (non-RON): citit identic din coloana curs de ambele cai;
     un curs gresit pentru EUR/USD (dar >0) NU se prinde aici (nu exista sursa
     independenta de curs BNR in acest modul). Se prinde DOAR abaterea de la
     regula RON=>1 si pierderile de agregare.
  3. Validitatea nr_doc/data_doc/tip/valuta (nomenclator, goluri, C(20)) e treaba
     lui _blocante_pre_duk din d301, nu a reconcilierii - nu se dubleaza aici.
  4. curs absent/<=0 pentru valuta: generatorul (calc_baza) ridica deja ValueError
     inainte sa se ajunga la reconciliere; calea 2 nu re-diagnostica.
  5. d_rec / pers_inreg / rectificativa: identitate/statut, nu continut de baza.

PRECONDITIE: conn e pozitionat pe schema tenantului (acelasi contract ca d301.pull,
care interogheaza d301_operatiuni fara a seta search_path).
"""

from core import afirmatii as _af  # [P8] necunoasterea isi poarta domeniul
from decimal import Decimal, ROUND_HALF_UP

TIPURI_OP = (1, 2, 3, 4, 5)   # re-declarat aici, NU importat din d301 (fara cod comun cu calea 1)


class ReconciliereD301(ValueError):
    """Cele doua cai D301 nu se reconciliaza. Poarta ambele valori si sectiunea divergenta."""


def _q(x):
    """Rotunjire fiscala ARITMETICA la intreg (ROUND_HALF_UP), ca in CLAUDE.md "Rotunjire
    fiscala". Autonoma - NU se importa _r0 din d301 (calea 2 e independenta si pe rotunjire)."""
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _curs_efectiv(tip_valuta, curs):
    """REGULA CORECTA a bazei: pentru RON cursul e 1 prin definitie (nu e conversie);
    pentru valuta e cursul stocat. Aici se naste divergenta fata de generator, care
    inmulteste orbeste val_valuta x curs_stocat inclusiv cand valuta e RON (T7)."""
    if (tip_valuta or "").strip().upper() == "RON":
        return Decimal(1)
    return Decimal(str(curs)) if curs not in (None, "") else Decimal(0)


def _agrega_independent(conn, perioada):
    """Pull SQL PROPRIU + agregare proprie pe d301_operatiuni. Intoarce {tip: [baza_int, tva_int]}
    cu rollup S4.1(tip 5)->S4(tip 4), ca structura ANAF (S4 = S4.1 + S4.2)."""
    import psycopg2.extras as _E
    an, luna = perioada.an, perioada.luna
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT tip, val_valuta, tip_valuta, curs, tva "
                    "FROM d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        rows = cur.fetchall()

    tot = {t: [0, 0] for t in TIPURI_OP}
    for r in rows:
        try:
            tip = int(r["tip"]) if r["tip"] is not None else 1
        except (TypeError, ValueError):
            tip = 1
        curs_ef = _curs_efectiv(r["tip_valuta"], r["curs"])
        baza = _q(Decimal(str(r["val_valuta"] if r["val_valuta"] is not None else 0)) * curs_ef)
        tva = _q(r["tva"] if r["tva"] is not None else 0)
        if tip in tot:
            tot[tip][0] += baza
            tot[tip][1] += tva
        if tip == 5:   # OPANAF 592/2016: serviciile S4.1 se preiau SI in S4
            tot[4][0] += baza
            tot[4][1] += tva
    return tot


def reconciliaza(conn, perioada, res):
    """Recalculeaza independent si confrunta. NU ridica - intoarce raportul.
    {"acoperit": bool, "neacoperit": afirmatie|None, "divergente": [...]}

    [P8, 21.08.2026] `motiv` (sir) -> `neacoperit` (afirmatie `necunoastere`, cu domeniul ei)."""
    if conn is None:
        return {"acoperit": False, "divergente": [], "neacoperit": _af.necunoastere_pe_luna(
            "d301", "fără conexiune DB (recompute independent indisponibil)",
            perioada.an, perioada.luna)}
    tot = _agrega_independent(conn, perioada)
    divergente = []

    def cmp(sect, eticheta, gen, cale2):
        if gen != cale2:
            divergente.append({"sectiune": sect, "eticheta": eticheta,
                               "generator": gen, "cale2": cale2, "diferenta": gen - cale2})

    for t in TIPURI_OP:
        gb, gt = res.totaluri.get(t, (0, 0))
        cmp("baza%d" % t, "sectiune %d baza" % t, int(gb), tot[t][0])
        cmp("tva%d" % t, "sectiune %d TVA" % t, int(gt), tot[t][1])
    # totalPlata_A = INT(sum baza1..5 + tva1..5) - recalculat independent
    tpa_cale2 = sum(tot[t][0] + tot[t][1] for t in TIPURI_OP)
    cmp("totalPlata_A", "suma de control", int(res.total_plata_a), tpa_cale2)

    return {"acoperit": True, "neacoperit": None, "divergente": divergente}


def verifica_reconciliere(conn, perioada, res, manual=None):
    """POARTA: ridica ReconciliereD301 daca cele doua cai diverg. Numeste AMBELE valori.
    NU repara tacit nici una din cai. Intoarce raportul cand e curat.
    (manual e ignorat: D301 nu accepta randuri manuale - semnatura uniforma cu D300.)"""
    rap = reconciliaza(conn, perioada, res)
    if rap["divergente"]:
        linii = "; ".join(
            "%s (%s): generator=%d vs cale2=%d (dif %d)" %
            (d["sectiune"], d["eticheta"], d["generator"], d["cale2"], d["diferenta"])
            for d in rap["divergente"])
        raise ReconciliereD301(
            "D301 A DOUA CALE: totalurile generatorului NU se reconciliaza cu recalculul "
            "independent din operatiunile brute (regula baza=round(val_valuta x curs), "
            "curs=1 pentru RON). Divergente: %s. Declaratia NU se genereaza - gardul nu "
            "alege singur cine are dreptate; verifica agregarea si cursul stocat." % linii)
    return rap
