# -*- coding: utf-8 -*-
"""SONDA BBB — gaura mecanismului de idempotenta: note care ating conturi de factura,
FARA sa poarte `factura_id`.

DE CE EXISTA CA FISIER. AAA7 (R87) numeste gaura in proza: `factura_contabilizeaza` refuza pe
`SELECT COUNT(*) FROM inregistrari WHERE factura_id=%s`, deci o nota scrisa din jurnalul liber
(`POST /jurnal`), care NU poarta `factura_id`, e invizibila pentru verificarea aia — iar
automatizarea ar scrie a doua nota peste ea. Proza nu are cifra. O cifra masurata ad-hoc n-ar putea
fi recalculata dupa constructie, deci nu s-ar putea arata ca gaura s-a inchis.

DOMENIUL, ca REGULA nu ca lista: TOATE schemele active din `public.tenants`. Nicio excludere.

TREI CLASE, numarate separat, fiindca inseamna lucruri diferite:

  * G0 — toate notele fara `factura_id`. Numitorul brut. Include note care n-au nicio treaba cu
    facturile (amortizare, salarii, fixturi).
  * G1 — GAURA LARGA: nota fara `factura_id` care atinge cel putin un cont din multimea de mai jos.
    E citirea larga a comenzii BBB1. **Supra-numara prin constructie**: o nota de casa (bon, chitanta,
    raport Z) crediteaza 707 si 4427 la fel ca o factura emisa, si e perfect legitima.
  * G2 — SEMNATURA DE FACTURA: nota fara `factura_id` care atinge un cont de TERT (4111 sau 401)
    SI un cont de fond sau de TVA. Asta e clasa care poate fi o contare manuala de factura: o nota
    de casa nu trece prin 4111/401, trece prin 5311. G2 e citirea stricta.

MULTIMEA DE CONTURI, si de ce fiecare (comanda: „4111, 401, 4426, 4427, 707, 6xx de marfa/cheltuiala"):
  TERT   4111, 401             — cele doua conturi de tert pe care le scrie `core/facturi.py`
         404                   — ADAUGAT dupa prima rulare, si nu din prudenta: prima forma a sondei
                                 a raportat G2=0, iar in lista lui G1 se vedeau doua note de forma
                                 `2131=404 · 4426=404` — o factura de achizitie de imobilizare,
                                 contata manual, care are semnatura de factura dar NU trece prin 401.
                                 Cu TERT={4111,401} sonda ar fi raportat „zero" despre o clasa pe care
                                 n-o vedea. `404` e contul de furnizor de imobilizari; nu e o largire
                                 de comoditate, e inchiderea unui punct orb aratat de propria lista.
  TVA    4426, 4427, 4428      — 4428 fiindca `factura_emisa/primita(tva_incasare=True)` il scrie
  FOND   70*, 6*               — veniturile (701/703/704/707) si cheltuielile, cerute de comanda
         371,301,302,303,213   — `ACHIZITIE` din `core/facturi.py`; ruta de contabilizare cheama
                                 `factura_primita` FARA `cont`, deci scrie implicit 371

CE RAMANE IN AFARA, declarat: `461`/`462` (debitori/creditori diversi). Nu sunt scrise de niciun
drum factura->nota din cod, iar includerea lor ar trage in clasa operatiuni care nu sunt facturi.
Daca vreodata o factura se conteaza manual pe 461/462, sonda asta n-o vede — si o spune aici.

BBB2 — COLIZIUNE REALA vs GAURA TEORETICA. Pentru fiecare nota din clasa, se cauta o factura
DECLARABILA in aceeasi luna (luna notei = luna `data_emitere`), cu suma care se potriveste. Doua
praguri, raportate separat:
  * STRICT — valoarea notei pe tert (suma liniilor care debiteaza 4111 sau crediteaza 401) coincide
    cu totalul facturii, la un ban.
  * LARG   — coincide cu totalul SAU cu baza (total - tva) SAU cu suma tuturor liniilor notei.
Numai coliziunile produc efectiv o a doua nota daca automatul ar rula. Restul sunt gauri teoretice.

ANTI-VACUU: daca domeniul e gol (nicio schema, sau nicio nota deloc), e EROARE, nu raspuns —
clasa [[gard-care-nu-se-verifica-pe-sine]], care a lovit chiar sonda R35 la prima ei forma.

CALIBRARE IN AMBELE DIRECTII, la fiecare pornire, INAINTE de masuratoare (METODA §22). Raspunsul
asteptat aici e ZERO, iar un zero e exact ce ar raporta si un clasificator orb. Deci sonda isi
demonstreaza de fiecare data ca:
  * POZITIV — o nota sintetica cu semnatura de factura emisa (4111=707, 4111=4427) si una de factura
    primita (371=401, 4426=401) CAD in G2, iar coliziunea pe suma+luna se APRINDE pe o factura
    sintetica potrivita;
  * NEGATIV — o nota de casa (5311=707, 5311=4427), una de amortizare (6811=2813) si una de banca
    (5121=4111... nu: 411 e tert, deci se ia 5121=5311) NU cad in G2, desi doua din ele cad in G1.
    Fara directia asta, un clasificator care spune „da" la tot ar trece la fel de bine;
  * COLIZIUNEA nu se aprinde pe suma diferita si nici pe alta luna.
Daca oricare pica, sonda se opreste cu AssertionError, nu raporteaza.

NU SCRIE NIMIC: `pg_stat_user_tables` inainte si dupa, iar diferenta se tipareste.

    ./venv/bin/python scripts/sonda_note_fara_factura_id.py
"""
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, nomenclator_status_factura as _nsf  # noqa: E402

