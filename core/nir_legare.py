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

[08.10.2026, deciziile Costin §6 pct.1–3, verbatim în DECIZII] FORMA NOUĂ a NIR-ului fără factură: 371 = 408 (costul) și TVA pe 4428
(analiticul de achiziție `CONT_TVA_NIR`) = 408 (`stocuri_api.adauga_nir`). La contarea facturii legate NU se mai stornează nimic: notele
facturii devin 408 = 401 (costul + TVA din NIR) și 4426 = 4428 (TVA-ul trece în deductibil odată cu factura — CF art.299 alin.(1)
lit.a), plus diferența de preț, în perioada facturii (`note_factura_legata`). Pe ambele metode (global-valoric și cantitativ-valoric),
fără a doua intrare în stoc, fără refuz; între exerciții, cât timp 408 e deschis — exercițiul închis nu se modifică (OMFP 1802/2014
pct.68 alin.(1): „Corectarea erorilor aferente exercițiilor financiare precedente nu determină modificarea situațiilor financiare ale
acelor exerciții.”). NIR-urile în FORMA VECHE (371 = 401, scrise înainte de 08.10) se leagă tot prin stornarea în roșu de mai jos, acum
și la cantitativ-valoric, numai în exercițiul curent (pct.69).

LIMITE, declarate (FORMA VECHE): (1) numai NIR-uri din ACELAȘI exercițiu cu nota facturii — pct.69 vorbește despre „exercițiul financiar
curent”; un NIR din exercițiul trecut nu se stornează de aici. (2) Costul NIR-ului (fără transport și taxe) trebuie să fie netul
facturii în lei, la ban — altfel nu e aceeași livrare (ca la ordinea directă, `COST_DIFERIT_DE_FACTURA`).
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
#: [08.10, §6 pct.1] datoria NIR-ului fără factură — „Furnizori - facturi nesosite” (OMFP 1802/2014, funcțiunea contului 408)
CONT_NESOSITE = "408"
#: [08.10, §6 pct.3] TVA-ul NIR-ului fără factură, neexigibil până la factură — analiticul de ACHIZIȚIE al lui 4428, ca să nu se
#: amestece cu TVA-ul din prețul de raft (pe 4428 sintetic, citit de K-ul global-valoric pe cont exact)
CONT_TVA_NIR = "4428.01"
#: metodele pe care se leagă (decizia §6 pct.1: „aceeași alegere ca la celelalte metode”)
METODE = (_ms.GV, _ms.CV)
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
    """Factura primită care încarcă 371 la o firmă cu metoda de stoc declarată (global- sau cantitativ-valoric)?"""
    if (f.get("directie") or "") != "primita":
        return False
    if not any(str(n.get("debit")) == CONT_MARFA for n in note):
        return False
    return _ms.citeste(cur, schema) in METODE


def forma_noua(cur, schema, nir):
    """True dacă NIR-ul e în forma nouă (datoria pe 408), False dacă e în forma veche (371 = 401)."""
    from core import stocuri_api as _sa
    note = _sa.note_nir(nir)
    if not note:
        return False
    cur.execute("SELECT 1 FROM %sinregistrari_linii WHERE inregistrare_id = ANY(%%s) AND cont_credit = %%s LIMIT 1" % _p(schema),
                (note, CONT_NESOSITE))
    return cur.fetchone() is not None


def sume_nir(cur, schema, nir):
    """(costul pe 408, TVA-ul pe 4428.01) ale unui NIR în forma nouă."""
    from core import stocuri_api as _sa
    cur.execute("SELECT COALESCE(SUM(CASE WHEN cont_debit <> %%s THEN suma ELSE 0 END), 0) AS cost, "
                "COALESCE(SUM(CASE WHEN cont_debit = %%s THEN suma ELSE 0 END), 0) AS tva FROM %sinregistrari_linii "
                "WHERE inregistrare_id = ANY(%%s) AND cont_credit = %%s" % _p(schema),
                (CONT_TVA_NIR, CONT_TVA_NIR, _sa.note_nir(nir), CONT_NESOSITE))
    r = cur.fetchone()
    v = list(r.values()) if isinstance(r, dict) else list(r)
    return _q2(v[0]), _q2(v[1])


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
                "WHERE factura_id IS NULL AND metoda_stoc = ANY(%%s) AND data <= %%s "
                "AND NOT EXISTS (SELECT 1 FROM %snir r WHERE r.refacut_din_id = %snir.id) ORDER BY data, id" % (s, s, s),
                (list(METODE), str(data_nota)[:10]))
    nirs = []
    for r in cur.fetchall():
        n = dict(r)
        if _cui(n["cui"]) != cui:
            continue
        n["forma_noua"] = forma_noua(cur, schema, n)
        # §6 pct.2: forma nouă se leagă și între exerciții, cât timp 408 e deschis (factura_id NULL); forma veche se stornează, deci
        # numai în exercițiul curent (OMFP 1802/2014 pct.69)
        if n["forma_noua"] or int(str(n["data"])[:4]) == an:
            nirs.append(n)
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
                    "acelasi_cost": cost == net, "forma_noua": n["forma_noua"],
                    "eticheta": "NIR nr %s din %s · cost %s lei" % (n["numar"], _pu.data_ro(n["data"]), cost)})
    return out


