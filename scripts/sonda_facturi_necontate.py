# -*- coding: utf-8 -*-
"""SONDA CCC — cate facturi DECLARABILE nu au nicio nota contabila, cu TVA-ul lor, pe firme si luni.

DE CE EXISTA CA FISIER. Cifra „28 din 43, 102.260,00 lei, 10 firme din 17" a fost masurata ad-hoc pe
24.08.2026 la R35 si citata de atunci in R87, R88 si in predare. **N-a lasat instrument.** O cifra
care nu se poate recalcula nu e o masuratoare, e o amintire — iar intre timp portofoliul a crescut la
19 firme, deci ancora nu mai descrie baza. `scripts/sonda_r35.py` masoara ALTCEVA (verdicte TVA verzi
peste un necunoscut din propriul payload); nu produce cifra asta.

DOMENIUL, ca REGULA nu ca lista: TOATE schemele active din `public.tenants`. Nicio excludere.

CE E O FACTURA „DECLARABILA": `core/nomenclator_status_factura.clauza_sql()` — sursa unica (P1), NU
o lista copiata aici. Plus `tip='factura'`: proforma si avizul sunt refuzate explicit de ruta de
contabilizare (*„proforma/avizul nu se contabilizeaza (nu e document fiscal)"*), deci a le numara
printre necontate ar produce o restanta care nu se poate inchide.

CE E „NECONTATA" — DOUA CITIRI, si nu dau acelasi numar. Prima forma a sondei avea numai prima, si
a subnumarat cu 2:

  * PE CHEIE — nu exista niciun rand in `inregistrari` cu `factura_id` = id-ul ei. **Aceeasi cheie**
    pe care o foloseste `factura_contabilizeaza` ca sa refuze a doua contare, deci asta e citirea
    care PREZICE ce ar face mecanismul.
  * FARA NOTA DE CONTARE — nu exista nicio nota cu `factura_id` care sa aiba SEMNATURA de contare
    (cont de tert + cont de fond sau de TVA). Asta e citirea care spune daca factura e in evidenta.

De ce difera, si nu e o subtilitate: **o nota de PLATA poarta si ea `factura_id`.** Reconcilierea
bancara scrie `401 = 5121` cu `factura_id` pe factura platita. Pe cheie, factura aia arata „contata";
in evidenta, cheltuiala/venitul ei nu exista nicaieri. Masurat azi: **2 facturi** (`tenant_004` #9 si
`tenant_017` #8) sunt exact asa. Ele arata si reversul gaurii din AAA7: acolo o nota fara
`factura_id` e invizibila pentru anti-dublare; aici o nota care NU e contare **blocheaza** contarea.

Limita declarata, comuna amandurora: o factura contata din jurnalul liber n-are `factura_id`, deci
apare ca necontata pe amandoua citirile. Marimea acelei clase: `scripts/sonda_note_fara_factura_id.py`.

SEMNATURA DE CONTARE nu se defineste aici: se IMPORTA din `scripts/sonda_note_fara_factura_id.py`
(P1 — un adevar, un loc). Doua definitii ale lui „arata a factura" ar da doua raspunsuri la prima
divergenta, iar sonda asta si cealalta masoara chiar cele doua fete ale aceleiasi chei.

LUNA INCHISA — doua criterii, amandoua raportate, fiindca nu dau acelasi numar:
  * MECANIC — luna facturii e chiar in `perioade_blocate`. Asta e ce citeste `_perioada_blocata`
    din `main.py`, deci e criteriul care PREZICE refuzul lui `_cere_luna_deschisa`.
  * SUB-ULTIMA — `data_emitere` <= ultima zi a ultimei perioade blocate a firmei. E citirea ceruta
    in comanda. Supra-numara fata de cel mecanic daca firma are goluri in blocaje.

NU CONTABILIZEAZA NIMIC, si nu propune nimic: numara si listeaza.

ANTI-VACUU: domeniul gol (nicio schema, sau nicio factura in nicio schema) e EROARE, nu raspuns.

NU SCRIE NIMIC: `pg_stat_user_tables` inainte si dupa, iar diferenta se tipareste.

    ./venv/bin/python scripts/sonda_facturi_necontate.py
"""
import os
import sys
from decimal import Decimal

_AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_AICI))
sys.path.insert(0, _AICI)

from core import db, nomenclator_status_factura as _nsf  # noqa: E402
import sonda_note_fara_factura_id as _bbb  # noqa: E402


def scrieri(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT coalesce(sum(n_tup_ins), 0), coalesce(sum(n_tup_upd), 0), "
                    "coalesce(sum(n_tup_del), 0) FROM pg_stat_user_tables")
        return cur.fetchone()


def firme(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name, id, nume, accounting_firm_id FROM public.tenants "
                    "WHERE activ ORDER BY schema_name")
        return [{"schema": r[0], "id": r[1], "nume": r[2], "cabinet": r[3]} for r in cur.fetchall()]


def blocaje(conn, s):
    with conn.cursor() as cur:
        cur.execute("SELECT an, luna FROM %s.perioade_blocate ORDER BY an, luna" % s)
        return [(r[0], r[1]) for r in cur.fetchall()]


def note_pe_factura(conn, s):
    """{factura_id: [nota, ...]} — notele care POARTA o cheie de factura, cu liniile lor."""
    with conn.cursor() as cur:
        cur.execute("SELECT i.factura_id, i.id, i.sursa, i.status, "
                    "       l.cont_debit, l.cont_credit, l.suma "
                    "FROM %s.inregistrari i "
                    "LEFT JOIN %s.inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.factura_id IS NOT NULL ORDER BY i.id" % (s, s))
        randuri = cur.fetchall()
    pe_id = {}
    note = {}
    for (fid, nid, sursa, status, cd, cc, suma) in randuri:
        n = note.get(nid)
        if n is None:
            n = {"id": nid, "sursa": sursa, "status": status, "linii": []}
            note[nid] = n
            pe_id.setdefault(fid, []).append(n)
        if cd is not None:
            n["linii"].append((cd, cc, Decimal(str(suma or 0))))
    return pe_id


def e_contare(n):
    """Semnatura de contare, IMPORTATA din sonda BBB (P1): tert + fond sau TVA.
    O nota de plata (`401 = 5121`) atinge tertul, dar nici fond, nici TVA — deci nu e contare."""
    t, v, f = _bbb.clasifica(n)
    return t and (v or f)


def facturi(conn, s):
    clauza = _nsf.clauza_sql(alias="f")
    pe_id = note_pe_factura(conn, s)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT f.id, f.data_emitere, f.directie, f.status, f.numar, f.serie, "
            "       COALESCE(f.total_lei, f.total, 0), COALESCE(f.tva, 0) "
            "FROM %s.facturi f WHERE %s AND COALESCE(f.tip,'factura')='factura' "
            "ORDER BY f.data_emitere, f.id" % (s, clauza))
        out = [{"id": r[0], "data": r[1], "directie": r[2], "status": r[3], "numar": r[4],
                "serie": r[5], "total": Decimal(str(r[6])), "tva": Decimal(str(r[7]))}
               for r in cur.fetchall()]
    for x in out:
        lot = pe_id.get(x["id"], [])
        x["note"] = len(lot)
        x["note_contare"] = len([n for n in lot if e_contare(n)])
        x["note_necontare"] = [n for n in lot if not e_contare(n)]
    return out


