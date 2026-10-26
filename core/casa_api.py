# -*- coding: utf-8 -*-
"""Registru de casă — API. Motorul de plafoane e în core/casa.py.

Fiecare operațiune generează notă ciornă (AI propune, contabilul validează)."""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from decimal import Decimal, ROUND_HALF_UP
from psycopg2.extras import RealDictCursor
from core import casa as _m
from core import cui_forma as _forma_cui
from core import chei_unice as _chei   # [lotul 10, C73 / U2] stornarea dublă -> refuz numit și la cursă, nu 500
from core.pdf_util import bani as _bani, data_ro as _data_ro, serie_nr as _ncs   # [lotul 11, 443] afișare „F6 nr. 1”, nu „F61” (numai pentru om: `numar` e text pe ecran, nu identificator)

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


def nota_numeste_chitanta(cur, schema, op_id, chitanta, scrie=True):
    """[lotul 12, deficiența 168 — „descrierea notei chitanței doar numele clientului”; retest 08.10 pct.19: „trebuie să conțină chitanța
    și factura stinsă”] Nota operațiunii de casă `op_id` pe care s-a emis chitanța `chitanta` („SERIE-NR”) o numește în descriere, cu ce
    stinge: „Încasare de la client — chitanța CHF1-2 — factura F1A nr. 4 din 06.10.2026 — Client”. Drumul care avea nevoie: chitanța emisă
    automat la încasarea facturii din Casă (456, `uc_tenants.chitante_pe_incasare`) — nota se scria înainte de chitanță, deci fără ea. Aceeași
    formulă ca la scriere (`descriere_nota`), aceeași factură ca nota (`inregistrari.factura_id`, seria separat — 443).
    Numai pe CIORNĂ (nota validată nu se modifică — OMFP 1802/2014 pct.69, triggerul `regula_nota`; decizia Costin 09.10: nota 118 rămâne).
    Numai încasarea de la client (factura stinsă sau avansul): la vânzarea fără factură (D394 Î2) descrierea poartă textul „reprezentând”
    al chitanței, scris de om la emitere, pe care nota nu-l mai are de unde reface — acolo nota numea deja chitanța (`chitanta_emite`).
    Întoarce (nota, starea, descrierea de acum, descrierea care numește chitanța, data notei), sau None (fără operațiune / altă categorie);
    scrie numai cu `scrie`, dacă diferă și nota e ciornă (`scrie=False`: planul migrării datelor existente,
    `core/migrare_descriere_nota_chitanta.py`). Cursorul: oricare (tuplu sau dicționar)."""
    cur.execute(f"""SELECT o.categorie, o.partener, o.avans, i.id, i.status, i.descriere, i.data, f.serie, f.numar, f.data_emitere
                      FROM {schema}.casa_operatiuni o JOIN {schema}.inregistrari i ON i.id = o.inregistrare_id
                      LEFT JOIN {schema}.facturi f ON f.id = i.factura_id
                     WHERE o.id = %s""", (op_id,))
    r = cur.fetchone()
    if not r:
        return None
    cat, partener, avans, nid, status, vechi, data_n, serie, numar, data_f = tuple(r.values()) if isinstance(r, dict) else tuple(r)
    if cat != "incasare_client":
        return None
    stinge = (("factura %s din %s" % (_ncs(serie, numar), _data_ro(data_f))) if numar is not None
              else ("avans de la client" if avans else None))
    nou = descriere_nota({"categorie": cat, "document": chitanta, "fel_document": "chitanța", "stinge": stinge, "partener": partener})
    if scrie and nou != vechi and status == "ciorna":
        cur.execute(f"UPDATE {schema}.inregistrari SET descriere = %s WHERE id = %s AND status = 'ciorna'", (nou, nid))
    return nid, status, vechi, nou, data_n


#: [lotul 6 pct.3a, 278] categoriile care sting facturi: încasarea stinge facturi EMISE, plata — PRIMITE
CATEGORII_CU_FACTURI = {"incasare_client": "emisa", "plata_furnizor": "primita"}
COD_AVANS_DESTINATIE = "AVANS_DESTINATIE"   # [407] avansul acordat furnizorului cere destinația (4091 / 4092 / 4093 / 4094)
#: [278] refuzurile legării de facturi, pe cod (ecranul și testele citesc codul, nu textul)
COD_FARA_FACTURI, COD_FACTURA_NEPOTRIVITA, COD_PESTE_SOLD = "CATEGORIE_FARA_FACTURI", "FACTURA_NEPOTRIVITA", "ALOCARE_PESTE_SOLD"
COD_DEJA_LEGATA, COD_NOTA_VALIDATA = "OPERATIUNE_DEJA_LEGATA", "NOTA_VALIDATA"
COD_NIR_NEPOTRIVIT = "NIR_NEPOTRIVIT"   # [405] NIR-ul ales nu e un NIR fără factură cu rest de plată
#: [405] destinația avansului plătit pentru un NIR: bunuri de natura stocurilor (4091) — marfa a intrat prin NIR
DESTINATIE_AVANS_NIR = "stocuri"
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


def _acelasi_partener(a, b):
    """[lotul 11, decizia Costin 10.3 pct.4] Același cod fiscal, în forma păstrată (`cui_forma.stocare`) pe ambele părți — nu numai
    cifrele: „DE123456789” nu e „123456789”."""
    return (_forma_cui.stocare(a) or "") == (_forma_cui.stocare(b) or "")


