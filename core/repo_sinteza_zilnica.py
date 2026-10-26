# -*- coding: utf-8 -*-
"""REPOSITORY — instrucțiunile SQL ale lui `core/sinteza_zilnica.py` (sinteza zilnică a cabinetului, emailul de seară al administratorului).

[lotul 13, deficiența 565] Jobul de cron își deschide acum conexiunea din pool-ul aplicației (registrul dezabonărilor se citește prin el),
deci e USE_CASE; SQL-ul a venit aici, în depozit (`PLAN_HARDENING.md:842`: *repository-ul e singurul care știe SQL și scheme*), neschimbat
în afară de lista patronilor, care aduce și bifele din Notificări (`notificari_tipuri`).

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback.
"""


def patronii(cur):
    """Administratorii activi ai cabinetelor, cu emailul și bifele din Notificări (cursor RealDict al apelantului)."""
    cur.execute(
        "SELECT id, email, prenume, nume, accounting_firm_id AS cabinet_id, notificari_tipuri "
        "  FROM public.users "
        " WHERE rol = 'admin_firma' AND activ = true "
        "   AND email IS NOT NULL AND email <> '' ORDER BY id")
    return cur.fetchall()


def numele_cabinetului(cur, cabinet_id):
    cur.execute("SELECT nume FROM public.accounting_firms WHERE id = %s", (cabinet_id,))
    r = cur.fetchone()
    return r[0] if r else None


def cifrele_zilei(cur, cabinet_id, zi):
    """Ce s-a petrecut în ziua `zi` și ce așteaptă acum: {pregatite, validate, respinse, depuse, de_validat, sesizari_noi,
    sesizari_fara_raspuns, pachete_trimise}."""
    d = {}
    # declaratii pe evenimentele zilei — [lotul 07.10 pct.4] pe PREGĂTIRE (documentul): „pregătite azi” = începute azi
    # (o retrimitere nu e o pregătire nouă), iar notele aceleiași facturi se validează / resping o dată
    # [lotul 11, 458] respinsă azi = de om: înlocuirea la „Generează din nou” nu e o respingere (`coada_api.sql_inlocuita`)
    from core.coada_api import sql_cheie_pregatire as _cheie, sql_inlocuita
    cur.execute(
        "WITH p AS (SELECT " + _cheie("d") + " AS cheie, MIN(creat_la) AS creat_la, "
        "  bool_or(aprobat_la::date = %(z)s) AS validata_azi, "
        "  bool_or(respins_la::date = %(z)s AND NOT " + sql_inlocuita("d") + ") AS respinsa_azi, "
        "  bool_or(depus_la::date = %(z)s) AS depusa_azi "
        "  FROM public.declaratii_coada d WHERE cabinet_id = %(c)s GROUP BY 1) "
        "SELECT "
        "  COUNT(*) FILTER (WHERE creat_la::date = %(z)s) AS pregatite, "
        "  COUNT(*) FILTER (WHERE validata_azi) AS validate, "
        "  COUNT(*) FILTER (WHERE respinsa_azi) AS respinse, "
        "  COUNT(*) FILTER (WHERE depusa_azi) AS depuse "
        "  FROM p",
        {"z": zi, "c": cabinet_id})
    r = cur.fetchone()
    d["pregatite"], d["validate"], d["respinse"], d["depuse"] = (int(r[0]), int(r[1]), int(r[2]), int(r[3]))

    # in asteptare ACUM: tot ce e la validare (declarații și note), oricând ar fi intrat (568)
    cur.execute(
        "SELECT COUNT(DISTINCT " + _cheie() + ") FROM public.declaratii_coada "
        " WHERE cabinet_id = %s AND stare = 'la_senior'", (cabinet_id,))
    d["de_validat"] = int(cur.fetchone()[0])

    # sesizari clienti: noi azi + fara raspuns acum
    cur.execute(
        "SELECT "
        "  COUNT(*) FILTER (WHERE creat_la::date = %(z)s) AS noi, "
        "  COUNT(*) FILTER (WHERE stare = 'noua') AS fara_raspuns "
        "  FROM public.raportari "
        " WHERE cabinet_id = %(c)s AND pentru_admin = false",
        {"z": zi, "c": cabinet_id})
    r = cur.fetchone()
    d["sesizari_noi"], d["sesizari_fara_raspuns"] = int(r[0]), int(r[1])

    # pachete lunare trimise azi (leg tenant -> cabinet)
    cur.execute(
        "SELECT COUNT(*) FROM public.pachet_povestea p "
        "  JOIN public.tenants t ON t.id = p.tenant_id "
        " WHERE t.accounting_firm_id = %(c)s "
        "   AND p.status = 'trimis' AND p.updated_at::date = %(z)s",
        {"z": zi, "c": cabinet_id})
    d["pachete_trimise"] = int(cur.fetchone()[0])
    return d
