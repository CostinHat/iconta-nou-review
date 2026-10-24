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


#: [598 / 600, lotul 12] Ce i se spune contabilului când drumul spre ANAF nu reușește: pe înțelesul lui, fără coduri HTTP, fără numele
#: excepțiilor, fără „state” / „token”, și cu ce face aplicația în loc. Textul excepției (detaliul tehnic) rămâne în jurnalul serverului,
#: nu pe ecran. `{ce}` = ce nu s-a întâmplat din cauza asta, spus de apelant („Factura nu a plecat în SPV și rămâne netrimisă.”).
MESAJ_SPV_NECONECTAT = ("Cabinetul nu e conectat la SPV. {ce} Conectează SPV din Setări cont → Conectare SPV (cu certificatul), apoi "
                        "încearcă din nou.")
MESAJ_SPV_ACCES_EXPIRAT = ("Accesul cabinetului la SPV a expirat și nu s-a putut reînnoi singur. {ce} Reconectează SPV din Setări cont → "
                           "Conectare SPV (cu certificatul), apoi încearcă din nou.")
MESAJ_SPV_FARA_DREPT = ("ANAF a refuzat accesul: certificatul conectat al cabinetului nu are drept pentru această operație. {ce} Verifică "
                        "în Setări cont → Conectare SPV pe ce firme are drept certificatul.")
MESAJ_ANAF_FARA_RASPUNS = "ANAF nu a răspuns la timp. {ce} Încearcă din nou peste câteva minute."
MESAJ_SPV_NEREUSIT = ("Legătura cu ANAF nu a reușit dintr-o eroare a aplicației, înregistrată pentru echipa iConta.eu. {ce} Încearcă din "
                      "nou; dacă se repetă, scrie-ne din Suport.")


#: [C42 + 598] citirea automată din SPV: ANAF n-a răspuns (se reia singură) / cabinetul fără conexiune — motivele aplicației pe citire
MESAJ_CITIRE_ANAF_TACE = "ANAF n-a răspuns la timp; citirea se reia singură la următoarea rulare."
MESAJ_CITIRE_NECONECTAT = "Cabinetul nu e conectat la SPV."


def e_motivul_aplicatiei(text):
    """PURĂ. [598] Textul scris pe o citire / trimitere e motivul spus de aplicație (șabloanele de aici), nu răspunsul ANAF — pe acela
    ecranul îl citează („a primit de la ANAF: …”), pe al aplicației nu."""
    t = (text or "").strip()
    inceputuri = [s.split("{ce}")[0].strip() for s in (MESAJ_SPV_NECONECTAT, MESAJ_SPV_ACCES_EXPIRAT, MESAJ_SPV_FARA_DREPT,
                                                       MESAJ_ANAF_FARA_RASPUNS, MESAJ_SPV_NEREUSIT)]
    return bool(t) and (t in (MESAJ_CITIRE_ANAF_TACE, MESAJ_CITIRE_NECONECTAT) or any(t.startswith(i) for i in inceputuri))


def mesaj_pentru_contabil(eroare, ce):
    """PURĂ. Mesajul de pe ecran pentru o eroare pe drumul spre ANAF (conector, rețea, răspuns neașteptat). Nu conține textul excepției."""
    if isinstance(eroare, EroareSpvRefreshEsuat):
        sablon = MESAJ_SPV_ACCES_EXPIRAT
    elif isinstance(eroare, EroareSpvNeconectat):
        sablon = MESAJ_SPV_NECONECTAT
    elif isinstance(eroare, EroareSpvFaraDrept):
        sablon = MESAJ_SPV_FARA_DREPT
    elif isinstance(eroare, (requests.exceptions.RequestException, OSError)):
        sablon = MESAJ_ANAF_FARA_RASPUNS
    else:
        sablon = MESAJ_SPV_NEREUSIT
    return " ".join(sablon.format(ce=(ce or "").strip()).split())


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


def principal_pentru_schema(conn, schema):
    """Token owner (Principal) pentru o schema tenant: cabinet daca accounting_firm_id setat, altfel
    gratuit (tenant). Partajat de cr-oanele SPV (poll F178 + receive F179) - un singur loc.

    [P7 · valul D2, 13.09.2026] Statea in `core/efactura_send.py`, care e motor fiscal si n-avea
    voie sa atinga baza. Locul ei e aici, langa `principal_firm`/`principal_tenant`: intrebarea e
    despre PRINCIPALI, nu despre e-Factura. Interogarea a trecut in `repo_tenants`.
    """
    from core import repo_tenants as _rt
    with conn.cursor() as cur:
        r = _rt.dupa_numele_schemei(cur, schema)
    if not r:
        raise ValueError("firma cu evidența %s nu mai există în lista firmelor" % schema)
    tid, afid = r
    return principal_firm(afid) if afid is not None else principal_tenant(tid)


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
    raise EroareSpv("rând spv_token fără principal (nici firm, nici tenant)")  # invariant-intern-ok: integritatea tabelului de chei


