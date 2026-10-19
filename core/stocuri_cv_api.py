# -*- coding: utf-8 -*-
"""Stocuri cantitativ-valorice — strat API. Motorul: core/stocuri_cv.py.
Ieșirile la CMP generează notă ciornă (cont_cheltuiala = cont_stoc)."""
import re

from core import pdf_util as _pu
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from psycopg2.extras import RealDictCursor
from core import stocuri_cv as _m
from core import eticheta_nota as _et


def _miscari(cur, schema, articol_id):
    from core import repo_stocuri   # [retest 07.10 R1] o singură citire a fișei (cu stornările)
    return [dict(r) for r in repo_stocuri.miscari_ale_articolului(cur, schema, articol_id)]


def articole(conn, schema):
    """Articolele cu stocul curent (cantitate, valoare, CMP)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole ORDER BY denumire")
        out = []
        for a in cur.fetchall():
            fisa = _m.fisa_magazie(_miscari(cur, schema, a["id"]))
            if fisa:
                cant, val, cmp = fisa[-1]["sold_cantitate"], fisa[-1]["sold_valoare"], fisa[-1]["cmp"]
            else:
                cant = val = Decimal("0"); cmp = None
            out.append({"id": a["id"], "denumire": a["denumire"], "um": a["um"],
                        "cont_stoc": a["cont_stoc"], "cont_cheltuiala": a["cont_cheltuiala"],
                        "barcode": a.get("barcode"), "nivel_minim": str(a["nivel_minim"]) if a.get("nivel_minim") is not None else None,
                        "stoc": str(cant), "valoare": str(val),
                        "cmp": str(cmp) if cmp is not None else None})
        return out


def retete_vizibile(conn, schema):
    """[comanda Costin 05.10.2026 pct.10] „Rețete apare doar la firmele HoReCa”: CAEN-ul firmei în lista din CF (`core.horeca`),
    sau firma are deja rețete (datele existente nu se ascund)."""
    from core import horeca
    with conn.cursor() as cur:
        cur.execute(f"SELECT caen FROM {schema}.firma_profil WHERE id = 1")
        r = cur.fetchone()
        if horeca.e_horeca(r[0] if r else None):
            return True
        cur.execute(f"SELECT 1 FROM {schema}.retete LIMIT 1")
        return cur.fetchone() is not None


#: [deficiența 403] documentul scris cu id-ul intern („Factura #1”, „factură primită #2”) de versiunile de dinainte de 258 (15.10.2026)
_DOC_CU_ID = re.compile(r"#\s*\d+")


def documente_fisa(cur, schema, linii):
    """[deficiența 403, retestul Costin 19.10.2026] „Fișa de magazie: documente «Factura #1», «Factura #48», «factură primită #2» (id
    intern) — toate cu serie, număr, dată.” Mișcările scrise atunci păstrează textul vechi; fișa îl numește din documentul legat
    (factura: `eticheta_nota.factura`, NIR-ul: `jurnal_api.eticheta_document`), ca Registrul jurnal. {id mișcare: document}."""
    ids = [l["id"] for l in linii if l.get("id") and (not l.get("document") or _DOC_CU_ID.search(str(l.get("document"))))]
    if not ids:
        return {}
    from core import jurnal_api as _j
    cur.execute(f"""SELECT m.id, m.factura_id, n.numar AS nir_numar, n.data AS nir_data FROM {schema}.miscari_stoc m
                    LEFT JOIN {schema}.nir n ON n.id = m.nir_id WHERE m.id = ANY(%s)""", (ids,))
    out = {}
    for r in cur.fetchall():
        if r["factura_id"]:
            out[r["id"]] = _et.factura(cur, schema, r["factura_id"])
        elif r["nir_numar"] is not None:
            out[r["id"]] = _j.eticheta_document("NIR", r["nir_numar"], r["nir_data"])
    return out


def fisa(conn, schema, articol_id):
    """Fișa de magazie a unui articol."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (articol_id,))
        a = cur.fetchone()
        if not a:
            return None
        linii = _m.fisa_magazie(_miscari(cur, schema, articol_id))
        doc = documente_fisa(cur, schema, linii)
    return {"articol": {"id": a["id"], "denumire": a["denumire"], "um": a["um"]},
            "linii": [{"data": str(l["data"]), "tip": l["tip"], "document": doc.get(l.get("id"), l.get("document")),
                       "cantitate": str(l["cantitate"]),
                       "pret_unitar": str(l["pret_unitar"]) if l.get("pret_unitar") else None,
                       "valoare": str(l["valoare"]), "sold_cantitate": str(l["sold_cantitate"]),
                       "sold_valoare": str(l["sold_valoare"]),
                       "cmp": str(l["cmp"]) if l["cmp"] is not None else None}
                      for l in linii]}


