# -*- coding: utf-8 -*-
"""CONTAREA ISTORICULUI — R89, blocul JJJ (29.08.2026).

CE E, ȘI CE NU E. **Nu e un script de migrare.** Nu scrie niciun `INSERT` propriu: pentru fiecare
factură cheamă **actul de contare obișnuit**, `core/contare_facturi.contabilizeaza`, același pe care
îl folosesc emiterea, validarea unei primite și ruta manuală. Cerut explicit la JJJ3, și motivul e că
altfel proba ar fi fost despre script, nu despre traseu: *rularea pe istoric e chiar dovada că
traseul construit la R87/R88 ține și pe cazuri vechi, nu doar pe facturi noi.*

DE CE SE POATE RULA PE DATE REALE. Costin, 29.08.2026: *„nu există clienți reali în aplicație — tot
portofoliul e de test."* Verificat cât se poate verifica mecanic: cele 55 de rânduri din
`public.declaratii_depuse` vin din **importul istoric**, nu din coada aplicației (R40 e deschisă chiar
pe faptul că **nicio** declarație n-a fost depusă prin aplicație), iar denumirile firmelor sunt
scenarii („Comert Micro TVA", „DELTA DEFECT-LUNA"). *Registrul spune „15 firme la cabinete reale" —
dar acolo „real" înseamnă doar că numele cabinetului nu conține TEST/PROBA, nu că are clienți.*

REGULA DE DATARE, dată de Costin (JJJ1/JJJ2):
  * **TVA = 0** → nota la **data descoperirii**. Nu poartă taxă, deci luna nu decide nimic fiscal.
  * **TVA > 0**, luna emiterii **deschisă** → nota pe **data emiterii**. Faptul și evidența lui au
    aceeași dată; asta e cazul normal.
  * **TVA > 0**, luna emiterii **închisă** → nota la **data descoperirii**, iar descrierea poartă
    mențiunea care o leagă de factură — *„nu doar o dată arbitrară"*.

RAMURA DE LUNA INCHISA nu se probeaza de aici. A fost, cat lotul avea membri; dupa ce lotul s-a
golit (R89, 29.08.2026) proba n-a mai avut pe ce sa se aprinde si tiparea „(nicio factura potrivita)"
— adica un verde care nu masoara nimic. S-a mutat in `scripts/proba_contare_reala.py`, blocul JJJ2,
care isi construieste singur cazul si deci nu depinde de starea portofoliului.

    ./venv/bin/python scripts/contare_istorica.py            # doar arata (ROLLBACK)
    ./venv/bin/python scripts/contare_istorica.py --scrie    # comite
"""
import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, contare_facturi as _cf, nomenclator_status_factura as _nsf  # noqa: E402

AZI = date.today()
MOTIV_TVA0 = "factura nu poarta TVA, contata la data descoperirii (R89)"
MOTIV_INCHISA = "luna emiterii era inchisa la data descoperirii (R89)"


def numaratori(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT (SELECT COUNT(*) FROM %s.inregistrari), "
                    "       (SELECT COUNT(*) FROM %s.inregistrari_linii)" % (schema, schema))
        return cur.fetchone()


def lot(conn, schema):
    """Facturile declarabile FARA nota de contare. A doua citire — cea care spune daca factura e in
    evidenta —, nu cea pe cheie: o factura a carei cheie e ocupata de o nota de PLATA lipseste din
    evidenta la fel de tare."""
    out = []
    with _cf.cursor_dict(conn) as cur:
        cur.execute("SELECT f.id, f.numar, f.serie, f.data_emitere, f.directie, f.status, "
                    "       COALESCE(f.total_lei, f.total, 0) AS total, COALESCE(f.tva,0) AS tva "
                    "FROM %sfacturi f WHERE %s AND COALESCE(f.tip,'factura')='factura' "
                    "ORDER BY f.data_emitere, f.id"
                    % (_cf._p(schema), _nsf.clauza_sql(alias="f")))
        for r in cur.fetchall():
            f = dict(r)
            if _cf.contare_existenta(cur, schema, f["id"]) is None:
                out.append(f)
    return out


