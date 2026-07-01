"""
core/observare.py — strat de observare: măsoară timpi + ocupare pool, alertă pe prag.
Modul IZOLAT și SUBSTITUIBIL: rutele nu știu că există; canalul de alertă
(Brevo azi, Slack mâine) se schimbă fără să atingi nimic altceva.

Ce monitorizează:
  - query/operație lentă (durată > prag)         -> alertă
  - pool aproape epuizat (ocupare > prag %)       -> alertă
  - eroare la conexiune DB                         -> alertă imediată

Throttling: aceeași alertă nu se retrimite mai des de N minute (anti-spam).
Logica de throttling + decizie prag e PURĂ (testabilă fără DB/email).
Trimiterea efectivă Brevo se dovedește pe server.
"""
from __future__ import annotations
import os
import time

REGULI = "2026.1"
MODUL = "observare"

# — praguri implicite (calibrate pe trafic real la deploy) —
PRAG_QUERY_LENT_SEC = float(os.environ.get("ICONTA_PRAG_QUERY_SEC", "2.0"))
PRAG_POOL_PCT = float(os.environ.get("ICONTA_PRAG_POOL_PCT", "80"))   # % din maxconn
THROTTLE_MIN = float(os.environ.get("ICONTA_ALERTA_THROTTLE_MIN", "15"))

# email destinatar alerte + sender (Brevo deja configurat pe iconta.eu)
ALERTA_CATRE = os.environ.get("ICONTA_ALERTA_EMAIL", "contact@iconta.eu")
ALERTA_DE_LA = os.environ.get("ICONTA_SENDER_EMAIL", "contact@iconta.eu")
BREVO_KEY = os.environ.get("BREVO_API_KEY", "")

# stare throttling: {cheie_alerta: ultima_trimitere_epoch}
_ultima_alerta = {}


# ============================================================
#  THROTTLING — pur, testabil
# ============================================================
def trebuie_trimisa(cheie, acum=None, throttle_min=None, stare=None):
    """
    True dacă alerta cu 'cheie' poate fi trimisă (n-a fost trimisă recent).
    Pură: primește acum + stare, nu citește ceasul/global direct.
    """
    acum = acum if acum is not None else time.time()
    throttle_min = THROTTLE_MIN if throttle_min is None else throttle_min
    stare = _ultima_alerta if stare is None else stare
    ultima = stare.get(cheie)
    if ultima is None or (acum - ultima) >= throttle_min * 60:
        stare[cheie] = acum
        return True
    return False


# ============================================================
#  DECIZIE PRAG — pur, testabil
# ============================================================
def pool_ocupare_pct(folosite, maxconn):
    """Procent de ocupare a pool-ului. Pură."""
    if maxconn <= 0:
        return 0.0
    return 100.0 * folosite / maxconn


def evalueaza_pool(folosite, maxconn, prag_pct=None):
    """
    Întoarce (alerta_da, pct, mesaj). Pură.
    """
    prag = PRAG_POOL_PCT if prag_pct is None else prag_pct
    pct = pool_ocupare_pct(folosite, maxconn)
    if pct >= prag:
        return True, pct, ("Pool DB la %.0f%% (%d/%d conexiuni). "
                           "Crește maxconn sau verifică operații lente."
                           % (pct, folosite, maxconn))
    return False, pct, None


def evalueaza_durata(eticheta, durata_sec, prag_sec=None):
    """Întoarce (alerta_da, mesaj) pentru o operație cronometrată. Pură."""
    prag = PRAG_QUERY_LENT_SEC if prag_sec is None else prag_sec
    if durata_sec >= prag:
        return True, ("Operație lentă: %s a durat %.2fs (prag %.1fs)."
                      % (eticheta, durata_sec, prag))
    return False, None


