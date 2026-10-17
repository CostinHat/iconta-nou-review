# -*- coding: utf-8 -*-
"""Registru de casă — API. Motorul de plafoane e în core/casa.py.

Fiecare operațiune generează notă ciornă (AI propune, contabilul validează)."""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from decimal import Decimal, ROUND_HALF_UP
from psycopg2.extras import RealDictCursor
from core import casa as _m
from core.pdf_util import bani as _bani, data_ro as _data_ro, numar_cu_serie as _ncs

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


#: [lotul 6 pct.3a, 278] categoriile care sting facturi: încasarea stinge facturi EMISE, plata — PRIMITE
CATEGORII_CU_FACTURI = {"incasare_client": "emisa", "plata_furnizor": "primita"}
#: [278] refuzurile legării de facturi, pe cod (ecranul și testele citesc codul, nu textul)
COD_FARA_FACTURI, COD_FACTURA_NEPOTRIVITA, COD_PESTE_SOLD = "CATEGORIE_FARA_FACTURI", "FACTURA_NEPOTRIVITA", "ALOCARE_PESTE_SOLD"
COD_DEJA_LEGATA, COD_NOTA_VALIDATA = "OPERATIUNE_DEJA_LEGATA", "NOTA_VALIDATA"
#: jumătate de ban: sub ea, două sume în lei cu două zecimale sunt egale (alocarea pe facturi, restul care devine avans)
_BAN = Decimal("0.005")


def termen_factura_avans(data):
    """CF art.319 alin.(16): „persoana impozabilă trebuie să emită o factură pentru suma avansurilor încasate în legătură cu o livrare de
    bunuri/prestare de servicii cel târziu până în cea de-a 15-a zi a lunii următoare celei în care a încasat avansurile”."""
    import datetime as _dt
    d = _dt.date.fromisoformat(str(data)[:10])
    return _dt.date(d.year + 1, 1, 15) if d.month == 12 else _dt.date(d.year, d.month + 1, 15)


def _cifre(cui):
    return "".join(ch for ch in str(cui or "") if ch.isdigit())


def facturi_partener(conn, schema, categorie, cui=None):
    """Facturile deschise pe direcția categoriei (emise la încasare, primite la plată), ale partenerului cu `cui` (cifrele lui) — toate,
    fără `cui`. Fiecare: {id, numar, data_emitere, tert_nume, tert_cui, sold}. Soldul e cel al reconcilierii (`facturi_deschise`)."""
    from core import reconciliere_api as _rec
    directie = CATEGORII_CU_FACTURI.get(categorie)
    if not directie:
        return []
    deschise = [f for f in _rec.facturi_deschise(conn, schema) if f["directie"] == directie
                and (not _cifre(cui) or _cifre(f["tert_cui"]) == _cifre(cui))]
    if not deschise:
        return []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, serie, numar, tert_nume FROM {schema}.facturi WHERE id = ANY(%s)", ([f["id"] for f in deschise],))
        nume = {r["id"]: r for r in cur.fetchall()}
    return sorted(({"id": f["id"], "numar": _ncs(nume[f["id"]]["serie"], nume[f["id"]]["numar"]), "data_emitere": str(f["data_emitere"]),
                    "tert_nume": nume[f["id"]]["tert_nume"], "tert_cui": f["tert_cui"], "sold": str(f["sold"])} for f in deschise),
                  key=lambda f: (f["data_emitere"], f["id"]))


def facturi_in_asteptare(conn, schema, categorie, cui=None):
    """[deficiența 310, comanda Costin 17.10.2026 7.2] „F1A4 nu apare la facturile deschise din cauza încasării bancare aflate la validare,
    fără să se spună asta”: facturile partenerului stinse NUMAI de o notă încă nevalidată — {numar, data_emitere, tert_nume, suma, note}
    (notele numite ca în Registrul jurnal). Nu se pot alege (ar fi încasate de două ori); se spune de ce nu sunt în listă."""
    from core import reconciliere_api as _rec, eticheta_nota as _et
    directie = CATEGORII_CU_FACTURI.get(categorie)
    if not directie:
        return []
    asteapta = [f for f in _rec.facturi_deschise(conn, schema, cu_asteptare=True) if f.get("in_asteptare") and f["directie"] == directie
                and (not _cifre(cui) or _cifre(f["tert_cui"]) == _cifre(cui))]
    if not asteapta:
        return []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, serie, numar, tert_nume FROM {schema}.facturi WHERE id = ANY(%s)", ([f["id"] for f in asteapta],))
        nume = {r["id"]: r for r in cur.fetchall()}
        out = []
        for f in sorted(asteapta, key=lambda f: (f["data_emitere"], f["id"])):
            out.append({"id": f["id"], "numar": _ncs(nume[f["id"]]["serie"], nume[f["id"]]["numar"]), "data_emitere": str(f["data_emitere"]),
                        "tert_nume": nume[f["id"]]["tert_nume"], "suma": str(f["sold_validat"]),
                        "note": [e for _i, e in _et.note(cur, schema.strip('"'), f["note_nevalidate"])]})
    return out


