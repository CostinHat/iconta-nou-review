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

ANTI-ROBOȚI, fără servicii externe (CSP-ul aplicației permite numai `self`):
  - JETONUL FORMULARULUI: semnat de server când se deschide formularul (`jeton_formular`); înregistrarea îl cere, mai vechi de
    MIN_SECUNDE (un om nu completează formularul mai repede) și mai nou de MAX_ORE_FORMULAR. Un robot care trimite direct cererea
    trebuie întâi să ceară jetonul și să aștepte.
  - CÂMPUL-CAPCANĂ (`site_web`): ascuns (`hidden`), deci un om nu-l completează; completat -> răspunsul de reușită, fără nicio scriere
    și fără email (robotul nu află că a fost oprit).
  - LIMITE PE ORĂ: `ritm_incape` pe IP (LIMITA_IP) și pe email (LIMITA_EMAIL), fereastră de o oră; la confirmare, pe IP.
Gard: core/test_inregistrare_libera.py + e2e frontend_test/e2e/e2e_inregistrare_libera.py.
"""
import datetime
import hashlib
import secrets

from core import afirmatii as _af
from core import nucleu

VALABILITATE_ORE = 24
PASTRARE_ZILE = 7
MIN_SECUNDE = 3
MAX_ORE_FORMULAR = 2
LIMITA_IP = 5            # încercări de înregistrare pe oră, de la același IP
LIMITA_EMAIL = 3         # încercări de înregistrare pe oră, pentru același email
LIMITA_CONFIRMARE_IP = 20
FEREASTRA_SEC = 3600
_SCOP = "formular_inregistrare"

MESAJ_PREA_DES = ("Prea multe încercări de înregistrare în ultima oră. Contul nu a fost creat — încearcă din nou peste o oră.")
MESAJ_FORMULAR = ("Formularul nu se poate trimite așa: redeschide-l („Client nou”), completează-l și trimite-l din nou.")
MESAJ_PREA_REPEDE = "Formularul a fost trimis prea repede. Verifică datele și apasă din nou „Creează cont”."
MESAJ_NECONFIRMAT = ("Contul nu e încă activ: confirmă adresa de email cu linkul primit la înregistrare (valabil %d de ore). Dacă "
                     "linkul a expirat, înregistrează-te din nou." % VALABILITATE_ORE)
REGULA = "Linkul de confirmare e valabil %d de ore și se folosește o singură dată." % VALABILITATE_ORE


def _hash(token):
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()


def _secret():
    """Cheia jetonului de formular, derivată din secretul sesiunilor, cu scopul ei: un jeton de formular nu poate trece drept sesiune."""
    from core.common import cfg_secret
    return cfg_secret("JWT_SECRET") + "|" + _SCOP


def jeton_formular(acum=None):
    """Jetonul semnat al formularului — se dă la deschiderea lui (GET /public/inregistrare)."""
    return nucleu.creeaza_token({"scop": _SCOP}, _secret(), durata_sec=MAX_ORE_FORMULAR * 3600, acum=acum)


def verifica_formular(jeton, acum=None):
    """None dacă jetonul e bun; altfel mesajul pentru om (jeton lipsă/falsificat/expirat, sau trimis prea repede)."""
    import time
    acum = acum if acum is not None else int(time.time())
    if not jeton:
        return MESAJ_FORMULAR
    r = nucleu.verifica_token(jeton, _secret(), acum=acum)
    if not r.get("ok") or (r.get("payload") or {}).get("scop") != _SCOP:
        return MESAJ_FORMULAR
    if acum - int(r["payload"].get("iat", acum)) < MIN_SECUNDE:
        return MESAJ_PREA_REPEDE
    return None


def creeaza(cur, date, parola_hash, termeni_versiune, ip, acum=None):
    """Cererea în așteptare -> tokenul (în clar numai aici, pentru link)."""
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    cur.execute("DELETE FROM public.inregistrari_in_asteptare WHERE confirmata_la IS NULL AND expira_la < %s",
                (acum - datetime.timedelta(days=PASTRARE_ZILE),))
    tok = secrets.token_urlsafe(32)
    cur.execute("INSERT INTO public.inregistrari_in_asteptare (email, token_hash, nume_cabinet, nume, prenume, cui, parola_hash, "
                "termeni_versiune, ip, expira_la) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (date["email"], _hash(tok), date["nume_cabinet"], date.get("nume"), date.get("prenume"), date.get("cui") or None,
                 parola_hash, termeni_versiune, ip, acum + datetime.timedelta(hours=VALABILITATE_ORE)))
    return tok


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
    cur.execute("SELECT id, email, nume_cabinet, nume, prenume, cui, parola_hash, termeni_versiune, expira_la, confirmata_la "
                "FROM public.inregistrari_in_asteptare WHERE token_hash = %s FOR UPDATE", (_hash(token),))
    r = cur.fetchone()
    if not r:
        return {"valida": False, "cerere": None, "refuz": _refuz("INEXISTENTA", "Linkul de confirmare nu există. Folosește linkul din "
                                                                  "emailul primit la înregistrare.", None)}
    c = dict(zip(("id", "email", "nume_cabinet", "nume", "prenume", "cui", "parola_hash", "termeni_versiune", "expira_la",
                  "confirmata_la"), r))
    if c["confirmata_la"] is not None:
        return {"valida": False, "cerere": c, "refuz": _refuz("FOLOSITA", "Linkul a fost folosit deja: contul cabinetului e activ. "
                                                               "Intră în cont cu emailul și parola.", c["email"])}
    if c["expira_la"] < acum:
        return {"valida": False, "cerere": c, "refuz": _refuz("EXPIRATA", "Linkul de confirmare a expirat (era valabil %d de ore). "
                                                               "Înregistrează-te din nou." % VALABILITATE_ORE, c["email"])}
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
