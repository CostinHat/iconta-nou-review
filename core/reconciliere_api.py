# -*- coding: utf-8 -*-
"""Reconciliere bancară — strat API (tipar stat_plata_api: funcții conn+schema).

Motorul de matching e în core/reconciliere.py (pur, testat)."""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from psycopg2.extras import RealDictCursor
from core import afirmatii as _af
from core import reconciliere as _m
from core.unde import Unde as _Unde
from core.common import cate as _cate

CONT_CLIENTI, CONT_FURNIZORI = "4111", "401"


def _data_iso(v):
    """z.l.aaaa / zz.ll.aa (cu . / -) -> aaaa-ll-zz; lasă neschimbat ce e deja ISO / date. [16.10.2026, 277] Înainte numai forma de
    exact 10 caractere cu punct: `1.8.2026` ajungea la Postgres așa cum era, care o citea lună-zi (DateStyle MDY) — 8 ianuarie."""
    import re
    m = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{2}|\d{4})", v.strip()) if isinstance(v, str) else None
    if m:
        z, l, a = m.groups()
        return "%s-%02d-%02d" % (a if len(a) == 4 else "20" + a, int(l), int(z))
    return v


def _text_cheie(v):
    """Referința / descrierea în cheia mișcării: fără spațiile în plus, fără deosebire de majuscule."""
    return " ".join(str(v or "").split()).lower()


def cheie_miscare(data, suma, tip, cont, referinta, descriere):
    """[16.10.2026, lotul 6 pct.1a, 277, verbatim în DECIZII] „o linie e duplicat numai dacă aceeași mișcare (dată, sumă, sens,
    referință/descriere, cont) există deja.” Contul necunoscut (extrasele în tabel, liniile de dinainte) rămâne `None` și nu se
    socotește egal cu un cont cunoscut."""
    return (str(data), Decimal(str(suma)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), tip, (cont or "").strip() or None,
            _text_cheie(referinta), _text_cheie(descriere))


def _cont_banca(valuta):
    return "5124" if valuta else "5121"


