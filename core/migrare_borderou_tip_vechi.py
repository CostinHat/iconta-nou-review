# -*- coding: utf-8 -*-
"""core/migrare_borderou_tip_vechi.py — borderourile de achiziție scrise înainte de lotul 9 trec pe tipul lor, `facturi.tip = 'borderou'`
(lotul 11, C75; decizia Costin, comanda 11.1 pct.2, verbatim: „C75: DA. Migrează borderourile vechi pe toate firmele, inclusiv pe cabinetul
pilot.”).

C75 (DEFICIENTE, găsită la reparația F1 a lui 434): până la lotul 9 (publicat 20.10.2026, restart 05:06:34) „Achiziție de la neînregistrat”
scria borderoul ca factură primită cu tipul implicit („factura”); numerotarea BA (`documente_interne.cel_mai_mare` /
`borderou_cu_numarul`) și indexul unic `facturi_borderou_numar_an_uniq` văd numai `tip = 'borderou'`, deci la o firmă cu borderouri vechi
aplicația poate da din nou un număr deja dat (cauza lui 434 pe F1).

CRITERIUL — EXACT forma pe care o scria codul de dinainte (`uc_tenants.achizitie_neinregistrat` în `27f4fab3`, lotul 8: `creeaza_factura(…
directie="primita", linii=[{descr, cantitate 1, cota 0}], tert_cui="", status="importata", tert_platitor_tva=False, tert_pf=True)` +
`nota_facturi_cu_factura(… descr)`), toate condițiile deodată, ca o factură primită reală să nu poată intra:
  · `tip` implicit („factura”), `directie = 'primita'`, fără factură de stornare legată (`storno_din_id` gol);
  · vânzător FĂRĂ cod fiscal (`tert_cui` gol) și neplătitor de TVA (`tert_platitor_tva = false`) — o factură primită cere codul
    furnizorului (`facturi_api.cere_cod_partener`; singura excepție, `tert_pf=True`, o folosea numai drumul borderoului);
  · `status = 'importata'` și fără XML (`xml` gol) — nu vine din SPV / e-Factura;
  · EXACT un rând, cantitatea 1, cota 0, cu descrierea „<descriere> - <vânzătorul>” (forma lui `descr`);
  · nota de contare a facturii (`factura_id`, sursa „facturi”) cu ACEEAȘI descriere;
  · scrisă înainte de restartul lotului 9 (`creat_la` < 20.10.2026 05:06:34 EEST): de atunci borderoul se scrie cu tipul lui.
O factură primită care îndeplinește doar o parte NU se atinge: se listează la „neconvertite”, cu condiția care lipsește.

COLIZIUNILE de număr (același număr în același an, ca indexul unic: `upper(btrim(numar))`): păstrează numărul cel mai vechi (data, apoi
id-ul) — ori borderoul din luna închisă, al cărui număr nu se mai poate schimba —, iar celelalte primesc `BA-<următorul>` după cel mai mare
BA al anului, în ordinea (data, id) — cum s-a făcut pe F1 la 434 (al doilea BA-1 -> BA-2). Documentul mișcărilor de stoc ale unui borderou
(„Borderou de achiziție BA-1 din …”, fișa de magazie) se aliniază la numărul lui, cât mișcarea nu e în evidență (notă validată: rămâne, și
se spune).

LUNA ÎNCHISĂ: triggerul perioadei blocate refuză orice schimbare pe o factură din luna închisă; borderoul vechi de acolo NU se convertește —
se raportează (redeschiderea lunii e decizia contabilului). Declarațiile nu se schimbă prin conversie: `nomenclator_status_factura.
TIPURI_FISCALE` cuprinde ambele tipuri.

Idempotentă: a doua rulare nu mai găsește nimic. Fiecare firmă se comite separat și se raportează (convertite, renumerotate, mișcări
aliniate, neconvertite cu motivul). Nu scrie în note (`core/test_migrari_registru.py`).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_borderou_tip_vechi.py` (după `migrare_borderou_numar_unic`).
"""
import re

from core import db

#: restartul publicării lotului 9 (ISTORIC, 20.10.2026: „restart 05:06:34, four-way închis”): de atunci borderoul are `tip = 'borderou'`
DATA_LOT9 = "2026-10-20 05:06:34+03:00"
PREFIX = "BA-"


