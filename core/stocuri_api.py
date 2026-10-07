# -*- coding: utf-8 -*-
"""Stocuri global-valorică — strat API. Motorul: core/stocuri.py.

AI propune (note ciorne), contabilul validează în jurnal."""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from core import afirmatii as _af  # [P8] absenta vanzarilor e un fapt
import json
from decimal import Decimal, ROUND_HALF_UP
from psycopg2.extras import RealDictCursor
from core import stocuri as _m


def _noteaza(cur, schema, data, descriere, note, document_ref=None, numar=None):
    """Creează câte o înregistrare ciornă per notă propusă. Întoarce id-urile. `document_ref` = documentul sursă (NIR);
    `numar` = cheia actului (descărcarea lunii: `DESC-GV-AAAA-LL`), după care a doua rulare se recunoaște."""
    ids = []
    for n in note:
        if Decimal(str(n["suma"])) <= 0:
            continue
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status, document_ref)
                        VALUES (%s,%s,%s,'stocuri','ciorna',%s) RETURNING id""",
                    (data, numar, descriere[:200], document_ref))
        iid = cur.fetchone()["id"]
        cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                        (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                    (iid, n["debit"], n["credit"], Decimal(str(n["suma"]))))
        ids.append(iid)
    return ids


def _nir_campuri_lipsa(linii, metoda=None):
    """Articole NIR incomplete -> [{camp, eticheta}]. Obligatorii: denumire nevida + cantitate>0 +
    pret_achizitie>0 (aceleasi criterii pe care frontendul le filtra tacit inainte). id camp = nir-l{i}-{camp}.
    [lotul 07.10 B, C11a] La firma cu stocul la preț de vânzare (global-valoric) și prețul de raft e obligatoriu: golul NU e 0
    (clasa „preț pe care nu l-a ales nimeni”) — refuz lângă câmp. La cost (cantitativ-valoric) prețul de raft nu se cere."""
    from core import metoda_stoc as _ms
    lipsa = []
    for i, l in enumerate(linii):
        n = i + 1
        if not str(l.get("denumire") or "").strip() and not l.get("articol_id"):
            lipsa.append({"camp": "nir-l%d-denumire" % i, "eticheta": "Articolul %d: denumirea" % n})
        cerute = [("cantitate", "cantitatea"), ("pret_achizitie", "prețul de achiziție")]
        if metoda == _ms.GV:
            cerute.append(("pret_vanzare", "prețul de raft (cu TVA)"))
        for camp, et in cerute:
            try:
                ok = float(l.get(camp) or 0) > 0
            except (TypeError, ValueError):
                ok = False
            if not ok:
                lipsa.append({"camp": "nir-l%d-%s" % (i, camp), "eticheta": "Articolul %d: %s" % (n, et)})
    return lipsa


def _norm_denumire(x):
    """„Marfa  A” și „marfa a” sunt același articol pentru om: spațiile multiple și majusculele nu fac alt articol."""
    return " ".join(str(x or "").split()).casefold()


def _articole_nir(cur, schema, linii):
    """[lotul 07.10 B, C11c] La cantitativ-valoric fiecare linie de NIR e un ARTICOL: ales din listă (`articol_id`) sau creat
    EXPLICIT (`articol_nou`), niciodată tacit. Un articol nou cu denumirea unuia existent (după `_norm_denumire`) se refuză lângă
    câmp, cu numele celui existent. Întoarce ([articol_id sau None pentru cel de creat], [erori de câmp])."""
    cur.execute(f"SELECT id, denumire FROM {schema}.articole")
    existente = {}
    for r in cur.fetchall():
        existente.setdefault(_norm_denumire(r["denumire"]), (r["id"], r["denumire"]))
    ids, erori = [], []
    for i, l in enumerate(linii):
        if l.get("articol_id"):
            cur.execute(f"SELECT 1 FROM {schema}.articole WHERE id = %s", (l["articol_id"],))
            if not cur.fetchone():
                erori.append({"camp": "nir-l%d-articol" % i, "mesaj": "Articolul ales nu mai există în listă."})
            ids.append(int(l["articol_id"]))
        elif l.get("articol_nou"):
            dubla = existente.get(_norm_denumire(l.get("denumire")))
            if dubla:
                erori.append({"camp": "nir-l%d-denumire" % i, "mesaj": "Articolul «%s» există deja în listă: alege-l de acolo — NIR-ul "
                              "nu creează un al doilea articol cu același nume." % dubla[1]})
            ids.append(None)
        else:
            erori.append({"camp": "nir-l%d-articol" % i, "mesaj": "Alege articolul din listă sau marchează-l „articol nou” — "
                          "stocul se ține pe articol, iar NIR-ul nu alege în locul tău."})
            ids.append(None)
    return ids, erori


def adauga_nir(conn, schema, nir):
    """nir: {numar, data, furnizor?, cui?, factura_ref?, linii: [...]}.
    Calculează prin motor, persistă NIR + linii, creează notele ciorne.
    [cap.24 regula 2] validare per-linie AUTORITARA: un articol incomplet se raporteaza langa campul lui
    (nir-l{i}-..), nu il filtreaza tacit frontendul."""
    # [lotul 5, 04.09.2026] Un NIR FARA articole nu e o receptie. Pana azi, `{}` trecea de
    # verificarea per-linie (n-avea ce verifica) si cadea mai jos pe `nir["linii"]`, iar contabilul
    # primea `{"detail": "'linii'"}` — numele campului intre ghilimele simple.
    if not (nir.get("linii") or []):
        return {"eroare": "Nota de recepție n-are niciun articol. O recepție consemnează ce a "
                          "intrat efectiv în gestiune — fără articole n-ar avea ce înregistra, "
                          "nici ce trece în jurnalul de cumpărări.",
                "erori_campuri": [{"camp": "nir-linii", "mesaj": "cel puțin un articol"}]}
    # [lotul 07.10 B, C10, decizia Costin] „evaluarea stocului (la cost CMP/FIFO sau la preț de vânzare cu amănuntul) e setare a
    # firmei și se aplică identic la intrări și ieșiri”. Setarea e `metoda_stoc` (etichetele ei spun evaluarea): cantitativ-
    # valoric = cost (ieșirile 607=371 la CMP), global-valoric = preț cu amănuntul (descărcarea lunară cu K). Nedeclarată -> se
    # cere acum, o dată, în Date firmă. Până azi NIR-ul scria MEREU la preț de vânzare (371=378, 371=4428), și la firma la cost.
    from core import metoda_stoc as _ms
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        metoda = _ms.citeste(cur, schema)
    if metoda is None:
        e = _ms.refuz(_ms.COD_NEDECLARATA, "NIR-ul nu s-a salvat: metoda de stoc a firmei nu e declarată. Declar-o în Date firmă — "
                                           "de ea depinde cum intră marfa (la cost sau la preț de vânzare), o singură dată.")
        return {"eroare": str(e), "cod": e.cod, "ecran": e.ecran}
    lipsa = _nir_campuri_lipsa(nir.get("linii") or [], metoda)
    if lipsa:
        return {"eroare": "Completează articolele: " + "; ".join(x["eticheta"] for x in lipsa),
                "erori_campuri": [{"camp": x["camp"], "mesaj": x["eticheta"]} for x in lipsa]}
    try:
        for _i, _l in enumerate(nir["linii"]):
            if _l.get("cota_tva") is None:
                raise _m.RefuzLinie("Alege cota de TVA la «%s»." % (_l.get("denumire") or ""), _i, "cota_tva")
        motor = _m.nir_gv if metoda == _ms.GV else _m.nir_cost
        rez = motor(nir["linii"], transport=nir.get("transport", 0), taxe=nir.get("taxe", 0),
                    cont_transport=nir.get("cont_transport") or "401", cont_taxe=nir.get("cont_taxe") or "446")
    except _m.RefuzLinie as e:
        return {"eroare": str(e), "erori_campuri": [{"camp": "nir-l%d-%s" % (e.linie, e.camp), "mesaj": str(e)}]}
    except (ValueError, KeyError) as e:
        return {"eroare": str(e)}
    articole = []
    if metoda == _ms.CV:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            articole, er = _articole_nir(cur, schema, nir["linii"])
        if er:
            return {"eroare": "; ".join(x["mesaj"] for x in er), "erori_campuri": er}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        desc = f"NIR {nir['numar']} {nir.get('furnizor') or ''}".strip()
        from core import jurnal_api as _j   # [05.10.2026, comanda Costin pct.6] NIR-ul e documentul notelor lui
        ids = _noteaza(cur, schema, nir["data"], desc, rez["note"], _j.eticheta_document("NIR", nir["numar"], nir["data"]))
        cur.execute(f"""INSERT INTO {schema}.nir
                        (numar, data, furnizor, cui, factura_ref, cost_total,
                         valoare_vanzare, adaos_total, tva_neexigibila, transport, taxe,
                         inregistrari_ids, metoda_stoc)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (nir["numar"], nir["data"], nir.get("furnizor"), nir.get("cui"),
                     nir.get("factura_ref"), rez["cost_total"], rez["valoare_vanzare"],
                     rez["adaos_total"], rez["tva_neexigibila"], rez["transport"], rez["taxe"],
                     json.dumps(ids), metoda))
        nid = cur.fetchone()["id"]
        document = _j.eticheta_document("NIR", nir["numar"], nir["data"])
        for i, l in enumerate(rez["linii"]):
            den = l.get("denumire")
            if metoda == _ms.CV:
                aid = articole[i]
                if aid is None:          # articol nou, creat EXPLICIT (C11c)
                    cur.execute(f"INSERT INTO {schema}.articole (denumire, um) VALUES (%s, %s) RETURNING id",
                                (" ".join(str(den).split()), l.get("um") or "buc"))
                    aid = cur.fetchone()["id"]
                else:
                    cur.execute(f"SELECT denumire FROM {schema}.articole WHERE id = %s", (aid,))
                    den = cur.fetchone()["denumire"]
                # intrarea în fișa de magazie, la COST (cu accesoriul repartizat): stocul și CMP-ul se văd imediat (C11e)
                cur.execute(f"""INSERT INTO {schema}.miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document)
                                VALUES (%s,%s,'intrare',%s,%s,%s,%s)""",
                            (aid, nir["data"], Decimal(str(l["cantitate"])),
                             (l["cost"] / Decimal(str(l["cantitate"]))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
                             l["cost"], document))
            cur.execute(f"""INSERT INTO {schema}.nir_linii
                            (nir_id, denumire, cantitate, pret_achizitie, pret_vanzare, cota_tva, articol_id)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (nid, den, Decimal(str(l["cantitate"])),
                         Decimal(str(l["pret_achizitie"])),
                         Decimal(str(l["pret_vanzare"])) if metoda == _ms.GV else None,
                         Decimal(str(l["cota_tva"])), aid if metoda == _ms.CV else None))
    return {"id": nid, "inregistrari": ids, "metoda": metoda,
            "cost_total": str(rez["cost_total"]), "cost_baza_total": str(rez["cost_baza_total"]),
            "transport": str(rez["transport"]), "taxe": str(rez["taxe"]),
            "adaos_total": str(rez["adaos_total"]),
            "tva_neexigibila": str(rez["tva_neexigibila"]),
            "valoare_vanzare": str(rez["valoare_vanzare"])}


def lista_nir(conn, schema, an, luna):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT * FROM {schema}.nir
                        WHERE date_trunc('month', data) = %s ORDER BY data, id""",
                    (f"{an}-{luna:02d}-01",))
        out = []
        for r in cur.fetchall():
            out.append({k: (str(v) if isinstance(v, Decimal) or hasattr(v, "isoformat") else v)
                        for k, v in r.items()})
        return out


def nir_detaliu(conn, schema, nir_id):
    """[lotul 07.10 B, C11d] NIR-ul cu articolele și notele lui (din `inregistrari_ids`), sau None."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.nir WHERE id = %s", (nir_id,))
        n = cur.fetchone()
        if not n:
            return None
        cur.execute(f"SELECT denumire, cantitate, pret_achizitie, pret_vanzare, cota_tva, articol_id FROM {schema}.nir_linii "
                    "WHERE nir_id = %s ORDER BY id", (nir_id,))
        linii = [dict(x) for x in cur.fetchall()]
        ids = [int(x) for x in (n["inregistrari_ids"] or [])]
        note = []
        if ids:
            cur.execute(f"""SELECT i.id, i.status, l.cont_debit, l.cont_credit, l.suma FROM {schema}.inregistrari i
                            JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id WHERE i.id = ANY(%s) ORDER BY i.id, l.id""",
                        (ids,))
            note = [dict(x) for x in cur.fetchall()]
    s = lambda v: str(v) if isinstance(v, Decimal) or hasattr(v, "isoformat") else v  # noqa: E731
    return {"nir": {k: s(v) for k, v in n.items()}, "linii": [{k: s(v) for k, v in x.items()} for x in linii],
            "note": [{k: s(v) for k, v in x.items()} for x in note]}


def _rulaj(cur, schema, cont, parte, pana_exclusiv, de_la=None, surse=None):
    """Rulajul unui cont (debit sau credit) pe note validate, in [de_la, pana)."""
    col = "cont_debit" if parte == "debit" else "cont_credit"
    q = f"""SELECT COALESCE(SUM(l.suma),0) FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE l.{col} = %s AND i.status='validata' AND i.data < %s"""
    p = [cont, pana_exclusiv]
    if surse:
        q += " AND i.sursa = ANY(%s)"; p.append(list(surse))
    if de_la:
        q += " AND i.data >= %s"; p.append(de_la)
    cur.execute(q, p)
    return Decimal(cur.fetchone()[0] or 0)


def descarca_luna(conn, schema, an, luna):
    """Descărcarea gestiunii pe luna dată, din rulajele reale (note validate).
    Cumulat de la 1 ianuarie (OMFP 1802); soldurile inițiale de exercițiu
    se preiau din solduri_initiale dacă există."""
    from datetime import date
    inceput_an = date(an, 1, 1)
    inceput_luna = date(an, luna, 1)
    sfarsit = date(an + (luna == 12), (luna % 12) + 1, 1)
    # [05.10.2026, comanda Costin pct.10] a doua rulare pe aceeași lună scria al doilea set de ciorne 607/378/4428=371.
    # Cheia actului e `numar`; notele de dinainte de cheie se recunosc după descriere (aceeași formă, aceeași sursă).
    cheie, descr = "DESC-GV-%d-%02d" % (an, luna), "Descarcare gestiune %02d/%d" % (luna, an)
    # [06.10.2026, comanda Costin §6.3] descărcarea globală e a firmei GLOBAL-VALORICE; la cea cantitativ-valorică marfa iese
    # pe articol (inclusiv Z-ul HoReCa, prin rețete) — o singură descărcare pe ieșire. Metoda nedeclarată se refuză numit.
    from core import metoda_stoc as _ms
    with conn.cursor() as cur:
        try:
            _ms.cere(cur, schema, _ms.GV, "Descărcarea lunară a gestiunii")
        except ValueError as e:
            return {"cod": e.cod, "eroare": str(e), "ecran": getattr(e, "ecran", None),   # [lotul 07.10 pct.2] ținta refuzului
                    "regula": getattr(e, "regula", None)}
    with conn.cursor() as cur:
        cur.execute(f"""SELECT id FROM {schema}.inregistrari
                        WHERE numar = %s OR (sursa = 'stocuri' AND descriere = %s) ORDER BY id""", (cheie, descr))
        existente = [r[0] for r in cur.fetchall()]
    if existente:
        return {"cod": "DEJA_DESCARCATA", "inregistrari_existente": existente,
                "eroare": "Gestiunea pe %02d/%d e deja descărcată (notele #%s). Ca s-o refaci, șterge întâi acele ciorne "
                          "din Registrul jurnal; o notă validată se corectează printr-o altă notă."
                          % (luna, an, ", #".join(str(x) for x in existente))}
    with conn.cursor() as cur:
        si = {}
        for cont in ("371", "378", "4428"):
            cur.execute(f"""SELECT COALESCE(SUM(sold_debitor),0), COALESCE(SUM(sold_creditor),0)
                            FROM {schema}.solduri_initiale WHERE cont LIKE %s""", (cont + "%",))
            d, c = cur.fetchone()
            si[cont] = Decimal(d or 0) - Decimal(c or 0)   # debitor pozitiv
        # rulaje cumulate de la inceputul anului pana la sfarsitul lunii
        rd_371 = _rulaj(cur, schema, "371", "debit", sfarsit, inceput_an)
        rc_378 = _rulaj(cur, schema, "378", "credit", sfarsit, inceput_an)
        rc_4428 = _rulaj(cur, schema, "4428", "credit", sfarsit, inceput_an)
        # vanzari de marfuri DOAR pe luna
        # [PIVOT 06.10.2026, comanda Costin §6.3 — supersedă nota din 05.10] Descărcarea globală rulează NUMAI la firma
        # global-valorică, unde ieșirile pe articol se refuză; deci vânzările din FACTURI (sursa `facturi`, cu sau fără articol)
        # intră aici — e singura lor descărcare. Înainte erau excluse, iar factura fără articol nu se descărca deloc.
        rc_707 = _rulaj(cur, schema, "707", "credit", sfarsit, inceput_luna, surse=("horeca_z", "amef", "stocuri", "facturi"))
        # TVA aferenta vanzarilor de marfuri: proportional din 4427 e riscant;
        # folosim TVA neexigibila medie: tva = rc707 * (Si4428+Rc4428)/numitor-ul fara TVA
        # -> mai sigur: tva = rc707 * cota medie din stoc
    try:
        k = _m.coeficient_k(-si["378"], rc_378, si["371"], rd_371, -si["4428"], rc_4428)
    except ValueError as e:
        return {"eroare": str(e)}
    baza_stoc = (si["371"] + rd_371) - (-si["4428"] + rc_4428)
    tva_stoc = -si["4428"] + rc_4428
    tva_vanzari = (rc_707 * tva_stoc / baza_stoc).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if baza_stoc else Decimal("0")
    rez = _m.descarcare_gv(rc_707, tva_vanzari, -si["378"], rc_378,
                           si["371"], rd_371, -si["4428"], rc_4428)
    if not rez["note"]:
        # [P8] FAPT despre luna, nu un mesaj: absenta vanzarilor e o constatare, si poarta perioada.
        return dict(_af.afirmatie(
            "fapt", "descarcare gestiune", "fără vânzări de mărfuri în luna", an=an, luna=luna,
            temei_completitudine="rulajele contului 707 din notele validate ale lunii"),
            k=None, mesaj="fără vânzări de mărfuri în luna", note=[])
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        import calendar
        ultima_zi = date(an, luna, calendar.monthrange(an, luna)[1])
        ids = _noteaza(cur, schema, ultima_zi, descr, rez["note"], numar=cheie)
        # [06.10.2026, comanda Costin §6.2] O descărcare = O situație de descărcare a gestiunii, pe toate notele ei
        from core import documente_interne as _di
        _di.genereaza(cur, schema, "situatie_descarcare", ultima_zi, ids)
    return {"k": str(rez["k"].quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)), "cmv": str(rez["cmv"]),
            "adaos": str(rez["adaos"]), "tva": str(rez["tva"]),
            "total_371": str(rez["total_371"]), "inregistrari": ids}
