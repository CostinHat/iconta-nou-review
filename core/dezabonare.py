# -*- coding: utf-8 -*-
"""core/dezabonare.py — dezabonarea de la emailurile INFORMATIVE ale aplicației (deficiența 268; comanda 4 a lotului 5, verbatim în
DECIZII: „emailurile tranzacționale nu au deloc «Dezabonează-te» și nici antet List-Unsubscribe … Dezabonarea rămâne numai pe emailurile
informative/de promovare”).

CARE SUNT INFORMATIVE: lista închisă `INFORMATIVE` de mai jos — azi sinteza zilnică (seara, către patron) și recomandările (iConta
recomandat la adrese străine). Numai ele, marcate la apel cu `informativ=True` în `observare.trimite_email_html`, poartă subsolul
„Dezabonează-te” (`subsol_html`) și antetele `List-Unsubscribe` (https) + `List-Unsubscribe-Post: List-Unsubscribe=One-Click` (RFC 8058),
și numai ele nu mai pleacă la o adresă dezabonată (fail-closed: registrul necitibil = nu pleacă). TOATE celelalte sunt tranzacționale
(confirmarea înregistrării, invitațiile, resetarea parolei, linkul de logare, confirmarea adresei noi, anunțul de cabinet nou, alertele
către admin, facturile, rapoartele lunare, notificările de scadență, răspunsurile cabinetului): fără subsol, fără antet, pleacă oricum.
Dezabonarea e pe ADRESĂ (`public.emailuri_dezabonate`, core/migrare_emailuri_dezabonate.py), nu pe cont: recomandările pleacă la adrese
fără cont. Linkul e SEMNAT (`semnatura`: HMAC-SHA256 cu o cheie derivată din JWT_SECRET și scopul „dezabonare”), fără termen; pagina
publică (`GET /public/dezabonare`) arată confirmarea cu un buton, abia `POST` dezabonează — un scanner de linkuri nu dezabonează pe nimeni.
STRATUL: depozit (REPOSITORY) — SQL-ul registrului primește cursorul apelantului; conexiunea o deschid `observare` și `uc_public`.
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
#: emailurile informative / de promovare — SINGURELE cu dezabonare: {(fișier, funcția care trimite): ce sunt}. Un email informativ nou
#: intră aici, cu numele lui; garda (core/test_dezabonare.py) cere ca `informativ=True` să stea exact pe aceste locuri.
INFORMATIVE = {
    ("core/sinteza_zilnica.py", "ruleaza"): "sinteza zilnică a cabinetului",
    ("core/uc_comun.py", "_trimite_recomandari"): "recomandările iConta.eu",
}
MESAJ_CE_RAMANE = ("Te dezabonezi numai de la emailurile informative: %s. Emailurile legate de contul tău și de lucrul cu cabinetul — "
                   "confirmări, invitații, resetarea parolei, linkul de logare, facturi, rapoarte, alerte — vin în continuare."
                   % " și ".join(INFORMATIVE.values()))


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
            '<p style="font-size:12px;color:#5b6b7c;margin:0">Primești acest email informativ de la iConta.eu la adresa %s. '
            'Nu mai vrei emailuri informative de la noi? <a href="%s" style="color:#5b6b7c">Dezabonează-te</a>.</p>'
            % (_html.escape(normalizeaza(email)), _html.escape(link(email), quote=True)))


def e_dezabonata(cur, email):
    cur.execute("SELECT 1 FROM public.emailuri_dezabonate WHERE email = %s", (normalizeaza(email),))
    return cur.fetchone() is not None


def dezaboneaza(cur, email):
    """Adaugă adresa în registru. Întoarce True dacă s-a dezabonat acum, False dacă era deja (data primei dezabonări rămâne)."""
    cur.execute("INSERT INTO public.emailuri_dezabonate (email) VALUES (%s) ON CONFLICT (email) DO NOTHING RETURNING email",
                (normalizeaza(email),))
    return cur.fetchone() is not None
