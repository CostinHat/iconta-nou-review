# -*- coding: utf-8 -*-
"""Jurnal — editare/ștergere/validare note. Doar ciornele se pot modifica:

AI propune (ciorna), contabilul validează."""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from decimal import Decimal
from psycopg2.extras import RealDictCursor

from core import contare_facturi as _cf
from core.common import Temei


def _nota(cur, schema, nota_id):
    cur.execute(f"SELECT * FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
    return cur.fetchone()


def _centru(l):
    """[F143] centru_cost_id de pe o linie -> int sau None (nealocat). Gol/0 = nealocat."""
    v = l.get("centru_cost_id")
    if v in (None, "", 0, "0"):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


#: Temeiurile refuzurilor din calea jurnalului. Pana la 31.08.2026, toate cele 12 refuzuri ale
#: acestei cai erau propozitii fara autor: spuneau CE lipseste, nu SUB CE NORMA. Interdictia 77 pe
#: cea mai folosita cale de scriere a aplicatiei.
TEMEI_PARTIDA_DUBLA = Temei(
    "Lege", 82, 1991, art="5", alin="1",
    data_in="1992-01-01", verificat_la="2026-08-31", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/legea_82_1991_consolidat.txt",
    text_citat=("Persoanele prevazute la art. 1 alin. (1)-(4) au obligatia sa conduca contabilitatea "
                "in partida dubla si sa intocmeasca situatii financiare anuale, potrivit "
                "reglementarilor contabile aplicabile"))

TEMEI_CONSEMNARE = Temei(
    "Lege", 82, 1991, art="6", alin="1",
    data_in="1992-01-01", verificat_la="2026-08-31", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/legea_82_1991_consolidat.txt",
    text_citat=("Orice operatiune economico-financiara efectuata se consemneaza in momentul "
                "efectuarii ei intr-un document care sta la baza inregistrarilor in contabilitate, "
                "dobandind astfel calitatea de document justificativ"))


def _refuz(mesaj, temei, camp=None, linia=None):
    """Refuzul, ca AFIRMATIE TIPATA — `neconformitate`: o VALOARE nu satisface o REGULA.

    `regula` e obligatorie la felul asta, si aici e chiar temeiul: refuzul spune sub ce norma. Iar
    `linia` calatoreste ca DATA, nu ingropata in propozitie — o garda care ar cauta «linia 2» in
    mesaj ar intreba un sir (clichetul 50).
    """
    from core.afirmatii import afirmatie
    from core.unde import Unde
    a = afirmatie(
        "neconformitate", tip="nota_contabila",
        motiv=mesaj, regula=str(temei),
        unde=Unde("inregistrare", linia if linia is not None else "nouă"),
        **{"eroare": mesaj, "temei": str(temei), "camp": camp, "linia": linia})
    return dict(a)


def _data_valida(data):
    """`(data, refuz)` — data notei, sau refuzul cu temeiul ei.

    Pana azi, o data lipsa sau in alt format iesea **500**, fara niciun mesaj: exceptia din driverul
    de baza nu era prinsa nicaieri. Un 500 nu e un refuz — nu spune nimic omului si nu poate purta
    temei. E chiar forma pe care interdictia 77 o exclude.
    """
    import datetime
    s = str(data or "").strip()
    if not s:
        return None, _refuz(
            "nota are nevoie de data operatiunii: fiecare operatiune se consemneaza in momentul "
            "efectuarii ei", TEMEI_CONSEMNARE, camp="data")
    try:
        return datetime.date.fromisoformat(s), None
    except ValueError:
        return None, _refuz(
            "data %r nu e in formatul AAAA-LL-ZZ. Se cere o data calendaristica, fiindca "
            "inregistrarea se face la momentul operatiunii, iar ordinea cronologica a "
            "registrului-jurnal atarna de ea" % s, TEMEI_CONSEMNARE, camp="data")


def _linii_valide(conn, schema, linii):
    """`refuz sau None` — forma liniilor SI conturile, confruntate cu planul firmei.

    Confruntarea cu planul lipsea de pe calea asta, iar `9999` intra in evidenta. R54 o declarase
    facuta „pe toate rutele care scriu in evidenta cu un cont venit de la om" — dar domeniul ei
    recunoaste citirile dupa NUMELE cheii (`cont`, `cont_*`), iar aici cheile se numesc `debit` si
    `credit`. N-a fost niciodata in domeniu, deci nici in cele 8 declarate NELEGATE.
    """
    from core import cont_valid as _cv
    if not linii:
        return _refuz("nota trebuie sa aiba cel putin o linie: o inregistrare in partida dubla are "
                      "cel putin un cont debitor si unul creditor", TEMEI_PARTIDA_DUBLA)
    for i, l in enumerate(linii, 1):
        for cheie, eticheta in (("debit", "contul debitor"), ("credit", "contul creditor")):
            if not str(l.get(cheie, "")).strip():
                return _refuz(
                    "linia %d n-are %s. Partida dubla cere ambele conturi pe fiecare inregistrare"
                    % (i, eticheta), TEMEI_PARTIDA_DUBLA, camp=cheie, linia=i)
            try:
                _cv.cere_cont(conn, schema, l[cheie], "%s (linia %d)" % (eticheta, i))
            except _cv.ContNecunoscut as e:
                # [R163, 05.09.2026] Propozitia despre cont se ia de la `cont_valid.randeaza`,
                # singurul loc unde se compune (o spune chiar docstringul ei). Aici se
                # recompunea de mana, iar `apropiate` — lista de PERECHI `(cod, denumire)` —
                # intra intr-un `", ".join(...)` care astepta siruri: `TypeError`, deci **500**.
                # Se vedea NUMAI pe un cont plauzibil: pentru o santinela fara vecini in plan
                # lista iese goala si ramura nici nu se executa. De-aia etapa 1, care apasa cu
                # `«»@#$%%`, a primit de aici un mesaj bun — iar etapa 2, cu `7015`, un 500.
                d = e.detalii if hasattr(e, "detalii") else {}
                return _refuz(
                    "linia %d: %s Iar o nota cu un cont inexistent nu e evidenta, e un rand "
                    "care arata ca evidenta"
                    % (i, _cv.randeaza(d) if d else str(e)),
                    TEMEI_PARTIDA_DUBLA, camp=cheie, linia=i)
        if Decimal(str(l.get("suma", 0))) <= 0:
            return _refuz("linia %d are suma %s: o inregistrare consemneaza o operatiune efectuata, "
                          "deci suma ei e strict pozitiva" % (i, l.get("suma")),
                          TEMEI_CONSEMNARE, camp="suma", linia=i)
        # [deficiența 381, comanda Costin 8.2, 18.10.2026: „Nota pe 401/4111 cere partenerul la introducere”] o datorie / creanță se ține
        # pe fiecare partener (D406, nota la GL.28/GL.29: „în câmpurile SupplierID, respectiv CustomerID se va completa codul [...]”)
        tert = next((str(l.get(k) or "").strip() for k in ("debit", "credit") if _cont_tert(l.get(k))), None)
        if tert and not str(l.get("partener_nume") or "").strip() and not str(l.get("partener_cui") or "").strip():
            return _refuz("linia %d e pe contul %s (%s): scrie partenerul — numele și, dacă are, codul fiscal. Fără el, datoria / creanța "
                          "nu se poate urmări pe partener, iar D406 n-ar ști cui i-ai plătit sau de la cine ai încasat"
                          % (i, tert, "furnizori" if tert.startswith("401") else "clienți"), TEMEI_CONSEMNARE, camp="partener_nume", linia=i)
        cifre = "".join(ch for ch in str(l.get("partener_cui") or "") if ch.isdigit())
        if cifre and len(cifre) != 13:   # 13 cifre = CNP (partener persoană fizică), nu CUI
            from core import identitate as _id
            ok, motiv = _id.valideaza_cui(cifre)
            if not ok:
                return _refuz("linia %d: codul fiscal al partenerului (%s) nu e valid — %s" % (i, l.get("partener_cui"), motiv),
                              TEMEI_CONSEMNARE, camp="partener_cui", linia=i)
    return None


#: [381] conturile de terți (sintetic de gradul I/II) pe care nota manuală cere partenerul: furnizori și clienți
CONTURI_TERT = ("401", "4111")


def _cont_tert(cont):
    """Contul e de furnizori / clienți: 401 sau 4111, cu sau fără analitic („401.00012”)."""
    return str(cont or "").strip().split(".")[0] in CONTURI_TERT


def _partener(l):
    """(cui, nume) al liniei, curățate; (None, None) dacă lipsesc."""
    return ((str(l.get("partener_cui") or "").strip() or None), (str(l.get("partener_nume") or "").strip()[:200] or None))


def _av_plan(conn, schema, linii, out):
    """[08.10.2026, decizia Costin V3] Avertismentul pentru conturile din afara planului legal al normei firmei (`plan_legal`)."""
    from core import plan_legal as _pl
    with conn.cursor() as cur:
        av = _pl.avertisment(cur, schema, [str(l.get(k) or "").strip() for l in (linii or []) for k in ("debit", "credit")])
    if av:
        out["avertisment"] = av
    return out


def creeaza(conn, schema, descriere, data, linii, document_ref=None):
    """Creeaza o nota manuala noua, ca ciorna. linii = [{debit, credit, suma}], min 1 linie.
    `document_ref` = documentul justificativ scris de om (Registrul-jurnal col.3); gol -> se derivă sau rămâne lipsă vizibilă."""
    data, rd = _data_valida(data)
    if rd:
        return rd
    rl = _linii_valide(conn, schema, linii)
    if rl:
        return rl
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                        VALUES (%s,%s,'manual','ciorna',%s) RETURNING id""",
                    (data, (descriere or "")[:200], (str(document_ref or "").strip() or None)))
        nota_id = cur.fetchone()["id"]
        for l in linii:
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                (inregistrare_id, cont_debit, cont_credit, suma, centru_cost_id, partener_cui, partener_nume)
                VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (nota_id, str(l["debit"]).strip(), str(l["credit"]).strip(),
                 Decimal(str(l["suma"])), _centru(l), *_partener(l)))
        # [DDD3] LA SURSĂ: dacă nota contează evident o factură, primește `factura_id` ACUM.
        # Gaura măsurată la BBB era că o notă din calea liberă nu poartă cheia, deci e invizibilă
        # pentru anti-dublare. Plasa (`candidate_fara_cheie`) rămâne plasă tocmai fiindcă legătura
        # se face aici, la scriere — nu invers.
        legata = _cf.leaga_nota_de_factura(
            cur, schema, nota_id,
            [(str(l["debit"]).strip(), str(l["credit"]).strip(), Decimal(str(l["suma"])))
             for l in linii], data)
    out = {"ok": True, "id": nota_id}
    if legata:
        out["factura_id"] = legata
        from core import eticheta_nota as _et   # [deficiența 258] factura cum o vede omul, nu id-ul ei
        with conn.cursor() as cur:
            out["mesaj"] = ("nota a fost legată de %s — o singură factură a lunii se "
                            "potrivește pe sumă" % _et.factura(cur, schema, legata))
    _av_plan(conn, schema, linii, out)   # [08.10, V3] „nu se poate … folosi fără avertisment”
    return out
def editeaza(conn, schema, nota_id, descriere=None, data=None, linii=None, document_ref=None):
    """Editează o notă ciornă. linii = [{debit, credit, suma}] înlocuiește complet liniile.
    `document_ref`: None = neschimbat; șir gol = șters (nota rămâne fără document, iar validarea o va spune)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        n = _nota(cur, schema, nota_id)
        if not n:
            return None
        if n["status"] != "ciorna":
            return {"eroare": "doar ciornele se pot edita"}
        from core import coada_api as _coada   # [lotul 07.10 pct.6] nota la validare nu se schimbă sub ochii cabinetului
        if _coada.nota_la_validare(cur, schema, nota_id):
            return {"eroare": _coada.mesaj_nota_la_validare(cur, schema, nota_id), "cod": _coada.COD_NOTA_LA_VALIDARE}
        # [lotul 07.10 B, C9, decizia Costin] nota derivată dintr-un document se corectează numai din documentul-sursă
        from core import note_derivate as _nd
        doc = _nd.documentul_sursa(cur, schema, nota_id)
        if doc:
            return {"eroare": _nd.mesaj_refuz(nota_id, doc), "cod": _nd.COD, "document": doc[0]}
        if data is not None:
            data, rd = _data_valida(data)
            if rd:
                return rd
        if linii is not None:
            rl = _linii_valide(conn, schema, linii)
            if rl:
                return rl
            # ai_corectie_v1: memoreaza contul debit dinainte de edit (propunerea AI)
            cur.execute(f"""SELECT cont_debit FROM {schema}.inregistrari_linii
                            WHERE inregistrare_id=%s ORDER BY id LIMIT 1""", (nota_id,))
            _vechi = cur.fetchone()
            _cont_vechi = (_vechi["cont_debit"] if isinstance(_vechi, dict) else _vechi[0]) if _vechi else None
            cur.execute(f"DELETE FROM {schema}.inregistrari_linii WHERE inregistrare_id=%s", (nota_id,))
            for l in linii:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                    (inregistrare_id, cont_debit, cont_credit, suma, centru_cost_id, partener_cui, partener_nume)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (nota_id, str(l["debit"]).strip(), str(l["credit"]).strip(),
                     Decimal(str(l["suma"])), _centru(l), *_partener(l)))
            # ai_corectie_v2: cont schimbat de contabil => corectie invatata
            try:
                _cont_nou = str(linii[0]["debit"]).strip()
                if _cont_vechi and _cont_nou and _cont_vechi != _cont_nou and n.get("descriere"):
                    from core import ai_incredere as _ai
                    _ctx = _ai.normalizeaza(n["descriere"])
                    if _ctx:
                        cur.execute(f"""INSERT INTO {schema}.ai_corectii
                                        (context, cont_propus, cont_final, corectat)
                                        VALUES (%s,%s,%s,true)""", (_ctx, _cont_vechi, _cont_nou))
            except Exception as _e:
                from core import observare as _obs
                _obs.esec_secundar("invatare AI la editare nota", _e)  # inghitit, dar nu tacut (27.07.2026)
        seturi, valori = [], []
        if descriere is not None:
            seturi.append("descriere=%s"); valori.append(descriere)
        if data is not None:
            seturi.append("data=%s"); valori.append(data)
        if document_ref is not None:
            seturi.append("document_ref=%s"); valori.append(str(document_ref).strip() or None)
        if seturi:
            cur.execute(f"UPDATE {schema}.inregistrari SET {', '.join(seturi)} WHERE id=%s",
                        (*valori, nota_id))
    return _av_plan(conn, schema, linii, {"ok": True}) if linii is not None else {"ok": True}   # [08.10, V3]


