# -*- coding: utf-8 -*-
"""core/autor_cerere.py — CINE face cererea curentă, văzut din orice strat (comanda Costin 06.10.2026, pct.1: „un singur
mecanism prin care cabinetul vede, validează sau respinge tot ce pregătește asistentul”).

DE CE. O notă contabilă se naște pe ~21 de drumuri de `INSERT` (facturi, bancă, casă, stocuri, salarii, jurnal…), niciunul
cu autor. Ca „tot ce pregătește asistentul” să ajungă în coada de validare fără să se cârpească fiecare drum (și fără ca un
drum nou să scape), autorul se ia din CERERE: middleware-ul HTTP îl pune aici, `db.get_conn` îl scrie pe SESIUNE cât ține
împrumutul conexiunii (`SET iconta.utilizator TO …`, șters cu `RESET` înainte de întoarcerea în pool), iar coloana `inregistrari.creat_de_id` îl preia ca valoare implicită.

ContextVar, nu thread-local (aceeași alegere ca `core/cronometru.py`): middleware-ul rulează pe buclă, ruta pe un fir din
threadpool, iar `anyio` copiază contextul când mută apelul pe fir. În afara unei cereri (cron, scripturi) e None -> notele
nu au autor și nu intră în coadă."""
import contextvars

_uid = contextvars.ContextVar("iconta_autor_cerere", default=None)


def seteaza(uid):
    """Întoarce tokenul pentru `reseteaza`."""
    return _uid.set(int(uid) if uid is not None else None)


def reseteaza(token):
    _uid.reset(token)


def uid():
    return _uid.get()


#: [368] notele ciornă (create ÎNAINTEA cererii) a căror validare internă la partidă simplă a fost refuzată, iar cererea curentă le-a
#: rezolvat cauza (raportul Z descărcat pe articol / pe rețetă, sau declarat „fără marfă din stoc”): middleware-ul le reîncearcă odată
#: cu notele cererii (`uc_coada.note_interne`). O listă pe cerere, pornită de middleware; în afara unei cereri nu se ține nimic.
_reincercare = contextvars.ContextVar("iconta_note_de_reincercat", default=None)


def porneste_reincercarea():
    """Întoarce tokenul pentru `opreste_reincercarea`; lista e a cererii (contextul se copiază pe firul rutei, lista rămâne aceeași)."""
    return _reincercare.set([])


def opreste_reincercarea(token):
    _reincercare.reset(token)


def reincearca_interna(nota_id):
    """Notează o notă de reîncercat la sfârșitul cererii (no-op în afara unei cereri)."""
    lista = _reincercare.get()
    if lista is not None and nota_id is not None:
        lista.append(int(nota_id))


def de_reincercat():
    return list(_reincercare.get() or [])

