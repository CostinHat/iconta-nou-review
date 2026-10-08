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
from core import sume_lei as _sl


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


def _q2(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _d(x):
    try:
        return Decimal(str(x or 0))
    except Exception:
        return Decimal("0")


def _factura_pentru_nir(cur, schema, factura_id):
    """[decizii 07.10 pct.2] Factura de care se leagă un NIR: există, e PRIMITĂ, e factură (nu proformă) și nu e deja legată de alt
    NIR (indexul unic `nir_factura_id_uq` o păzește și în bază). Întoarce (factura, None) sau (None, motivul)."""
    try:
        fid = int(factura_id)
    except (TypeError, ValueError):
        return None, ("FACTURA_INVALIDA", "Factura aleasă nu e validă.")
    cur.execute(f"""SELECT id, serie, numar, data_emitere, directie, tip, tert_nume, tert_cui, total, tva, total_lei, tva_lei,
                           moneda, curs_bnr FROM {schema}.facturi WHERE id = %s""", (fid,))
    f = cur.fetchone()
    if not f:
        return None, ("FACTURA_INEXISTENTA", "Factura aleasă nu există.")
    f = dict(f)
    if (f.get("directie") or "") != "primita" or (f.get("tip") or "factura") != "factura":
        return None, ("FACTURA_NU_E_PRIMITA", "NIR-ul se leagă numai de o factură primită.")
    cur.execute(f"SELECT numar FROM {schema}.nir WHERE factura_id = %s LIMIT 1", (fid,))
    alt = cur.fetchone()
    f["eticheta"] = ("%s %s" % (f.get("serie") or "", f.get("numar") or "")).strip()
    if alt:
        return None, ("FACTURA_DEJA_LEGATA", "Factura %s e deja legată de NIR-ul %s." % (f["eticheta"], alt["numar"]))
    return f, None


def _nir_de_refacut(cur, schema, nir_id):
    """[retest 07.10 R1] NIR-ul pe care îl reface unul nou: există, a fost RESPINS la validare (vreuna din notele lui are ultimul
    element din coadă `respinsa`) și n-a mai fost refăcut. Întoarce ({id, numar, note}, None) sau (None, motivul)."""
    from core import note_derivate as _nd
    try:
        nid = int(nir_id)
    except (TypeError, ValueError):
        return None, ("NIR_INVALID", "NIR-ul de refăcut nu e valid.")
    cur.execute(f"SELECT id, numar, inregistrari_ids FROM {schema}.nir WHERE id = %s", (nid,))
    v = cur.fetchone()
    if not v:
        return None, ("NIR_INEXISTENT", "NIR-ul de refăcut nu există.")
    cur.execute(f"SELECT numar FROM {schema}.nir WHERE refacut_din_id = %s LIMIT 1", (nid,))
    r = cur.fetchone()
    if r:
        return None, ("NIR_DEJA_REFACUT", "NIR-ul %s a fost deja refăcut (NIR-ul %s)." % (v["numar"], r["numar"]))
    note = note_nir(v)
    if not any(_nd.respinsa(cur, schema, i) for i in note):
        return None, ("NIR_NERESPINS", "Se reface numai un NIR respins la validare; NIR-ul %s nu e respins." % v["numar"])
    return {"id": v["id"], "numar": v["numar"], "note": note}, None


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
    # [decizii 07.10 pct.2, decizia Costin] „NIR legat de factura primită, la global-valoric: NIR-ul legat scrie numai adaosul
    # (371=378) și TVA neexigibilă (371=4428); costul vine din factură. Un NIR nelegat rămâne complet.” Factura primită de marfă
    # contează deja 371=401 + 4426=401 la cost (`contare_facturi`, ACHIZITIE["marfa"]); NIR-ul legat aduce 371 la preț de vânzare.
    vechi = None
    if nir.get("refacut_din_id") not in (None, ""):
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            vechi, er = _nir_de_refacut(cur, schema, nir["refacut_din_id"])
        if er:
            return {"eroare": er[1], "cod": er[0]}
    factura = None
    if nir.get("factura_id") not in (None, ""):
        if metoda != _ms.GV:
            return {"eroare": "La firma cu stocul la cost (cantitativ-valoric), factura primită aduce ea însăși marfa în fișa de "
                              "magazie și în contabilitate — NIR-ul nu se leagă de ea. Salvează NIR-ul fără factură, sau doar "
                              "factura.", "cod": "NIR_LEGAT_LA_COST",
                    "erori_campuri": [{"camp": "sn-factura", "mesaj": "nu se leagă la stocul la cost"}]}
        if _d(nir.get("transport")) or _d(nir.get("taxe")):
            return {"eroare": "NIR-ul legat de factură nu adaugă transport sau taxe: costul vine din facturi (și accesoriul, din "
                              "factura lui). Lasă transportul și taxele la 0.", "cod": "TRANSPORT_LA_NIR_LEGAT",
                    "erori_campuri": [{"camp": "sn-transport", "mesaj": "0 la NIR-ul legat de factură"}]}
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            factura, er = _factura_pentru_nir(cur, schema, nir["factura_id"])
        if er:
            return {"eroare": er[1], "cod": er[0], "erori_campuri": [{"camp": "sn-factura", "mesaj": er[1]}]}
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
    if factura is not None:
        # Costul NIR-ului trebuie să fie costul din factură: altfel 371 (cost din factură + adaos + TVA neexigibilă calculate pe
        # costul NIR-ului) n-ar mai fi valoarea de vânzare a mărfii, iar coeficientul K al descărcării ar ieși greșit.
        try:
            _tl, _vl = _sl.antet_lei(factura)
        except _sl.LipsaCurs as e:
            return {"eroare": "Factura %s e în valută fără curs: %s" % (factura["eticheta"], e), "cod": "FACTURA_FARA_CURS",
                    "erori_campuri": [{"camp": "sn-factura", "mesaj": "factura n-are curs"}]}
        net = _q2(_tl - _vl)
        if _q2(rez["cost_baza_total"]) != net:   # amândouă la ban: egale, nu „aproape”
            msg = ("Costul din NIR (%s lei fără TVA) nu e costul din factura %s (%s lei fără TVA). La NIR-ul legat, costul vine din "
                   "factură — prețurile de achiziție de pe articole trebuie să dea aceeași sumă." %
                   (_q2(rez["cost_baza_total"]), factura["eticheta"], net))
            return {"eroare": msg, "cod": "COST_DIFERIT_DE_FACTURA", "erori_campuri": [{"camp": "sn-factura", "mesaj": msg}]}
        rez = {**rez, "note": [n for n in rez["note"] if n["debit"] == "371" and n["credit"] in ("378", "4428")]}
        nir = {**nir, "furnizor": nir.get("furnizor") or factura.get("tert_nume"), "cui": nir.get("cui") or factura.get("tert_cui"),
               "factura_ref": nir.get("factura_ref") or factura["eticheta"]}
    articole = []
    if metoda == _ms.CV:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            articole, er = _articole_nir(cur, schema, nir["linii"])
        if er:
            return {"eroare": "; ".join(x["mesaj"] for x in er), "erori_campuri": er}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SAVEPOINT nir_salvare")   # [S3] avertismentul refacerii identice nu lasă nimic scris, oricine ar fi apelantul
        desc = f"NIR {nir['numar']} {nir.get('furnizor') or ''}".strip()
        from core import jurnal_api as _j   # [05.10.2026, comanda Costin pct.6] NIR-ul e documentul notelor lui
        ids = _noteaza(cur, schema, nir["data"], desc, rez["note"], _j.eticheta_document("NIR", nir["numar"], nir["data"]))
        cur.execute(f"""INSERT INTO {schema}.nir
                        (numar, data, furnizor, cui, factura_ref, cost_total,
                         valoare_vanzare, adaos_total, tva_neexigibila, transport, taxe,
                         inregistrari_ids, metoda_stoc, factura_id, refacut_din_id)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (nir["numar"], nir["data"], nir.get("furnizor"), nir.get("cui"),
                     nir.get("factura_ref"), rez["cost_total"], rez["valoare_vanzare"],
                     rez["adaos_total"], rez["tva_neexigibila"], rez["transport"], rez["taxe"],
                     json.dumps(ids), metoda, factura["id"] if factura else None, vechi["id"] if vechi else None))
        nid = cur.fetchone()["id"]
        if vechi:
            # [retest 07.10 R1] NIR-ul refăcut înlocuiește ciornele respinse ale celui vechi (altfel ar rămâne ciorne în jurnal,
            # validabile pe alt drum); elementele lor din coadă rămân, cu motivul, ca istoric
            from core import note_derivate as _nd, coada_api as _cq
            # [S3] refacerea identică cu NIR-ul respins cere confirmare explicită (nu se blochează)
            _av = _cq.avertisment_neschimbata(_cq.amprente_note(cur, vechi["note"], schema), _cq.amprente_note(cur, ids, schema),
                                              next((_cq.motiv_respingere(cur, schema, i) for i in vechi["note"]
                                                    if _cq.motiv_respingere(cur, schema, i)), None),
                                              bool(nir.get("confirma_neschimbata")))
            if _av:
                cur.execute("ROLLBACK TO SAVEPOINT nir_salvare")
                return _av
            for _iid in vechi["note"]:
                if _nd.respinsa(cur, schema, _iid):
                    _nd.sterge_respinsa(cur, schema, _iid)
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
                # [retest 07.10 R1] `nir_id`: intrarea e a NIR-ului — respingerea lui o găsește și o stornează (`stocuri_anulare`)
                cur.execute(f"""INSERT INTO {schema}.miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, nir_id)
                                VALUES (%s,%s,'intrare',%s,%s,%s,%s,%s)""",
                            (aid, nir["data"], Decimal(str(l["cantitate"])),
                             (l["cost"] / Decimal(str(l["cantitate"]))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
                             l["cost"], document, nid))
            cur.execute(f"""INSERT INTO {schema}.nir_linii
                            (nir_id, denumire, cantitate, pret_achizitie, pret_vanzare, cota_tva, articol_id)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (nid, den, Decimal(str(l["cantitate"])),
                         Decimal(str(l["pret_achizitie"])),
                         Decimal(str(l["pret_vanzare"])) if metoda == _ms.GV else None,
                         Decimal(str(l["cota_tva"])), aid if metoda == _ms.CV else None))
    return {"id": nid, "inregistrari": ids, "metoda": metoda,
            "factura_id": factura["id"] if factura else None, "factura_ref": nir.get("factura_ref"),
            "cost_total": str(rez["cost_total"]), "cost_baza_total": str(rez["cost_baza_total"]),
            "transport": str(rez["transport"]), "taxe": str(rez["taxe"]),
            "adaos_total": str(rez["adaos_total"]),
            "tva_neexigibila": str(rez["tva_neexigibila"]),
            "valoare_vanzare": str(rez["valoare_vanzare"])}


