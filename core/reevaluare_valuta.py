# -*- coding: utf-8 -*-
"""core/reevaluare_valuta.py — reevaluarea lunară a elementelor monetare în valută, PROPUSĂ de aplicație (lotul 10, deficiența 429).

Comanda Costin 20.10.2026 (10.1 pct.8, verbatim în DECIZII „Comanda 10.1”): „Deficiența 429 — reevaluarea lunară a soldurilor în
valută cere de mână soldul, moneda și cursul pe fiecare cont. La închiderea lunii, aplicația propune singură creanțele și datoriile în
valută neîncasate (pe factură), disponibilitățile în valută, cursul din evidență, cursul BNR din ultima zi bancară și diferența pe
665/765; contabilul verifică și generează nota. Reevaluarea apare în „Ce oprește închiderea” când există solduri în valută.”

TEMEI — OMFP 1802/2014 pct.325 (`anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`), verbatim:
  alin.(1) „La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat
  de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate
  la venituri sau cheltuieli din diferențe de curs valutar, după caz.”
  alin.(2) lit.b „cursul de schimb al pieței valutare comunicat de Banca Națională a României, din ultima zi bancară a lunii în cauză,
  pentru evaluarea creanțelor și datoriilor în valută, a disponibilităților în valută și a altor valori de trezorerie, cum sunt
  titlurile de stat în valută, acreditivele și depozitele în valută, existente în sold la sfârșitul lunii.”
  Deci reevaluarea e OBLIGATORIE LUNAR (nu numai la închiderea exercițiului, pct.94 lit.a) — de-aici blocajul din „Ce oprește
  închiderea” (`uc_comun.controale_inchidere`, cod REEVALUARE_VALUTA).
  OMFP 1802/2014 pct.316 alin.(2): avansurile (4091–4094, 409, 419) „nu mai fac obiectul evaluării în funcție de cursul valutar, la
  finele lunii” — de-aceea elementele sunt facturile (4111 / 401 / 404) și disponibilitățile (5124, 5314, 5414), nu avansurile.
  Conturile 665 / 765 — planul de conturi din același ordin: 665 „diferențele nefavorabile de curs valutar rezultate în urma evaluării
  creanțelor în valută, la finele lunii [...] (267, 411, ...)”, „[...] din evaluarea datoriilor în valută, la finele lunii [...] (401,
  404, ...)”, „[...] din evaluarea la finele lunii [...] a disponibilităților bancare în valută, a disponibilităților în valută
  existente în casierie”; 765 simetric. Regula de semn: `diferente_curs._cont_si_sens` (sursa unică).

CE PROPUNE (fiecare element cu ce se știe din date; ce nu se știe se CERE pe ecran, nu se inventează):
  · creanțele / datoriile: facturile în valută (`facturi.moneda <> 'RON'`, nu proforme, nu stornări), cu nota de contare VALIDATĂ
    până la sfârșitul lunii, cu sold în valută rămas la sfârșitul lunii. Contul = contul de terț din nota de contare (4111… / 401… /
    404…). Soldul în valută = totalul (+ stornările lui, în valută) − plățile; o plată e în lei (notele legate de factură care ating
    contul de terț, chitanțele nelegate de notă), deci în valută = lei / cursul din evidență la data plății — INTERPRETARE CU TEMEI
    (o plată stinge creanța la valoarea ei din evidență: pct.322 alin.(1)), de aceea soldul unei facturi cu plăți e ESTIMAT și
    se poate corecta pe ecran. `platita_la` până la sfârșitul lunii = încasată integral.
    Cursul din evidență = `curs_nou` al ultimei reevaluări a facturii (tabela `reevaluari_valuta`), altfel cursul facturii.
    Valoarea în lei din evidență = `total_lei` (+ stornări) urmărit prin reevaluări (fiecare aduce soldul la `sold_valuta x curs_nou`)
    și plăți (minus leii plătiți) — exact soldul facturii pe contul de terț.
  · disponibilitățile: fiecare cont 5124 / 5314 / 5414 (cu analiticele lui) cu sold debitor în lei la sfârșitul lunii
    (`bilant_api.sold_la`, notele validate). Soldul în VALUTĂ nu e în evidență (extrasul MT940 nu-și păstrează soldul, iar o linie de
    extras ține numai `valuta` ca bifă) -> se CERE pe ecran; moneda se propune din simbolul / denumirea contului dacă ele conțin
    exact o monedă cotată de BNR, altfel din reevaluarea anterioară a contului, altfel se cere. Cursul din evidență = lei / valută.
  · cursul BNR: `curs_bnr.curs_pentru(…, ultima zi a lunii)` = ultimul curs publicat cu data <= ultima zi a lunii, adică cel din
    ultima zi bancară a lunii; data lui se arată.

A DOUA GENERARE înlocuiește ciorna nevalidată a lunii (DECIZII „R36 … a doua generare înlocuiește ciorna nevalidată (T1)”); o notă
validată nu se atinge: elementele ei au deja cursul lunii, deci diferența 0, iar ce a apărut după ea intră într-o notă nouă.

Stratul: REPOSITORY (SQL pe schema firmei, primește `cur`, fără conexiuni și fără commit); calculul diferenței e în motorul pur
`core/diferente_curs.py`.
"""
from decimal import Decimal, ROUND_HALF_UP

