# -*- coding: utf-8 -*-
"""NIR-ul „fără factură” legat la contarea facturii (decizia Costin 08.10.2026, pct.2 — D2 în ordinea inversă).

Comanda, verbatim: „la contarea facturii se propune legarea cu NIR-ul nelegat de la același furnizor (preselecție permisă —
dedusă din date, vizibilă, modificabilă). Dacă contabilul nu leagă, confirmă explicit «altă livrare»; nu se blochează. Se elimină
astfel dubla încărcare a lui 371.”

DE CE. La global-valoric, un NIR nelegat scrie complet: 371=401 (costul), 4426=401 (TVA), 371=378, 371=4428
(`stocuri.nir_gv`). Factura aceleiași livrări, contată după el pe 371, scria din nou 371=401 + 4426=401 — costul și TVA
deductibilă de două ori. Ordinea directă (NIR legat la creare, decizia 07.10 pct.2) scrie numai adaosul și TVA neexigibilă;
ordinea inversă trebuie să ajungă în ACEEAȘI stare.

CUM. Legarea scrie o notă de stornare în ROȘU a costului NIR-ului (371=401 −costul de bază, 4426=401 −TVA lui), documentul =
NIR-ul, în `nir.inregistrari_ids`, și pune `nir.factura_id`. Factura se contează ÎNTREAGĂ (documentul fiscal al costului și al
deducerii: CF art.299 alin.(1) lit.a) cere factura pentru deducere), iar NIR-ul rămâne cu adaosul și TVA neexigibilă — exact
starea din ordinea directă. OMFP 1802/2014 pct.69: „Înregistrarea stornării unei operațiuni contabile aferente exercițiului
financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin
înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate.”
*INTERPRETARE CU TEMEI:* roșu, nu negru — coeficientul K al descărcării lunare citește RULAJUL DEBITOR al lui 371
(`stocuri.coeficient_k`); o stornare în negru (401=371) l-ar lăsa cu costul de două ori și K ar ieși greșit. Aceeași alegere ca la
stornarea stocului (R1, `stocuri_anulare`). De reconfirmat dacă politica contabilă a firmei cere negru.

LIMITE, declarate: (1) numai NIR-uri din ACELAȘI exercițiu cu nota facturii — pct.69 vorbește despre „exercițiul financiar
curent”; un NIR din exercițiul trecut nu se stornează de aici. (2) Costul NIR-ului (fără transport și taxe) trebuie să fie netul
facturii în lei, la ban — altfel nu e aceeași livrare (ca la ordinea directă, `COST_DIFERIT_DE_FACTURA`). (3) Numai global-valoric:
la cantitativ-valoric factura face ea însăși intrarea în fișă, iar legarea nu e decisă (vezi `core/test_datorie.py`).
"""
from decimal import Decimal, ROUND_HALF_UP

from core import facturi as _fc
from core import metoda_stoc as _ms
from core import sume_lei as _sl

#: valoarea care confirmă explicit „altă livrare” (factura nu e a niciunuia din NIR-urile nelegate)
ALTA_LIVRARE = "alta_livrare"
COD_DE_ALES = "NIR_DE_LEGAT"
COD_NELEGABIL = "NIR_NELEGABIL"
COD_COST = "COST_DIFERIT_DE_FACTURA"
#: refuzurile alegerii — rutele le întorc STRUCTURAT (candidații, propunerea, câmpul), ca ecranul să poată cere alegerea
CODURI = (COD_DE_ALES, COD_NELEGABIL, COD_COST)
#: contul pe care factura primită de marfă îl încarcă (`facturi.ACHIZITIE["marfa"]`)
CONT_MARFA = _fc.ACHIZITIE["marfa"]
TEMEI = "OMFP 1802/2014 pct.69"
#: mențiunea care rămâne în descrierea notei facturii când omul confirmă „altă livrare”
MENTIUNE_ALTA_LIVRARE = " · altă livrare decât NIR-urile nelegate (confirmat)"


