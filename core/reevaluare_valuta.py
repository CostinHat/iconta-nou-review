# -*- coding: utf-8 -*-
"""core/reevaluare_valuta.py — reevaluarea lunară a elementelor monetare în valută, PROPUSĂ de aplicație (lotul 10, deficiența 429;
lotul 11: pe partener, un singur formular).

Comanda Costin 20.10.2026 (10.1 pct.8, verbatim în DECIZII „Comanda 10.1”): „Deficiența 429 — reevaluarea lunară a soldurilor în
valută cere de mână soldul, moneda și cursul pe fiecare cont. La închiderea lunii, aplicația propune singură creanțele și datoriile în
valută neîncasate (pe factură), disponibilitățile în valută, cursul din evidență, cursul BNR din ultima zi bancară și diferența pe
665/765; contabilul verifică și generează nota. Reevaluarea apare în „Ce oprește închiderea” când există solduri în valută.”
Comanda 11.1 pct.11 (21.10.2026): „429: reevaluarea în valută e neschimbată pe producție (formular manual, fără propunere, fără curs
BNR, nimic la închiderea lunii).” Decizia din 10.3 (verbatim în DECIZII „Comanda 10.3”): „Reevaluarea valutei se face pe soldul în
valută al partenerului, inclusiv plățile nelegate; avansurile intră doar dacă OMFP 1802 pct. 325 le cuprinde, verificat verbatim.”

TEMEI — OMFP 1802/2014 (`anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, forma consolidată 19.11.2025), verbatim:
  pct.325 alin.(1) „La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare,
  comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în
  contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz.”
  pct.325 alin.(2) lit.b „cursul de schimb al pieței valutare comunicat de Banca Națională a României, din ultima zi bancară a lunii în
  cauză, pentru evaluarea creanțelor și datoriilor în valută, a disponibilităților în valută și a altor valori de trezorerie, cum sunt
  titlurile de stat în valută, acreditivele și depozitele în valută, existente în sold la sfârșitul lunii.”
  pct.325 alin.(3) „Prevederile prezentului punct se aplică și creanțelor și datoriilor exprimate în lei, a căror decontare se face în
  funcție de cursul unei valute. În acest caz, diferențele înregistrate se recunosc în contabilitate la alte venituri financiare sau alte
  cheltuieli financiare, după caz.” (768 / 668 — ajustarea manuală „în lei cu clauză valutară”.)
  AVANSURILE NU INTRĂ — pct.325 vorbește de „creanțele și datoriile”, iar pct.316 alin.(2) le scoate explicit: „Începând cu data de 1
  ianuarie 2015, sumele înregistrate în conturile menționate la alin. (1) [4093, 4094], precum și cele reflectate în conturile 409
  "Furnizori - debitori" și 419 "Clienți - creditori", nu mai fac obiectul evaluării în funcție de cursul valutar, la finele lunii,
  respectiv la finele exercițiului financiar.”; pct.315 alin.(3): „Exemplele [de elemente nemonetare] includ: sumele plătite în avans
  pentru bunuri și servicii”. De aceea un cont de avansuri (409…, 419…) nu se primește nici la ajustarea manuală.
  Conturile 665 / 765 — planul de conturi din același ordin; regula de semn: `diferente_curs._cont_si_sens` (sursa unică).

CE PROPUNE (fiecare element cu ce se știe din date; ce nu se știe se CERE pe ecran, nu se inventează):
  · creanțele / datoriile, PE PARTENER (decizia 10.3): grupul (contul de terț, partenerul, moneda) — contul din nota de contare
    VALIDATĂ a facturii (4111… / 401… / 404…), partenerul după codul fiscal (`compensari_api.cui_partener`: fără RO și spații), altfel
    după nume. Soldul în valută al partenerului = facturile lui în valută (+ stornările) − plățile, legate de factură SAU NELEGATE (o
    linie validată pe contul de terț, cu partenerul pe linie, pe partea care stinge, a unei note fără factură — banca nealocată, o notă
    din Registrul jurnal), urmărit prin reevaluările anterioare. O plată e în lei, deci în valută = lei / cursul din evidență al
    partenerului la data plății — INTERPRETARE CU TEMEI (o plată stinge creanța la valoarea ei din evidență: pct.322 alin.(1)), de aceea
    soldul unui partener cu plăți e ESTIMAT și se poate corecta pe ecran. Valoarea în lei din evidență = exact soldul partenerului pe
    contul de terț (facturi − plăți + diferențele reevaluărilor). O plată nelegată a unui partener care are, pe aceeași parte, facturi
    în MAI MULTE monede nu se poate atribui unei monede: elementul o arată (`plati_de_legat`) și generarea se oprește până e legată de
    factura pe care o stinge — nu se ghicește moneda. Factura încasată integral (`platita_la`) iese cu plățile ei legate.
    Facturile în valută care NU intră (nota de contare în ciornă, fără curs) se spun pe ecran (`neincluse`), nu se sar tăcut —
    pe producție, F1 avea facturile EUR cu contarea în ciornă și ecranul nu spunea nimic (429, 21.10.2026).
  · disponibilitățile: fiecare cont 5124 / 5314 / 5414 (cu analiticele lui) cu sold debitor în lei la sfârșitul lunii
    (`bilant_api.sold_la`, notele validate). Soldul în VALUTĂ nu e în evidență (extrasul MT940 nu-și păstrează soldul, iar o linie de
    extras ține numai `valuta` ca bifă) -> se CERE pe ecran; moneda se propune din simbolul / denumirea contului dacă ele conțin
    exact o monedă cotată de BNR, altfel din reevaluarea anterioară a contului, altfel se cere. Cursul din evidență = lei / valută.
  · AJUSTAREA MANUALĂ, în același formular (fostul formular din Operațiuni a fost scos: un singur formular, lotul 11): un cont pe care
    aplicația nu-l propune (un împrumut în valută, un depozit — pct.326 lit.b —, o creanță în lei cu clauză valutară — pct.325 alin.(3))
    se adaugă pe ecran cu moneda și soldul în valută; soldul în lei vine din evidență (`sold_la`), nu se scrie. Elementul e marcat
    `manual`, iar luna următoare contul revine singur în propunere (moneda știută, soldul în valută cerut din nou). Un cont deja propus
    (partener, disponibilitate) sau un cont de avansuri se refuză lângă câmp.
  · cursul BNR: `curs_bnr.curs_sfarsit_luna(…, ultima zi a lunii)` = ultimul curs comunicat cu data <= ultima zi a lunii, adică cel
    din ultima zi bancară a lunii (pct.325 alin.(2) lit.b); data lui se arată.

TOATE REFUZURILE COMPLETĂRILOR DEODATĂ (deficiența 440, aceeași clasă): `RefuzReevaluare` poartă lista {camp, mesaj} — câmpul de pe
ecran (`rv-<câmp>-<cheie>`, `rv-m<i>-<câmp>`) —, ridicată o singură dată, după ce s-au citit toate.

A DOUA GENERARE înlocuiește ciorna nevalidată a lunii (DECIZII „R36 … a doua generare înlocuiește ciorna nevalidată (T1)”); o notă
validată nu se atinge: elementele ei au deja cursul lunii, deci diferența 0, iar ce a apărut după ea intră într-o notă nouă.

Stratul: REPOSITORY (SQL pe schema firmei, primește `cur`, fără conexiuni și fără commit); calculul diferenței e în motorul pur
`core/diferente_curs.py`.
"""
import re
from decimal import Decimal, ROUND_HALF_UP

