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
from core.mesaje import (FARA_DREPT_VALIDARE, FARA_DREPT_DEPUNERE, FARA_DREPT_PREGATIRE)
from core import tranzactie


#: [comanda Costin 07.10.2026, C3] Refuzurile DUK la intrarea în coadă: `cod -> (mesaj, acțiune, câmpul de trecere)`. Eroarea n-are
#: câmp de trecere (oprește); atenționarea îl are — confirmarea scrisă a contabilului.
_REFUZ_DUK = {
    "ERORI_DUK": (
        "Declarația nu intră în coadă: validatorul oficial ANAF a găsit erori — ar fi respinsă la depunere.",
        "Corectează ce semnalează validatorul și generează din nou.", None),
    "ATENTIONARI_NECONFIRMATE": (
        "Validatorul oficial ANAF a semnalat atenționări (nu erori). Declarația intră în coadă după ce le confirmi în scris: "
        "de ce e corectă așa.",
        "Citește atenționările și scrie confirmarea — se păstrează cu numele tău.", "motiv_trecere"),
}


def _refuz_duk(cod, rez, sev):
    """Refuzul structurat (422) cu ce a spus validatorul — ecranul arată erorile/atenționările și, la atenționare, cere confirmarea."""
    mesaj, actiune, camp = _REFUZ_DUK[cod]
    out = {"cod": cod, "mesaj": mesaj, "stare": rez.get("stare"), "erori": rez.get("erori") or "", "severitate": sev,
           "temei": rez.get("temei"), "limita": rez.get("limita"), "actiune": actiune}
    if camp:
        out["camp_trecere"] = camp
    return out


#: [08.10.2026, decizia Costin] declarațiile de TVA: intră în coadă numai dacă TVA-ul lor se potrivește cu balanța lunii
DECLARATII_TVA = ("d300", "d394", "d390")
COD_TVA_BALANTA = "TVA_DIFERA_DE_BALANTA"
CONTURI_TVA_POARTA = ("4427", "4426")


def poarta_tva_balanta(schema, an, luna, trim=None):
    """Refuzul structurat (sau None) când D300 al perioadei nu se potrivește cu rulajele 4427 / 4426 (note validate):
    {cod, mesaj, diferente: [{cont, rand, eticheta, declarat, contabil, diferenta}]}. D394 și D390 se construiesc din aceleași
    documente, deci se judecă pe aceeași pereche. O perioadă trimestrială se ancorează în ultima ei lună."""
    from core import control_incrucisat as _ci
    luna_ancora = luna or (int(trim) * 3 if trim else None)
    if not luna_ancora:
        return None
    with db.get_conn(schema) as conn:
        v = _ci.verifica_tva(conn, schema, an, luna_ancora)
    rosii = [c for c in (v.get("constatari") or []) if c.get("stare") == "rosu" and c.get("cont") in CONTURI_TVA_POARTA]
    if not rosii:
        return None
    dif = [{"cont": c["cont"], "rand": c.get("rand"), "eticheta": c.get("eticheta"), "declarat": "%.2f" % c["declarat"],
            "contabil": "%.2f" % c["contabil"], "diferenta": "%.2f" % c["diferenta"]} for c in rosii]
    from core import afirmatii as _af
    mesaj = ("Declarația nu intră în coadă: TVA-ul ei nu se potrivește cu balanța lunii — " + "; ".join(
                "%s (rândul %s): declarat %s, contul %s are %s, diferență %s lei" % (
                    d["eticheta"], d["rand"], d["declarat"], d["cont"], d["contabil"], d["diferenta"]) for d in dif)
                      + ". Toleranța e rotunjirea la leu. Validatorul ANAF verifică structura, nu cifrele: corectează documentele "
                        "(o factură necontată, o notă nevalidată, o achiziție fără factură) și generează din nou.")
    return dict(_af.afirmatie("neconformitate", "declaratie_tva", mesaj, unde="perioada %02d/%04d" % (luna_ancora, an),
                              regula="R17_2 = rulajul creditor 4427 și R27_2 = rulajul debitor 4426 ale ferestrei TVA (toleranța 1 leu)"),
                cod=COD_TVA_BALANTA, diferente=dif, mesaj=mesaj)


COD_D406_BALANTA = "D406_DIFERA_DE_BALANTA"