def _s(schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    return '"%s"' % schema


def _luni_inchise(cur, s):
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", ("%s.perioade_blocate" % s,))
    if not cur.fetchone()[0]:
        return set()
    cur.execute("SELECT an, luna FROM %s.perioade_blocate" % s)
    return {(int(a), int(l)) for a, l in cur.fetchall()}


def candidati(cur, schema):
    """[{id, numar, data, vanzator, motiv}] — facturile primite fără cod de vânzător, `importata`, fără XML, cu tipul implicit; `motiv`
    None = borderou vechi (toate condițiile), altfel condiția care lipsește (se raportează, nu se atinge)."""
    s = _s(schema)
    cur.execute(f"""SELECT f.id, f.numar, f.data_emitere, f.tert_nume, f.creat_la < %s::timestamptz AS vechi,
                           (SELECT count(*) FROM {s}.factura_linii l WHERE l.factura_id = f.id) AS n_linii,
                           (SELECT l.descriere FROM {s}.factura_linii l WHERE l.factura_id = f.id
                             AND l.cantitate = 1 AND COALESCE(l.cota_tva, 0) = 0 ORDER BY l.id LIMIT 1) AS linie
                    FROM {s}.facturi f
                    WHERE COALESCE(f.tip, 'factura') = 'factura' AND f.directie = 'primita' AND f.storno_din_id IS NULL
                      AND COALESCE(btrim(f.tert_cui), '') = '' AND f.tert_platitor_tva IS FALSE
                      AND f.status = 'importata' AND COALESCE(f.xml, '') = ''
                    ORDER BY f.data_emitere, f.id""", (DATA_LOT9,))
    out = []
    for fid, numar, data, vanz, vechi, n_linii, linie in cur.fetchall():
        motiv = None
        if not vechi:
            motiv = "scrisă după lotul 9 (de atunci borderoul are tipul lui): nu e forma veche"
        elif n_linii != 1 or linie is None:
            motiv = "nu are exact un rând cu cantitatea 1 și cota 0"
        elif not str(linie).endswith(" - " + str(vanz or "")):
            motiv = "rândul nu are forma borderoului vechi („<descriere> - <vânzător>”)"
        else:
            cur.execute(f"SELECT 1 FROM {s}.inregistrari WHERE factura_id = %s AND sursa = 'facturi' AND descriere = %s LIMIT 1",
                        (fid, linie))
            if not cur.fetchone():
                motiv = "nu are nota de contare cu aceeași descriere (forma borderoului vechi)"
        out.append({"id": fid, "numar": numar, "data": data, "vanzator": vanz, "motiv": motiv})
    return out


def _cheie(numar, data):
    return (str(numar or "").strip().upper(), data.year)


def plan(cur, schema):
    """{"convertite": [rând], "renumerotate": [(id, număr vechi, număr nou)], "neconvertite": [(rând, motiv)]} — ce ar face migrarea,
    fără să scrie."""
    s = _s(schema)
    inchise = _luni_inchise(cur, s)
    conv, necon = [], []
    for c in candidati(cur, schema):
        if c["motiv"]:
            necon.append((c, c["motiv"]))
        elif (c["data"].year, c["data"].month) in inchise:
            necon.append((c, "luna %02d/%d e închisă: borderoul vechi rămâne cu tipul „factura” până la redeschiderea ei"
                          % (c["data"].month, c["data"].year)))
        else:
            conv.append(c)
    cur.execute(f"SELECT id, numar, data_emitere FROM {s}.facturi WHERE tip = 'borderou' ORDER BY data_emitere, id")
    existente = [{"id": i, "numar": n, "data": d, "existent": True} for i, n, d in cur.fetchall()]
    toate = existente + [dict(c, existent=False) for c in conv]
    maxim = {}
    for r in toate:
        m = re.fullmatch(re.escape(PREFIX) + r"([0-9]{1,9})", str(r["numar"] or "").strip().upper())
        if m:
            maxim[r["data"].year] = max(maxim.get(r["data"].year, 0), int(m.group(1)))
    grupe = {}
    for r in toate:
        grupe.setdefault(_cheie(r["numar"], r["data"]), []).append(r)
    renum = []
    for _k, g in sorted(grupe.items(), key=lambda kv: min((r["data"], r["id"]) for r in kv[1])):
        if len(g) < 2:
            continue
        g = sorted(g, key=lambda r: (r["data"], r["id"]))
        fix = next((r for r in g if (r["data"].year, r["data"].month) in inchise), g[0])
        for r in g:
            if r is fix:
                continue
            an = r["data"].year
            maxim[an] = maxim.get(an, 0) + 1
            renum.append((r["id"], r["numar"], PREFIX + str(maxim[an])))
    return {"convertite": conv, "renumerotate": renum, "neconvertite": necon}


def aplica(conn, schema):
    """Scrie planul în tranzacția `conn` (fără commit). Întoarce raportul firmei (planul + mișcările aliniate / lăsate)."""
    from core import jurnal_api as _j
    s = _s(schema)
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s) IS NOT NULL", ("%s.facturi" % s,))
        if not cur.fetchone()[0]:
            return {"convertite": [], "renumerotate": [], "neconvertite": [], "miscari": [], "miscari_lasate": []}
        p = plan(cur, schema)
        for fid, _vechi, nou in p["renumerotate"]:
            cur.execute(f"UPDATE {s}.facturi SET numar = %s WHERE id = %s", (nou, fid))
        if p["convertite"]:
            cur.execute(f"UPDATE {s}.facturi SET tip = 'borderou' WHERE id = ANY(%s)", ([c["id"] for c in p["convertite"]],))
        # documentul mișcărilor de stoc ale borderourilor, aliniat la numărul lor (fișa de magazie), cât mișcarea nu e în evidență
        # (regula de fond R5: mișcarea în evidență nu se modifică — aceeași funcție din bază, `miscare_in_evidenta`; luna închisă nu se atinge)
        inchise = _luni_inchise(cur, s)
        cur.execute(f"""SELECT m.id, m.document, f.serie, f.numar, f.data_emitere, m.data, {s}.miscare_in_evidenta(m.id) AS in_evidenta
                        FROM {s}.miscari_stoc m JOIN {s}.facturi f ON f.id = m.factura_id
                        WHERE f.tip = 'borderou' AND m.document LIKE 'Borderou de achiziție %%' ORDER BY m.id""")
        miscari, lasate = [], []
        for mid, doc, serie, numar, data, data_m, in_ev in cur.fetchall():
            corect = _j.eticheta_factura("borderou", serie, numar, data)
            if doc == corect:
                continue
            if in_ev or (data_m.year, data_m.month) in inchise:
                lasate.append((mid, doc, corect))
                continue
            cur.execute(f"UPDATE {s}.miscari_stoc SET document = %s WHERE id = %s", (corect[:100], mid))
            miscari.append((mid, doc, corect))
    return {**p, "miscari": miscari, "miscari_lasate": lasate}


