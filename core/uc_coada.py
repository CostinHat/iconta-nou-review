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
from core.common import cate as _cate
from core import uc_comun as _uc_comun
from core import db, auth_api, coada_api, supervizor
from core.mesaje import (FARA_DREPT_VALIDARE, FARA_DREPT_DEPUNERE, FARA_DREPT_PREGATIRE)
from core import tranzactie
from core import drepturi as _drepturi


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
DECLARATII_TVA = coada_api.DECLARATII_DIN_FACTURI   # declarațiile făcute din facturi (o singură listă)
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
            "contabil": "%.2f" % c["contabil"], "diferenta": "%.2f" % c["diferenta"], "note": c.get("ciorne") or [],
            "note_explica": bool(c.get("ciorne_explica"))} for c in rosii]
    from core import afirmatii as _af
    from core.pdf_util import bani as _bani   # [284] suma scrisă ca pe ecran (63,00), ca în notele numite mai jos
    mesaj = ("Declarația nu intră în coadă: TVA-ul ei nu se potrivește cu balanța lunii — " + "; ".join(
                "%s (rândul %s): declarat %s, contul %s are %s, diferență %s lei" % (
                    d["eticheta"], d["rand"], _bani(d["declarat"]), d["cont"], _bani(d["contabil"]), _bani(d["diferenta"])) for d in dif)
                      + ". Toleranța e rotunjirea la leu.")
    # [deficiența 284] notele nevalidate care mișcă contul se numesc, cu numărul din Registrul-jurnal, documentul și suma
    numite = [d for d in dif if d["note"]]
    for d in numite:
        mesaj += (" %s pe contul %s: %s." % ("Diferența o explică" if d["note_explica"] else
                                             "Note nevalidate (nu acoperă toată diferența)", d["cont"], "; ".join(
            eticheta_nota_tva(n) for n in d["note"])))
    if not numite or not all(d["note_explica"] for d in dif):
        mesaj += (" Validatorul ANAF verifică structura, nu cifrele: corectează documentele (o factură necontată, o notă nevalidată, o "
                  "achiziție fără factură) și generează din nou.")
    return dict(_af.afirmatie("neconformitate", "declaratie_tva", mesaj, unde="perioada %02d/%04d" % (luna_ancora, an),
                              regula="R17_2 = rulajul creditor 4427 și R27_2 = rulajul debitor 4426 ale ferestrei TVA (toleranța 1 leu)"),
                cod=COD_TVA_BALANTA, diferente=dif, mesaj=mesaj, note=_note_unice(dif))


def eticheta_nota_tva(n):
    """„nr. crt. 21 — Factură F1A4 din 16.10.2026, 42,00 lei” — cum se numește nota în refuz (nr. crt. = Registrul-jurnal); [302] ciorna:
    „nota din 16.10.2026 — Factură F1A4 din 16.10.2026, 42,00 lei”."""
    from core.pdf_util import bani as _bani
    # [302] numele vine din bază (`eticheta_nota`: „nr. crt. N din …” la nota validată, „ciorna din …” la ciornă), fără dată a doua oară
    nume = ("nr. crt. %d" % n["nr_curent"] if n.get("nr_curent") else "nota " + (n.get("eticheta_nota") or "nevalidată"))
    return "%s — %s%s lei" % (nume, (n.get("document") or n.get("descriere") or "fără document") + ", ",
                                       _bani(n["suma"]))


def _note_unice(dif):
    """Notele numite, o dată fiecare (o notă poate atinge și 4427, și 4426): pentru legăturile ecranului spre Registrul-jurnal."""
    vazute, out = set(), []
    for d in dif:
        for n in d["note"]:
            if n["nota_id"] not in vazute:
                vazute.add(n["nota_id"])
                out.append(dict(n, eticheta=eticheta_nota_tva(n)))
    return out


COD_D406_BALANTA = "D406_DIFERA_DE_BALANTA"


def poarta_d406_balanta(schema, an, luna, res):
    """[08.10.2026, decizia Costin V1, completarea 2 la U1, verbatim în DECIZII] „Gardă: totalurile GeneralLedgerEntries din D406
    trebuie să egaleze rulajele balanței pe lună; dacă nu, «Trimite în coadă» e blocat.”

    Rulajele BALANȚEI (`documente_api.balanta`, rulajele curente ale fiecărei luni din fereastra D406 — `common.fereastra_d406`),
    adică exact ce vede contabilul pe ecranul Balanță. [08.10.2026, decizia Costin §6 pct.7 — R36] balanța arată numai validatul, ca
    D406: „Porțile D300/D394/D390/D406 compară validat cu validat; dacă există ciorne în lună, dau doar avertisment, nu blocaj.”
    (`coada_adauga`, `ciorne_in_perioada`). Legarea cont cu cont pe notele validate rămâne `d406_reconciliere` (la generare).
    Refuzul (sau None): {cod, mesaj, d406, balanta, diferenta, ciorne}."""
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
                          (" În perioadă sunt %d notă(e) nevalidată(e): nici balanța, nici D406 nu le cuprind până nu le validează "
                           "un om." % ciorne) if ciorne else ""))
    return dict(_af.afirmatie("neconformitate", "declaratie_d406", mesaj, unde="perioada %s – %s" % (di.isoformat(), ds.isoformat()),
                              regula="totalul GeneralLedgerEntries = rulajul balanței pe fereastra D406"),
                cod=COD_D406_BALANTA, d406="%.2f" % gl, balanta="%.2f" % bal, diferenta="%.2f" % (gl - bal), ciorne=ciorne, mesaj=mesaj)


