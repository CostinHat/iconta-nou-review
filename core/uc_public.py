# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/public`.

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
            raise _erori.CerereGresita("Linkul nu mai e valabil: a expirat sau a fost folosit deja. Cere alt link din „Am uitat parola”.")
    try:
        with db.get_conn() as c, c.cursor() as cur:
            repo_admin.scrie_audit_reset_schimbat(cur, r["user_id"])
            c.commit()
    except Exception as _e:
        _obs.esec_secundar("audit_log reset parola schimbat", _e)  # inghitit, dar nu tacut (27.07.2026)
    return {"ok": True}


# [lotul 13, deficiența 608 — „Mesajele de autentificare încep cu literă mică”] mesajele linkului de logare: propoziții întregi, cu ce are
# omul de făcut (DS cap.0: „Mesajele către utilizator […] spun ce s-a întâmplat și ce are de făcut”)
MESAJ_LINK_INVALID = "Linkul de logare nu e valid. Cere unul nou din „Trimite-mi link de logare”."
MESAJ_LINK_FOLOSIT = "Linkul de logare a expirat sau a fost folosit deja. Cere unul nou din „Trimite-mi link de logare”."


def magic_login(date):
    """[P7 · use-case] Corpul rutei `/public/magic-login`; docstringul ei a ramas in stratul HTTP."""
    tok = (date.token or "").strip()
    if not tok.startswith("ml_"):
        raise _erori.Neautentificat(MESAJ_LINK_INVALID)
    with db.get_conn() as conn, conn.cursor() as cur:
        r = repo_utilizatori.cont_din_token_activare(cur, _uc_comun._hash_tok(tok))
        if not r:
            raise _erori.Neautentificat(MESAJ_LINK_FOLOSIT)
        repo_utilizatori.marcheaza_tokenul_folosit(cur, _uc_comun._hash_tok(tok))
        conn.commit()
    with db.get_conn() as conn:
        rez = auth_api.sesiune_pentru_user(conn, r[0])
    if not rez.get("ok") and rez.get("cod") == "CABINET_SUSPENDAT":
        # [lotul 13, 645] linkul fără parolă al unui cabinet suspendat: motivul ales, ca la logarea cu parolă
        from core import uc_admin as _uc_admin
        raise _erori.Neautentificat(_uc_admin.mesaj_suspendare(rez.get("cabinet_id")))
    if not rez.get("ok"):
        raise _erori.Neautentificat(rez.get("mesaj") or "Contul nu e activ.")
    return rez


def activare_cont(date):
    """[P7 · use-case] Corpul rutei `/public/activare`; docstringul ei a ramas in stratul HTTP."""
    if not _nucleu.parola_ok(date.parola):
        raise _erori.CerereGresita(_nucleu.PAROLA_MESAJ)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            r = repo_utilizatori.cont_din_token_activare_2(cur, _uc_comun._hash_tok(date.token))
            if not r:
                raise _erori.CerereGresita("Linkul de activare nu mai e valabil: a expirat sau a fost folosit deja.")   # [608]
            repo_utilizatori.seteaza_parola(cur, _nucleu.hash_parola(date.parola), r["user_id"])
            repo_utilizatori.marcheaza_tokenul_folosit(cur, _uc_comun._hash_tok(date.token))
            # [deficiența 320, „Cont și echipă”] administratorul cabinetului află că asistentul invitat și-a activat contul
            from core import repo_inceput as _ri, notificari_api as _notif
            rol, nume, admini = _ri.adminii_pentru_activare(cur, r["user_id"])
            if rol == "angajat":
                for a in admini:
                    _notif.adauga(conn, a, "asistent_activat", "%s și-a activat contul de asistent: îl găsești în Asistenți." % nume)
    return {"ok": True}


