# -*- coding: utf-8 -*-
"""core/inregistrare_libera.py — înregistrarea liberă cu confirmarea emailului (comanda Costin 15.10.2026, „Lotul 4” pct.2–3, verbatim
în DECIZII: „oricine își creează cabinetul, iar contul devine activ numai după clicul pe linkul de confirmare (valabil limitat, o
singură folosire). Până la confirmare nu se poate loga și nu se creează firme.” + „Protecție anti-roboți pe formular și limită de
încercări pe oră (pe adresă IP și pe email).”).

CEREREA ÎN AȘTEPTARE (`public.inregistrari_in_asteptare`, core/migrare_inregistrare_libera.py): formularul nu creează NIMIC în
`users` / `accounting_firms`; se păstrează datele lui, hash-ul parolei (scrypt, ca la cont) și hash-ul tokenului (sha256; tokenul
pleacă numai în link). Contul, acordul termenilor și firma din CUI se creează abia la confirmare (`uc_auth.confirma_inregistrarea`),
într-o singură tranzacție cu folosirea cererii. Până atunci nu există cont — deci nimic cu care să te loghezi și nicio firmă.
VALABILITATE_ORE ore, o singură folosire. Cererile neconfirmate se șterg la PASTRARE_ZILE zile după expirare (date personale fără cont).

ANTI-ROBOȚI — Cloudflare Turnstile (deficiența 257, comanda Costin 15.10.2026, verbatim în DECIZII „Poarta o dată pe lot”: „implementezi
Cloudflare Turnstile pe formularul «Înregistrează cabinetul tău», cum cerea lotul 4”; înlocuiește jetonul semnat + câmpul-capcană
construite în lotul 4). Sursa, Cloudflare (citită 15.10.2026): widgetul se încarcă din `SCRIPT_WIDGET` (CSP: `script-src` și `frame-src`
`https://challenges.cloudflare.com` — `config/nginx-iconta`); tokenul lui se validează pe server la `SITEVERIFY` (`secret`,
`response`, `remoteip`), e valabil 300 s și se folosește o singură dată. Cheile (`TURNSTILE_SITEKEY` public, `TURNSTILE_SECRET` privat)
vin din mediu; cheile de test publicate de Cloudflare (`CHEI_DE_TEST`, trec/pică mereu) se acceptă NUMAI pe instanța de probă (cutia
poștală de test) — pe producție o cheie de test ar lăsa orice robot să treacă. FAIL-CLOSED: fără chei, înregistrarea liberă e închisă
(`setari_platforma`); cu Cloudflare indisponibil, cererea e refuzată, cu motivul.
  - LIMITE PE ORĂ: `ritm_incape` pe IP (LIMITA_IP) și pe email (LIMITA_EMAIL), fereastră de o oră; la confirmare, pe IP.
Gard: core/test_inregistrare_libera.py + e2e frontend_test/e2e/e2e_inregistrare_libera.py.
"""
import datetime
import hashlib
import os
import secrets

from core import afirmatii as _af
from core import nucleu
from core.common import cate as _cate

VALABILITATE_ORE = 24
#: [deficiența 316, comanda Costin 17.10.2026 7.2] „cererile de înregistrare expirate (cele 2 de la persoane necunoscute) au dispărut din
#: listă; trebuie arătate «expirat»”: cererea expirată rămâne în Panou Admin, marcată, 30 de zile după expirare (era 7 — după ele ștergerea
#: le scotea din listă la următoarea înregistrare); apoi se șterge (date personale fără cont). Lista spune când.
PASTRARE_ZILE = 30
LIMITA_IP = 5            # încercări de înregistrare pe oră, de la același IP
LIMITA_EMAIL = 3         # încercări de înregistrare pe oră, pentru același email
LIMITA_CONFIRMARE_IP = 20
FEREASTRA_SEC = 3600
SITEVERIFY = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
SCRIPT_WIDGET = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit"
#: cheile de test publicate de Cloudflare (developers.cloudflare.com/turnstile/troubleshooting/testing): sitekey-uri, apoi secrete
CHEI_DE_TEST = ("1x00000000000000000000AA", "2x00000000000000000000AB", "1x00000000000000000000BB", "2x00000000000000000000BB",
                "3x00000000000000000000FF", "1x0000000000000000000000000000000AA", "2x0000000000000000000000000000000AA",
                "3x0000000000000000000000000000000AA")

MESAJ_PREA_DES = ("Prea multe încercări de înregistrare în ultima oră. Contul nu a fost creat — încearcă din nou peste o oră.")
MESAJ_ANTIROBOT = ("Verificarea anti-roboți n-a trecut, deci contul nu a fost creat. Așteaptă bifa verde din caseta de verificare de "
                   "deasupra butonului, apoi apasă din nou „Creează cont”.")