def ciorne_in_perioada(schema, an, luna):
    """[08.10.2026, R36] Câte note NEvalidate are perioada fiscală a declarației (fereastra TVA = fereastra D406, `common.fereastra_d406`)."""
    from core import repo_contabilitate
    from core.common import fereastra_d406 as _fd
    if not luna:
        return 0
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            r = repo_contabilitate.profil_tva(cur)
            di, ds = _fd({"platitor_tva": r[0], "tip_decont": r[1]} if r else {}, an, luna)
            n = repo_contabilitate.note_nevalidate_in_interval(cur, di, ds)
        conn.rollback()
    return n


def fereastra_declaratie(schema, tip, an, luna, trim):
    """[297 + 298] Fereastra documentelor declarației (`coada_api.fereastra_perioadei`, o singură definiție), pe conexiunea firmei."""
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            r = coada_api.fereastra_perioadei(cur, schema, tip, an, luna, trim)
        conn.rollback()
    return r


MAX_NUMITE = coada_api.MAX_NUMITE   # o singură definiție, lângă `nevalidate_acum`
_numite = coada_api._numite


def surse_declaratiei(schema, tip, an, luna, trim):
    """[deficiențele 297 + 298, comanda Costin 17.10.2026 7.2 pct.3, verbatim în DECIZII] „declarațiile se fac numai din notele
    validate sau numesc explicit notele nevalidate pe care se bazează; garda nu se limitează la TVA”. Pentru ORICE declarație:
    amprenta documentelor perioadei (din ea, mai târziu, „depășită”), notele nevalidate ale perioadei și — la D300 / D394 / D390, care
    se fac din facturi — facturile fără notă validată (inclusiv cele cu TVA 0, `control_incrucisat.facturi_necontabilizate`).
    {de_la, pana_la, amprenta, note: [{nota_id, data, eticheta, suma}], facturi: [{factura_id, eticheta}], documente_nevalidate: afirmație „fapt” | None}."""
    de_la, pana_la = fereastra_declaratie(schema, tip, an, luna, trim)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            amp = coada_api.amprenta_surse(cur, schema, de_la, pana_la)
            note, facturi, nevalidate = coada_api.nevalidate_acum(cur, schema, tip, de_la, pana_la)
        conn.rollback()
    return {"de_la": de_la, "pana_la": pana_la, "amprenta": amp, "note": note, "facturi": facturi, "documente_nevalidate": nevalidate}


#: [313, 17.10.2026] notele nu se mai numără („1 notă(e) nevalidată(e)”), se numesc: `%s` = notele, ca în Registrul jurnal
MESAJ_CIORNE_POARTA = ("Comparația cu balanța s-a făcut pe notele validate. Notele nevalidate ale perioadei: %s. Declarația intră în "
                       "coadă; validează-le înainte de depunere.")


MESAJ_CIORNE_BLOCAJ = (" Notele nevalidate ale perioadei: %s — dacă ele corectează diferența, validează-le și generează din nou; până "
                       "atunci evidența e cea validată, iar declarația nu se potrivește cu ea.")


MESAJ_ASTEPTARE = (" După validarea %s, declarația se generează din nou și intră singură în coadă; depunerea la ANAF rămâne clicul "
                   "contabilului.")


def decizie_poarta(refuz, ciorne):
    """(blocaj, avertisment) pentru porțile D300 / D394 / D390 / D406 față de balanță. PURĂ.
    [08.10.2026, decizia Costin §6 pct.7 — R36] „Porțile D300/D394/D390/D406 compară validat cu validat; dacă există ciorne în lună,
    dau doar avertisment, nu blocaj.”
    [PIVOT 09.10.2026, retestul Costin, deficiențele 120 + 210] la D300 / D394 / D390 o DIFERENȚĂ blochează și cu ciorne în perioadă.
    [PIVOT 10.10.2026, comanda Costin pct.3: „D406: blocajul la o diferență față de balanță se extinde și la D406, inclusiv când luna
    are ciorne, ca la D300/D394/D390.”] Deci acum, la toate patru: o diferență blochează, iar mesajul numește și ciornele (dacă ele
    corectează diferența, se validează și se generează din nou); ciornele FĂRĂ diferență dau numai avertisment."""
    # [313, 17.10.2026] `ciorne` = notele nevalidate NUMITE ([{eticheta, ...}]); se numesc în mesaj, nu se numără
    numite = _numite([n["eticheta"] for n in ciorne or []])
    if refuz:
        # [deficiența 284] notele care mișcă TVA-ul sunt numite în refuz
        if refuz.get("note"):
            return dict(refuz, ciorne=len(ciorne or [])), None
        return ((dict(refuz, mesaj=refuz.get("mesaj", "") + MESAJ_CIORNE_BLOCAJ % numite, ciorne=len(ciorne), note=list(ciorne))
                 if ciorne else refuz), None)
    return None, (MESAJ_CIORNE_POARTA % numite if ciorne else None)


