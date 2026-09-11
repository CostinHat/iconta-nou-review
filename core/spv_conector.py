# -*- coding: utf-8 -*-
"""
core/spv_conector.py — conectorul UNIC SPV/ANAF (OAuth2).

Sursa arhitecturii: ARHITECTURA_SPV.md, sectiunea "CONECTORUL SPV" (17.07.2026).
Parametrii OAuth (endpointuri, 90/365 zile, 1000 apeluri/min) sunt VERIFICATI la
sursa oficiala ANAF (Oauth_procedura_inregistrare_aplicatii_portal_ANAF.pdf) — nu se
recalculeaza din memorie.

FACE: autorizare OAuth, stocare token (CRIPTAT Fernet), refresh cu ROTATIE, apel_anaf().
NU FACE: e-Factura / e-Transport. Alea sunt F126/F160/F121, construite PESTE conector.
Daca intra logica de facturi aici, scopul e ratat.

CAPCANA CRITICA — ROTATIA REFRESH TOKEN-ULUI (ARHITECTURA_SPV.md):
La /token cu grant_type=refresh_token, ANAF intoarce valori NOI si pentru access_token
SI pentru refresh_token. AMANDOUA trebuie salvate. Daca salvezi doar access-ul nou,
urmatorul refresh esueaza -> cabinetul reautorizeaza cu stickul. De aceea
_proceseaza_raspuns_token() salveaza intotdeauna AMBELE valori din raspuns.

APELURI REALE catre ANAF: schimba_cod_pe_token(), reimprospateaza_pereche(), apel_anaf().
Testul functional real il face Costin cu certificatul lui (TestOauth). Testele din
test_spv_conector.py folosesc MOCK, nu ANAF real.
"""
import os
import json
import base64
import time
import urllib.parse
from datetime import datetime, timezone, timedelta

import requests

from core import nucleu
from core import db
from core.common import cfg, cfg_secret

MODUL = "spv_conector"

# --- Parametri ANAF (env, cititi LA APEL prin cfg — item 5; endpointurile au
#     fallback = valorile verificate la sursa). Chei: ANAF_CLIENT_ID / ANAF_CLIENT_SECRET,
#     ANAF_REDIRECT_URI, ANAF_AUTHORIZE_URL, ANAF_TOKEN_URL. (ANAF_REVOKE_URL era declarat
#     dar nefolosit nicaieri -> eliminat, nu convertit.) ---
_AUTHORIZE_URL_DEFAULT = "https://logincert.anaf.ro/anaf-oauth2/v1/authorize"
_TOKEN_URL_DEFAULT     = "https://logincert.anaf.ro/anaf-oauth2/v1/token"

# STATE_SECRET = JWT_SECRET (state CSRF = token semnat, fara tabel nou). Citit LA APEL prin
# cfg_secret (EXCEPTIE DURA la absenta/gol, NICIODATA default — secret gol = tokenuri forjabile).
# Vezi DECIZII 22.07 (vulnerabilitate default gol pe cheie HMAC).
STATE_DURATA_SEC  = 600            # 10 minute (ARHITECTURA: state expira in 10 min)
REFRESH_DURATA_ZILE = 365          # refresh token 365 zile (verificat la sursa ANAF)
ACCES_IMPLICIT_SEC  = 90 * 86400   # fallback daca raspunsul nu da expires_in (90 zile)
MARJA_REFRESH_ZILE  = 7            # cronul reimprospateaza sub aceasta marja
MAX_BACKOFF_429     = 3            # reincercari la 429 (limita ANAF 1000/min)


# ============================================================
#  EXCEPTII
# ============================================================
class EroareSpv(Exception):
    """Baza pentru erorile conectorului."""


class EroareSpvNeconectat(EroareSpv):
    """Nu exista token activ pentru cabinet (nu autorizat / refresh esuat)."""


class EroareSpvFaraDrept(EroareSpv):
    """403 ANAF: certificatul nu are drept pe CIF-ul cerut."""


class EroareSpvRefreshEsuat(EroareSpv):
    """Refresh-ul a esuat (refresh_token invalid/expirat)."""