def sterge(conn, schema, nota_id):
    """Șterge o notă ciornă (liniile cad prin ON DELETE CASCADE)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        n = _nota(cur, schema, nota_id)
        if not n:
            return None
        if n["status"] != "ciorna":
            return {"eroare": "doar ciornele se pot șterge"}
        from core import coada_api as _coada   # [lotul 07.10 pct.6]
        if _coada.nota_la_validare(cur, schema, nota_id):
            return {"eroare": _coada.mesaj_nota_la_validare(cur, schema, nota_id), "cod": _coada.COD_NOTA_LA_VALIDARE}
        # [lotul 07.10 B, C9] o notă derivată nu se șterge din jurnal acolo unde ALT tabel o indică (mișcarea de stoc, NIR-ul,
        # chitanța, raportul Z, amortizarea). [328, 18.10.2026] Nici nota statului, nici contarea facturii emise: documentul rămâne, iar
        # nota se corectează din el (`note_derivate.se_sterge`). Se șterg (ciornă) contarea facturii-ciornă (drumul ștergerii ei) și cele
        # care își desfac sursa aici (operațiunea de casă, linia de extras redevine „potrivită”). Editarea rămâne blocată pentru toate.
        from core import note_derivate as _nd
        doc = _nd.documentul_sursa(cur, schema, nota_id)
        if doc and not _nd.se_sterge(cur, schema, doc, nota_id):
            return {"eroare": _nd.mesaj_refuz(nota_id, doc), "cod": _nd.COD, "document": doc[0]}
        cur.execute(f"DELETE FROM {schema}.casa_operatiuni WHERE inregistrare_id=%s", (nota_id,))
        cur.execute(f"""UPDATE {schema}.extras_linii SET status='potrivit'
                        WHERE status='contat'
                          AND alocari->'inregistrari_ids' @> %s::jsonb""", (str(nota_id),))
        cur.execute(f"DELETE FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
    return {"ok": True}


def valideaza(conn, schema, nota_id):
    """Ciorna -> validata (aprobarea contabilului)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        n = _nota(cur, schema, nota_id)
        if not n:
            return None
        if n["status"] != "ciorna":
            return {"eroare": "nota nu e ciorna"}
        cur.execute(f"SELECT COUNT(*) AS c FROM {schema}.inregistrari_linii WHERE inregistrare_id=%s",
                    (nota_id,))
        if cur.fetchone()["c"] == 0:
            return {"eroare": "nota nu are linii"}
        # [retest 07.10 R1] nota unui document respins, cu stocul stornat, nu mai intră în evidență pe niciun drum (unicul drum
        # de validare e acesta: jurnalul și coada) — altfel nota ar fi validată, iar marfa ei n-ar mai fi în fișă
        from core import stocuri_anulare as _sa
        _st = _sa.document_stornat(cur, schema, nota_id)
        if _st:   # OMFP 1802/2014 pct.69: stornarea operațiunii — nota ei nu mai are ce înregistra
            return {**_refuz(_sa.MESAJ_NOTA_STORNATA % _st, "OMFP 1802/2014 pct.69"), "cod": _sa.COD_DOCUMENT_STORNAT}
        # [decizii 07.10 pct.3] raportul Z la cantitativ-valoric nu se validează fără descărcarea pe articol (sau „fără marfă”)
        from core import z_descarcare as _zd
        _z = _zd.refuz_validare(cur, schema, nota_id)
        if _z:
            return {**_refuz(_z, "OMFP 1802/2014 pct.287 alin.(1)-(2)"), "cod": _zd.COD_NEDESCARCAT}
        # [deficiența 243] nota de închidere: numai după 31.12 și numai cât e încă a soldurilor validate de acum
        from core import inchidere_an as _ia
        _i = _ia.refuz_validare(cur, schema, nota_id)
        if _i:
            return {**_refuz(_i, "OMFP 1802/2014, contul 121"), "cod": "INCHIDERE_NEVALIDABILA"}
        # [deficiența 406, PRIORITAR] nota care scoate bani din casă nu se validează dacă evidența validată ar arăta casa sub zero (în ziua
        # notei sau după) — orice drum de scriere (dispoziție, notă manuală, import, stornare) trece pe aici
        from core import casa_sold as _cs
        cur.execute(f"SELECT cont_debit, cont_credit, suma FROM {schema}.inregistrari_linii WHERE inregistrare_id=%s", (nota_id,))
        _var = {}
        for _l in cur.fetchall():
            for _c, _s in ((_cs.sintetic_casa(_l["cont_debit"]), 1), (_cs.sintetic_casa(_l["cont_credit"]), -1)):
                if _c:
                    _var[_c] = _var.get(_c, Decimal(0)) + _s * Decimal(str(_l["suma"]))
        for _c in sorted(_var):
            _r = _cs.refuz_iesire(cur, schema, _c, n["data"], -_var[_c], doar_validate=True, ce="Nota")
            if _r:
                return {**_refuz(_r, _cs.TEMEI), "cod": _cs.COD}
        cur.execute(f"UPDATE {schema}.inregistrari SET status='validata' WHERE id=%s", (nota_id,))
        # ai_invatare_v1: invatare din validare (context = descriere, cont = debitul primei linii)
        try:
            cur.execute(f"""SELECT cont_debit FROM {schema}.inregistrari_linii
                            WHERE inregistrare_id=%s ORDER BY id LIMIT 1""", (nota_id,))
            ld = cur.fetchone()
            if ld and n.get("descriere"):
                from core import ai_incredere as _ai
                ctx_t = _ai.normalizeaza(n["descriere"])
                cont_f = ld["cont_debit"] if isinstance(ld, dict) else ld[0]
                if ctx_t and cont_f:
                    cur.execute(f"""INSERT INTO {schema}.ai_corectii
                                    (context, cont_propus, cont_final, corectat)
                                    VALUES (%s,%s,%s,false)""", (ctx_t, cont_f, cont_f))
        except Exception as _e:
            from core import observare as _obs
            _obs.esec_secundar("invatare AI la validare nota", _e)  # inghitit, dar nu tacut (27.07.2026)
    return {"ok": True}


