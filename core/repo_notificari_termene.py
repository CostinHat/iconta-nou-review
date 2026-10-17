# -*- coding: utf-8 -*-
"""REPOSITORY — notificarea zilnică a termenelor (deficiența 320, tipul `termen_declaratie`, `core/notificari_termene.py`).

Textul canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care știe SQL și scheme*. FIECARE FUNCȚIE PRIMEȘTE CURSORUL
APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback.
"""

CHEIE_ZI = "notificari_termene_zi"


def revendica_ziua(cur, zi):
    """True dacă ziua `zi` (ISO) n-a fost încă notificată și acum e a acestei rulări (o singură rulare pe zi, oricâte procese)."""
    # upsert-ok: revendicarea zilei pe cheia ei — rândul se rescrie numai când ziua e alta (WHERE ... IS DISTINCT FROM), deci RETURNING gol = ziua deja luată
    cur.execute("INSERT INTO public.setari_platforma (cheie, valoare) VALUES (%s, %s) ON CONFLICT (cheie) DO UPDATE "
                "SET valoare = EXCLUDED.valoare, modificat_la = now() WHERE public.setari_platforma.valoare IS DISTINCT FROM EXCLUDED.valoare "
                "RETURNING cheie", (CHEIE_ZI, zi))
    return cur.fetchone() is not None


def firmele_cabinetelor(cur):
    """[(tenant_id, nume, cabinet_id)] — firmele active ale cabinetelor active."""
    cur.execute("SELECT t.id, t.nume, t.accounting_firm_id FROM public.tenants t JOIN public.accounting_firms a ON a.id = t.accounting_firm_id "
                "WHERE t.activ = true AND COALESCE(a.activ, true) = true ORDER BY t.id")
    return cur.fetchall()


def destinatarii_firmei(cur, cabinet_id, tenant_id):
    """[uid] — cine pregătește pe firmă: administratorul cabinetului și asistenții cu „Poate pregăti” cărora le e alocată."""
    cur.execute("SELECT u.id FROM public.users u WHERE u.activ = true AND u.accounting_firm_id = %s AND (u.rol = 'admin_firma' "
                "OR (u.rol = 'angajat' AND COALESCE(u.poate_pregati, false) AND EXISTS (SELECT 1 FROM public.user_tenants ut "
                "WHERE ut.user_id = u.id AND ut.tenant_id = %s))) ORDER BY u.id", (cabinet_id, tenant_id))
    return [r[0] for r in cur.fetchall()]


def firma_din_schema(cur, schema):
    """(tenant_id, nume, cabinet_id) firmei cu schema dată, sau None."""
    cur.execute("SELECT id, nume, accounting_firm_id FROM public.tenants WHERE schema_name = %s", (str(schema).strip('"'),))
    return cur.fetchone()
