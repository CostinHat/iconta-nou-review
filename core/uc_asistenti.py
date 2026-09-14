# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/asistenti`.

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

from core import asistenti_api as _asist
from core import db
from core.mesaje import mesaj_din_cod
from core import erori as _erori
from core import uc_comun as _uc_comun
from core.mesaje import (mesaj_din_cod, EMAIL_INVALID, EMAIL_EXISTA)
from core import db, observare as _obs
import os
from core import repo_utilizatori
import psycopg2.extras as _E_audit


def asistenti_lista(ctx):
    """[P7 · use-case] Corpul rutei `/asistenti`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return {
            "sumar": _asist.sumar(conn, cabinet_id),
            "actori": _asist.lista_actori(conn, cabinet_id),
        }


def asistenti_detalii(uid, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.detalii_actor(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise _erori.Inexistent(mesaj_din_cod(r.get("cod")))
        return r


def asistenti_permisiuni(uid, date, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}/permisiuni`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.set_permisiuni(
            conn, cabinet_id, uid,
            date.get("poate_pregati", False),
            date.get("poate_valida", False),
            date.get("poate_depune", False),
        )
        if not r.get("ok"):
            raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
        return r


def asistenti_atribuie(uid, tid, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}/firme/{tid}`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.atribuie_firma(conn, cabinet_id, uid, tid)
        if not r.get("ok"):
            raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
        return r


def asistenti_elimina(uid, tid, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}/firme/{tid}`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.elimina_firma(conn, cabinet_id, uid, tid)
        if not r.get("ok"):
            raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
        return r


def asistenti_dezactiveaza(uid, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}/dezactiveaza`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.dezactiveaza(conn, cabinet_id, uid, ctx["uid"])
        if not r.get("ok"):
            raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
        return r


def asistenti_reactiveaza(uid, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}/reactiveaza`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.reactiveaza(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
        return r


def asistenti_finalizeaza_firme(uid, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}/finalizeaza-firme`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.aplica_regula_zero_firme(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise _erori.CerereGresita(mesaj_din_cod(r.get("cod")))
        return r


def asistenti_semafor(zile, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/echipa/semafor`; docstringul ei a ramas in stratul HTTP."""
    if zile < 1:
        raise _erori.DateInvalide("Numărul de zile privite înapoi trebuie să fie cel puțin 1 — "
                                     "am primit %d." % zile)
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.semafor_echipa(conn, cabinet_id, zile)


def asistenti_erori(zile, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/echipa/erori`; docstringul ei a ramas in stratul HTTP."""
    if zile < 1:
        raise _erori.DateInvalide("Numărul de zile privite înapoi trebuie să fie cel puțin 1 — "
                                     "am primit %d." % zile)
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.erori_echipa(conn, cabinet_id, zile)


def asistenti_centralizator(de, pana, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/echipa/centralizator`; docstringul ei a ramas in stratul HTTP."""
    if de and pana and str(pana) < str(de):
        raise _erori.DateInvalide("Sfârșitul intervalului (%s) e înaintea începutului "
                                     "(%s). Raportul se cere pe un interval, iar intervalul "
                                     "are o ordine." % (pana, de))
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.centralizator(conn, cabinet_id, de=de, pana=pana)


def asistenti_jurnal(de, pana, limit, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/echipa/jurnal`; docstringul ei a ramas in stratul HTTP."""
    if de and pana and str(pana) < str(de):
        raise _erori.DateInvalide("Sfârșitul intervalului (%s) e înaintea începutului "
                                     "(%s). Raportul se cere pe un interval, iar intervalul "
                                     "are o ordine." % (pana, de))
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.jurnal(conn, cabinet_id, de=de, pana=pana, limit=limit)


def asistenti_calitate(uid, de, pana, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}/calitate`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.calitate(conn, cabinet_id, uid, de=de, pana=pana)
        if not r.get("ok"):
            raise _erori.Inexistent(mesaj_din_cod(r.get("cod")))
        return r


def asistenti_activitate(uid, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti/{uid}/activitate`; docstringul ei a ramas in stratul HTTP."""
    cabinet_id = _uc_comun._cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.activitate(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise _erori.Inexistent(mesaj_din_cod(r.get("cod")))
        return r


def asistent_creeaza(date, ctx):
    """[P7 · use-case] Corpul rutei `/asistenti`; docstringul ei a ramas in stratul HTTP."""
    from core import nucleu as _nucleu
    import secrets as _sec
    email = date.email.strip().lower()
    if not _uc_comun._email_valid(email):  # [R138] altfel `«»@#$%` devine un cont de `angajat`
        raise _erori.DateInvalide(EMAIL_INVALID)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            if repo_utilizatori.id_si_activ_dupa_email(cur, email):
                raise _erori.DateInvalide(EMAIL_EXISTA)
            uid = repo_utilizatori.creeaza_cont_de_client(cur, email, _nucleu.hash_parola(_sec.token_urlsafe(16)), date.nume or email.split("@")[0], ctx["firm"], date.poate_valida)["id"]
        with conn.cursor() as cur:
            tok = _sec.token_urlsafe(32)
            _uc_comun._pune_token(cur, tok, uid, "48 hours")
    baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
    link = baza + "/#activare=" + tok
    html = ("<p>Buna,</p><p>Ai fost adaugat ca asistent in cabinetul tau pe iConta.eu.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Activeaza contul</a></p>"
            "<p>Dupa activare, intra cu emailul <b>%s</b> si parola setata. Linkul e valabil 48 de ore.</p>") % (link, email)
    try:
        _obs.trimite_email_html(email, "Acces asistent iConta.eu", html)
    except Exception as _e:
        # [R73] ALERTA: fara linkul de activare, asistentul nu are cont.
        _obs.esec_secundar("email invitatie asistent", _e, alerta=True)
    return {"ok": True, "user_id": uid}

