# -*- coding: utf-8 -*-
"""core/migrare_retest_0810.py — migrările lotului „Retest 08.10” (comanda Costin 08.10.2026, verbatim în DECIZII).

  · pct.1  analiticul TVA-ului din prețul de raft (`stocuri.CONT_TVA_STOC` = 4428.02) în planul fiecărei firme, iar SOLDURILE EXISTENTE
           mutate pe el: rândurile pe 4428 cu contrapartida 371 (NIR global-valoric `371 = 4428`, descărcarea `4428 = 371`) trec pe
           analitic; soldul inițial 4428 trece numai la firma global-valorică fără TVA la încasare (acolo 4428 nu poate fi altceva).
           Orice alt sold 4428 rămâne pe loc și se RAPORTEAZĂ — nu se ghicește a cui e. Un rând într-o perioadă închisă nu se atinge
           (triggerul de perioadă refuză; se raportează).
  · pct.4  NIR-urile „fără factură” scrise în forma veche (371 = 401, 4426 = 401; nelegate, nerefăcute) primesc câte o notă de
           REFACERE, ciornă care trece din nou prin validare: stornarea în roșu a costului și a TVA-ului de pe 401 și forma nouă
           (371 = 408, 4428.01 = 408). Notele validate de atunci nu se rescriu — istoria rămâne (OMFP 1802/2014 pct.69: „corectarea cu
           semnul minus a operațiunii inițiale (stornare în roșu)”, același exercițiu). Autorul notei de refacere e autorul NIR-ului:
           la un autor fără „Poate valida” nota intră în coadă (`uc_coada.note_in_coada`), ca orice notă pregătită de el.
  · pct.17 conturile 731–738 (OMFP 3103/2017, venituri ale entităților fără scop patrimonial) se scot din planul firmelor care NU le
           folosesc și în al căror plan legal nu sunt (`plan_legal.in_afara`: societatea comercială, norma OMFP 1802/2014). „Folosit” =
           orice coloană de cont din schemă (`cont%`, text) care îl poartă, sintetic sau analitic — note, solduri inițiale, articole,
           mijloace fixe, profilul firmei. Un cont folosit rămâne și se RAPORTEAZĂ.
Sursa UNICĂ (mirror în tenant_template.sql). Idempotentă. `python3 -m core.migrare_retest_0810`.
"""
import json
from core import db
from core.stocuri import CONT_TVA_STOC



def descriere_refacere_nir(numar):
    """Descrierea notei de refacere a unui NIR fără factură, în cuvintele contabilului. [Retest 2 pct.2] Prima formă purta proveniența
    internă („decizia Costin 08.10, pct.4”) în descrierea notei, adică pe ecranul „Note de validat” și în registrul-jurnal."""
    return ("Refacere NIR nr. %s fără factură: costul și TVA-ul trec de pe 401 pe 408 (furnizori - facturi nesosite) și 4428.01 "
            "(TVA neexigibilă), până la sosirea facturii" % numar)[:200]