def intrare(conn, schema, corp, factura_id=None):
    """corp: {articol_id | denumire+um+cont_stoc+cont_cheltuiala, data, cantitate,
    pret_unitar, document?}. Nota de intrare vine din NIR/factură — aici doar mișcarea."""
    # [comanda Costin 06.10.2026 pct.1b, clasa] „Un preț pe care nu l-a ales nimeni” nu intră în fișa de magazie: ecranul trimitea
    # golul ca 0 (`parseFloat(...) || 0`), iar intrarea la preț 0 strică CMP-ul tăcut. Lipsa se refuză, ÎNAINTE de a crea
    # articolul nou (înainte, refuzul venea după INSERT); `Decimal(str(None))` ieșea `500` (InvalidOperation nu e ValueError).
    if corp.get("pret_unitar") is None or str(corp.get("pret_unitar")).strip() == "":
        return {"eroare": "Prețul unitar al intrării lipsește. Scrie prețul de achiziție; nu se presupune niciunul."}
    cant = Decimal(str(corp["cantitate"]))
    pret = Decimal(str(corp["pret_unitar"]))
    if cant <= 0 or pret < 0:
        return {"eroare": "cantitate/preț invalide"}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        aid = corp.get("articol_id")
        if not aid:
            cur.execute(f"""INSERT INTO {schema}.articole (denumire, um, cont_stoc, cont_cheltuiala)
                            VALUES (%s,%s,%s,%s) RETURNING id""",
                        (corp["denumire"], corp.get("um", "buc"),
                         (str(corp.get("cont_stoc") or "").strip() or "371"), (str(corp.get("cont_cheltuiala") or "").strip() or "607")))
            aid = cur.fetchone()["id"]
            # [415] articolul creat de un document (factura primită) își ia cota de pe linia lui, în nomenclator
            from core import produse_api as _pa
            _pa.asigura_din_document(cur, schema, corp["denumire"], corp.get("um"), corp.get("cota_tva"), corp.get("document"))
        val = (cant * pret).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                        (articol_id, data, tip, cantitate, pret_unitar, valoare, document, locatie, factura_id)
                        VALUES (%s,%s,'intrare',%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (aid, corp["data"], cant, pret, val, corp.get("document"),
                     corp.get("locatie") or None, factura_id))
        mid = cur.fetchone()["id"]
    return {"id": mid, "articol_id": aid, "valoare": str(val)}