def _q2(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _cui(v):
    return "".join(ch for ch in str(v or "") if ch.isdigit())


def _p(schema):
    return ('"%s".' % str(schema).strip('"')) if schema else ""


def net_lei(f):
    """Netul facturii în lei (totalul fără TVA), la ban."""
    tl, vl = _sl.antet_lei(f)
    return _q2(tl - vl)


def se_aplica(cur, schema, f, note):
    """Factura primită care încarcă 371 la o firmă cu stocul la preț de vânzare (global-valoric)?"""
    if (f.get("directie") or "") != "primita":
        return False
    if not any(str(n.get("debit")) == CONT_MARFA for n in note):
        return False
    return _ms.citeste(cur, schema) == _ms.GV


def candidati(cur, schema, f, data_nota):
    """NIR-urile pe care factura le poate închide: global-valoric, nelegate, de la același furnizor (CUI), din exercițiul notei,
    nerespinse și nerefăcute. Fiecare: {id, numar, data, cost, eticheta, acelasi_cost}."""
    from core import coada_api as _cq
    from core import stocuri_api as _sa
    cui = _cui(f.get("tert_cui"))
    if not cui:
        return []
    an = int(str(data_nota)[:4])
    s = _p(schema)
    cur.execute("SELECT id, numar, data, cui, cost_total, transport, taxe, inregistrari_ids FROM %snir "
                "WHERE factura_id IS NULL AND metoda_stoc = %%s AND EXTRACT(YEAR FROM data) = %%s "
                "AND NOT EXISTS (SELECT 1 FROM %snir r WHERE r.refacut_din_id = %snir.id) ORDER BY data, id" % (s, s, s),
                (_ms.GV, an))
    nirs = [dict(r) for r in cur.fetchall() if _cui(r["cui"]) == cui]
    if not nirs:
        return []
    tenant = _tenant(cur, schema)
    stari = _cq.stari_note(cur.connection, tenant, [i for n in nirs for i in _sa.note_nir(n)]) if tenant else {}
    net = net_lei(f)
    out = []
    for n in nirs:
        if any((stari.get(i) or {}).get("stare_coada") == "respinsa" for i in _sa.note_nir(n)):
            continue   # NIR respins: se reface, iar NIR-ul refăcut e cel care se leagă
        cost = _q2(Decimal(str(n["cost_total"] or 0)) - Decimal(str(n["transport"] or 0)) - Decimal(str(n["taxe"] or 0)))
        from core import pdf_util as _pu
        out.append({"id": n["id"], "numar": n["numar"], "data": str(n["data"])[:10], "cost": str(cost),
                    "acelasi_cost": cost == net,
                    "eticheta": "NIR nr %s din %s · cost %s lei" % (n["numar"], _pu.data_ro(n["data"]), cost)})
    return out


def alegerea(nir_id=None, alta_livrare=False):
    """Alegerea trimisă de om, într-o singură valoare pentru `contare_facturi.contabilizeaza(nir_legat=)`."""
    return ALTA_LIVRARE if alta_livrare else (nir_id if nir_id not in (None, "") else None)


def detaliu_refuz(e):
    """Refuzul alegerii ca obiect pentru stratul HTTP: {cod, mesaj, camp, candidati, propus, ...}."""
    from core import afirmatii as _af   # afirmație tipată (P8); `cod` / `mesaj` / detaliile pentru ecran
    return dict(_af.afirmatie("neconformitate", "legare_nir", e.mesaj, unde="factura primită",
                              regula="aceeași livrare se înregistrează o singură dată (OMFP 1802/2014 pct.69)"),
                cod=e.cod, mesaj=e.mesaj, **(e.detalii or {}))


def propus(cands):
    """Propunerea DEDUSĂ: singurul NIR cu costul egal cu netul facturii. Niciunul sau mai mulți -> nicio propunere."""
    egale = [c["id"] for c in cands if c["acelasi_cost"]]
    return egale[0] if len(egale) == 1 else None


def _tenant(cur, schema):
    cur.execute("SELECT id FROM public.tenants WHERE schema_name = COALESCE(NULLIF(%s, ''), current_schema())",
                (str(schema or "").strip('"'),))
    r = cur.fetchone()
    return (r["id"] if isinstance(r, dict) else r[0]) if r else None


def refuz_de_ales(f, cands):
    """(cod, mesaj, detalii) — factura are NIR-uri nelegate de la furnizorul ei și nu s-a ales nimic."""
    p = propus(cands)
    et = ("%s %s" % (f.get("serie") or "", f.get("numar") or "")).strip()
    mesaj = ("Factura %s e de la un furnizor cu %s NIR „fără factură” nelegat. Dacă e aceeași livrare, leag-o de NIR — altfel "
             "371 s-ar încărca de două ori. Dacă nu e, confirmă „altă livrare”." % (et, len(cands)))
    return COD_DE_ALES, mesaj, {"camp": "nir-legat", "candidati": cands, "propus": p, "factura_id": f.get("id"),
                                "alta_livrare": ALTA_LIVRARE}


def verifica_alegerea(cands, f, nir_id):
    """Alegerea unui NIR: e printre candidați și are costul facturii. Întoarce (candidatul, None) sau (None, (cod, mesaj))."""
    try:
        nid = int(nir_id)
    except (TypeError, ValueError):
        return None, (COD_NELEGABIL, "NIR-ul ales nu e valid.")
    c = next((x for x in cands if x["id"] == nid), None)
    if c is None:
        return None, (COD_NELEGABIL, "NIR-ul ales nu se poate lega de factura asta: nu e un NIR „fără factură” nelegat, de la "
                                     "același furnizor, din același exercițiu.")
    if not c["acelasi_cost"]:
        return None, (COD_COST, "Costul din NIR-ul %s (%s lei fără TVA) nu e netul facturii (%s lei). La legare costul vine din "
                                "factură — nu e aceeași livrare, sau unul din documente are altă sumă." % (c["numar"], c["cost"],
                                                                                                           net_lei(f)))
    return c, None


def leaga(cur, schema, nir_id, f, data_nota):
    """Leagă NIR-ul de factură: nota de stornare în roșu a costului lui (371=401, 4426=401), documentul = NIR-ul, în
    `inregistrari_ids`, și `nir.factura_id`. Întoarce id-ul notei de stornare."""
    import json
    from core import jurnal_api as _j
    from core import stocuri_api as _sa
    s = _p(schema)
    cur.execute("SELECT id, numar, data, cost_total, transport, taxe, inregistrari_ids FROM %snir WHERE id = %%s FOR UPDATE" % s,
                (int(nir_id),))
    n = dict(cur.fetchone())
    note = _sa.note_nir(n)
    cur.execute("SELECT COALESCE(SUM(suma), 0) FROM %sinregistrari_linii WHERE inregistrare_id = ANY(%%s) "
                "AND cont_debit = '4426' AND cont_credit = '401'" % s, (note,))
    r = cur.fetchone()
    tva = _q2(r[0] if not isinstance(r, dict) else list(r.values())[0])
    cost = _q2(Decimal(str(n["cost_total"] or 0)) - Decimal(str(n["transport"] or 0)) - Decimal(str(n["taxe"] or 0)))
    stornare = _fc.storno([{"debit": CONT_MARFA, "credit": "401", "suma": cost}] +
                          ([{"debit": "4426", "credit": "401", "suma": tva}] if tva else []))
    fact = ("%s %s" % (f.get("serie") or "", f.get("numar") or "")).strip()
    doc = _j.eticheta_document("NIR", n["numar"], n["data"])
    cur.execute("INSERT INTO %sinregistrari (data, descriere, sursa, status, document_ref) VALUES (%%s,%%s,'stocuri','ciorna',%%s) "
                "RETURNING id" % s,
                (data_nota, ("Stornare cost NIR %s — costul vine din factura %s (legată la contare; %s)" % (n["numar"], fact, TEMEI))[:200],
                 doc))
    r = cur.fetchone()
    iid = r["id"] if isinstance(r, dict) else r[0]
    for x in stornare:
        cur.execute("INSERT INTO %sinregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s,%%s,%%s,%%s)" % s,
                    (iid, x["debit"], x["credit"], x["suma"]))
    cur.execute("UPDATE %snir SET factura_id = %%s, factura_ref = COALESCE(NULLIF(factura_ref, ''), %%s), inregistrari_ids = %%s "
                "WHERE id = %%s" % s, (f["id"], fact, json.dumps(note + [iid]), n["id"]))
    return iid