def probabil_aceeasi_miscare(noua, veche):
    """PURĂ. [lotul 12, deficiența 479 (grav), Costin: „Linie dublă importată; notă 5121=5121 propusă”] Limita declarată la 277 (DECIZII
    „Lotul 6, comanda 1”): „aceeași mișcare venită o dată din tabel (fără cont) și o dată din MT940 (cu cont) nu se recunoaște ca aceeași”
    — linia se adăuga a doua oară și se propunea la contat. `noua` / `veche` = {data, suma, tip, cont}. Aceeași dată, sumă și sens, iar
    contul e cunoscut pe EXACT una din ele (extrasul în tabel nu-l are) -> probabil aceeași mișcare. Regula lui 277 rămâne neatinsă: cu
    contul cunoscut pe amândouă (egal sau nu) ori necunoscut pe amândouă, numai cheia întreagă (`cheie_miscare`) hotărăște."""
    def _c(x):
        return (x.get("cont") or "").strip() or None
    if (str(noua["data"]), noua["tip"]) != (str(veche["data"]), veche["tip"]):
        return False
    if Decimal(str(noua["suma"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) != \
            Decimal(str(veche["suma"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):
        return False
    return (_c(noua) is None) != (_c(veche) is None)


def motiv_dublura(veche):
    """Textul de pe rândul liniei puse deoparte (479): ce linie pare, de unde și ce poate face contabilul."""
    from core import pdf_util as _pu
    fis = (" din «%s»" % veche["fisier_sursa"]) if veche.get("fisier_sursa") else ""
    return ("pare aceeași mișcare ca linia din %s importată deja%s (aceeași dată, sumă și sens; un extras are contul băncii, celălalt nu): "
            "n-am pus-o la contat, ca să nu se înregistreze de două ori. Dacă e altă mișcare, apasă «readu»."
            % (_pu.data_ro(veche["data"]), fis))


def facturi_deschise(conn, schema, cu_asteptare=False):
    """Facturi cu sold > 0. Sold = total_lei(±total) - sume decontate prin
    inregistrari legate cu factura_id (credit 4111 la emise / debit 401 la primite).
    [17.10.2026, lotul 6, 278] Nota unei chitanțe de dinainte de 278 n-are `factura_id` (atunci nu se punea), iar o notă validată nu se
    mai modifică (`regula_nota`) — legătura ei cu factura se citește din chitanța neanulată (`chitante.inregistrare_id` ->
    `chitante.factura_id`), ca la `jurnal_api`. Fără ea, factura încasată cu chitanță rămânea „deschisă” la reconcilierea bancară.
    [lotul 10, 428, decizia Costin „Construiesc acum”] „fiecare compensare stinge cele două facturi”: nota compensării (401 = 4111, fără
    `factura_id`) stinge ambele facturi prin `compensari` (`compensari_api.nota_de_compensare`) — altfel banca și casa ar mai încasa o dată
    partea compensată."""
    from core import compensari_api as _cz, nomenclator_status_factura as _nsf
    from core import facturi as _fc_tp   # [lotul 13, 546] totalul de plată: factura primită cu taxare inversă, fără TVA-ul beneficiarului
    stinge = _cz.nota_stinge_factura("i", "f.id", f"{schema}.")   # [lotul 12, C153] condiția unică: nota legată, chitanța veche, compensarea
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.id, f.tert_cui, f.directie, f.data_emitere, f.serie, f.numar,
                   {_fc_tp.SQL_TOTAL_DE_PLATA_LEI.format(a='f')} AS total,
                   COALESCE((SELECT SUM(l.suma)
                             FROM {schema}.inregistrari i
                             JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                             WHERE {stinge}
                               AND ((f.directie='emisa'   AND l.cont_credit=%s)
                                 OR (f.directie='primita' AND l.cont_debit=%s))), 0) AS decontat,
                   (SELECT array_agg(DISTINCT i.id ORDER BY i.id)
                      FROM {schema}.inregistrari i
                      JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                     WHERE {stinge} AND i.status <> 'validata'
                       AND ((f.directie='emisa' AND l.cont_credit=%s) OR (f.directie='primita' AND l.cont_debit=%s))) AS note_nevalidate,
                   COALESCE((SELECT SUM(l.suma)
                             FROM {schema}.inregistrari i
                             JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                             WHERE {stinge} AND i.status <> 'validata'
                               AND ((f.directie='emisa'   AND l.cont_credit=%s)
                                 OR (f.directie='primita' AND l.cont_debit=%s))), 0) AS decontat_nevalidat,
                   COALESCE((SELECT SUM(COALESCE(st.total_lei, st.total))
                             FROM {schema}.facturi st
                             WHERE st.storno_din_id = f.id), 0) AS storno
            FROM {schema}.facturi f
            WHERE f.status NOT IN ('anulata','storno')
              AND f.storno_din_id IS NULL
              AND {_nsf.clauza_tip_cu_incasare("f")}
        """, (CONT_CLIENTI, CONT_FURNIZORI) * 3)   # [lotul 12, C144] numai documentele cu încasare (nu proforme, avize)
        rez = []
        for r in cur.fetchall():
            sold = Decimal(r["total"] or 0) - Decimal(r["decontat"] or 0) + Decimal(r["storno"] or 0)
            if sold > Decimal("0.01"):
                # [480] seria și numărul: potrivirea după numărul facturii scris în descrierea liniei (`reconciliere.facturi_dupa_numar`)
                rez.append({"id": r["id"], "tert_cui": r["tert_cui"],
                            "directie": r["directie"],
                            "data_emitere": r["data_emitere"], "sold": sold, "serie": r["serie"], "numar": r["numar"]})
            elif cu_asteptare and sold + Decimal(r["decontat_nevalidat"] or 0) > Decimal("0.01"):
                # [deficiența 310] stinsă numai de o încasare / plată a cărei notă e încă la validare: nu e deschisă, dar se spune de ce
                rez.append({"id": r["id"], "tert_cui": r["tert_cui"], "directie": r["directie"], "data_emitere": r["data_emitere"],
                            "sold": sold, "in_asteptare": True, "note_nevalidate": list(r["note_nevalidate"] or []),
                            "sold_validat": sold + Decimal(r["decontat_nevalidat"] or 0)})
        return rez


def _cont_norm(v):
    return re.sub(r"\s+", "", str(v or "")).upper() or None


def cont_alta_firma(conn, schema, cont):
    """[lotul 12, deficiența C121 (găsită de pachetul migr): „extrasul altei firme intră fără întrebare”] Contul extrasului (MT940 `:25:`,
    IBAN-ul din antetul tabelului) față de contul bancar al firmei (Date firmă, IBAN). None când se potrivesc sau când unul din ele nu e
    cunoscut (nimic de comparat); altfel contradicția celor două conturi (`core/afirmatii.py`, cu ambele surse), cu `cod`, `mesaj`,
    `intrebare`, `cont_extras`, `cont_firma` pentru ecran — importul nu scrie nimic până nu confirmă contabilul (aceeași formă ca 599,
    firma din fișier la importurile de migrare)."""
    ce = _cont_norm(cont)
    with conn.cursor() as cur:
        cur.execute(f"SELECT iban FROM {schema}.firma_profil LIMIT 1")
        r = cur.fetchone()
    cf = _cont_norm(r[0] if r else None)
    if not ce or not cf or ce == cf:
        return None
    mesaj = ("Extrasul pare al altui cont: în el scrie contul %s, iar contul firmei (Date firmă) e %s. Verifică dacă ai încărcat "
             "extrasul firmei potrivite; liniile intră numai după ce confirmi." % (ce, cf))
    return _af.afirmatie("contradictie", "cont_extras", mesaj, sursele=["extrasul: contul %s" % ce, "Date firmă: IBAN %s" % cf],
                         cod=COD_CONT_ALTA_FIRMA, cont_extras=ce, cont_firma=cf, mesaj=mesaj,
                         intrebare="Liniile extrasului contului %s intră la această firmă. Confirmi că e extrasul ei?" % ce)


COD_CONT_ALTA_FIRMA = "EXTRAS_ALT_CONT"


def importa_extras(conn, schema, tranzactii, fisier="", continut=None, cont=None, cont_confirmat=False):
    """Persistă liniile NOI ale extrasului + rulează matching-ul pe ele. Întoarce `{"linii": [noi], "deja": [găsite], "rezumat"}`.

    [16.10.2026, lotul 6 pct.1, 277 — PIVOT peste C5 (DECIZII „Lotul 6, comanda 1”)] Duplicatul e MIȘCAREA, nu fișierul:
    `cheie_miscare` (dată, sumă, sens, cont, referință, descriere). O linie e găsită deja numai dacă aceeași mișcare există în
    `extras_linii`, socotită cu multiplicitatea ei: două comisioane identice în același extras rămân două, iar la reimport amândouă
    se găsesc. Înainte, hash-ul fișierului întreg hotăra tot: un fișier cu aceiași octeți ca unul vechi era respins în întregime
    („Extras deja importat: 2 linii”, F1, 16.10 13:18), iar un extras care se suprapunea cu unul vechi îi dubla liniile.
    Importurile pe aceeași firmă se serializează (`pg_advisory_xact_lock`), ca un dublu-clic să nu insereze de două ori.
    `extras_import` rămâne registrul fișierelor (hash, nume, număr de linii), nu mai decide nimic.
    """
    import hashlib
    from core import repo_banca
    if not cont_confirmat:   # [C121] contul altei firme: nimic scris până la confirmarea contabilului
        alt = cont_alta_firma(conn, schema, cont)
        if alt:
            return {"linii": [], "deja": [], "cere_confirmare": alt,
                    "rezumat": {"total": len(tranzactii), "noi": 0, "deja": 0, "potrivite": 0, "fara_potrivire": 0}}
    linii = [{"suma": Decimal(str(abs(t.get("suma", 0)))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
              "tip": "incasare" if t.get("suma", 0) > 0 else "plata",
              "cui": t.get("cui"), "descriere": t.get("detalii", ""),
              "referinta": (t.get("referinta") or "").strip() or None,
              "data": _data_iso(t.get("data"))} for t in tranzactii]
    rezumat = {"total": len(tranzactii), "noi": 0, "deja": 0, "potrivite": 0, "fara_potrivire": 0}
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", ("extras_import:" + schema,))
        cur.execute(f"SELECT id, data, suma, tip, cont_extras, referinta, descriere, fisier_sursa FROM {schema}.extras_linii "
                    f"WHERE data = ANY(%s::date[]) ORDER BY id", (sorted({str(ln["data"]) for ln in linii}),))
        vechi = [{"id": r[0], "data": r[1], "suma": r[2], "tip": r[3], "cont": r[4], "fisier_sursa": r[7],
                  "cheie": cheie_miscare(*r[1:7])} for r in cur.fetchall()]
        folosite = set()   # liniile vechi găsite deja (o linie veche răspunde pentru o singură linie nouă: multiplicitatea)
        noi, deja = [], []
        for t, ln in zip(tranzactii, linii):
            k = cheie_miscare(ln["data"], ln["suma"], ln["tip"], cont, ln["referinta"], ln["descriere"])
            v = next((x for x in vechi if x["id"] not in folosite and x["cheie"] == k), None)
            if v is not None:
                folosite.add(v["id"])
                deja.append({"data": str(ln["data"]), "suma": str(ln["suma"]), "tip": ln["tip"], "descriere": ln["descriere"]})
            else:
                noi.append((t, ln))
        # [479] a doua trecere, după ce cheia întreagă și-a luat liniile: mișcarea venită din alt format (tabel <-> MT940) se adaugă
        # VIZIBIL, dar deoparte („Ignorată”, cu motivul și «readu»), fără potrivire și fără notă propusă — nici pierdută, nici dublată
        dubluri = {}
        for i, (t, ln) in enumerate(noi):
            v = next((x for x in vechi if x["id"] not in folosite
                      and probabil_aceeasi_miscare(dict(ln, cont=cont), x)), None)
            if v is not None:
                folosite.add(v["id"])
                dubluri[i] = v
        probabile = [noi[i] for i in sorted(dubluri)]
        noi = [x for i, x in enumerate(noi) if i not in dubluri]
        rezumat["noi"], rezumat["deja"] = len(noi), len(deja)
        if probabile:   # [479] numai când există (forma rezumatului de până azi rămâne aceeași pentru importurile fără dubluri)
            rezumat["probabil_deja"] = len(probabile)
        if continut is not None:
            h = hashlib.sha256(continut if isinstance(continut, bytes)
                               else str(continut).encode("utf-8")).hexdigest()
            repo_banca.inregistreaza_import(cur, schema, h, fisier, len(tranzactii))
        tranzactii = [t for t, _ln in noi]
        linii = [ln for _t, ln in noi]
        rezultate = _m.potriveste_extras(linii, facturi_deschise(conn, schema)) if linii else []
        out = []
        for t, ln, rez in zip(tranzactii, linii, rezultate):
            # [P8] `rez` E DEJA o afirmatie tipata (potriveste_linie); se duce mai departe intreaga,
            # nu se re-extrage `motiv` - altfel ar exista doua surse ale aceluiasi text.
            aloc = dict(rez, status_match=rez["status"],
                        alocari=[{"factura_id": a["factura_id"], "suma": str(a["suma"])}
                                 for a in rez["alocari"]])
            aloc.pop("status", None)
            # ai_sugestie_v1: linie fara facturi -> sugestie din istoricul invatat. [05.10.2026] Condiția veche cerea „fără
            # notă”, dar `banca.regula_cont` pune mereu una (client/furnizor PRESUPUS din sens) -> ramura nu rula niciodată.
            # Acum rulează când tipul NU s-a recunoscut din descriere; un tip recunoscut (comision, TVA…) rămâne al regulii.
            if rez["status"] == "rosu" and not t.get("tip_detectat"):
                try:
                    from core import ai_incredere as _ai
                    sug = _ai.sugestie(conn, schema, ln.get("descriere") or "")
                    # [479] o sugestie pe contul de trezorerie ar da nota 5121 = 5121: nu se propune (`ai_incredere.sugestie` le sare deja)
                    if sug and not _ai.e_trezorerie(sug["cont"]):
                        cont_banca = _cont_banca(t.get("valuta"))
                        if ln["tip"] == "plata":
                            t["nota"] = {"debit": sug["cont"], "credit": cont_banca}
                        else:
                            t["nota"] = {"debit": cont_banca, "credit": sug["cont"]}
                        aloc["incredere"] = sug["incredere"]
                        aloc["motiv"] = aloc["motiv"] + f"; sugestie învățată: {sug['cont']} ({sug['incredere']}, {_cate(sug['validari'], 'validare', 'validări')})"
                except Exception as _e:
                    from core import observare as _obs
                    _obs.esec_secundar("sugestie invatata la importul extrasului", _e)   # înghițit, dar nu tăcut
            status = "potrivit" if rez["status"] in ("verde", "galben") else "nou"
            rezumat["potrivite" if status == "potrivit" else "fara_potrivire"] += 1
            cur.execute(f"""
                INSERT INTO {schema}.extras_linii
                  (data, descriere, suma, valuta, tip, cui_detectat, status,
                   alocari, nota_propusa, fisier_sursa, cont_extras, referinta)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            """, (ln["data"], ln["descriere"], ln["suma"], bool(t.get("valuta")),
                  ln["tip"], ln["cui"], status, json.dumps(aloc),
                  json.dumps(t.get("nota"), default=str) if t.get("nota") else None, fisier,
                  (cont or "").strip() or None, ln["referinta"]))
            # [lotul 12, găsit la 479] câmpurile liniei DUPĂ afirmația potrivirii: afirmația are și ea o cheie „tip” („reconciliere extras”),
            # care suprascria sensul liniei (încasare / plată) în răspunsul importului
            out.append({**aloc, "id": cur.fetchone()[0], "data": str(ln["data"]),
                        "descriere": ln["descriere"], "suma": str(ln["suma"]),
                        "tip": ln["tip"], "cui": ln["cui"], "status": status})
        puse_deoparte = []
        for i in sorted(dubluri):
            t, ln = probabile.pop(0)
            v = dubluri[i]
            # afirmația potrivirii, ca la liniile de mai sus (`reconciliere.potriveste_linie`): aici, linia pare una importată deja
            aloc = dict(_af.afirmatie("fapt", "reconciliere extras", motiv_dublura(v),
                                      unde=_Unde("linie_extras", v["id"], "importată deja, suma %s" % ln["suma"]),
                                      temei_completitudine="liniile extraselor importate în aceeași zi, cu aceeași sumă și același "
                                                           "sens, iar contul băncii cunoscut pe exact una din ele"),   # `probabil_aceeasi_miscare`
                        status_match="rosu", alocari=[], dublura_de=v["id"])
            cur.execute(f"""
                INSERT INTO {schema}.extras_linii
                  (data, descriere, suma, valuta, tip, cui_detectat, status,
                   alocari, nota_propusa, fisier_sursa, cont_extras, referinta)
                VALUES (%s,%s,%s,%s,%s,%s,'ignorat',%s,NULL,%s,%s,%s) RETURNING id
            """, (ln["data"], ln["descriere"], ln["suma"], bool(t.get("valuta")), ln["tip"], ln["cui"], json.dumps(aloc), fisier,
                  (cont or "").strip() or None, ln["referinta"]))
            puse_deoparte.append({"id": cur.fetchone()[0], "data": str(ln["data"]), "suma": str(ln["suma"]), "tip": ln["tip"],
                                  "descriere": ln["descriere"], "dublura_de": v["id"]})
    return {"linii": out, "deja": deja, "probabil_deja": puse_deoparte, "rezumat": rezumat}


def compara_solduri(conn, schema, sold_initial, sold_final):
    """[16.10.2026, lotul 6 pct.2b, 276] Soldurile din extras (MT940 `:60F:` / `:62F:`) față de contul băncii din contabilitate (5121, la
    valută 5124, cu analiticele) la aceeași zi: soldul de preluare + notele VALIDATE până la acea zi (`bilant_api.sold_la`). Liniile
    extrasului încă necontate apar ca diferență la soldul final — de-aia se arată amândouă. `None` la extrasele fără solduri (tabele).
    Contabilul vede `contabil = None` dacă ziua e dinaintea soldurilor de preluare (aplicația nu știe soldul de atunci)."""
    import datetime
    from psycopg2.extras import RealDictCursor as _RD
    from core import bilant_api as _ba
    if not (sold_initial or sold_final):
        return None
    valuta = (sold_initial or sold_final).get("valuta") or "RON"
    cont = _cont_banca(valuta != "RON")
    out = {"cont": cont, "valuta": valuta}
    with conn.cursor(cursor_factory=_RD) as cur:
        for nume, s in (("initial", sold_initial), ("final", sold_final)):
            if not s:
                out[nume] = None
                continue
            sl = _ba.sold_la(cur, schema, datetime.date.fromisoformat(s["data"]))
            contabil = (None if sl is None else
                        sum((d - c for k, (d, c) in sl.items() if k == cont or k.startswith(cont + ".")), Decimal("0")))
            extras = Decimal(str(s["suma"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            out[nume] = {"data": s["data"], "extras": str(extras), "contabil": None if contabil is None else str(contabil),
                         "diferenta": None if contabil is None else str(extras - contabil)}
    return out


#: [deficiența 309] motivele scrise la importul extrasului înainte de 7d718193 (engleză, fără diacritice) stau în `extras_linii.alocari`;
#: se spun ca acum, la citire — linia importată atunci nu se reimportă
_MOTIVE_VECHI = (("match exact pe o factura", "potrivire exactă pe o factură"), ("match exact pe ", "potrivire exactă pe "),
                 ("alocare partiala FIFO", "alocare parțială, pe facturile cele mai vechi întâi"), ("sugestie invatata", "sugestie învățată"))


def motiv_pe_romaneste(motiv):
    for vechi, nou in _MOTIVE_VECHI:
        motiv = motiv.replace(vechi, nou)
    return motiv


def stare_note_linie(ids, stari, coada):
    """PURĂ. [lotul 11, deficiența 457] Starea notelor unei linii contate, în forma rândului de Casă (`nota_status`, `stare_coada`,
    `motiv_respingere` — câmpurile pe care ecranul le citește cu o singură funcție, `stareNotaCasa`): `stari` = {id: status din Registrul
    jurnal}, `coada` = `coada_api.stari_note`. Toate validate -> `validata`; altfel `ciorna`, iar coada se spune NUMAI cum e: o notă
    respinsă -> `respinsa` (cu motivul); `la_senior` numai dacă TOATE nevalidatele sunt în coadă; altfel fără stare de coadă (ciornă
    netrimisă). None când linia n-are note."""
    ids = [i for i in ids or [] if i in stari]
    if not ids:
        return None
    nev = [i for i in ids if stari[i] != "validata"]
    if not nev:
        return {"nota_status": "validata", "stare_coada": None, "motiv_respingere": None, "nevalidate": 0}
    sc = [(coada.get(i) or {}).get("stare_coada") for i in nev]
    resp = [coada[i] for i in nev if (coada.get(i) or {}).get("stare_coada") == "respinsa"]
    st = "respinsa" if resp else ("la_senior" if all(s == "la_senior" for s in sc) else None)
    return {"nota_status": "ciorna", "stare_coada": st, "motiv_respingere": resp[0].get("motiv_respingere") if resp else None,
            "nevalidate": len(nev)}


def lista(conn, schema, status=None):
    """Liniile de extras cu detaliile facturilor alocate (pentru UI)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q = f"SELECT * FROM {schema}.extras_linii"
        # [05.10.2026, comanda Costin pct.8] liniile noi ale extrasului apar primele, nu sub cele vechi
        ordine = " ORDER BY creat_la DESC, data DESC, id DESC"
        if status:
            cur.execute(q + " WHERE status=%s" + ordine, (status,))
        else:
            cur.execute(q + ordine)
        linii = cur.fetchall()
        ids = set()
        for l in linii:
            for a in (l.get("alocari") or {}).get("alocari", []):
                ids.add(a["factura_id"])
        facturi = {}
        if ids:
            cur.execute(f"""SELECT id, numar, serie, data_emitere, tert_nume, tert_cui,
                            COALESCE(total_lei, total) AS total
                            FROM {schema}.facturi WHERE id = ANY(%s)""", (list(ids),))
            facturi = {f["id"]: f for f in cur.fetchall()}
        # [deficiența 309, comanda Costin 17.10.2026 7.2] „linia contată arată «Contat ✓» cât nota e încă la validare”: starea notelor
        # liniei (`alocari.inregistrari_ids`) se citește aici; ecranul nu spune „Contat ✓” până la validare
        note_ids = {i for l in linii for i in ((l.get("alocari") or {}).get("inregistrari_ids") or [])}
        stari, coada = {}, {}
        if note_ids:
            cur.execute(f"SELECT id, status FROM {schema}.inregistrari WHERE id = ANY(%s)", (list(note_ids),))
            stari = {r["id"]: r["status"] for r in cur.fetchall()}
            # [lotul 11, deficiența 457] „după contarea din bancă, rândul spune «la validare» deși nota e ciornă”: o notă nevalidată nu e
            # neapărat în coada de validare (nota scrisă de cine validează rămâne ciornă, n-o trimite nimeni). Starea din coadă se citește
            # (`coada_api.stari_note`, aceeași sursă ca Registrul jurnal și Casa), nu se presupune din „nevalidată”.
            from core import coada_api as _coada
            cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (str(schema).strip('"'),))
            t = cur.fetchone()
            coada = _coada.stari_note(conn, t["id"], list(note_ids)) if t else {}
        for l in linii:
            l["suma"] = str(l["suma"])
            l["data"] = str(l["data"])
            l["creat_la"] = str(l["creat_la"])
            ids_l = (l.get("alocari") or {}).get("inregistrari_ids") or []
            l["note_de_validat"] = sum(1 for i in ids_l if stari.get(i) not in (None, "validata"))
            l["nota_stare"] = stare_note_linie(ids_l, stari, coada)
            al = l.get("alocari") or {}
            if al.get("motiv"):
                al["motiv"] = motiv_pe_romaneste(al["motiv"])
            for a in (l.get("alocari") or {}).get("alocari", []):
                f = facturi.get(a["factura_id"])
                if f:
                    a["factura"] = {"numar": f["numar"], "serie": f["serie"],
                                    "data": str(f["data_emitere"]),
                                    "tert": f["tert_nume"], "total": str(f["total"])}
        return linii


def conteaza(conn, schema, linie_id, alocari=None):
    """Contează o linie: câte o înregistrare per factură alocată.
    incasare: 5121/5124 = 4111; plata: 401 = 5121/5124.
    alocari=None → folosește alocările din matching."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.extras_linii WHERE id=%s", (linie_id,))
        l = cur.fetchone()
        if not l:
            return None
        if l["status"] == "contat":
            return {"eroare": "linia e deja contată"}
        aloc = alocari or (l.get("alocari") or {}).get("alocari", [])
        # [05.10.2026, comanda Costin pct.6] fiecare notă din extras poartă extrasul ca document justificativ
        from core import pdf_util as _pu
        doc = ("Extras bancar %s din %s" % (l["fisier_sursa"], _pu.data_ro(l["data"])) if l.get("fisier_sursa")
               else "Extras bancar din %s" % _pu.data_ro(l["data"]))
        if not aloc:
            np = l.get("nota_propusa") or {}
            if not (np.get("debit") and np.get("credit")):
                return {"eroare": "fără alocări și fără notă propusă; alege facturile"}
            if str(np["debit"]).split(".")[0] == str(np["credit"]).split(".")[0]:
                # [479] o notă cu același cont pe debit și pe credit nu mișcă nimic (propusă înainte de reparație: 5121 = 5121)
                return {"eroare": "Nota propusă are același cont pe debit și pe credit (%s = %s): nu înregistrează nimic. Alege facturile "
                                  "sau scrie nota în Registru jurnal." % (np["debit"], np["credit"])}
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                VALUES (%s,%s,'banca','ciorna',%s) RETURNING id
            """, (l["data"], (l["descriere"] or "")[:200] or "operatiune bancara", doc))
            iid = cur.fetchone()["id"]
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                VALUES (%s,%s,%s,%s)
            """, (iid, np["debit"], np["credit"], Decimal(str(np.get("suma") or l["suma"]))))
            cur.execute(f"UPDATE {schema}.extras_linii SET status='contat', alocari=%s WHERE id=%s",
                        (json.dumps({**(l.get("alocari") or {}), "inregistrari_ids": [iid]}), linie_id))
            # [05.10.2026, comanda Costin pct.8] se OPREȘTE aici. Înainte cădea în ramura alocărilor: fără alocări nu
            # scria nimic, rescria `inregistrari_ids` cu [] (legătura notei pierdută) și răspundea cu nota din tipul
            # liniei („Nota 401=5121 — 0 înregistrări create”) deși se crease 627=5121.
            return {"inregistrari": [iid], "nota": "%s=%s" % (np["debit"], np["credit"])}
        banca = _cont_banca(l["valuta"])
        debit, credit = (banca, CONT_CLIENTI) if l["tip"] == "incasare" else (CONT_FURNIZORI, banca)
        create = []
        for a in aloc:
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, factura_id, descriere, sursa, status, document_ref)
                VALUES (%s,%s,%s,'banca','ciorna',%s) RETURNING id
            """, (l["data"], a["factura_id"],
                  (l["descriere"] or "")[:200] or "operatiune bancara", doc))
            iid = cur.fetchone()["id"]
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                VALUES (%s,%s,%s,%s)
            """, (iid, debit, credit, Decimal(str(a["suma"]))))
            # [lotul 10, deficiența 428] TVA la încasare: partea încasată / plătită trece 4428 -> 4427 (emisă, CF art.282 alin.(3), (8)) /
            # 4428 -> 4426 (primită, CF art.297 alin.(2)-(3)), pe regimul FACTURII la data ei — punctul unic, același cu casa. Înainte:
            # bifa firmei de azi, cota primei linii (o factură cu două cote ieșea greșit) și nimic pentru furnizorul în sistem.
            from core import tva_incasare as _tv
            for _deb, _cred, _tva in _tv.linii_la_incasare(cur, schema, a["factura_id"], a["suma"]):
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, _deb, _cred, _tva))
            create.append(iid)
        cur.execute(f"UPDATE {schema}.extras_linii SET status='contat', alocari=%s WHERE id=%s",
                    (json.dumps({**(l.get("alocari") or {}),
                                 "alocari": [{"factura_id": a["factura_id"], "suma": str(a["suma"])}
                                             for a in aloc],
                                 "inregistrari_ids": create}), linie_id))
    return {"inregistrari": create, "nota": f"{debit}={credit}"}


def facturi_deschise_detalii(conn, schema):
    """Facturile deschise cu detalii pentru picker-ul din UI."""
    fd = facturi_deschise(conn, schema)
    if not fd:
        return []
    ids = [f["id"] for f in fd]
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, numar, serie, tert_nume, tip FROM {schema}.facturi WHERE id=ANY(%s)", (ids,))
        det = {r["id"]: r for r in cur.fetchall()}
    # [lotul 13, 669] `preluata`: soldul pe partener preluat la migrare („Sold la <data>”), stins ca o factură (Casă, Bancă, Compensări)
    from core import nomenclator_status_factura as _nsf
    return [{"id": f["id"], "tert_cui": f["tert_cui"], "directie": f["directie"],
             "data_emitere": str(f["data_emitere"]), "sold": str(f["sold"]),
             "numar": det[f["id"]]["numar"], "serie": det[f["id"]]["serie"],
             "tert_nume": det[f["id"]]["tert_nume"], "preluata": det[f["id"]]["tip"] == _nsf.TIP_SOLD_PRELUAT} for f in fd]