# ============================================================
#  PRINCIPAL — cabinet XOR firma gratuita (F160, DECIZII 18.07)
#  Tokenul apartine unui PRINCIPAL, nu unei tabele de firme. Aici e SURSA UNICA a
#  branch-ului cabinet/gratuit (GARDUL 2): ia_token_activ/salveaza/stare/refresh trec pe aici.
# ============================================================
from collections import namedtuple

Principal = namedtuple("Principal", ["kind", "id"])   # kind: 'firm' (cabinet) | 'tenant' (gratuit)


def principal_firm(fid):
    return Principal("firm", int(fid))


def principal_tenant(tid):
    return Principal("tenant", int(tid))


def _principal_sql(p):
    """(cond_where, params, coloana) pentru un principal. Unicul loc care stie schema cheii."""
    if p.kind == "firm":
        return "accounting_firm_id = %s AND tenant_id IS NULL", (int(p.id),), "accounting_firm_id"
    if p.kind == "tenant":
        return "tenant_id = %s AND accounting_firm_id IS NULL", (int(p.id),), "tenant_id"
    raise EroareSpv("principal invalid: %r" % (p,))


def principal_din_rand(accounting_firm_id, tenant_id):
    """Principalul unui rand spv_token (pt F177/refresh - GARDUL 3: nu presupune firm)."""
    if accounting_firm_id is not None:
        return principal_firm(accounting_firm_id)
    if tenant_id is not None:
        return principal_tenant(tenant_id)
    raise EroareSpv("rand spv_token fara principal (nici firm, nici tenant)")


# ============================================================
#  CRIPTARE (Fernet) — PURA (primeste cheia din env la apel)
# ============================================================
def _fernet():
    """Instanta Fernet din SPV_FERNET_KEY. Ridica daca lipseste (nu stoca in clar)."""
    from cryptography.fernet import Fernet
    cheie = os.environ.get("SPV_FERNET_KEY", "")
    if not cheie:
        raise EroareSpv("SPV_FERNET_KEY lipseste din env — token-urile nu se stocheaza in clar")
    return Fernet(cheie.encode() if isinstance(cheie, str) else cheie)


def cripteaza(text):
    """text (str) -> ciphertext (str). Pura fata de DB."""
    return _fernet().encrypt(text.encode()).decode()


def decripteaza(text):
    """ciphertext (str) -> text (str)."""
    return _fernet().decrypt(text.encode()).decode()


# ============================================================
#  JWT ANAF — decodare FARA verificare de semnatura
#  (nu detinem cheia publica ANAF; ne trebuie doar claim-urile)
# ============================================================
def decodeaza_jwt(token):
    """Intoarce payload-ul (dict) din segmentul de mijloc al JWT. Pura."""
    try:
        seg = token.split(".")[1]
    except (AttributeError, IndexError):
        return {}
    seg += "=" * (-len(seg) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(seg.encode()))
    except (ValueError, json.JSONDecodeError):
        return {}


# NECUNOSCUTA DECLARATA (ARHITECTURA_SPV.md): formatul JWT ANAF nu e documentat.
# Numele exact al claim-ului cu serialul certificatului se CONFIRMA la primul token
# real (decodare pe jwt.io — pasul 5 din ordinea de executie). Pana atunci incercam
# un set de chei plauzibile si cadem pe 'sub'/marcaj. NU se ghiceste tacut.
_CANDIDATI_SERIAL = ("serial_number", "serialNumber", "serial", "certSerial", "sub")


def extrage_serial(payload):
    """Serialul certificatului din claim-uri. Vezi NECUNOSCUTA DECLARATA. Pura."""
    for k in _CANDIDATI_SERIAL:
        v = payload.get(k)
        if v:
            return str(v)
    return "NECONFIRMAT"   # se corecteaza la primul token real (jwt.io)


# ============================================================
#  STATE OAuth (CSRF) — semnat, fara tabel nou (reuse nucleu)
# ============================================================
def genereaza_state(principal, acum=None):
    """State CSRF legat de PRINCIPAL (cabinet sau gratuit), expira in 10 min. Pura."""
    return nucleu.creeaza_token(
        {"pk": principal.kind, "pi": int(principal.id), "scop": "spv_state"},
        cfg_secret("JWT_SECRET"), durata_sec=STATE_DURATA_SEC, acum=acum)