from core import curs_bnr as _cb
from core import diferente_curs as _dc

#: disponibilitățile în valută (OMFP 1802/2014 pct.325 alin.(2) lit.b: bănci, casă, acreditive)
CONTURI_DISPONIBIL = ("5124", "5314", "5414")
B = Decimal("0.01")
_TOL = Decimal("0.005")
TEMEI = "OMFP 1802/2014 pct.325"


def _q(schema):
    return '"%s".' % str(schema).strip('"') if schema else ""


def _v(r, k, i):
    return r[k] if isinstance(r, dict) else r[i]


def _dec(x):
    return Decimal(str(x if x is not None else 0))


def _lei(x):
    return _dec(x).quantize(B, rounding=ROUND_HALF_UP)


# ── citiri ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def reevaluari(cur, schema, pana_la):
    """Reevaluările consemnate până la `pana_la` (inclusiv), cu starea notei lor: [{id, data, nota_id, status, factura_id, cont,
    moneda, sold_valuta, curs_vechi, curs_nou, diferenta}], în ordinea datei."""
    s = _q(schema)
    cur.execute("SELECT r.id, r.data, r.inregistrare_id, i.status, r.factura_id, r.cont, r.moneda, r.sold_valuta, r.curs_vechi, "
                "r.curs_nou, r.diferenta, r.sursa FROM %sreevaluari_valuta r JOIN %sinregistrari i ON i.id = r.inregistrare_id "
                "WHERE r.data <= %%s ORDER BY r.data, r.id" % (s, s), (pana_la,))
    chei = ("id", "data", "nota_id", "status", "factura_id", "cont", "moneda", "sold_valuta", "curs_vechi", "curs_nou", "diferenta",
            "sursa")
    return [dict(zip(chei, list(r.values()) if isinstance(r, dict) else r)) for r in cur.fetchall()]


def facturi_in_valuta(cur, schema, sfarsit):
    """Facturile în valută emise până la `sfarsit`, nestornări, nu proforme / avize: [{id, directie, tip, serie, numar, data_emitere,
    moneda, total, total_lei, curs_bnr, tert_nume, platita_la, storno_valuta, storno_lei}]."""
    s = _q(schema)
    cur.execute("SELECT f.id, f.directie, f.tip, f.serie, f.numar, f.data_emitere, upper(f.moneda) AS moneda, f.total, f.total_lei, f.curs_bnr, "
                "f.tert_nume, f.platita_la, "
                "(SELECT COALESCE(SUM(st.total), 0) FROM %sfacturi st WHERE st.storno_din_id = f.id AND st.data_emitere <= %%s) AS storno_valuta, "
                "(SELECT COALESCE(SUM(COALESCE(st.total_lei, st.total * st.curs_bnr)), 0) FROM %sfacturi st "
                " WHERE st.storno_din_id = f.id AND st.data_emitere <= %%s) AS storno_lei "
                "FROM %sfacturi f WHERE upper(COALESCE(f.moneda, 'RON')) <> 'RON' AND COALESCE(f.tip, 'factura') = 'factura' "
                "AND f.storno_din_id IS NULL AND f.data_emitere <= %%s ORDER BY f.data_emitere, f.id" % (s, s, s),
                (sfarsit, sfarsit, sfarsit))
    chei = ("id", "directie", "tip", "serie", "numar", "data_emitere", "moneda", "total", "total_lei", "curs_bnr", "tert_nume",
            "platita_la", "storno_valuta", "storno_lei")
    return [dict(zip(chei, list(r.values()) if isinstance(r, dict) else r)) for r in cur.fetchall()]


