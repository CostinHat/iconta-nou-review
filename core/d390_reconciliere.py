# -*- coding: utf-8 -*-
"""
core/d390_reconciliere.py — A DOUA CALE D390 (gard de continut / POARTA DE GENERARE, 10.08.2026).

DE CE EXISTA: DUK valideaza STRUCTURA + regulile R16/R24 pe XML-ul deja construit, dar NU
confrunta declaratia cu SURSA (facturile intracomunitare). O declaratie in care generatorul
a PIERDUT un partener / o operatiune intre sursa si <rezumat> (agregare gresita, factura
scapata din pull, baza mutata pe alt tip) e structural valida si trece DUK - dar e falsa.
Analog cu d300_reconciliere: recalcul INDEPENDENT din sursa, confruntat cu generatorul, EROARE
vizibila care numeste AMBELE valori. Gardul NU alege singur cine are dreptate si NU repara tacit
- blocheaza generarea si cere verificare.

RAPORT FATA DE STRATUL 2 (control_incrucisat.verifica_d390 / compara_d390 / facturi_ic):
  - Stratul 2 e un CONTROL FISCAL post-hoc, TOLERANT (verde/gri/rosu cu toleranta la leu), care
    compara D390 cu evidenta contabila VALIDATA si cu D300 DEPUS. E orientat pe DECIZIA omului
    (decalaje de exigibilitate, storno, note in ciorna = legitime -> gri, nu blocheaza nimic).
  - Acest modul e STRATUL 1, POARTA DE GENERARE (ca d300_reconciliere): recalcul aritmetic EXACT
    (fara toleranta) sursa->declaratie, care BLOCHEAZA emiterea la orice divergenta. Nu compara
    cu evidenta/D300, ci cu FACTURILE care au produs chiar acea declaratie. Stratul 2 raspunde
    "declaratia se potriveste cu contabilitatea?"; stratul 1 raspunde "generatorul a agregat corect
    sursa in declaratie?". Sunt complementare - stratul 2 NU acopera aceasta a doua intrebare
    (nu recalculeaza independent nr_opi/total_baza/totalPlata_A din sursa si nu blocheaza).

NON-TAUTOLOGIE (probata prin cod - vezi test_d390_reconciliere.test_non_tautologie_*):
acest modul NU importa `core.d390` si NU cheama nicaieri `calcul_d390`, `_facturi_ic`,
`operatiuni_auto`, `_int`, `numar_fiscal` sau `pull`. Isi trage SINGUR facturile (SQL propriu),
isi clasifica SINGUR partenerul UE (regex + nomenclator re-declarate local), agrega SINGUR pe
(tip, tara, cod, den) si rotunjeste SINGUR (Decimal ROUND_HALF_UP). Cele doua cai NU impart codul
de agregare, deci un bug in agregarea generatorului (factura scapata din pull/suma, baza pusa pe
tip gresit, dublare) apare ca divergenta.

CE PRINDE:  operatiune/partener pierdut(a) intre sursa si declaratie (aggregation-loss, catalog
            "### D390"); baza mutata pe alt tip; dublare/omisiune; nr_opi sau total_baza incoerent
            cu recalculul din facturi.
CE NU PRINDE (limite declarate, GARZI cat.4 "Iesire catre autoritati"):
  1. Corectiile <cos>: generatorul emite doar d_rec="0" (fara sectiune de corectie) - recalculul
     pe facturile lunii NU acopera declaratii rectificative; daca generatorul ar capata <cos>,
     acest gard trebuie extins (declarat aici, nu alarma falsa azi).
  2. Checksum-ul VIES invalid: NU e treaba acestui gard (e mesaj per-partener din TURA-3 /
     calcul_d390.avertismente si il prinde DUK R24.1). Recalculul include partenerul cu cod
     invalid EXACT ca generatorul (nu-l scoate) -> fara divergenta falsa pe cod.
  3. Coliziunea de cheie manual<->auto: daca o linie d390_manual are exact aceeasi cheie
     (tip, tara, cod, den) ca o operatiune auto, generatorul le SUMEAZA inainte de rotunjire, iar
     recalculul le poate rotunji separat -> posibila diferenta de 1 leu pe acea cheie. Rar
     (contabilul introduce manual alt partener), declarat ca limita.
  4. Eroare de INTRARE partajata (ambele cai citesc aceeasi factura gresita) - raspunderea
     contabilului (CLAUDE.md §8).

PRECONDITIE: se apeleaza in `genereaza` DUPA `calcul` si DUPA `valideaza` (deci codO/tara/manual
deja curate), inainte de / impreuna cu poarta-zero. `conn` e pozitionat pe schema tenantului
(genereaza primeste `schema`, iar SQL-ul e schema-calificat - independent de search_path).
"""

import re
from decimal import Decimal, ROUND_HALF_UP

