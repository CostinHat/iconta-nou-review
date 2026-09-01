# -*- coding: utf-8 -*-
"""
core/migrare_supervizor_confirmari.py — unde rămâne SCRISĂ confirmarea unei constatări certe.

SCHEMA PUBLIC (nu tenant), ca `public.alerte_control_emise`: e un jurnal peste portofoliu, iar
supervizorul rulează pe portofoliu, nu pe o firmă.

CHEIA POARTĂ AMPRENTA, nu doar tipul. O confirmare acoperă **nepotrivirea văzută atunci**: dacă
cifrele se schimbă, amprenta se schimbă și confirmarea veche nu se mai potrivește — deci nu acoperă
tăcut o divergență nouă. *Fără amprentă în cheie, „am confirmat o dată" ar fi însemnat „pentru
totdeauna", iar confirmarea explicită ar fi devenit o bifă la prima folosire.*

`motiv` e NOT NULL: o confirmare fără motiv scris nu se poate citi peste șase luni, iar cerința lui
Costin e ca ea să RĂMÂNĂ scrisă, nu doar să existe.

Idempotent (CREATE TABLE IF NOT EXISTS).
"""

DDL = """
CREATE TABLE IF NOT EXISTS public.supervizor_confirmari (
    tenant_id        integer     NOT NULL,
    an               integer     NOT NULL,
    luna             integer     NOT NULL,
    tip_constatare   text        NOT NULL,
    amprenta         text        NOT NULL,
    confirmat_de     text        NOT NULL,
    confirmat_de_id  integer,
    confirmat_la     timestamptz NOT NULL DEFAULT now(),
    motiv            text        NOT NULL,
    CONSTRAINT supervizor_confirmari_pkey
        PRIMARY KEY (tenant_id, an, luna, tip_constatare, amprenta),
    CONSTRAINT supervizor_confirmari_motiv_nevid CHECK (btrim(motiv) <> '')
)
"""


def aplica(conn):
    """Aplica DDL-ul idempotent pe public. Comiterea o face apelantul."""
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    """True daca public.supervizor_confirmari exista."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.supervizor_confirmari')")
        return cur.fetchone()[0] is not None