def verifica_state(state, acum=None):
    """Verifica state-ul, intoarce Principal. Ridica EroareSpv la invalid/expirat."""
    r = nucleu.verifica_token(state, cfg_secret("JWT_SECRET"), acum=acum)
    if not r["ok"]:
        raise EroareSpv("state invalid: %s" % r.get("mesaj", r.get("cod")))
    p = r["payload"]
    if p.get("scop") != "spv_state" or "pk" not in p or "pi" not in p:
        raise EroareSpv("state cu scop gresit")
    return Principal(p["pk"], int(p["pi"]))


def url_autorizare(principal, acum=None):
    """(url_authorize, state). token_content_type=jwt pe QUERY aici (ARHITECTURA)."""
    state = genereaza_state(principal, acum=acum)
    q = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": cfg("ANAF_CLIENT_ID"),
        "redirect_uri": cfg("ANAF_REDIRECT_URI"),
        "token_content_type": "jwt",
        "state": state,
    })
    return f"{cfg('ANAF_AUTHORIZE_URL', _AUTHORIZE_URL_DEFAULT)}?{q}", state


# ============================================================
#  PARSARE RASPUNS /token -> valori de stocat (PURA)
# ============================================================
def valori_din_raspuns_token(tok, acum=None):
    """
    Din JSON-ul raspunsului /token extrage AMBELE valori + expirari + serial.
    Pura (nu atinge DB/retea). ROTATIE: intoarce si access_token, si refresh_token noi.
    """
    acum = acum if acum is not None else int(time.time())
    access = tok.get("access_token")
    refresh = tok.get("refresh_token")
    if not access or not refresh:
        raise EroareSpv("raspuns /token fara access_token sau refresh_token")
    expires_in = int(tok.get("expires_in") or 0) or ACCES_IMPLICIT_SEC
    access_expira = datetime.fromtimestamp(acum + expires_in, tz=timezone.utc)
    refresh_expira = datetime.fromtimestamp(acum, tz=timezone.utc) + timedelta(days=REFRESH_DURATA_ZILE)
    serial = extrage_serial(decodeaza_jwt(access))
    return {
        "access_token": access,
        "refresh_token": refresh,
        "serial_certificat": serial,
        "access_expira": access_expira,
        "refresh_expira": refresh_expira,
    }


# ============================================================
#  STOCARE (DB) — se dovedeste pe server
# ============================================================
def salveaza_token(conn, principal, valori, acum_dt=None):
    """
    UPSERT token pentru un PRINCIPAL (cabinet XOR gratuit). GARDUL 1: dezactiveaza intai orice
    alt token VIU al principalului (alt serial), apoi upsert pe (coloana_principal, serial) - un
    singur token viu per principal. access/refresh stocate CRIPTAT. Intoarce id-ul randului.
    """
    acum_dt = acum_dt if acum_dt is not None else datetime.now(timezone.utc)
    where, params, col = _principal_sql(principal)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.spv_token SET activ=false WHERE " + where +
                    " AND serial_certificat <> %s", params + (valori["serial_certificat"],))
        # upsert-ok: refresh token SPV pe (col,serial) - actualizare intentionata a tokenului
        cur.execute(f"""
            INSERT INTO public.spv_token
                ({col}, serial_certificat, access_token, refresh_token,
                 access_expira, refresh_expira, activ)
            VALUES (%s,%s,%s,%s,%s,%s, true)
            ON CONFLICT ({col}, serial_certificat) WHERE {col} IS NOT NULL DO UPDATE SET
                access_token   = EXCLUDED.access_token,
                refresh_token  = EXCLUDED.refresh_token,
                access_expira  = EXCLUDED.access_expira,
                refresh_expira = EXCLUDED.refresh_expira,
                activ          = true,
                reimprospatat_la = %s
            RETURNING id
        """, (int(principal.id), valori["serial_certificat"],
              cripteaza(valori["access_token"]), cripteaza(valori["refresh_token"]),
              valori["access_expira"], valori["refresh_expira"], acum_dt))
        return cur.fetchone()[0]