def legat_de_factura(cur, schema, factura_id):
    """NIR-ul în forma nouă deja legat de factura asta — re-contarea după o notă RESPINSĂ (`note_derivate.sterge_respinsa`). Alegerea
    omului s-a făcut la prima contare și rămâne: nota nouă închide același 408, altfel factura ar încărca 371 a doua oară (marfa a intrat
    prin NIR, iar NIR-ul legat nu mai e candidat). Forma veche nu intră aici: stornarea ei a rămas, deci factura se contează întreagă."""
    cur.execute("SELECT id, numar, data, inregistrari_ids FROM %snir WHERE factura_id = %%s ORDER BY id" % _p(schema), (int(factura_id),))
    for r in cur.fetchall():
        n = dict(r)
        if forma_noua(cur, schema, n):
            return {"id": n["id"], "numar": n["numar"], "data": str(n["data"])[:10], "forma_noua": True}
    return None


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
                                     "același furnizor (unul în forma veche, pe 401, numai din același exercițiu).")
    if not c["acelasi_cost"] and not c["forma_noua"]:   # forma nouă: diferența de preț intră în perioada facturii (§6 pct.2)
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


def note_factura_legata(note, cost_nir, tva_nir, metoda, d_607=0):
    """[08.10.2026, deciziile Costin §6 pct.1–3] Notele facturii legate de un NIR în FORMA NOUĂ — PURĂ.

    `note` = notele facturii (`contare_facturi.genereaza_note`): marfa 371 = 401 (netul N) și TVA-ul X = 401 (T; X = 4426 la regimul
    normal, 4428 la TVA la încasare), sau 4426 = 4427 la taxarea inversă. Se înlocuiește încărcarea 371 = 401, fiindcă marfa a intrat
    deja prin NIR:
      408 = 401   costul din NIR (+ TVA-ul din NIR, când factura are TVA pe 4426 = 401)       — se închide „factura nesosită”
      4426 = 4428.01  TVA-ul din NIR                                                         — CF art.299 alin.(1) lit.a: deducerea
                                                                                               cere factura
      diferența de cost  (N − costul NIR), în perioada facturii: global-valoric 378 = 401 (adaosul); cantitativ-valoric 371 = 401, iar
                         partea articolelor care nu mai sunt în stoc (`d_607`, din `plan_ajustare_cv`) 607 = 401
      diferența de TVA   4426 = 401 (T − TVA-ul din NIR)
    Altfel (TVA la încasare, taxare inversă): 408 = 401 (costul), 408 = 4428.01 (TVA-ul din NIR se anulează) și TVA-ul facturii rămâne
    cum îl scrie factura. O diferență negativă se scrie cu minus (stornare în roșu, OMFP 1802/2014 pct.69)."""
    cost_nir, tva_nir = _q2(cost_nir), _q2(tva_nir)
    net = _q2(sum(Decimal(str(n["suma"])) for n in note if n["debit"] == CONT_MARFA and n["credit"] == "401"))
    tva_4426 = _q2(sum(Decimal(str(n["suma"])) for n in note if n["debit"] == "4426" and n["credit"] == "401"))
    rest = [n for n in note if not (n["debit"] == CONT_MARFA and n["credit"] == "401")]
    out = []
    d_cost = net - cost_nir
    if tva_4426:   # regimul normal: TVA-ul trece 4428 -> 4426
        rest = [n for n in rest if not (n["debit"] == "4426" and n["credit"] == "401")]
        out.append({"debit": CONT_NESOSITE, "credit": "401", "suma": cost_nir + tva_nir})
        if tva_nir:
            out.append({"debit": "4426", "credit": CONT_TVA_NIR, "suma": tva_nir})
        if tva_4426 - tva_nir:
            out.append({"debit": "4426", "credit": "401", "suma": tva_4426 - tva_nir})
    else:
        out.append({"debit": CONT_NESOSITE, "credit": "401", "suma": cost_nir})
        if tva_nir:
            out.append({"debit": CONT_NESOSITE, "credit": CONT_TVA_NIR, "suma": tva_nir})
    d_607 = _q2(d_607)
    if d_cost - d_607:
        out.append({"debit": "378" if metoda == _ms.GV else CONT_MARFA, "credit": "401", "suma": d_cost - d_607})
    if d_607:
        out.append({"debit": "607", "credit": "401", "suma": d_607})
    return out + rest