def coada_adauga(date, ctx):
    """[P7 · use-case] Corpul rutei `/coada`; docstringul ei a ramas in stratul HTTP."""
    # [B4, 17.09.2026] A pune o declarație în coadă e actul de PREGĂTIRE — cere `poate_pregati`.
    # Până azi flagul apărea doar la setare, nu la folosire: orice angajat sub `cere_cabinet` genera
    # și punea în coadă. Poarta e aici, pe acțiune, nu doar în profil.
    if not _uc_comun._are_permisiune(ctx, "poate_pregati"):
        raise _erori.FaraDrept(FARA_DREPT_PREGATIRE)
    schema = _uc_comun._schema_sau_404(ctx, date.tenant_id)
    body = date.model_dump(exclude_none=True)
    for k in ("tenant_id", "tip", "inceput_la", "inlocuieste"):  # [p15] inceput_la nu merge la generator; [297] nici înlocuirea
        body.pop(k, None)
    # 1) generează declarația pe schema tenantului — [lotul 10, C69] localitatea partenerilor din ANAF, înaintea tranzacției
    from core.uc_declaratii import aduce_localitati_parteneri
    aduce_localitati_parteneri(schema, date.tip)
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
    # 1c) [08.10.2026, decizia Costin V1] D406: totalurile GeneralLedgerEntries = rulajele balanței pe perioadă, altfel blocat.
    # [08.10.2026, decizia Costin §6 pct.7 — R36] „Porțile D300/D394/D390/D406 compară validat cu validat; dacă există ciorne în lună,
    # dau doar avertisment, nu blocaj.” Fără ciorne, diferența blochează ca înainte; cu ciorne, intră în coadă cu avertismentul.
    # [PIVOT 09.10.2026, deficiențele 120 + 210; PIVOT 10.10.2026, comanda Costin pct.3] diferența blochează și cu ciorne, la toate patru.
    avertismente_poarta = []
    # [deficiențele 297 + 298] datele-sursă ale declarației: amprenta (pentru „depășită”), notele nevalidate și facturile fără notă
    # validată ale perioadei, NUMITE — la orice declarație, nu numai la TVA
    _surse = surse_declaratiei(schema, date.tip, date.an, date.luna, date.trim)
    payload["_surse"] = {k: _surse[k] for k in ("de_la", "pana_la", "amprenta")}
    # [329, 18.10.2026] avertismentul documentelor nevalidate NU se mai îngheață aici: lista cozii îl calculează la fiecare citire
    # (`coada_api.nevalidate_acum`); notele numite rămân, pentru motivul lui „depășită” (`coada_api.depasire`)
    payload["_surse"]["note"] = [{"nota_id": n["nota_id"], "data": n["data"], "eticheta": n["eticheta"]} for n in _surse["note"]]
    payload["_cerere"] = {k: v for k, v in body.items() if k != "motiv_trecere"}
    payload["_cerere"].update(tenant_id=date.tenant_id, tip=date.tip)
    if date.tip in DECLARATII_TVA or date.tip == "d406":
        _ancora = date.luna or (int(date.trim) * 3 if date.trim else None)
        _ciorne = _surse["note"]
        _refuz = (poarta_tva_balanta(schema, date.an, date.luna, date.trim) if date.tip in DECLARATII_TVA
                  else poarta_d406_balanta(schema, date.an, _ancora, res))
        _blocaj, _avert = decizie_poarta(_refuz, _ciorne)
        if _blocaj and _blocaj.get("note"):
            # [deficiența 284] declarația așteaptă validarea notelor numite; după ea se generează din nou și intră singură în coadă
            _blocaj = dict(_blocaj, mesaj=_blocaj["mesaj"] + MESAJ_ASTEPTARE % ("notei" if len(_blocaj["note"]) == 1 else "notelor"),
                           asteptare=asteapta_notele(date, ctx, [n["nota_id"] for n in _blocaj["note"]]))
        if _blocaj:
            raise _erori.DateInvalide(_blocaj)
        if _avert and not _surse["facturi"]:
            avertismente_poarta.append(_avert)
    # [lotul 10, deficiența 436, comanda Costin 10.2 pct.6, verbatim în DECIZII] „când declarația știe că are cifra greșită din note
    # nevalidate, depunerea se blochează până la validare, cu motivul lângă buton, la toate declarațiile.” Declarația calculată din evidența
    # validată (`coada_api.DECLARATII_DIN_EVIDENTA`) nu intră în coadă cu note nevalidate în fereastra ei: le numește, iar după validarea
    # lor se generează din nou și intră singură (așteptarea de la 284 — același drum ca poarta TVA)
    _bl_note = coada_api.blocaj_note_nevalidate(date.tip, _surse["note"])
    if _bl_note:
        _bl_note = dict(_bl_note, mesaj=_bl_note["mesaj"] + MESAJ_ASTEPTARE % ("notei" if len(_bl_note["note"]) == 1 else "notelor"),
                        asteptare=asteapta_notele(date, ctx, [n["nota_id"] for n in _bl_note["note"]]))
        raise _erori.DateInvalide(_bl_note)
    _nev = (_surse["documente_nevalidate"] or {}).get("motiv")
    if _nev and _nev not in avertismente_poarta and (_surse["facturi"] or not avertismente_poarta):
        avertismente_poarta.append(_nev)
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
        _inlocuit = getattr(date, "inlocuieste", None)
        if _inlocuit:
            # [297 + 299] „Generează din nou” / „Înlocuiește”: elementul activ iese din coadă în ACEEAȘI tranzacție cu intrarea celui nou
            with conn.cursor() as cur:
                if not coada_api.inlocuieste(cur, int(_inlocuit), ctx["firm"], ctx["uid"],
                                             "Înlocuită de declarația generată din nou (%s)." % _cine(ctx)):
                    raise _erori.Conflict("Declarația de înlocuit nu mai e în coadă (a fost depusă, retrasă sau înlocuită între timp).")
        r = coada_api.adauga_in_coada(
            conn, ctx["firm"], date.tenant_id, date.tip, date.an, payload,
            creat_de=str(ctx["uid"]), creat_de_id=int(ctx["uid"]), luna=date.luna, trim=date.trim,
            inceput_la=date.inceput_la)  # [p15]
    if not r["ok"] and r.get("cod") == "DEJA_IN_COADA":
        raise _erori.Conflict(refuz_deja_in_coada(date))
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
    r["surse_note"] = payload["_surse"]["note"]
    if avertismente_poarta:
        r["avertismente_poarta"] = avertismente_poarta
    if r.get("ok"):
        with db.get_conn() as conn:
            r["pas_urmator"] = pas_urmator(conn, ctx)
    _anunta_validatorii(r, date, ctx)
    return r


def _cine(ctx):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            return repo_declaratii.numele_utilizatorului(cur, int(ctx["uid"])) or "un coleg"


