# -*- coding: utf-8 -*-
"""REPOSITORY — ciornele formularelor începute, păstrate pe server (deficiența 495, lotul 12, comanda 12.1): `public.ciorne_formular`
(`core/migrare_ciorne_formular.py`), un rând pe UTILIZATOR + FIRMĂ + FORMULAR. Use-case-ul (rutele) e `core/ciorne_formular.py`.

Textul canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care știe SQL și scheme*. FIECARE FUNCȚIE PRIMEȘTE CURSORUL
APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback.
"""
import json


def citeste(cur, user_id, tenant_id, formular):
    """Conținutul ciornei (dict) sau None."""
    cur.execute("SELECT continut FROM public.ciorne_formular WHERE user_id = %s AND tenant_id = %s AND formular = %s",
                (user_id, tenant_id, formular))
    r = cur.fetchone()
    if not r:
        return None
    c = r[0]
    return json.loads(c) if isinstance(c, str) else c


def scrie(cur, user_id, tenant_id, formular, continut):
    """Pune (sau înlocuiește) ciorna; întoarce momentul scrierii (ISO)."""
    # upsert-ok: cheia naturală e (utilizator, firmă, formular) — un singur formular început pe om, firmă și formular; scrierea nouă a
    # aceluiași om ESTE ciorna lui de acum (495), nu o înregistrare a altcuiva suprascrisă tacit
    cur.execute("INSERT INTO public.ciorne_formular (user_id, tenant_id, formular, continut, salvat_la) "
                "VALUES (%s, %s, %s, %s::jsonb, now()) ON CONFLICT (user_id, tenant_id, formular) "
                "DO UPDATE SET continut = EXCLUDED.continut, salvat_la = EXCLUDED.salvat_la RETURNING salvat_la",
                (user_id, tenant_id, formular, json.dumps(continut, ensure_ascii=False)))
    return cur.fetchone()[0].isoformat()


def sterge(cur, user_id, tenant_id, formular):
    """Șterge ciorna; True dacă exista."""
    cur.execute("DELETE FROM public.ciorne_formular WHERE user_id = %s AND tenant_id = %s AND formular = %s RETURNING 1",
                (user_id, tenant_id, formular))
    return cur.fetchone() is not None