def alocare_pe_factura(conn, schema, categorie, factura_id, suma):
    """`facturi` pentru `adauga` când documentul (chitanța emisă, chitanța furnizorului) e pe O factură: cât mai e de stins din ea, cel
    mult suma documentului; restul devine avans în `adauga`. Fără factură -> []. Factura stinsă deja integral -> [] (documentul nu se mai
    leagă de ea; `adauga` îl trece ca nelegat, iar semnalul spune că depășește facturile deschise)."""
    if not factura_id:
        return []
    f = {x["id"]: x for x in facturi_partener(conn, schema, categorie)}.get(int(factura_id))
    if not f:
        return []
    return [{"factura_id": f["id"], "suma": str(min(Decimal(str(suma)), Decimal(f["sold"])))}]


def semnale(conn, schema, op):
    """[lotul 6 pct.3, 278] Ce trebuie să știe contabilul înainte și după salvarea dispoziției — O SINGURĂ sursă pentru formular
    (`previzualizare`) și pentru răspunsul salvării: avansul (partea care depășește facturile alese sau, fără facturi alese, pe cele
    deschise ale partenerului) și factura care rămâne neîncasată. Întoarce {"avans": {suma, termen, mesaj} | None, "semnale": [text]}."""
    cat = op.get("categorie")
    if cat not in CATEGORII_CU_FACTURI:
        return {"avans": None, "semnale": []}
    suma = Decimal(str(op.get("suma") or 0))
    alocat = sum((Decimal(str(a.get("suma") or 0)) for a in (op.get("facturi") or [])), Decimal(0))
    deschise = facturi_partener(conn, schema, cat, op.get("cui")) if _cifre(op.get("cui")) else []
    total_deschis = sum((Decimal(f["sold"]) for f in deschise), Decimal(0))
    out = {"avans": None, "semnale": []}
    incasare = cat == "incasare_client"
    rest = suma - alocat if op.get("facturi") else (suma - total_deschis if _cifre(op.get("cui")) else Decimal(0))
    if op.get("avans") and not op.get("facturi"):
        rest = suma
    if rest > _BAN:
        termen = termen_factura_avans(op.get("data"))
        from core.pdf_util import data_ro as _dr
        from core import afirmatii as _af
        mesaj = (("%s lei depășesc facturile %s ale %s: sunt avans %s. Emite factura de avans până la %s (Codul fiscal art.319 alin.(16)); "
                  "TVA e exigibilă la data %s (art.282 alin.(2) lit.b). Dacă suma e greșită, corecteaz-o.") % (
                     _bani(rest), "alese" if op.get("facturi") else "deschise",
                     "clientului" if incasare else "furnizorului", "de la client" if incasare else "plătit furnizorului",
                     _dr(termen), "încasării avansului" if incasare else "plății avansului"))
        out["avans"] = dict(_af.afirmatie("fapt", "avans_numerar", mesaj, unde="dispoziția de casă din %s" % _dr(op.get("data")),
                                          temei_completitudine="suma dispoziției minus facturile %s ale partenerului (soldul lor din evidență)"
                                          % ("alese" if op.get("facturi") else "deschise")),
                            suma=str(rest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), termen=str(termen), mesaj=mesaj)
    if not op.get("facturi") and not op.get("avans") and deschise:
        from core.common import cate as _cate
        out["semnale"].append("%s are %s (de %s lei). Dispoziția nu e legată de niciuna, deci %s: alege factura %s." % (
            "Clientul" if incasare else "Furnizorul", _cate(len(deschise), "factură deschisă", "facturi deschise"),
            _bani(total_deschis), "rămân neîncasate" if incasare else "rămân neplătite",
            "încasată" if incasare else "plătită"))
    return out