def ia_token_activ(conn, principal):
    """
    Randul token activ pentru PRINCIPAL (cabinet sau gratuit), cu access/refresh DECRIPTATE.
    Intoarce si accounting_firm_id + tenant_id (pt derivarea principalului la refresh). None daca lipseste.
    """
    where, params, _ = _principal_sql(principal)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, serial_certificat, access_token, refresh_token,
                   access_expira, refresh_expira, accounting_firm_id, tenant_id
              FROM public.spv_token
             WHERE """ + where + """ AND activ = true
             ORDER BY id DESC LIMIT 1
        """, params)
        r = cur.fetchone()
    if not r:
        return None
    return {
        "id": r[0], "serial_certificat": r[1],
        "access_token": decripteaza(r[2]), "refresh_token": decripteaza(r[3]),
        "access_expira": r[4], "refresh_expira": r[5],
        "accounting_firm_id": r[6], "tenant_id": r[7],
    }


def stare_conexiune(conn, principal, acum_dt=None):
    """
    Stare conexiune pentru ecran (FARA secrete, FARA apel ANAF): conectat + expirari.
    'expira_curand' = access_expira sub marja cronului. None-uri daca nu e conectat.
    """
    acum_dt = acum_dt if acum_dt is not None else datetime.now(timezone.utc)
    where, params, _ = _principal_sql(principal)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT serial_certificat, access_expira, refresh_expira
              FROM public.spv_token
             WHERE """ + where + """ AND activ = true
             ORDER BY id DESC LIMIT 1
        """, params)
        r = cur.fetchone()
    if not r:
        return {"conectat": False}
    prag = acum_dt + timedelta(days=MARJA_REFRESH_ZILE)
    return {
        "conectat": True,
        "serial_certificat": r[0],
        "access_expira": r[1].isoformat() if r[1] else None,
        "refresh_expira": r[2].isoformat() if r[2] else None,
        "expira_curand": bool(r[1] and r[1] <= prag),
    }


def dezactiveaza_token(conn, token_id):
    """activ=false (refresh esuat / revocat). Cronul + notificarea sunt separate."""
    with conn.cursor() as cur:
        cur.execute("UPDATE public.spv_token SET activ=false WHERE id=%s", (int(token_id),))


# ============================================================
#  APELURI REALE catre ANAF (retea) — testate pe MOCK
# ============================================================
def _post_token(data):
    """POST /token cu Basic Auth. Intoarce JSON. Ridica pe non-200."""
    auth = base64.b64encode(f"{cfg('ANAF_CLIENT_ID')}:{cfg('ANAF_CLIENT_SECRET')}".encode()).decode()
    r = requests.post(cfg("ANAF_TOKEN_URL", _TOKEN_URL_DEFAULT), data=data,
                      headers={"Authorization": f"Basic {auth}",
                               "Content-Type": "application/x-www-form-urlencoded"},
                      timeout=30)
    if r.status_code != 200:
        raise EroareSpv("HTTP %s la /token: %s" % (r.status_code, r.text[:300]))
    return r.json()


def schimba_cod_pe_token(code):
    """
    Pasul 6 din flux: authorization_code -> token. token_content_type=jwt in BODY aici.
    FEREASTRA 60 SECUNDE (procedura ANAF) — nu se amana. APEL REAL ANAF.
    """
    return _post_token({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": cfg("ANAF_REDIRECT_URI"),
        "token_content_type": "jwt",
    })


def reimprospateaza_pereche(refresh_token):
    """grant_type=refresh_token -> pereche NOUA (access+refresh). APEL REAL ANAF."""
    return _post_token({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    })