def note_nir(n):
    """Notele NIR-ului (`inregistrari_ids`, jsonb citit ca listă sau ca text)."""
    ids = n.get("inregistrari_ids") or []
    return [int(i) for i in (json.loads(ids) if isinstance(ids, str) else ids)]


def stare_validare_nir(nirs, stari, refaceri):
    """[retest 07.10 R1] Starea NIR-ului în listă și în detaliu: „respins”, cu motivul (ultimul element din coadă al vreuneia din
    notele lui e `respinsa`), și NIR-ul care l-a refăcut, dacă există. `stari` = `coada_api.stari_note`; `refaceri` =
    {nir_id_vechi: {id, numar, data}}. Notele unui NIR refăcut au fost scoase — elementele lor din coadă rămân ca istoric."""
    for n in nirs:
        resp = [stari[i] for i in note_nir(n) if (stari.get(i) or {}).get("stare_coada") == "respinsa"]
        n["respins"] = ({"motiv_respingere": resp[0].get("motiv_respingere"), "la": resp[0].get("la")} if resp else None)
        r = refaceri.get(n["id"])
        n["refacut_in"] = r["numar"] if r else None
        # [retest 08.10 pct.5] NIR-ul care îl înlocuiește (lista îl reduce pe cel respins la o linie, lângă cel valabil)
        n["inlocuit_de"] = r
    return nirs


def refaceri_nir(conn, schema, nir_ids):
    """{nir_id_vechi: {id, numar, data}} — NIR-ul care l-a refăcut."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT refacut_din_id, id, numar, data FROM {schema}.nir WHERE refacut_din_id = ANY(%s)", ([int(i) for i in nir_ids],))
        return {r["refacut_din_id"]: {"id": r["id"], "numar": r["numar"], "data": str(r["data"])} for r in cur.fetchall()}


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
        ids = note_nir(n)
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