def adauga(conn, schema, op, linii=None):
    """op: {data, categorie, suma, document?, partener?, cui?, facturi?: [{factura_id, suma}], avans?}; `linii` = [(debit, credit, suma)]
    pentru categoriile din `CATEGORII_CU_LINII` (suma lor = suma operațiunii). Creează operațiunea + nota ciornă. Întoarce operațiunea +
    avertismente plafon + semnalele (`semnale`).

    [lotul 6 pct.3a/3b, 278, comanda Costin verbatim în DECIZII] „Dispoziția de casă se leagă de factura încasată (alegi factura), ca factura
    să devină încasată.” Cu `facturi`, dispoziția se împarte: câte o operațiune pe factură, cu nota legată de ea (`inregistrari.factura_id`
    — de aici o citesc reconcilierea, starea de încasare și D300), plus una `avans` pentru ce depășește facturile (OMFP 1802/2014,
    funcțiunea contului 419: avansul trece prin 411 și prin factura de avans; CF art.282 alin.(2) lit.b, art.319 alin.(16)). Fiecare
    operațiune are nota ei — invariantul pe care îl citesc ștergerea, stornarea și registrul."""
    # [lotul 6, 04.09.2026] `data="2026-02-31"` mergea neatinsa in `INSERT` si cadea in driver:
    # contabilul primea `500`. O zi care nu exista in calendar e o greseala de tastare.
    import datetime as _dt
    _d = op.get("data")
    if _d and not hasattr(_d, "year"):
        try:
            _dt.date.fromisoformat(str(_d)[:10])
        except ValueError:
            return {"eroare": "Data operațiunii: %r nu e o dată din calendar. Se așteaptă forma "
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
    aloc = op.get("facturi") or []
    if aloc and cat not in CATEGORII_CU_FACTURI:
        return {"eroare": "Numai încasarea de la client și plata către furnizor se leagă de facturi.", "cod": COD_FARA_FACTURI}
    parti = []   # (suma, factura_id, stinge, avans)
    if aloc:
        deschise = {f["id"]: f for f in facturi_partener(conn, schema, cat)}
        for a in aloc:
            try:
                fid, s_a = int(a.get("factura_id")), Decimal(str(a.get("suma")))
            except (TypeError, ValueError, ArithmeticError):
                return {"eroare": "Factura aleasă și suma pe ea trebuie date amândouă (primit: %r)." % (a,)}
            f = deschise.get(fid)
            if not f:
                return {"eroare": "Factura aleasă nu e o factură %s cu sold de %s." % (
                    "emisă" if cat == "incasare_client" else "primită", "încasat" if cat == "incasare_client" else "plătit"),
                        "cod": COD_FACTURA_NEPOTRIVITA}
            if s_a <= 0 or s_a > Decimal(f["sold"]) + _BAN:
                return {"eroare": "Pe factura %s rămân %s lei; nu se pot aloca %s lei." % (f["numar"], f["sold"], s_a), "cod": COD_PESTE_SOLD}
            parti.append((s_a, fid, "factura %s din %s" % (f["numar"], _data_ro(f["data_emitere"])), False))
        alocat = sum((p[0] for p in parti), Decimal(0))
        if alocat > suma + _BAN:
            return {"eroare": "Suma alocată pe facturi (%s lei) depășește suma dispoziției (%s lei)." % (alocat, suma)}
        if suma - alocat > _BAN:
            parti.append((suma - alocat, None, "avans", True))
    else:
        parti = [(suma, None, op.get("stinge"), bool(op.get("avans")) and cat in CATEGORII_CU_FACTURI)]
    sem = semnale(conn, schema, op)
    tip = "incasare" if cat in CATEGORII_INCASARE else "plata"
    create = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for s_p, fid, stinge, avans in parti:
            rand = [(d, c, Decimal(str(v))) for d, c, v in linii if Decimal(str(v))] if linii else [CONTURI[cat] + (s_p,)]
            op_p = dict(op, suma=s_p, stinge=("avans " + ("de la client" if tip == "incasare" else "către furnizor")) if avans else stinge)
            # [05.10.2026, comanda Costin pct.6] documentul scris pe operațiune (chitanța/dispoziția) e și al notei
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref, factura_id)
                            VALUES (%s,%s,'casa','ciorna',%s,%s) RETURNING id""",
                        (op["data"], descriere_nota(op_p), (str(op.get("document") or "").strip() or None), fid))
            iid = cur.fetchone()["id"]
            for debit, credit, v in rand:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                            (iid, debit, credit, v))
            cur.execute(f"""INSERT INTO {schema}.casa_operatiuni
                            (data, tip, categorie, document, partener, cui, suma, inregistrare_id, avans)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                        (op["data"], tip, cat, op.get("document"), op.get("partener"),
                         op.get("cui"), s_p, iid, avans))
            create.append({"id": cur.fetchone()["id"], "inregistrare_id": iid, "factura_id": fid, "suma": str(s_p), "avans": avans,
                           "nota": " + ".join("%s=%s" % (d, c) for d, c, _v in rand)})
    return {"id": create[0]["id"], "inregistrare_id": create[0]["inregistrare_id"], "nota": create[0]["nota"], "operatiuni": create,
            "avans": sem["avans"], "semnale": sem["semnale"],
            "avertismente": verifica_plafon(conn, schema, op["data"])}


