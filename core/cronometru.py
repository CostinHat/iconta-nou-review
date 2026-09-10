# -*- coding: utf-8 -*-
"""core/cronometru.py — segmentele unei cereri, măsurate ÎN codul de producție.

**DE CE EXISTĂ, și de ce a trebuit cerută aprobare.** După valurile 1 și 1b, o cerere pe ruta
măsurată durează ~460 ms la k=10, din care serverul consumă doar ~18 ms de procesor. Restul se
așteaptă undeva, iar așteptarea nu se suprapune între cereri. Trei cauze au fost EXCLUSE prin
măsurătoare — clientul (0,32 saturare), pool-ul (10 vs 40: 381 → 379 ms), procesorul serverului
(0,47) — și n-am inventat a patra. *Ca să afli unde stă timpul într-o cerere, trebuie să te uiți
din interiorul ei;* din afară se vede numai totalul. De-aia instrumentarea asta a fost cerută și
aprobată separat, pe 10.09.2026, în loc să fie strecurată.

**INERTĂ IMPLICIT, și asta e chiar contractul ei.** `ACTIV` se citește O DATĂ, la import, din
`ICONTA_CRONOMETRU`. Nesetat — cum e în producție — fiecare funcție de aici iese pe prima linie, iar
în răspuns nu apare niciun antet. Nu se adaugă niciun middleware, deci calea de cerere nu capătă
niciun hop: ce se adaugă sunt câteva apeluri care, inactive, costă o comparație.

**CUM SE ÎNCHIDE BUCLA CU CLIENTUL.** Segmentele dinăuntrul handler-ului se măsoară cu
`perf_counter`, care e comparabil numai în procesul lui. Ca sonda să poată afla și cât a stat
cererea ÎNAINTE să ajungă la handler — coadă de fire, lanțul de middleware, parsarea multipart — se
trimit și două repere de **ceas de perete** (`time.time()`), comparabile între procese pe aceeași
mașină. Sonda scade: `intrare = handler_start − trimis`, `iesire = primit − handler_end`.

**CE NU MĂSOARĂ:** nimic din ce se întâmplă în alt proces (PostgreSQL nu e cronometrat pe dinăuntru,
doar durata apelului), și nimic sub granularitatea unui apel de funcție.
"""
import contextvars
import os
import time

#: comutatorul, citit O DATĂ la import. Nesetat = tot modulul e inert.
ACTIV = os.environ.get("ICONTA_CRONOMETRU") == "1"

#: prefixul antetelor. Un singur loc, ca sonda și garda să nu-l scrie fiecare din memorie.
ANTET = "x-crono-"

#: **ContextVar, nu thread-local.** Middleware-urile rulează pe BUCLĂ, handler-ul pe un FIR din
#: threadpool. Un thread-local nu trece granița aia, deci reperele puse în lanțul de middleware
#: n-ar fi văzute în handler. `contextvars` sunt copiate de `anyio` când mută apelul pe fir, iar
#: obiectul-listă e ACELAȘI — deci și ce adaugă firul se vede înapoi pe buclă, după `call_next`.
_stare = contextvars.ContextVar("crono", default=None)


def porneste(eticheta="intrare_lant"):
    """Începe cronometrarea cererii curente. Se cheamă din cel mai din AFARĂ middleware."""
    if not ACTIV:
        return
    _stare.set({"marci": [(eticheta, time.perf_counter())], "real_start": time.time()})


def marca(nume):
    """Un reper. Fără `porneste()` înainte, nu face nimic — deci nu poate cădea în producție."""
    if not ACTIV:
        return
    st = _stare.get()
    if st is None:
        return
    st["marci"].append((nume, time.perf_counter()))


def segmente():
    """`[(nume, milisecunde)]` — duratele DINTRE repere, nu reperele. Golește starea firului."""
    if not ACTIV:
        return []
    st = _stare.get()
    if not st or not st.get("marci"):
        return []
    marci = st["marci"]
    st["marci"] = []
    # Duratele cu ACELAȘI nume se ADUNĂ. `db.get_conn` se cheamă de mai multe ori pe unele căi;
    # fără însumare, a doua conexiune ar șterge măsurătoarea primei, iar profilul ar arăta mai
    # ieftin decât e. *Un reper care se suprascrie e mai rău decât unul care lipsește: lipsa se
    # vede în restul neacoperit, suprascrierea nu.*
    out = {}
    ordine = []
    for i in range(len(marci) - 1):
        nume = marci[i + 1][0]
        ms = (marci[i + 1][1] - marci[i][1]) * 1000
        if nume not in out:
            ordine.append(nume)
            out[nume] = 0.0
        out[nume] += ms
    return [(n, round(out[n], 2)) for n in ordine]


def antete():
    """`{antet: valoare}` pentru răspuns — sau `{}` când e inert.

    Se pun în ANTETE, nu în corp: corpul e contractul rutei, iar o măsurătoare care schimbă corpul
    ar schimba chiar lucrul măsurat. Un antet în plus nu e citit de nimeni în afară de sondă.
    """
    if not ACTIV:
        return {}
    st = _stare.get()
    real_start = (st or {}).get("real_start")
    segs = segmente()
    if real_start is None:
        return {}
    h = {ANTET + "start": "%.6f" % real_start, ANTET + "end": "%.6f" % time.time()}
    for nume, ms in segs:
        h[ANTET + nume.replace("_", "-")] = "%.2f" % ms
    return h


def citeste_antete(headers):
    """Partea de sondă: din antetele răspunsului, `{segment: ms}` + cele două repere de perete."""
    out = {}
    for k, v in dict(headers).items():
        kl = k.lower()
        if kl.startswith(ANTET):
            try:
                out[kl[len(ANTET):]] = float(v)
            except (TypeError, ValueError):
                pass
    return out
