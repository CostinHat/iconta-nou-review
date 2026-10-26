# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/notificari.py` (livrarea notificarilor pe canalul omului, lotul 7 pct.2.1).

Textul canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Acces la `public.notificari` (cutia de
iesire, `de_livrat`), `public.notificari_jurnal` si destinatarii din `public.users`.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback. *Hotarele tranzactiei raman ale
apelantului* (`core/notificari.py`: revendicarea se comite INAINTEA trimiterii).
"""


def scrie_jurnalul(cur, nid, user_id, tip, canal, link, mesaj_id, stare, rezerva, detaliu):
    cur.execute("INSERT INTO public.notificari_jurnal (notificare_id, user_id, tip, canal, link, mesaj_id, stare, rezerva_email, "
                "detaliu) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (nid, user_id, tip, canal, link, mesaj_id, stare, rezerva, detaliu))


def revendica(cur, limita):
    """Randurile de livrat (cel mult `limita`), blocate `FOR UPDATE SKIP LOCKED` si scoase din cutie, cu destinatarul lor."""
    cur.execute("SELECT n.id FROM public.notificari n WHERE n.de_livrat ORDER BY n.id LIMIT %s FOR UPDATE SKIP LOCKED", (limita,))
    ids = [r[0] for r in cur.fetchall()]
    if not ids:
        return []
    cur.execute("UPDATE public.notificari SET de_livrat = false WHERE id = ANY(%s)", (ids,))
    cur.execute("SELECT n.id, n.tip, u.id, u.email, u.canal_notificari, u.telefon, u.telefon_confirmat_la IS NOT NULL, "
                "u.acord_whatsapp_la IS NOT NULL, u.activ, u.notificari_tipuri, n.text FROM public.notificari n JOIN public.users u ON u.id = n.user_id "
                "WHERE n.id = ANY(%s) ORDER BY n.id", (ids,))
    return cur.fetchall()


def superadmini(cur):
    cur.execute("SELECT id FROM public.users WHERE rol = 'superadmin' AND activ ORDER BY id")
    return [r[0] for r in cur.fetchall()]


def scrie_starea_mesajului(cur, mesaj_id, stare, detaliu):
    """Starea raportata de Meta pentru un mesaj; intoarce (notificare_id, user_id, tip, rezerva_email) sau None."""
    cur.execute("UPDATE public.notificari_jurnal SET stare = %s, detaliu = COALESCE(%s, detaliu), actualizat_la = now() "
                "WHERE mesaj_id = %s RETURNING notificare_id, user_id, tip, rezerva_email", (stare, detaliu, mesaj_id))
    return cur.fetchone()


def marcheaza_rezerva(cur, mesaj_id):
    cur.execute("UPDATE public.notificari_jurnal SET rezerva_email = true WHERE mesaj_id = %s", (mesaj_id,))


def textul(cur, nid):
    """[567] Textul notificării din clopoțel (firma, elementul, motivul), pentru emailul de rezervă; None dacă notificarea nu mai există."""
    if not nid:
        return None
    cur.execute("SELECT text FROM public.notificari WHERE id = %s", (nid,))
    r = cur.fetchone()
    return r[0] if r else None