def previzualizare(conn, schema, op):
    """[lotul 6 pct.3b/3c, 278] Ce ar spune salvarea, fără să scrie: plafoanele Legii 70/2015 cu operațiunea propusă inclusă, avansul și
    factura nelegată. Formularul o cheamă la fiecare schimbare, ca avertismentul să apară înainte de „Adaugă”."""
    an, luna = int(str(op["data"])[:4]), int(str(op["data"])[5:7])
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        rows = _operatiuni_luna(cur, schema, an, luna)
    ops = _pentru_motor(rows) + _pentru_motor([{"data": _date_iso(op["data"]), "tip": "incasare" if op.get("categorie") in CATEGORII_INCASARE
                                                else "plata", "suma": Decimal(str(op.get("suma") or 0)), "partener": op.get("partener"),
                                                "cui": op.get("cui"), "categorie": op.get("categorie")}])
    return dict(semnale(conn, schema, op), avertismente=_fara_decimal(_m.verifica_plafon(ops)),
                facturi=facturi_partener(conn, schema, op.get("categorie"), op.get("cui")),
                facturi_asteptare=facturi_in_asteptare(conn, schema, op.get("categorie"), op.get("cui")))


def leaga(conn, schema, op_id, factura_id):
    """[lotul 6 pct.3a, 278] Leagă operațiunea (încasare de la client / plată către furnizor) de factura pe care o stinge: nota ei, încă
    ciornă, primește `factura_id`. Așa se leagă și avansul de factura de avans emisă după încasare (CF art.319 alin.(16)). Refuzuri:
    nota validată (se stornează și se reface), operațiunea legată deja, factura de altă direcție sau cu sold mai mic decât suma.
    None dacă operațiunea nu există."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT o.*, i.status AS nota_status, i.factura_id FROM {schema}.casa_operatiuni o
                        LEFT JOIN {schema}.inregistrari i ON i.id = o.inregistrare_id WHERE o.id = %s""", (op_id,))
        op = cur.fetchone()
    if not op:
        return None
    if op["categorie"] not in CATEGORII_CU_FACTURI or op.get("storno_de"):
        return {"eroare": "Numai încasarea de la client și plata către furnizor se leagă de o factură.", "cod": COD_FARA_FACTURI}
    if op["factura_id"]:
        return {"eroare": "Operațiunea e legată deja de o factură.", "cod": COD_DEJA_LEGATA}
    if op["nota_status"] != "ciorna":
        return {"eroare": "Nota operațiunii e validată: legătura nu se mai schimbă. Stornează operațiunea și refă-o cu factura aleasă.",
                "cod": COD_NOTA_VALIDATA}
    from core import coada_api as _coada
    with conn.cursor() as cur:
        if _coada.nota_la_validare(cur, schema, op["inregistrare_id"]):
            return {"eroare": _coada.mesaj_nota_la_validare(cur, schema, op["inregistrare_id"]), "cod": _coada.COD_NOTA_LA_VALIDARE}
    try:
        fid = int(factura_id)
    except (TypeError, ValueError):
        return {"eroare": "Alege factura."}
    f = {x["id"]: x for x in facturi_partener(conn, schema, op["categorie"])}.get(fid)
    if not f:
        return {"eroare": "Factura aleasă nu e o factură %s cu sold." % ("emisă" if op["categorie"] == "incasare_client" else "primită"),
                "cod": COD_FACTURA_NEPOTRIVITA}
    if Decimal(str(op["suma"])) > Decimal(f["sold"]) + _BAN:
        return {"eroare": "Pe factura %s rămân %s lei, iar operațiunea are %s lei: alege o factură cu sold suficient." % (
            f["numar"], f["sold"], op["suma"]), "cod": COD_PESTE_SOLD}
    stinge = "factura %s din %s" % (f["numar"], _data_ro(f["data_emitere"]))
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {schema}.inregistrari SET factura_id = %s, descriere = %s WHERE id = %s",
                    (fid, descriere_nota(dict(op, stinge=stinge, fel_document=None)), op["inregistrare_id"]))
    return {"ok": True, "factura": f["numar"]}


