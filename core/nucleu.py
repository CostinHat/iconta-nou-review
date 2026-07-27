"""
core/nucleu.py — infrastructură: parole + token-uri + RBAC. Logică PURĂ, fără DB.
(Partea de DB — conexiune, query-uri — se face la integrarea pe server.)

Surse:
- Parole: OWASP Password Storage Cheat Sheet (2024/2026) — scrypt N=2^16, r=8, p=1,
  salt 16 octeți, hash 32 octeți, doar stdlib (hashlib.scrypt), memory-hard.
- Token: HMAC-SHA256 semnat, cu expirare (stateless, verificabil fără DB).
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import secrets
import time

REGULI = "2026.1"
MODUL = "nucleu"

# — parametri scrypt (OWASP) —
_SCRYPT_N = 2 ** 16
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_DKLEN = 32
_SCRYPT_MAXMEM = 132 * 1024 * 1024
_SALT_BYTES = 16


def _rezultat(ok, cod=None, mesaj=None, **extra):
    r = {"ok": ok}
    if not ok:
        r["cod"] = cod
        r["mesaj"] = mesaj
    r.update(extra)
    return r


def _b64e(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _b64d(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


# ============================================================
#  PAROLE (scrypt, format PHC-like: scrypt$n,r,p$salt$hash)
# ============================================================
def hash_parola(parola):
    salt = secrets.token_bytes(_SALT_BYTES)
    h = hashlib.scrypt(parola.encode("utf-8"), salt=salt,
                       n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P,
                       dklen=_SCRYPT_DKLEN, maxmem=_SCRYPT_MAXMEM)
    return f"scrypt${_SCRYPT_N},{_SCRYPT_R},{_SCRYPT_P}${_b64e(salt)}${_b64e(h)}"


def verifica_parola(parola, hash_stocat):
    try:
        schema, params, salt_b64, hash_b64 = hash_stocat.split("$")
        if schema != "scrypt":
            return False
        n, r, p = (int(x) for x in params.split(","))
        salt = _b64d(salt_b64)
        asteptat = _b64d(hash_b64)
        calculat = hashlib.scrypt(parola.encode("utf-8"), salt=salt,
                                  n=n, r=r, p=p, dklen=len(asteptat),
                                  maxmem=_SCRYPT_MAXMEM)
        return hmac.compare_digest(calculat, asteptat)
    except (ValueError, AttributeError):
        return False


# ============================================================
#  TOKEN semnat HMAC-SHA256, cu expirare
# ============================================================
def creeaza_token(payload, secret, durata_sec=3600, acum=None):
    """payload: dict. Adaugă 'exp'. Întoarce string token.
    GARDĂ SECURITATE: secret gol/None -> excepție. HMAC cu cheie goală e forjabil de oricine
    (cheia publică = ""), deci NICIODATĂ nu semnăm cu cheie goală. Vezi DECIZII 22.07."""
    if not secret:
        raise ValueError("secret gol la semnarea tokenului — refuz (ar fi forjabil cu cheie goală)")
    acum = acum if acum is not None else int(time.time())
    date = {**payload, "iat": acum, "exp": acum + durata_sec}  # [reset_parola_v1] iat pt invalidarea sesiunilor
    corp = _b64e(json.dumps(date, separators=(",", ":"), sort_keys=True).encode())
    sig = hmac.new(secret.encode(), corp.encode(), hashlib.sha256).digest()
    return f"{corp}.{_b64e(sig)}"


def verifica_token(token, secret, acum=None):
    """Întoarce {ok, payload} sau {ok:False, cod, mesaj}.
    GARDĂ SECURITATE: secret gol/None -> excepție (orice token forjat cu cheie goală ar trece).
    Vezi DECIZII 22.07."""
    if not secret:
        raise ValueError("secret gol la verificarea tokenului — refuz (orice token forjat cu cheie goală ar trece)")
    acum = acum if acum is not None else int(time.time())
    try:
        corp, sig_b64 = token.split(".")
    except (ValueError, AttributeError):
        return _rezultat(False, "TOKEN_INVALID", "format token incorect")
    asteptat = hmac.new(secret.encode(), corp.encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(_b64d(sig_b64), asteptat):
        return _rezultat(False, "TOKEN_INVALID", "semnătură invalidă (token modificat)")
    payload = json.loads(_b64d(corp))
    if payload.get("exp", 0) < acum:
        return _rezultat(False, "TOKEN_EXPIRAT", "token expirat")
    return _rezultat(True, payload=payload)


# ============================================================
#  RBAC — 3 roluri
# ============================================================
ROLURI = ("superadmin", "admin_firma", "angajat")

# acțiune -> roluri permise (superadmin are tot, implicit)
PERMISIUNI = {
    "gestiune_cabinet": {"superadmin"},
    "gestiune_firme": {"superadmin", "admin_firma"},
    "gestiune_angajati": {"superadmin", "admin_firma"},
    "depune_declaratii": {"superadmin", "admin_firma"},
    "vede_firme": {"superadmin", "admin_firma", "angajat"},
    "introduce_documente": {"superadmin", "admin_firma", "angajat"},
}


def poate(rol, actiune):
    """True dacă rolul are voie la acțiune. superadmin poate tot."""
    if rol == "superadmin":
        return True
    permise = PERMISIUNI.get(actiune)
    if permise is None:
        raise ValueError(f"acțiune necunoscută: {actiune!r}")
    return rol in permise

# [parola_min_v1] Cerinta UNICA de parola, aplicata pe BACKEND peste tot (inregistrare cabinet,
# activare, schimbare, resetare). DOAR lungime minima — fara complexitate, fara blacklist.
PAROLA_MIN = 8
PAROLA_MESAJ = "Parola trebuie să aibă minim %d caractere." % PAROLA_MIN

def parola_ok(parola):
    """True daca parola respecta cerinta unica (lungimea minima)."""
    return len(parola or "") >= PAROLA_MIN