def portal_confirma_email(date):
    """[P7 · use-case] Corpul rutei `/public/confirma-email`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            r = repo_utilizatori.schimbare_email_in_asteptare(cur, _uc_comun._hash_tok(date.token))
            if not r:
                raise _erori.CerereGresita(MESAJ_EMAIL_TOKEN_INVALID)
            _uc_comun._adresa_e_libera(cur, r["email_nou"], r["user_id"])
            # [lotul 10, C73 / U3] adresa luată între verificare și scriere -> același refuz ca `_adresa_e_libera`, nu 500
            from core import chei_unice as _chei
            with _chei.refuza_dublura(cur, _uc_comun.CHEIE_EMAIL, _uc_comun._refuz_email_la_cursa(None, r["email_nou"], None, "email")):
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
        baza = os.environ.get("ICONTA_BAZA_URL", "https://iconta.eu")
        link = baza + "/#reset=" + token
        import html as _h
        from core import common as _common
        nume = _common.nume_de_salut(u.get("prenume"), u.get("nume"))   # [269] prenumele scris separat, altfel numele întreg
        html = ("<p>Bună%s,</p>"
                "<p>A sosit o cerere de resetare a parolei contului tău de cabinet pe iConta.eu.</p>"
                "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Setează o parolă nouă</a></p>"
                "<p>Linkul e valabil 60 de minute și poate fi folosit o singură dată. "
                "Dacă nu tu ai cerut resetarea, ignoră acest mesaj — parola rămâne neschimbată.</p>"
                % ((" " + _h.escape(nume)) if nume else "", link))
        # [R73] ALERTA: e cale de acces. Tacerea aici inseamna ca omul nu mai poate intra
        # si nimeni nu afla — chiar criteriul din docstringul lui `esec_secundar`.
        _obs.trimite_email_html_sau_semnaleaza("email resetare parola", u["email"], "Resetare parola iConta.eu", html, alerta=True,
                                               postmark=True)
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
            _html_magic = ("<p>Bună,</p><p>Apasă butonul ca să intri în iConta.eu, fără parolă:</p>"
                    "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intră în iConta.eu</a></p>"
                    "<p>Linkul e valabil 15 minute și se folosește o singură dată.</p>") % link
    # [P5 val 3, 11.09.2026] AICI, nu inauntru. Tokenul e COMIS mai sus (`conn.commit()`), deci
    # trimiterea nu mai are ce sa astepte de la tranzactie — dar tinea o conexiune din pool peste un
    # apel cu termen de 15 s. Conditiile de trimitere sunt neschimbate: se trimite exact cand exista
    # `_html_magic`, adica exact cand exista utilizatorul. Raspunsul rutei ramane acelasi indiferent,
    # ca sa nu se poata enumera adresele.
    if _html_magic is not None:
        # [R73] ALERTA: SINGURA usa de intrare in portalul clientului.
        _obs.trimite_email_html_sau_semnaleaza("email link de logare", email, "Link de logare iConta.eu", _html_magic, alerta=True,
                                               postmark=True)
    return {"ok": True, "mesaj": MESAJ_LINK_LOGARE_CERUT}



# ── [268] DEZABONAREA (Lotul 5, decizia în DECIZII) ─────────────────────────────────────────────────────────────────────────────
# Pagina publică a linkului „Dezabonează-te” din subsolul fiecărui email (core/dezabonare.py). GET arată confirmarea cu un buton, POST
# dezabonează: un scanner de linkuri care deschide adresa nu dezabonează pe nimeni, iar programul de email care oferă singur butonul
# (antetul List-Unsubscribe-Post, RFC 8058) trimite POST la aceeași adresă. Pagina e HTML gata făcut (ca termenii): se deschide din
# email, fără aplicație și fără cont.
_DEZABONARE_PAGINA = """<!doctype html><html lang="ro" class="pagina-publica"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dezabonare - iConta.eu</title>
<link rel="stylesheet" href="/static/stil.css">
<style>
body{background:#f4f6f9;margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1d3a5f;line-height:1.6}
.dz-bara{display:flex;align-items:center;gap:10px;padding:14px 22px;background:#1d3a5f;color:#fff;font-weight:600}
.dz-bara a{color:#fff;text-decoration:none}
.dz-wrap{max-width:640px;margin:0 auto;padding:30px 22px 90px}
.dz-wrap h1{font-size:1.5rem;margin:.2em 0 .6em}
.dz-wrap p{color:#33445a}
.dz-wrap form{margin:22px 0}
</style></head><body class="pagina-publica">
<div class="dz-bara"><a href="/">iConta.eu</a><span>&middot; Dezabonare</span></div>
<main class="dz-wrap" id="dz-pagina"><h1>Dezabonare de la emailurile informative iConta.eu</h1>%(corp)s
<p><a href="/">&larr; Înapoi la iConta.eu</a></p></main>
</body></html>"""
MESAJ_DEZABONARE_LINK_INVALID = ("Linkul de dezabonare nu e valid. Deschide linkul „Dezabonează-te” din subsolul unui email primit de la "
                                 "iConta.eu, întreg, așa cum a venit.")


def _pagina_dezabonare(corp):
    return _DEZABONARE_PAGINA % {"corp": corp}


def _p(text, id_=None):
    import html as _h
    return '<p%s>%s</p>' % ((' id="%s"' % id_) if id_ else "", _h.escape(text))


def dezabonare_pagina(email, semnatura):
    """`GET /public/dezabonare`: (cod HTTP, pagina). Arată ce se întâmplă și butonul; nu schimbă nimic."""
    import html as _h
    from urllib.parse import urlencode
    from core import dezabonare as _dez
    if not _dez.semnatura_valida(email, semnatura):
        return 400, _pagina_dezabonare(_p(MESAJ_DEZABONARE_LINK_INVALID, "dz-mesaj"))
    adresa = _dez.normalizeaza(email)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            deja = _dez.e_dezabonata(cur, adresa)
        conn.rollback()
    if deja:
        return 200, _pagina_dezabonare(_p("Adresa %s e deja dezabonată de la emailurile informative iConta.eu." % adresa, "dz-mesaj")
                                       + _p(_dez.MESAJ_CE_RAMANE))
    actiune = _h.escape(_dez.RUTA + "?" + urlencode({"e": adresa, "s": semnatura}), quote=True)
    return 200, _pagina_dezabonare(
        _p("Dacă te dezabonezi, adresa %s nu mai primește emailurile informative iConta.eu." % adresa, "dz-mesaj")
        + _p(_dez.MESAJ_CE_RAMANE)
        + '<form method="post" action="%s"><button type="submit" class="buton-primar" id="dz-confirma">Dezabonează-mă</button></form>'
        % actiune)


def dezabonare_confirma(email, semnatura):
    """`POST /public/dezabonare`: (cod HTTP, pagina). Butonul paginii sau programul de email (List-Unsubscribe-Post)."""
    from core import dezabonare as _dez
    if not _dez.semnatura_valida(email, semnatura):
        return 400, _pagina_dezabonare(_p(MESAJ_DEZABONARE_LINK_INVALID, "dz-mesaj"))
    adresa = _dez.normalizeaza(email)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _dez.dezaboneaza(cur, adresa)
        conn.commit()
    return 200, _pagina_dezabonare(_p("Gata: adresa %s e dezabonată. De acum nu mai primești emailurile informative iConta.eu."
                                      % adresa, "dz-mesaj") + _p(_dez.MESAJ_CE_RAMANE))