def perioada_text(an, luna, trim):
    """„10/2026”, „T3/2026”, „anul 2026” — perioada declarată, nu termenul."""
    return "%02d/%d" % (luna, an) if luna else "T%d/%d" % (trim, an) if trim else "anul %d" % an


def refuz_deja_in_coada(date):
    """[deficiența 299, comanda Costin 17.10.2026 7.2 pct.4] refuzul cu perioada declarată (nu termenul), tipul cum îl scrie formularul,
    cine a pregătit-o și în ce stare e, plus drumul: deschide-o sau înlocuiește-o cu cea generată acum."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            perioada = (coada_api.scadente.scadenta(date.tip, date.an, luna=date.luna, trim=date.trim)
                        if coada_api.scadente.are_termen(date.tip, date.an, luna=date.luna, trim=date.trim) else None)
            el = coada_api.element_activ(cur, date.tenant_id, date.tip, perioada) if perioada else None
    per = perioada_text(date.an, date.luna, date.trim)
    if not el:
        return {"ok": False, "cod": "DEJA_IN_COADA", "mesaj": "Există deja în coadă o declarație %s activă pentru %s." % (date.tip.upper(), per)}
    cid, stare, *_x, cine = el
    return {"ok": False, "cod": "DEJA_IN_COADA", "coada_id": cid, "stare": stare,
            "mesaj": ("Există deja în coadă o declarație %s pentru %s, pregătită de %s, %s. Deschide-o, sau înlocuiește-o cu cea "
                      "generată acum (cea veche iese din coadă)." % (date.tip.upper(), per, cine or "un coleg",
                                                                  "validată, gata de depunere" if stare == "aprobata" else "la validare")),
            "actiune": "Înlocuiește"}


def _anunta_validatorii(r, date, ctx):
    """[p57_notif] notifica validatorii ca e ceva de validat.
    [deficiența 339, 18.10.2026] numai cu validarea în doi a declarațiilor EFECTIVĂ (`patru_ochi_stare`, aceeași sursă ca aprobarea și
    ecranul): fără ea declarația nu așteaptă nicio validare (se aprobă la depunere, `auto_aproba_daca_e_cazul`), iar „un element nou de
    validat” trimis validatorilor era fals. Notele trimise de asistenți se validează întotdeauna — notificarea lor e alta."""
    if not r.get("ok"):
        return
    try:
        with db.get_conn() as conn:
            if coada_api.patru_ochi_stare(conn, ctx["firm"])["efectiv"]:
                _uc_comun._notif_de_validat(conn, ctx["firm"], date.tip,
                                            r.get("perioada") or ("%s/%s" % (date.luna or date.trim or "", date.an)),
                                            int(ctx["uid"]), tenant_id=date.tenant_id, coada_id=r.get("coada_id"))
    except Exception as _e:   # declarația a intrat; o notificare căzută se scrie în jurnal, nu se înghite
        import logging
        logging.getLogger("iconta").warning("notificare de validat esuata (coada %s): %s", r.get("coada_id"), _e)


def coada_regenereaza(coada_id, ctx):
    """[deficiența 297] „Generează din nou” pe o declarație din coadă (depășită sau nu): aceeași cerere ca la prima generare, păstrată în
    element, trece din nou prin `coada_adauga` (aceleași porți), iar elementul vechi iese din coadă în aceeași tranzacție."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            el = coada_api.element_declaratie(cur, coada_id)
    if not el or el[0] != ctx["firm"]:
        raise _erori.Inexistent("Element de coadă negăsit (sau alt cabinet).")
    cabinet_id, tenant_id, tip, stare, payload, fel = el
    if fel == "nota" or stare not in coada_api.STARI_ACTIVE:
        raise _erori.Conflict("Se generează din nou numai o declarație care așteaptă validarea sau depunerea.")
    cerere = (payload or {}).get("_cerere")
    if not cerere:
        raise _erori.Conflict({"ok": False, "cod": "FARA_CERERE", "mesaj": (
            "Declarația a intrat în coadă înainte ca aplicația să-i păstreze cererea, deci nu se poate genera din nou de aici. Generează-o "
            "din Declarații (%s %s) și alege „Înlocuiește”." % (tip.upper(), perioada_text(payload.get("_an"), payload.get("_luna"),
                                                                                            payload.get("_trim"))))})
    date = _CerereSalvata(dict(cerere, inlocuieste=coada_id))
    return coada_adauga(date, ctx)


# ============================================================
#  [deficiența 284] DECLARAȚIA CARE AȘTEAPTĂ VALIDAREA NOTELOR — comanda Costin 16.10.2026, completarea 1 la lotul 6 (verbatim în DECIZII):
#  „După validarea notei, declarația se regenerează singură și intră în coadă; depunerea la ANAF rămâne clicul contabilului.”
# ============================================================
class _CerereSalvata:
    """Cererea `POST /coada` refăcută din rândul de așteptare (aceleași câmpuri ca `main.CoadaIn`; `coada_adauga` citește atributele și
    `model_dump`)."""
    _CAMPURI = ("tenant_id", "tip", "an", "luna", "trim", "manual", "obligatii", "cota", "date_extra", "ca_an_precedent_eur",
                "inceput_la", "motiv_trecere", "inlocuieste")

    def __init__(self, d):
        for k in self._CAMPURI:
            setattr(self, k, d.get(k))

    def model_dump(self, exclude_none=False):
        d = {k: getattr(self, k) for k in self._CAMPURI}
        return {k: v for k, v in d.items() if v is not None} if exclude_none else d