from core import curs_bnr as _cb
from core import diferente_curs as _dc

#: disponibilitățile în valută (OMFP 1802/2014 pct.325 alin.(2) lit.b: bănci, casă, acreditive)
CONTURI_DISPONIBIL = ("5124", "5314", "5414")
#: avansurile — OMFP 1802/2014 pct.316 alin.(2): 4093, 4094, 409 „Furnizori - debitori”, 419 „Clienți - creditori” „nu mai fac obiectul
#: evaluării în funcție de cursul valutar, la finele lunii”
CONTURI_AVANS = ("409", "419")
B = Decimal("0.01")
_TOL = Decimal("0.005")
TEMEI = "OMFP 1802/2014 pct.325"
TEMEI_AVANSURI = "OMFP 1802/2014 pct.316 alin.(2)"


class RefuzReevaluare(ValueError):
    """Completările de pe ecran care nu se pot primi — TOATE deodată: `erori` = [{camp, mesaj}] (câmpul de pe ecran)."""

    def __init__(self, erori):
        self.erori = list(erori)
        super().__init__(" ".join(e["mesaj"] for e in self.erori))


def _q(schema):
    return '"%s".' % str(schema).strip('"') if schema else ""


def _v(r, k, i):
    return r[k] if isinstance(r, dict) else r[i]


def _dec(x):
    return Decimal(str(x if x is not None else 0))


def _lei(x):
    return _dec(x).quantize(B, rounding=ROUND_HALF_UP)


def _rand(r, chei):
    return dict(zip(chei, list(r.values()) if isinstance(r, dict) else r))


def cheie_partener(cui, nume):
    """Partenerul unei facturi / al unei linii de notă: codul fiscal fără RO și spații (`compensari_api.cui_partener`, același ca la
    compensare), altfel numele (majuscule, spațiile strânse), prefixat cu „~” ca să nu se confunde cu un cod. None = fără partener."""
    from core.compensari_api import cui_partener
    c = cui_partener(cui)
    if c:
        return c
    n = " ".join(str(nume or "").split()).upper()
    return ("~" + n) if n else None


def _e_avans(cont):
    return any(str(cont).startswith(p) for p in CONTURI_AVANS)


def _e_disponibil(cont):
    return any(str(cont).startswith(p) for p in CONTURI_DISPONIBIL)