# ── [deficiența 368, decizia Costin 19.10.2026 „Se validează automat”, verbatim în DECIZII „Închiderea lotului 9”] ──────────────────────
# „la PFA nota scrisă în fundal (Casă, Bancă, facturi, Z, salarii) se validează automat la scriere, ca «notă internă», cu documentul ei
# (regula R3); actul omului rămâne operațiunea din registrul de încasări și plăți.” La partidă simplă (OMFP 170/2015) nota nu e evidență:  # TEMEI LIBER: citat verbatim al deciziei
# poartă TVA-ul pe cote pentru D300 / D394, care le citesc NUMAI validate (`repo_d300.py`, `repo_d394.py`).

#: etichetele refuzurilor din bază (regulile de fond: R3 documentul, perioada blocată, ciorna altuia) — aceleași ca în `main.py`
_REFUZURI_BAZA = ("REGULA_CONTABILA:", "PERIOADA_BLOCATA:", "DREPT_CIORNA:")


def _motiv_din_baza(exc):
    """Textul pentru contabil al unui refuz din bază (după eticheta lui), sau None pentru o eroare care nu e un refuz."""
    msg = str(exc)
    for et in _REFUZURI_BAZA:
        if et in msg:
            t = msg.split(et)[1].split("\n")[0].strip()
            return ("Perioada %s." % t) if et == "PERIOADA_BLOCATA:" else t
    return None