def poarta_d406_balanta(schema, an, luna, res):
    """[08.10.2026, decizia Costin V1, completarea 2 la U1, verbatim în DECIZII] „Gardă: totalurile GeneralLedgerEntries din D406
    trebuie să egaleze rulajele balanței pe lună; dacă nu, «Trimite în coadă» e blocat.”

    Rulajele BALANȚEI (`documente_api.balanta`, rulajele curente ale fiecărei luni din fereastra D406 — `common.fereastra_d406`),
    adică exact ce vede contabilul pe ecranul Balanță: cu tot cu ciorne (balanța nu filtrează pe status, `scan_populatii_registre`).
    D406 cuprinde numai notele VALIDATE, deci o lună cu ciorne nu intră în coadă până nu se validează (MĂSURAT pe F1 10/2026: notele
    de bancă 106/107 — încasarea 6.938 și comisionul 15 — sunt ciornă; în balanță sunt, în D406 nu). Legarea cont cu cont pe notele
    validate rămâne `d406_reconciliere` (la generare). Refuzul (sau None): {cod, mesaj, d406, balanta, diferenta, ciorne}."""
    from decimal import Decimal
    from core import documente_api as _doc
    from core.common import fereastra_d406 as _fd
    gl = sum((Decimal(str(l.debit or 0)) for n in (getattr(res, "note", None) or []) for l in n.linii), Decimal(0))
    from core import repo_contabilitate
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            r = repo_contabilitate.profil_tva(cur)
        di, ds = _fd({"platitor_tva": r[0], "tip_decont": r[1]} if r else {}, an, luna)
        bal, a, l = Decimal(0), di.year, di.month
        while (a, l) < (ds.year, ds.month):
            bal += Decimal(str(_doc.totaluri_balanta(_doc.balanta(conn, schema, a, l))["rul_d"]))
            a, l = (a + 1, 1) if l == 12 else (a, l + 1)
        with conn.cursor() as cur:
            ciorne = repo_contabilitate.note_nevalidate_in_interval(cur, di, ds)
        conn.rollback()
    from decimal import ROUND_HALF_UP
    gl, bal = gl.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), bal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if gl == bal:
        return None
    from core import afirmatii as _af
    mesaj = ("D406 nu intră în coadă: totalul notelor din GeneralLedgerEntries (%s lei) nu e rulajul balanței pe perioadă "
                      "(%s lei), diferență %s lei.%s" % (
                          "%.2f" % gl, "%.2f" % bal, "%.2f" % (gl - bal),
                          (" În perioadă sunt %d notă(e) nevalidată(e): balanța le arată, D406 cuprinde numai notele validate — "
                           "validează-le (sau șterge-le) din Registrul jurnal și generează din nou." % ciorne) if ciorne else ""))
    return dict(_af.afirmatie("neconformitate", "declaratie_d406", mesaj, unde="perioada %s – %s" % (di.isoformat(), ds.isoformat()),
                              regula="totalul GeneralLedgerEntries = rulajul balanței pe fereastra D406"),
                cod=COD_D406_BALANTA, d406="%.2f" % gl, balanta="%.2f" % bal, diferenta="%.2f" % (gl - bal), ciorne=ciorne, mesaj=mesaj)


