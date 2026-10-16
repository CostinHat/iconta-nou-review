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
    from core import dezabonare as _dez
    catre = cfg("ICONTA_ALERTA_EMAIL", _EMAIL_IMPLICIT)
    # [268] dezabonarea: refuzul dintr-un registru CITIT; registrul care nu se poate citi NU oprește alerta (fail-open, invers decât
    # la `trimite_email_html`): o alertă despre o bază căzută trebuie să plece tocmai atunci (core/dezabonare.py)
    try:
        if _adresa_dezabonata(catre):
            print("[ALERTĂ netrimisă, adresa %s s-a dezabonat] %s" % (catre, subiect), flush=True)
            return False
    except Exception as e:  # noqa: BLE001 — fail-open, cu urmă: alerta pleacă
        print("[alertă: registrul dezabonărilor nu s-a putut citi (%s: %s); alerta pleacă] %s" % (type(e).__name__, e, subiect),
              flush=True)
    payload = json.dumps({
        "sender": {"email": cfg("ICONTA_SENDER_EMAIL", _EMAIL_IMPLICIT), "name": "iConta.eu Alerte"},
        "to": [{"email": catre}],
        "subject": "[iConta.eu] " + subiect,
        "textContent": mesaj + _dez.subsol_text(catre),
        "headers": _dez.antete(catre),
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


def _adresa_dezabonata(catre):
    """[268] Adresa e în registrul dezabonărilor (core/dezabonare.py)? Ridică dacă registrul nu se poate citi — apelantul alege: emailul
    nu pleacă (`refuz_dezabonare`, fail-closed), alerta internă pleacă (`_trimite_brevo`, fail-open)."""
    from core import db, dezabonare as _dez
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = _dez.e_dezabonata(cur, catre)
        conn.rollback()
    return r


def refuz_dezabonare(catre):
    """De ce NU pleacă un email la `catre` (text), sau None. Nu ridică: registrul care nu se poate citi e un refuz, cu motivul lui."""
    from core import dezabonare as _dez
    try:
        d = _adresa_dezabonata(catre)
    except Exception as e:  # noqa: BLE001 — devine motivul refuzului, nu se pierde
        return "registrul dezabonărilor nu s-a putut citi (%s: %s), deci emailul către %s nu pleacă" % (type(e).__name__, e, catre)
    return ("adresa %s s-a dezabonat de la emailurile iConta.eu" % _dez.normalizeaza(catre)) if d else None


def _in_cutia_de_test(director, catre, subiect, html, antete):
    """[15.10.2026, lotul 4] CUTIA POȘTALĂ DE TEST: pe instanța de probă (`ICONTA_EMAIL_CUTIE`, pus numai de `scripts/e2e_poarta.py`)
    emailul se scrie ca fișier JSON în director, în loc să plece — probele își iau de acolo linkul de confirmare a înregistrării, pe
    care altfel numai destinatarul îl vede. Producția nu are variabila (gard `core/test_cutia_email_numai_la_proba.py`)."""
    import json
    import time
    cale = os.path.join(director, "%d_%s.json" % (time.time_ns(), "".join(c if c.isalnum() else "_" for c in catre)))
    try:
        os.makedirs(director, exist_ok=True)
        with open(cale, "w", encoding="utf-8") as f:
            json.dump({"catre": catre, "subiect": subiect, "html": html, "antete": antete}, f, ensure_ascii=False)
    except OSError as e:          # cutia care nu primește = emailul care n-a plecat (probele îl simulează așa: director needitabil)
        print("[email netrimis, cutia de test] %s -> %s: %s" % (subiect, catre, e))
        return False
    return True


# [p30_email_generic]
def trimite_email_html(catre, subiect, html, attachments=None, reply_to=None,
                       expeditor_nume="iConta.eu", cerut_de_destinatar=False):
    """Email HTML catre un destinatar arbitrar (nu doar alerta interna).
    Refoloseste cheia Brevo + sender-ul (env, citit la apel). Intoarce True/False.

    reply_to: adresa la care raspunde destinatarul (Reply-To). From-ul RAMANE
      ICONTA_SENDER_EMAIL (implicit contact@iconta.eu) - autorizat SPF/DKIM pe iconta.eu; NU se
      trimite From pe alt domeniu (ar pica SPF/DMARC). Folosit de F131: emailul
      pleaca in numele firmei (expeditor_nume='<Firma> prin iConta'), dar reply-to
      = adresa firmei ca raspunsul clientului sa ajunga la ea, nu la iConta.
    expeditor_nume: numele afisat al expeditorului (implicit 'iConta').
    cerut_de_destinatar: [268] emailul e cerut CHIAR ACUM de destinatar (resetarea parolei, linkul de logare, confirmarea propriei
      adrese) — pleacă și la o adresă dezabonată. Orice alt email NU pleacă la o adresă din registrul dezabonărilor (refuzul se scrie în
      jurnal, iar funcția întoarce False). Subsolul „Dezabonează-te” și antetele List-Unsubscribe se pun AICI, la toate emailurile —
      un singur loc, nu la fiecare apelant (core/dezabonare.py; gard core/test_dezabonare.py)."""
    from core import dezabonare as _dez
    if not cerut_de_destinatar:
        motiv = refuz_dezabonare(catre)
        if motiv:
            print("[email netrimis, %s] %s -> %s" % (motiv, subiect, catre), flush=True)
            return False
    html = html + _dez.subsol_html(catre)
    antete = _dez.antete(catre)
    cutie = cfg("ICONTA_EMAIL_CUTIE")
    if cutie:
        return _in_cutia_de_test(cutie, catre, subiect, html, antete)
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
        "headers": antete,
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


def trimite_email_html_sau_semnaleaza(eticheta, catre, subiect, html, alerta=False, **k):
    """`trimite_email_html` + semnalarea eșecului, într-un singur loc. Întoarce True/False (emailul a plecat sau nu).

    DE CE (15.10.2026): `trimite_email_html` semnalează eșecul prin `False` (fără cheie Brevo, Brevo refuză, rețeaua cade) și practic
    nu aruncă. Patru locuri îl prindeau NUMAI pe excepție (`try: ... except: esec_secundar(..., alerta=True)`) — resetarea parolei,
    linkul de logare, activarea asistentului, bun venit — deci alerta R73 „cale de acces” nu pleca niciodată la un eșec real; alte
    șapte ignorau rezultatul cu totul, iar invitația de cabinet îi spunea superadminului „a plecat” fără să știe. Aici eșecul, oricum
    ar veni, ajunge în `esec_secundar` (cu alertă numai unde tăcerea taie accesul cuiva — criteriul R73 din `esec_secundar`).
    Gard: `core/test_email_html_rezultat.py` (orice apel direct al lui `trimite_email_html` în producție își citește rezultatul)."""
    try:
        ok = trimite_email_html(catre, subiect, html, **k)
    except Exception as e:  # noqa: BLE001 — eșecul se semnalează mai jos, operația principală continuă
        esec_secundar(eticheta, e, alerta=alerta)
        return False
    if not ok:
        esec_secundar(eticheta, RuntimeError("emailul către %s nu a plecat (adresa dezabonată, Brevo a refuzat, lipsește cheia sau rețeaua — "
                                                  "motivul e în rândul de jurnal de dinainte)" % catre),
                      alerta=alerta)
    return bool(ok)


def alerteaza(cheie, subiect, mesaj, acum=None):
    """
    Trimite alerta DOAR dacă throttling permite. cheie = grupează alertele
    de același fel (ex. 'pool_plin') ca să nu se retrimită des.

    **SINCRONĂ, și rămâne așa.** Întoarce dacă alerta chiar a plecat, iar `expirare_cote` numără pe
    răspunsul ăsta. Cine nu are nevoie de răspuns și nu vrea să aștepte Brevo folosește
    `alerteaza_in_fundal`.
    """
    if trebuie_trimisa(cheie, acum=acum):
        return _trimite_brevo(subiect, mesaj)
    return False


def alerteaza_in_fundal(cheie, subiect, mesaj, acum=None):
    """Ca `alerteaza`, dar trimiterea pleacă pe un FIR PROPRIU. Întoarce dacă a fost pornită.

    **[P5 val 3, 10.09.2026] De ce.** Alerta despre un eșec secundar se ridică din interiorul unui
    `except` care, de cele mai multe ori, e sub un `with db.get_conn()`. Apelul la Brevo are termen
    de **10 s** — deci o conexiune din cele 10 ale pool-ului stătea blocată tot atâta, pentru un
    e-mail care n-are nicio legătură cu tranzacția. *Alerta nu e un efect al tranzacției: e o
    observație despre ceva care s-a întâmplat deja.*

    **Firul NU e `daemon`.** Interpretorul îl așteaptă la oprirea procesului, deci o alertă ridicată
    cu o clipă înainte de restart tot pleacă. Întârzierea maximă a opririi e chiar termenul de 10 s
    al apelului. *O alertă pierdută la restart ar fi exact tăcerea pe care funcția asta există s-o
    înlăture.*

    **Ce se pierde, declarat:** apelantul nu mai află dacă e-mailul a plecat. De-aia funcția e
    separată, nu o schimbare a celei de sus — `expirare_cote` numără pe răspunsul ei.
    """
    if not trebuie_trimisa(cheie, acum=acum):
        return False
    import threading
    threading.Thread(target=_trimite_brevo, args=(subiect, mesaj),
                     name="alerta-brevo", daemon=False).start()
    return True


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
        # [P5 val 3] ÎN FUNDAL: apelantul e aproape întotdeauna sub un `with db.get_conn()`, iar
        # Brevo are termen de 10 s. Nimeni nu citește rezultatul de aici, deci nu se pierde nimic
        # în afară de așteptare.
        alerteaza_in_fundal("secundar_%s" % eticheta,
                            "Esec pe cale secundara: %s" % eticheta,
                            "Operatia principala a continuat, dar '%s' a esuat:\n\n%s"
                            % (eticheta, traceback.format_exc()))