def _cod_din_baza(exc):
    """Felul unui refuz din bază (eticheta lui, fără „:”), sau None pentru o eroare care nu e un refuz."""
    msg = str(exc)
    return next((et.rstrip(":") for et in _REFUZURI_BAZA if et in msg), None)


def valideaza_interne(conn, schema, nota_ids, cu_cod=False):
    """Validează notele interne ale unei firme în partidă simplă pe ACELAȘI drum ca validarea omului (`valideaza`: nota stornată, Z-ul
    nedescărcat, închiderea anului, casa sub zero — 406; în bază R3 documentul justificativ și perioada blocată), fiecare în punctul ei
    de salvare: un refuz lasă nota ciornă, cu motivul, fără să le strice pe celelalte. Ordinea e a Registrului jurnal (data, apoi id-ul):
    o încasare în casă se validează înaintea plății din aceeași zi. Tranzacția e a apelantului.
    -> (validate: [nota_id], refuzate: [(nota_id, motiv)]); cu `cu_cod`: refuzate [(nota_id, motiv, cod)] — felul refuzului (codul
    regulii din `valideaza`, eticheta refuzului din bază, „EROARE”), pentru o numărătoare care nu poartă datele notelor."""
    import psycopg2
    validate, refuzate = [], []
    with conn.cursor() as cur:
        cur.execute(f"SELECT id FROM {schema}.inregistrari WHERE id = ANY(%s) ORDER BY data, id", ([int(i) for i in nota_ids],))
        ids = [r[0] for r in cur.fetchall()]
        for nid in ids:
            cur.execute("SAVEPOINT nota_interna")
            try:
                rez = valideaza(conn, schema, nid)
            except psycopg2.Error as e:
                cur.execute("ROLLBACK TO SAVEPOINT nota_interna")
                motiv = _motiv_din_baza(e)
                if motiv is None:   # o eroare care nu e un refuz al regulilor: nota rămâne ciornă, iar eroarea nu e tăcută
                    from core import observare as _obs
                    _obs.esec_secundar("validarea notei interne %s" % nid, e)
                    motiv = "nota nu s-a putut valida (eroare la scriere)"
                refuzate.append((nid, motiv, _cod_din_baza(e) or "EROARE") if cu_cod else (nid, motiv))
                continue
            if rez and rez.get("ok"):
                cur.execute("RELEASE SAVEPOINT nota_interna")
                validate.append(nid)
            else:
                cur.execute("ROLLBACK TO SAVEPOINT nota_interna")
                _m = str((rez or {}).get("eroare") or "nota nu mai există")
                refuzate.append((nid, _m, str((rez or {}).get("cod") or "REFUZ")) if cu_cod else (nid, _m))
    return validate, refuzate


