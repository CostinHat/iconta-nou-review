# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/uc_cont_notificari.py` (Setari cont -> Notificari: telefonul, codul de confirmare,
acordul si canalul; lotul 7 pct.2.2).

Textul canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Acces la coloanele de notificare din
`public.users` si la `public.telefon_coduri`. Ordinea canalului (numarul confirmat + acordul) o pazeste si baza
(`users_canal_notificari_check`, `core/migrare_canal_notificari.py`).

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback. *Hotarele tranzactiei raman ale
apelantului.*
"""


def stare(cur, uid):
    """(telefon, confirmat, canal, acord)."""
    cur.execute("SELECT telefon, telefon_confirmat_la IS NOT NULL, canal_notificari, acord_whatsapp_la IS NOT NULL FROM public.users "
                "WHERE id = %s", (uid,))
    return cur.fetchone()


def seteaza_telefonul(cur, uid, tel):
    """Numarul nou; altul decat cel salvat -> confirmarea se sterge, canalul revine pe email."""
    cur.execute("UPDATE public.users SET "
                "telefon_confirmat_la = CASE WHEN telefon IS NOT DISTINCT FROM %s THEN telefon_confirmat_la END, "
                "canal_notificari = CASE WHEN telefon IS NOT DISTINCT FROM %s THEN canal_notificari ELSE 'email' END, "
                "telefon = %s WHERE id = %s", (tel, tel, tel, uid))
    cur.execute("DELETE FROM public.telefon_coduri WHERE user_id = %s AND telefon IS DISTINCT FROM %s", (uid, tel))


def telefonul(cur, uid):
    cur.execute("SELECT telefon FROM public.users WHERE id = %s", (uid,))
    return cur.fetchone()[0]


def cod_cerut_de_curand(cur, uid, secunde):
    cur.execute("SELECT now() - creat_la < make_interval(secs => %s) FROM public.telefon_coduri WHERE user_id = %s", (secunde, uid))
    r = cur.fetchone()
    return bool(r and r[0])


def scrie_acordul(cur, uid):
    cur.execute("UPDATE public.users SET acord_whatsapp_la = COALESCE(acord_whatsapp_la, now()) WHERE id = %s", (uid,))


def scrie_codul(cur, uid, tel, cod_hash, minute):
    cur.execute("INSERT INTO public.telefon_coduri (user_id, telefon, cod_hash, expira_la) "
                "VALUES (%s, %s, %s, now() + make_interval(mins => %s)) ON CONFLICT (user_id) DO UPDATE SET "  # upsert-ok: un cod pe om
                "telefon = EXCLUDED.telefon, cod_hash = EXCLUDED.cod_hash, expira_la = EXCLUDED.expira_la, incercari = 0, "
                "creat_la = now()", (uid, tel, cod_hash, minute))


def codul_in_curs(cur, uid):
    """(cod_hash, neexpirat, incercari, pentru_numarul_salvat) sau None; randul ramane blocat pana la commit."""
    cur.execute("SELECT c.cod_hash, c.expira_la > now(), c.incercari, c.telefon = u.telefon FROM public.telefon_coduri c "
                "JOIN public.users u ON u.id = c.user_id WHERE c.user_id = %s FOR UPDATE OF c", (uid,))
    return cur.fetchone()


def sterge_codul(cur, uid):
    cur.execute("DELETE FROM public.telefon_coduri WHERE user_id = %s", (uid,))


def numara_incercarea(cur, uid):
    cur.execute("UPDATE public.telefon_coduri SET incercari = incercari + 1 WHERE user_id = %s", (uid,))


def confirma_telefonul(cur, uid):
    cur.execute("UPDATE public.users SET telefon_confirmat_la = now() WHERE id = %s", (uid,))


def retrage_acordul(cur, uid):
    cur.execute("UPDATE public.users SET acord_whatsapp_la = NULL, canal_notificari = 'email' WHERE id = %s", (uid,))


def alege_whatsapp(cur, uid):
    cur.execute("UPDATE public.users SET acord_whatsapp_la = COALESCE(acord_whatsapp_la, now()), "
                "canal_notificari = 'whatsapp' WHERE id = %s", (uid,))


def alege_emailul(cur, uid):
    cur.execute("UPDATE public.users SET canal_notificari = 'email' WHERE id = %s", (uid,))


def scrie_telefonul_contului_nou(cur, user_id, telefon):
    """Telefonul din formularul de inregistrare (lotul 7 pct.2.2), NECONFIRMAT."""
    cur.execute("UPDATE public.users SET telefon = %s WHERE id = %s", (telefon, user_id))


def preferintele(cur, uid):
    """[320] (bifele salvate | None, salvate (bool), rol, poate_pregati, poate_valida, scutit de prima intrare (bool)) — cine e omul și
    ce a bifat în Notificări."""
    cur.execute("SELECT notificari_tipuri, notificari_salvate_la IS NOT NULL, rol, COALESCE(poate_pregati, false), "
                "COALESCE(poate_valida, false), prima_intrare_scutita_la IS NOT NULL FROM public.users WHERE id = %s", (uid,))
    return cur.fetchone()


def scrie_preferintele(cur, uid, tipuri_json):
    """[320] Bifele din Notificări și momentul salvării (prima intrare le cere)."""
    cur.execute("UPDATE public.users SET notificari_tipuri = %s::jsonb, notificari_salvate_la = now() WHERE id = %s", (tipuri_json, uid))