def facturi_partener(conn, schema, categorie, cui=None):
    """Facturile deschise pe direcția categoriei (emise la încasare, primite la plată), ale partenerului cu `cui` (cifrele lui) — toate,
    fără `cui`. Fiecare: {id, numar, data_emitere, tert_nume, tert_cui, sold}. Soldul e cel al reconcilierii (`facturi_deschise`)."""
    from core import reconciliere_api as _rec
    directie = CATEGORII_CU_FACTURI.get(categorie)
    if not directie:
        return []
    deschise = [f for f in _rec.facturi_deschise(conn, schema) if f["directie"] == directie
                and (not _cifre(cui) or _acelasi_partener(f["tert_cui"], cui))]
    if not deschise:
        return []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, serie, numar, tert_nume, tip FROM {schema}.facturi WHERE id = ANY(%s)", ([f["id"] for f in deschise],))
        nume = {r["id"]: r for r in cur.fetchall()}
    # [lotul 13, 669] `preluata`: documentul „Sold la <data>” scris la migrare din soldurile pe parteneri (`nomenclator_status_factura.
    # TIP_SOLD_PRELUAT`) — ecranul îl numește ca sold preluat, nu ca factură „din <data>”
    from core import nomenclator_status_factura as _nsf
    return sorted(({"id": f["id"], "numar": _ncs(nume[f["id"]]["serie"], nume[f["id"]]["numar"]), "data_emitere": str(f["data_emitere"]),
                    "tert_nume": nume[f["id"]]["tert_nume"], "tert_cui": f["tert_cui"], "sold": str(f["sold"]),
                    "preluata": nume[f["id"]]["tip"] == _nsf.TIP_SOLD_PRELUAT} for f in deschise),
                  key=lambda f: (f["data_emitere"], f["id"]))