# ── citiri ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def reevaluari(cur, schema, pana_la):
    """Reevaluările consemnate până la `pana_la` (inclusiv), cu starea notei lor: [{id, data, nota_id, status, factura_id, cont,
    moneda, sold_valuta, curs_vechi, curs_nou, diferenta, sursa, partener, manual, clauza}], în ordinea datei."""
    s = _q(schema)
    cur.execute("SELECT r.id, r.data, r.inregistrare_id, i.status, r.factura_id, r.cont, r.moneda, r.sold_valuta, r.curs_vechi, "
                "r.curs_nou, r.diferenta, r.sursa, r.partener, r.manual, r.clauza FROM %sreevaluari_valuta r "
                "JOIN %sinregistrari i ON i.id = r.inregistrare_id WHERE r.data <= %%s ORDER BY r.data, r.id" % (s, s), (pana_la,))
    chei = ("id", "data", "nota_id", "status", "factura_id", "cont", "moneda", "sold_valuta", "curs_vechi", "curs_nou", "diferenta",
            "sursa", "partener", "manual", "clauza")
    return [_rand(r, chei) for r in cur.fetchall()]


def facturi_in_valuta(cur, schema, sfarsit):
    """Facturile în valută emise până la `sfarsit`, nestornări, nu proforme / avize: [{id, directie, tip, serie, numar, data_emitere,
    moneda, total, total_lei, curs_bnr, tert_nume, tert_cui, platita_la, storno_valuta, storno_lei}]."""
    s = _q(schema)
    cur.execute("SELECT f.id, f.directie, f.tip, f.serie, f.numar, f.data_emitere, upper(f.moneda) AS moneda, f.total, f.total_lei, f.curs_bnr, "
                "f.tert_nume, f.tert_cui, f.platita_la, "
                "(SELECT COALESCE(SUM(st.total), 0) FROM %sfacturi st WHERE st.storno_din_id = f.id AND st.data_emitere <= %%s) AS storno_valuta, "
                "(SELECT COALESCE(SUM(COALESCE(st.total_lei, st.total * st.curs_bnr)), 0) FROM %sfacturi st "
                " WHERE st.storno_din_id = f.id AND st.data_emitere <= %%s) AS storno_lei "
                "FROM %sfacturi f WHERE upper(COALESCE(f.moneda, 'RON')) <> 'RON' AND COALESCE(f.tip, 'factura') = 'factura' "
                "AND f.storno_din_id IS NULL AND f.data_emitere <= %%s ORDER BY f.data_emitere, f.id" % (s, s, s),
                (sfarsit, sfarsit, sfarsit))
    chei = ("id", "directie", "tip", "serie", "numar", "data_emitere", "moneda", "total", "total_lei", "curs_bnr", "tert_nume", "tert_cui",
            "platita_la", "storno_valuta", "storno_lei")
    return [_rand(r, chei) for r in cur.fetchall()]


def monede_pe_partener(cur, schema, sfarsit):
    """{(directie, partener): {monede}} — monedele facturilor (inclusiv RON) fiecărui partener, pe fiecare parte, până la `sfarsit`.
    Un partener cu mai multe monede pe aceeași parte face plata lui nelegată neatribuibilă unei monede."""
    cur.execute("SELECT directie, tert_cui, tert_nume, upper(COALESCE(moneda, 'RON')) AS m FROM %sfacturi WHERE COALESCE(tip, 'factura') "
                "= 'factura' AND storno_din_id IS NULL AND data_emitere <= %%s" % _q(schema), (sfarsit,))
    out = {}
    for r in cur.fetchall():
        d, cui, nume, m = list(r.values()) if isinstance(r, dict) else r
        out.setdefault((d, cheie_partener(cui, nume)), set()).add(m)
    return out


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


def plati_nelegate(cur, schema, conturi, sfarsit):
    """[decizia 10.3] Liniile VALIDATE pe conturile de terți `conturi`, până la `sfarsit`, ale notelor FĂRĂ factură (banca nealocată, o
    notă din Registrul jurnal): [{nota_id, data, document, cont_debit, cont_credit, suma, partener}]. Nu intră: notele de reevaluare
    (au rândurile lor în `reevaluari_valuta`), compensările (`compensari`) și notele chitanțelor legate de o factură (le numără
    `chitante_nelegate`)."""
    if not conturi:
        return []
    s = _q(schema)
    cur.execute("SELECT i.id, i.data, i.document_ref, l.cont_debit, l.cont_credit, l.suma, l.partener_cui, l.partener_nume "
                "FROM %sinregistrari i JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                "WHERE i.status = 'validata' AND i.data <= %%s AND i.factura_id IS NULL "
                "AND (l.cont_credit = ANY(%%s) OR l.cont_debit = ANY(%%s)) "
                "AND NOT EXISTS (SELECT 1 FROM %sreevaluari_valuta r WHERE r.inregistrare_id = i.id) "
                "AND NOT EXISTS (SELECT 1 FROM %scompensari cz WHERE cz.inregistrare_id = i.id) "
                "AND NOT EXISTS (SELECT 1 FROM %schitante c WHERE c.inregistrare_id = i.id AND c.factura_id IS NOT NULL AND NOT c.anulata) "
                "ORDER BY i.data, i.id, l.id" % (s, s, s, s, s), (sfarsit, list(conturi), list(conturi)))
    out = []
    for r in cur.fetchall():
        nid, data, doc, cd, cc, suma, pcui, pnume = list(r.values()) if isinstance(r, dict) else r
        out.append({"nota_id": nid, "data": data, "document": doc, "cont_debit": cd, "cont_credit": cc, "suma": _dec(suma),
                    "partener": cheie_partener(pcui, pnume)})
    return out