def plan_ajustare_cv(cur, schema, nir_id, d_cost, data):
    """[§6 pct.2, cantitativ-valoric] Diferența de cost împărțită pe articolele NIR-ului, proporțional cu costul liniei (restul de
    rotunjire pe ultima): [(articol_id, suma, e_in_stoc)]. Pe articolul încă în stoc, diferența intră în fișă (ajustare de valoare,
    CMP recalculat); pe cel vândut, pe 607 — nu mai are pe ce sta în stoc."""
    from core import repo_stocuri
    from core import stocuri_cv as _cv
    d_cost = _q2(d_cost)
    if not d_cost:
        return []
    s = _p(schema)
    cur.execute("SELECT articol_id, cantitate * pret_achizitie AS cost FROM %snir_linii WHERE nir_id = %%s ORDER BY id" % s, (int(nir_id),))
    linii = [(r["articol_id"], Decimal(str(r["cost"]))) if isinstance(r, dict) else (r[0], Decimal(str(r[1])))
             for r in cur.fetchall()]
    total = sum((x[1] for x in linii), Decimal(0))
    out, ramas = [], d_cost
    for k, (aid, cost) in enumerate(linii):
        parte = ramas if k == len(linii) - 1 else _q2(d_cost * cost / total) if total else Decimal(0)
        ramas -= parte if k < len(linii) - 1 else Decimal(0)
        fisa = _cv.fisa_magazie([m for m in repo_stocuri.miscari_ale_articolului(cur, schema, aid)
                                 if str(m["data"]) <= str(data)[:10]]) if aid else []
        in_stoc = bool(fisa) and Decimal(str(fisa[-1]["sold_cantitate"])) > 0
        out.append((aid, parte, in_stoc))
    return out


def scrie_ajustari_cv(cur, schema, plan, data, inregistrare_id, nir_id, factura_id, document):
    """Ajustările de valoare din fișă (tip `ajustare`, cantitate 0), legate de nota facturii și de NIR. La re-contare (nota de dinainte
    respinsă) ajustarea veche a fost stornată în roșu la respingere (`stocuri_anulare.storneaza`) și rămâne în fișă ca istoric; cea
    rămasă VIE fără nota ei (ștearsă de `note_derivate.sterge_respinsa`, fără stornare) se scoate — o diferență de preț intră o dată."""
    s = _p(schema)
    cur.execute("DELETE FROM %smiscari_stoc m WHERE m.tip = 'ajustare' AND m.nir_id = %%s AND m.factura_id = %%s AND m.anuleaza_id IS NULL "
                "AND NOT EXISTS (SELECT 1 FROM %smiscari_stoc r WHERE r.anuleaza_id = m.id) "
                "AND NOT EXISTS (SELECT 1 FROM %sinregistrari i WHERE i.id = m.inregistrare_id)" % (s, s, s), (int(nir_id), factura_id))
    for aid, suma, in_stoc in plan:
        if in_stoc and suma:
            cur.execute("INSERT INTO %smiscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, inregistrare_id, "
                        "nir_id, factura_id) VALUES (%%s, %%s, 'ajustare', 0, NULL, %%s, %%s, %%s, %%s, %%s)" % s,
                        (aid, str(data)[:10], suma, document[:100], inregistrare_id, int(nir_id), factura_id))


def leaga_forma_noua(cur, schema, nir_id, f):
    """Leagă un NIR în forma nouă: `nir.factura_id` (408 se închide prin notele facturii). Nicio notă de stornare."""
    s = _p(schema)
    fact = ("%s %s" % (f.get("serie") or "", f.get("numar") or "")).strip()
    cur.execute("UPDATE %snir SET factura_id = %%s, factura_ref = COALESCE(NULLIF(factura_ref, ''), %%s) WHERE id = %%s AND factura_id IS NULL"
                % s, (f["id"], fact, int(nir_id)))