def niruri_neplatite(conn, schema, categorie, cui=None):
    """[deficiența 405, retestul Costin 19.10.2026] „Casă plată DANTE: «Nicio factură primită neplătită» deși NIR 1, 2, 3 neplătite; datoriile
    din NIR (408/401) nu sunt oferite.” NIR-urile fără factură (forma nouă: datoria pe 408 «Furnizori - facturi nesosite»), nelegate de o
    factură, nerefăcute și nerespinse, cu rest de plată — ale partenerului cu `cui`, toate fără `cui`. Restul = ce datorează NIR-ul pe 408
    (costul + TVA-ul neexigibil, `nir_legare.sume_nir`) minus plățile în numerar legate de el (`casa_operatiuni.nir_id`, stornările cu minus).
    Fiecare: {id, numar, data, furnizor, cui, datorie, platit, rest, eticheta}. Plata unui NIR e avans acordat furnizorului (4091 = 5311,
    decizia Costin „Avans 409x = 5311”), compensat la factură (`compensare_avans_nir`)."""
    from core import coada_api as _cq, nir_legare as _nl, stocuri_api as _sa
    from core.pdf_util import data_ro as _dr
    if categorie != "plata_furnizor":
        return []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT n.id, n.numar, n.data, n.furnizor, n.cui, n.inregistrari_ids,
                               COALESCE((SELECT SUM(o.suma) FROM {schema}.casa_operatiuni o WHERE o.nir_id = n.id), 0) AS platit
                        FROM {schema}.nir n WHERE n.factura_id IS NULL
                         AND NOT EXISTS (SELECT 1 FROM {schema}.nir r WHERE r.refacut_din_id = n.id) ORDER BY n.data, n.id""")
        nirs = [dict(r) for r in cur.fetchall() if not _cifre(cui) or _acelasi_partener(r["cui"], cui)]
        nirs = [n for n in nirs if _nl.forma_noua(cur, schema, n)]
        tenant = _nl._tenant(cur, schema) if nirs else None
        stari = _cq.stari_note(conn, tenant, [i for n in nirs for i in _sa.note_nir(n)]) if tenant else {}
        out = []
        for n in nirs:
            if any((stari.get(i) or {}).get("stare_coada") == "respinsa" for i in _sa.note_nir(n)):
                continue   # NIR respins la validare: se reface, iar NIR-ul refăcut e cel care se plătește
            cost, tva = _nl.sume_nir(cur, schema, n)
            rest = cost + tva - Decimal(str(n["platit"]))
            if rest > _BAN:
                out.append({"id": n["id"], "numar": n["numar"], "data": str(n["data"])[:10], "furnizor": n["furnizor"], "cui": n["cui"],
                            "datorie": str(cost + tva), "platit": str(n["platit"]), "rest": str(rest),
                            "eticheta": "NIR nr %s din %s" % (n["numar"], _dr(n["data"]))})
    return out


def compensare_avans_nir(cur, schema, nir_id, note):
    """[deficiența 405] Rândurile care se ADAUGĂ notei facturii legate de NIR-ul `nir_id` (`contare_facturi.contabilizeaza`, după
    `nir_legare.note_factura_legata`): avansul plătit în numerar pentru NIR (4091 = 5311) se compensează cu datoria din factură — 401 = 4091,
    cel mult cât credităm 401 în notele facturii (`avansuri.compensare_avans_platit`). Pe nota facturii (`factura_id`), deci reconcilierea
    vede factura plătită cu suma compensată, iar respingerea / re-contarea facturii o ia cu ea. [{debit, credit, suma}]; [] fără avans."""
    from core import avansuri as _av, nir_legare as _nl
    cur.execute("SELECT COALESCE(SUM(suma), 0) FROM %scasa_operatiuni WHERE nir_id = %%s" % _nl._p(schema), (int(nir_id),))
    r = cur.fetchone()
    avans = Decimal(str(list(r.values())[0] if isinstance(r, dict) else r[0]))
    datorie = (sum((Decimal(str(n["suma"])) for n in note if str(n["credit"]) == "401"), Decimal(0))
               - sum((Decimal(str(n["suma"])) for n in note if str(n["debit"]) == "401"), Decimal(0)))
    return [{"debit": d, "credit": c, "suma": v}
            for d, c, v in _av.compensare_avans_platit(avans, datorie, DESTINATIE_AVANS_NIR)]


def facturi_in_asteptare(conn, schema, categorie, cui=None):
    """[deficiența 310, comanda Costin 17.10.2026 7.2] „F1A4 nu apare la facturile deschise din cauza încasării bancare aflate la validare,
    fără să se spună asta”: facturile partenerului stinse NUMAI de o notă încă nevalidată — {numar, data_emitere, tert_nume, suma, note}
    (notele numite ca în Registrul jurnal). Nu se pot alege (ar fi încasate de două ori); se spune de ce nu sunt în listă."""
    from core import reconciliere_api as _rec, eticheta_nota as _et
    directie = CATEGORII_CU_FACTURI.get(categorie)
    if not directie:
        return []
    asteapta = [f for f in _rec.facturi_deschise(conn, schema, cu_asteptare=True) if f.get("in_asteptare") and f["directie"] == directie
                and (not _cifre(cui) or _acelasi_partener(f["tert_cui"], cui))]
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
    # [405] NIR-urile alese (plata unui NIR fără factură) sunt alocate la fel ca facturile: avansul e numai ce le depășește
    alese = (op.get("facturi") or []) + (op.get("niruri") or [])
    alocat = sum((Decimal(str(a.get("suma") or 0)) for a in alese), Decimal(0))
    deschise = facturi_partener(conn, schema, cat, op.get("cui")) if _cifre(op.get("cui")) else []
    total_deschis = sum((Decimal(f["sold"]) for f in deschise), Decimal(0))
    out = {"avans": None, "semnale": []}
    incasare = cat == "incasare_client"
    rest = suma - alocat if alese else (suma - total_deschis if _cifre(op.get("cui")) else Decimal(0))
    if op.get("avans") and not alese:
        rest = suma
    if op.get("avans_automat") is False and not alese:
        # chitanța furnizorului adusă la verificare (`uc_tenants.chitanta_stinge`) e documentul plății, nu o dispoziție: fără factura aleasă rămâne
        # plată nelegată (401 = 5311), ca înainte de 407 — ruta n-are de unde cere destinația unui avans
        rest = Decimal(0)
    if rest > _BAN:
        termen = termen_factura_avans(op.get("data"))
        from core.pdf_util import data_ro as _dr
        from core import afirmatii as _af
        # [deficiența 407] la plată, avansul e ACORDAT furnizorului: nota e 409x = 5311 (nu 401 = 5311), iar factura de avans o emite
        # furnizorul — nu firma; mesajul spune nota și cine emite factura
        mesaj = (("%s lei depășesc facturile %s ale clientului: sunt avans de la client. Emite factura de avans până la %s (Codul fiscal "
                  "art.319 alin.(16)); TVA e exigibilă la data încasării avansului (art.282 alin.(2) lit.b). Dacă suma e greșită, "
                  "corecteaz-o.") % (_bani(rest), "alese" if op.get("facturi") else "deschise", _dr(termen))) if incasare else (
                 ("%s lei depășesc %s ale furnizorului: sunt avans acordat furnizorului, cu nota 409x = 5311 (4091 la bunuri, "
                  "4092 la servicii — alege mai jos). Factura de avans o emite furnizorul, până la %s (Codul fiscal art.319 alin.(16)); "
                  "TVA-ul din ea se deduce la primire. Dacă suma e greșită, corecteaz-o.") % (
                     _bani(rest), "facturile și NIR-urile alese" if op.get("niruri") else "facturile alese" if op.get("facturi")
                     else "facturile deschise", _dr(termen)))
        out["avans"] = dict(_af.afirmatie("fapt", "avans_numerar", mesaj, unde="dispoziția de casă din %s" % _dr(op.get("data")),
                                          temei_completitudine="suma dispoziției minus facturile %s ale partenerului (soldul lor din evidență)"
                                          % ("alese" if op.get("facturi") else "deschise")),
                            suma=str(rest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), termen=str(termen), mesaj=mesaj)
    if not alese and not op.get("avans") and deschise:
        from core.common import cate as _cate
        out["semnale"].append("%s are %s (de %s lei). Dispoziția nu e legată de niciuna, deci %s: alege factura %s." % (
            "Clientul" if incasare else "Furnizorul", _cate(len(deschise), "factură deschisă", "facturi deschise"),
            _bani(total_deschis), "rămân neîncasate" if incasare else "rămân neplătite",
            "încasată" if incasare else "plătită"))
    nirs = niruri_neplatite(conn, schema, cat, op.get("cui")) if _cifre(op.get("cui")) and not alese and not op.get("avans") else []
    if nirs:
        from core.common import cate as _cate
        out["semnale"].append("Furnizorul are %s (de %s lei, marfa pe 408). Dacă dispoziția plătește unul, alege NIR-ul: plata lui e avans "
                              "acordat furnizorului (4091 = 5311), compensat la sosirea facturii (401 = 4091)." % (
                                  _cate(len(nirs), "NIR fără factură neplătit", "NIR-uri fără factură neplătite"),
                                  _bani(sum((Decimal(n["rest"]) for n in nirs), Decimal(0)))))
    return out


def _refuz_adunat(er, coduri=()):
    """[lotul 11, deficiența 440] Refuzul dispoziției cu TOATE erorile (`core.erori.ErorileFormularului`): `eroare` = toate, rând cu rând
    (o singură eroare = textul ei, ca înainte), `erori_campuri` = fiecare lângă câmpul ei, `cod` = al primei probleme care are unul."""
    d = er.detaliu()
    r = {"eroare": d["mesaj"], "erori_campuri": d["erori_campuri"]}
    if coduri:
        r["cod"] = coduri[0]
    return r


def adauga(conn, schema, op, linii=None):
    """op: {data, categorie, suma, document?, partener?, cui?, facturi?: [{factura_id, suma}], avans?}; `linii` = [(debit, credit, suma)]
    pentru categoriile din `CATEGORII_CU_LINII` (suma lor = suma operațiunii). Creează operațiunea + nota ciornă. Întoarce operațiunea +
    avertismente plafon + semnalele (`semnale`).

    [lotul 6 pct.3a/3b, 278, comanda Costin verbatim în DECIZII] „Dispoziția de casă se leagă de factura încasată (alegi factura), ca factura
    să devină încasată.” Cu `facturi`, dispoziția se împarte: câte o operațiune pe factură, cu nota legată de ea (`inregistrari.factura_id`
    — de aici o citesc reconcilierea, starea de încasare și D300), plus una `avans` pentru ce depășește facturile (OMFP 1802/2014,
    funcțiunea contului 419: avansul trece prin 411 și prin factura de avans; CF art.282 alin.(2) lit.b, art.319 alin.(16)). Fiecare
    operațiune are nota ei — invariantul pe care îl citesc ștergerea, stornarea și registrul."""
    # [lotul 11, deficiența 440, comanda Costin 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp”]
    # Fiecare problemă a dispoziției se ADAUGĂ (`core.erori.ErorileFormularului`), cu id-ul câmpului din formularul Casă (`c-data`,
    # `c-cat`, `c-suma`, `c-facturi`, `c-avans-dest`); refuzul pleacă o dată, cu toate (`_refuz_adunat`). O verificare care cere o valoare
    # refuzată deja (soldul casei cere data și suma) nu se mai face: ar spune a doua oară aceeași greșeală, cu alte cuvinte.
    from core.erori import ErorileFormularului as _Erori
    er = _Erori("Dispoziția nu s-a salvat")
    coduri = []
    # [lotul 6, 04.09.2026] `data="2026-02-31"` mergea neatinsa in `INSERT` si cadea in driver:
    # contabilul primea `500`. O zi care nu exista in calendar e o greseala de tastare.
    import datetime as _dt
    _d = op.get("data")
    data_ok = bool(_d)
    if not _d:
        er.camp("c-data", "Completează data dispoziției.")
    elif not hasattr(_d, "year"):
        try:
            _dt.date.fromisoformat(str(_d)[:10])
        except ValueError:
            er.camp("c-data", "Data operațiunii: %r nu e o dată din calendar. Se așteaptă forma "
                              "AAAA-LL-ZZ, cu o zi care există în luna aia." % (_d,))
            data_ok = False
    cat = op.get("categorie")
    if cat not in CONTURI:
        er.camp("c-cat", "Categoria %r nu e una dintre cele pe care le cunoaște registrul de "
                         "casă. Valorile posibile: %s." % (cat, ", ".join(sorted(CONTURI))))
        cat = None
    try:
        suma = Decimal(str(op.get("suma", 0)))
    except ArithmeticError:
        suma = None
    if suma is None or not suma.is_finite() or suma <= 0:
        er.camp("c-suma", "suma trebuie să fie > 0")
        suma = None
    if cat is not None and (cat in CATEGORII_CU_LINII) != bool(linii):
        er.fara_camp("Încasarea din vânzare fără factură se înregistrează din «Chitanță fără factură», cu cota "
                     "de TVA — nu ca dispoziție de casă." if cat in CATEGORII_CU_LINII
                     else "Categoria %r are o singură notă, fără rânduri date de apelant." % cat)
    if linii and suma is not None and sum(Decimal(str(l[2])) for l in linii) != suma:
        er.fara_camp("Rândurile notei (%s) nu dau suma operațiunii (%s)." % (sum(Decimal(str(l[2])) for l in linii), suma))
    aloc = op.get("facturi") or []
    aloc_nir = op.get("niruri") or []   # [405] NIR-urile fără factură plătite de dispoziție
    if cat is not None and aloc and cat not in CATEGORII_CU_FACTURI:
        er.camp("c-facturi", "Numai încasarea de la client și plata către furnizor se leagă de facturi.")
        coduri.append(COD_FARA_FACTURI)
        aloc = []
    if cat is not None and aloc_nir and cat != "plata_furnizor":
        er.camp("c-facturi", "Numai plata către furnizor se leagă de un NIR fără factură.")
        coduri.append(COD_FARA_FACTURI)
        aloc_nir = []
    if cat is None:
        aloc, aloc_nir = [], []
    parti = []   # (suma, factura_id, stinge, avans, nir_id)
    if aloc or aloc_nir:
        deschise = {f["id"]: f for f in facturi_partener(conn, schema, cat)}
        for a in aloc:
            try:
                fid, s_a = int(a.get("factura_id")), Decimal(str(a.get("suma")))
            except (TypeError, ValueError, ArithmeticError):
                er.camp("c-facturi", "Factura aleasă și suma pe ea trebuie date amândouă (primit: %r)." % (a,))
                continue
            f = deschise.get(fid)
            if not f:
                er.camp("c-facturi", "Factura aleasă nu e o factură %s cu sold de %s." % (
                    "emisă" if cat == "incasare_client" else "primită", "încasat" if cat == "incasare_client" else "plătit"))
                coduri.append(COD_FACTURA_NEPOTRIVITA)
                continue
            if s_a <= 0 or s_a > Decimal(f["sold"]) + _BAN:
                er.camp("c-facturi", "Pe factura %s rămân %s lei; nu se pot aloca %s lei." % (f["numar"], f["sold"], s_a))
                coduri.append(COD_PESTE_SOLD)
                continue
            parti.append((s_a, fid, "factura %s din %s" % (f["numar"], _data_ro(f["data_emitere"])), False, None))
        # [405] plata unui NIR fără factură: avans acordat furnizorului pentru bunurile din NIR (4091 = 5311), legat de NIR
        de_plata = {n["id"]: n for n in niruri_neplatite(conn, schema, cat)} if aloc_nir else {}
        for a in aloc_nir:
            try:
                nid, s_a = int(a.get("nir_id")), Decimal(str(a.get("suma")))
            except (TypeError, ValueError, ArithmeticError):
                er.camp("c-facturi", "NIR-ul ales și suma pe el trebuie date amândouă (primit: %r)." % (a,))
                continue
            n = de_plata.get(nid)
            if not n:
                er.camp("c-facturi", "NIR-ul ales nu e un NIR fără factură cu rest de plată (e legat de factură, plătit, refăcut sau "
                                     "respins).")
                coduri.append(COD_NIR_NEPOTRIVIT)
                continue
            if s_a <= 0 or s_a > Decimal(n["rest"]) + _BAN:
                er.camp("c-facturi", "Pe %s rămân %s lei de plată; nu se pot aloca %s lei." % (n["eticheta"], _bani(n["rest"]), _bani(s_a)))
                coduri.append(COD_PESTE_SOLD)
                continue
            parti.append((s_a, None, "avans pentru %s (factura nesosită)" % n["eticheta"], True, nid))
        alocat = sum((p[0] for p in parti), Decimal(0))
        if suma is not None and alocat > suma + _BAN:
            er.camp("c-facturi", "Suma alocată pe facturi (%s lei) depășește suma dispoziției (%s lei)." % (alocat, suma))
        elif suma is not None and suma - alocat > _BAN:
            parti.append((suma - alocat, None, "avans", True, None))
    elif cat is not None and suma is not None:
        parti = [(suma, None, op.get("stinge"), bool(op.get("avans")) and cat in CATEGORII_CU_FACTURI, None)]
        if cat == "plata_furnizor" and not op.get("avans") and data_ok:
            # [deficiența 407] partea care depășește facturile deschise ale furnizorului E avans (mesajul o spune) — nota ei e 409x = 5311,
            # nu 401 = 5311; restul, plată nelegată (401 = 5311), ca înainte
            _av0 = semnale(conn, schema, op)["avans"]
            if _av0:
                _r = Decimal(_av0["suma"])
                parti = ([(suma - _r, None, op.get("stinge"), False, None)] if suma - _r > _BAN else []) + [(_r, None, "avans", True, None)]
    tip = ("incasare" if cat in CATEGORII_INCASARE else "plata") if cat is not None else None
    if tip == "plata" and data_ok and suma is not None:
        # [deficiența 406, PRIORITAR] plata nu se salvează dacă duce casa sub zero (în ziua ei sau după): `casa_sold`, aceeași regulă
        # ca la validarea notei — eroarea sumei (`c-suma`): suma nu încape în casă
        from core import casa_sold as _cs
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            _r = _cs.refuz_iesire(cur, schema, CONTURI[cat][1], op["data"], suma, doar_validate=False, ce=ETICHETE_CATEGORIE[cat])
        if _r:
            er.camp("c-suma", _r)
            coduri.append(_cs.COD)
    # [deficiența 407] avansul ACORDAT furnizorului: 409x = 5311; contul după destinație (`avansuri.CONT_AVANS`), ales de om.
    # TEMEIUL, citit la sursă (19.10.2026, `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, funcțiunea contului 409): „Cu ajutorul
    # acestui cont se ține evidența avansurilor acordate furnizorilor [...]. În debitul contului 409 «Furnizori - debitori» se înregistrează:
    # – valoarea avansurilor acordate (401, 404)”. INTERPRETARE CU TEMEI: textul numește corespondentul 401 (avansul trece prin 401: 409x =
    # 401, apoi 401 = 5311), nu casa; 409x = 5311 e forma prescurtată a celor două, cu același sold, aleasă de Costin (decizia 405, „Avans
    # 409x = 5311”, verbatim în DECIZII „Închiderea lotului 9”). Citarea de aici spunea până azi „(5121, 5311 …)” — text care nu e în sursă.
    # [405] avansul plătit pentru un NIR (`p[4]`) are destinația dată de NIR (bunuri, 4091): nu se cere
    cont_avans = None
    if cat == "plata_furnizor" and any(p[3] and not p[4] for p in parti):
        from core import avansuri as _av
        cont_avans = _av.CONT_AVANS.get(str(op.get("avans_destinatie") or ""))
        if not cont_avans:
            er.camp("c-avans-dest", "Plata cuprinde un avans acordat furnizorului (%s lei): alege pentru ce e avansul — bunuri (4091), "
                                    "servicii (4092), imobilizări corporale (4093) sau necorporale (4094); nota avansului e 409x = 5311."
                                    % _bani(sum((p[0] for p in parti if p[3]), Decimal(0))))
            coduri.append(COD_AVANS_DESTINATIE)
    if er:
        return _refuz_adunat(er, coduri)
    sem = semnale(conn, schema, op)
    create = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        from core import avansuri as _av
        for s_p, fid, stinge, avans, nid in parti:
            rand = ([(d, c, Decimal(str(v))) for d, c, v in linii if Decimal(str(v))] if linii
                    else [(_av.CONT_AVANS[DESTINATIE_AVANS_NIR], "5311", s_p)] if nid   # [405] NIR-ul plătit: 4091 = 5311
                    else [(cont_avans, "5311", s_p)] if (avans and cont_avans) else [CONTURI[cat] + (s_p,)])   # [407]
            if fid:
                # [lotul 10, deficiența 428] încasarea / plata prin casă a unei facturi în sistemul TVA la încasare mută partea ei de TVA
                # (4428 -> 4427 la emisă, CF art.282 alin.(3), (8); 4428 -> 4426 la primită, CF art.297 alin.(2)-(3)) — punctul unic,
                # același cu banca. Înainte, casa nu muta nimic: TVA-ul facturii încasate în numerar rămânea neexigibil.
                from core import tva_incasare as _tvi
                rand = rand + _tvi.linii_la_incasare(cur, schema, fid, s_p)
            op_p = dict(op, suma=s_p, stinge=(stinge if nid else "avans " + ("de la client" if tip == "incasare" else "către furnizor"))
                        if avans else stinge)
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
                            (data, tip, categorie, document, partener, cui, suma, inregistrare_id, avans, nir_id)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                        (op["data"], tip, cat, op.get("document"), op.get("partener"),
                         op.get("cui"), s_p, iid, avans, nid))
            create.append({"id": cur.fetchone()["id"], "inregistrare_id": iid, "factura_id": fid, "nir_id": nid, "suma": str(s_p), "avans": avans,
                           "nota": " + ".join("%s=%s" % (d, c) for d, c, _v in rand)})
    return {"id": create[0]["id"], "inregistrare_id": create[0]["inregistrare_id"], "nota": create[0]["nota"], "operatiuni": create,
            "avans": sem["avans"], "semnale": sem["semnale"],
            "avertismente": verifica_plafon(conn, schema, op["data"])}


def previzualizare(conn, schema, op):
    """[lotul 6 pct.3b/3c, 278] Ce ar spune salvarea, fără să scrie: plafoanele Legii 70/2015 cu operațiunea propusă inclusă, avansul și
    factura nelegată. Formularul o cheamă la fiecare schimbare, ca avertismentul să apară înainte de „Adaugă”."""
    from core import casa_sold as _cs
    an, luna = int(str(op["data"])[:4]), int(str(op["data"])[5:7])
    plata = op.get("categorie") in CONTURI and op.get("categorie") not in CATEGORII_INCASARE
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        sold_initial, rows = _registru_luna(cur, schema, an, luna)   # [455] aceleași rânduri și același sold ca registrul
        # [406] refuzul salvării, spus înainte de „Adaugă” — aceeași regulă ca `adauga`
        refuz = _cs.refuz_iesire(cur, schema, CONTURI[op["categorie"]][1], op["data"], Decimal(str(op.get("suma") or 0)),
                                 doar_validate=False, ce=ETICHETE_CATEGORIE[op["categorie"]]) if plata else None
    ops = _pentru_motor(rows) + _pentru_motor([{"data": _date_iso(op["data"]), "tip": "incasare" if op.get("categorie") in CATEGORII_INCASARE
                                                else "plata", "suma": Decimal(str(op.get("suma") or 0)), "partener": op.get("partener"),
                                                "cui": op.get("cui"), "categorie": op.get("categorie")}])
    return dict(semnale(conn, schema, op), avertismente=_fara_decimal(_m.verifica_plafon(ops, sold_initial)), refuz=refuz,
                facturi=facturi_partener(conn, schema, op.get("categorie"), op.get("cui")),
                niruri=niruri_neplatite(conn, schema, op.get("categorie"), op.get("cui")),   # [405]
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
        # [lotul 10, deficiența 428] legată acum de factură, încasarea / plata mută și TVA-ul ei la încasare (punctul unic, ca la adăugare)
        from core import tva_incasare as _tvi
        for d, c, v in _tvi.linii_la_incasare(cur, schema, fid, op["suma"]):
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                            VALUES (%s,%s,%s,%s)""", (op["inregistrare_id"], d, c, v))
        # [lotul 12, C151] chitanța emisă automat pe încasare (456 a) stinge acum factura: o leagă de ea (D394 Î2 n-o mai cere
        # „de clasificat”, starea de încasare o vede pe factură), iar nota o numește, ca la încasarea facturii din Casă (168).
        # Textul „reprezentând” al chitanței emise nu se rescrie: documentul e emis.
        if op["categorie"] == "incasare_client":
            cur.execute(f"""UPDATE {schema}.chitante SET factura_id = %s WHERE casa_operatiune_id = %s AND NOT anulata
                            AND factura_id IS NULL RETURNING serie, numar""", (fid, op_id))
            chit = cur.fetchone()
            if chit:
                nota_numeste_chitanta(cur, schema, op_id, "%s-%s" % chit)
    return {"ok": True, "factura": f["numar"]}