# ============================================================
#  CRIPTARE (Fernet) — PURA (primeste cheia din env la apel)
# ============================================================
def _fernet():
    """Instanta Fernet din SPV_FERNET_KEY. Ridica daca lipseste (nu stoca in clar)."""
    from cryptography.fernet import Fernet
    cheie = os.environ.get("SPV_FERNET_KEY", "")
    if not cheie:
        raise EroareSpv("SPV_FERNET_KEY lipsește din env — token-urile nu se stochează în clar")  # invariant-intern-ok: configurarea serverului
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


class EroareStateExpirat(EroareSpv):
    """[600] State-ul e al nostru, dar a trecut de `STATE_DURATA_SEC`: drumul la ANAF a durat prea mult."""


def verifica_state(state, acum=None):
    """Verifica state-ul, intoarce Principal. Ridica EroareStateExpirat la expirat, EroareSpv la invalid / ilizibil."""
    secret = cfg_secret("JWT_SECRET")
    try:
        r = nucleu.verifica_token(state, secret, acum=acum)
    except (ValueError, TypeError, UnicodeDecodeError) as e:   # [600] base64 / JSON stricat: tot „state invalid”, nu 500
        raise EroareSpv("state ilizibil: %s" % type(e).__name__)
    if not r["ok"]:
        if r.get("cod") == "TOKEN_EXPIRAT":
            raise EroareStateExpirat("state expirat")
        raise EroareSpv("state invalid: %s" % r.get("mesaj", r.get("cod")))
    p = r["payload"]
    if p.get("scop") != "spv_state" or "pk" not in p or "pi" not in p:
        raise EroareSpv("state cu scop greșit")
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
        raise EroareSpv("ANAF a răspuns fără cheile de acces, deci conectarea la SPV nu s-a încheiat. Încearcă din nou.")
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


#: [17.10.2026, decizia Costin pct.2, verbatim în DECIZII] certificatul conectat fără drept SPV pe CUI-ul firmei — textul UNIC (fereastra
#: firmei, Facturi primite, emiterea, Conectare SPV, refuzul de la „Trimite în SPV”). Ce are de făcut: OMFP 660/2017 art.15 alin.(1) —
#: persoana juridică se identifică în SPV „cu certificatul calificat deţinut de persoana fizică reprezentant legal”, „de reprezentantul
#: desemnat” sau „de împuternicitul persoanei juridice” (lit.b–d); împuternicitul, potrivit art.18 din Codul de procedură fiscală (alin.(6)).
MESAJ_FARA_DREPT = ("Certificatul conectat al cabinetului nu are drept în SPV pentru CUI-ul acestei firme ({cui}); ANAF răspunde: „{eroare}”. "
                    "Până se rezolvă, facturile ei nu pleacă în SPV, iar cele de la furnizori nu vin. Ce faci: titularul certificatului "
                    "trebuie să fie, pentru această firmă, reprezentantul legal, reprezentantul desemnat sau împuternicitul ei înregistrat "
                    "în SPV (OMFP 660/2017 art.15 alin.(1)) — înregistrarea se face la ANAF; sau conectezi cabinetul cu certificatul cuiva "
                    "care are deja acest drept. Citirea automată verifică din nou la :17 și :47.")


#: [deficiența 315, comanda Costin 17.10.2026 7.2] în Conectare SPV explicația se spune O DATĂ, deasupra firmelor; pe fiecare firmă, un rând:
#: „<firmă> · fără drept în SPV · verificat <data, ora>” — același temei ca `MESAJ_FARA_DREPT`, fără CUI-ul unei firme anume
EXPLICATIE_FARA_DREPT = ("Pe firmele de mai jos marcate „fără drept în SPV”, certificatul conectat al cabinetului nu are drept în SPV pentru "
                         "CUI-ul lor{eroare}: facturile lor nu pleacă în SPV, iar cele de la furnizori nu vin. Ce faci: titularul "
                         "certificatului trebuie să fie, pentru fiecare dintre ele, reprezentantul legal, reprezentantul desemnat sau "
                         "împuternicitul firmei înregistrat în SPV (OMFP 660/2017 art.15 alin.(1)) — înregistrarea se face la ANAF; sau "
                         "conectezi cabinetul cu certificatul cuiva care are deja acest drept. Citirea automată verifică din nou la :17 și "
                         ":47.")


def explicatie_fara_drept(cuiuri):
    """[315] Explicația unică pentru firmele fără drept (None dacă nu e niciuna); răspunsurile ANAF, o dată fiecare."""
    fara = [c for c in cuiuri or [] if c.get("are_drept") is False]
    if not fara:
        return None
    erori = list(dict.fromkeys((c.get("eroare") or "").strip() for c in fara if (c.get("eroare") or "").strip()))
    return EXPLICATIE_FARA_DREPT.format(eroare=("; ANAF răspunde: " + "; ".join("„%s”" % e for e in erori)) if erori else "")


def mesaj_fara_drept(cui, eroare):
    return MESAJ_FARA_DREPT.format(cui=cui or "—", eroare=(eroare or "fără drept").strip())


