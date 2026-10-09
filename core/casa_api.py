# -*- coding: utf-8 -*-
"""Registru de casă — API. Motorul de plafoane e în core/casa.py.

Fiecare operațiune generează notă ciornă (AI propune, contabilul validează)."""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import casa as _m

# categorie -> (debit, credit) ; 5311 = casa in lei
CONTURI = {
    "incasare_client":  ("5311", "4111"),
    "plata_furnizor":   ("401",  "5311"),
    "ridicare_banca":   ("5311", "581"),
    "depunere_banca":   ("581",  "5311"),
    "avans_decontare":  ("542",  "5311"),
    # [D394 Î2, 03.10.2026] vânzarea încasată pe chitanță fără factură, la firma exceptată de la AMEF (OUG 28/1999
    # art.2): nota are DOUĂ rânduri — 5311 = cont venit (baza) și 5311 = 4427 (TVA) — date de `chitanta_emite` prin
    # `linii`. Fără ele categoria e refuzată: nu se naște din dispoziția generică, unde n-ar avea cotă.
    "vanzare_fara_factura": ("5311", None),
}
CATEGORII_INCASARE = {"incasare_client", "ridicare_banca", "vanzare_fara_factura"}
#: [retest 08.10 pct.19] felul operațiunii, în cuvinte — începutul descrierii notei (`descriere_nota`)
ETICHETE_CATEGORIE = {
    "incasare_client": "Încasare de la client", "plata_furnizor": "Plată către furnizor",
    "ridicare_banca": "Ridicare de numerar din bancă", "depunere_banca": "Depunere de numerar în bancă",
    "avans_decontare": "Avans spre decontare", "vanzare_fara_factura": "Vânzare fără factură",
}
#: categoriile care se nasc DOAR dintr-un document propriu (cu `linii`), nu din dispoziția generică
CATEGORII_CU_LINII = {"vanzare_fara_factura"}
#: [D394 Î2] încasările CUNOSCUTE fără caracter de vânzare (decizia Costin 03.10: ridicare de numerar din bancă,
#: împrumut, restituire — registrul are azi doar prima). Orice altă încasare fără chitanță, la o firmă exceptată de la
#: AMEF, e semnalată la D394 (nu blochează).
CATEGORII_FARA_VANZARE = {"ridicare_banca"}


def _fara_decimal(x):
    """Convertește recursiv Decimal/date în str pentru JSON."""
    if isinstance(x, list):
        return [_fara_decimal(i) for i in x]
    if isinstance(x, dict):
        return {k: _fara_decimal(v) for k, v in x.items()}
    return str(x) if isinstance(x, Decimal) or hasattr(x, "isoformat") else x


def descriere_nota(op):
    """Descrierea notei unei operațiuni de casă: ce s-a întâmplat, pe ce document, cu cine (și ce s-a stins, când apelantul o
    știe). [retest 08.10 pct.19] „Nota chitanței (F1, nr. crt. 17): descrierea e doar numele clientului; trebuie să conțină
    chitanța și factura stinsă.” — până azi descrierea era `partener` sau categoria, pe toate operațiunile de casă."""
    parti = [ETICHETE_CATEGORIE.get(op.get("categorie"), str(op.get("categorie") or "").replace("_", " ")),
             ("%s %s" % (op.get("fel_document") or "document", op["document"])) if op.get("document") else "",
             op.get("stinge") or "", op.get("partener") or ""]
    return " — ".join(p for p in parti if p)[:200]