def _date_iso(v):
    import datetime as _dt
    return v if hasattr(v, "year") else _dt.date.fromisoformat(str(v)[:10])


def _registru_luna(cur, schema, an, luna):
    """[lotul 11, deficiența 455, PRIORITAR] „casa F1 are două solduri în același moment: 294 la refuzul plății, 42 în registrul de casă.
    Registrul de casă, contul 5311 și verificarea de sold negativ folosesc aceeași cifră, din aceeași sursă.”

    (soldul la 1 ale lunii, rândurile registrului lunii) — amândouă din `casa_sold.note_casa`, sursa unică a soldului casei: fiecare
    notă care mișcă 5311 e un rând, cu suma și soldul ei. Nota unei operațiuni din ecranul Casă (dispoziție, chitanță, stornare) poartă
    datele operațiunii (partener, document, factură, starea, acțiunile); nota scrisă de alt modul (raportul Z, statul de plată, decontul,
    nota manuală) e rând fără acțiuni aici — se corectează din modulul ei. Până la 22.10.2026 registrul aduna numai `casa_operatiuni`,
    deci raportul Z (5311 = 707) era în casă pentru refuz și lipsea din registru.
    Temei: OMFP 2634/2015 anexa 2, Registrul de casă (cod 14-4-7A): „Registrul de casă servește ca: - document de înregistrare operativă a
    încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei
    zile, a soldului de casă; [...] Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți.” Iar
    la Chitanță (14-4-1): „În condițiile utilizării aparatelor de marcat electronice fiscale [...] documentul în baza căruia se înregistrează
    în contabilitate veniturile aferente încasărilor zilnice este Raportul fiscal de închidere zilnică” — raportul Z e document de încasare
    în numerar, deci rând în registru."""
    import datetime as _dt
    from core import casa_sold as _cs
    from core.jurnal_api import eticheta_sursa as _eticheta_sursa
    prima = _dt.date(an, luna, 1)
    urmatoarea = _dt.date(an + (luna == 12), luna % 12 + 1, 1)
    sold_initial = _cs.sold_inainte(cur, schema, "5311", prima)
    _ref, _init, note = _cs.note_casa(cur, schema, "5311", de_la=prima, pana_la=urmatoarea)
    ids = [n["inregistrare_id"] for n in note]
    # [D394 Î2] `chitanta_neclasificata`: chitanța fără factură și fără cotă legată de operațiune (de clasificat la o
    # firmă exceptată de la AMEF — D394 o refuză numită până primește cota)
    # [lotul 11, deficiența 456] `chitanta`: chitanța emisă (neanulată) pe operațiune — încasarea de la client fără ea se vede pe rând
    cur.execute(f"""SELECT o.*, (SELECT c.id FROM {schema}.chitante c WHERE c.casa_operatiune_id = o.id
                           AND c.factura_id IS NULL AND c.cota_tva IS NULL AND NOT c.anulata LIMIT 1)
                           AS chitanta_neclasificata,
                           (SELECT c.id FROM {schema}.chitante c WHERE c.casa_operatiune_id = o.id AND NOT c.anulata
                             ORDER BY c.id LIMIT 1) AS chitanta_id,
                           (SELECT ARRAY[f.serie, f.numar] FROM {schema}.inregistrari i JOIN {schema}.facturi f ON f.id = i.factura_id
                             WHERE i.id = o.inregistrare_id) AS factura_numar,
                           EXISTS (SELECT 1 FROM {schema}.casa_operatiuni s WHERE s.storno_de = o.id) AS stornata,
                           (SELECT ARRAY[n.numar, n.data::text] FROM {schema}.nir n WHERE n.id = o.nir_id) AS nir_doc
                    FROM {schema}.casa_operatiuni o
                    WHERE o.inregistrare_id = ANY(%s) ORDER BY o.id""", (ids,))
    ops = {}
    for o in cur.fetchall():
        ops.setdefault(o["inregistrare_id"], o)
    # [lotul 13, 692 / clasa 603] felul documentului legat al notei (borderou ≠ factură): eticheta sursei „facturile” nu se pune pe nota borderoului
    cur.execute(f"""SELECT i.id AS inregistrare_id, f.tip FROM {schema}.inregistrari i JOIN {schema}.facturi f ON f.id = i.factura_id
                    WHERE i.id = ANY(%s)""", (ids,))
    fel_document = {r["inregistrare_id"]: r["tip"] for r in cur.fetchall()}
    rows = []
    for n in note:
        o = ops.get(n["inregistrare_id"])
        v = n["variatie"]
        if o is not None:
            # suma și data rândului = ale notei (sursa soldului), semnul după felul operațiunii (stornarea are suma cu minus)
            rows.append(dict(o, data=n["data"], suma=v if o["tip"] == "incasare" else -v, nota_status=n["status"], alt_modul=False))
        elif v:
            rows.append({"id": None, "data": n["data"], "tip": "incasare" if v > 0 else "plata", "categorie": None,
                         "document": n["document_ref"], "partener": n["descriere"], "cui": None, "suma": abs(v),
                         "inregistrare_id": n["inregistrare_id"], "chitanta_neclasificata": None, "chitanta_id": None,
                         "nota_status": n["status"], "stornata": False, "storno_de": None, "factura_numar": None, "avans": False,
                         "nir_doc": None, "alt_modul": True,
                         "categorie_eticheta": "notă din %s" % (_eticheta_sursa(n["sursa"], fel_document.get(n["inregistrare_id"])) or "jurnal")})
    return sold_initial, rows