def finalizeaza_autorizare(principal, code, acum=None):
    """Callback: schimba codul pe token si il salveaza (criptat) pentru principal. Intoarce id-ul.

    [P5 val 3, 11.09.2026] APELUL HTTP SE FACE FARA NICIO CONEXIUNE IN MANA. Schimbul `code ->
    token` are fereastra de 60 de secunde la ANAF si termen de 30 s, iar codul se consuma o singura
    data — nu e ceva ce se poate relua. Forma dinainte il facea din interiorul blocului rutei, deci
    o conexiune din cele zece statea blocata tot atat, pentru un apel care n-avea nevoie de ea:
    baza se atinge abia DUPA raspuns.

    Tranzactia scurta de mai jos e a rotatiei, si se COMITE inainte de a intoarce — deci tokenul e
    persistat inainte ca apelantul sa poata continua.
    """
    tok = schimba_cod_pe_token(code)                    # HTTP, fara conexiune
    valori = valori_din_raspuns_token(tok, acum=acum)
    with db.get_conn() as conn:                         # scurta, proprie
        id_ = salveaza_token(conn, principal, valori)
        conn.commit()
    return id_


def reimprospateaza_token(token_row, acum=None):
    """Rotatia unui token: HTTP FARA conexiune, apoi tranzactie scurta proprie care COMITE.

    Salveaza AMBELE valori noi (ROTATIE). Deriva PRINCIPALUL din rand (GARDUL 3: nu presupune
    `firm`). La esec: dezactiveaza tokenul si ridica `EroareSpvRefreshEsuat`.

    **[P5 val 3, 11.09.2026] PROPRIETATEA TRANZACTIEI S-A MUTAT AICI.** Contractul P4 de dinainte
    spunea ca *limita apartine use-case-ului* — `apel_anaf` deschidea conexiunea, deci el hotara
    cand se comite. Consecinta era ca apelul `/token`, cu termen de 30 s, se executa cu o conexiune
    din pool in mana, pe toate cele sapte cai. Decizia arhitectului din 11.09: rotatia detine
    tranzactia scurta de persist+commit, de dupa HTTP.

    **Garantia P4 ramane**: perechea noua e COMISA inainte ca functia sa se intoarca, deci inainte
    ca apelantul sa poata esua. Daca `apel_anaf` cade dupa rotatie, ce a scris ANAF si ce am scris
    noi raman de acord.

    **Regresia de care avertiza P4 e imposibila prin constructie**: fiecare bloc de mai jos se
    INCHIDE inainte ca urmatorul sa se deschida. Prima forma a reparatiei R180 deschidea o a doua
    conexiune *peste* prima si se bloca pe randul tinut de tranzactia apelantului; aici nu exista
    nicio suprapunere.

    **Si pe calea de esec se comite**: dezactivarea tokenului mort e tot un fapt — daca s-ar
    intoarce, un token pe care ANAF l-a refuzat ar ramane `activ = true` si ar fi reincercat la
    nesfarsit.
    """
    if token_row.get("accounting_firm_id") is not None or token_row.get("tenant_id") is not None:
        principal = principal_din_rand(token_row.get("accounting_firm_id"),
                                       token_row.get("tenant_id"))
    else:
        with db.get_conn() as conn:                     # scurta, DOAR citire; se inchide inainte de HTTP
            principal = _principal_din_token(conn, token_row["id"])

    try:
        tok = reimprospateaza_pereche(token_row["refresh_token"])    # HTTP, fara conexiune
        valori = valori_din_raspuns_token(tok, acum=acum)
    except EroareSpv:
        with db.get_conn() as conn:                     # scurta, proprie
            dezactiveaza_token(conn, token_row["id"])
            conn.commit()
        raise EroareSpvRefreshEsuat(
            "refresh esuat pentru token %s — principalul reconecteaza SPV" % token_row["id"])

    # serialul ramane cel cunoscut daca noul JWT nu-l expune
    if valori["serial_certificat"] == "NECONFIRMAT":
        valori["serial_certificat"] = token_row["serial_certificat"]

    with db.get_conn() as conn:                         # scurta, proprie: scrie SI COMITE
        salveaza_token(conn, principal, valori)
        conn.commit()
        return ia_token_activ(conn, principal)



def _principal_din_token(conn, token_id):
    with conn.cursor() as cur:
        cur.execute("SELECT accounting_firm_id, tenant_id FROM public.spv_token WHERE id=%s", (int(token_id),))
        r = cur.fetchone()
    if not r:
        raise EroareSpv("token %s inexistent" % token_id)
    return principal_din_rand(r[0], r[1])