def intrare_din_factura(conn, schema, factura_id, cont_stoc, data, cont_cheltuiala=None):
    """[reconciliere factura->stoc] Recepția CANTITATIVĂ a unei facturi PRIMITE de marfă: creează intrarea
    în fișa de magazie (miscari_stoc) din liniile facturii, legată prin `factura_id`. Cantitate-DOAR — nota
    contabilă (371=401, 4426=401) vine deja din factură (contare_facturi), deci NU se dublează. O singură
    recepție = notă (din factură) + cantitate (aici). Fără asta, 371-contabil urcă dar fișa nu se mișcă
    (divergență GL↔fișă). OMFP 1802/2014: recepția mărfii e un act unic; evidența cantitativ-valorică
    concordă cu contabilitatea sintetică.
    Idempotent pe `factura_id` (o a doua chemare nu creează a doua intrare). Potrivește articolul pe
    denumire (case-insensitive); dacă nu există, îl creează (ca `intrare`)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # [retest 07.10 R1] numai o intrare VIE (nestornată) face factura „intrată”: după respingere, refacerea o scrie din nou
        cur.execute(f"""SELECT 1 FROM {schema}.miscari_stoc m WHERE m.factura_id=%s AND m.tip='intrare' AND m.anuleaza_id IS NULL
                        AND NOT EXISTS (SELECT 1 FROM {schema}.miscari_stoc r WHERE r.anuleaza_id = m.id) LIMIT 1""",
                    (factura_id,))
        if cur.fetchone():
            return {"stare": "deja_intrat", "factura_id": factura_id, "linii": 0}
        # [08.10.2026, decizia Costin §6 pct.1] factura LEGATĂ de un NIR „fără factură”: marfa a intrat în fișă prin NIR — „fără a
        # doua intrare în stoc”
        cur.execute(f"SELECT id FROM {schema}.nir WHERE factura_id = %s LIMIT 1", (factura_id,))
        _nir = cur.fetchone()
        if _nir:
            return {"stare": "intrat_prin_nir", "factura_id": factura_id, "nir_id": _nir["id"], "linii": 0}
        cur.execute(f"""SELECT descriere, cantitate, pret_unitar, cont_cheltuiala, cota_tva FROM {schema}.factura_linii
                        WHERE factura_id=%s ORDER BY id""", (factura_id,))
        brute = []
        from core import contare_facturi as _cf
        for l in cur.fetchall():
            den = (l["descriere"] or "").strip()
            cant = Decimal(str(l["cantitate"] or 0))
            pret = Decimal(str(l["pret_unitar"] or 0))
            # [deficiența 418b] contul LINIEI (gol = al facturii): numai liniile contate pe un cont de stoc intră în fișa de magazie
            cont_l = (l["cont_cheltuiala"] or "").strip() or cont_stoc
            if not den or cant <= 0 or not any(cont_l.startswith(p) for p in _cf.CONTURI_FOND_EXACT):
                continue
            cur.execute(f"SELECT id FROM {schema}.articole WHERE lower(denumire)=lower(%s) LIMIT 1", (den,))
            row = cur.fetchone()
            brute.append((row["id"] if row else None, den, cant, pret, cont_l, l["cota_tva"]))
        document = _et.factura(cur, schema, factura_id)   # [258] documentul mișcării: factura cum o vede omul, nu id-ul ei
    n = 0
    for aid, den, cant, pret, cont_l, cota in brute:
        intrare(conn, schema, {"articol_id": aid, "denumire": den, "cantitate": str(cant), "cota_tva": cota,
                               "pret_unitar": str(pret), "cont_stoc": cont_l,
                               "cont_cheltuiala": cont_cheltuiala, "data": str(data),
                               "document": document}, factura_id=factura_id)
        n += 1
    return {"stare": "intrat", "factura_id": factura_id, "linii": n}


def iesire(conn, schema, corp, factura_id=None):
    """corp: {articol_id, data, cantitate, document?, locatie?}. Valoare la CMP + notă ciornă
    cont_cheltuiala = cont_stoc.
    factura_id: leagă mișcarea de o factură (puntea factură->stoc, F172); NULL la ieșirea manuală.

    [E2b, 15.09.2026] Parametrul `commit` a fost scos. El exista ca să poată spune apelantul „nu
    comite acum, sunt în tranzacția mea" — adică exact ce e acum REGULA: tranzacția e a stratului,
    iar depozitul nu comite niciodată. Cu `commit`-urile scoase, parametrul n-ar mai fi comandat
    nimic, iar un parametru care nu face nimic e o urmă de intenție, nu o decizie."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # [06.10.2026, comanda Costin §6.3] ieșirea pe articol e a firmei CANTITATIV-VALORICE (o singură descărcare pe ieșire)
        from core import metoda_stoc as _ms
        _ms.cere(cur, schema, _ms.CV, "Ieșirea pe articol, la CMP")
        cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (corp["articol_id"],))
        a = cur.fetchone()
        if not a:
            return None
        # [decizii 07.10 pct.3] ieșirea care descarcă un raport Z se leagă de el (Z-ul nu se validează fără descărcare)
        from core import z_descarcare as _zd
        z_id = _zd.cere_z(cur, schema, corp["z_id"]) if corp.get("z_id") not in (None, "") else None
        try:
            r = _m.valoare_iesire(_miscari(cur, schema, a["id"]), None, corp["cantitate"])
        except ValueError as e:
            return {"eroare": str(e)}
        # [05.10.2026, comanda Costin pct.6] nota automată poartă documentul sursă (Registrul-jurnal, col.3). Fără
        # `factura_id`: 607=371 nu e nici contarea facturii, nici o plată — legată, ar bloca ștergerea facturii.
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                        VALUES (%s,%s,'stocuri','ciorna',%s) RETURNING id""",
                    (corp["data"], f"Ieșire stoc {a['denumire']} × {_pu.cantitate(corp['cantitate'], a['um'])}"[:200],
                     (str(corp.get("document") or "").strip() or None)))
        iid = cur.fetchone()["id"]
        if not (str(corp.get("document") or "").strip()):
            # [06.10.2026 §6.2] ieșirea fără document scris de om: bonul de consum, generat odată cu nota
            from core import documente_interne as _di
            _di.genereaza(cur, schema, "bon_consum", corp["data"], [iid])
        cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                        (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                    (iid, a["cont_cheltuiala"], a["cont_stoc"], r["valoare"]))
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                        (articol_id, data, tip, cantitate, valoare, document, inregistrare_id, locatie, factura_id, z_inregistrare_id)
                        VALUES (%s,%s,'iesire',%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (a["id"], corp["data"], Decimal(str(corp["cantitate"])), r["valoare"],
                     corp.get("document"), iid, corp.get("locatie") or None, factura_id, z_id))
        mid = cur.fetchone()["id"]
        if z_id:
            _zd.deblocat(z_id)   # [368] Z-ul descărcat: la PFA nota lui se reîncearcă la validarea internă
    return {"id": mid, "cmp": str(r["cmp"]), "valoare": str(r["valoare"]),
            "nota": f"{a['cont_cheltuiala']}={a['cont_stoc']}", "inregistrare_id": iid}


def descarca_factura(conn, schema, factura_id, data):
    """Puntea factura->stoc (F172): descarca gestiunea pentru liniile facturii cu articol_id, in
    tranzactia emiterii (NU commit aici - atomicitate). Refoloseste iesire() existent (nu motor
    paralel), leaga fiecare miscare de factura prin factura_id. Liniile fara articol (servicii) se
    ignora. O linie cu stoc insuficient NU rupe factura - se raporteaza in `erori` (patru-ochi:
    notele raman ciorna). Intoarce {descarcate, erori}."""
    from core import jurnal_api as _j
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # [05.10.2026] o factură se descarcă o singură dată: dacă are deja ieșiri de stoc, a doua chemare nu mai scrie nimic
        cur.execute(f"""SELECT 1 FROM {schema}.miscari_stoc m WHERE m.factura_id = %s AND m.tip = 'iesire' AND m.anuleaza_id IS NULL
                        AND NOT EXISTS (SELECT 1 FROM {schema}.miscari_stoc r WHERE r.anuleaza_id = m.id) LIMIT 1""", (factura_id,))
        if cur.fetchone():
            return {"descarcate": [], "erori": [], "deja_descarcata": True}
        cur.execute(f"""SELECT id, descriere, cantitate, articol_id FROM {schema}.factura_linii
                        WHERE factura_id=%s AND articol_id IS NOT NULL ORDER BY id""", (factura_id,))
        linii = cur.fetchall()
        cur.execute(f"SELECT tip, serie, numar, data_emitere FROM {schema}.facturi WHERE id=%s", (factura_id,))
        f = cur.fetchone() or {}
    document = (_j.eticheta_factura(f.get("tip"), f.get("serie"), f["numar"], f.get("data_emitere") or data)
                if f.get("numar") else "factura care nu mai există")   # [258] niciodată id-ul intern
    descarcate, erori = [], []
    for l in linii:
        rez = iesire(conn, schema,
                     {"articol_id": l["articol_id"], "data": data, "cantitate": l["cantitate"],
                      "document": document},
                     factura_id=factura_id)
        if rez is None:
            erori.append({"articol_id": l["articol_id"], "descriere": l["descriere"], "eroare": "articol inexistent"})
        elif rez.get("eroare"):
            erori.append({"articol_id": l["articol_id"], "descriere": l["descriere"], "eroare": rez["eroare"]})
        else:
            descarcate.append({"articol_id": l["articol_id"], "descriere": l["descriere"], "valoare": rez["valoare"]})
    return {"descarcate": descarcate, "erori": erori}


def iesiri_facturii(cur, schema, factura_id):
    """[deficiența 419] Ieșirile de stoc VII ale facturii (nici stornări, nici stornate deja), cu articolul: ce a plecat din magazie cu ea.
    `schema` None = schema conexiunii (apelanții din `facturi_api` lucrează pe `search_path`)."""
    from core import stocuri_anulare as _sa
    if schema is None:
        cur.execute("SELECT current_schema() AS s")
        schema = cur.fetchone()["s"]
    cur.execute(("SELECT m.*, a.denumire, a.um, a.cont_stoc, a.cont_cheltuiala FROM {s}.miscari_stoc m JOIN {s}.articole a ON a.id = m.articol_id "
                 "WHERE m.factura_id = %s AND m.tip = 'iesire' AND " + _sa._VII + " ORDER BY m.id").format(s=schema), (factura_id,))
    return [dict(r) for r in cur.fetchall()]


def retur_la_stornare(conn, schema, factura_id, storno_id, data, document):
    """[deficiența 419, comanda Costin 9.3, PRIORITAR] „Stornarea integrală F1A9 nu a readus marfa în stoc [...] Aplicația nici nu întreabă
    dacă marfa se întoarce fizic (retur) sau rămâne la client.” La retur: fiecare ieșire a facturii stornate se stornează în ROȘU (cantitatea
    și valoarea cu minus, `anuleaza_id` = ieșirea, valoarea exact a ieșirii — nu CMP-ul de acum), cu documentul de corecție: o notă NOUĂ în
    ciornă „cont cheltuială = cont stoc” cu minus (regula de fond R5; OMFP 1802/2014 pct.69: „corectarea cu semnul minus a operațiunii
    inițiale”), legată de factura de stornare prin document. Data = data stornării. Întoarce [{articol, cantitate, valoare, inregistrare_id}]."""
    out = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if schema is None:
            cur.execute("SELECT current_schema() AS s")
            schema = cur.fetchone()["s"]
        for m in iesiri_facturii(cur, schema, factura_id):
            cant, val = Decimal(str(m["cantitate"])), Decimal(str(m["valoare"]))
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                            VALUES (%s,%s,'stocuri','ciorna',%s) RETURNING id""",
                        (data, ("Retur în stoc %s × %s (stornare)" % (m["denumire"], _pu.cantitate(cant, m["um"])))[:200], document))
            iid = cur.fetchone()["id"]
            cur.execute(f"INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                        (iid, m["cont_cheltuiala"], m["cont_stoc"], -val))
            cur.execute(f"""INSERT INTO {schema}.miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document,
                                inregistrare_id, locatie, factura_id, anuleaza_id)
                            VALUES (%s,%s,'iesire',%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (m["articol_id"], data, -cant, m.get("pret_unitar"), -val, document[:100], iid, m.get("locatie"), storno_id, m["id"]))
            out.append({"articol": m["denumire"], "cantitate": str(cant), "um": m["um"], "valoare": str(val), "inregistrare_id": iid})
    return out


def inventar(conn, schema, corp):
    """corp: {data, linii: [{articol_id, faptic}]}. Diferente la CMP:
    plus -> intrare + nota 371=607 (ciorna); minus -> iesire + nota 607=371 (ciorna).
    Temei: OMFP 1802/2014, functiunea conturilor 371/607."""
    # [lotul 6, 04.09.2026] Un inventar FARA linii intorcea `{"rezultate": []}` — adica „am
    # inventariat si n-am gasit nimic de corectat", cand de fapt nu se numarase nimic. Inventarierea
    # e un act: absenta lui nu se raporteaza ca rezultatul lui.
    if not (corp.get("linii") or []):
        raise ValueError("Inventarul n-are niciun articol numărat. Un inventar fără linii nu e o "
                         "inventariere fără diferențe — e o inventariere care nu s-a făcut.")
    rez = []
    note_inventar = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT COALESCE(platitor_tva, false) AS p, regim_fiscal FROM {schema}.firma_profil WHERE id = 1")
        _pr = cur.fetchone()
        platitor = bool(_pr and _pr["p"])
        # [deficiența 404] microîntreprinderea nu plătește impozit pe profit (CF titlul III): lipsa neimputabilă nu are unde ajusta
        micro = bool(_pr and str(_pr["regim_fiscal"] or "").lower() == "micro")
        for l in corp.get("linii", []):
            fv = l.get("faptic")
            if fv is None or (isinstance(fv, str) and fv.strip() == ""):
                continue   # [cap.24] articol necontorizat (faptic gol) - nu se inregistreaza, NU e eroare
            cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (l["articol_id"],))
            a = cur.fetchone()
            if not a:
                rez.append({"articol_id": l["articol_id"], "camp": "cvi-a%s-faptic" % l["articol_id"], "eroare": "articol inexistent"})
                continue
            fisa = _m.fisa_magazie(_miscari(cur, schema, a["id"]))
            scriptic = fisa[-1]["sold_cantitate"] if fisa else Decimal("0")
            cmp = Decimal(str(fisa[-1]["cmp"])) if fisa and fisa[-1]["cmp"] else Decimal("0")
            try:
                faptic = Decimal(str(fv))
            except (InvalidOperation, ValueError):
                rez.append({"articol_id": a["id"], "denumire": a["denumire"], "camp": "cvi-a%s-faptic" % a["id"], "eroare": "valoare invalidă (număr)"})
                continue
            dif = faptic - scriptic
            if dif == 0:
                rez.append({"articol_id": a["id"], "denumire": a["denumire"], "diferenta": "0"})
                continue
            val = (abs(dif) * cmp).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if dif > 0:
                debit, credit, tip = a["cont_stoc"], a["cont_cheltuiala"], "intrare"
            else:
                if abs(dif) > scriptic:
                    rez.append({"articol_id": a["id"], "denumire": a["denumire"], "camp": "cvi-a%s-faptic" % a["id"], "eroare": "minus peste stocul scriptic"})
                    continue
                debit, credit, tip = a["cont_cheltuiala"], a["cont_stoc"], "iesire"
                # [deficiența 404] lipsa se încadrează de om: imputabilă / neimputabilă / justificată (art.304 alin.(2))
                _lipsa = _incadreaza_lipsa(cur, schema, a, l, val, platitor)
                if _lipsa.get("eroare"):
                    rez.append({"articol_id": a["id"], "denumire": a["denumire"], **_lipsa})
                    continue
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'stocuri','ciorna') RETURNING id""",
                        (corp["data"], f"Inventar {a['denumire']}: {'plus' if dif > 0 else 'minus'} {_pu.cantitate(abs(dif), a['um'])}"[:200]))
            iid = cur.fetchone()["id"]
            note_inventar.append(iid)
            linii_nota = [(debit, credit, val)] + (_lipsa["linii"] if dif < 0 else [])
            for _d_, _c_, _s_ in linii_nota:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                            (iid, _d_, _c_, _s_))
            cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                            (articol_id, data, tip, cantitate, pret_unitar, valoare, document, inregistrare_id)
                            VALUES (%s,%s,%s,%s,%s,%s,'inventar',%s)""",
                        (a["id"], corp["data"], tip, abs(dif),
                         cmp if tip == "intrare" else None, val, iid))
            ajustare = None
            if dif < 0 and _lipsa.get("nedeductibil"):
                # [deficiența 404, decizia Costin 19.10.2026 „Da, automat”] cheltuiala + TVA-ul ajustat trec singure la ajustările fiscale
                # ale impozitului pe profit (rd.33 D101, CF art.25 alin.(4) lit.c), în aceeași tranzacție cu nota și legate de ea
                ajustare = _lipsa_la_ajustari(cur, schema, corp["data"], a["denumire"], _lipsa, iid, micro)
            rand = {"articol_id": a["id"], "denumire": a["denumire"], "diferenta": str(dif), "valoare": str(val),
                    "nota": " + ".join("%s=%s" % (x[0], x[1]) for x in linii_nota), "inregistrare_id": iid,
                    **({"ajustare_fiscala": ajustare} if ajustare else {})}
            if dif < 0:
                # [404] ce înseamnă încadrarea lipsei pentru impozitul pe profit: afirmație tipată despre articolul inventariat
                from core import afirmatii as _af
                rand["lipsa"] = _lipsa["lipsa"]
                rand["semnal"] = _af.afirmatie(
                    "fapt", "lipsa_inventar", _lipsa["text"], unde="inventarul din %s, articolul %s" % (_pu.data_ro(corp["data"]), a["denumire"]),
                    temei_completitudine="încadrarea lipsei aleasă de contabil pe rândul inventarului") if _lipsa["text"] else None
            rez.append(rand)
        if note_inventar:
            # [06.10.2026 §6.2] UN inventar = O listă de inventariere, pe toate notele diferențelor lui
            from core import documente_interne as _di
            _di.genereaza(cur, schema, "lista_inventariere", corp["data"], note_inventar)
    return {"rezultate": rez}


#: [deficiența 404] încadrarea lipsei la inventar — alegerea omului
LIPSE = {"imputabila": "imputabilă (persoana răspunzătoare o plătește)", "neimputabila": "neimputabilă",
         "justificata": "justificată: bunuri distruse, pierdute sau furate, dovedit (CF art.304 alin.(2) lit.a)"}


def _incadreaza_lipsa(cur, schema, a, l, val, platitor):
    """[deficiența 404, retestul Costin 19.10.2026] „Inventar (lipsă 607=371 205,90): nu întreabă imputabil/neimputabil (TVA 635=4427 +
    nedeductibil).” Rândurile notei, după încadrare, sau {"eroare", "camp"}.
    Temei:
      - HG 1/2016 titlul VII pct.78 alin.(6) lit.a: „[...] trebuie să efectueze o ajustare negativă a taxei deductibile în situații precum: a) bunuri lipsă
        în gestiune din alte cauze decât cele prevăzute la art. 304 alin. (2) din Codul fiscal. În cazul bunurilor lipsă din gestiune care
        sunt imputate, sumele imputate nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA”;
      - CF art.304 alin.(2) lit.a: nu se ajustează la „bunurile distruse, pierdute sau furate, în condițiile în care aceste situații sunt
        demonstrate sau confirmate în mod corespunzător”;
      - CF art.25 alin.(4) lit.c: nedeductibile „cheltuielile privind bunurile de natura stocurilor [...] constatate lipsă din gestiune
        ori degradate, neimputabile, precum și taxa pe valoarea adăugată aferentă”.
    Ajustarea TVA: 635 = 4427 (TVA-ul dedus la achiziție, la cota articolului din nomenclator sau cea scrisă pe rând); imputarea: 4282 =
    7581 (suma imputată, fără TVA — HG 1/2016 de mai sus)."""
    lipsa = str(l.get("lipsa") or "")
    if lipsa not in LIPSE:
        return {"eroare": "Lipsa de %s lei: alege dacă e imputabilă, neimputabilă sau justificată (distrusă, pierdută, furată — dovedit)." % val,
                "camp": "cvi-a%s-lipsa" % a["id"]}
    linii, text, nedeductibil = [], None, None
    if lipsa != "justificata" and platitor:
        cota = l.get("cota_tva")
        if cota in (None, ""):   # cota articolului din nomenclatorul Produse (aceeași denumire, ca la emitere — 415)
            cur.execute(f"SELECT cota_tva FROM {schema}.produse WHERE lower(denumire) = lower(%s) LIMIT 1", (a["denumire"],))
            _p = cur.fetchone()
            cota = _p["cota_tva"] if _p else None
        if cota in (None, ""):
            return {"eroare": "Cota de TVA a articolului nu e în nomenclator: scrie cota cu care s-a dedus TVA-ul la cumpărare (ajustarea "
                              "TVA, HG 1/2016 titlul VII pct.78 alin.(6) lit.a).", "camp": "cvi-a%s-cota" % a["id"]}
        tva = (val * Decimal(str(cota)) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if tva:
            linii.append(("635", "4427", tva))
        if lipsa == "neimputabila":
            text = ("Lipsa neimputabilă: cheltuiala (%s lei) și TVA-ul ajustat (%s lei) sunt nedeductibile la impozitul pe profit (CF "
                    "art.25 alin.(4) lit.c)." % (val, tva))
            nedeductibil = (val, tva)
    elif lipsa == "neimputabila":
        text = "Lipsa neimputabilă: cheltuiala (%s lei) e nedeductibilă la impozitul pe profit (CF art.25 alin.(4) lit.c)." % val
        nedeductibil = (val, Decimal(0))
    if lipsa == "imputabila":
        try:
            imp = Decimal(str(l.get("suma_imputata")))
        except (InvalidOperation, ValueError, TypeError):
            imp = Decimal(0)
        if imp <= 0:
            return {"eroare": "Lipsa imputabilă: scrie suma imputată persoanei răspunzătoare.", "camp": "cvi-a%s-imputat" % a["id"]}
        linii.append(("4282", "7581", imp.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)))
    return {"lipsa": lipsa, "linii": linii, "text": text, "nedeductibil": nedeductibil}


def _lipsa_la_ajustari(cur, schema, data, articol, lipsa, inregistrare_id, micro):
    """[deficiența 404] Nedeductibilul lipsei neimputabile (cheltuiala, TVA-ul ajustat) scris la ajustările fiscale (`ajustari_fiscale.
    din_lipsa_neimputabila`), cu semnalul completat: unde a ajuns și când intră în calcul. La microîntreprindere nu se scrie (nu există
    impozit pe profit de ajustat) și semnalul o spune. Întoarce {id, suma, trim, rand} sau None."""
    from core import ajustari_fiscale as _aj
    if micro:
        lipsa["text"] += " Firma e microîntreprindere: nu plătește impozit pe profit, deci lipsa nu trece la ajustările fiscale."
        return None
    chelt, tva = lipsa["nedeductibil"]
    aid, suma, trim = _aj.din_lipsa_neimputabila(cur, schema, data, articol, chelt, tva, inregistrare_id,
                                                 document="Inventarul din %s" % _pu.data_ro(data))
    lipsa["text"] += (" Suma de %s lei a trecut la ajustările fiscale (Registrul de evidență fiscală, %s, T%d/%s); intră în D100 / D101 "
                        "după validarea notei inventarului." % (_pu.bani(suma), _aj.RANDURI[_aj.RAND_LIPSA_NEIMPUTABILA][0], trim,
                                                                str(data)[:4]))
    return {"id": aid, "suma": str(suma), "trim": trim, "rand": _aj.RAND_LIPSA_NEIMPUTABILA}


def analitica(conn, schema, zile_inert):   # pragul inertului vine din ruta (`main.cv_analitica`, implicit 90 de zile)
    """Analitica de stoc (F140). NU introduce valorizare per locatie (CMP global):
      - critic: articole cu nivel_minim setat si stoc <= nivel_minim
                (necesar aprovizionare = nivel_minim - stoc)
      - inert:  articole cu stoc > 0 fara nicio miscare de peste `zile_inert` zile
      - abc:    clasificare Pareto pe valoarea stocului (A <=80%, B <=95%, C restul)
      - consum: iesiri in ultimele 30 zile vs cele 30 anterioare (perioade comparabile)
    Data de referinta = CURRENT_DATE (Postgres)."""
    zi = int(zile_inert) if str(zile_inert).lstrip("-").isdigit() else 90
    critic, inert, abc, consum = [], [], [], []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, denumire, um, nivel_minim FROM {schema}.articole ORDER BY denumire")
        arts = cur.fetchall()
        cur.execute(f"""SELECT articol_id, MAX(data) AS ultima,
            COALESCE(SUM(CASE WHEN tip='iesire' AND data > CURRENT_DATE - 30
                              THEN cantitate ELSE 0 END),0) AS iesiri30,
            COALESCE(SUM(CASE WHEN tip='iesire' AND data <= CURRENT_DATE - 30
                              AND data > CURRENT_DATE - 60 THEN cantitate ELSE 0 END),0) AS iesiri30ant,
            (CURRENT_DATE - MAX(data)) AS zile_de_la
            FROM {schema}.miscari_stoc GROUP BY articol_id""")
        agg = {r["articol_id"]: r for r in cur.fetchall()}
        for a in arts:
            fisa = _m.fisa_magazie(_miscari(cur, schema, a["id"]))
            stoc = fisa[-1]["sold_cantitate"] if fisa else Decimal("0")
            val = _m._d(fisa[-1]["sold_valoare"]) if fisa else Decimal("0")
            g = agg.get(a["id"])
            nm = a["nivel_minim"]
            if nm is not None and stoc <= nm:
                critic.append({"articol_id": a["id"], "denumire": a["denumire"], "um": a["um"],
                               "stoc": str(stoc), "nivel_minim": str(nm),
                               "necesar": str(max(Decimal("0"), Decimal(str(nm)) - stoc))})
            if stoc > 0 and g and g["zile_de_la"] is not None and g["zile_de_la"] > zi:
                inert.append({"articol_id": a["id"], "denumire": a["denumire"], "um": a["um"],
                              "stoc": str(stoc), "ultima_miscare": str(g["ultima"]),
                              "zile": int(g["zile_de_la"])})
            if val > 0:
                abc.append({"articol_id": a["id"], "denumire": a["denumire"],
                            "valoare": val})
            if g and (g["iesiri30"] or g["iesiri30ant"]):
                consum.append({"articol_id": a["id"], "denumire": a["denumire"], "um": a["um"],
                               "iesiri_30z": str(g["iesiri30"]), "iesiri_30z_anterior": str(g["iesiri30ant"])})
    # ABC: Pareto pe valoare cumulata
    abc.sort(key=lambda x: x["valoare"], reverse=True)
    total = sum((x["valoare"] for x in abc), Decimal("0"))
    cumul = Decimal("0")
    abc_out = []
    for x in abc:
        # clasa = banda in care INTRA articolul (cumulativul INAINTE de el), ca primul
        # articol - oricat de dominant - sa fie mereu A; A pana la 80%, B pana la 95%, C restul.
        pond_inainte = (cumul / total * 100) if total > 0 else Decimal("0")
        clasa = "A" if pond_inainte < 80 else ("B" if pond_inainte < 95 else "C")
        cumul += x["valoare"]
        pond = (cumul / total * 100) if total > 0 else Decimal("0")
        abc_out.append({"articol_id": x["articol_id"], "denumire": x["denumire"],
                        "valoare": str(_m._q(x["valoare"])),
                        "pondere_cumulata": str(_m._q(pond)), "clasa": clasa})
    return {"critic": critic, "inert": inert, "abc": abc_out, "consum": consum,
            "zile_inert": zi}


def gaseste_barcode(conn, schema, barcode):
    """Articolul care poarta codul de bare dat, sau None. F141."""
    bc = (barcode or "").strip()
    if not bc:
        return None
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT id, denumire, um, cont_stoc, cont_cheltuiala, barcode
                        FROM {schema}.articole WHERE barcode=%s""", (bc,))
        a = cur.fetchone()
    return dict(a) if a else None


