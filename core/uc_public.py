# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/public`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:827`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

from core import db, auth_api, observare as _obs
from core import nucleu as _nucleu
from core import repo_admin
from core import repo_utilizatori
from core.mesaje import MESAJ_EMAIL_TOKEN_INVALID
import psycopg2.extras as _E_audit
from core import erori as _erori
from core import uc_comun as _uc_comun
from core import db, auth_api, observare as _obs
import os
from core.mesaje import (MESAJ_LINK_LOGARE_CERUT)


def reset_parola_seteaza(date):
    """[P7 · use-case] Corpul rutei `/public/reset-parola/seteaza`; docstringul ei a ramas in stratul HTTP."""
    if not _nucleu.parola_ok(date.parola):
        raise _erori.CerereGresita(_nucleu.PAROLA_MESAJ)
    from core import reset_parola as _rp
    with db.get_conn() as conn:
        try:
            r = _rp.seteaza(conn, date.token, date.parola)
            conn.commit()
        except ValueError:
            raise _erori.CerereGresita("Link invalid, expirat sau deja folosit. Cere alt link din sectiunea Am uitat parola.")
    try:
        with db.get_conn() as c, c.cursor() as cur:
            repo_admin.scrie_audit_reset_schimbat(cur, r["user_id"])
            c.commit()
    except Exception as _e:
        _obs.esec_secundar("audit_log reset parola schimbat", _e)  # inghitit, dar nu tacut (27.07.2026)
    return {"ok": True}


def magic_login(date):
    """[P7 · use-case] Corpul rutei `/public/magic-login`; docstringul ei a ramas in stratul HTTP."""
    tok = (date.token or "").strip()
    if not tok.startswith("ml_"):
        raise _erori.Neautentificat("link invalid")
    with db.get_conn() as conn, conn.cursor() as cur:
        r = repo_utilizatori.cont_din_token_activare(cur, _uc_comun._hash_tok(tok))
        if not r:
            raise _erori.Neautentificat("link expirat sau folosit")
        repo_utilizatori.marcheaza_tokenul_folosit(cur, _uc_comun._hash_tok(tok))
        conn.commit()
    with db.get_conn() as conn:
        rez = auth_api.sesiune_pentru_user(conn, r[0])
    if not rez.get("ok"):
        raise _erori.Neautentificat(rez.get("mesaj", "cont inactiv"))
    return rez


def activare_cont(date):
    """[P7 · use-case] Corpul rutei `/public/activare`; docstringul ei a ramas in stratul HTTP."""
    if not _nucleu.parola_ok(date.parola):
        raise _erori.CerereGresita(_nucleu.PAROLA_MESAJ)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            r = repo_utilizatori.cont_din_token_activare_2(cur, _uc_comun._hash_tok(date.token))
            if not r:
                raise _erori.CerereGresita("link de activare invalid sau expirat")
            repo_utilizatori.seteaza_parola(cur, _nucleu.hash_parola(date.parola), r["user_id"])
            repo_utilizatori.marcheaza_tokenul_folosit(cur, _uc_comun._hash_tok(date.token))
    return {"ok": True}


def portal_confirma_email(date):
    """[P7 · use-case] Corpul rutei `/public/confirma-email`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            r = repo_utilizatori.schimbare_email_in_asteptare(cur, _uc_comun._hash_tok(date.token))
            if not r:
                raise _erori.CerereGresita(MESAJ_EMAIL_TOKEN_INVALID)
            _uc_comun._adresa_e_libera(cur, r["email_nou"], r["user_id"])
            repo_utilizatori.schimba_emailul(cur, r["email_nou"], r["user_id"])
            repo_utilizatori.confirma_schimbarea_de_email(cur, r["id"])
            _uc_comun._urma_portal(cur, r["tenant_id"], "email_confirmat",
                         "adresa de autentificare schimbata: %s -> %s"
                         % (r["email_vechi"], r["email_nou"]), r["user_id"])
    return {"ok": True, "email": r["email_nou"]}


def reset_parola_cere(date):
    """[P7 · use-case] Corpul rutei `/public/reset-parola/cere`; docstringul ei a ramas in stratul HTTP."""
    from core import reset_parola as _rp
    with db.get_conn() as conn:
        token, u = _rp.cere_reset(conn, date.email)
        conn.commit()
    if token and u:
        try:
            baza = os.environ.get("ICONTA_BAZA_URL", "https://iconta.eu")
            link = baza + "/#reset=" + token
            nume = (u.get("prenume") or u.get("nume") or "").strip()
            html = ("<p>Buna%s,</p>"
                    "<p>Am primit o cerere de resetare a parolei contului tau de cabinet pe iConta.eu.</p>"
                    "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Seteaza o parola noua</a></p>"
                    "<p>Linkul e valabil 60 de minute si poate fi folosit o singura data. "
                    "Daca nu tu ai cerut resetarea, ignora acest mesaj — parola ramane neschimbata.</p>"
                    % ((" " + nume) if nume else "", link))
            _obs.trimite_email_html(u["email"], "Resetare parola iConta.eu", html)
        except Exception as _e:
            # [R73] ALERTA: e cale de acces. Tacerea aici inseamna ca omul nu mai poate intra
            # si nimeni nu afla — chiar criteriul din docstringul lui `esec_secundar`.
            _obs.esec_secundar("email resetare parola", _e, alerta=True)
        try:
            with db.get_conn() as c, c.cursor() as cur:
                repo_admin.scrie_audit_reset_cerut(cur, u["user_id"])
                c.commit()
        except Exception as _e:
            _obs.esec_secundar("audit_log reset parola cerut", _e)  # inghitit, dar nu tacut (27.07.2026)
    return {"ok": True, "mesaj": "Dacă adresa e înregistrată, vei primi un mesaj cu instrucțiuni de resetare."}



def magic_link_cere(date):
    """[P7 · use-case] Corpul rutei `/public/magic-link`; docstringul ei a ramas in stratul HTTP."""
    import secrets as _sec
    email = (date.email or "").strip().lower()
    _html_magic = None          # ce ramane de trimis DUPA ce se inchide blocul de conexiune
    with db.get_conn() as conn, conn.cursor() as cur:
        r = repo_utilizatori.id_cont_activ_dupa_email(cur, email)
        if r:
            tok = "ml_" + _sec.token_urlsafe(32)
            _uc_comun._pune_token(cur, tok, r[0], "15 minutes")
            conn.commit()
            baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
            link = baza + "/#magic=" + tok
            _html_magic = ("<p>Buna,</p><p>Apasa butonul pentru a intra in iConta.eu, fara parola:</p>"
                    "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intra in iConta.eu</a></p>"
                    "<p>Linkul e valabil 15 minute si poate fi folosit o singura data.</p>") % link
    # [P5 val 3, 11.09.2026] AICI, nu inauntru. Tokenul e COMIS mai sus (`conn.commit()`), deci
    # trimiterea nu mai are ce sa astepte de la tranzactie — dar tinea o conexiune din pool peste un
    # apel cu termen de 15 s. Conditiile de trimitere sunt neschimbate: se trimite exact cand exista
    # `_html_magic`, adica exact cand exista utilizatorul. Raspunsul rutei ramane acelasi indiferent,
    # ca sa nu se poata enumera adresele.
    if _html_magic is not None:
        try:
            _obs.trimite_email_html(email, "Link de logare iConta.eu", _html_magic)
        except Exception as _e:
            # [R73] ALERTA: SINGURA usa de intrare in portalul clientului.
            _obs.esec_secundar("email link de logare", _e, alerta=True)
    return {"ok": True, "mesaj": MESAJ_LINK_LOGARE_CERUT}