def chitante_nelegate(cur, schema, factura_ids, sfarsit):
    """{factura_id: [(data, suma lei)]} — chitanțele nenulate a căror notă NU e legată de factură (cea legată se numără din note,
    ca în `facturi_api._cu_stare_incasare`: altfel aceeași încasare ar intra de două ori)."""
    if not factura_ids:
        return {}
    s = _q(schema)
    cur.execute("SELECT c.factura_id, c.data, c.suma FROM %schitante c WHERE c.factura_id = ANY(%%s) AND NOT c.anulata AND c.data <= %%s "
                "AND NOT EXISTS (SELECT 1 FROM %sinregistrari i WHERE i.id = c.inregistrare_id AND i.factura_id = c.factura_id)"
                % (s, s), (list(factura_ids), sfarsit))
    out = {}
    for r in cur.fetchall():
        out.setdefault(_v(r, "factura_id", 0), []).append((_v(r, "data", 1), _dec(_v(r, "suma", 2))))
    return out


def monede_cotate(cur):
    """Monedele pe care BNR le-a cotat (cache-ul local) — ca să se recunoască o monedă în simbolul / denumirea contului."""
    return _cb._monede_din_cache(cur.connection)


def denumiri_conturi(cur, schema, simboluri):
    if not simboluri:
        return {}
    cur.execute("SELECT simbol, denumire FROM %splan_conturi WHERE simbol = ANY(%%s)" % _q(schema), (list(simboluri),))
    return {_v(r, "simbol", 0): _v(r, "denumire", 1) for r in cur.fetchall()}


def solduri_disponibil(cur, schema, sfarsit):
    """{cont: sold debitor net în lei} la `sfarsit` pe conturile de disponibilități în valută, din notele validate
    (`bilant_api.sold_la`, aceeași sursă ca balanța). None dacă ziua e înaintea soldurilor de preluare."""
    from psycopg2.extras import RealDictCursor
    from core import bilant_api as _ba
    with cur.connection.cursor(cursor_factory=RealDictCursor) as c2:
        sl = _ba.sold_la(c2, schema, sfarsit)
    if sl is None:
        return None
    return {k: d - c for k, (d, c) in sl.items() if any(k == p or k.startswith(p) for p in CONTURI_DISPONIBIL) and d - c != 0}


# ── propunerea ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _cont_tert(note, directie):
    """Contul de terț din nota de CONTARE validată (debit 411… la emisă, credit 401… / 404… la primită)."""
    for n in note:
        if not n["e_contare"] or n["status"] != "validata":
            continue
        for cd, cc, _s in n["linii"]:
            if directie == "emisa" and str(cd).startswith("411"):
                return cd, n["data"]
            if directie != "emisa" and (str(cc).startswith("401") or str(cc).startswith("404")):
                return cc, n["data"]
    return None, None


def _plati_din_note(note, cont, directie, sfarsit):
    """[(data, lei)] — notele legate de factură care NU sunt contarea ei și ating contul de terț pe partea care stinge (credit la creanță,
    debit la datorie), până la sfârșitul lunii."""
    out = []
    for n in note:
        if n["e_contare"] or n["data"] > sfarsit:
            continue
        lei = sum((s for cd, cc, s in n["linii"] if (cc if directie == "emisa" else cd) == cont), Decimal("0"))
        if lei:
            out.append((n["data"], lei))
    return out


