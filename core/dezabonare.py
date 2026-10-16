# -*- coding: utf-8 -*-
"""core/dezabonare.py — dezabonarea de la emailurile aplicației (deficiența 268, „Lotul 5”, decizia în DECIZII: „emailurile
tranzacționale (confirmare, invitație, resetare parolă, anunț cabinet nou, alerte) nu au link «Dezabonează-te»”).

CE FACE. Dezabonarea e pe ADRESĂ (`public.emailuri_dezabonate`, core/migrare_emailuri_dezabonate.py), nu pe cont: invitația, emailul
pachetului lunar și alertele pleacă și la adrese fără cont. Fiecare email poartă, adăugate CENTRAL de `observare` (nu de apelanți):
  - subsolul „Dezabonează-te” (`subsol_html` în `trimite_email_html`, `subsol_text` în alertele text din `_trimite_brevo`);
  - antetele `List-Unsubscribe` (https) și `List-Unsubscribe-Post: List-Unsubscribe=One-Click` (RFC 8058: programul de email al
    destinatarului oferă singur butonul „Dezabonează-te” și trimite POST la adresa din antet).
Linkul e SEMNAT (`semnatura`: HMAC-SHA256 cu o cheie derivată din JWT_SECRET și scopul „dezabonare”), fără termen: un email vechi din
cutie trebuie să se poată dezabona oricând, iar semnătura împiedică pe oricine să dezaboneze adresa altcuiva. Pagina publică
(`GET /public/dezabonare`) arată confirmarea cu un buton; abia `POST` dezabonează — un scanner de linkuri care deschide adresa nu
dezabonează pe nimeni.

DUPĂ DEZABONARE nu mai pleacă nimic la acea adresă (`observare.refuz_dezabonare`, în `trimite_email_html`; refuzul se scrie în jurnal), CU
EXCEPȚIA emailurilor cerute chiar atunci de destinatar — resetarea parolei, linkul de logare, confirmarea propriei adrese (la
înregistrare sau la schimbarea adresei) — marcate la apel cu `cerut_de_destinatar=True`. Pagina de dezabonare o spune.
FAIL-CLOSED la emailuri: dacă registrul nu se poate citi, emailul nu pleacă (nu știm dacă adresa s-a dezabonat). La alertele interne
(`_trimite_brevo`) invers: o alertă despre o bază căzută trebuie să plece tocmai când registrul nu se poate citi.
STRATUL: depozit (REPOSITORY) — SQL-ul registrului primește cursorul apelantului, fără conexiuni și commit proprii; conexiunea o deschid
`observare` (verificarea dinaintea trimiterii) și `uc_public` (pagina).
Gard: core/test_dezabonare.py; e2e frontend_test/e2e/e2e_lot5_emailuri.py::test_def_268_*.
"""
import base64
import hashlib
import hmac
import html as _html
from urllib.parse import urlencode

from core.common import cfg, cfg_secret

RUTA = "/public/dezabonare"
SCOP = b"dezabonare"
MESAJ_CERUTE = ("Emailurile pe care le ceri chiar tu — resetarea parolei, linkul de logare, confirmarea adresei tale — vin în "
                "continuare, fiindcă fără ele nu ai putea intra în cont.")


def normalizeaza(email):
    return str(email or "").strip().lower()


def _cheie():
    """Cheia linkurilor de dezabonare: derivată din JWT_SECRET, pentru scopul ei. Un token de sesiune nu e o semnătură de dezabonare
    și invers. `cfg_secret` refuză un secret gol (o cheie goală ar face semnătura forjabilă de oricine)."""
    return hmac.new(cfg_secret("JWT_SECRET").encode(), SCOP, hashlib.sha256).digest()


def semnatura(email):
    sig = hmac.new(_cheie(), normalizeaza(email).encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).rstrip(b"=").decode()


def semnatura_valida(email, sig):
    return bool(normalizeaza(email)) and hmac.compare_digest(semnatura(email), str(sig or ""))


def link(email):
    return cfg("ICONTA_BAZA_URL", "https://iconta.eu") + RUTA + "?" + urlencode({"e": normalizeaza(email), "s": semnatura(email)})


def antete(email):
    """Antetele emailului (RFC 2369 + RFC 8058). Numai https: un `mailto:` ar ajunge ca simplu mesaj la cutia noastră, fără să
    dezaboneze nimic — o dezabonare cerută și neexecutată."""
    return {"List-Unsubscribe": "<%s>" % link(email), "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}


def subsol_html(email):
    return ('<hr style="border:none;border-top:1px solid #dbe1ea;margin:28px 0 12px">'
            '<p style="font-size:12px;color:#5b6b7c;margin:0">Primești acest email de la iConta.eu la adresa %s. '
            'Nu mai vrei emailuri de la noi? <a href="%s" style="color:#5b6b7c">Dezabonează-te</a>.</p>'
            % (_html.escape(normalizeaza(email)), _html.escape(link(email), quote=True)))


def subsol_text(email):
    return ("\n\n--\nPrimești acest mesaj de la iConta.eu la adresa %s. Nu mai vrei aceste emailuri? Dezabonează-te: %s"
            % (normalizeaza(email), link(email)))


def e_dezabonata(cur, email):
    cur.execute("SELECT 1 FROM public.emailuri_dezabonate WHERE email = %s", (normalizeaza(email),))
    return cur.fetchone() is not None


def dezaboneaza(cur, email):
    """Adaugă adresa în registru. Întoarce True dacă s-a dezabonat acum, False dacă era deja (data primei dezabonări rămâne)."""
    cur.execute("INSERT INTO public.emailuri_dezabonate (email) VALUES (%s) ON CONFLICT (email) DO NOTHING RETURNING email",
                (normalizeaza(email),))
    return cur.fetchone() is not None