def adauga(conn, schema, op, linii=None):
    """op: {data, categorie, suma, document?, partener?, cui?}; `linii` = [(debit, credit, suma)] pentru categoriile
    din `CATEGORII_CU_LINII` (suma lor = suma operațiunii). Creează operațiunea + nota ciornă. Întoarce operațiunea +
    avertismente plafon."""
    # [lotul 6, 04.09.2026] `data="2026-02-31"` mergea neatinsa in `INSERT` si cadea in driver:
    # contabilul primea `500`. O zi care nu exista in calendar e o greseala de tastare.
    import datetime as _dt
    _d = op.get("data")
    if _d and not hasattr(_d, "year"):
        try:
            _dt.date.fromisoformat(str(_d)[:10])
        except ValueError:
            return {"eroare": "Data operațiunii: %r nu e o dată din calendar. Aștept forma "
                              "AAAA-LL-ZZ, cu o zi care există în luna aia." % (_d,)}
    cat = op.get("categorie")
    if cat not in CONTURI:
        return {"eroare": "Categoria %r nu e una dintre cele pe care le cunoaște registrul de "
                          "casă. Valorile posibile: %s." % (cat, ", ".join(sorted(CONTURI)))}
    suma = Decimal(str(op.get("suma", 0)))
    if suma <= 0:
        return {"eroare": "suma trebuie să fie > 0"}
    if (cat in CATEGORII_CU_LINII) != bool(linii):
        return {"eroare": "Încasarea din vânzare fără factură se înregistrează din «Chitanță fără factură», cu cota "
                          "de TVA — nu ca dispoziție de casă." if cat in CATEGORII_CU_LINII
                else "Categoria %r are o singură notă, fără rânduri date de apelant." % cat}
    if linii and sum(Decimal(str(l[2])) for l in linii) != suma:
        return {"eroare": "Rândurile notei (%s) nu dau suma operațiunii (%s)." % (
            sum(Decimal(str(l[2])) for l in linii), suma)}
    tip = "incasare" if cat in CATEGORII_INCASARE else "plata"
    linii = [(d, c, Decimal(str(v))) for d, c, v in linii if Decimal(str(v))] if linii else [CONTURI[cat] + (suma,)]
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # [05.10.2026, comanda Costin pct.6] documentul scris pe operațiune (chitanța/dispoziția) e și al notei
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                        VALUES (%s,%s,'casa','ciorna',%s) RETURNING id""",
                    (op["data"], descriere_nota(op),
                     (str(op.get("document") or "").strip() or None)))
        iid = cur.fetchone()["id"]
        for debit, credit, v in linii:
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                        (iid, debit, credit, v))
        cur.execute(f"""INSERT INTO {schema}.casa_operatiuni
                        (data, tip, categorie, document, partener, cui, suma, inregistrare_id)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (op["data"], tip, cat, op.get("document"), op.get("partener"),
                     op.get("cui"), suma, iid))
        oid = cur.fetchone()["id"]
    return {"id": oid, "inregistrare_id": iid, "nota": " + ".join("%s=%s" % (d, c) for d, c, _v in linii),
            "avertismente": verifica_plafon(conn, schema, op["data"])}


def _operatiuni_luna(cur, schema, an, luna):
    # [D394 Î2] `chitanta_neclasificata`: chitanța fără factură și fără cotă legată de operațiune (de clasificat la o
    # firmă exceptată de la AMEF — D394 o refuză numită până primește cota)
    # [Retest 2, pct.4] starea notei (o operațiune cu notă validată nu se șterge, se stornează) și stornarea deja făcută
    cur.execute(f"""SELECT o.*, (SELECT c.id FROM {schema}.chitante c WHERE c.casa_operatiune_id = o.id
                           AND c.factura_id IS NULL AND c.cota_tva IS NULL AND NOT c.anulata LIMIT 1)
                           AS chitanta_neclasificata,
                           (SELECT i.status FROM {schema}.inregistrari i WHERE i.id = o.inregistrare_id) AS nota_status,
                           EXISTS (SELECT 1 FROM {schema}.casa_operatiuni s WHERE s.storno_de = o.id) AS stornata
                    FROM {schema}.casa_operatiuni o
                    WHERE date_trunc('month', o.data) = %s ORDER BY o.data, o.id""",
                (f"{an}-{luna:02d}-01",))
    return cur.fetchall()


def _pentru_motor(rows):
    return [{"data": r["data"], "tip": r["tip"], "suma": Decimal(r["suma"]),
             "partener": r["partener"], "cui": r["cui"],
             "categorie": r["categorie"]} for r in rows]