def cuiuri_verificate(conn, principal):
    """[17.10.2026, 289 + pct.2] CUI-urile pe care citirea automată le-a verificat cu tokenul activ: [{cui, nume, are_drept, eroare,
    verificat_la}] — „CUI-urile acoperite” din Conectare SPV, cu cele fără drept arătate ca atare."""
    where, params, _ = _principal_sql(principal)
    nume_sql = ("(SELECT t.nume FROM public.tenants t WHERE regexp_replace(t.cui, '\\D', '', 'g') = a.cui AND t.accounting_firm_id = %s "
                "ORDER BY t.id LIMIT 1)" if principal.kind == "firm" else "NULL")
    with conn.cursor() as cur:
        cur.execute("SELECT a.cui, " + nume_sql + ", a.are_drept, a.eroare, a.verificat_la FROM public.spv_cui_acoperit a "
                    "WHERE a.token_id = (SELECT id FROM public.spv_token WHERE " + where + " AND activ = true ORDER BY id DESC LIMIT 1) "
                    "ORDER BY a.are_drept NULLS LAST, a.cui",
                    ((int(principal.id),) if principal.kind == "firm" else ()) + tuple(params))
        randuri = cur.fetchall()
    from core import afirmatii as _af
    out = []
    for r in randuri:
        x = {"cui": r[0], "nume": r[1], "are_drept": r[2], "eroare": r[3], "verificat_la": r[4].isoformat() if r[4] else None}
        if r[2] is False:
            # statutul CUI-ului față de certificat, ca afirmație tipată (decizia 21.08: obiecte cu `fel`, nu proză în dicționar)
            m = mesaj_fara_drept(r[0], r[3])
            x.update(_af.afirmatie("statut", "drept_spv_cui", m, statut="fara_drept", statut_din=x["verificat_la"]), mesaj=m)
        out.append(x)
    return out


def stare_conexiune(conn, principal, acum_dt=None):
    """
    Stare conexiune pentru ecran (FARA secrete, FARA apel ANAF): conectat + expirari.
    'expira_curand' = access_expira sub marja cronului. None-uri daca nu e conectat.
    """
    acum_dt = acum_dt if acum_dt is not None else datetime.now(timezone.utc)
    where, params, _ = _principal_sql(principal)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT serial_certificat, access_expira, refresh_expira, access_token
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
        # [deficiența 289a] emitentul certificatului — claim-ul `issuer` al JWT-ului ANAF (ARHITECTURA_SPV.md, decodat pe tokenul real
        # din 18.07.2026: „issuer-ul certificatului (ex. DigiSign)”). Titularul NU e în token: ANAF nu-l trimite.
        "emitent_certificat": emitent_certificat(r[3]),
        "access_expira": r[1].isoformat() if r[1] else None,
        "refresh_expira": r[2].isoformat() if r[2] else None,
        "expira_curand": bool(r[1] and r[1] <= prag),
    }


def emitent_certificat(access_token_criptat):
    """Emitentul certificatului din tokenul (criptat) stocat: claim-ul `issuer`. None dacă tokenul nu se poate citi."""
    try:
        return decodeaza_jwt(decripteaza(access_token_criptat)).get("issuer") or None
    except Exception:  # noqa: BLE001 — un token ilizibil nu oprește ecranul; starea conexiunii rămâne
        return None


def stare_firma(conn, principal, cui, acum_dt=None):
    """[lotul 6: 273a, 275c, 289b] Starea SPV a unei FIRME: conexiunea cabinetului (`stare_conexiune`) + ultima citire a CUI-ului ei
    (`public.spv_cui_acoperit`, scrisă de `spv_receive.citeste_firma`): `verificat_la`, `are_drept` (True / False / None = necunoscut),
    `eroare` (răspunsul ANAF), `mesaje`. Fără apel la ANAF."""
    st = stare_conexiune(conn, principal, acum_dt)
    cui = "".join(ch for ch in str(cui or "") if ch.isdigit())
    st.update({"cui": cui, "verificat_la": None, "are_drept": None, "eroare": None, "mesaje": None})
    if st["conectat"] and cui:
        where, params, _ = _principal_sql(principal)
        with conn.cursor() as cur:
            cur.execute("SELECT verificat_la, are_drept, eroare, mesaje FROM public.spv_cui_acoperit WHERE cui = %s AND token_id = "
                        "(SELECT id FROM public.spv_token WHERE " + where + " AND activ = true ORDER BY id DESC LIMIT 1)",
                        (cui,) + tuple(params))
            r = cur.fetchone()
        if r:
            st.update({"verificat_la": r[0].isoformat() if r[0] else None, "are_drept": r[1], "eroare": r[2], "mesaje": r[3],
                       # [598] ecranul citează numai răspunsul ANAF; motivul aplicației (ANAF n-a răspuns, acces expirat) îl spune ca atare
                       "eroare_de_la_anaf": bool(r[2]) and not e_motivul_aplicatiei(r[2])})
            if r[1] is False:
                st["mesaj"] = mesaj_fara_drept(cui, r[2])   # [17.10.2026] spus la fel peste tot (spv_stare.js, refuzul trimiterii)
    return st


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
            "refresh eșuat pentru token %s — principalul reconecteaza SPV" % token_row["id"])

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