def _expirat(access_expira, acum_dt=None):
    acum_dt = acum_dt if acum_dt is not None else datetime.now(timezone.utc)
    return access_expira is None or access_expira <= acum_dt


# ============================================================
#  FUNCTIA UNICA DE APEL — TOATE apelurile ANAF trec prin ea
# ============================================================
def apel_anaf(principal, metoda, url, acum_dt=None, _dormi=time.sleep, **kw):
    """
    Apel autentificat catre ANAF pentru un PRINCIPAL (cabinet sau gratuit). FUNCTIA UNICA DE APEL.
    Reguli: fara token activ -> EroareSpvNeconectat; access expirat -> refresh sincron;
    401 -> refresh o data + retry o data; 429 -> backoff exponential; 403 -> EroareSpvFaraDrept.
    APEL REAL ANAF.
    """
    # ── [P5 val 3, 10.09.2026] CONEXIUNEA NU MAI STĂ PESTE APELUL EXTERN ────────────────
    # Forma dinainte ținea conexiunea deschisă peste TOT ce urmează: apelul HTTP (termen până la
    # 60 s la încărcările de facturi), retry-ul de 401, și backoff-ul exponențial de la 429 — care
    # poate însemna zeci de secunde. Pool-ul are 10 conexiuni; zece încărcări simultane îl goleau
    # pentru toată aplicația, inclusiv pentru rute care n-au nicio treabă cu ANAF. Asta e restanța
    # R183, și tiparul pe care valul 3 îl repară.
    #
    # NU e lucrul pe care P4 l-a interzis. Nota lui `_roteste_si_comite` spune că prima formă a
    # reparației R180 deschidea *o a doua conexiune și scria pe același rând*, și se bloca fiindcă
    # tranzacția apelantului ținea rândul. Aici nu există suprapunere: blocul de mai jos SE ÎNCHIDE
    # — commit, conexiune înapoi în pool — înainte ca vreo altă conexiune să se deschidă.
    with db.get_conn() as conn:
        tok = ia_token_activ(conn, principal)
        if not tok:
            raise EroareSpvNeconectat("principalul %r nu are token SPV activ" % (principal,))
        _cere_rotatie = _expirat(tok["access_expira"], acum_dt)
    # [P5 val 3] Rotatia e AFARA din blocul de mai sus: apelul `/token` are termen de 30 s, iar
    # blocul asta nu mai are nimic de facut dupa citire. `reimprospateaza_token` isi deschide
    # singura tranzactia scurta in care scrie si comite.
    if _cere_rotatie:
        tok = reimprospateaza_token(tok, acum=None)

    # ANTETELE, citite O SINGURĂ DATĂ. Forma veche avea `kw.pop("headers", {})` ÎN BUCLĂ: la a doua
    # încercare `kw` nu mai avea `headers`, deci antetele apelantului — `Content-Type:
    # application/xml`, la încărcările UBL/UIT — se pierdeau tăcut, iar retry-ul pleca altfel decât
    # prima încercare. *E o schimbare de semantică, și se scrie; nu păstrez un defect ca să pot
    # spune că n-am schimbat nimic.*
    antete_apelant = kw.pop("headers", {})
    incercat_refresh = False
    backoff = 0
    while True:
        # ── FĂRĂ NICIO CONEXIUNE ÎN MÂNĂ ────────────────────────────────────────────────
        r = requests.request(metoda, url,
                             headers={**antete_apelant,
                                      "Authorization": "Bearer %s" % tok["access_token"]},
                             **kw)
        if r.status_code == 401 and not incercat_refresh:
            incercat_refresh = True
            # [P5 val 3] Nici aici nu se mai tine conexiune peste apelul `/token`: rotatia si-o
            # deschide singura, DUPA raspunsul ANAF, si o inchide imediat.
            tok = reimprospateaza_token(tok, acum=None)
            continue
        if r.status_code == 429 and backoff < MAX_BACKOFF_429:
            _dormi(2 ** backoff)
            backoff += 1
            continue
        if r.status_code == 403:
            raise EroareSpvFaraDrept("403 ANAF: certificatul nu are drept (CIF/serviciu)")
        return r