def asteapta_notele(date, ctx, note_ids):
    """Scrie (sau înlocuiește) așteptarea declarației: o singură așteptare deschisă pe (firmă, declarație, perioadă). Întoarce id-ul."""
    import json as _json
    cerere = date.model_dump(exclude_none=True)
    from core import chei_unice as _chei
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            def _scrie():
                repo_declaratii.inchide_asteptarea_deschisa(cur, date.tenant_id, date.tip, date.an, date.luna, date.trim,
                                                            _json.dumps({"cod": "INLOCUITA"}))
                return repo_declaratii.insereaza_asteptare(cur, int(ctx["firm"]), date.tenant_id, date.tip, date.an, date.luna, date.trim,
                                                           _json.dumps(cerere, default=str), int(ctx["uid"]), ctx.get("rol"),
                                                           sorted({int(i) for i in note_ids}))
            # [lotul 10, C73 / U3] două cereri simultane pe aceeași declarație și perioadă: a doua nu vedea așteptarea primei (necomisă) ca
            # s-o închidă, iar indexul `declaratii_in_asteptare_deschisa` o refuza cu 500. Operația e „scrie SAU ÎNLOCUIEȘTE”: se reia,
            # iar a doua oară închide așteptarea comisă între timp și o înlocuiește — exact ca două cereri una după alta.
            aid = _chei.reincearca_la_dublura(cur, ("declaratii_in_asteptare_deschisa",), _scrie, lambda c, e: _chei.CheieDublata(
                "Declarația nu s-a putut pune în așteptare: alte cereri pe aceeași declarație și perioadă se scriu chiar acum. "
                "Încearcă din nou."))
        conn.commit()
    return aid


def reia_declaratiile_in_asteptare(cabinet_id):
    """Chemată de middleware DUPĂ orice cerere de modificare reușită a cabinetului (validarea unei note trece pe două drumuri: Registrul
    jurnal și coada — `jurnal_api.valideaza`; ambele sunt cereri de modificare). O așteptare se reia când niciuna din notele ei nu mai e
    nevalidată (validate sau șterse): declarația se generează din nou prin `coada_adauga`, cu contextul celui care a trimis-o (drepturile
    se citesc din nou). Rezultatul — intrată în coadă sau refuzată din nou, cu motivul — se scrie pe rând și se anunță prin notificare.
    Întoarce lista rezultatelor [{id, ok, mesaj}]."""
    import json as _json
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            deschise = repo_declaratii.asteptari_deschise(cur, int(cabinet_id))
    from core import repo_contabilitate
    out = []
    for aid, tenant_id, note_ids, schema in deschise:
        def _ramase(conn, _ids=note_ids):
            with conn.cursor() as cur:
                n = repo_contabilitate.cate_nevalidate_dintre(cur, list(_ids))
            conn.rollback()
            return n
        exista, ramase = db.pe_firma_existenta(schema, _ramase)
        if not exista or ramase:   # [lotul 10] firma ștearsă între timp: așteptarea ei nu se mai reia
            continue
        with db.get_conn() as conn:   # o singură reluare, chiar cu două cereri simultane
            with conn.cursor() as cur:
                rand = repo_declaratii.revendica_asteptarea(cur, aid)
            conn.commit()
        if not rand:
            continue
        cerere, uid, rol, tip, an, luna, trim = rand
        ctx = {"ok": True, "uid": uid, "rol": rol, "firm": int(cabinet_id)}
        per = "%s %s/%d" % (tip.upper(), ("%02d" % luna) if luna else ("T%d" % trim if trim else ""), an)
        try:
            r = coada_adauga(_CerereSalvata(cerere if isinstance(cerere, dict) else _json.loads(cerere)), ctx)
            rez = {"ok": True, "coada_id": r.get("coada_id"),
                   "mesaj": "%s: notele au fost validate, declarația s-a generat din nou și %s" % (
                       per, (r.get("pas_urmator") or {}).get("mesaj") or "a intrat în coadă.")}
        except _erori.EroareDeDomeniu as e:
            det = e.detaliu
            rez = {"ok": False, "mesaj": "%s: notele au fost validate, dar declarația tot nu intră în coadă — %s" % (
                per, (det.get("mesaj") if isinstance(det, dict) else str(det)) or "refuzată")}
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                repo_declaratii.scrie_rezultatul_asteptarii(cur, aid, _json.dumps(rez))
            from core import notificari_api as _notif
            _notif.adauga(conn, uid, "declaratie_reluata", _uc_comun._cu_firma(conn, tenant_id, rez["mesaj"]),
                          link=("validat:%d" % rez["coada_id"]) if rez.get("coada_id") else None)
            conn.commit()
        out.append(dict(rez, id=aid))
    return out


def reia_in_fundal(cabinet_id):
    """`reia_declaratiile_in_asteptare` pe un fir separat; eșecul nu e tăcut (`observare.esec_secundar`)."""
    import threading

    def _ruleaza():
        try:
            reia_declaratiile_in_asteptare(cabinet_id)
        except Exception as e:
            from core import observare as _obs
            _obs.esec_secundar("declaratii in asteptare reluate dupa validarea notelor", e)
    threading.Thread(target=_ruleaza, name="reia-asteptare-%s" % cabinet_id, daemon=True).start()


#: [deficiența 287] ce urmează după „Trimite în coadă”, spus după starea REALĂ: validarea în doi efectivă (`coada_api.patru_ochi_stare`) și
#: dreptul de depunere al celui care a trimis. Fără validare în doi, `depune` trece direct (aprobarea se face la depunere).
PAS_VALIDARE = "a fost trimisă la validare: validarea în doi e activă, deci un coleg o aprobă înainte de depunere."
PAS_DEPUNERE = ("e în coadă, gata de depunere: validarea în doi e oprită, deci o depui tu, din „De depus”. Depunerea la ANAF rămâne "
                "clicul tău.")
PAS_DEPUNERE_ALTCINEVA = "e în coadă, gata de depunere: o depune cine are în cabinet dreptul de depunere."


