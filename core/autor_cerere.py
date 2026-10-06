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
