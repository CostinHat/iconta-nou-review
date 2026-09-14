# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/coada`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:840`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

from core import db, declaratii_api, coada_api
from core import repo_declaratii
from core import erori as _erori
from core import uc_comun as _uc_comun
from core import db, auth_api, coada_api, supervizor
from core.mesaje import (FARA_DREPT_VALIDARE, FARA_DREPT_DEPUNERE)
from core import tranzactie


def coada_adauga(date, ctx):
    """[P7 · use-case] Corpul rutei `/coada`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, date.tenant_id)
    body = date.model_dump(exclude_none=True)
    for k in ("tenant_id", "tip", "inceput_la"):  # [p15] inceput_la nu merge la generator
        body.pop(k, None)
    # 1) generează declarația pe schema tenantului
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, date.tip, body)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    # [F163v2] păstrăm și `res` întreg (serializat) în payload, nu doar avertismente: e singura
    # cale prin care rândurile depuse ajung persistate (marcheaza_depusa le scrie în
    # declaratii_depuse.randuri). d112 -> randuri None (randuri_din_res, temei acolo).
    payload = {"xml": xml,
               "avertismente": (res if isinstance(res, list) else getattr(res, "avertismente", None)),
               "note_rezultat": ([] if isinstance(res, list) else (getattr(res, "note_rezultat", None) or [])),
               "randuri": coada_api.randuri_din_res(res)}
    # 2) POARTA: se VALIDEAZĂ ÎNAINTE de a intra în coadă (decizia lui Costin, 26.08.2026).
    #
    # Până azi coada primea orice se genera, iar validatorul rula abia când cineva deschidea
    # elementul (`GET /coada/{id}/continut`). Poarta exista, dar la DEPUNERE. Consecința: lista
    # pe care ecranul o numește „De depus" putea conține declarații care n-au trecut niciodată
    # prin validator — o afirmație falsă despre propria stare (P13). Cazul care a produs regula
    # e chiar cel din antetul lui `TRASEE.md`: trei declarații în coadă fără verdict, găsite
    # fiindcă cineva a apăsat un buton, nu de vreo măsurătoare.
    #
    # NU se adaugă o a doua rulare de validator în lanț: rularea de aici e cea care oricum se
    # făcea la prima deschidere, mutată mai devreme. Verdictul se PĂSTREAZĂ imediat după
    # inserare, cu amprenta XML-ului validat, deci elementul intră în coadă purtându-l din
    # naștere — nu îl capătă când se uită cineva la el.
    #
    # `gri` (nu am putut valida) NU trece drept favorabil (P6): se refuză la fel ca `erori`.
    # Portița e aceeași ca la aprobare și depunere — `motiv_trecere` scris explicit, care se
    # păstrează. Fără ea, un validator picat ar bloca toată munca; cu ea, trecerea are autor.
    from core import duk as _duk_poarta
    _rez = _duk_poarta.valideaza(xml, date.tip, an=date.an, luna=date.luna) if xml else {
        "stare": "gri", "erori": "", "severitate": None,
        "temei": "Generarea n-a produs XML.", "limita": ""}
    _motiv = (date.motiv_trecere or "").strip()
    if _rez.get("stare") != "valid" and not _motiv:
        # Refuzul poartă CE lipsește, nu doar că lipsește — altfel contabilul află ce are de
        # făcut abia deschizând altceva.
        raise _erori.DateInvalide({
                "mesaj": ("Declarația nu intră în coadă: validatorul oficial a răspuns „%s”."
                          % _rez.get("stare")),
                "stare": _rez.get("stare"), "erori": _rez.get("erori") or "",
                "severitate": _rez.get("severitate"), "temei": _rez.get("temei"),
                "limita": _rez.get("limita"),
                # Mesajul NU numește câmpul intern al cererii (Regula 14 pct.4): contabilul vede
                # ce are de făcut, nu numele coloanei. Câmpul rămâne în contractul API, la `detalii`.
                "actiune": ("Corectează ce semnalează validatorul și generează din nou. Dacă treci "
                            "peste deliberat, scrie motivul trecerii — se păstrează cu numele tău."),
                "camp_trecere": "motiv_trecere"})

    # 3) pune în coadă (pe public), stare 'la_senior'
    with db.get_conn() as conn:
        r = coada_api.adauga_in_coada(
            conn, ctx["firm"], date.tenant_id, date.tip, date.an, payload,
            creat_de=str(ctx["uid"]), creat_de_id=int(ctx["uid"]), luna=date.luna, trim=date.trim,
            inceput_la=date.inceput_la)  # [p15]
    if not r["ok"] and r.get("cod") == "DEJA_IN_COADA":
        raise _erori.Conflict(r["mesaj"])
    # verdictul intră odată cu elementul, nu la prima privire asupra lui
    if r.get("ok") and r.get("coada_id"):
        _versiune = _duk_poarta.versiune_validator(date.tip)   # [P5 val 3] citire de fisier, INAINTE
        try:
            with db.get_conn() as conn:
                coada_api.scrie_verdict(conn, r["coada_id"], _rez, _versiune, xml)
        except Exception as _e:
            import logging
            logging.getLogger("iconta").warning("verdict nepersistat la intrarea in coada (%s): %s",
                                                r.get("coada_id"), _e)
    r["verdict"] = {"stare": _rez.get("stare"), "trecut_cu_motiv": _motiv or None}
    # [p57_notif] notifica validatorii ca e ceva de validat
    if r.get("ok"):
        try:
            with db.get_conn() as conn:
                _uc_comun._notif_de_validat(conn, ctx["firm"], date.tip,
                                  r.get("perioada") or ("%s/%s" % (date.luna or date.trim or "", date.an)),
                                  int(ctx["uid"]))
        except Exception:
            pass
    return r


def coada_lista(stare, ctx):
    """[P7 · use-case] Corpul rutei `/coada`; docstringul ei a ramas in stratul HTTP."""
    if stare is not None and stare not in coada_api.STARI:
        raise _erori.DateInvalide("stare necunoscută: %r (stările cozii: %s)"
                                % (stare, ", ".join(coada_api.STARI)))
    with db.get_conn() as conn:
        return {"coada": coada_api.lista_coada(conn, ctx["firm"], stare)}


def coada_continut(coada_id, ctx):
    """[P7 · use-case] Corpul rutei `/coada/{coada_id}/continut`; docstringul ei a ramas in stratul HTTP."""
    import base64 as _b64
    from core import duk as _duk
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            row = repo_declaratii.continutul_din_coada(cur, coada_id, ctx["firm"])
    if not row:
        raise _erori.Inexistent("Element de coadă negăsit (sau alt cabinet).")
    tip, payload, _an, _luna = row
    payload = payload or {}
    xml = payload.get("xml") or ""
    if xml:
        rez = _duk.valideaza(xml, tip, an=_an, luna=_luna)  # java blocant - verdictul oficial ANAF
    else:
        rez = {"stare": "gri", "erori": "", "severitate": None,
               "temei": "XML lipsă din payload-ul cozii.", "limita": ""}
    # [R41] Verdictul se PĂSTREAZĂ. Până azi se producea aici și se arunca, iar ecranul numea
    # „De depus" o listă care conținea declarații fără verdict. Nu se adaugă o a doua rulare de
    # validator: se scrie exact rezultatul celei care se făcea oricum, cu amprenta XML-ului validat.
    _versiune = _duk.versiune_validator(tip)                   # [P5 val 3] citire de fisier, INAINTE
    try:
        with db.get_conn() as conn:
            coada_api.scrie_verdict(conn, coada_id, rez, _versiune, xml)
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning("verdict nepersistat (coada %s): %s", coada_id, _e)
    return {"tip": tip,
            "xml_b64": _b64.b64encode(xml.encode()).decode(),
            "avertismente": payload.get("avertismente") or [],
            "note_rezultat": payload.get("note_rezultat") or [],
            "stare": rez["stare"], "erori": rez["erori"], "severitate": rez.get("severitate"),
            "temei": rez.get("temei"), "limita": rez.get("limita")}


def coada_aproba(coada_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/coada/{coada_id}/aproba`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not _uc_comun._are_permisiune(ctx, "poate_valida"):
            raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
        # [R41] `motiv_trecere` = trecerea EXPLICITĂ peste un verdict lipsă, stătut sau cu erori.
        # Fără el, acțiunea e refuzată; cu el, se consemnează cine și de ce.
        r = coada_api.aproba(conn, coada_id, str(ctx["uid"]), aprobat_de_id=int(ctx["uid"]),
                             motiv_trecere=(date or {}).get("motiv_trecere"))
    if not r["ok"]:
        cod = r.get("cod")
        http = ((_erori.Conflict if cod == "STARE_GRESITA" else _erori.FaraDrept if cod in ("PATRU_OCHI", "FARA_VERDICT") else _erori.Inexistent))
        raise http(r.get("mesaj", cod))
    # [p57_notif] notifica pregatitorul
    try:
        with db.get_conn() as conn:
            _uc_comun._notif_pregatitor(conn, coada_id, "aprobata")
    except Exception as _e:
        import logging; logging.getLogger("iconta").warning("notificare pregatitor esuata (aprobare, coada %s): %s", coada_id, _e)
    return r



def coada_respinge(coada_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/coada/{coada_id}/respinge`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not _uc_comun._are_permisiune(ctx, "poate_valida"):
            raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
        r = coada_api.respinge(conn, coada_id, str(ctx["uid"]), date.motiv, respins_de_id=int(ctx["uid"]))
    if not r["ok"]:  # [motiv_lipsa_400_v1] MOTIV_LIPSA e input invalid -> 400
        _cod = r.get("cod")
        _http = (_erori.Conflict if _cod == "STARE_GRESITA" else _erori.CerereGresita if _cod == "MOTIV_LIPSA" else _erori.Inexistent)
        raise _http(r.get("mesaj", _cod))
    # [p57_notif] notifica pregatitorul cu motivul
    try:
        with db.get_conn() as conn:
            _uc_comun._notif_pregatitor(conn, coada_id, "respinsa", motiv=date.motiv)
    except Exception as _e:
        import logging; logging.getLogger("iconta").warning("notificare pregatitor esuata (respingere, coada %s): %s", coada_id, _e)
    return r



def coada_depune(coada_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/coada/{coada_id}/depune`; docstringul ei a ramas in stratul HTTP."""
    if not _uc_comun._are_permisiune(ctx, "poate_depune"):
        raise _erori.FaraDrept(FARA_DREPT_DEPUNERE)
    _tid = _an_d = _luna_d = _schema_d = None
    try:
        with db.get_conn() as _cp:
            _fp = coada_api.firma_si_perioada(_cp, coada_id)
        if _fp:
            _tid, _an_d, _luna_d = _fp
            with db.get_conn() as _cp:
                _schema_d = auth_api.schema_tenant(_cp, ctx["uid"], _tid)
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning(
            "contextul supervizorului n-a putut fi citit pe coada %s: %s — depunerea CONTINUA "
            "(supervizorul nu blocheaza niciodata)", coada_id, _e)
        _schema_d = None
    with db.get_conn(_schema_d) as conn:
        _ramase = []
        if _schema_d:
            # DE CE `SAVEPOINT` și nu un `try` care înghite: dacă supervizorul crapă cu o eroare
            # de bază, tranzacția e deja abortată, iar depunerea de după ar pica din alt motiv
            # decât cel real. Savepointul întoarce exact partea lui.
            with conn.cursor() as _cur:
                tranzactie.savepoint_supervizor(_cur)
            try:
                _ramase = supervizor.poarta_confirmarii(
                    conn, _schema_d, _tid, _an_d, _luna_d,
                    confirmari=date.confirmari, confirmat_de=str(ctx["uid"]),
                    confirmat_de_id=int(ctx["uid"]))
                with conn.cursor() as _cur:
                    tranzactie.elibereaza_supervizor(_cur)
            except Exception as _e:
                with conn.cursor() as _cur:
                    tranzactie.intoarce_la_supervizor(_cur)
                import logging
                logging.getLogger("iconta").warning(
                    "poarta confirmarii supervizorului a esuat pe coada %s: %s — depunerea "
                    "CONTINUA (supervizorul nu blocheaza niciodata)", coada_id, _e)
                _ramase = []
        if _ramase:
            # NU e un blocaj: e o cerere de confirmare, cu calea de trecere numită în chiar
            # răspunsul ăsta (trimite `confirmari` cu amprenta și motivul). Interdicția 47 — un
            # refuz fără cale de ieșire pentru om.
            raise _erori.Conflict({
                "cod": "CONSTATARI_NECONFIRMATE",
                "mesaj": ("%d constatare/constatări certe pe firma și perioada asta cer o "
                          "confirmare scrisă înainte de depunere. Depunerea NU e blocată: "
                          "confirmă-le, cu motiv, și continuă." % len(_ramase)),
                # constatarile se trimit AȘA CUM SUNT: sunt deja afirmații tipate, produse de
                # `control_incrucisat`. Reîmpachetarea lor aici ar fi fost o a doua afirmație,
                # netipată — și cine o citea n-ar fi știut care e cea adevărată.
                "constatari": _ramase,
                "actiune": "Retrimite cererea cu `confirmari`: [{amprenta, motiv}] pentru fiecare.",
            })
        # [02.09.2026, defect gasit apasand] APROBAREA VINE DUPA POARTA, si e a serverului.
        # Inlantuirea traia in client (`POST /aproba` apoi `POST /depune`), deci aprobarea trecea si
        # poarta cadea dupa ea — iar elementul ramanea `aprobata`, stare din care nu se mai poate
        # RESPINGE. Un refuz al portii ingusta optiunile omului, exact ce contractul interzice.
        # Masurat in `uvicorn.log` pe elementul 8052; v. `coada_api.auto_aproba_daca_e_cazul`.
        _ap = coada_api.auto_aproba_daca_e_cazul(
            conn, coada_id, str(ctx["uid"]), int(ctx["uid"]),
            motiv_trecere=getattr(date, "motiv_trecere", None))
        if not _ap.get("ok"):
            # [probare invalid, 03.09.2026] `INEXISTENT` cădea pe 403 — „n-ai voie" în loc de
            # „nu există". Aceeași cerere pe `/aproba` răspundea 404: două coduri pentru
            # aceeași stare.
            _c = _ap.get("cod")
            raise (_erori.Conflict if _c in ("CERE_APROBARE", "STARE_GRESITA") else _erori.Inexistent if _c == "INEXISTENT" else _erori.FaraDrept)(_ap.get("mesaj") or _c)
        r = coada_api.marcheaza_depusa(conn, coada_id, date.spv_index, depus_de=str(ctx["uid"]),
                                       depus_de_id=int(ctx["uid"]),
                                       motiv_trecere=getattr(date, "motiv_trecere", None))
        # [P4] REFUZUL SE RIDICA DINAUNTRUL TRANZACTIEI, ca sa se intoarca si aprobarea de dinainte.
        #
        # Pana azi, `raise` statea DUPA `with`, deci tranzactia se inchidea NORMAL si comitea ce
        # scrisese `auto_aproba_daca_e_cazul`. Un refuz al marcarii lasa elementul `aprobata` fara
        # sa fie depus — chiar forma pe care R128 o reparase venind din client: *un refuz care
        # ingusta optiunile omului* (din `aprobata` nu se mai poate RESPINGE). Ordinea celor doua
        # scrieri era corecta; ce lipsea era ca refuzul sa fie inauntrul limitei lor.
        if not r["ok"]:
            cod = r.get("cod")
            raise (_erori.Conflict if cod == "STARE_GRESITA" else _erori.FaraDrept if cod == "FARA_VERDICT" else _erori.Inexistent)(r.get("mesaj", cod))
    return r