def coada_adauga(date, ctx):
    """[P7 · use-case] Corpul rutei `/coada`; docstringul ei a ramas in stratul HTTP."""
    # [B4, 17.09.2026] A pune o declarație în coadă e actul de PREGĂTIRE — cere `poate_pregati`.
    # Până azi flagul apărea doar la setare, nu la folosire: orice angajat sub `cere_cabinet` genera
    # și punea în coadă. Poarta e aici, pe acțiune, nu doar în profil.
    if not _uc_comun._are_permisiune(ctx, "poate_pregati"):
        raise _erori.FaraDrept(FARA_DREPT_PREGATIRE)
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
    # 1b) [08.10.2026, decizia Costin U1 + completarea] „Gardă obligatorie: dacă rândurile de TVA colectată și deductibilă ale D300 nu
    # se potrivesc cu rulajele 4427 și 4426 ale lunii (toleranță: rotunjirea la leu), «Trimite în coadă» e blocat și se afișează
    # diferența pe conturi. Validatorul DUK verifică doar structura, nu cifrele.” — și „se aplică tuturor declarațiilor de TVA: D300,
    # D394, D390”. Comparația există o singură dată (`control_incrucisat.verifica_tva`: R17_2 <-> rulajul creditor 4427, R27_2 <->
    # rulajul debitor 4426, numai note validate, toleranța 1 leu); aici devine poartă. Fără portiță: `motiv_trecere` e pentru DUK.
    if date.tip in DECLARATII_TVA:
        _refuz_tva = poarta_tva_balanta(schema, date.an, date.luna, date.trim)
        if _refuz_tva:
            raise _erori.DateInvalide(_refuz_tva)
    # 1c) [08.10.2026, decizia Costin V1] D406: totalurile GeneralLedgerEntries = rulajele balanței pe perioadă, altfel blocat.
    if date.tip == "d406":
        _refuz_d406 = poarta_d406_balanta(schema, date.an, date.luna or (int(date.trim) * 3 if date.trim else None), res)
        if _refuz_d406:
            raise _erori.DateInvalide(_refuz_d406)
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
    # [comanda Costin 07.10.2026, C3] „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului.
    # O eroare DUK oprește.” Până azi orice ieșire DUK (și atenționările) refuza intrarea, iar `motiv_trecere` trecea peste
    # ORICE, inclusiv peste erori. Acum: eroarea nu are portiță; atenționarea intră cu confirmarea scrisă, păstrată cu autorul și
    # cu amprenta XML-ului confirmat (aprobarea și depunerea o recunosc cât timp XML-ul e același).
    _sev = _rez.get("severitate") if _rez.get("stare") == "erori" else None
    if _rez.get("stare") == "erori" and _sev != "atentionare":
        raise _erori.DateInvalide(_refuz_duk("ERORI_DUK", _rez, _sev))
    if _sev == "atentionare" and not _motiv:
        raise _erori.DateInvalide(_refuz_duk("ATENTIONARI_NECONFIRMATE", _rez, _sev))
    if _sev == "atentionare":
        import datetime as _dtc
        payload["confirmare_atentionari"] = {"text": _motiv[:500], "de_id": int(ctx["uid"]),   # act al omului, nu afirmație
                                             "la": _dtc.datetime.now().isoformat(timespec="seconds"),
                                             "amprenta": coada_api.amprenta_xml(xml)}
    elif _rez.get("stare") != "valid" and not _motiv:
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
                                  int(ctx["uid"]), tenant_id=date.tenant_id, coada_id=r.get("coada_id"))
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
    _fel, _schema_nota, _el = _schema_notei(coada_id, ctx)
    if _fel == "nota":
        # [validare_note] nota: data, descrierea, documentul justificativ și liniile — ce aprobă validatorul.
        # [lotul 07.10 pct.9] un document cu mai multe note (contarea + ieșirea din stoc a aceleiași facturi) le arată pe toate.
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                membri = coada_api.membri_grup(cur, coada_id, stare=None) or [(coada_id, _el[4])]
        note = []
        with db.get_conn(_schema_nota) as conn:
            with conn.cursor() as cur:
                for _mid, _pl in membri:
                    n, linii = repo_declaratii.nota_cu_linii(cur, _schema_nota, int((_pl or {}).get("inregistrare_id") or 0))
                    if n:
                        from core import jurnal_api as _jst   # [08.10, U5] factura stinsă de chitanța notei
                        note.append({"nota": {"id": n[0], "data": n[1].isoformat(), "descriere": n[2], "document_ref": n[3],
                                              "status": n[4], "sursa": n[5],
                                              "stinge": _jst.facturi_stinse(cur, _schema_nota, [n[0]]).get(n[0])},
                                     "linii": [{"debit": a, "credit": b, "suma": float(c)} for a, b, c in linii]})
        if not note:
            raise _erori.Inexistent("Nota nu mai există în jurnal (a fost ștearsă).")
        return {"fel": "nota", "nota": note[0]["nota"], "linii": note[0]["linii"], "note": note}
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
    _fel, _schema_nota, _el = _schema_notei(coada_id, ctx)   # [validare_note] nota se validează pe schema firmei ei
    with db.get_conn(_schema_nota) as conn:
        if not _uc_comun._are_permisiune(ctx, "poate_valida"):
            raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
        # [R41] `motiv_trecere` = trecerea EXPLICITĂ peste un verdict lipsă, stătut sau cu erori.
        # Fără el, acțiunea e refuzată; cu el, se consemnează cine și de ce.
        r = coada_api.aproba(conn, coada_id, str(ctx["uid"]), aprobat_de_id=int(ctx["uid"]),
                             motiv_trecere=(date or {}).get("motiv_trecere"),
                             cabinet_id_apelant=ctx["firm"],  # [B1] apartenenta pe obiect
                             schema_nota=_schema_nota)
    if not r["ok"]:
        cod = r.get("cod")
        # [B1] ALT_CABINET -> 404 (Inexistent): elementul altui cabinet nu-si dezvaluie existenta.
        # [C3, 07.10.2026] eroarea DUK / atenționările neconfirmate sunt refuzuri de conținut (422), nu „inexistent” (404)
        http = ((_erori.Conflict if cod == "STARE_GRESITA" else _erori.FaraDrept if cod in ("PATRU_OCHI", "FARA_VERDICT")
                 else _erori.DateInvalide if cod in ("ERORI_DUK", "ATENTIONARI_NECONFIRMATE") else _erori.Inexistent))
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
    if not _uc_comun._are_permisiune(ctx, "poate_valida"):
        raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
    # [retest 07.10 R1] nota se respinge pe schema firmei ei: respingerea stornează în aceeași tranzacție mișcarea de stoc a
    # documentului (`stocuri_anulare.storneaza`) — ori ambele, ori niciuna
    _fel, _schema_nota, _el = _schema_notei(coada_id, ctx)
    with db.get_conn(_schema_nota) as conn:
        r = coada_api.respinge(conn, coada_id, str(ctx["uid"]), date.motiv, respins_de_id=int(ctx["uid"]),
                               cabinet_id_apelant=ctx["firm"],  # [B1] apartenenta pe obiect
                               schema_nota=_schema_nota)
        if not r["ok"]:
            conn.rollback()
    if not r["ok"]:  # [motiv_lipsa_400_v1] MOTIV_LIPSA e input invalid -> 400
        _cod = r.get("cod")
        # [B1] ALT_CABINET -> 404 (Inexistent) prin ramura else.
        _http = (_erori.Conflict if _cod == "STARE_GRESITA" else _erori.CerereGresita if _cod in ("MOTIV_LIPSA", "STOC_IESIT")
                 else _erori.Inexistent)
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
    # [B1, 17.09.2026] APARTENENȚA PE OBIECT, verificată ÎNAINTE de poarta supervizorului: elementul
    # e al cabinetului apelant? Altfel 404, fără să atingem firma altui cabinet. Fără ea, un cabinet
    # depunea declarația altuia — scrisă în `declaratii_depuse` al firmei lui. SQL-ul stă în
    # repository (P7): use-case-ul întreabă `repo_declaratii.cabinet_din_coada`, nu execută el SELECT.
    with db.get_conn() as _cp:
        with _cp.cursor() as _cur:
            _own = repo_declaratii.cabinet_din_coada(_cur, coada_id)
    if _own is None or _own != ctx["firm"]:
        raise _erori.Inexistent("Element de coadă negăsit (sau alt cabinet).")
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
            motiv_trecere=getattr(date, "motiv_trecere", None),
            cabinet_id_apelant=ctx["firm"])  # [B1] apartenenta pe obiect
        if not _ap.get("ok"):
            # [probare invalid, 03.09.2026] `INEXISTENT` cădea pe 403 — „n-ai voie" în loc de
            # „nu există". Aceeași cerere pe `/aproba` răspundea 404: două coduri pentru
            # aceeași stare.
            _c = _ap.get("cod")
            raise (_erori.Conflict if _c in ("CERE_APROBARE", "STARE_GRESITA") else _erori.Inexistent if _c in ("INEXISTENT", "ALT_CABINET") else _erori.FaraDrept)(_ap.get("mesaj") or _c)
        r = coada_api.marcheaza_depusa(conn, coada_id, date.spv_index, depus_de=str(ctx["uid"]),
                                       depus_de_id=int(ctx["uid"]),
                                       motiv_trecere=getattr(date, "motiv_trecere", None),
                                       cabinet_id_apelant=ctx["firm"])  # [B1] apartenenta pe obiect
        # [P4] REFUZUL SE RIDICA DINAUNTRUL TRANZACTIEI, ca sa se intoarca si aprobarea de dinainte.
        #
        # Pana azi, `raise` statea DUPA `with`, deci tranzactia se inchidea NORMAL si comitea ce
        # scrisese `auto_aproba_daca_e_cazul`. Un refuz al marcarii lasa elementul `aprobata` fara
        # sa fie depus — chiar forma pe care R128 o reparase venind din client: *un refuz care
        # ingusta optiunile omului* (din `aprobata` nu se mai poate RESPINGE). Ordinea celor doua
        # scrieri era corecta; ce lipsea era ca refuzul sa fie inauntrul limitei lor.
        if not r["ok"]:
            cod = r.get("cod")
            raise (_erori.Conflict if cod == "STARE_GRESITA" else _erori.FaraDrept if cod == "FARA_VERDICT"
                   else _erori.DateInvalide if cod in ("ERORI_DUK", "ATENTIONARI_NECONFIRMATE")   # [C3] 422, nu 404
                   else _erori.Inexistent)(r.get("mesaj", cod))
    return r