MESAJ_ANTIROBOT_INDISPONIBIL = ("Verificarea anti-roboți nu răspunde acum, deci contul nu a fost creat. Încearcă din nou peste câteva "
                                "minute.")
MESAJ_NECONFIRMAT = ("Contul nu e încă activ: confirmă adresa de email cu linkul primit la înregistrare (valabil %s). Dacă "
                     "linkul a expirat, înregistrează-te din nou." % _cate(VALABILITATE_ORE, "oră", "ore"))
REGULA = "Linkul de confirmare e valabil %s și se folosește o singură dată." % _cate(VALABILITATE_ORE, "oră", "ore")


def _hash(token):
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()


def chei_turnstile():
    """`(sitekey, secret)` din mediu, sau None dacă lipsesc — ori dacă sunt chei de test în afara instanței de probă."""
    sitekey, secret = os.environ.get("TURNSTILE_SITEKEY", "").strip(), os.environ.get("TURNSTILE_SECRET", "").strip()
    if not (sitekey and secret):
        return None
    if (sitekey in CHEI_DE_TEST or secret in CHEI_DE_TEST) and not os.environ.get("ICONTA_EMAIL_CUTIE"):
        return None
    return sitekey, secret


def _siteverify(secret, token, ip):
    import json
    import urllib.parse
    import urllib.request
    campuri = {"secret": secret, "response": token}
    if ip:
        campuri["remoteip"] = ip
    cerere = urllib.request.Request(SITEVERIFY, data=urllib.parse.urlencode(campuri).encode("utf-8"))
    with urllib.request.urlopen(cerere, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def verifica_turnstile(token, ip):
    """None dacă tokenul widgetului e bun; altfel `("respins" | "indisponibil", mesajul pentru om)`."""
    chei = chei_turnstile()
    if not chei:
        return "indisponibil", MESAJ_ANTIROBOT_INDISPONIBIL
    if not token:
        return "respins", MESAJ_ANTIROBOT
    try:
        r = _siteverify(chei[1], token, ip)
    except (OSError, ValueError) as e:      # rețea / HTTP (URLError, HTTPError sunt OSError) / răspuns care nu e JSON
        print("[inregistrare] siteverify indisponibil: %s, ip=%s" % (type(e).__name__, ip), flush=True)
        return "indisponibil", MESAJ_ANTIROBOT_INDISPONIBIL
    if r.get("success") is True:
        return None
    print("[inregistrare] turnstile respins: %s, ip=%s" % (r.get("error-codes"), ip), flush=True)
    return "respins", MESAJ_ANTIROBOT


def creeaza(cur, date, parola_hash, termeni_versiune, ip, acum=None):
    """Cererea în așteptare -> tokenul (în clar numai aici, pentru link)."""
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    cur.execute("DELETE FROM public.inregistrari_in_asteptare WHERE confirmata_la IS NULL AND expira_la < %s",
                (acum - datetime.timedelta(days=PASTRARE_ZILE),))
    tok = secrets.token_urlsafe(32)
    cur.execute("INSERT INTO public.inregistrari_in_asteptare (email, token_hash, nume_cabinet, nume, prenume, cui, parola_hash, "
                "termeni_versiune, ip, expira_la, telefon) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (date["email"], _hash(tok), date["nume_cabinet"], date.get("nume"), date.get("prenume"), date.get("cui") or None,
                 parola_hash, termeni_versiune, ip, acum + datetime.timedelta(hours=VALABILITATE_ORE), date.get("telefon")))
    return tok


def marcheaza_trimis(cur, token):
    """[deficiența 282] Emailul de confirmare a plecat (Brevo l-a primit): momentul, pe cerere."""
    cur.execute("UPDATE public.inregistrari_in_asteptare SET email_trimis_la = now() WHERE token_hash = %s", (_hash(token),))


def neconfirmate(cur, acum=None):
    """[deficiența 282] Cererile neconfirmate (și cele expirate, până la ștergerea lor după PASTRARE_ZILE), cele mai noi întâi."""
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    cur.execute("SELECT id, creat_la, nume_cabinet, email, email_trimis_la, expira_la, retrimiteri FROM public.inregistrari_in_asteptare "
                "WHERE confirmata_la IS NULL ORDER BY creat_la DESC")
    return [{"id": r[0], "creat_la": r[1].isoformat(), "nume_cabinet": r[2], "email": r[3],
             "email_trimis_la": r[4].isoformat() if r[4] else None, "expira_la": r[5].isoformat(), "expirata": r[5] < acum,
             "se_sterge_la": (r[5] + datetime.timedelta(days=PASTRARE_ZILE)).isoformat(),   # [316]
             "retrimiteri": r[6]} for r in cur.fetchall()]