# Nomenclator UE re-declarat LOCAL (nu se importa din core.d390 - non-tautologie inclusiv pe
# nomenclator). Identic ca CONTINUT cu d390.TARI_UE; daca diverge, testul de baseline pe ALFA/DELTA
# si reconcilierea curata il prind. codul de tara = prefixul de TVA (ISO): Croatia = HR.
_TARI_UE = frozenset({
    "AT", "BE", "BG", "CZ", "CY", "HR", "DK", "EE", "DE", "EL", "FI", "FR",
    "IE", "IT", "LV", "LU", "LT", "MT", "GB", "NL", "PL", "PT", "SI", "SK",
    "ES", "SE", "HU", "XI",
})
# tipurile legale per directie (latura de livrare/prestare vs achizitie) - re-declarat local.
_EMISA_TIPURI = ("L", "T", "P", "R")
_PRIMITA_TIPURI = ("A", "S")
_TIPURI = _EMISA_TIPURI + _PRIMITA_TIPURI
_CUI_UE = re.compile(r"^([A-Z]{2})([0-9A-Z]+)$")


class ReconciliereD390(ValueError):
    """Cele doua cai nu se reconciliaza. Poarta ambele valori si campul divergent."""


def _q(d):
    """Rotunjire fiscala ARITMETICA la intreg (ROUND_HALF_UP), ca la D390 (OPANAF 705/2020 nu
    prescrie regula -> aritmetica, ca celelalte generatoare). NU se importa din core.numere/d390 -
    calea 2 e autonoma inclusiv pe rotunjire."""
    return int(Decimal(d).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _clasifica_ue(cui):
    """CUI brut -> (tara, cod) daca partenerul e intracomunitar valid, altfel None. Re-implementat
    local (nu se importa _clasifica_partener) - acelasi filtru ca latura auto a generatorului:
    prefix de 2 litere, tara != RO, tara in nomenclatorul UE. Fara checksum (limita 2)."""
    raw = (cui or "").strip().upper().replace(" ", "").replace("-", "")
    m = _CUI_UE.match(raw)
    if not m:
        return None                       # fara prefix -> intern/persoana fizica (exclus)
    tara, cod = m.group(1), m.group(2)
    if tara == "RO" or tara not in _TARI_UE:
        return None                       # domestic sau tara ne-UE mistypata (exclus)
    return tara, cod


# Fereastra de exigibilitate D390 re-declarata local (art. 284: exigibilitate IC =
# MIN(data_emitere, ziua 15 a lunii urmatoare faptului); NULL -> data_emitere). Trebuie sa fie
# IDENTICA semantic cu pull-ul generatorului, altfel apar divergente FALSE pe facturi cu fapt tarziu.
_EXIG_SQL = ("CASE WHEN f.data_faptului_generator IS NULL THEN f.data_emitere "
             "ELSE LEAST(f.data_emitere, (date_trunc('month', f.data_faptului_generator) "
             "+ interval '1 month' + interval '14 days')::date) END")


def _pull_facturi(conn, schema, an, luna):
    """Pull SQL PROPRIU al facturilor din fereastra de exigibilitate (an, luna). Intoarce
    [(directie, cui, nume, baza_Decimal)]. CUI-ul: intai clientul (c.cui), altfel tert_cui - ca
    la generator (facturile PRIMITE n-au client_id). SQL schema-calificat (independent de search_path)."""
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    q = ("SELECT f.directie AS directie, "
         "COALESCE(c.cui, f.tert_cui) AS cui, COALESCE(c.nume, f.tert_nume) AS nume, "
         "f.total AS total, f.tva AS tva "
         "FROM {s}.facturi f LEFT JOIN {s}.clienti c ON c.id = f.client_id "
         "WHERE {e} >= %s AND {e} < %s ORDER BY f.id").format(s=schema, e=_EXIG_SQL)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(q, (inceput, sfarsit))
        rows = cur.fetchall()
    out = []
    for r in rows:
        baza = Decimal(str(r["total"] if r["total"] is not None else 0)) \
            - Decimal(str(r["tva"] if r["tva"] is not None else 0))
        out.append((r["directie"], (r["cui"] or "").strip(), (r["nume"] or "").strip(), baza))
    return out


def _pull_reclasificari(conn, schema, an, luna):
    """Override-urile de tip {(directie, tara, cod): tip}. SQL propriu (nu se importa
    pull_reclasificari)."""
    with conn.cursor() as cur:
        cur.execute("SELECT directie, tara, cod, tip FROM {s}.d390_reclasificare "
                    "WHERE an=%s AND luna=%s".format(s=schema), (an, luna))
        return {(d, t, c): tip for (d, t, c, tip) in cur.fetchall()}


def _pull_manual(conn, schema, an, luna):
    """Liniile pur manuale {tip, tara, cod, den, baza}. SQL propriu (nu se importa pull_manual)."""
    with conn.cursor() as cur:
        cur.execute("SELECT tip, tara, cod, den, baza FROM {s}.d390_manual "
                    "WHERE an=%s AND luna=%s".format(s=schema), (an, luna))
        return [{"tip": t, "tara": ta, "cod": c, "den": d, "baza": b}
                for (t, ta, c, d, b) in cur.fetchall()]


def _recalcul_independent(conn, schema, an, luna, manual, reclasificari):
    """Recalcul COMPLET si INDEPENDENT al rezumatului D390 din sursa. Reproduce aritmetica
    generatorului cu cod propriu: pull -> filtru UE -> agregare pe (tip, tara, cod, den[:200]) ->
    rotunjire pe operatie -> rezumat pe tip, nr_opi, total_baza, totalPlata_A. Intoarce
    (rezumat{tip:int}, nr_opi, total_baza, total_plata)."""
    recl = reclasificari if reclasificari is not None else _pull_reclasificari(conn, schema, an, luna)
    man = manual if manual is not None else _pull_manual(conn, schema, an, luna)

    ops = {}   # (tip, tara, cod, den) -> Decimal
    # latura AUTO din facturi IC
    for (directie, cui, nume, baza) in _pull_facturi(conn, schema, an, luna):
        ue = _clasifica_ue(cui)
        if ue is None:
            continue                                   # domestic/ne-UE: exclus (nu intra in D390)
        tara, cod = ue
        den = (nume or "")[:200]
        tip_def = "L" if directie == "emisa" else "A"
        tip = recl.get((directie, tara, cod), tip_def)
        ops[(tip, tara, cod, den)] = ops.get((tip, tara, cod, den), Decimal(0)) + baza
    # latura MANUALA (P/S/T/R introduse de contabil, fara factura)
    for op in (man or []):
        tip = op.get("tip")
        tara = (op.get("tara") or "").upper()
        cod = (op.get("cod") or "")
        den = (op.get("den") or "")[:200]
        ops[(tip, tara, cod, den)] = ops.get((tip, tara, cod, den), Decimal(0)) \
            + Decimal(str(op.get("baza") or 0))

    ops_int = {k: _q(v) for k, v in ops.items()}
    rezumat = {t: 0 for t in _TIPURI}
    for (tip, _, _, _), b in ops_int.items():
        if tip in rezumat:
            rezumat[tip] += b
    nr_opi = len(ops_int)
    total_baza = sum(rezumat.values())
    total_plata = (nr_opi + rezumat["L"] + rezumat["T"] + rezumat["A"]
                   + rezumat["P"] + rezumat["S"] + rezumat["R"])
    return rezumat, nr_opi, total_baza, total_plata


def _res_camp(res, nume, implicit=0):
    """Acces uniform la res (dataclass Rezultat SAU dict), ca stratul 2."""
    if isinstance(res, dict):
        return res.get(nume, implicit)
    return getattr(res, nume, implicit)


def reconciliaza(conn, schema, an, luna, res, manual=None, reclasificari=None):
    """Recalculeaza independent si confrunta. NU ridica - intoarce raportul.
    {"acoperit": bool, "motiv": str|None, "divergente": [...]}."""
    if conn is None:
        return {"acoperit": False, "motiv": "fără conexiune DB (recompute independent indisponibil)", "divergente": []}
    rezumat_g = _res_camp(res, "rezumat", {}) or {}
    rez2, nr2, tot2, plata2 = _recalcul_independent(conn, schema, an, luna, manual, reclasificari)

    divergente = []

    def cmp(camp, eticheta, gen, cale2):
        if int(gen) != int(cale2):
            divergente.append({"camp": camp, "eticheta": eticheta,
                               "generator": int(gen), "cale2": int(cale2),
                               "diferenta": int(gen) - int(cale2)})

    for tip in _TIPURI:
        cmp("baza%s" % tip, "baza tip %s" % tip,
            (rezumat_g.get(tip, 0) if isinstance(rezumat_g, dict) else getattr(rezumat_g, tip, 0)),
            rez2[tip])
    cmp("nrOPI", "numar operatiuni", _res_camp(res, "nr_opi", 0), nr2)
    cmp("total_baza", "total baze", _res_camp(res, "total_baza", 0), tot2)
    cmp("totalPlata_A", "totalPlata_A", _res_camp(res, "total_plata_a", 0), plata2)

    return {"acoperit": True, "motiv": None, "divergente": divergente}


def verifica_reconciliere(conn, schema, an, luna, res, manual=None, reclasificari=None):
    """POARTA: ridica ReconciliereD390 daca cele doua cai diverg. Numeste AMBELE valori si campul.
    NU repara tacit nici una din cai. Intoarce raportul cand e curat."""
    rap = reconciliaza(conn, schema, an, luna, res, manual, reclasificari)
    if rap["divergente"]:
        linii = "; ".join(
            "%s (%s): generator=%d vs cale2=%d (dif %d)" %
            (d["camp"], d["eticheta"], d["generator"], d["cale2"], d["diferenta"])
            for d in rap["divergente"])
        raise ReconciliereD390(
            "D390 A DOUA CALE: rezumatul generatorului NU se reconciliaza cu recalculul independent "
            "din facturile intracomunitare (aggregation-loss). Divergente: %s. Declaratia NU se "
            "genereaza - gardul nu alege singur cine are dreptate; verifica agregarea (factura "
            "scapata din pull/suma, baza pe tip gresit, dublare) si datele." % linii)
    return rap