def set_barcode(conn, schema, articol_id, barcode):
    """Seteaza (sau sterge, daca gol) codul de bare al unui articol. Unic pe articole
    (index partial WHERE barcode IS NOT NULL). F141."""
    bc = (barcode or "").strip() or None
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id FROM {schema}.articole WHERE id=%s", (articol_id,))
        if not cur.fetchone():
            return None
        if bc is not None:
            cur.execute(f"SELECT id FROM {schema}.articole WHERE barcode=%s AND id<>%s",
                        (bc, articol_id))
            if cur.fetchone():
                return {"eroare": "codul de bare există deja la alt articol"}
        cur.execute(f"UPDATE {schema}.articole SET barcode=%s WHERE id=%s", (bc, articol_id))
    return {"articol_id": articol_id, "barcode": bc}


def set_nivel_minim(conn, schema, articol_id, nivel):
    """Seteaza (sau sterge, daca gol/negativ) nivelul minim de stoc al unui articol,
    prag pentru raportul de stoc critic si necesar de aprovizionare. F140."""
    nm = None
    if nivel is not None and str(nivel).strip() != "":
        try:
            nm = Decimal(str(nivel))
        except Exception:
            return {"eroare": "nivel minim invalid"}
        if nm < 0:
            return {"eroare": "nivel minim negativ"}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id FROM {schema}.articole WHERE id=%s", (articol_id,))
        if not cur.fetchone():
            return None
        cur.execute(f"UPDATE {schema}.articole SET nivel_minim=%s WHERE id=%s", (nm, articol_id))
    return {"articol_id": articol_id, "nivel_minim": str(nm) if nm is not None else None}