#: [deficiența 245, retestul Costin 13.10.2026, comanda 14.10 pct.2, verbatim în DECIZII] „pe note apare «sursa: inchidere_an». Scrie
#: «sursa: închiderea anului» și verifică toate sursele de note afișate.” Sursa notei (`inregistrari.sursa`) e un cod intern; contabilul
#: vede eticheta. Fiecare sursă pe care aplicația o scrie are etichetă aici — păzit de `core/test_jurnal_sursa_eticheta.py` (citește
#: toate scrierile în `inregistrari` din cod).
ETICHETE_SURSA = {
    "manual": "introducere manuală",
    "facturi": "facturile",
    "banca": "banca (extrasul de cont)",
    "casa": "registrul de casă",
    "stocuri": "gestiunea stocurilor",
    "salarii": "statul de plată",
    "amortizare": "amortizarea mijloacelor fixe",
    "bon": "bonul fiscal",
    "horeca_z": "raportul Z",
    "amef": "raportul Z din casa de marcat",
    "inchidere_an": "închiderea anului",
    # [lotul 10, deficiența 430d] notele din Operațiuni speciale (dividende, leasing, provizioane…): până azi „sursa: facturile”
    "operatiuni": "operațiunile speciale",
}


def eticheta_sursa(sursa):
    """Eticheta sursei notei, pentru ecran; None pentru o notă fără sursă sau cu un cod pe care aplicația nu-l scrie (nu se afișează
    codul)."""
    return ETICHETE_SURSA.get(sursa)