def _curs_fn(cur, sfarsit):
    """Cursul BNR al lunii, pe monedă (memorat): (curs, data_curs) sau excepția `curs_bnr` (necotată / indisponibil / prea vechi)."""
    memo = {}

    def f(moneda):
        if moneda not in memo:
            try:
                c, dc, _s = _cb.curs_pentru(cur.connection, moneda, sfarsit)
                memo[moneda] = (c, dc, None)
            except (_cb.CursIndisponibil, _cb.CursPreaVechi) as e:
                memo[moneda] = (None, None, str(e))
        return memo[moneda]
    return f


def _cu_curs(el, curs_fn, tip):
    """Completează elementul cu cursul BNR și diferența (motorul pur), dacă se știu soldul și moneda."""
    if not el.get("moneda"):
        return el
    c, dc, motiv = curs_fn(el["moneda"])
    el["curs_bnr"], el["data_curs"] = (str(c) if c is not None else None), (str(dc) if dc else None)
    if c is None:
        el["motiv_curs"] = motiv
        return el
    if el.get("sold_valuta") is None or el.get("lei_evidenta") is None:
        return el
    r = _dc.reevaluare_element(el["sold_valuta"], el["lei_evidenta"], c, tip, el["cont"])
    el["lei_bnr"], el["diferenta"] = str(r["lei_nou"]), str(r["diferenta"])
    el["cont_diferenta"], el["sens"], el["linie"] = r["cont"], r["sens"], r["linie"]
    return el