def _stoc_locatie(cur, schema, articol_id, locatie):
    """Cantitatea neta a unui articol la o locatie (intrari - iesiri). Pur cantitativ."""
    cur.execute(f"""SELECT COALESCE(SUM(CASE WHEN tip='intrare' THEN cantitate
                    WHEN tip='iesire' THEN -cantitate ELSE 0 END),0) AS q
                    FROM {schema}.miscari_stoc
                    WHERE articol_id=%s AND locatie IS NOT DISTINCT FROM %s""",
                (articol_id, locatie or None))
    return Decimal(str(cur.fetchone()["q"]))


def stoc_pe_locatii(conn, schema, articol_id=None):
    """Stocul CANTITATIV pe fiecare locatie (F138 Tier 1, eticheta descriptiva).
    CMP ramane GLOBAL — aici doar cantitati, nu valorizare per locatie (Tier 3 AMANAT)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q = f"""SELECT m.articol_id, a.denumire, a.um, m.locatie,
                   SUM(CASE WHEN m.tip='intrare' THEN m.cantitate
                            WHEN m.tip='iesire' THEN -m.cantitate ELSE 0 END) AS cantitate
                FROM {schema}.miscari_stoc m JOIN {schema}.articole a ON a.id=m.articol_id"""
        params = []
        if articol_id:
            q += " WHERE m.articol_id=%s"
            params.append(articol_id)
        q += """ GROUP BY m.articol_id, a.denumire, a.um, m.locatie
                 HAVING SUM(CASE WHEN m.tip='intrare' THEN m.cantitate
                                 WHEN m.tip='iesire' THEN -m.cantitate ELSE 0 END) <> 0
                 ORDER BY a.denumire, m.locatie NULLS FIRST"""
        cur.execute(q, params)
        return [{"articol_id": r["articol_id"], "denumire": r["denumire"], "um": r["um"],
                 "locatie": r["locatie"] or "(nespecificat)", "cantitate": str(r["cantitate"])}
                for r in cur.fetchall()]


def transfer(conn, schema, corp):
    """corp: {articol_id, din_locatie, in_locatie, cantitate, data, document?}.
    Transfer FIZIC intre locatii: iesire din sursa + intrare in destinatie, ambele la
    CMP-ul GLOBAL curent. NU genereaza nota contabila (nu e consum/achizitie) si e NEUTRU
    pe CMP si pe D406 (net zero cantitate+valoare). F138 Tier 1."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (corp["articol_id"],))
        a = cur.fetchone()
        if not a:
            return None
        din = (corp.get("din_locatie") or "").strip() or None
        catre = (corp.get("in_locatie") or "").strip() or None
        if din == catre:
            return {"eroare": "locația sursă și destinație sunt identice"}
        cant = Decimal(str(corp["cantitate"]))
        if cant <= 0:
            return {"eroare": "cantitate invalidă"}
        disp = _stoc_locatie(cur, schema, a["id"], din)
        if cant > disp:
            return {"eroare": f"transfer {cant} peste stocul {disp} la locația sursă"}
        try:
            r = _m.valoare_iesire(_miscari(cur, schema, a["id"]), None, cant)
        except ValueError as e:
            return {"eroare": str(e)}
        doc = (corp.get("document") or f"transfer {din or '-'}->{catre or '-'}")[:100]
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                        (articol_id, data, tip, cantitate, valoare, document, locatie)
                        VALUES (%s,%s,'iesire',%s,%s,%s,%s)""",
                    (a["id"], corp["data"], cant, r["valoare"], doc, din))
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                        (articol_id, data, tip, cantitate, pret_unitar, valoare, document, locatie)
                        VALUES (%s,%s,'intrare',%s,%s,%s,%s,%s)""",
                    (a["id"], corp["data"], cant, r["cmp"], r["valoare"], doc, catre))
    return {"articol_id": a["id"], "denumire": a["denumire"], "cantitate": str(cant),
            "cmp": str(r["cmp"]), "valoare": str(r["valoare"]),
            "din_locatie": din or "(nespecificat)", "in_locatie": catre or "(nespecificat)"}