def _descoperire(f):
    """Data descoperirii, dar NICIODATA inaintea faptului.

    IESIT DIN DRY-RUN, nu presupus: `tenant_017` #5 e emisa la **2026-09-10**, cu TVA 0. Regula
    literala („TVA=0 -> data descoperirii") i-ar fi dat o nota pe **2026-08-29** — adica *inaintea*
    documentului pe care il inregistreaza. O inregistrare nu poate preceda faptul; pe date cu
    scadente in viitor, regula are nevoie de podeaua asta. **Un singur caz din 31**, dar taie o
    imposibilitate, nu un caz particular."""
    d = f["data_emitere"]
    return d if (d and d > AZI) else AZI


def decide(cur, schema, f):
    """(data_nota, motiv_data, eticheta_ramurii) — regula de datare, aplicata."""
    if Decimal(str(f["tva"] or 0)) == 0:
        d = _descoperire(f)
        if d != AZI:
            return d, None, "TVA=0, dar emisa in viitor -> data emiterii (nota nu precede faptul)"
        return d, MOTIV_TVA0, "TVA=0 -> data descoperirii"
    if _cf.luna_blocata(cur, schema, f["data_emitere"]):
        return _descoperire(f), MOTIV_INCHISA, "luna emiterii INCHISA -> data descoperirii"
    return f["data_emitere"], None, "luna emiterii deschisa -> data emiterii"


def ruleaza(scrie=False):
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name, nume FROM public.tenants WHERE activ ORDER BY schema_name")
            firme = cur.fetchall()
    assert firme, "domeniul e gol - nicio firma activa"

    total, contate, refuzate, avertizate, plasa_lovita = 0, 0, [], [], 0
    print("DATA DESCOPERIRII: %s   ·   MOD: %s\n" % (AZI, "SCRIE" if scrie else "doar arata (ROLLBACK)"))
    for schema, nume in firme:
        with db.get_conn(schema) as conn:
            de_facut = lot(conn, "")
            if not de_facut:
                conn.rollback()
                continue
            inainte = numaratori(conn, schema)
            print("%s — %s   (%d de contat)" % (schema, nume, len(de_facut)))
            for f in de_facut:
                total += 1
                with _cf.cursor_dict(conn) as cur:
                    data_nota, motiv, ramura = decide(cur, "", f)
                    # [JJJ4] Plasa anti-dublare: ar fi OPRIT automatul pe factura asta?
                    cand = _cf.candidate_fara_cheie(cur, "", f)
                    if cand:
                        plasa_lovita += 1
                    try:
                        rez = _cf.contabilizeaza(cur, "", f["id"], automat=False,
                                                 data_nota=data_nota, motiv_data=motiv)
                    except _cf.RefuzContare as e:
                        refuzate.append((schema, f["id"], e.cod, e.mesaj[:80]))
                        print("    #%-4s %s  TVA %9s  REFUZ %s" % (f["id"], f["data_emitere"],
                                                                   f["tva"], e.cod))
                        continue
                contate += 1
                if rez.get("avertisment"):
                    avertizate.append((schema, f["id"], rez["avertisment"]["note"]))
                print("    #%-4s %s  TVA %9s  ->  nota #%s la %s   [%s]%s"
                      % (f["id"], f["data_emitere"], f["tva"], rez["inregistrare_id"],
                         data_nota, ramura, "  AVERTISMENT" if rez.get("avertisment") else ""))
            dupa = numaratori(conn, schema)
            print("    randuri inregistrari/linii: %s -> %s" % (inainte, dupa))
            if not scrie:
                conn.rollback()

    print("\n═══ REZULTAT")
    print("  facturi in lot (fara nota de contare): %d" % total)
    print("  contate:                              %d" % contate)
    print("  refuzate:                             %d" % len(refuzate))
    for s, fid, cod, mesaj in refuzate:
        print("      %s #%s — %s: %s" % (s, fid, cod, mesaj))
    print("  [JJJ4] facturi pe care plasa anti-dublare le-ar fi oprit: %d" % plasa_lovita)
    print("  [JJJ4] contari facute CU avertisment de posibila dublare: %d" % len(avertizate))
    for s, fid, note in avertizate:
        print("      %s #%s — note candidate: %s" % (s, fid, note))
    if not scrie:
        print("\n  NU S-A SCRIS NIMIC — toate tranzactiile s-au intors. Ruleaza cu --scrie ca sa comita.")
    return total, contate, refuzate, plasa_lovita


if __name__ == "__main__":
    t, c, r, p = ruleaza(scrie="--scrie" in sys.argv)
    sys.exit(0 if (t == c and not r) else 1)