def document_justificativ(document_ref, fel, serie, numar, data, sursa=None, numar_nota=None):
    """Coloana 3 din Registrul-jurnal (OMFP 2634/2015, cod 14-1-1): *„felul, numărul și data
    documentului justificativ care stă la baza operațiunilor (factura, chitanța etc.)"*.

    Se DERIVĂ, nu se fabrică. Trei căi, în ordine:
      1. `document_ref` scris explicit pe notă — se ia ca atare;
      2. factura legată prin `factura_id` — se compune „Factură <serie><număr> din <data>";
      2b. [deficiența 214, retestul Costin 09.10: „Nota de amortizare … «Document justificativ: nederivat»”] nota de amortizare are
          documentul ei prin construcție — tabloul de amortizare al lunii, numit de numărul notei (`AMORT-AAAA-LL`); notele scrise
          înainte ca tabloul să primească număr intern (`document_ref` gol) îl primesc la citire;
      3. nimic din care s-o derivi -> **None**, adică lipsă vizibilă.

    A treia e importantă: un registru care ar completa un document inexistent ar face exact ce am
    scos din ecranul de NIR — ar răspunde în locul omului. O coloană goală e onestă.
    """
    if document_ref:
        return str(document_ref).strip() or None
    if sursa == "amortizare" and numar_nota:
        return "Tabloul de amortizare %s" % numar_nota
    if numar is None:
        return None
    return eticheta_factura(fel, serie, numar, data)