def monede_cotate(cur):
    """Monedele pe care BNR le-a cotat (cache-ul local) — ca să se recunoască o monedă în simbolul / denumirea contului."""
    return _cb._monede_din_cache(cur.connection)


def denumiri_conturi(cur, schema, simboluri):
    if not simboluri:
        return {}
    cur.execute("SELECT simbol, denumire FROM %splan_conturi WHERE simbol = ANY(%%s)" % _q(schema), (list(simboluri),))
    return {_v(r, "simbol", 0): _v(r, "denumire", 1) for r in cur.fetchall()}


def solduri_conturi(cur, schema, sfarsit):
    """{cont: sold net în lei (debit − credit)} la `sfarsit`, din notele validate și soldurile de preluare (`bilant_api.sold_la`, aceeași
    sursă ca balanța). {} dacă ziua e înaintea soldurilor de preluare."""
    from psycopg2.extras import RealDictCursor
    from core import bilant_api as _ba
    with cur.connection.cursor(cursor_factory=RealDictCursor) as c2:
        sl = _ba.sold_la(c2, schema, sfarsit)
    return {k: d - c for k, (d, c) in (sl or {}).items() if d - c != 0}


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
                c, dc, _s = _cb.curs_sfarsit_luna(cur.connection, moneda, sfarsit)
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
    r = _dc.reevaluare_element(el["sold_valuta"], el["lei_evidenta"], c, tip, el["cont"], in_lei_cu_clauza=bool(el.get("clauza")))
    el["lei_bnr"], el["diferenta"] = str(r["lei_nou"]), str(r["diferenta"])
    el["cont_diferenta"], el["sens"], el["linie"] = r["cont"], r["sens"], r["linie"]
    return el