#: categoria registrului -> `scop` din motorul de plafoane (`casa.verifica_plafon`): ridicarea / depunerea nu sunt încasări / plăți cu
#: o persoană, iar avansul spre decontare intră în plafonul total al zilei (Legea 70/2015 art.3 alin.(4))
_SCOP = {"ridicare_banca": "ridicare_banca", "depunere_banca": "depunere_banca", "avans_decontare": "avans"}


def _pentru_motor(rows):
    """[lotul 6 pct.3c, 278] Motorul citește `scop` și `partener_tip`; până azi primea numai `categorie`, deci o ridicare de numerar
    de la bancă era socotită încasare de la o persoană juridică (avertisment fals peste 5.000 lei), iar plafonul persoanei fizice
    (Legea 70/2015 art.4 alin.(1), 10.000 lei) nu se aplica niciodată. Persoana fizică = CNP-ul (13 cifre) în locul CUI-ului.
    [455] Rândul scris de alt modul (raportul Z, statul de plată…) intră în soldul zilei (plafonul soldului), nu în plafoanele pe
    persoană: nota lui nu numește partenerul (`casa.SCOP_ALT_DOCUMENT`)."""
    return [{"data": r["data"], "tip": r["tip"], "suma": Decimal(r["suma"]),
             "partener": r["partener"] or r["cui"] or "?", "cui": r["cui"],
             "categorie": r["categorie"], "scop": _m.SCOP_ALT_DOCUMENT if r.get("alt_modul") else _SCOP.get(r["categorie"], ""),
             "partener_tip": "pf" if len(_cifre(r["cui"])) == 13 else "pj"} for r in rows]