def _date_iso(v):
    import datetime as _dt
    return v if hasattr(v, "year") else _dt.date.fromisoformat(str(v)[:10])


def _operatiuni_luna(cur, schema, an, luna):
    # [D394 Î2] `chitanta_neclasificata`: chitanța fără factură și fără cotă legată de operațiune (de clasificat la o
    # firmă exceptată de la AMEF — D394 o refuză numită până primește cota)
    # [Retest 2, pct.4] starea notei (o operațiune cu notă validată nu se șterge, se stornează) și stornarea deja făcută
    cur.execute(f"""SELECT o.*, (SELECT c.id FROM {schema}.chitante c WHERE c.casa_operatiune_id = o.id
                           AND c.factura_id IS NULL AND c.cota_tva IS NULL AND NOT c.anulata LIMIT 1)
                           AS chitanta_neclasificata,
                           (SELECT i.status FROM {schema}.inregistrari i WHERE i.id = o.inregistrare_id) AS nota_status,
                           (SELECT ARRAY[f.serie, f.numar] FROM {schema}.inregistrari i JOIN {schema}.facturi f ON f.id = i.factura_id
                             WHERE i.id = o.inregistrare_id) AS factura_numar,
                           EXISTS (SELECT 1 FROM {schema}.casa_operatiuni s WHERE s.storno_de = o.id) AS stornata
                    FROM {schema}.casa_operatiuni o
                    WHERE date_trunc('month', o.data) = %s ORDER BY o.data, o.id""",
                (f"{an}-{luna:02d}-01",))
    return cur.fetchall()


#: categoria registrului -> `scop` din motorul de plafoane (`casa.verifica_plafon`): ridicarea / depunerea nu sunt încasări / plăți cu
#: o persoană, iar avansul spre decontare intră în plafonul total al zilei (Legea 70/2015 art.3 alin.(4))
_SCOP = {"ridicare_banca": "ridicare_banca", "depunere_banca": "depunere_banca", "avans_decontare": "avans"}


def _pentru_motor(rows):
    """[lotul 6 pct.3c, 278] Motorul citește `scop` și `partener_tip`; până azi primea numai `categorie`, deci o ridicare de numerar
    de la bancă era socotită încasare de la o persoană juridică (avertisment fals peste 5.000 lei), iar plafonul persoanei fizice
    (Legea 70/2015 art.4 alin.(1), 10.000 lei) nu se aplica niciodată. Persoana fizică = CNP-ul (13 cifre) în locul CUI-ului."""
    return [{"data": r["data"], "tip": r["tip"], "suma": Decimal(r["suma"]),
             "partener": r["partener"] or r["cui"] or "?", "cui": r["cui"],
             "categorie": r["categorie"], "scop": _SCOP.get(r["categorie"], ""),
             "partener_tip": "pf" if len(_cifre(r["cui"])) == 13 else "pj"} for r in rows]


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
                    # [lotul 6 pct.3a, 278] factura stinsă de operațiune (numărul cu seria) și avansul
                    "factura": _ncs(*r["factura_numar"]) if r["factura_numar"] else None, "avans": bool(r.get("avans")),
                    "se_leaga": r["categorie"] in CATEGORII_CU_FACTURI and not r["factura_numar"] and not r.get("storno_de")
                                and r["nota_status"] == "ciorna",
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
        cur.execute(f"SELECT status, descriere, factura_id FROM {schema}.inregistrari WHERE id=%s", (op["inregistrare_id"],))
        n = cur.fetchone()
        if not n or n["status"] != "validata":
            return {"eroare": "Nota operațiunii nu e validată — operațiunea se șterge, nu se stornează."}
        doc = ("STORNO " + (op["document"] or "op. %s" % op["id"]))[:50]   # casa_operatiuni.document varchar(50)
        # [lotul 6 pct.3a, 278] nota în roșu stinge aceeași factură ca nota inițială, în minus: factura redevine neîncasată
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref, factura_id)
                        VALUES (%s, %s, 'casa', 'ciorna', %s, %s) RETURNING id""",
                    (data, ("Stornare: " + (n["descriere"] or ""))[:200], doc, n["factura_id"]))
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
                return {"eroare": _coada.mesaj_nota_la_validare(cur, schema, op["inregistrare_id"]), "cod": _coada.COD_NOTA_LA_VALIDARE}
            cur.execute(f"DELETE FROM {schema}.inregistrari WHERE id=%s",
                        (op["inregistrare_id"],))
        cur.execute(f"DELETE FROM {schema}.casa_operatiuni WHERE id=%s", (op_id,))
    return {"ok": True}