TERT = ("4111", "401", "404")
TVA = ("4426", "4427", "4428")
FOND_PREFIX = ("70", "6")
FOND_EXACT = ("371", "301", "302", "303", "213")


def _e_tert(c):
    return any(c.startswith(p) for p in TERT)


def _e_tva(c):
    return any(c.startswith(p) for p in TVA)


def _e_fond(c):
    return any(c.startswith(p) for p in FOND_PREFIX) or any(c.startswith(p) for p in FOND_EXACT)


def scrieri(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT coalesce(sum(n_tup_ins), 0), coalesce(sum(n_tup_upd), 0), "
                    "coalesce(sum(n_tup_del), 0) FROM pg_stat_user_tables")
        return cur.fetchone()


def scheme(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE activ ORDER BY schema_name")
        return [r[0] for r in cur.fetchall()]


def note_schema(conn, s):
    """Toate notele schemei, cu liniile lor. Intoarce lista de dict."""
    with conn.cursor() as cur:
        cur.execute("SELECT i.id, i.data, i.status, i.sursa, i.factura_id, i.descriere, "
                    "       l.cont_debit, l.cont_credit, l.suma "
                    "FROM %s.inregistrari i "
                    "LEFT JOIN %s.inregistrari_linii l ON l.inregistrare_id = i.id "
                    "ORDER BY i.id" % (s, s))
        randuri = cur.fetchall()
    note = {}
    for (nid, data, status, sursa, fid, descriere, cd, cc, suma) in randuri:
        n = note.setdefault(nid, {"id": nid, "data": data, "status": status, "sursa": sursa,
                                  "factura_id": fid, "descriere": descriere, "linii": []})
        if cd is not None:
            n["linii"].append((cd, cc, Decimal(str(suma or 0))))
    return list(note.values())


def facturi_schema(conn, s):
    clauza = _nsf.clauza_sql(alias="f")
    with conn.cursor() as cur:
        cur.execute("SELECT f.id, f.data_emitere, f.directie, f.total, f.total_lei, f.tva, "
                    "       f.numar, f.serie, f.status, f.tip "
                    "FROM %s.facturi f WHERE %s AND COALESCE(f.tip,'factura')='factura' "
                    "ORDER BY f.id" % (s, clauza))
        return [{"id": r[0], "data_emitere": r[1], "directie": r[2],
                 "total": Decimal(str(r[3] or 0)), "total_lei": Decimal(str(r[4] or 0)),
                 "tva": Decimal(str(r[5] or 0)), "numar": r[6], "serie": r[7],
                 "status": r[8], "tip": r[9]} for r in cur.fetchall()]


def clasifica(n):
    """(atinge_tert, atinge_tva, atinge_fond) pe toate conturile notei."""
    t = v = f = False
    for cd, cc, _ in n["linii"]:
        for c in (cd, cc):
            if _e_tert(c):
                t = True
            if _e_tva(c):
                v = True
            if _e_fond(c):
                f = True
    return t, v, f


def valoare_tert(n):
    """Suma liniilor care debiteaza 4111 sau crediteaza 401/404 — totalul facturii, daca nota e o
    factura. Pe emisa tertul se DEBITEAZA (4111 = venit, 4111 = 4427); pe primita se CREDITEAZA
    (cheltuiala = 401, 4426 = 401). Suma tuturor liniilor ar da altceva, si e raportata separat."""
    s = Decimal(0)
    for cd, cc, suma in n["linii"]:
        if cd.startswith("4111") or cc.startswith("401") or cc.startswith("404"):
            s += suma
    return s


def valoare_totala(n):
    return sum((l[2] for l in n["linii"]), Decimal(0))


def _luna(d):
    return (d.year, d.month) if d is not None else None


def coliziuni(n, facturi):
    """Facturile din aceeasi luna cu suma care se potriveste. (stricte, largi)."""
    ln = _luna(n["data"])
    if ln is None:
        return [], []
    vt, vtot = valoare_tert(n), valoare_totala(n)
    stricte, largi = [], []
    for f in facturi:
        if _luna(f["data_emitere"]) != ln:
            continue
        tot = f["total_lei"] or f["total"]
        baza = tot - f["tva"]
        if vt and abs(vt - tot) <= Decimal("0.01"):
            stricte.append(f)
            largi.append(f)
        elif any(abs(x - y) <= Decimal("0.01")
                 for x in (vt, vtot) if x
                 for y in (tot, baza) if y):
            largi.append(f)
    return stricte, largi


def _nota_sintetica(linii, data=None, status="validata", sursa=None):
    from datetime import date
    return {"id": -1, "data": data or date(2026, 5, 5), "status": status, "sursa": sursa,
            "factura_id": None, "descriere": "sintetica",
            "linii": [(cd, cc, Decimal(str(s))) for cd, cc, s in linii]}


def _factura_sintetica(id_, an, luna, zi, total, tva):
    from datetime import date
    return {"id": id_, "data_emitere": date(an, luna, zi), "directie": "emisa",
            "total": Decimal(str(total)), "total_lei": Decimal(str(total)),
            "tva": Decimal(str(tva)), "numar": "SINT", "serie": "", "status": "emisa",
            "tip": "factura"}


def calibreaza():
    """METODA §22 — ambele directii de esec, rulate INAINTE de masuratoare.

    Raspunsul asteptat al sondei e ZERO. Un zero e si ce ar raporta un clasificator care nu vede
    nimic, deci fara blocul asta cifra n-ar dovedi nimic."""
    emisa = _nota_sintetica([("4111", "707", 84000), ("4111", "4427", 16000)])
    primita = _nota_sintetica([("371", "401", 84000), ("4426", "401", 16000)])
    casa = _nota_sintetica([("5311", "707", 840), ("5311", "4427", 160)])
    amort = _nota_sintetica([("6811", "2813", 500)])
    trezorerie = _nota_sintetica([("5121", "5311", 1000)])

    # 404: chiar clasa pe care prima forma a sondei o rata (achizitie de imobilizare).
    imobilizare = _nota_sintetica([("2131", "404", 84000), ("4426", "404", 16000)])

    # POZITIV: semnatura de factura e recunoscuta pe amandoua directiile, si pe 404.
    for et, n in (("emisa", emisa), ("primita", primita), ("imobilizare/404", imobilizare)):
        t, v, f = clasifica(n)
        assert t and (v or f), "CALIBRARE POZITIVA: nota sintetica de factura %s nu cade in G2" % et

    # NEGATIV: ce NU e factura nu trebuie sa cada in G2 — altfel clasificatorul spune „da" la tot.
    for et, n, asteptat_g1 in (("casa", casa, True), ("amortizare", amort, True),
                               ("trezorerie", trezorerie, False)):
        t, v, f = clasifica(n)
        assert not (t and (v or f)), "CALIBRARE NEGATIVA: nota de %s cade gresit in G2" % et
        assert (t or v or f) is asteptat_g1, \
            "CALIBRARE NEGATIVA: nota de %s nu are apartenenta G1 asteptata (%s)" % (et, asteptat_g1)

    # VALOAREA PE TERT: totalul facturii, nu suma tuturor liniilor.
    assert valoare_tert(emisa) == Decimal(100000), "CALIBRARE: valoare_tert(emisa) gresita"
    assert valoare_tert(primita) == Decimal(100000), "CALIBRARE: valoare_tert(primita) gresita"
    assert valoare_tert(imobilizare) == Decimal(100000), "CALIBRARE: valoare_tert(404) gresita"

    # COLIZIUNEA se aprinde pe suma+luna, si NU se aprinde altfel.
    potrivita = _factura_sintetica(1, 2026, 5, 20, 100000, 16000)
    alta_suma = _factura_sintetica(2, 2026, 5, 20, 123456, 19700)
    alta_luna = _factura_sintetica(3, 2026, 4, 20, 100000, 16000)
    st, lg = coliziuni(emisa, [potrivita])
    assert len(st) == 1, "CALIBRARE: coliziunea stricta nu se aprinde pe suma+luna potrivite"
    st, lg = coliziuni(emisa, [alta_suma])
    assert not st and not lg, "CALIBRARE: coliziunea se aprinde pe alta suma"
    st, lg = coliziuni(emisa, [alta_luna])
    assert not st and not lg, "CALIBRARE: coliziunea se aprinde pe alta luna"
    print("CALIBRARE: 3 pozitive (emisa · primita · imobilizare/404) · 3 negative (casa · "
          "amortizare · trezorerie) · 3 pe valoarea de tert · 3 pe coliziune — toate trecute\n")


def ruleaza():
    calibreaza()
    db.init_pool()
    with db.get_conn() as conn:
        inainte = scrieri(conn)
        sch = scheme(conn)
        assert sch, "sonda n-a gasit nicio schema activa - domeniul e gol"
        total_note = total_fara_fid = 0
        g1, g2, sarite = [], [], []
        per_schema = {}
        for s in sch:
            try:
                note = note_schema(conn, s)
                facturi = facturi_schema(conn, s)
            except Exception as e:
                conn.rollback()
                sarite.append((s, "%s: %s" % (type(e).__name__, str(e)[:80])))
                continue
            total_note += len(note)
            fara = [n for n in note if n["factura_id"] is None]
            total_fara_fid += len(fara)
            per_schema[s] = {"note": len(note), "fara_fid": len(fara), "facturi": len(facturi),
                             "g1": 0, "g2": 0}
            for n in fara:
                t, v, f = clasifica(n)
                if not (t or v or f):
                    continue
                st, lg = coliziuni(n, facturi)
                rec = dict(n, schema=s, tert=t, tva=v, fond=f,
                           val_tert=valoare_tert(n), val_tot=valoare_totala(n),
                           col_stricte=st, col_largi=lg)
                g1.append(rec)
                per_schema[s]["g1"] += 1
                if t and (v or f):
                    g2.append(rec)
                    per_schema[s]["g2"] += 1
        dupa = scrieri(conn)

    assert total_note, ("sonda n-a gasit nicio nota in nicio schema - domeniul e gol, deci orice "
                        "raspuns al ei ar fi despre nimic")

    print("DOMENIU: %d scheme active - %d note in total, din care %d FARA factura_id"
          % (len(sch), total_note, total_fara_fid))
    print("pg_stat_user_tables INAINTE: ins=%d upd=%d del=%d\n" % inainte)

    print("BBB1 — G1 (GAURA LARGA: atinge orice cont de factura, fara factura_id): %d note" % len(g1))
    print("BBB1 — G2 (SEMNATURA DE FACTURA: atinge 4111/401 SI fond/TVA):          %d note" % len(g2))
    for eticheta, lot in (("G1", g1), ("G2", g2)):
        val = [n for n in lot if (n["status"] or "") == "validata"]
        cio = [n for n in lot if (n["status"] or "") != "validata"]
        print("    %s: validate=%d - restul (ciorna/alta)=%d" % (eticheta, len(val), len(cio)))
    print()

    print("DEFALCARE pe `sursa` (G1), ca sa se vada supra-numararea:")
    pe_sursa = {}
    for n in g1:
        k = (n["sursa"] or "(null)", n["status"] or "(null)")
        pe_sursa[k] = pe_sursa.get(k, 0) + 1
    for (srs, st), k in sorted(pe_sursa.items(), key=lambda x: -x[1]):
        print("    sursa=%-12s status=%-10s  %d" % (srs, st, k))
    print()

    print("DEFALCARE pe `sursa` (G2):")
    pe_sursa2 = {}
    for n in g2:
        k = (n["sursa"] or "(null)", n["status"] or "(null)")
        pe_sursa2[k] = pe_sursa2.get(k, 0) + 1
    for (srs, st), k in sorted(pe_sursa2.items(), key=lambda x: -x[1]):
        print("    sursa=%-12s status=%-10s  %d" % (srs, st, k))
    print()

    print("BBB2 — COLIZIUNI (factura declarabila, aceeasi luna, suma potrivita):")
    for eticheta, lot in (("G1", g1), ("G2", g2)):
        for cls, cheie in (("VALIDATE", "validata"), ("TOATE", None)):
            sub = [n for n in lot if cheie is None or (n["status"] or "") == cheie]
            st = [n for n in sub if n["col_stricte"]]
            lg = [n for n in sub if n["col_largi"]]
            print("    %s / %-8s  note=%3d   cu coliziune STRICTA=%3d   cu coliziune LARGA=%3d"
                  % (eticheta, cls, len(sub), len(st), len(lg)))
    print()

    print("LISTA G1 (gaura larga), nota cu nota — ca sa se poata CITI de ce nu sunt facturi:")
    if not g1:
        print("    (niciuna)")
    for n in sorted(g1, key=lambda x: (x["schema"], x["id"])):
        print("    %s #%d %s status=%-9s sursa=%-11s tert=%s tva=%s fond=%s  val_tot=%s  col: S=%d L=%d"
              % (n["schema"], n["id"], n["data"], n["status"], n["sursa"],
                 n["tert"], n["tva"], n["fond"], n["val_tot"],
                 len(n["col_stricte"]), len(n["col_largi"])))
        print("        descriere: %s" % (n["descriere"] or "")[:110])
        print("        linii: %s" % " · ".join("%s=%s %s" % (cd, cc, s) for cd, cc, s in n["linii"]))
        for f in n["col_largi"]:
            print("        coliziune LARGA -> factura #%d %s %s%s total=%s tva=%s"
                  % (f["id"], f["directie"], f["serie"] or "", f["numar"],
                     f["total_lei"] or f["total"], f["tva"]))
    print()

    print("LISTA G2 (semnatura de factura), nota cu nota:")
    if not g2:
        print("    (niciuna)")
    for n in sorted(g2, key=lambda x: (x["schema"], x["id"])):
        print("    %s #%d %s status=%s sursa=%s val_tert=%s val_tot=%s coliziuni: stricte=%d largi=%d"
              % (n["schema"], n["id"], n["data"], n["status"], n["sursa"],
                 n["val_tert"], n["val_tot"], len(n["col_stricte"]), len(n["col_largi"])))
        print("        descriere: %s" % (n["descriere"] or "")[:110])
        for cd, cc, suma in n["linii"]:
            print("        %s = %s  %s" % (cd, cc, suma))
        for f in n["col_stricte"]:
            print("        COLIZIUNE STRICTA -> factura #%d %s %s%s total=%s tva=%s status=%s"
                  % (f["id"], f["directie"], f["serie"] or "", f["numar"],
                     f["total_lei"] or f["total"], f["tva"], f["status"]))
        for f in n["col_largi"]:
            if f not in n["col_stricte"]:
                print("        coliziune LARGA   -> factura #%d %s %s%s total=%s tva=%s"
                      % (f["id"], f["directie"], f["serie"] or "", f["numar"],
                         f["total_lei"] or f["total"], f["tva"]))
    print()

    print("PE SCHEMA:")
    for s in sch:
        d = per_schema.get(s)
        if not d:
            continue
        print("    %-12s note=%3d fara_fid=%3d facturi_decl=%3d  G1=%2d G2=%2d"
              % (s, d["note"], d["fara_fid"], d["facturi"], d["g1"], d["g2"]))
    if sarite:
        print("\nSCHEME NEMASURABILE: %d" % len(sarite))
        for s, motiv in sarite:
            print("    SARIT %s - %s" % (s, motiv))

    delta = tuple(b - a for a, b in zip(inainte, dupa))
    print("\npg_stat_user_tables DUPA: ins=%d upd=%d del=%d" % dupa)
    print("DELTA scrieri: ins=%+d upd=%+d del=%+d  ->  %s"
          % (delta + ("SONDA N-A SCRIS" if delta == (0, 0, 0) else "*** A SCRIS ***",)))
    return g1, g2, sarite, delta


if __name__ == "__main__":
    g1, g2, sar, delta = ruleaza()
    print("\nVERDICT BBB")
    print("  BBB1 gaura larga (G1):        %d note (validate: %d)"
          % (len(g1), len([n for n in g1 if (n["status"] or "") == "validata"])))
    print("  BBB1 semnatura factura (G2):  %d note (validate: %d)"
          % (len(g2), len([n for n in g2 if (n["status"] or "") == "validata"])))
    print("  BBB2 coliziuni STRICTE pe G2: %d" % len([n for n in g2 if n["col_stricte"]]))
    print("  BBB2 coliziuni LARGI pe G2:   %d" % len([n for n in g2 if n["col_largi"]]))
    print("  scrieri: %s" % ("ZERO" if delta == (0, 0, 0) else str(delta)))