def pas_urmator(conn, ctx):
    """Statutul declarației trimise (afirmație tipată, `statut` = `cod`: `validare` / `depunere` / `depunere_altcineva`), cu `mesaj`."""
    from core import afirmatii as _af
    if coada_api.patru_ochi_stare(conn, ctx["firm"])["efectiv"]:
        cod, mesaj = "validare", PAS_VALIDARE
    elif _uc_comun._are_permisiune(ctx, "poate_depune"):
        cod, mesaj = "depunere", PAS_DEPUNERE
    else:
        cod, mesaj = "depunere_altcineva", PAS_DEPUNERE_ALTCINEVA
    return dict(_af.afirmatie("statut", "declaratie_trimisa", mesaj, statut=cod, statut_din=None), cod=cod, mesaj=mesaj)


def coada_lista(stare, ctx):
    """[P7 · use-case] Corpul rutei `/coada`; docstringul ei a ramas in stratul HTTP."""
    if stare is not None and stare not in coada_api.STARI:
        raise _erori.DateInvalide("stare necunoscută: %r (stările cozii: %s)"
                                % (stare, ", ".join(coada_api.STARI)))
    with db.get_conn() as conn:
        lista = coada_api.lista_coada(conn, ctx["firm"], stare)
        vizibile = _uc_comun._firme_vizibile(conn, ctx)   # [C26, clasa] asistentul: numai elementele firmelor alocate lui
    return {"coada": lista if vizibile is None else [x for x in lista if x["tenant_id"] in vizibile]}


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
                        from core import eticheta_nota as _eticheta_nota
                        note.append({"nota": {"id": n[0], "data": n[1].isoformat(), "descriere": n[2], "document_ref": n[3],
                                              "status": n[4], "sursa": n[5],
                                              # [258] nota cum o arată Registrul jurnal, nu prin id-ul intern
                                              "eticheta": _eticheta_nota.nota(cur, _schema_nota, n[0]),
                                              "stinge": _jst.facturi_stinse(cur, _schema_nota, [n[0]]).get(n[0])},
                                     "linii": [{"debit": a, "credit": b, "suma": float(c)} for a, b, c in linii]})
        if not note:
            raise _erori.Inexistent("Nota nu mai există în jurnal (a fost ștearsă).")
        return {"fel": "nota", "nota": note[0]["nota"], "linii": note[0]["linii"], "note": note}
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            row = repo_declaratii.continutul_din_coada(cur, coada_id, ctx["firm"])
            depasita = coada_api.depasire_element(cur, coada_id) if row else None   # [323] fereastra spune „depășită”
    if not row:
        raise _erori.Inexistent("Element de coadă negăsit (sau alt cabinet).")
    tip, payload, _an, _luna = row
    payload = payload or {}
    xml = payload.get("xml") or ""
    if xml:
        rez = _duk.valideaza(xml, tip, an=_an, luna=_luna)  # java blocant - verdictul oficial ANAF
    else:
        rez = {"stare": "gri", "erori": "", "severitate": None,
               "temei": "Declarația din coadă nu are XML-ul salvat.", "limita": ""}
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
            "temei": rez.get("temei"), "limita": rez.get("limita"),
            "depasita": depasita}   # [323] afirmația tipată din `coada_api.depasire` (fel, tip, motiv, mesaj), sau None


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
        if cod == "DEPASITA":   # [297] declarația depășită nu se validează: refuzul poartă drumul („Generează din nou”)
            raise _erori.Conflict({"cod": cod, "mesaj": r["mesaj"], "coada_id": coada_id, "actiune": "Generează din nou"})
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



#: Câte elemente se validează într-o singură cerere (o zi de Z-uri pe un portofoliu încape; o cerere nu ține serverul minute în șir).
MAX_APROBARI_DEODATA = 200


def coada_aproba_mai_multe(ids, ctx):
    """[08.10.2026, decizia Costin pct.3 la §6 S6, verbatim în DECIZII] „Coada de validare permite validarea mai multor note deodată
    (Z-urile vin zilnic).” Fiecare element trece prin `coada_aproba` — aceleași porți (dreptul, patru ochi, apartenența la cabinet,
    verdictul), câte o tranzacție pe element: un refuz nu anulează validările celorlalte, iar răspunsul îl numește.
    {"validate": [id], "refuzate": [{"id", "mesaj"}]}."""
    if not _uc_comun._are_permisiune(ctx, "poate_valida"):
        raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
    ids = list(dict.fromkeys(int(i) for i in (ids or [])))
    if not ids:
        raise _erori.DateInvalide("Alege cel puțin o notă de validat.")
    if len(ids) > MAX_APROBARI_DEODATA:
        raise _erori.DateInvalide("Se validează cel mult %s deodată; ai ales %d." % (_cate(MAX_APROBARI_DEODATA, "notă", "note"), len(ids)))
    validate, refuzate = [], []
    for i in ids:
        try:
            coada_aproba(i, {}, ctx)
            validate.append(i)
        except _erori.EroareDeDomeniu as e:
            from core import afirmatii as _af
            d = e.args[0] if e.args else str(e)
            mesaj = d.get("mesaj", str(d)) if isinstance(d, dict) else str(d)
            # [258] `unde` fără id-ul intern (elementul îl poartă în `id`)
            refuzate.append(dict(_af.afirmatie("neconformitate", "aprobare_refuzata", mesaj, unde="nota aleasă la validare",
                                               regula="fiecare notă trece prin porțile aprobării ei"), id=i, mesaj=mesaj))
    return {"ok": True, "validate": validate, "refuzate": refuzate}


MESAJ_RENUNTA_ALTUI = ("Declarația a pregătit-o altcineva, iar validarea în doi e oprită: la ea renunță cine a pregătit-o sau cine o "
                       "depune (dreptul «Poate depune»). Tu o poți vedea.")