# ============================================================
#  CANAL ALERTĂ — Brevo (substituibil). Se dovedește pe server.
# ============================================================
def _trimite_brevo(subiect, mesaj):
    """Trimite email via Brevo. Întoarce True/False. Izolat — singurul loc
    care știe de Brevo; schimbi aici pt Slack/alt canal."""
    if not BREVO_KEY:
        # fără cheie (ex. local): doar log, nu crăpa aplicația
        print("[ALERTĂ netrimisă, fără BREVO_API_KEY] %s — %s" % (subiect, mesaj))
        return False
    import json
    import urllib.request
    payload = json.dumps({
        "sender": {"email": ALERTA_DE_LA, "name": "iConta Alerte"},
        "to": [{"email": ALERTA_CATRE}],
        "subject": "[iConta] " + subiect,
        "textContent": mesaj,
    }).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email", data=payload,
        headers={"api-key": BREVO_KEY, "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 201)
    except Exception as e:
        print("[ALERTĂ eșuată Brevo] %s — %s" % (subiect, e))
        return False


# [p30_email_generic]
def trimite_email_html(catre, subiect, html, attachments=None):
    """Email HTML catre un destinatar arbitrar (nu doar alerta interna).
    Refoloseste BREVO_KEY + sender. Intoarce True/False."""
    if not BREVO_KEY:
        print("[email netrimis, fara BREVO_API_KEY] %s -> %s" % (subiect, catre))
        return False
    import json
    import urllib.request
    corp = {
        "sender": {"email": ALERTA_DE_LA, "name": "iConta"},
        "to": [{"email": catre}],
        "subject": subiect,
        "htmlContent": html,
    }
    if attachments:
        # attachments = list de {"content": <base64 str>, "name": <str>}
        corp["attachment"] = attachments
    payload = json.dumps(corp).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email", data=payload,
        headers={"api-key": BREVO_KEY, "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status in (200, 201)
    except Exception as e:
        print("[email esuat Brevo] %s -> %s: %s" % (subiect, catre, e))
        return False


def alerteaza(cheie, subiect, mesaj, acum=None):
    """
    Trimite alerta DOAR dacă throttling permite. cheie = grupează alertele
    de același fel (ex. 'pool_plin') ca să nu se retrimită des.
    """
    if trebuie_trimisa(cheie, acum=acum):
        return _trimite_brevo(subiect, mesaj)
    return False


# ============================================================
#  CRONOMETRU — wrapper peste o operație. Emite alertă dacă e lentă.
# ============================================================
class masoara:
    """
    Context manager: cronometrează un bloc, alertă dacă depășește pragul.
        with masoara("D406 firma X"):
            ... operație ...
    Rutele NU știu de el — se pune în get_conn-wrapper sau în dispatch.
    """
    def __init__(self, eticheta, prag_sec=None):
        self.eticheta = eticheta
        self.prag_sec = prag_sec
        self.t0 = None
        self.durata = None

    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.durata = time.time() - self.t0
        if exc_type is not None:
            # eroare în timpul operației — alertă imediată (ex. DB căzut)
            alerteaza("eroare_op:" + self.eticheta,
                      "Eroare la %s" % self.eticheta,
                      "%s: %s" % (exc_type.__name__, exc))
            return False  # nu înghite excepția
        lent, mesaj = evalueaza_durata(self.eticheta, self.durata, self.prag_sec)
        if lent:
            alerteaza("lent:" + self.eticheta, "Operație lentă", mesaj)
        return False


# ============================================================
#  VERIFICARE POOL — apelată periodic sau după fiecare request
# ============================================================
def verifica_pool(pool_obj, maxconn):
    """
    Inspectează ocuparea pool-ului și alertează la prag. Întoarce pct.
    pool_obj: ThreadedConnectionPool. Numărul de conexiuni folosite se
    deduce din structura internă (_used) — verificat pe server, defensiv.
    """
    try:
        folosite = len(getattr(pool_obj, "_used", {}))
    except Exception:
        return None
    alerta, pct, mesaj = evalueaza_pool(folosite, maxconn)
    if alerta:
        alerteaza("pool_plin", "Pool DB aproape epuizat", mesaj)
    return pct