# ============================================================
#  [validare_note] NOTELE PREGĂTITE DE ASISTENT — comanda Costin 06.10.2026, pct.1, varianta (a)
# ============================================================
def note_in_coada(tenant_id, uid, cabinet_id):
    """Chemată de middleware DUPĂ orice cerere de modificare reușită pe `/tenants/{id}/…`: notele ciornă scrise de un
    utilizator FĂRĂ drept de validare intră în coadă, iar validatorii primesc o notificare. Un singur punct de intrare
    pentru toate drumurile pe care se naște o notă (autorul vine din cerere, `core/autor_cerere.py`)."""
    with db.get_conn() as conn:
        if coada_api.e_validator(conn, uid):
            return []
        with conn.cursor() as cur:
            schema = repo_declaratii.schema_firmei_cabinetului(cur, tenant_id, cabinet_id)
    if not schema:
        return []
    with db.get_conn(schema) as conn:
        adaugate = coada_api.pune_notele_in_coada(conn, cabinet_id, tenant_id, uid)
    if adaugate:
        with db.get_conn() as conn:
            _uc_comun._notif_note_de_validat(conn, cabinet_id, [a["eticheta"] for a in adaugate], uid, tenant_id=tenant_id,
                                             coada_id=adaugate[0]["coada_id"])
    return adaugate