def facturi_stinse(cur, schema, nota_ids):
    """[08.10.2026, decizia Costin U5] „Nota unei chitanțe (de ex. CHF1-1) afișează factura pe care o stinge.” {nota_id: „factura
    <serie><număr> din <zz.ll.aaaa>”} — din legătura chitanței (`chitante.inregistrare_id` -> `chitante.factura_id`), numai chitanțe
    nenulate. O singură derivare, pentru Registrul jurnal și pentru coadă (cardul și detaliul notei)."""
    ids = [int(i) for i in nota_ids or [] if i]
    if not ids:
        return {}
    p = ('"%s".' % str(schema).strip('"')) if schema else ""
    cur.execute("SELECT ch.inregistrare_id, f.tip, f.serie, f.numar, f.data_emitere FROM %schitante ch JOIN %sfacturi f "
                "ON f.id = ch.factura_id WHERE ch.inregistrare_id = ANY(%%s) AND NOT ch.anulata" % (p, p), (ids,))
    out = {}
    for x in cur.fetchall():
        v = tuple(x.values()) if isinstance(x, dict) else tuple(x)
        out[v[0]] = eticheta_factura_in_text(v[1], v[2], v[3], v[4]) if v[3] is not None else None
    return {k: v for k, v in out.items() if v}