def ruleaza():
    # Clasificatorul de „contare" e imprumutat, deci se calibreaza aici la fel ca la el acasa:
    # fara asta, un `e_contare` care spune „nu" la tot ar umfla cifra fara sa se vada.
    _bbb.calibreaza()
    db.init_pool()
    with db.get_conn() as conn:
        inainte = scrieri(conn)
        fs = firme(conn)
        assert fs, "sonda n-a gasit nicio firma activa - domeniul e gol"
        rez, sarite = [], []
        for f in fs:
            s = f["schema"]
            try:
                bl = blocaje(conn, s)
                fac = facturi(conn, s)
            except Exception as e:
                conn.rollback()
                sarite.append((s, "%s: %s" % (type(e).__name__, str(e)[:80])))
                continue
            bset = set(bl)
            ultima = max(bl) if bl else None
            for x in fac:
                d = x["data"]
                x["blocata_mecanic"] = (d is not None and (d.year, d.month) in bset)
                x["blocata_sub_ultima"] = (
                    d is not None and ultima is not None and (d.year, d.month) <= ultima)
            rez.append(dict(f, blocaje=bl, ultima_blocata=ultima, facturi=fac))
        dupa = scrieri(conn)

    total_fac = sum(len(r["facturi"]) for r in rez)
    assert total_fac, ("sonda n-a gasit nicio factura declarabila in nicio schema - domeniul e gol, "
                       "deci orice raspuns al ei ar fi despre nimic")

    nec = [(r, x) for r in rez for x in r["facturi"] if x["note"] == 0]
    nec_ev = [(r, x) for r in rez for x in r["facturi"] if x["note_contare"] == 0]
    doar_plata = [(r, x) for r, x in nec_ev if x["note"] > 0]
    firme_cu_nec = sorted({r["schema"] for r, _ in nec})
    tva_nec = sum((x["tva"] for _, x in nec), Decimal(0))

    print("DOMENIU: %d firme active - %d facturi declarabile (tip='factura'), pe %d firme cu cel "
          "putin una" % (len(rez), total_fac, len({r["schema"] for r in rez if r["facturi"]})))
    print("stari declarabile (din nomenclator): %s" % (", ".join(_nsf.declarabile())))
    print("pg_stat_user_tables INAINTE: ins=%d upd=%d del=%d\n" % inainte)

    print("CCC1 — RE-MASURATOAREA")
    print("  [PE CHEIE — citirea care prezice ce face `factura_contabilizeaza`]")
    print("  facturi declarabile necontate: %d din %d (%.0f%%)"
          % (len(nec), total_fac, 100.0 * len(nec) / total_fac))
    print("  TVA purtat de ele:             %s lei" % ("{:,.2f}".format(tva_nec)))
    print("  firme atinse:                  %d din %d active (%d au cel putin o factura declarabila)"
          % (len(firme_cu_nec), len(rez), len({r["schema"] for r in rez if r["facturi"]})))
    pe_directie = {}
    for _, x in nec:
        k = x["directie"] or "(null)"
        d = pe_directie.setdefault(k, [0, Decimal(0)])
        d[0] += 1
        d[1] += x["tva"]
    print("  pe directie:                   " + " · ".join(
        "%s=%d (TVA %s)" % (k, v[0], "{:,.2f}".format(v[1])) for k, v in sorted(pe_directie.items())))
    bl_mec = [x for _, x in nec if x["blocata_mecanic"]]
    bl_sub = [x for _, x in nec if x["blocata_sub_ultima"]]
    print("  din care in luni INCHISE (mecanic, luna in perioade_blocate): %d (TVA %s)"
          % (len(bl_mec), "{:,.2f}".format(sum((x["tva"] for x in bl_mec), Decimal(0)))))
    print("  din care in luni INCHISE (sub ultima perioada blocata):       %d (TVA %s)"
          % (len(bl_sub), "{:,.2f}".format(sum((x["tva"] for x in bl_sub), Decimal(0)))))
    print()
    print("  [FARA NOTA DE CONTARE — citirea care spune daca factura e in evidenta]")
    print("  facturi declarabile fara nota de contare: %d din %d (%.0f%%), TVA %s lei, pe %d firme"
          % (len(nec_ev), total_fac, 100.0 * len(nec_ev) / total_fac,
             "{:,.2f}".format(sum((x["tva"] for _, x in nec_ev), Decimal(0))),
             len({r["schema"] for r, _ in nec_ev})))
    print("  DIFERENTA fata de citirea pe cheie: %d facturi care au nota cu `factura_id`, dar nu de "
          "contare" % len(doar_plata))
    for r, x in doar_plata:
        print("      %s #%d %s %s total=%s tva=%s — notele ei: %s"
              % (r["schema"], x["id"], x["data"], x["directie"],
                 "{:,.2f}".format(x["total"]), "{:,.2f}".format(x["tva"]),
                 " · ".join("#%d sursa=%s status=%s [%s]"
                            % (n["id"], n["sursa"], n["status"],
                               ", ".join("%s=%s %s" % (cd, cc, s) for cd, cc, s in n["linii"]))
                            for n in x["note_necontare"])))
    print("  *Pe astea, contarea automata ar fi REFUZATA de `factura_contabilizeaza` — cheia e "
          "ocupata de o nota de plata. E reversul gaurii din AAA7, si nu era masurat.*")
    print()

    print("CCC2 — FIRMA CU FIRMA (numai cele cu necontate)")
    print("  %-12s %-32s %5s %5s %14s  %-17s %6s %6s" % (
        "schema", "firma", "decl", "nec", "TVA nec", "interval luni", "inch.M", "inch.U"))
    for r in rez:
        lot = [x for x in r["facturi"] if x["note"] == 0]
        if not lot:
            continue
        luni = sorted({(x["data"].year, x["data"].month) for x in lot if x["data"]})
        interval = ("%04d-%02d .. %04d-%02d" % (luni[0][0], luni[0][1], luni[-1][0], luni[-1][1])
                    if luni else "(fara data)")
        print("  %-12s %-32s %5d %5d %14s  %-17s %6d %6d" % (
            r["schema"], (r["nume"] or "")[:32], len(r["facturi"]), len(lot),
            "{:,.2f}".format(sum((x["tva"] for x in lot), Decimal(0))), interval,
            len([x for x in lot if x["blocata_mecanic"]]),
            len([x for x in lot if x["blocata_sub_ultima"]])))
    print()

    print("FIRME FARA NICIO NECONTATA (contra-proba: tiparul nu e universal):")
    fara = [r for r in rez if r["facturi"] and not [x for x in r["facturi"] if x["note"] == 0]]
    print("  " + (", ".join("%s (%d decl)" % (r["schema"], len(r["facturi"])) for r in fara)
                  if fara else "(niciuna)"))
    goale = [r for r in rez if not r["facturi"]]
    print("FIRME FARA NICIO FACTURA DECLARABILA: %d — %s"
          % (len(goale), ", ".join(r["schema"] for r in goale) if goale else "(niciuna)"))
    print()

    print("LISTA COMPLETA, factura cu factura (pentru revizuire — NU se contabilizeaza nimic):")
    for r in rez:
        lot = [x for x in r["facturi"] if x["note"] == 0]
        if not lot:
            continue
        print("  %s — %s (blocaje: %s; ultima blocata: %s)"
              % (r["schema"], r["nume"], len(r["blocaje"]),
                 ("%04d-%02d" % r["ultima_blocata"]) if r["ultima_blocata"] else "niciuna"))
        for x in lot:
            print("      #%-5d %s %-7s %-11s %12s lei  TVA %10s  %s"
                  % (x["id"], x["data"], x["directie"], x["status"],
                     "{:,.2f}".format(x["total"]), "{:,.2f}".format(x["tva"]),
                     "LUNA INCHISA" if x["blocata_mecanic"]
                     else ("sub ultima blocata" if x["blocata_sub_ultima"] else "luna deschisa")))
    if sarite:
        print("\nSCHEME NEMASURABILE: %d" % len(sarite))
        for s, motiv in sarite:
            print("    SARIT %s - %s" % (s, motiv))

    delta = tuple(b - a for a, b in zip(inainte, dupa))
    print("\npg_stat_user_tables DUPA: ins=%d upd=%d del=%d" % dupa)
    print("DELTA scrieri: ins=%+d upd=%+d del=%+d  ->  %s"
          % (delta + ("SONDA N-A SCRIS" if delta == (0, 0, 0) else "*** A SCRIS ***",)))
    return rez, nec, sarite, delta


if __name__ == "__main__":
    rez, nec, sar, delta = ruleaza()
    print("\nVERDICT CCC")
    print("  necontate: %d" % len(nec))
    print("  TVA:       %s lei" % "{:,.2f}".format(sum((x["tva"] for _, x in nec), Decimal(0))))
    print("  firme:     %d" % len({r["schema"] for r, _ in nec}))
    print("  scrieri:   %s" % ("ZERO" if delta == (0, 0, 0) else str(delta)))