def _schema_notei(coada_id, ctx):
    """(fel, schema) al elementului, numai pe cabinetul apelantului; pentru o declarație schema e None."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            el = repo_declaratii.element_coada(cur, coada_id)
    if not el or el[3] != ctx["firm"]:
        raise _erori.Inexistent("Element de coadă negăsit (sau alt cabinet).")
    return el[0], (el[2] if el[0] == "nota" else None), el


def jurnal_retrimite(tenant_id, nota_id, ctx, confirma=False):
    """Nota respinsă, corectată, se trimite din nou la validare (act explicit al celui care a pregătit-o)."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            n, _linii = repo_declaratii.nota_cu_linii(cur, schema, nota_id)
        if not n:
            raise _erori.Inexistent("nota #%s nu există" % nota_id)
        # R42: o notă dintr-o lună ÎNCHISĂ nu se mai poate valida, deci nici trimite la validare
        _uc_comun._cere_luna_deschisa(conn, schema, n[1])
        r = coada_api.retrimite_nota(conn, ctx["firm"], tenant_id, nota_id, int(ctx["uid"]), confirma=confirma)
    if r.get("cod") == coada_api.COD_NESCHIMBATA:   # [S3] avertisment, nu refuz: ecranul cere confirmarea
        return r
    if not r["ok"]:
        raise (_erori.Inexistent if r.get("cod") == "INEXISTENT" else _erori.Conflict)(r.get("mesaj"))
    with db.get_conn() as conn:
        _uc_comun._notif_note_de_validat(conn, ctx["firm"], [r["eticheta"]], int(ctx["uid"]), tenant_id=tenant_id,
                                         coada_id=r.get("coada_id"))
    return r