def reclasificare(conn, schema, corp):
    """corp: {articol_id, cont_stoc_nou, cont_cheltuiala_nou?, data, document?}.
    Schimba tipul de produs (ex. materie prima 301 -> marfa 371): actualizeaza conturile
    articolului si emite nota de reclasificare a soldului la CMP curent
    (debit cont_stoc_nou = credit cont_stoc_vechi). Cantitatea NU se atinge.
    Temei: OMFP 1802/2014, functiunea conturilor de stoc. F138 (jumatatea usoara)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (corp["articol_id"],))
        a = cur.fetchone()
        if not a:
            return None
        cont_nou = (corp.get("cont_stoc_nou") or "").strip()
        if not cont_nou:
            return {"eroare": "Contul de stoc nou lipsește."}
        if cont_nou == a["cont_stoc"]:
            return {"eroare": "contul de stoc e neschimbat"}
        chelt_nou = (corp.get("cont_cheltuiala_nou") or "").strip() or a["cont_cheltuiala"]
        fisa = _m.fisa_magazie(_miscari(cur, schema, a["id"]))
        val = Decimal(str(fisa[-1]["sold_valoare"])) if fisa else Decimal("0")
        iid = None
        if val > 0:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'stocuri','ciorna') RETURNING id""",
                        (corp["data"],
                         f"Reclasificare {a['denumire']}: {a['cont_stoc']}->{cont_nou}"[:200]))
            iid = cur.fetchone()["id"]
            # [06.10.2026 §6.2] documentul scris de om, altfel nota de calcul a reclasificării
            from core import documente_interne as _di
            if str(corp.get("document") or "").strip():
                cur.execute(f"UPDATE {schema}.inregistrari SET document_ref=%s WHERE id=%s", (str(corp["document"]).strip(), iid))
            else:
                _di.genereaza(cur, schema, "nota_calcul", corp["data"], [iid])
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                        (iid, cont_nou, a["cont_stoc"], val))
        cur.execute(f"UPDATE {schema}.articole SET cont_stoc=%s, cont_cheltuiala=%s WHERE id=%s",
                    (cont_nou, chelt_nou, a["id"]))
    return {"articol_id": a["id"], "denumire": a["denumire"],
            "cont_stoc_vechi": a["cont_stoc"], "cont_stoc": cont_nou,
            "cont_cheltuiala": chelt_nou, "valoare_reclasificata": str(val),
            "nota": (f"{cont_nou}={a['cont_stoc']}" if val > 0 else None),
            "inregistrare_id": iid}
