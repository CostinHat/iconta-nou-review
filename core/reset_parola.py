# -*- coding: utf-8 -*-
"""core/reset_parola.py — recuperare parola cont CABINET ("Am uitat parola").

NU e magic-link: magic-link = autentificare directa pentru CLIENTII cabinetului (fara parola).
Aici omul ARE parola, o pierde, primeste dreptul sa seteze alta, apoi se logheaza normal.

Securitate:
  - token aleator criptografic (secrets.token_urlsafe), stocat DOAR ca hash sha256 (niciodata in clar);
  - expira 60 min; single-use (consumat atomic la prima folosire valida);
  - raspuns identic la /cere indiferent daca emailul exista (anti-enumerare) -> vezi ruta;
  - la setarea parolei: users.sesiuni_valide_de = now() -> sesiunile emise inainte mor;
  - curatarea expiratelor la fiecare scriere.
Doar conturi de CABINET (rol != client). Clientii folosesc magic-link.
"""
import secrets
import hashlib
from core import nucleu

EXPIRA_MIN = 60


def _hash(token):
    return hashlib.sha256((token or "").encode("utf-8")).hexdigest()


def cere_reset(conn, email):
    """Daca `email` e un cont de cabinet ACTIV, creeaza un token si intoarce (token_clar, user_dict).
    Altfel (inexistent / inactiv / client) intoarce (None, None). Apelantul NU divulga diferenta."""
    email = (email or "").strip().lower()
    with conn.cursor() as cur:
        # curatare la scriere: expirate SAU deja folosite
        cur.execute("DELETE FROM public.reset_parola_token WHERE expira < now() OR folosit = true")
        cur.execute("SELECT id, rol, nume, prenume FROM public.users "
                    "WHERE lower(email) = %s AND activ = true", (email,))
        u = cur.fetchone()
        if not u or u[1] == "client":   # clientii au magic-link, nu parola
            return None, None
        token = secrets.token_urlsafe(32)
        cur.execute("INSERT INTO public.reset_parola_token (user_id, token_hash, expira) "
                    "VALUES (%s, %s, now() + make_interval(mins => %s))",
                    (u[0], _hash(token), EXPIRA_MIN))
    return token, {"user_id": u[0], "nume": u[2], "prenume": u[3], "email": email}


def seteaza(conn, token, parola_noua):
    """Consuma tokenul ATOMIC (single-use: folosit=true doar daca era valid), seteaza parola
    noua si INVALIDEAZA sesiunile existente (sesiuni_valide_de=now()). Ridica ValueError daca
    tokenul e invalid / expirat / deja folosit. Parola se valideaza in ruta INAINTE de apel."""
    with conn.cursor() as cur:
        cur.execute("UPDATE public.reset_parola_token SET folosit = true "
                    "WHERE token_hash = %s AND folosit = false AND expira >= now() "
                    "RETURNING user_id", (_hash(token),))
        r = cur.fetchone()
        if not r:
            raise ValueError("token invalid, expirat sau deja folosit")
        uid = r[0]
        # [reset_parola_v1] TRUNCHIAT la secunda: iat-ul din token e secunde intregi (floor);
        # daca am pastra sub-secunda, un login imediat dupa reset (acelasi second) ar avea
        # iat < sesiuni_valide_de si s-ar autoinvalida. date_trunc => login-ul nou ramane valid.
        cur.execute("UPDATE public.users SET password_hash = %s, parola_schimbata = true, "
                    "sesiuni_valide_de = date_trunc('second', now()) WHERE id = %s",
                    (nucleu.hash_parola(parola_noua), uid))
    return {"ok": True, "user_id": uid}