def registru(conn, schema, an, luna):
    """Registrul lunii cu sold curent pe fiecare rând + avertismente plafon. [406] Soldul de pornire e al casei la 1 ale lunii
    (preluare + notele de dinainte), nu zero în fiecare lună. [455] Rândurile și soldurile vin din `_registru_luna` (sursa unică,
    `casa_sold.note_casa`): soldul final al lunii e cel cu care refuzul ieșirii compară, iar `sold_final_validat` e al evidenței validate
    (fișa contului 5311) — diferența dintre ele sunt notele încă ciornă, fiecare pe rândul ei."""
    import datetime as _dt
    from core import casa_sold as _cs
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        sold_initial, rows = _registru_luna(cur, schema, an, luna)
        sold_validat = _cs.sold_inainte(cur, schema, "5311", _dt.date(an + (luna == 12), luna % 12 + 1, 1), doar_validate=True)
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
                    # [405] NIR-ul plătit (avans 4091 = 5311), numit ca documentul, nu prin id
                    "nir": ("NIR nr %s din %s" % (r["nir_doc"][0], _data_ro(r["nir_doc"][1]))) if r.get("nir_doc") else None,
                    # [407] avansul acordat furnizorului (409x) nu se leagă de o factură: se compensează la factura finală
                    "se_leaga": r["categorie"] in CATEGORII_CU_FACTURI and not r["factura_numar"] and not r.get("storno_de")
                                and r["nota_status"] == "ciorna" and not (r["categorie"] == "plata_furnizor" and r.get("avans")),
                    # [455] rândul scris de alt modul (raportul Z, statul de plată…): fără acțiuni în Casă
                    "alt_modul": bool(r.get("alt_modul")),
                    # [456] chitanța emisă pe operațiune; încasarea de la client fără chitanță se spune pe rând
                    "chitanta_id": r.get("chitanta_id"),
                    "fara_chitanta": r["categorie"] == "incasare_client" and not r.get("storno_de") and not r.get("chitanta_id")
                                     and not r.get("stornata"),
                    # [Retest 2 pct.2] categoria în cuvinte — ecranul nu afișează cheia din bază
                    "categorie_eticheta": r.get("categorie_eticheta") or ETICHETE_CATEGORIE.get(r["categorie"], r["categorie"])})
    return {"operatiuni": out,
            "sold_initial": str(sold_initial), "sold_final": str(_m.sold_final(ops, sold_initial)),
            "sold_final_validat": str(sold_validat),
            "avertismente": _fara_decimal(_m.verifica_plafon(ops, sold_initial))}