def verifica(conn, schema):
    """După rulare: niciun borderou vechi convertibil rămas și nicio dublură de număr între borderouri."""
    with conn.cursor() as cur:
        p = plan(cur, schema)
    return not p["convertite"] and not p["renumerotate"]


def text_raport(schema, r):
    from core import pdf_util as _pu
    from core.common import cate as _cate
    lin = ["%s: %s, %s, %s, %s" % (
        schema, _cate(len(r["convertite"]), "borderou convertit", "borderouri convertite"),
        _cate(len(r["renumerotate"]), "număr schimbat", "numere schimbate"),
        _cate(len(r["miscari"]), "mișcare aliniată", "mișcări aliniate"),
        _cate(len(r["neconvertite"]), "candidat neconvertit", "candidați neconvertiți"))]
    lin += ["  convertit: %s din %s (%s)" % (c["numar"], _pu.data_ro(c["data"]), c["vanzator"]) for c in r["convertite"]]
    lin += ["  renumerotat: %s -> %s" % (v, n) for _i, v, n in r["renumerotate"]]
    lin += ["  mișcare aliniată: «%s» -> «%s»" % (v, n) for _i, v, n in r["miscari"]]
    lin += ["  mișcare în evidență, lăsată: «%s» (numărul de acum: «%s»)" % (v, n) for _i, v, n in r.get("miscari_lasate", [])]
    lin += ["  neconvertit: %s din %s (%s) — %s" % (c["numar"], _pu.data_ro(c["data"]), c["vanzator"], m) for c, m in r["neconvertite"]]
    return "\n".join(lin)


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                r = aplica(conn, s)
                conn.commit()
            ok += 1
            if r["convertite"] or r["renumerotate"] or r["miscari"] or r["neconvertite"] or r["miscari_lasate"]:
                print(text_raport(s, r))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_borderou_tip_vechi: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