def _numar(v):
    """Un sold scris pe ecran („1.000,50” / „1000.5”) ca Decimal, sau None dacă nu e un număr."""
    t = str(v).strip().replace(" ", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        x = Decimal(t)
    except Exception:   # noqa: BLE001 — orice text nenumeric e același refuz, numit de apelant
        return None
    return x if x.is_finite() else None


def _aplica(el, c, erori):
    """Completarea contabilului, numai pe câmpurile editabile ale elementului; refuzurile se adaugă în `erori` (toate deodată)."""
    if not c:
        return
    nume = el.get("document") or el.get("partener") or "contul %s" % el["cont"]
    for k, v in c.items():
        if v in (None, "") or k == "manual":
            continue
        camp = "rv-%s-%s" % (k, el["cheie"])
        if k not in el["editabile"]:   # FORMĂ: câmp needitabil pe element
            if k == "clauza" and v in (False, "false", "nu", "0", 0):
                continue
            erori.append({"camp": camp, "mesaj": "%s: câmpul „%s” nu se completează pe acest element." % (
                nume, {"sold_valuta": "sold în valută", "clauza": "în lei cu clauză valutară"}.get(k, k))})
        elif k == "sold_valuta":
            x = _numar(v)
            if x is None or x <= 0:
                erori.append({"camp": camp, "mesaj": "Soldul în valută pentru %s trebuie să fie un număr pozitiv." % nume})
            else:
                el["sold_valuta"], el["estimat"] = str(x.quantize(B, rounding=ROUND_HALF_UP)), False
        elif k == "moneda":
            el["moneda"] = str(v).strip().upper()
        elif k == "clauza":
            el["clauza"] = v in (True, "true", "da", "1", 1)


def _neinclusa(factura_id, document, partener, motiv, sfarsit):
    """[lotul 11, decizia 21.08: afirmațiile despre datele firmei sunt obiecte cu `fel`] O factură în valută (sau soldul unui partener)
    care NU intră în reevaluarea lunii, cu motivul: un fapt despre evidența firmei la sfârșitul lunii, cu domeniul (documentul) și pe ce
    se sprijină. `document`, `partener`, `motiv`, `factura_id` = cheile citite de ecran (`#rv-neincluse`)."""
    from core import afirmatii as _af
    return _af.afirmatie("fapt", "neinclus_in_reevaluare", motiv, factura_id=factura_id, document=document, partener=partener,
                         unde="%s, la %s" % (document or partener or "sold", sfarsit),
                         temei_completitudine="facturile în valută ale firmei și plățile lor până la sfârșitul lunii")


def _elemente_parteneri(cur, schema, sfarsit, rev, completari, curs_fn, erori, neincluse):
    """Creanțele și datoriile în valută, pe partener (decizia 10.3)."""
    from core import contare_facturi as _cf
    from core import eticheta_nota as _et
    fact = facturi_in_valuta(cur, schema, sfarsit)
    note = _cf.note_pe_facturi(cur, schema, [f["id"] for f in fact])
    chit = chitante_nelegate(cur, schema, [f["id"] for f in fact], sfarsit)
    grupuri = {}
    for f in fact:
        nf = note.get(f["id"], [])
        doc = _et.factura_din_rand(f)
        cont, data_contare = _cont_tert(nf, f["directie"])
        if f["curs_bnr"] is None:
            neincluse.append(_neinclusa(f["id"], doc, f["tert_nume"], "factura n-are cursul BNR — nu se poate exprima în lei", sfarsit))
            continue
        if not cont or data_contare > sfarsit:
            ciorna = any(n["e_contare"] for n in nf)
            neincluse.append(_neinclusa(f["id"], doc, f["tert_nume"],
                                        ("nota ei de contare e ciornă — valideaz-o în Registrul jurnal, apoi reevaluarea o cuprinde" if ciorna
                                         else "nu e contată — contează factura, apoi reevaluarea o cuprinde"), sfarsit))
            continue
        if f["platita_la"] is not None and f["platita_la"].date() <= sfarsit:
            continue
        pk = cheie_partener(f["tert_cui"], f["tert_nume"])
        g = grupuri.setdefault((cont, pk, f["moneda"]), {"nume": f["tert_nume"], "directie": f["directie"], "facturi": [], "ev": []})
        g["facturi"].append((f["id"], doc))
        valuta = _dec(f["total"]) + _dec(f["storno_valuta"])
        lei = _lei(_dec(f["total_lei"] if f["total_lei"] is not None else _dec(f["total"]) * _dec(f["curs_bnr"])) + _dec(f["storno_lei"]))
        g["ev"].append((f["data_emitere"], 0, "factura", (valuta, lei, _dec(f["curs_bnr"]))))
        for d, x in _plati_din_note(nf, cont, f["directie"], sfarsit) + chit.get(f["id"], []):
            g["ev"].append((d, 1, "plata", x))
    # plățile nelegate, pe partener (decizia 10.3)
    monede = monede_pe_partener(cur, schema, sfarsit) if grupuri else {}
    pe_cont = {}
    for (cont, pk, _m), g in grupuri.items():
        pe_cont.setdefault((cont, pk), []).append(g)
    for p in plati_nelegate(cur, schema, sorted({k[0] for k in grupuri}), sfarsit):
        for cont, lei in ((p["cont_credit"], p["suma"]), (p["cont_debit"], -p["suma"])):
            gs = pe_cont.get((cont, p["partener"]))
            if not gs:
                continue
            stinge = lei if gs[0]["directie"] == "emisa" else -lei   # creanța se stinge pe credit, datoria pe debit
            if stinge <= 0:
                continue
            rand = {"data": str(p["data"]), "lei": str(_lei(stinge)), "document": p["document"], "nota_id": p["nota_id"]}
            if len(gs) > 1 or len(monede.get((gs[0]["directie"], p["partener"]), set())) > 1:
                for g in gs:   # partenerul are facturi în mai multe monede pe aceeași parte: plata nu se atribuie unei monede
                    g.setdefault("de_legat", []).append(rand)
            else:
                gs[0]["ev"].append((p["data"], 1, "plata", stinge))
                gs[0].setdefault("nelegate", []).append(rand)
    elemente = []
    for (cont, pk, m), g in sorted(grupuri.items(), key=lambda kv: (kv[1]["nume"] or "", kv[0][0], kv[0][1] or "", kv[0][2])):
        tip = "creanta" if g["directie"] == "emisa" else "datorie"
        ids = {fid for fid, _d in g["facturi"]}
        for r in rev:   # reevaluările anterioare: pe partener (lotul 11) sau, cele dinainte, pe factură
            if (r["factura_id"] is None and r["partener"] == pk and r["cont"] == cont and r["moneda"] == m) or r["factura_id"] in ids:
                g["ev"].append((r["data"], 2, "reevaluare", r))
        valuta = lei = Decimal("0")
        curs_ev, sursa_ev, cu_plati = None, None, False
        for d, _o, fel, x in sorted(g["ev"], key=lambda e: (e[0], e[1])):
            if fel == "factura":
                valuta, lei = valuta + x[0], lei + x[1]
                curs_ev, sursa_ev = x[2], ("factura" if sursa_ev is None else "medie")
            elif fel == "plata":    # plata stinge creanța / datoria la cursul din evidență al partenerului (pct.322 alin.(1))
                c = (lei / valuta) if valuta > 0 else curs_ev
                valuta -= x / c
                lei -= x
                cu_plati = True
            else:                   # reevaluarea: diferența ei a intrat pe cont; cea pe partener fixează și soldul în valută
                lei += _dec(x["diferenta"])
                if x["factura_id"] is None:
                    valuta = _dec(x["sold_valuta"])
                sursa_ev = str(d)
        valuta, lei = valuta.quantize(B, rounding=ROUND_HALF_UP), _lei(lei)
        documente = ", ".join(dd for _i, dd in g["facturi"] if dd)
        if valuta <= _TOL and not g.get("de_legat"):
            if valuta < -_TOL:
                neincluse.append(_neinclusa(None, documente, g["nume"],
                                            "plătit mai mult decât facturile în %s (sold invers pe %s) — un avans nu se reevaluează (%s)"
                                            % (m, cont, TEMEI_AVANSURI), sfarsit))
            continue
        cheie = "p:%s:%s:%s" % (cont, pk or "", m)
        pozitiv = valuta > _TOL
        el = {"cheie": cheie, "fel": tip, "factura_id": None, "facturi": sorted(ids), "document": documente, "partener": g["nume"],
              "partener_cheie": pk, "cont": cont, "moneda": m, "sold_valuta": str(valuta) if pozitiv else None,
              "estimat": cu_plati and pozitiv,
              "curs_evidenta": str(_cb.curs_derivat(lei / valuta, m)) if pozitiv else None,   # [C88] precizia BNR a monedei
              "curs_evidenta_din": sursa_ev if pozitiv else None, "lei_evidenta": str(lei),
              "plati_nelegate": g.get("nelegate", []), "plati_de_legat": g.get("de_legat", []), "manual": False, "clauza": False,
              "editabile": ["sold_valuta"] if (cu_plati or not pozitiv) else [], "de_completat": []}
        _aplica(el, completari.pop(cheie, None), erori)
        if el["sold_valuta"] is not None and el["curs_evidenta"] is None:
            el["curs_evidenta"] = str(_cb.curs_derivat(lei / _dec(el["sold_valuta"]), el["moneda"]))
            el["curs_evidenta_din"] = "sold"
        elemente.append(_cu_curs(el, curs_fn, tip))
    return elemente


def _refuz_rand_manual(cont, i, solduri, disponibil, conturi_parteneri, noi):
    """Motivul pentru care rândul manual `i` (contul `cont`) nu se primește, sau None."""
    if not cont:
        return "Rândul %d: scrie contul în valută de reevaluat." % (i + 1)
    if _e_avans(cont):
        # normativ: OMFP 1802/2014 pct.316 alin.(2) — avansurile (409, 419, 4093, 4094) nu se evaluează la curs la finele lunii
        return "Contul %s e de avansuri: avansurile nu se reevaluează la curs la sfârșitul lunii (%s)." % (cont, TEMEI_AVANSURI)
    if cont in conturi_parteneri:
        return "Contul %s e reevaluat pe parteneri, mai sus — corectează soldul în valută pe rândul partenerului." % cont
    if cont in disponibil:
        return "Contul %s e deja în propunere, la disponibilități — completează-l pe rândul lui." % cont
    if cont in noi:
        return "Contul %s apare de două ori în ajustări." % cont
    if not solduri.get(cont):
        return "Contul %s n-are sold la sfârșitul lunii în evidență — n-are ce se reevalua." % cont
    return None


def _elemente_conturi(cur, schema, sfarsit, inceput, rev, completari, manuale, conturi_parteneri, curs_fn, erori):
    """Disponibilitățile în valută și conturile ajustate manual (luna trecută sau acum, pe ecran)."""
    solduri = solduri_conturi(cur, schema, sfarsit)
    disponibil = sorted(k for k, v in solduri.items() if _e_disponibil(k) and _lei(v) > 0)
    # conturile ajustate manual în lunile trecute revin în propunere (moneda știută; soldul în valută se cere din nou)
    anterioare = {r["cont"] for r in rev if r["factura_id"] is None and r["partener"] is None and not _e_disponibil(r["cont"])}
    noi = {}
    for i, m in enumerate(manuale):
        cont = str((m or {}).get("cont") or "").strip()
        motiv = _refuz_rand_manual(cont, i, solduri, disponibil, conturi_parteneri, noi)
        if motiv:
            erori.append({"camp": "rv-m%d-cont" % i, "mesaj": motiv})
        else:
            noi[cont] = (i, m)
    manuale_conturi = sorted((anterioare | set(noi)) - set(disponibil) - set(conturi_parteneri))
    den = denumiri_conturi(cur, schema, disponibil + manuale_conturi)
    cotate = monede_cotate(cur) if (disponibil or manuale_conturi) else set()
    elemente = []
    for cont in disponibil + manuale_conturi:
        net = _lei(solduri.get(cont, 0))
        if not net:
            continue   # contul ajustat luna trecută nu mai are sold (împrumutul s-a rambursat)
        manual = cont not in disponibil
        tip = "disponibil" if not manual else ("creanta" if net > 0 else "datorie")
        ale_contului = [r for r in rev if r["factura_id"] is None and r["partener"] is None and r["cont"] == cont]
        a_lunii = [r for r in ale_contului if r["data"] >= inceput]
        moneda = (None if manual else _moneda_din_cont(cont, den.get(cont), cotate)) or \
            (ale_contului[-1]["moneda"] if ale_contului else None)
        cheie = ("m" if manual else "c") + cont
        L = abs(net)
        el = {"cheie": cheie, "fel": tip, "factura_id": None, "document": None, "partener": den.get(cont), "cont": cont,
              "moneda": moneda, "sold_valuta": None, "estimat": False, "curs_evidenta": None, "curs_evidenta_din": None,
              "lei_evidenta": str(L), "manual": manual, "clauza": bool(ale_contului and ale_contului[-1]["clauza"]),
              "sold_anterior": str(_dec(ale_contului[-1]["sold_valuta"])) if ale_contului else None,
              "editabile": ["sold_valuta", "moneda"] + (["clauza"] if manual else []), "de_completat": [],
              "plati_nelegate": [], "plati_de_legat": []}
        if cont in noi:
            el["rand_manual"] = noi[cont][0]
        if a_lunii:           # deja reevaluat în lună: soldul în valută e cel consemnat, iar ciorna lunii își adaugă diferența
            r = a_lunii[-1]
            el.update(moneda=r["moneda"], sold_valuta=str(_dec(r["sold_valuta"])), curs_evidenta=str(_dec(r["curs_nou"])),
                      curs_evidenta_din=str(r["data"]), editabile=[],
                      lei_evidenta=str(L + sum((_dec(x["diferenta"]) for x in a_lunii if x["status"] == "ciorna"), Decimal("0"))))
        _aplica(el, completari.pop(cheie, None), erori)
        if cont in noi:       # rândul adăugat pe ecran: refuzul stă lângă câmpul RÂNDULUI, nu al elementului
            i, m = noi[cont]
            ale_randului = []
            _aplica(el, {k: m.get(k) for k in ("moneda", "sold_valuta", "clauza")}, ale_randului)
            if not ale_contului and m.get("clauza") in (None, ""):
                # [DS cap.17 v2.79] contul adăugat acum, fără „Da / Nu” la clauza valutară: 765/665 sau 768/668 (pct.325 alin.(3)) nu
                # se alege în locul omului — rămâne de completat (generarea se refuză lângă câmp), nu „Nu” implicit
                el["clauza"] = None
            erori += [dict(e, camp="rv-m%d-%s" % (i, e["camp"].split("-")[1])) for e in ale_randului]
        if el.get("moneda") and not re.fullmatch(r"[A-Z]{3}", el["moneda"]):
            erori.append({"camp": ("rv-m%d-moneda" % noi[cont][0]) if cont in noi else "rv-moneda-%s" % cheie,
                          "mesaj": "Moneda contului %s se scrie cu trei litere (ex. EUR)." % cont})
            el["moneda"] = None
        if el["sold_valuta"] is not None and el["curs_evidenta"] is None:
            el["curs_evidenta"] = str(_cb.curs_derivat(L / _dec(el["sold_valuta"]), el["moneda"]))
            el["curs_evidenta_din"] = "sold"
        elemente.append(_cu_curs(el, curs_fn, tip))
    return elemente


def propunere(cur, schema, an, luna, completari=None, cu_ciorna_lunii=False, curs_fn=None, manuale=None):
    """Propunerea reevaluării lunii (an, luna). `completari` = {cheie: {sold_valuta?, moneda?, clauza?}} — ce a scris contabilul pe ecran,
    numai pe câmpurile `editabile` ale elementului; `manuale` = [{cont, moneda, sold_valuta, clauza?}] — conturile adăugate pe ecran la
    ajustarea manuală. Refuzurile lor: `RefuzReevaluare`, toate deodată. `cu_ciorna_lunii`: reevaluările lunii aflate în ciornă
    contează ca făcute (controalele închiderii; CIORNE o spune separat) — altfel se ignoră, fiindcă generarea le înlocuiește.
    -> {an, luna, data, elemente: [...], neincluse: [...], totaluri, ciorna_lunii: [nota_id], temei}."""
    import calendar as _cal
    from datetime import date as _date
    completari = dict(completari or {})
    inceput = _date(int(an), int(luna), 1)
    sfarsit = _date(int(an), int(luna), _cal.monthrange(int(an), int(luna))[1])
    curs_fn = curs_fn or _curs_fn(cur, sfarsit)
    toate = reevaluari(cur, schema, sfarsit)
    # numai ciornele PROPUNERII se înlocuiesc la generare (și se ignoră aici); reevaluarea din vechiul formular manual (lotul 10, scos
    # în lotul 11) rămâne a omului și contează ca făcută — altfel diferența ei s-ar înregistra a doua oară
    _a_propunerii = lambda r: r["data"] >= inceput and r["status"] == "ciorna" and r["sursa"] == "propunere"
    ciorna_lunii = sorted({r["nota_id"] for r in toate if _a_propunerii(r)})
    rev = [r for r in toate if cu_ciorna_lunii or not _a_propunerii(r)]
    erori, neincluse = [], []
    elemente = _elemente_parteneri(cur, schema, sfarsit, rev, completari, curs_fn, erori, neincluse)
    elemente += _elemente_conturi(cur, schema, sfarsit, inceput, rev, completari, list(manuale or []), {e["cont"] for e in elemente},
                                  curs_fn, erori)
    for k in sorted(completari):   # o completare pe un element care nu mai e în propunere
        erori.append({"camp": "rv-sold_valuta-%s" % k, "mesaj": "Elementul %s nu mai e în propunerea lunii — reîncarcă propunerea." % k})
    if erori:
        raise RefuzReevaluare(erori)   # FORMĂ: completările de pe ecran (normativul — avansurile — își citează temeiul în mesaj)
    for el in elemente:
        el["de_completat"] = [c for c in ("moneda", "sold_valuta") if el.get(c) in (None, "")] + (
            ["clauza"] if el.get("manual") and el.get("clauza") is None else [])
    return {"an": int(an), "luna": int(luna), "data": str(sfarsit), "elemente": elemente, "neincluse": neincluse,
            "totaluri": totaluri(elemente), "ciorna_lunii": ciorna_lunii, "temei": TEMEI}


def _moneda_din_cont(cont, denumire, cotate):
    """Moneda din simbolul sau denumirea contului, dacă ele conțin EXACT o monedă cotată de BNR („5124.EUR”, „BT cont EUR”)."""
    gasite = {t for t in re.findall(r"[A-Za-z]{3}", "%s %s" % (cont, denumire or "")) if t.upper() == t and t in cotate}
    return gasite.pop() if len(gasite) == 1 else None


def totaluri(elemente):
    t765 = sum((_dec(e["linie"][2]) for e in elemente if e.get("linie") and e["sens"] == "favorabila"), Decimal("0"))
    t665 = sum((_dec(e["linie"][2]) for e in elemente if e.get("linie") and e["sens"] == "nefavorabila"), Decimal("0"))
    return {"venit": str(_lei(t765)), "cheltuiala": str(_lei(t665)), "net": str(_lei(t765 - t665)),
            "de_completat": sum(1 for e in elemente if e["de_completat"] or (e.get("moneda") and e.get("curs_bnr") is None)),
            "de_legat": sum(len(e.get("plati_de_legat") or []) for e in elemente)}


def de_reevaluat(prop):
    """Elementele care opresc închiderea: cu diferență nenulă neînregistrată, fără ce trebuie ca să se calculeze (soldul în valută,
    moneda, cursul BNR) sau cu o plată nelegată pe care n-o pot atribui unei monede."""
    return [e for e in prop["elemente"]
            if e["de_completat"] or e.get("curs_bnr") is None or e.get("plati_de_legat")
            or (e.get("diferenta") and _dec(e["diferenta"]) != 0)]


def blocaj_inchidere(cur, schema, an, luna):
    """[lotul 11, sursa unică a textului] Blocajul REEVALUARE_VALUTA din „Ce oprește închiderea” (`uc_comun.controale_inchidere`), sau
    None: (mesaj, câte elemente). Numără partenerii și conturile, cu temeiul: OMFP 1802/2014 pct.325 alin.(1) „La finele fiecărei luni,
    creanțele și datoriile în valută se evaluează la cursul [...] din ultima zi bancară a lunii în cauză” — lunar și obligatoriu."""
    from core.common import cate as _cate
    de = de_reevaluat(propunere(cur, schema, an, luna, cu_ciorna_lunii=True))
    if not de:
        return None
    parteneri = sum(1 for e in de if e["fel"] in ("creanta", "datorie") and not e["manual"])
    conturi = len(de) - parteneri
    ce = ", ".join(x for x in (_cate(parteneri, "partener", "parteneri") if parteneri else "",
                               _cate(conturi, "cont în valută", "conturi în valută") if conturi else "") if x)
    return ("soldurile în valută de la sfârșitul lunii nu sunt reevaluate la cursul BNR din ultima zi bancară (%s: %s); deschide "
            "„Reevaluare valută”, verifică propunerea și generează nota" % (TEMEI, ce), len(de))


# ── scrieri ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def consemneaza(cur, schema, nota_id, data, elemente, sursa="propunere"):
    """Un rând în `reevaluari_valuta` pe element reevaluat, legat de notă (ștergerea notei îl șterge: ON DELETE CASCADE). `diferenta`
    e semnată: cu cât a crescut soldul în lei al elementului. Cursul nou devine cursul din evidență al lunii următoare. Partenerul (cheia
    lui) pe creanțe / datorii; `manual` = contul adăugat la ajustarea manuală; `clauza` = în lei cu clauză valutară (768 / 668)."""
    for e in elemente:
        cur.execute("INSERT INTO %sreevaluari_valuta (data, inregistrare_id, factura_id, cont, moneda, sold_valuta, curs_vechi, "
                    "curs_nou, diferenta, sursa, partener, manual, clauza) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, "
                    "%%s, %%s, %%s)" % _q(schema),
                    (data, nota_id, e["factura_id"], e["cont"], e["moneda"], e["sold_valuta"], e["curs_evidenta"], e["curs_bnr"],
                     e["diferenta"], sursa, e.get("partener_cheie"), bool(e.get("manual")), bool(e.get("clauza"))))