def verifica_plafon(conn, schema, la_data):
    """Avertismentele de plafon pentru luna datei date."""
    an, luna = int(str(la_data)[:4]), int(str(la_data)[5:7])
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        sold_initial, rows = _registru_luna(cur, schema, an, luna)   # [455] aceleași rânduri și același sold ca registrul
    return _fara_decimal(_m.verifica_plafon(_pentru_motor(rows), sold_initial))


#: refuzul stornării a doua — la a doua cerere conștientă și la cursa dintre două cereri simultane (un singur text)
MESAJ_DEJA_STORNATA = "Operațiunea e deja stornată."


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
            return {"eroare": MESAJ_DEJA_STORNATA}
        cur.execute(f"SELECT status, descriere, factura_id FROM {schema}.inregistrari WHERE id=%s", (op["inregistrare_id"],))
        n = cur.fetchone()
        if not n or n["status"] != "validata":
            return {"eroare": "Nota operațiunii nu e validată — operațiunea se șterge, nu se stornează."}
        if op["tip"] == "incasare":
            # [406] stornarea unei încasări scoate banii din casă: aceeași regulă ca plata (`casa_sold`)
            from core import casa_sold as _cs
            _r = _cs.refuz_iesire(cur, schema, "5311", data, op["suma"], doar_validate=False, ce="Stornarea încasării")
            if _r:
                return {"eroare": _r, "cod": _cs.COD}
        doc = ("STORNO " + (op["document"] or "op. %s" % op["id"]))[:50]   # casa_operatiuni.document varchar(50)
        # [lotul 10, C73 / U2] o operațiune se stornează o singură dată (`casa_operatiuni_storno_de_uq`). Două stornări simultane treceau
        # amândouă de verificarea de mai sus, iar a doua cădea cu 500. Savepoint-ul helperului cuprinde și nota în roșu, deci la cursă
        # nu rămâne nimic scris, iar refuzul e ACELAȘI ca la a doua stornare conștientă.
        try:
            with _chei.refuza_dublura(cur, ("casa_operatiuni_storno_de_uq",), lambda cur, e: _chei.CheieDublata(MESAJ_DEJA_STORNATA)):
                # [lotul 6 pct.3a, 278] nota în roșu stinge aceeași factură ca nota inițială, în minus: factura redevine neîncasată
                cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref, factura_id)
                                VALUES (%s, %s, 'casa', 'ciorna', %s, %s) RETURNING id""",
                            (data, ("Stornare: " + (n["descriere"] or ""))[:200], doc, n["factura_id"]))
                iid = cur.fetchone()["id"]
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                                SELECT %s, cont_debit, cont_credit, -suma FROM {schema}.inregistrari_linii WHERE inregistrare_id = %s""",
                            (iid, op["inregistrare_id"]))
                # [405] stornarea plății unui NIR poartă NIR-ul, cu suma cu minus: NIR-ul redevine neplătit (`niruri_neplatite`)
                cur.execute(f"""INSERT INTO {schema}.casa_operatiuni (data, tip, categorie, document, partener, cui, suma, inregistrare_id,
                                                                      storno_de, nir_id)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                            (data, op["tip"], op["categorie"], doc, op["partener"], op["cui"], -op["suma"], iid, op_id, op.get("nir_id")))
                oid = cur.fetchone()["id"]
        except _chei.CheieDublata as e:
            return {"eroare": str(e)}
        from core import repo_casa as _rc
        _rc.anuleaza_chitantele_operatiunii(cur, schema, op_id)
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
        # [lotul 11, 456] chitanța emisă pe operațiune (automat, la încasarea facturii) nu se șterge cu ea: se anulează, ca la stornare
        from core import repo_casa as _rc
        _rc.anuleaza_chitantele_operatiunii(cur, schema, op_id)
        cur.execute(f"DELETE FROM {schema}.casa_operatiuni WHERE id=%s", (op_id,))
    return {"ok": True}