MOTIV_RENUNTARE = "Retrasă din coadă de cel care a pregătit-o."


def coada_respinge(coada_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/coada/{coada_id}/respinge`; docstringul ei a ramas in stratul HTTP."""
    if not _uc_comun._are_permisiune(ctx, "poate_valida"):
        raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
    # [retest 07.10 R1] nota se respinge pe schema firmei ei: respingerea stornează în aceeași tranzacție mișcarea de stoc a
    # documentului (`stocuri_anulare.storneaza`) — ori ambele, ori niciuna
    _fel, _schema_nota, _el = _schema_notei(coada_id, ctx)
    if _fel != "nota":
        # [deficiența 293, comanda Costin 16.10.2026, verbatim în DECIZII] „Pe o declarație a altcuiva, fără dreptul de depunere, nu se
        # oferă nicio acțiune în afară de vizualizare; serverul refuză la fel.” Fără validarea în doi, „respinge” e RENUNȚAREA la
        # declarație — a celui care a pregătit-o sau a celui care o depune; cu validarea în doi e actul validatorului (rămâne).
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                autor = repo_declaratii.autorul_elementului(cur, coada_id)
            efectiv = coada_api.patru_ochi_stare(conn, ctx["firm"])["efectiv"]
        if not efectiv and autor != int(ctx["uid"]) and not _uc_comun._are_permisiune(ctx, "poate_depune"):
            raise _erori.FaraDrept(MESAJ_RENUNTA_ALTUI)
    motiv = (date.motiv or "").strip()
    if _fel != "nota" and not motiv and not efectiv and autor == int(ctx["uid"]):
        # [deficiența 313, comanda Costin 17.10.2026 7.2] renunțarea la PROPRIA declarație, fără validarea în doi, nu e o respingere:
        # motivul e opțional; respingerea unei lucrări a altcuiva rămâne cu motiv obligatoriu (îl citește cel care a pregătit-o)
        motiv = MOTIV_RENUNTARE
    with db.get_conn(_schema_nota) as conn:
        r = coada_api.respinge(conn, coada_id, str(ctx["uid"]), motiv, respins_de_id=int(ctx["uid"]),
                               cabinet_id_apelant=ctx["firm"],  # [B1] apartenenta pe obiect
                               schema_nota=_schema_nota)
        if not r["ok"]:
            conn.rollback()
    if not r["ok"]:  # [motiv_lipsa_400_v1] MOTIV_LIPSA e input invalid -> 400
        _cod = r.get("cod")
        # [B1] ALT_CABINET -> 404 (Inexistent) prin ramura else.
        # [lotul 10, C73 / U2] DEJA_RESPINS = altă cerere a respins documentul între timp (cursa) -> 409, ca starea greșită
        _http = (_erori.Conflict if _cod in ("STARE_GRESITA", "DEJA_RESPINS") else _erori.CerereGresita if _cod in ("MOTIV_LIPSA", "STOC_IESIT")
                 else _erori.Inexistent)
        raise _http(r.get("mesaj", _cod))
    # [p57_notif] notifica pregatitorul cu motivul
    try:
        with db.get_conn() as conn:
            if motiv != MOTIV_RENUNTARE:   # cine renunță la propria declarație nu-și trimite notificare
                _uc_comun._notif_pregatitor(conn, coada_id, "respinsa", motiv=motiv)
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
    _schema_notei(coada_id, ctx)   # [C26, clasa] și firma elementului trebuie să fie a asistentului
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
                "mesaj": ("Înainte de depunere se cere o confirmare scrisă pentru %s pe firma și perioada asta. "
                          "Depunerea nu e blocată: confirmă-le, cu motiv, și continuă."
                          % _cate(len(_ramase), "constatare certă", "constatări certe")),
                # constatarile se trimit AȘA CUM SUNT: sunt deja afirmații tipate, produse de
                # `control_incrucisat`. Reîmpachetarea lor aici ar fi fost o a doua afirmație,
                # netipată — și cine o citea n-ar fi știut care e cea adevărată.
                "constatari": _ramase,
                "actiune": "Confirmă fiecare atenționare (cu motivul tău), apoi trimite din nou.",
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
            if _c == "DEPASITA":   # [297] „«Confirmă depunerea» oprit pe o declarație depășită”
                raise _erori.Conflict({"cod": _c, "mesaj": _ap["mesaj"], "coada_id": coada_id, "actiune": "Generează din nou"})
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
            if cod == "DEPASITA":
                raise _erori.Conflict({"cod": cod, "mesaj": r["mesaj"], "coada_id": coada_id, "actiune": "Generează din nou"})
            raise (_erori.Conflict if cod == "STARE_GRESITA" else _erori.FaraDrept if cod == "FARA_VERDICT"
                   else _erori.DateInvalide if cod in ("ERORI_DUK", "ATENTIONARI_NECONFIRMATE", "PERIOADA_NEINCHEIATA")   # [C3] 422; [383]
                   else _erori.Inexistent)(r.get("mesaj", cod))
    # [deficiența 320] „o declarație pregătită de tine a fost depusă”: cine a pregătit-o află, când a depus-o altcineva
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                autor = repo_declaratii.autorul_elementului(cur, coada_id)
            if autor and autor != int(ctx["uid"]):
                _uc_comun._notif_pregatitor(conn, coada_id, "depusa")
                conn.commit()
    except Exception as _e:  # noqa: BLE001 — depunerea s-a făcut; notificarea căzută se semnalează, nu se ascunde
        from core import observare as _obs
        _obs.esec_secundar("notificare pregatitor (depunere, coada %s)" % coada_id, _e)
    return r


# ============================================================
#  [368] NOTELE INTERNE ALE FIRMEI ÎN PARTIDĂ SIMPLĂ — decizia Costin 19.10.2026 „Se validează automat” (DECIZII „Închiderea lotului 9”)
# ============================================================
#: [368] marja pentru ceasul bazei (aplicația și baza sunt pe același server): notele unei scrieri au `creat_la` după începutul ei
_MARJA_CEAS_SECUNDE = 2


def inceputul_scrierii():
    """[368] Momentul de dinaintea unei scrieri, de la care se caută notele ei (`coada_api.ciorne_din_cerere`): ceasul aplicației minus
    marja. Aceeași definiție pentru middleware-ul cererii și pentru drumurile fără cerere (API v1, facturile recurente, WooCommerce)."""
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(seconds=_MARJA_CEAS_SECUNDE)


def note_interne(tenant_id, uid, cabinet_id, de_la, in_plus=()):
    """Chemată de middleware DUPĂ orice cerere de modificare reușită pe `/tenants/{id}/…`, ÎNAINTEA cozii: la o firmă în partidă simplă
    (PFA / II / IF) notele ciornă scrise în cerere (`coada_api.ciorne_din_cerere`, oricine e autorul) se validează automat, ca note
    interne, pe drumul validării (`jurnal_api.valideaza_interne`, cu toate regulile ei). Nota refuzată rămâne ciornă: la un autor fără
    drept de validare intră apoi în coadă (`note_in_coada`), ca orice ciornă; refuzul se întoarce și ecranului (antetul din middleware).
    -> {"interne": [eticheta], "refuzate": [{"eticheta", "motiv"}]}"""
    schema = _schema_firmei(tenant_id, cabinet_id)
    return note_interne_schema(schema, uid, de_la, in_plus) if schema else {"interne": [], "refuzate": []}


def _schema_firmei(tenant_id, cabinet_id):
    """Schema firmei, numai dacă e a cabinetului (altfel None) — o singură citire pentru notele interne și coadă."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            return repo_declaratii.schema_firmei_cabinetului(cur, tenant_id, cabinet_id)


def note_interne_schema(schema, uid, de_la, in_plus=()):
    """`note_interne` pe schema firmei — și pentru drumurile care scriu note în afara unei cereri `/tenants/{id}/…` (un job de fundal:
    `uid=None`, notele fără autor). `in_plus`: note mai vechi de reîncercat (numai cele încă ciornă). Comite."""
    gol = {"interne": [], "refuzate": []}
    from core import eticheta_nota as _et
    from core import jurnal_api as _jurnal
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            if not coada_api.partida_simpla(cur):
                return gol
            ids = coada_api.ciorne_din_cerere(cur, uid, de_la)
            # [368] și ciornele mai vechi a căror cauză de refuz a rezolvat-o cererea (`autor_cerere.reincearca_interna`), încă ciorne
            ids = ids + [n for n in coada_api.ciorne_dintre(cur, in_plus) if n not in ids]
        if not ids:
            return gol
        validate, refuzate = _jurnal.valideaza_interne(conn, schema, ids, cu_cod=True)
        with conn.cursor() as cur:
            et = dict(_et.note(cur, schema, validate + [n for n, _, _ in refuzate]))
    from core import afirmatii as _af
    # refuzul e o afirmație despre nota firmei: tipată (`neconformitate` — nota și regula care n-o lasă validată), cu eticheta pentru ecran
    return {"interne": [et.get(n, _et.NOTA_INEXISTENTA) for n in validate],
            "refuzate": [_af.afirmatie("neconformitate", "nota_interna_refuzata", m, unde=et.get(n, _et.NOTA_INEXISTENTA), regula=cod,
                                       eticheta=et.get(n, _et.NOTA_INEXISTENTA)) for n, m, cod in refuzate]}


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
    schema = _schema_firmei(tenant_id, cabinet_id)
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
        # [C26, clasa] un asistent nu vede, nu aprobă, nu respinge și nu depune elementul unei firme care nu i-a fost alocată
        vizibil = bool(el) and el[3] == ctx["firm"] and _uc_comun._firma_vizibila(conn, ctx, el[1])
    if not vizibil:
        raise _erori.Inexistent("Element de coadă negăsit (sau alt cabinet).")
    return el[0], (el[2] if el[0] == "nota" else None), el


def jurnal_retrimite(tenant_id, nota_id, ctx, confirma=False):
    """Nota respinsă, corectată, se trimite din nou la validare (act explicit al celui care a pregătit-o)."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            n, _linii = repo_declaratii.nota_cu_linii(cur, schema, nota_id)
        if not n:
            raise _erori.Inexistent("Nota nu mai există: a fost ștearsă între timp.")   # [258] fără id-ul intern
        # R42: o notă dintr-o lună ÎNCHISĂ nu se mai poate valida, deci nici trimite la validare
        _uc_comun._cere_luna_deschisa(conn, schema, n[1])
        r = coada_api.retrimite_nota(conn, ctx["firm"], tenant_id, nota_id, int(ctx["uid"]), confirma=confirma)
    if r.get("cod") == coada_api.COD_NESCHIMBATA:   # [S3] avertisment, nu refuz: ecranul cere confirmarea
        return r
    if not r["ok"]:
        if r.get("cod") == _drepturi.COD_CIORNA_ALTUI:   # [deficiența 246] un drept, nu o stare: 403, ca refuzul din bază
            raise _erori.FaraDrept(r.get("mesaj"))
        raise (_erori.Inexistent if r.get("cod") == "INEXISTENT" else _erori.Conflict)(r.get("mesaj"))
    with db.get_conn() as conn:
        _uc_comun._notif_note_de_validat(conn, ctx["firm"], [r["eticheta"]], int(ctx["uid"]), tenant_id=tenant_id,
                                         coada_id=r.get("coada_id"))
    return r