#: [lotul 10, deficiența 401] felul documentului în mijlocul unei fraze („nota e derivată din …”, „stinge …”), cu articolul hotărât
_FEL_IN_TEXT = {"factura": "factura", "borderou": "borderoul de achiziție"}


def eticheta_factura_in_text(fel, serie, numar, data):
    """„factura FCT12 din 05.10.2026” / „borderoul de achiziție BA-1 din 19.10.2026” — documentul din `facturi` în mijlocul unei fraze.
    [lotul 10, deficiența 401, comanda Costin 10.2 pct.7a, verbatim] „sub nota borderoului, textul zice «factura de achiziție BA-1» și
    trimite la Facturi.” Cauza: textul se compunea din „factura ” + eticheta tăiată la primul cuvânt („Borderou de achiziție BA-1” ->
    „de achiziție BA-1”). Felul se ia din `facturi.tip`, aceeași sursă ca `eticheta_factura`."""
    from core import pdf_util
    return "%s %s din %s" % (_FEL_IN_TEXT.get(fel or "factura") or str(fel), pdf_util.numar_cu_serie(serie, numar), pdf_util.data_ro(data))


def eticheta_document(fel, numar=None, data=None, detaliu=None):
    """„<Fel> nr <număr> din <zz.ll.aaaa> (<detaliu>)” — documentul sursă al unei note scrise de aplicație (Registrul-jurnal
    col.3: felul, numărul și data). Numai din ce există în date: un câmp lipsă nu se completează, se omite.
    [05.10.2026, comanda Costin pct.6] Sursa UNICĂ pentru notele automate: bon, raport Z, stat de plată, NIR."""
    from core import pdf_util
    t = str(fel)
    if numar not in (None, ""):
        t += " nr %s" % numar
    if data not in (None, ""):
        t += " din %s" % pdf_util.data_ro(data)
    if detaliu:
        t += " (%s)" % detaliu
    return t


def eticheta_factura(fel, serie, numar, data):
    """„Factură FCT12 din 05.10.2026” — felul, numărul și data, în forma în care le citește omul.

    [05.10.2026, comanda Costin pct.6] Numărul unei facturi EMISE conține deja seria (`facturi_api`: număr = serie + număr),
    deci seria se pune în față numai când lipsește din număr — înainte ieșea „FCTFCT12”. Data în forma românească
    (`pdf_util.data_ro`), nu ISO. Sursa UNICĂ: o folosesc și Registrul-jurnal, și nota de descărcare a stocului."""
    from core import pdf_util
    nr = pdf_util.numar_cu_serie(serie, numar)
    # [401] borderoul de achiziție de la persoana fizică (OMFP 2634/2015, cod 14-4-13) nu e „Factură”
    et = {"factura": "Factură", "borderou": "Borderou de achiziție"}.get(fel or "factura") or str(fel).capitalize()
    return "%s %s din %s" % (et, nr, pdf_util.data_ro(data))