def propunere(cur, schema, an, luna, completari=None, cu_ciorna_lunii=False, curs_fn=None):
    """Propunerea reevaluării lunii (an, luna). `completari` = {cheie: {sold_valuta?, moneda?}} — ce a scris contabilul pe ecran,
    numai pe câmpurile `editabile` ale elementului (altfel `ValueError`). `cu_ciorna_lunii`: reevaluările lunii aflate în ciornă
    contează ca făcute (controalele închiderii; CIORNE o spune separat) — altfel se ignoră, fiindcă generarea le înlocuiește.
    -> {an, luna, data, elemente: [...], totaluri, ciorna_lunii: [nota_id], temei}."""
    import calendar as _cal
    from datetime import date as _date
    from core import contare_facturi as _cf
    from core import eticheta_nota as _et
    completari = dict(completari or {})
    inceput = _date(int(an), int(luna), 1)
    sfarsit = _date(int(an), int(luna), _cal.monthrange(int(an), int(luna))[1])
    curs_fn = curs_fn or _curs_fn(cur, sfarsit)
    toate = reevaluari(cur, schema, sfarsit)
    # [lotul 10] numai ciornele PROPUNERII se înlocuiesc la generare (și se ignoră aici); reevaluarea din formularul manual rămâne a
    # omului și contează ca făcută — altfel diferența ei s-ar înregistra a doua oară
    _a_propunerii = lambda r: r["data"] >= inceput and r["status"] == "ciorna" and r["sursa"] == "propunere"
    ciorna_lunii = sorted({r["nota_id"] for r in toate if _a_propunerii(r)})
    rev = [r for r in toate if cu_ciorna_lunii or not _a_propunerii(r)]
    elemente = []

    # creanțele și datoriile, pe factură
    fact = facturi_in_valuta(cur, schema, sfarsit)
    note = _cf.note_pe_facturi(cur, schema, [f["id"] for f in fact])
    chit = chitante_nelegate(cur, schema, [f["id"] for f in fact], sfarsit)
    for f in fact:
        nf = note.get(f["id"], [])
        cont, data_contare = _cont_tert(nf, f["directie"])
        if not cont or data_contare > sfarsit or f["curs_bnr"] is None:
            continue   # nu e (încă) în evidență: nota de contare nevalidată — CIORNE / FACTURI_NEINCHEIATE o spun
        if f["platita_la"] is not None and f["platita_la"].date() <= sfarsit:
            continue
        tip = "creanta" if f["directie"] == "emisa" else "datorie"
        ev = sorted([(r["data"], 0, r) for r in rev if r["factura_id"] == f["id"]]
                    + [(d, 1, lei) for d, lei in _plati_din_note(nf, cont, f["directie"], sfarsit) + chit.get(f["id"], [])],
                    key=lambda x: (x[0], x[1]))
        valuta = _dec(f["total"]) + _dec(f["storno_valuta"])
        lei = _lei(_dec(f["total_lei"] if f["total_lei"] is not None else _dec(f["total"]) * _dec(f["curs_bnr"])) + _dec(f["storno_lei"]))
        curs_ev, sursa_ev, cu_plati = _dec(f["curs_bnr"]), "factura", False
        for d, fel, x in ev:
            if fel == 0:     # reevaluarea aduce soldul la `sold_valuta x curs_nou`
                valuta, curs_ev, sursa_ev = _dec(x["sold_valuta"]), _dec(x["curs_nou"]), str(d)
                lei = _lei(valuta * curs_ev)
            else:            # plata stinge creanța / datoria la cursul din evidență (pct.322 alin.(1))
                valuta -= (x / curs_ev)
                lei -= x
                cu_plati = True
        valuta = valuta.quantize(B, rounding=ROUND_HALF_UP)
        if valuta <= _TOL:
            continue
        cheie = "f%d" % f["id"]
        el = {"cheie": cheie, "fel": tip, "factura_id": f["id"], "document": _et.factura_din_rand(f), "partener": f["tert_nume"],
              "cont": cont, "moneda": f["moneda"], "sold_valuta": str(valuta), "estimat": cu_plati,
              "curs_evidenta": str(curs_ev), "curs_evidenta_din": sursa_ev, "lei_evidenta": str(lei),
              "editabile": ["sold_valuta"] if cu_plati else [], "de_completat": []}
        _aplica(el, completari.pop(cheie, None))
        elemente.append(_cu_curs(el, curs_fn, tip))

    # disponibilitățile
    solduri = solduri_disponibil(cur, schema, sfarsit) or {}
    den = denumiri_conturi(cur, schema, list(solduri))
    cotate = monede_cotate(cur) if solduri else set()
    for cont in sorted(solduri):
        L = _lei(solduri[cont])
        if L <= 0:
            continue
        ale_contului = [r for r in rev if r["factura_id"] is None and r["cont"] == cont]
        a_lunii = [r for r in ale_contului if r["data"] >= inceput]
        moneda = _moneda_din_cont(cont, den.get(cont), cotate) or (ale_contului[-1]["moneda"] if ale_contului else None)
        cheie = "c" + cont
        el = {"cheie": cheie, "fel": "disponibil", "factura_id": None, "document": None, "partener": den.get(cont), "cont": cont,
              "moneda": moneda, "sold_valuta": None, "estimat": False, "curs_evidenta": None, "curs_evidenta_din": None,
              "lei_evidenta": str(L), "editabile": ["sold_valuta", "moneda"], "de_completat": []}
        if a_lunii:           # deja reevaluat în lună: soldul în valută e cel consemnat, iar ciorna lunii își adaugă diferența
            r = a_lunii[-1]
            el.update(moneda=r["moneda"], sold_valuta=str(_dec(r["sold_valuta"])), curs_evidenta=str(_dec(r["curs_nou"])),
                      curs_evidenta_din=str(r["data"]), editabile=[],
                      lei_evidenta=str(L + (sum((_dec(x["diferenta"]) for x in a_lunii if x["status"] == "ciorna"), Decimal("0")))))
        _aplica(el, completari.pop(cheie, None))
        if el["sold_valuta"] is not None and el["curs_evidenta"] is None:
            el["curs_evidenta"] = str((L / _dec(el["sold_valuta"])).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
            el["curs_evidenta_din"] = "sold"
        elemente.append(_cu_curs(el, curs_fn, "disponibil"))
    if completari:
        raise ValueError("Elementele %s nu mai sunt în propunerea lunii — reîncarcă propunerea." % ", ".join(sorted(completari)))   # FORMĂ
    for el in elemente:
        el["de_completat"] = [c for c in ("moneda", "sold_valuta") if el.get(c) in (None, "")]
    return {"an": int(an), "luna": int(luna), "data": str(sfarsit), "elemente": elemente, "totaluri": totaluri(elemente),
            "ciorna_lunii": ciorna_lunii, "temei": TEMEI}


def _moneda_din_cont(cont, denumire, cotate):
    """Moneda din simbolul sau denumirea contului, dacă ele conțin EXACT o monedă cotată de BNR („5124.EUR”, „BT cont EUR”)."""
    import re
    gasite = {t for t in re.findall(r"[A-Za-z]{3}", "%s %s" % (cont, denumire or "")) if t.upper() == t and t in cotate}
    return gasite.pop() if len(gasite) == 1 else None


def _aplica(el, c):
    """Completarea contabilului, numai pe câmpurile editabile ale elementului."""
    if not c:
        return
    for k, v in c.items():
        if v in (None, ""):
            continue
        if k not in el["editabile"]:   # FORMĂ: câmp needitabil pe element
            raise ValueError("%s: câmpul „%s” nu se completează pe acest element." % (el.get("document") or "Contul %s" % el["cont"],
                                                                                    {"sold_valuta": "sold în valută"}.get(k, k)))
        if k == "sold_valuta":
            try:
                v = _dec(str(v).replace(" ", "").replace(",", "."))
            except Exception:   # noqa: BLE001 — orice text nenumeric e același refuz
                raise ValueError("Soldul în valută pentru contul %s nu e un număr." % el["cont"])   # FORMĂ
            if v <= 0:
                raise ValueError("Soldul în valută pentru contul %s trebuie să fie pozitiv." % el["cont"])   # FORMĂ
            el["sold_valuta"], el["estimat"] = str(v.quantize(B, rounding=ROUND_HALF_UP)), False
        elif k == "moneda":
            el["moneda"] = str(v).strip().upper()


def totaluri(elemente):
    t765 = sum((_dec(e["linie"][2]) for e in elemente if e.get("linie") and e["sens"] == "favorabila"), Decimal("0"))
    t665 = sum((_dec(e["linie"][2]) for e in elemente if e.get("linie") and e["sens"] == "nefavorabila"), Decimal("0"))
    return {"venit": str(_lei(t765)), "cheltuiala": str(_lei(t665)), "net": str(_lei(t765 - t665)),
            "de_completat": sum(1 for e in elemente if e["de_completat"] or (e.get("moneda") and e.get("curs_bnr") is None))}


def de_reevaluat(prop):
    """Elementele care opresc închiderea: cu diferență nenulă neînregistrată, sau fără ce trebuie ca să se calculeze (soldul în
    valută, moneda, cursul BNR)."""
    return [e for e in prop["elemente"]
            if e["de_completat"] or e.get("curs_bnr") is None or (e.get("diferenta") and _dec(e["diferenta"]) != 0)]


# ── scrieri ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def conturi_pe_facturi(cur, schema, sfarsit):
    """[lotul 10, 429 — riscul de dublare] Conturile de terți (411… / 401… / 404…) ale facturilor în valută aflate în evidență la
    `sfarsit` (nota de contare validată): pe ele reevaluarea o face propunerea, factură cu factură. Formularul manual le refuză —
    o reevaluare pe sold agregat al aceluiași cont ar înregistra diferența a doua oară. Aceeași regulă ca `propunere`."""
    from core import contare_facturi as _cf
    fact = [f for f in facturi_in_valuta(cur, schema, sfarsit) if f["curs_bnr"] is not None]
    note = _cf.note_pe_facturi(cur, schema, [f["id"] for f in fact])
    out = set()
    for f in fact:
        cont, data_contare = _cont_tert(note.get(f["id"], []), f["directie"])
        if cont and data_contare <= sfarsit:
            out.add(str(cont))
    return out


def consemneaza(cur, schema, nota_id, data, elemente, sursa="propunere"):
    """Un rând în `reevaluari_valuta` pe element reevaluat, legat de notă (ștergerea notei îl șterge: ON DELETE CASCADE). `diferenta`
    e semnată: cu cât a crescut soldul în lei al elementului. Cursul nou devine cursul din evidență al lunii următoare."""
    for e in elemente:
        cur.execute("INSERT INTO %sreevaluari_valuta (data, inregistrare_id, factura_id, cont, moneda, sold_valuta, curs_vechi, "
                    "curs_nou, diferenta, sursa) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)" % _q(schema),
                    (data, nota_id, e["factura_id"], e["cont"], e["moneda"], e["sold_valuta"], e["curs_evidenta"], e["curs_bnr"],
                     e["diferenta"], sursa))
