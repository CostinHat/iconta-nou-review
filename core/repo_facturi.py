# -*- coding: utf-8 -*-
"""REPOSITORY — facturile din schema unui tenant.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""
from decimal import Decimal, ROUND_HALF_UP


def tip_document(cur, schema, factura_id):
    """[lotul 12, 252] `facturi.tip` al documentului (None dacă nu există), pe schema dată."""
    cur.execute(f"SELECT tip FROM {(schema + '.') if schema else ''}facturi WHERE id = %s", (factura_id,))
    r = cur.fetchone()
    return (r["tip"] if isinstance(r, dict) else r[0]) if r else None


def tip_si_transformare(cur, factura_id):
    cur.execute("SELECT tip, transformat_in_id FROM facturi WHERE id=%s",
                (factura_id,))
    return cur.fetchone()


def candidate_pentru_bon(cur, schema, cui, total):
    """`cui` în forma păstrată (`cui_forma.stocare`); factura comparată în aceeași formă (`cui_forma.SQL`) — rândurile vechi au „RO”.
    [lotul 11, decizia Costin 10.3 pct.4] Înainte: un `replace` SQL al lui „RO”, un al doilea dialect (scotea „RO” de oriunde din text).
    [lotul 12, 466, clasa „plătită = `platita_la`”] candidatele sunt facturile primite care MAI AU de plătit, după starea de plată unică
    (`de_incasat`): una plătită prin bancă nu se mai oferă bonului (o a doua plată). Rândul: (id, numar, serie, data_emitere, restul de
    plată în lei, tert_nume, tert_cui), cel mai potrivit întâi (același cod, apoi suma cea mai apropiată, apoi cea mai nouă)."""
    from core import cui_forma as _forma_cui, repo_contabilitate as _rc
    _rc.search_path_firma(cur, schema)
    total = Decimal(str(total or 0))
    fs = de_incasat(cur, "primita")
    fs.sort(key=lambda f: ((_forma_cui.stocare(f["tert_cui"]) or "") != cui, abs(f["rest_lei"] - total), -f["data_emitere"].toordinal()
                           if f["data_emitere"] else 0))
    return [(f["id"], f["numar"], f["serie"], f["data_emitere"], f["rest_lei"], f["tert_nume"], f["tert_cui"]) for f in fs[:10]]


def factura_pentru_chitanta(cur, schema, factura_id):
    cur.execute(f"SELECT serie, numar, tert_nume, tert_cui, total, directie, data_emitere FROM {schema}.facturi WHERE id=%s",
                (factura_id,))
    return cur.fetchone()


#: [deficiența 417] factura stornată (seria, numărul, data), adusă pe factura de stornare — același SQL în detaliu / PDF
#: (`facturi_api.detalii_factura`) și în loaderul e-Factura (`repo_efactura.factura_pentru_ubl`)
SQL_STORNO_DIN = ("(SELECT json_build_object('serie', o.serie, 'numar', o.numar, 'data_emitere', o.data_emitere) "
                  "FROM {s}facturi o WHERE o.id = {a}.storno_din_id) AS storno_din")

#: [deficiența 416] suma facturilor de stornare ale facturii `{a}`, în moneda ei (negativă: liniile negate) — o singură definiție pentru
#: starea de încasare, scadențar, notificările de scadență și cashflow (toleranța: `TOLERANTA_STORNATA`)
SQL_STORNARI = "COALESCE((SELECT SUM(st.total) FROM {s}facturi st WHERE st.storno_din_id = {a}.id), 0)"
#: [416] rămasul facturii = total + stornările ei (negative); sub toleranță = „stornată” integral (CF art.330 alin.(1) lit.b: factura cu
#: valorile cu semnul minus anulează valorile facturii corectate). Toleranța de rotunjire, nu un prag fiscal: jumătate de ban.
TOLERANTA_STORNATA = Decimal("0.005")


def seteaza_act_identitate(cur, schema, factura_id, act):
    """[402] actul de identitate al vânzătorului persoană fizică, pe borderoul de achiziție."""
    cur.execute(f"UPDATE {schema}.facturi SET tert_act_identitate = %s WHERE id = %s", (act, factura_id))


#: [lotul 12, 468] aceeași sumă a stornărilor, în LEI (`total_lei` al stornării; RON fără `total_lei` = totalul) — pentru cititorii care
#: adună facturi în monede diferite (cashflow-ul se alocă din soldul balanței, care e în lei)
SQL_STORNARI_LEI = "COALESCE((SELECT SUM(COALESCE(st.total_lei, st.total)) FROM {s}facturi st WHERE st.storno_din_id = {a}.id), 0)"


def pentru_cashflow(cur):
    # [deficiența 416] totalul de după stornări (`repo_facturi.SQL_STORNARI`); factura stornată integral nu mai intră
    # [lotul 12, 468, clasa „lei adunați cu euro”] totalul în LEI (`total_lei`): `cashflow.aloca_sold` îl împarte din soldul balanței (în
    # lei), iar o factură de 1.000 EUR intra ca 1.000 lei
    # [lotul 13, 546] totalul DE PLATĂ (`facturi.SQL_TOTAL_DE_PLATA_LEI`): factura primită cu taxare inversă e datorată fără TVA-ul ei
    from core import facturi as _fc
    st = SQL_STORNARI_LEI.format(s="", a="facturi")
    tp = _fc.SQL_TOTAL_DE_PLATA_LEI.format(a="facturi")
    cur.execute("SELECT directie, data_emitere, data_scadenta, " + tp + " + " + st + " AS total "
                "FROM facturi WHERE tip='factura' AND storno_din_id IS NULL AND " + tp + " + " + st + " > %s",
                (TOLERANTA_STORNATA,))
    return cur.fetchall()


#: [lotul 12, 466] stările de încasare ale unei facturi care mai are ceva de încasat / de plătit (`facturi_api._cu_stare_incasare`)
STARI_DE_INCASAT = ("neincasata", "partial")


def de_incasat(cur, directie, conditii="", parametri=()):
    """[lotul 12, deficiența 466 — „Scadențar: facturi încasate apar neîncasate”] Facturile `directie` (emisa / primita) care mai au ceva de
    încasat / de plătit, după definiția UNICĂ a stării de încasare (`facturi_api._cu_stare_incasare`: chitanțele, plățile legate de factură
    — banca, casa —, compensările, stornările, `platita_la`), cu restul lor. Înainte scadențarul, notificările de scadență și potrivirea
    bonului cu factura primită socoteau „neîncasată” orice factură fără `platita_la` — pe care o pune numai chitanța integrală sau bonul
    stins; factura încasată prin bancă rămânea „restantă” (iar notificarea pleca la client).

    `conditii` = condiții SQL în plus pe `f` (încep cu „ AND”), cu `parametri`. Fiecare rând: coloanele facturii (`f.*` cele de mai jos,
    `email` al clientului) + `stare_incasare` + `rest` (Decimal, în MONEDA facturii) + `rest_lei` (Decimal). Restul în valută = totalul
    în valută (după stornări) × restul în lei / totalul în lei: plata (în lei, din notele pe 4111 / 401) stinge creanța la valoarea ei din
    evidență — aceeași regulă ca reevaluarea (`reevaluare_valuta`, OMFP 1802/2014 pct.322 alin.(1)). Se întorc dict-uri, oricare ar fi
    cursorul apelantului."""
    from core import facturi_api as _fa
    from core import nomenclator_status_factura as _nsf
    st = SQL_STORNARI.format(s="", a="f")
    cur.execute("SELECT f.id, f.numar, f.serie, f.data_emitere, f.data_scadenta, f.total, f.tva, f.total_lei, f.tva_lei, f.curs_bnr, "
                "       f.directie, COALESCE(f.taxare_inversa, false) AS taxare_inversa, "   # [lotul 13, 546] totalul de plată (taxarea inversă)
                "       COALESCE(f.moneda, 'RON') AS moneda, f.tip, f.storno_din_id, f.platita_la, f.tert_nume, f.tert_cui, f.client_id, "
                "       c.email, COALESCE(f.notificare_stop, false) AS notificare_stop, f.notificare_amanata_pana, "
                "       " + st + " AS storno_valuta "
                "  FROM facturi f LEFT JOIN clienti c ON c.id = f.client_id "
                # [lotul 12, 252] și facturile deschise preluate (`TIPURI_CU_INCASARE`): restul lor e de încasat / de plătit ca al oricărei facturi
                " WHERE f.directie = %s AND " + _nsf.clauza_tip_cu_incasare("f") + " AND f.storno_din_id IS NULL "
                "   AND COALESCE(f.status, '') NOT IN ('anulata', 'storno')" + conditii + " ORDER BY f.id",
                (directie,) + tuple(parametri))
    cols = [d[0] for d in cur.description]
    facturi = [dict(r) if isinstance(r, dict) else dict(zip(cols, r)) for r in cur.fetchall()]
    _fa._cu_stare_incasare(cur, facturi)
    out = []
    for f in facturi:
        s = f["stare_incasare"]
        if not s or s["stare"] not in STARI_DE_INCASAT:
            continue
        total_lei, rest_lei = Decimal(s["total"]), Decimal(s["total"]) - Decimal(s["incasat"])
        # [lotul 13, 546] în valută, tot totalul de plată: la factura primită cu taxare inversă, fără TVA-ul beneficiarului (CF art.331 alin.(3))
        from core import facturi as _fc
        valuta = _fc.total_de_plata(f, f["total"], f["tva"]) + Decimal(str(f["storno_valuta"] or 0))
        if s["stare"] == "neincasata" or total_lei <= 0:
            rest = valuta
        else:
            rest = (valuta * rest_lei / total_lei).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if rest <= TOLERANTA_STORNATA:
            continue
        out.append(dict(f, rest=rest, rest_lei=rest_lei, total_valuta=valuta))
    return out


def cursul_fixat(cur, schema, factura_id):
    """[lotul 12, decizia „cursul vechi la validare (a)”] {moneda, data_emitere, curs_bnr, data_curs} ale facturii, sau None."""
    cur.execute(f"SELECT moneda, data_emitere, curs_bnr, data_curs FROM {(schema + '.') if schema else ''}facturi WHERE id = %s",
                (factura_id,))
    r = cur.fetchone()
    if not r:
        return None
    return dict(r) if isinstance(r, dict) else dict(zip(("moneda", "data_emitere", "curs_bnr", "data_curs"), r))


def stare_pentru_recunoastere(cur, schema, factura_id):
    cur.execute(f"SELECT status, directie, (xml IS NOT NULL) FROM {schema}.facturi "
                        f"WHERE id=%s FOR UPDATE",
                (factura_id,))
    return cur.fetchone()


def emise_pe_luni_pentru_intrastat(cur, schema, an):
    # [lotul 12, 252 / C145] numai documentele fiscale: factura preluată (soldul ei e în soldurile inițiale) și proforma / avizul nu sunt
    # livrări facturate ale anului (avizul e urmat de factură — s-ar număra de două ori)
    from core import nomenclator_status_factura as _nsf
    cur.execute(f"""SELECT directie, tert_cui,
                                   EXTRACT(MONTH FROM data_emitere)::int AS luna,
                                   COALESCE(total,0) - COALESCE(tva,0) AS baza
                            FROM {schema}.facturi
                            WHERE EXTRACT(YEAR FROM data_emitere) = %s AND {_nsf.clauza_tip_document(None)}""",   # [lotul 12, C145] numai facturile
                (an,))
    return cur.fetchall()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def jurnalizeaza_cota_aleasa(cur, factura_id, linii, user_id):
    """[comanda Costin 05.10.2026 pct.3] „contabilul poate corecta cota; schimbarea rămâne consemnată (propus → ales, cine, când)”.
    Un rând pentru fiecare linie emisă cu altă cotă decât cea PROPUSĂ automat; o linie fără propunere sau cu propunerea păstrată nu
    scrie nimic. Fără utilizator nu se scrie (jurnalul fără autor nu consemnează nimic). Întoarce câte rânduri a scris."""
    from decimal import Decimal
    if user_id is None:
        raise ValueError("cota aleasă se consemnează cu utilizatorul care a ales-o — lipsește")
    scrise = 0
    for nr, l in enumerate(linii, 1):
        p, a = l.get("cota_propusa"), l.get("cota_tva")
        if p is None or a is None or Decimal(str(p)) == Decimal(str(a)):
            continue
        cur.execute("INSERT INTO factura_cota_jurnal (factura_id, linie_nr, descriere, cota_propusa, cota_aleasa, user_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s)", (factura_id, nr, l.get("descriere"), p, a, user_id))
        scrise += 1
    return scrise


def leaga_proforma_de_factura(cur, transformat_in_id, id_):
    cur.execute("UPDATE facturi SET transformat_in_id=%s WHERE id=%s",
                (transformat_in_id, id_))


def marcheaza_primita_platita(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.facturi SET platita_la=now() WHERE id=%s AND directie='primita'",
                (id_,))


def marcheaza_platita(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.facturi SET platita_la=now() WHERE id=%s",
                (id_,))


def marcheaza_emisa(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.facturi SET status='emisa' WHERE id=%s",
                (id_,))


def actualizeaza_clasificarea(cur, schema, bucati_set, valori):
    """Scrie clasificarea aleasă la validare, pe coloanele pe care apelantul le-a ales.

    `bucati_set` sunt bucățile `coloana=%s` compuse de apelant, iar `valori` le urmează în ordine,
    cu `id`-ul la coadă. Repository-ul nu alege coloanele și nu decide dacă operația are loc — asta
    rămâne la apelant; el doar persistă.
    """
    cur.execute(f"UPDATE {schema}.facturi SET " + ", ".join(bucati_set) + " WHERE id=%s",
                valori)


def actualizeaza_conturi_linii(cur, schema, fid, conturi):
    """[deficiența 418b] Contul fiecărei linii a facturii PRIMITE, în ordinea liniilor (ca `actualizeaza_destinatii_linii`):
    conturi[i] <-> linia i; gol = contul facturii."""
    if not conturi:
        return
    cur.execute(f"SELECT id FROM {schema}.factura_linii WHERE factura_id=%s ORDER BY id", (fid,))
    for lid, cont in zip([r[0] for r in cur.fetchall()], conturi):
        cur.execute(f"UPDATE {schema}.factura_linii SET cont_cheltuiala=%s WHERE id=%s", ((str(cont or "").strip() or None), lid))


def actualizeaza_centre_linii(cur, schema, fid, centre):
    """[lotul 13, 536] Centrul de cost al fiecărei linii a facturii PRIMITE, în ordinea liniilor (ca `actualizeaza_conturi_linii`):
    centre[i] <-> linia i; None = fără centru. Valorile vin verificate (`centre_cost_api.campuri_centru_gresit`)."""
    cur.execute(f"SELECT id FROM {schema}.factura_linii WHERE factura_id=%s ORDER BY id", (fid,))
    for lid, centru in zip([r[0] for r in cur.fetchall()], centre or []):
        cur.execute(f"UPDATE {schema}.factura_linii SET centru_cost_id=%s WHERE id=%s", (centru, lid))


def actualizeaza_destinatii_linii(cur, schema, fid, destinatii):
    """[A12b] Aplica destinatia TVA (taxabil/scutit/mixt) per linie de factura, in ORDINEA
    liniilor (ORDER BY id) — aceeasi ordine in care `_factura_din_parsat` insereaza `f["linii"]`
    din XML. UPDATE, nu INSERT: functioneaza si cand factura era deja creata prin dedup (liniile
    exista deja), nu doar la prima validare. destinatii[i] <-> linia i.

    De ce coloana ramane taxabil implicit: art.300 alin.5 (pro-rata) se aplica DOAR achizitiilor cu
    destinatie mixta; achizitia pur taxabila se deduce integral. Contabilul CLASIFICA un fapt
    importat, nu-l editeaza — vezi DESIGN_SYSTEM cap.28 (clasificare per-linie pe ecran de validare).
    """
    from core.migrare_destinatie_tva import DESTINATII
    if not destinatii:
        return
    cur.execute(f"SELECT id FROM {schema}.factura_linii WHERE factura_id=%s ORDER BY id",
                (fid,))
    ids = [r[0] for r in cur.fetchall()]
    for lid, dest in zip(ids, destinatii):
        d = (dest or "taxabil").strip()
        if d not in DESTINATII:
            raise ValueError("destinație TVA invalidă: %r (permise: %s)"
                             % (d, ", ".join(DESTINATII)))
        cur.execute(f"UPDATE {schema}.factura_linii SET destinatie_tva=%s WHERE id=%s",
                    (d, lid))


# ── [lotul 12, C73.1] DUBLURA FACTURII DE FURNIZOR: aceeași factură (furnizor + număr) o singură dată în evidență ──────────────────────
# Cheia și refuzul: `core/factura_primita_dublura.py`. Aici, citirea — chemată de cele trei căi prin care se naște o factură.
_COLOANE_DUBLURA = "id, serie, numar, data_emitere, total, moneda, tert_nume, tert_cui, tip"


def primite_cu_aceeasi_cheie(cur, schema, tert_cui, tert_nume, serie, numar, negativ=False, xml=None):
    """Facturile de furnizor deja în evidență cu aceeași cheie (furnizor + număr, `factura_primita_dublura`) și același semn (stornarea,
    cu minus, nu se ciocnește de factura pozitivă): [dict cu `_COLOANE_DUBLURA` + `acelasi_xml` (rândul poartă exact XML-ul `xml` — același
    document e-Factura)], cele mai vechi întâi; [] fără număr sau fără furnizor. Factura preluată la migrare (`tip = 'preluata'`) intră:
    soldul ei e în soldurile inițiale, deci aceeași factură introdusă din nou ar dubla datoria.
    Ia întâi lacătul tranzacției pe cheie (`pg_advisory_xact_lock`): o a doua salvare simultană a aceleiași facturi așteaptă commitul
    primei și o vede, în loc să treacă și ea (verificarea și scrierea nu sunt atomice altfel). `schema` None = schema curentă."""
    from core import factura_primita_dublura as _fd
    nr = _fd.numar(serie, numar)
    este_cui, cheie = _fd.furnizor(tert_cui, tert_nume)
    if not nr or not cheie:
        return []
    s = (schema + ".") if schema else ""
    pc, pn, nn = _fd.expresii_facturi()
    partener = f"{pc} = %s" if este_cui else f"{pc} = '' AND {pn} = %s"
    # cheia lacătului poartă schema firmei (dată sau cea curentă), aceeași pe toate căile, ca două căi diferite să se aștepte una pe alta
    cur.execute("SELECT pg_advisory_xact_lock(hashtext(COALESCE(%s, current_schema()) || %s))",
                ((schema or "").strip('"') or None, "|factura_primita|%s|%s" % (cheie, nr)))
    cur.execute(f"""SELECT {_COLOANE_DUBLURA}, (COALESCE(xml, '') <> '' AND xml = %s) AS acelasi_xml FROM {s}facturi
                WHERE directie = 'primita' AND COALESCE(tip, 'factura') IN %s AND COALESCE(status, '') <> 'anulata'
                  AND {nn} = %s AND {partener} AND (COALESCE(total, 0) < 0) = %s ORDER BY data_emitere, id""",
                (xml or "", _fd.TIPURI, nr, cheie, bool(negativ)))
    cols = [c.strip() for c in _COLOANE_DUBLURA.split(",")] + ["acelasi_xml"]
    return [dict(r) if isinstance(r, dict) else dict(zip(cols, r)) for r in cur.fetchall()]


def dubluri_primite(cur, schema):
    """Dublurile DEJA în evidență (scrise înainte de C73.1): grupurile de facturi de furnizor cu aceeași cheie și același semn, fiecare
    [dict cu `_COLOANE_DUBLURA`] (cel puțin două), în ordinea datei. Numai citire — ce se păstrează decide contabilul."""
    from core import factura_primita_dublura as _fd
    s = (schema + ".") if schema else ""
    pc, pn, nn = _fd.expresii_facturi()
    cheie_p = f"CASE WHEN {pc} <> '' THEN 'c:' || {pc} ELSE 'n:' || {pn} END"
    cur.execute(f"""SELECT {_COLOANE_DUBLURA}, grup FROM (
                  SELECT {_COLOANE_DUBLURA}, {cheie_p} || '|' || {nn} || '|' || (COALESCE(total, 0) < 0)::text AS grup,
                         count(*) OVER (PARTITION BY {cheie_p}, {nn}, COALESCE(total, 0) < 0) AS n
                  FROM {s}facturi WHERE directie = 'primita' AND COALESCE(tip, 'factura') IN %s AND COALESCE(status, '') <> 'anulata'
                    AND {nn} <> '' AND {cheie_p} NOT IN ('c:', 'n:')) x
                WHERE n > 1 ORDER BY grup, data_emitere, id""", (_fd.TIPURI,))
    cols = [c.strip() for c in _COLOANE_DUBLURA.split(",")] + ["grup"]
    grupuri = {}
    for r in cur.fetchall():
        d = dict(r) if isinstance(r, dict) else dict(zip(cols, r))
        grupuri.setdefault(d.pop("grup"), []).append(d)
    return list(grupuri.values())