def registru(conn, schema, an, luna, sold_initial=0):
    """Registrul lunii cu sold curent pe fiecare operațiune + avertismente plafon."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        rows = _operatiuni_luna(cur, schema, an, luna)
    ops = _pentru_motor(rows)
    reg = _m.registru_casa(ops, sold_initial)
    out = []
    for r, linie in zip(rows, reg):
        out.append({"id": r["id"], "data": str(r["data"]), "tip": r["tip"],
                    "categorie": r["categorie"], "document": r["document"],
                    "partener": r["partener"], "cui": r["cui"],
                    "suma": str(r["suma"]), "sold": str(linie["sold"]),
                    "inregistrare_id": r["inregistrare_id"],
                    "chitanta_neclasificata": r["chitanta_neclasificata"],
                    "nota_status": r["nota_status"], "stornata": r["stornata"], "storno_de": r.get("storno_de"),
                    # [Retest 2 pct.2] categoria în cuvinte — ecranul nu afișează cheia din bază
                    "categorie_eticheta": ETICHETE_CATEGORIE.get(r["categorie"], r["categorie"])})
    return {"operatiuni": out,
            "sold_final": str(_m.sold_final(ops, sold_initial)),
            "avertismente": _fara_decimal(_m.verifica_plafon(ops, sold_initial))}


def verifica_plafon(conn, schema, la_data):
    """Avertismentele de plafon pentru luna datei date."""
    an, luna = int(str(la_data)[:4]), int(str(la_data)[5:7])
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        rows = _operatiuni_luna(cur, schema, an, luna)
    return _fara_decimal(_m.verifica_plafon(_pentru_motor(rows)))


def storneaza(conn, schema, op_id, data):
    """Stornarea unei operațiuni de casă a cărei notă e VALIDATĂ. Comanda Costin 09.10.2026 („Retest 2” pct.4, verbatim în DECIZII):
    „o operațiune cu notă validată nu se șterge, se corectează prin stornare. Aceeași regulă pentru toate sursele de note.”
    Stornare în roșu (OMFP 1802/2014 pct.69: „corectarea cu semnul minus a operațiunii inițiale”): o operațiune nouă în registru, cu
    suma cu minus, legată de cea inițială (`storno_de`), și o notă CIORNĂ cu aceleași conturi și sumele cu minus — trece prin validare
    ca orice notă. Chitanța emisă pe operațiune se anulează; factura pe care o stingea redevine neîncasată dacă nu mai e altă chitanță.
    Întoarce {"id", "inregistrare_id"} sau {"eroare"}; None dacă operațiunea nu există."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.casa_operatiuni WHERE id=%s", (op_id,))
        op = cur.fetchone()
        if not op:
            return None
        if op.get("storno_de"):
            return {"eroare": "Operațiunea e ea însăși o stornare; nu se stornează a doua oară."}
        cur.execute(f"SELECT 1 FROM {schema}.casa_operatiuni WHERE storno_de = %s", (op_id,))
        if cur.fetchone():
            return {"eroare": "Operațiunea e deja stornată."}
        cur.execute(f"SELECT status, descriere FROM {schema}.inregistrari WHERE id=%s", (op["inregistrare_id"],))
        n = cur.fetchone()
        if not n or n["status"] != "validata":
            return {"eroare": "Nota operațiunii nu e validată — operațiunea se șterge, nu se stornează."}
        doc = ("STORNO " + (op["document"] or "op. %s" % op["id"]))[:50]   # casa_operatiuni.document varchar(50)
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                        VALUES (%s, %s, 'casa', 'ciorna', %s) RETURNING id""",
                    (data, ("Stornare: " + (n["descriere"] or ""))[:200], doc))
        iid = cur.fetchone()["id"]
        cur.execute(f"""INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                        SELECT %s, cont_debit, cont_credit, -suma FROM {schema}.inregistrari_linii WHERE inregistrare_id = %s""",
                    (iid, op["inregistrare_id"]))
        cur.execute(f"""INSERT INTO {schema}.casa_operatiuni (data, tip, categorie, document, partener, cui, suma, inregistrare_id, storno_de)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (data, op["tip"], op["categorie"], doc, op["partener"], op["cui"], -op["suma"], iid, op_id))
        oid = cur.fetchone()["id"]
        cur.execute(f"UPDATE {schema}.chitante SET anulata = true WHERE casa_operatiune_id = %s AND NOT anulata RETURNING factura_id", (op_id,))
        for (fid,) in [(r["factura_id"],) for r in cur.fetchall() if r["factura_id"]]:
            cur.execute(f"SELECT 1 FROM {schema}.chitante WHERE factura_id = %s AND NOT anulata", (fid,))
            if not cur.fetchone():
                cur.execute(f"UPDATE {schema}.facturi SET platita_la = NULL WHERE id = %s", (fid,))
    return {"id": oid, "inregistrare_id": iid}


def sterge(conn, schema, op_id):
    """Șterge operațiunea + nota legată, doar dacă nota e încă ciornă."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.casa_operatiuni WHERE id=%s", (op_id,))
        op = cur.fetchone()
        if not op:
            return None
        if op["inregistrare_id"]:
            cur.execute(f"SELECT status FROM {schema}.inregistrari WHERE id=%s",
                        (op["inregistrare_id"],))
            n = cur.fetchone()
            if n and n["status"] != "ciorna":
                return {"eroare": "Nota operațiunii e validată, deci operațiunea nu se mai șterge: se corectează prin stornare."}
            from core import coada_api as _coada   # [lotul 07.10 pct.6] ștergerea operațiunii ar șterge nota de la validare
            if _coada.nota_la_validare(cur, schema, op["inregistrare_id"]):
                return {"eroare": _coada.MESAJ_NOTA_LA_VALIDARE % op["inregistrare_id"], "cod": _coada.COD_NOTA_LA_VALIDARE}
            cur.execute(f"DELETE FROM {schema}.inregistrari WHERE id=%s",
                        (op["inregistrare_id"],))
        cur.execute(f"DELETE FROM {schema}.casa_operatiuni WHERE id=%s", (op_id,))
    return {"ok": True}
