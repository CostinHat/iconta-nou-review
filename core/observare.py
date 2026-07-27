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
import time

from core.common import cfg

REGULI = "2026.1"
MODUL = "observare"

# Config din env — citită LA APEL prin cfg() (nu înghețată la import, item 5).
# Praguri (float): ICONTA_PRAG_QUERY_SEC=2.0, ICONTA_PRAG_POOL_PCT=80 (% maxconn),
#   ICONTA_ALERTA_THROTTLE_MIN=15. Email: ICONTA_ALERTA_EMAIL (destinatar),
#   ICONTA_SENDER_EMAIL (sender). Cheie Brevo: BREVO_API_KEY.
_EMAIL_IMPLICIT = "contact@iconta.eu"   # destinatar + sender impliciti (SPF/DKIM iconta.eu)

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
    throttle_min = cfg("ICONTA_ALERTA_THROTTLE_MIN", "15", float) if throttle_min is None else throttle_min
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
    prag = cfg("ICONTA_PRAG_POOL_PCT", "80", float) if prag_pct is None else prag_pct
    pct = pool_ocupare_pct(folosite, maxconn)
    if pct >= prag:
        return True, pct, ("Pool DB la %.0f%% (%d/%d conexiuni). "
                           "Crește maxconn sau verifică operații lente."
                           % (pct, folosite, maxconn))
    return False, pct, None


def evalueaza_durata(eticheta, durata_sec, prag_sec=None):
    """Întoarce (alerta_da, mesaj) pentru o operație cronometrată. Pură."""
    prag = cfg("ICONTA_PRAG_QUERY_SEC", "2.0", float) if prag_sec is None else prag_sec
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
    brevo_key = cfg("BREVO_API_KEY")
    if not brevo_key:
        # fără cheie (ex. local): doar log, nu crăpa aplicația
        print("[ALERTĂ netrimisă, fără BREVO_API_KEY] %s — %s" % (subiect, mesaj))
        return False
    import json
    import urllib.request
    payload = json.dumps({
        "sender": {"email": cfg("ICONTA_SENDER_EMAIL", _EMAIL_IMPLICIT), "name": "iConta.eu Alerte"},
        "to": [{"email": cfg("ICONTA_ALERTA_EMAIL", _EMAIL_IMPLICIT)}],
        "subject": "[iConta.eu] " + subiect,
        "textContent": mesaj,
    }).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email", data=payload,
        headers={"api-key": brevo_key, "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 201)
    except Exception as e:
        print("[ALERTĂ eșuată Brevo] %s — %s" % (subiect, e))
        return False


# [p30_email_generic]
def trimite_email_html(catre, subiect, html, attachments=None, reply_to=None,
                       expeditor_nume="iConta.eu"):
    """Email HTML catre un destinatar arbitrar (nu doar alerta interna).
    Refoloseste cheia Brevo + sender-ul (env, citit la apel). Intoarce True/False.

    reply_to: adresa la care raspunde destinatarul (Reply-To). From-ul RAMANE
      ICONTA_SENDER_EMAIL (implicit contact@iconta.eu) - autorizat SPF/DKIM pe iconta.eu; NU se
      trimite From pe alt domeniu (ar pica SPF/DMARC). Folosit de F131: emailul
      pleaca in numele firmei (expeditor_nume='<Firma> prin iConta'), dar reply-to
      = adresa firmei ca raspunsul clientului sa ajunga la ea, nu la iConta.
    expeditor_nume: numele afisat al expeditorului (implicit 'iConta')."""
    brevo_key = cfg("BREVO_API_KEY")
    if not brevo_key:
        print("[email netrimis, fara BREVO_API_KEY] %s -> %s" % (subiect, catre))
        return False
    import json
    import urllib.request
    corp = {
        "sender": {"email": cfg("ICONTA_SENDER_EMAIL", _EMAIL_IMPLICIT), "name": expeditor_nume},
        "to": [{"email": catre}],
        "subject": subiect,
        "htmlContent": html,
    }
    if reply_to:
        corp["replyTo"] = {"email": reply_to}
    if attachments:
        # attachments = list de {"content": <base64 str>, "name": <str>}
        corp["attachment"] = attachments
    payload = json.dumps(corp).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email", data=payload,
        headers={"api-key": brevo_key, "content-type": "application/json"})
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


# ============================================================
#  ESEC PE CALE SECUNDARA — inghitit, dar NU tacut
# ============================================================
def esec_secundar(eticheta, eroare, alerta=False):
    """Un efect secundar a esuat. Operatia principala continua, dar eroarea NU dispare.

    DE CE (27.07.2026): 15 locuri aveau `except: pass` peste un query. Alegerea de a nu
    opri operatia principala e corecta - un audit_log care crapa nu trebuie sa impiedice
    login-ul. Dar tacerea nu era o alegere, era o scapare: nimic, nicaieri, nu spunea ca
    s-a intamplat. Un audit_log care esueaza tacut e mai rau decat unul absent, pentru ca
    `alerta_acces` il citeste ca sa detecteze acces anormal - deci gardul de securitate ar
    raporta linistit "0 verificati" pe o baza care nu se scrie.

    alerta=True doar pentru caile unde tacerea are cost legal sau de securitate (evidenta
    prelucrarilor GDPR, provisionare esuata). Restul: log. Alerta pe orice ar produce
    zgomot, iar un canal zgomotos se ignora - alt fel de tacere.
    """
    print("[esec secundar: %s] %s: %s" % (eticheta, type(eroare).__name__, eroare), flush=True)
    if alerta:
        import traceback
        alerteaza("secundar_%s" % eticheta,
                  "Esec pe cale secundara: %s" % eticheta,
                  "Operatia principala a continuat, dar '%s' a esuat:\n\n%s"
                  % (eticheta, traceback.format_exc()))
