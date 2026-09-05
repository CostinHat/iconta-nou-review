# -*- coding: utf-8 -*-
"""Jurnal — editare/ștergere/validare note. Doar ciornele se pot modifica:
AI propune (ciorna), contabilul validează."""
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
    return None


def creeaza(conn, schema, descriere, data, linii):
    """Creeaza o nota manuala noua, ca ciorna. linii = [{debit, credit, suma}], min 1 linie."""
    data, rd = _data_valida(data)
    if rd:
        return rd
    rl = _linii_valide(conn, schema, linii)
    if rl:
        return rl
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                        VALUES (%s,%s,'manual','ciorna') RETURNING id""",
                    (data, (descriere or "")[:200]))
        nota_id = cur.fetchone()["id"]
        for l in linii:
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                (inregistrare_id, cont_debit, cont_credit, suma, centru_cost_id)
                VALUES (%s,%s,%s,%s,%s)""",
                (nota_id, str(l["debit"]).strip(), str(l["credit"]).strip(),
                 Decimal(str(l["suma"])), _centru(l)))
        # [DDD3] LA SURSĂ: dacă nota contează evident o factură, primește `factura_id` ACUM.
        # Gaura măsurată la BBB era că o notă din calea liberă nu poartă cheia, deci e invizibilă
        # pentru anti-dublare. Plasa (`candidate_fara_cheie`) rămâne plasă tocmai fiindcă legătura
        # se face aici, la scriere — nu invers.
        legata = _cf.leaga_nota_de_factura(
            cur, schema, nota_id,
            [(str(l["debit"]).strip(), str(l["credit"]).strip(), Decimal(str(l["suma"])))
             for l in linii], data)
    conn.commit()
    out = {"ok": True, "id": nota_id}
    if legata:
        out["factura_id"] = legata
        out["mesaj"] = ("nota a fost legată de factura #%d — o singură factură a lunii se "
                        "potrivește pe sumă" % legata)
    return out
def editeaza(conn, schema, nota_id, descriere=None, data=None, linii=None):
    """Editează o notă ciornă. linii = [{debit, credit, suma}] înlocuiește complet liniile."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        n = _nota(cur, schema, nota_id)
        if not n:
            return None
        if n["status"] != "ciorna":
            return {"eroare": "doar ciornele se pot edita"}
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
                    (inregistrare_id, cont_debit, cont_credit, suma, centru_cost_id)
                    VALUES (%s,%s,%s,%s,%s)""",
                    (nota_id, str(l["debit"]).strip(), str(l["credit"]).strip(),
                     Decimal(str(l["suma"])), _centru(l)))
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
        if seturi:
            cur.execute(f"UPDATE {schema}.inregistrari SET {', '.join(seturi)} WHERE id=%s",
                        (*valori, nota_id))
    conn.commit()
    return {"ok": True}


def sterge(conn, schema, nota_id):
    """Șterge o notă ciornă (liniile cad prin ON DELETE CASCADE)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        n = _nota(cur, schema, nota_id)
        if not n:
            return None
        if n["status"] != "ciorna":
            return {"eroare": "doar ciornele se pot șterge"}
        cur.execute(f"DELETE FROM {schema}.casa_operatiuni WHERE inregistrare_id=%s", (nota_id,))
        cur.execute(f"""UPDATE {schema}.extras_linii SET status='potrivit'
                        WHERE status='contat'
                          AND alocari->'inregistrari_ids' @> %s::jsonb""", (str(nota_id),))
        cur.execute(f"DELETE FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
    conn.commit()
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
    conn.commit()
    return {"ok": True}


def document_justificativ(document_ref, fel, serie, numar, data):
    """Coloana 3 din Registrul-jurnal (OMFP 2634/2015, cod 14-1-1): *„felul, numărul și data
    documentului justificativ care stă la baza operațiunilor (factura, chitanța etc.)"*.

    Se DERIVĂ, nu se fabrică. Trei căi, în ordine:
      1. `document_ref` scris explicit pe notă — se ia ca atare;
      2. factura legată prin `factura_id` — se compune „Factură <serie><număr> din <data>";
      3. nimic din care s-o derivi -> **None**, adică lipsă vizibilă.

    A treia e importantă: un registru care ar completa un document inexistent ar face exact ce am
    scos din ecranul de NIR — ar răspunde în locul omului. O coloană goală e onestă.
    """
    if document_ref:
        return str(document_ref).strip() or None
    if numar is None:
        return None
    nr = "%s%s" % (serie or "", numar)
    et = "Factură" if (fel or "factura") == "factura" else str(fel).capitalize()
    return "%s %s din %s" % (et, nr, data.isoformat() if hasattr(data, "isoformat") else data)
