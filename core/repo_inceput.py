# -*- coding: utf-8 -*-
"""REPOSITORY — semnalele cardurilor de început (deficiențele 319 + 320, comanda Costin 17.10.2026 7.2): ce s-a făcut DEJA, în ecranele
reale, pentru fiecare card — nu un clic pe card.

Textul canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care știe SQL și scheme*. FIECARE FUNCȚIE PRIMEȘTE CURSORUL
APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback.
"""


def omul(cur, uid):
    """(rol, cabinet, telefon, notificări salvate, firmele văzute (asistentul), poate_pregati, poate_valida, poate_depune)."""
    cur.execute("SELECT rol, accounting_firm_id, telefon, notificari_salvate_la IS NOT NULL, inceput_firme_vazute_la IS NOT NULL, "
                "COALESCE(poate_pregati, false), COALESCE(poate_valida, false), COALESCE(poate_depune, false) "
                "FROM public.users WHERE id = %s", (uid,))
    return cur.fetchone()


def firmele_cabinetului(cur, cabinet_id):
    """[(tenant_id, schema)] — firmele active ale cabinetului."""
    cur.execute("SELECT id, schema_name FROM public.tenants WHERE accounting_firm_id = %s AND activ = true AND schema_name IS NOT NULL "
                "ORDER BY id", (cabinet_id,))
    return cur.fetchall()


def preluare_facuta(cur, schema):
    """(balanța importată, auditul de preluare rulat) pe firma din `schema`: soldurile inițiale există; auditul și-a păstrat raportul
    (`artefacte_produse`, fel `audit_preluare` — `uc_control_fiscal`)."""
    q = '"%s".' % str(schema).strip('"')
    cur.execute("SELECT to_regclass(%s) IS NOT NULL, to_regclass(%s) IS NOT NULL", (q + "solduri_initiale", q + "artefacte_produse"))
    are_sold, are_art = cur.fetchone()
    sold = audit = False
    if are_sold:
        cur.execute("SELECT EXISTS (SELECT 1 FROM " + q + "solduri_initiale)")
        sold = bool(cur.fetchone()[0])
    if are_art:
        cur.execute("SELECT EXISTS (SELECT 1 FROM " + q + "artefacte_produse WHERE fel = 'audit_preluare')")
        audit = bool(cur.fetchone()[0])
    return sold, audit


def spv_conectat(cur, cabinet_id):
    cur.execute("SELECT EXISTS (SELECT 1 FROM public.spv_token WHERE accounting_firm_id = %s AND tenant_id IS NULL AND activ = true)",
                (cabinet_id,))
    return bool(cur.fetchone()[0])


def echipa(cur, cabinet_id):
    """(are un asistent adăugat, „Lucrez singur” ales)."""
    cur.execute("SELECT EXISTS (SELECT 1 FROM public.users WHERE accounting_firm_id = %s AND rol = 'angajat'), "
                "(SELECT lucreaza_singur_la IS NOT NULL FROM public.accounting_firms WHERE id = %s)", (cabinet_id, cabinet_id))
    r = cur.fetchone()
    return bool(r[0]), bool(r[1])


def lucrez_singur(cur, cabinet_id):
    cur.execute("UPDATE public.accounting_firms SET lucreaza_singur_la = COALESCE(lucreaza_singur_la, now()) WHERE id = %s", (cabinet_id,))


def firmele_asistentului(cur, uid):
    """[(tenant_id, numele)] — firmele alocate asistentului."""
    cur.execute("SELECT t.id, t.nume FROM public.user_tenants ut JOIN public.tenants t ON t.id = ut.tenant_id "
                "WHERE ut.user_id = %s AND t.activ = true ORDER BY t.nume", (uid,))
    return cur.fetchall()


def firme_vazute(cur, uid):
    cur.execute("UPDATE public.users SET inceput_firme_vazute_la = COALESCE(inceput_firme_vazute_la, now()) WHERE id = %s", (uid,))


def adminii_pentru_activare(cur, uid):
    """[320, `asistent_activat`] (rolul omului, numele lui, [administratorii activi ai cabinetului lui])."""
    cur.execute("SELECT u.rol, COALESCE(NULLIF(btrim(u.nume), ''), u.email), ARRAY(SELECT a.id FROM public.users a WHERE "
                "a.accounting_firm_id = u.accounting_firm_id AND a.rol = 'admin_firma' AND a.activ = true ORDER BY a.id) "
                "FROM public.users u WHERE u.id = %s", (uid,))
    r = cur.fetchone()
    if not r:
        return None, None, []
    v = list(r.values()) if isinstance(r, dict) else list(r)
    return v[0], v[1], list(v[2] or [])


def clientii_firmei(cur, tenant_id):
    """[320, tipurile clientului] [(uid, email, și-a salvat alegerile din Notificări)] — conturile active de client ale firmei."""
    cur.execute("SELECT u.id, lower(u.email), u.notificari_salvate_la IS NOT NULL FROM public.users u JOIN public.user_tenants ut "
                "ON ut.user_id = u.id WHERE ut.tenant_id = %s AND u.rol = 'client' AND u.activ = true ORDER BY u.id", (tenant_id,))
    return [tuple(r.values()) if isinstance(r, dict) else tuple(r) for r in cur.fetchall()]