def cerere_neconfirmata(cur, cerere_id):
    """[deficiența 282] (emailul, numele cabinetului) cererii care încă așteaptă confirmarea, sau None."""
    cur.execute("SELECT email, nume_cabinet FROM public.inregistrari_in_asteptare WHERE id = %s AND confirmata_la IS NULL", (cerere_id,))
    r = cur.fetchone()
    return (r[0], r[1]) if r else None


def inlocuieste_tokenul(cur, cerere_id, tok, acum=None):
    """[deficiența 282] „Retrimite confirmarea”, DUPĂ ce emailul cu `tok` a plecat: tokenul se înlocuiește (cel vechi nu se poate
    retrimite — se păstrează numai hash-ul), valabilitatea pornește din nou și se scrie momentul trimiterii. False dacă cererea a fost
    confirmată sau ștearsă între timp."""
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    cur.execute("UPDATE public.inregistrari_in_asteptare SET token_hash = %s, expira_la = %s, retrimiteri = retrimiteri + 1, "
                "email_trimis_la = now() WHERE id = %s AND confirmata_la IS NULL",
                (_hash(tok), acum + datetime.timedelta(hours=VALABILITATE_ORE), cerere_id))
    return cur.rowcount == 1


def sterge(cur, token):
    """Cererea a cărei confirmare n-a putut pleca pe email nu rămâne (nimeni n-ar putea s-o confirme)."""
    cur.execute("DELETE FROM public.inregistrari_in_asteptare WHERE token_hash = %s AND confirmata_la IS NULL", (_hash(token),))


def _refuz(cod, motiv, email):
    return _af.afirmatie("neconformitate", "confirmare_inregistrare", motiv,
                         unde=("înregistrarea pentru %s" % email) if email else "linkul primit", regula=REGULA, cod=cod)


def ia_pentru_confirmare(cur, token, acum=None):
    """Rândul cererii, BLOCAT (`FOR UPDATE`: două clicuri simultane pe același link nu creează două conturi) -> `{valida, cerere,
    refuz}`; `refuz` = afirmația tipată `neconformitate` (cod INEXISTENTA / FOLOSITA / EXPIRATA)."""
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    cur.execute("SELECT id, email, nume_cabinet, nume, prenume, cui, parola_hash, termeni_versiune, expira_la, confirmata_la, telefon "
                "FROM public.inregistrari_in_asteptare WHERE token_hash = %s FOR UPDATE", (_hash(token),))
    r = cur.fetchone()
    if not r:
        return {"valida": False, "cerere": None, "refuz": _refuz("INEXISTENTA", "Linkul de confirmare nu există. Folosește linkul din "
                                                                  "emailul primit la înregistrare.", None)}
    c = dict(zip(("id", "email", "nume_cabinet", "nume", "prenume", "cui", "parola_hash", "termeni_versiune", "expira_la",
                  "confirmata_la", "telefon"), r))
    if c["confirmata_la"] is not None:
        return {"valida": False, "cerere": c, "refuz": _refuz("FOLOSITA", "Linkul a fost folosit deja: contul cabinetului e activ. "
                                                               "Intră în cont cu emailul și parola.", c["email"])}
    if c["expira_la"] < acum:
        return {"valida": False, "cerere": c, "refuz": _refuz("EXPIRATA", "Linkul de confirmare a expirat (era valabil %s). "
                                                               "Înregistrează-te din nou." % _cate(VALABILITATE_ORE, "oră", "ore"), c["email"])}
    return {"valida": True, "cerere": c, "refuz": None}


def marcheaza_confirmata(cur, cerere_id, firm_id):
    cur.execute("UPDATE public.inregistrari_in_asteptare SET confirmata_la = now(), firm_id = %s WHERE id = %s", (firm_id, cerere_id))


def asteapta_confirmare(cur, email, parola, acum=None):
    """La un login eșuat: are emailul o cerere NECONFIRMATĂ și neexpirată, cu ACEEAȘI parolă? Numai atunci login-ul spune „confirmă
    emailul” — cine nu știe parola nu află că cererea există."""
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    cur.execute("SELECT to_regclass('public.inregistrari_in_asteptare') IS NOT NULL")   # înaintea migrării: nicio cerere
    if not cur.fetchone()[0]:
        return False
    cur.execute("SELECT parola_hash FROM public.inregistrari_in_asteptare WHERE email = %s AND confirmata_la IS NULL AND expira_la > %s "
                "ORDER BY id DESC LIMIT 5", (str(email or "").strip().lower(), acum))
    return any(nucleu.verifica_parola(parola or "", h) for (h,) in cur.fetchall())