def plan_si_solduri_tva_stoc(conn, schema):
    """{"plan", "linii", "solduri", "raportat"} pentru o schemă; None dacă schema n-are `plan_conturi`."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='plan_conturi'", (schema,))
        if not cur.fetchone():
            return None
        cur.execute('INSERT INTO "{s}".plan_conturi (simbol, denumire, tip) VALUES (%s, %s, %s) ON CONFLICT (simbol) DO NOTHING'
                    .format(s=schema), (CONT_TVA_STOC, "TVA neexigibilă aferentă mărfurilor (preț de vânzare)", "Bifunctional"))
        plan = cur.rowcount
        cur.execute('UPDATE "{s}".inregistrari_linii SET cont_credit = %s WHERE cont_credit = %s AND cont_debit = %s'.format(s=schema),
                    (CONT_TVA_STOC, "4428", "371"))
        linii = cur.rowcount
        cur.execute('UPDATE "{s}".inregistrari_linii SET cont_debit = %s WHERE cont_debit = %s AND cont_credit = %s'.format(s=schema),
                    (CONT_TVA_STOC, "4428", "371"))
        linii += cur.rowcount
        cur.execute('SELECT metoda_stoc, COALESCE(tva_la_incasare, false) FROM "{s}".firma_profil WHERE id = 1'.format(s=schema))
        r = cur.fetchone()
        gv_fara_tvai = bool(r) and r[0] == "global_valoric" and not r[1]
        solduri = raportat = 0
        if gv_fara_tvai:
            cur.execute('UPDATE "{s}".solduri_initiale SET cont = %s WHERE cont = %s'.format(s=schema), (CONT_TVA_STOC, "4428"))
            solduri = cur.rowcount
        else:
            cur.execute('SELECT count(*) FROM "{s}".solduri_initiale WHERE cont = %s'.format(s=schema), ("4428",))
            raportat = cur.fetchone()[0]
    return {"plan": plan, "linii": linii, "solduri": solduri, "raportat": raportat}


def _q2(x):
    from decimal import Decimal, ROUND_HALF_UP
    return Decimal(str(x or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def refa_nir_forma_veche(conn, schema):
    """[(nir_id, numar, nota_id, autor)] — notele de refacere scrise (ciorne). Sare peste NIR-urile deja refăcute (idempotent), legate,
    refăcute din alt NIR sau din perioade închise (acestea se raportează, nu se ating)."""
    from core import nir_legare as _nl
    from core import stocuri_api as _sa
    from core import jurnal_api as _j
    s = '"%s".' % schema
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT id, numar, data, cost_total, transport, taxe, inregistrari_ids FROM %snir n WHERE factura_id IS NULL "
                    "AND NOT EXISTS (SELECT 1 FROM %snir r WHERE r.refacut_din_id = n.id) ORDER BY id" % (s, s))
        nirs = [dict(zip(("id", "numar", "data", "cost_total", "transport", "taxe", "inregistrari_ids"), r)) for r in cur.fetchall()]
        for n in nirs:
            note = _sa.note_nir(n)
            if not note:
                continue
            cur.execute("SELECT 1 FROM %sinregistrari WHERE id = ANY(%%s) AND numar = %%s" % s, (note, "REFACERE-NIR-%d" % n["id"]))
            if cur.fetchone():
                continue   # deja refăcut
            cur.execute("SELECT COALESCE(SUM(suma) FILTER (WHERE cont_debit = '371' AND cont_credit = '401'), 0), "
                        "COALESCE(SUM(suma) FILTER (WHERE cont_debit = '4426' AND cont_credit = '401'), 0), "
                        "COALESCE(SUM(suma) FILTER (WHERE cont_credit = %%s), 0), min(i.creat_de_id) "
                        "FROM %sinregistrari_linii l JOIN %sinregistrari i ON i.id = l.inregistrare_id WHERE i.id = ANY(%%s)" % (s, s),
                        (_nl.CONT_NESOSITE, note))
            pe_401, tva_401, pe_408, autor = cur.fetchone()
            if not pe_401 or pe_408:
                continue   # nu e forma veche „fără factură” (NIR legat la creare, sau deja pe 408)
            cost = _q2(_q2(n["cost_total"]) - _q2(n["transport"]) - _q2(n["taxe"]))
            tva = _q2(tva_401)
            cur.execute("SAVEPOINT refacere_nir")
            try:
                cur.execute("INSERT INTO %sinregistrari (data, numar, descriere, sursa, status, document_ref, creat_de_id) "
                            "VALUES (%%s, %%s, %%s, 'stocuri', 'ciorna', %%s, %%s) RETURNING id" % s,
                            (n["data"], "REFACERE-NIR-%d" % n["id"],
                             descriere_refacere_nir(n["numar"]),
                             _j.eticheta_document("NIR", n["numar"], n["data"]), autor))
                nid = cur.fetchone()[0]
                for d, c, suma in (("371", "401", -cost), ("4426", "401", -tva), ("371", _nl.CONT_NESOSITE, cost),
                                   (_nl.CONT_TVA_NIR, _nl.CONT_NESOSITE, tva)):
                    if suma:
                        cur.execute("INSERT INTO %sinregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES "
                                    "(%%s, %%s, %%s, %%s)" % s, (nid, d, c, suma))
                cur.execute("UPDATE %snir SET inregistrari_ids = %%s WHERE id = %%s" % s, (json.dumps(note + [nid]), n["id"]))
                cur.execute("RELEASE SAVEPOINT refacere_nir")
            except Exception as e:  # noqa: BLE001 — perioadă închisă: se raportează, nu se ocolește triggerul
                cur.execute("ROLLBACK TO SAVEPOINT refacere_nir")
                out.append((n["id"], n["numar"], None, "NEREFĂCUT: %s" % str(e).split("\n")[0][:160]))
                continue
            out.append((n["id"], n["numar"], nid, autor))
    return out


def _scheme(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
        return [x[0] for x in cur.fetchall()]


CONTURI_73X = ("731", "732", "733", "734", "736", "738")   # exact cele semănate de șablonul vechi


def scoate_conturi_73x(conn, schema):
    """{"scoase": [...], "folosite": {cont: [tabel.coloana, …]}, "in_plan_legal": [...]}; None dacă schema n-are `plan_conturi`."""
    from core import plan_legal
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='plan_conturi'", (schema,))
        if not cur.fetchone():
            return None
        cur.execute('SELECT simbol FROM "{s}".plan_conturi WHERE simbol = ANY(%s)'.format(s=schema), (list(CONTURI_73X),))
        prezente = sorted(r[0] for r in cur.fetchall())
        legale = [c for c in prezente if c not in plan_legal.in_afara(cur, schema, prezente)]
        cur.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = %s AND column_name LIKE 'cont%%' "
                    "AND data_type IN ('text', 'character varying') AND table_name <> 'plan_conturi'", (schema,))
        coloane = cur.fetchall()
        folosite, scoase = {}, []
        for c in prezente:
            if c in legale:
                continue
            for t, col in coloane:
                cur.execute('SELECT 1 FROM "{s}"."{t}" WHERE "{c}" = %s OR "{c}" LIKE %s LIMIT 1'.format(s=schema, t=t, c=col), (c, c + ".%"))
                if cur.fetchone():
                    folosite.setdefault(c, []).append("%s.%s" % (t, col))
            if c not in folosite:
                cur.execute('DELETE FROM "{s}".plan_conturi WHERE simbol = %s'.format(s=schema), (c,))
                scoase.append(c)
    return {"scoase": scoase, "folosite": folosite, "in_plan_legal": legale}


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = _scheme(conn)
        tot = {"plan": 0, "linii": 0, "solduri": 0, "raportat": 0}
        for s in scheme:
            try:
                r = plan_si_solduri_tva_stoc(conn, s)
                conn.commit()
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                print("  ESEC", s, e)
                continue
            if r:
                for k in tot:
                    tot[k] += r[k]
                if r["linii"] or r["solduri"] or r["raportat"]:
                    print("  ", s, r)
    print("pct.1 4428.02: %d scheme; %s" % (len(scheme), tot))
    # pct.17 — 731–738 din planul firmelor care nu le folosesc
    for s in scheme:
        try:
            with db.get_conn() as conn:
                r = scoate_conturi_73x(conn, s)
                conn.commit()
        except Exception as e:  # noqa: BLE001
            print("  ESEC 73x", s, e)
            continue
        if r and (r["scoase"] or r["folosite"] or r["in_plan_legal"]):
            print("  pct.17", s, r)
    # pct.4 — notele de refacere, apoi coada (autorul fără drept de validare -> coada cabinetului firmei)
    from core import uc_coada as _uq
    for s in scheme:
        with db.get_conn() as c2, c2.cursor() as cur:
            cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name = %s", (s,))
            t = cur.fetchone()
        try:
            with db.get_conn() as conn:
                r = refa_nir_forma_veche(conn, s)
                conn.commit()
        except Exception as e:  # noqa: BLE001
            print("  ESEC refacere", s, e)
            continue
        for nir_id, numar, nid, autor in r:
            print("  pct.4", s, "NIR", nir_id, numar, "-> nota", nid, "autor", autor)
            if nid and autor and t:
                print("     coada:", _uq.note_in_coada(t[0], autor, t[1]))


if __name__ == "__main__":
    _main()
